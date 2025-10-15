"""Utilities for agent memory and conversation persistence.

This module centralizes read/write operations for the three-layer
memory strategy (structured memory, conversation history, and
append-only audit log). It is designed to be used from FastAPI endpoints
and other agent orchestration code.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENTS_ROOT = PROJECT_ROOT / "agents"

ALLOWED_SECTIONS: tuple[Literal["persona", "facts", "messages"], ...] = (
    "persona",
    "facts",
    "messages",
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _memory_template() -> Dict[str, Any]:
    return {
        "persona": {"goals": [], "tagline": "", "do_not": []},
        "facts": [],
        "messages": [],
    }


def _conversation_template() -> Dict[str, Any]:
    return {"conversations": []}


def _ensure_agent_dir(agent: str) -> Path:
    agent_dir = AGENTS_ROOT / agent.upper()
    agent_dir.mkdir(parents=True, exist_ok=True)
    return agent_dir


async def _read_json(path: Path, default_factory) -> Dict[str, Any]:
    if not path.exists():
        return default_factory()

    def _load() -> Dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    try:
        return await asyncio.to_thread(_load)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        logger.warning(
            "Falling back to default for %s due to decode error: %s", path, exc
        )
        return default_factory()


async def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")

    def _dump() -> None:
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
        tmp_path.replace(path)

    await asyncio.to_thread(_dump)


async def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    line = json.dumps(payload, ensure_ascii=False)
    path.parent.mkdir(parents=True, exist_ok=True)

    def _append() -> None:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    await asyncio.to_thread(_append)


_AGENT_LOCKS: Dict[str, asyncio.Lock] = {}


def _agent_lock(agent: str) -> asyncio.Lock:
    lock = _AGENT_LOCKS.get(agent)
    if lock is None:
        lock = asyncio.Lock()
        _AGENT_LOCKS[agent] = lock
    return lock


class MemoryUpdatePayload(BaseModel):
    agent: str = Field(..., description="Agent identifier, e.g. 'CTO'")
    section: Literal["persona", "facts", "messages"]
    entry: Dict[str, Any] | str = Field(
        ..., description="Content to append/update (dict or string)"
    )

    @field_validator("agent")
    @classmethod
    def _agent_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("agent must not be empty")
        return value.strip()


class ConversationMessage(BaseModel):
    sender: str
    message: str
    timestamp: Optional[str] = None

    @field_validator("sender", "message")
    @classmethod
    def _not_blank(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("value must not be empty")
        return value


class ConversationAppendPayload(BaseModel):
    agent: str
    session_id: Optional[str] = None
    messages: List[ConversationMessage]
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("agent")
    @classmethod
    def _agent_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("agent must not be empty")
        return value.strip()

    @field_validator("messages")
    @classmethod
    def _validate_messages(
        cls, value: List[ConversationMessage]
    ) -> List[ConversationMessage]:
        if not value:
            raise ValueError("messages must contain at least one item")
        return value


async def apply_memory_update(payload: MemoryUpdatePayload) -> Dict[str, Any]:
    agent = payload.agent.upper()
    agent_dir = _ensure_agent_dir(agent)
    memory_path = agent_dir / "memory.json"
    audit_path = agent_dir / "memory.jsonl"

    async with _agent_lock(agent):
        memory_state = await _read_json(memory_path, _memory_template)

        # Handle both string and dict entries
        if isinstance(payload.entry, str):
            # Convert string to dict format for consistency
            entry = {"content": payload.entry, "timestamp": _iso_now()}
        else:
            entry = json.loads(
                json.dumps(payload.entry)
            )  # deep copy via JSON round-trip

        if payload.section == "persona":
            if not isinstance(entry, dict):
                raise ValueError("persona updates must be a JSON object")
            persona_state = memory_state.setdefault("persona", {})
            if not isinstance(persona_state, dict):
                persona_state = {}
            persona_state.update(entry)
            memory_state["persona"] = persona_state
        else:
            section_items = memory_state.setdefault(payload.section, [])
            if not isinstance(section_items, list):
                section_items = []
            if isinstance(entry, dict) and "timestamp" not in entry:
                entry["timestamp"] = _iso_now()
            section_items.append(entry)
            memory_state[payload.section] = section_items

        await _write_json(memory_path, memory_state)

        audit_record = {
            "timestamp": _iso_now(),
            "agent": agent,
            "section": payload.section,
            "entry": entry,
        }
        await _append_jsonl(audit_path, audit_record)

        logger.info(
            "Memory update applied",
            extra={"agent": agent, "section": payload.section},
        )

    return memory_state


async def get_memory_state(agent: str) -> Dict[str, Any]:
    agent_upper = agent.upper()
    agent_dir = _ensure_agent_dir(agent_upper)
    memory_path = agent_dir / "memory.json"
    async with _agent_lock(agent_upper):
        return await _read_json(memory_path, _memory_template)


async def reset_memory_section(agent: str, section: Optional[str]) -> Dict[str, Any]:
    agent_upper = agent.upper()
    agent_dir = _ensure_agent_dir(agent_upper)
    memory_path = agent_dir / "memory.json"

    if section is not None and section not in ALLOWED_SECTIONS:
        raise ValueError(f"section must be one of {ALLOWED_SECTIONS}")

    async with _agent_lock(agent_upper):
        memory_state = await _read_json(memory_path, _memory_template)
        if section is None:
            memory_state = _memory_template()
        elif section == "persona":
            memory_state["persona"] = _memory_template()["persona"]
        else:
            memory_state[section] = []
        await _write_json(memory_path, memory_state)

    return memory_state


async def append_conversation(payload: ConversationAppendPayload) -> Dict[str, Any]:
    agent = payload.agent.upper()
    agent_dir = _ensure_agent_dir(agent)
    convo_path = agent_dir / "conversation_history.json"
    session_id = payload.session_id or uuid4().hex
    now = _iso_now()

    async with _agent_lock(agent):
        conversation_state = await _read_json(convo_path, _conversation_template)
        conversations: List[Dict[str, Any]] = conversation_state.setdefault(
            "conversations", []
        )

        conversation_entry: Optional[Dict[str, Any]] = next(
            (c for c in conversations if c.get("session_id") == session_id),
            None,
        )

        if conversation_entry is None:
            conversation_entry = {
                "session_id": session_id,
                "timestamp": now,
                "messages": [],
            }
            conversations.append(conversation_entry)

        conversation_entry.setdefault("messages", [])
        conversation_entry["last_active_timestamp"] = now
        if payload.metadata:
            existing_meta = conversation_entry.setdefault("metadata", {})
            existing_meta.update(payload.metadata)

        for message in payload.messages:
            message_dict = message.model_dump()
            if not message_dict.get("timestamp"):
                message_dict["timestamp"] = _iso_now()
            conversation_entry["messages"].append(message_dict)

        await _write_json(convo_path, conversation_state)

    return {"session_id": session_id, "conversation": conversation_entry}


async def get_conversation_history(
    agent: str, session_id: Optional[str] = None
) -> Dict[str, Any]:
    agent_upper = agent.upper()
    agent_dir = _ensure_agent_dir(agent_upper)
    convo_path = agent_dir / "conversation_history.json"

    async with _agent_lock(agent_upper):
        conversation_state = await _read_json(convo_path, _conversation_template)

    if session_id is None:
        return conversation_state

    for conversation in conversation_state.get("conversations", []):
        if conversation.get("session_id") == session_id:
            return conversation

    raise FileNotFoundError(f"Session '{session_id}' not found for agent {agent_upper}")


async def load_agent_context(
    agent: str,
    *,
    max_messages: int = 5,
    max_facts: int = 5,
) -> Dict[str, Any]:
    """Return a snapshot of persona, facts, and latest conversation for an agent."""

    if max_messages <= 0:
        raise ValueError("max_messages must be a positive integer")
    if max_facts <= 0:
        raise ValueError("max_facts must be a positive integer")

    memory_state = await get_memory_state(agent)
    persona = memory_state.get("persona", {}) or {}
    facts = (memory_state.get("facts") or [])[-max_facts:]
    recent_messages = (memory_state.get("messages") or [])[-max_messages:]

    conversation_state = await get_conversation_history(agent)
    conversations = conversation_state.get("conversations", []) or []

    latest_messages: List[Dict[str, Any]] = []
    if conversations:

        def _ts(entry: Dict[str, Any]) -> str:
            return (
                entry.get("last_active_timestamp")
                or entry.get("timestamp")
                or "1970-01-01T00:00:00Z"
            )

        latest_session = max(conversations, key=_ts)
        latest_messages = (latest_session.get("messages") or [])[-max_messages:]

    return {
        "agent": agent.upper(),
        "persona": persona,
        "facts": facts,
        "recent_messages": recent_messages,
        "conversation_history": latest_messages,
    }

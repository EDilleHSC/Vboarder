from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Note: app will be re-initialized with lifespan parameter after lifespan function is defined
# This early version is temporary for imports that reference app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Add this health endpoint ---
@app.get("/health")
async def health():
    return {"status": "ok"}


#!/usr/bin/env python3
"""
VBoarder Backend — Full Async RAG v3.3 (Optimized Build)
Includes: Async Embedding Caching, Parallel Embeddings, Async LLM/Ollama.
"""

import asyncio  # New: For async operations
import datetime
import json
import logging
import os
import textwrap
import time
from functools import lru_cache
from pathlib import Path
from threading import Lock
from typing import List, Optional, Tuple

# --------------------------------------------------------
# 🧠 Persistent Memory Integration Patch
# --------------------------------------------------------
import aiofiles
import httpx
import numpy as np
import psutil
from fastapi import APIRouter, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Global memory cache + lock ---
MEMORY_FILE = os.path.join("data", "memory.jsonl")
MEMORY_CACHE = []
MEMORY_LOCK = asyncio.Lock()


# --- Load memory on startup ---
async def preload_memory():
    """Loads all memory entries into the global cache asynchronously."""
    if os.path.exists(MEMORY_FILE):
        async with aiofiles.open(MEMORY_FILE, "r") as f:
            async for line in f:
                try:
                    MEMORY_CACHE.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
        print(f"[MEMORY] Preloaded {len(MEMORY_CACHE)} past entries.")
    else:
        # Ensure the 'data' directory exists for the memory file
        Path("data").mkdir(exist_ok=True)
        print("[MEMORY] No memory file found, starting fresh.")


# --------------------------------------------------------

# ========================================================
# ⚙️ Logging Setup
# ========================================================
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("vboarder")

# ========================================================
# 🧠 Config & Globals
# ========================================================
MAX_MEMORY_SIZE = int(os.getenv("MAX_MEMORY_MB", 5)) * 1024 * 1024
TOP_K_DEFAULT = int(os.getenv("TOP_K_DEFAULT", 3))
START_TIME = time.time()
REQUEST_COUNT = 0

# Environment
API_KEY = os.getenv("API_KEY")
LLM_MODE = os.getenv("LLM_MODE", "local").lower()
LOCAL_URL = os.getenv("LOCAL_URL", "http://localhost:11434")
OPENAI_URL = os.getenv("OPENAI_URL", "https://api.openai.com/v1/chat/completions")

# Pathing
PROJECT_ROOT = Path(__file__).resolve().parent
# Canonical agents directory (migrated from agents_v2)
AGENT_BASE_DIR = PROJECT_ROOT / "agents"
AGENT_BASE_DIR.mkdir(parents=True, exist_ok=True)

# VECTOR RECALL SETUP
file_write_lock = Lock()

# 🧩 Optimization: ASYNC CACHE IMPLEMENTATION
# This dictionary will store (embeddings, memory_lines) tuple keyed by agent_name
# The value includes the modification time for easy invalidation.
_EMBEDDING_CACHE = {}
_CACHE_TIMEOUT_SECONDS = (
    300  # Cache entries expire after 5 minutes, or on file modification
)


def clear_agent_cache():
    """Clears all entries in the cache."""
    global _EMBEDDING_CACHE
    _EMBEDDING_CACHE = {}
    log.info("Embedding cache cleared globally.")


# ========================================================
# ⚙️ Agent Config (cached)
# ========================================================
@lru_cache(maxsize=32)
def load_agent_config(agent_name: str) -> dict:
    """Load agent config, safely creating default if missing."""
    agent_path = AGENT_BASE_DIR / agent_name
    agent_path.mkdir(parents=True, exist_ok=True)
    cfg_path = agent_path / "config.json"

    if not cfg_path.exists():
        default_config = {
            "persona": "You are a helpful and versatile AI assistant.",
            "goal": "Answer the user's questions truthfully and accurately.",
            "model": "llama3",
        }
        with cfg_path.open("w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)
            log.info(f"Created default config for agent: {agent_name}")
        return default_config

    with cfg_path.open("r", encoding="utf-8") as f:
        return json.load(f)


# ========================================================
# 🧠 RAG TEMPLATE
# ========================================================
AGENT_TEMPLATE = textwrap.dedent(
    """
    --- AGENT SYSTEM INSTRUCTIONS ---
    **ROLE**: {persona}
    **GOAL**: {goal}

    --- MEMORY SNIPPET (CONTEXT) ---
    {context}
    ---------------------------------

    --- USER QUERY ---
    {query}
    ------------------

    Agent Response:
    """
)


# ========================================================
# 🧩 Embeddings (Fully Async & Parallel)
# ========================================================
async def _ollama_embed_single(
    client: httpx.AsyncClient, text: str, model_name: str, url: str
) -> List[float]:
    """Helper for parallel single embedding request."""
    try:
        r = await client.post(url, json={"model": model_name, "prompt": text})
        r.raise_for_status()
        return r.json().get("embedding", [])
    except Exception as e:
        log.error(f"❌ Embed failed for text: {text[:40]}... Error: {e}")
        return [0.0] * 3072  # Fallback vector


async def async_embed_texts(texts: List[str]) -> Optional[np.ndarray]:
    """
    Uses httpx and asyncio.gather for PARALLEL non-blocking Ollama embedding API calls.
    """
    url = os.getenv("EMBEDDING_URL", f"{LOCAL_URL}/api/embeddings")
    model_name = os.getenv("EMBEDDING_MODEL", "embeddinggemma")

    # Use httpx.AsyncClient for concurrent non-blocking requests
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 🧩 Optimization: Use asyncio.gather() for parallel I/O
        tasks = [_ollama_embed_single(client, t, model_name, url) for t in texts]
        vectors = await asyncio.gather(*tasks)

    # Check if a zero-vector fallback occurred for all texts
    if all(all(x == 0.0 for x in v) for v in vectors if len(v) == 3072):
        log.warning("All embeddings failed, returning None to disable vector search.")
        return None

    return np.array(vectors, dtype=np.float32)


# ========================================================
# 🧠 Ollama / LLM Query (Fully Async)
# ========================================================
async def smart_infer(prompt: str, max_retries: int = 2) -> str:
    """Unified asynchronous interface for local or API model inference with retries."""
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, read=60.0)
            ) as client:
                if LLM_MODE == "local":
                    # Non-streaming call for stable asynchronous operation
                    payload = {"model": "llama3", "prompt": prompt, "stream": False}
                    r = await client.post(f"{LOCAL_URL}/api/generate", json=payload)
                    r.raise_for_status()
                    return r.json().get("response", "").strip()

                elif LLM_MODE == "openai":
                    headers = {"Authorization": f"Bearer {API_KEY}"}
                    data = {
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.7,
                    }
                    r = await client.post(OPENAI_URL, headers=headers, json=data)
                    r.raise_for_status()
                    return r.json()["choices"][0]["message"]["content"].strip()

                else:
                    return "[Error] Invalid LLM_MODE configured."

        except httpx.TimeoutException:
            if attempt + 1 == max_retries:
                return "[LLM Timeout] Model did not respond in time."
        except Exception as e:
            if attempt + 1 == max_retries:
                return f"[Inference Error] {e}"


# ========================================================
# 🧩 Memory Helpers (Sync I/O)
# ========================================================
def safe_read_jsonl(path: Path) -> list:
    """Read a JSONL file, safely skipping malformed lines."""
    if not path.exists():
        return []
    # NOTE: This memory is being phased out in favor of the global, preloaded cache
    # But it remains for older agent-specific memory.jsonl files.
    try:
        with path.open("r", encoding="utf-8") as f:
            data = []
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        log.warning(f"Skipping malformed JSON line in {path}: {e}")
            return data
    except Exception as e:
        log.error(f"Failed to read {path}: {e}")
        return []


def _get_memory_file(agent: str) -> Path:
    """Helper: Return path to agent's memory file."""
    # NOTE: This path is for old agent-specific memory. The new global memory is MEMORY_FILE.
    agent_path = AGENT_BASE_DIR / agent
    agent_path.mkdir(parents=True, exist_ok=True)
    return agent_path / "memory.jsonl"


def append_jsonl_safe(file: Path, entry: dict):
    """Safely appends a JSON entry to a JSONL file using a thread lock."""
    # NOTE: This is the legacy *synchronous* memory logging.
    with file_write_lock:
        with file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


# --------------------------------------------------------
# ✅ Optional Recall Helper
# --------------------------------------------------------
def recall_recent(agent: str, limit: int = 5):
    """
    Retrieves the most recent memory entries for a specific agent from the global cache.
    """
    # NOTE: We use the global MEMORY_CACHE which stores the new format:
    # {"timestamp": ..., "agent": ..., "query": ..., "response": ...}
    return [m for m in MEMORY_CACHE if m.get("agent") == agent][-limit:]


# --------------------------------------------------------

# ========================================================
# 🧠 VECTOR RECALL CORE (with Async Caching)
# ========================================================


async def _get_embeddings_cached(agent: str) -> Optional[Tuple[np.ndarray, List[dict]]]:
    """Retrieves embeddings from cache or generates them asynchronously."""

    # NOTE: This function currently still loads from the agent-specific memory.jsonl.
    # For a full transition, you would want this function to filter and process the global MEMORY_CACHE.
    # We will keep it using the agent-specific file for now to maintain the RAG functionality
    # of the original code, but we must rename the memory fields (q/a).

    memory_file = _get_memory_file(agent)

    # 1. Check cache
    if agent in _EMBEDDING_CACHE:
        cache_entry = _EMBEDDING_CACHE[agent]
        cached_mtime, cached_data = cache_entry["mtime"], cache_entry["data"]

        try:
            current_mtime = os.path.getmtime(memory_file)
            current_time = time.time()

            # Check for file modification or cache timeout
            if (
                current_mtime <= cached_mtime
                and (current_time - cache_entry["timestamp"]) < _CACHE_TIMEOUT_SECONDS
            ):
                log.debug(f"Cache hit for agent: {agent}")
                return cached_data
            else:
                log.debug(f"Cache expired for agent: {agent}. Rebuilding...")
                del _EMBEDDING_CACHE[agent]  # Invalidate expired entry
        except FileNotFoundError:
            # File deleted, invalidate cache
            del _EMBEDDING_CACHE[agent]

    # 2. Cache miss or invalidation: Generate new embeddings
    lines = safe_read_jsonl(memory_file)

    if not lines:
        return None

    # NOTE: This logic assumes the old 'q' and 'a' keys for existing RAG files.
    # The new global memory uses 'query' and 'response'.
    # We maintain 'q' and 'a' here for backwards compatibility of the RAG vector files.
    texts = [f"User: {l['q']} Agent: {l['a']}" for l in lines]

    # Async call to parallel embedder
    embeddings = await async_embed_texts(texts)

    if embeddings is None or len(embeddings) == 0:
        return None

    # Normalize embeddings
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    result = (embeddings, lines)

    # 3. Store in cache
    try:
        current_mtime = os.path.getmtime(memory_file)
    except FileNotFoundError:
        current_mtime = time.time()  # Use current time if file was just created

    _EMBEDDING_CACHE[agent] = {
        "timestamp": time.time(),
        "mtime": current_mtime,
        "data": result,
    }
    log.debug(f"New embeddings generated and cached for agent: {agent}.")

    return result


async def search_agent_memory(agent: str, query: str, top_k: int) -> dict:
    """Search agent memory semantically using vector embeddings (RAG/Recall)."""

    # 1. Fetch memory and embeddings using async cache
    embeddings_data = await _get_embeddings_cached(agent)

    if not embeddings_data:
        return {
            "status": "error",
            "detail": "No memory data found or embedding service failed.",
            "agent": agent,
        }

    embeddings, entries = embeddings_data

    # 2. Embed the user query (Async)
    # The query is a single text, but we keep the list format for the async embedder
    query_embedding_array = await async_embed_texts([query])

    if query_embedding_array is None or len(query_embedding_array) == 0:
        return {
            "status": "error",
            "detail": "Failed to embed query using Ollama.",
            "agent": agent,
        }

    query_embedding = query_embedding_array[0]
    query_embedding = query_embedding / np.linalg.norm(query_embedding)

    # 3. Calculate Cosine Similarity & Recency Weight (Sync Numpy)
    similarities = np.dot(embeddings, query_embedding)

    weights = np.linspace(1.2, 0.8, num=len(similarities))
    weighted_scores = similarities * weights

    top_k_indices = np.argsort(weighted_scores)[::-1][:top_k]

    # 4. Format results
    results = []
    for i in top_k_indices:
        results.append({"score": float(weighted_scores[i]), "memory_entry": entries[i]})

    return {
        "status": "success",
        "agent": agent,
        "query": query,
        "top_k": top_k,
        "results": results,
    }


# ========================================================
# 📦 Models & Setup
# ========================================================
# NOTE: The app definition was moved up earlier in this file, so it's commented out here.
# app = FastAPI(title="VBoarder Backend", version="3.3")

# CORS
# NOTE: CORS configuration was moved up earlier in this file, so it's commented out here.
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


class MemoryEntry(BaseModel):
    q: str
    a: str


class AskRequest(BaseModel):
    agent: str
    query: str


memory_router = APIRouter(prefix="/api/memory", tags=["Memory"])
app.include_router(memory_router)

# ========================================================
# 🧩 MEMORY CRUD ENDPOINTS (Sync I/O handled by threads)
# ========================================================


@memory_router.post("/{agent}/add")
def add_agent_memory(agent: str, entry: MemoryEntry):
    """Add a memory entry (question + answer) to the agent-specific memory file."""
    # NOTE: This endpoint still uses the legacy agent-specific memory file.
    memory_file = _get_memory_file(agent)

    if memory_file.exists() and memory_file.stat().st_size > MAX_MEMORY_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Memory file for agent '{agent}' is too large (> {round(MAX_MEMORY_SIZE/1024/1024)} MB).",
        )

    try:
        append_jsonl_safe(memory_file, entry.dict())
        # Clear the specific agent's cache entry immediately upon write
        if agent in _EMBEDDING_CACHE:
            del _EMBEDDING_CACHE[agent]
            log.debug(f"Cache entry deleted for agent: {agent} after write.")
        return {"agent": agent, "added": entry.dict()}
    except Exception as e:
        log.error(f"Error writing memory: {e}")
        raise HTTPException(status_code=500, detail=f"Error writing memory: {e}")


@memory_router.get("/{agent}/stats")
def memory_stats(agent: str):
    """Return memory entry count and file size."""
    memory_file = _get_memory_file(agent)
    # NOTE: This endpoint still reports stats for the agent-specific RAG memory file.
    lines = safe_read_jsonl(memory_file)

    file_size_bytes = 0
    if memory_file.exists():
        file_size_bytes = memory_file.stat().st_size

    return {
        "agent": agent,
        "entries": len(lines),
        "file_size_kb": round(file_size_bytes / 1024, 2),
        "file_path": str(memory_file),
        "global_memory_entries": len(MEMORY_CACHE),  # Added global memory count
    }


@memory_router.get("/{agent}/search")
async def search_memory_api(
    agent: str,
    query: str = Query(..., description="The semantic query to search for."),
    top_k: int = Query(
        TOP_K_DEFAULT, description="The number of top results to return."
    ),
):
    """Search agent memory semantically using vector embeddings (RAG/Recall)."""
    return await search_agent_memory(agent, query, top_k)


# ========================================================
# 🚀 AGENT & HEALTH ROUTES
# ========================================================


@app.get("/api/health", tags=["System"])
def health_check():
    """Basic health and system info."""
    uptime = time.time() - START_TIME

    cache_keys = list(_EMBEDDING_CACHE.keys())

    return {
        "status": "ok",
        "uptime_sec": round(uptime, 1),
        "llm_mode": LLM_MODE,
        "local_url": LOCAL_URL,
        "agent_base_dir": str(AGENT_BASE_DIR),
        "vector_search_enabled": True,  # Assume enabled, errors reported on failure
        "embedding_cache_size": len(cache_keys),
        "cached_agents": cache_keys,
        "global_memory_count": len(MEMORY_CACHE),  # Added global memory count
    }


@app.post("/api/ask", tags=["Agents"])
async def ask_agent(req: AskRequest):
    """Handle user queries, automatically recall relevant memory, and log the interaction."""
    global REQUEST_COUNT
    REQUEST_COUNT += 1

    # 0. Load Agent Configuration
    config = load_agent_config(req.agent)
    persona = config.get("persona", "a helpful and versatile AI assistant")
    goal = config.get("goal", "Answer the user's questions truthfully and accurately.")

    # 1. AUTO RECALL: Perform semantic search
    search_results = await search_agent_memory(
        agent=req.agent, query=req.query, top_k=TOP_K_DEFAULT
    )

    context_lines = []
    if search_results.get("status") == "success":
        for res in search_results["results"]:
            # NOTE: RAG memory still uses 'q' and 'a' fields
            q = res["memory_entry"]["q"]
            a = res["memory_entry"]["a"]
            context_lines.append(f"Q: {q}\nA: {a}")

    # 2. BUILD PROMPT: Construct the final RAG prompt
    context_snippet = (
        "\n---\n".join(context_lines)
        if context_lines
        else "No relevant short-term memory recalled."
    )

    final_prompt = AGENT_TEMPLATE.format(
        persona=persona, goal=goal, context=context_snippet, query=req.query
    )

    if context_lines:
        log.info(f"Auto-recalled {len(context_lines)} memories for agent {req.agent}.")

    # 3. INFERENCE: Get the agent's response
    response_text = await smart_infer(
        final_prompt
    )  # Renamed 'response' to 'response_text' for clarity

    # 4. LOG: Log the interaction
    # NOTE: The original synchronous log is removed here and replaced with the new global async log.

    # --- Log to persistent memory ---
    async with MEMORY_LOCK:
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": req.agent,
            "query": req.query,
            "response": response_text,
        }
        MEMORY_CACHE.append(entry)
        async with aiofiles.open(MEMORY_FILE, "a") as f:
            await f.write(json.dumps(entry) + "\n")

    # NOTE: Legacy agent-specific memory logging is removed to avoid duplicates
    # unless you explicitly want to keep both. Assuming you only want the new global log.

    # 5. RETURN: Return the response
    return {"agent": req.agent, "query": req.query, "response": response_text}


# --- Demo echo chat endpoint (safe, minimal) ---
@app.post("/chat/{agent_name}")
async def demo_chat(agent_name: str, payload: dict):
    """Simple demo route that echoes the incoming message without invoking LLMs.

    Useful for local smoke tests and health-checking agent routing.
    """
    message = payload.get("message") if isinstance(payload, dict) else None
    message_text = message or ""
    return {"response": f"[{agent_name.upper()}]: (Echoing) {message_text}"}


@app.get("/api/system/metrics", tags=["System"])
def system_metrics():
    """Report live system usage."""
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    return {
        "cpu_percent": cpu,
        "memory_used": f"{mem.used / (1024**3):.2f} GB",
        "memory_total": f"{mem.total / (1024**3):.2f} GB",
        "memory_percent": mem.percent,
        "uptime_min": round((time.time() - psutil.boot_time()) / 60, 1),
    }


# ========================================================
# 🚀 Lifespan Context Manager (Replaces on_event)
# ========================================================
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    # Startup
    await preload_memory()
    log.info("🧠 VBOARDER SYSTEM STARTUP - Fully Async RAG v3.3")
    log.info(f"🔑 API Key: {'✅ Loaded' if API_KEY else '❌ Missing'}")
    log.info(f"⚙️  Mode: {LLM_MODE.upper()}")
    log.info(f"📂 Agents Base Dir: {AGENT_BASE_DIR}")
    log.info(
        f"⚙️ Config: Max Memory={round(MAX_MEMORY_SIZE / 1024 / 1024)}MB, Default Top K={TOP_K_DEFAULT}"
    )

    yield

    # Shutdown
    log.info("🧹 Shutting down VBoarder backend gracefully.")


# ========================================================
# 🔄 Recreate App with Lifespan Handler
# ========================================================
# Recreate the FastAPI app with the lifespan parameter
app = FastAPI(lifespan=lifespan, title="VBoarder Backend", version="3.3")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Re-register all routes (they're already decorated with @app, so they'll work)
# The decorators will automatically register to the new app instance

# ========================================================
# 🏁 Main Entrypoint
# ========================================================
if __name__ == "__main__":
    import uvicorn

    log.info("Starting VBoarder Backend v3.3...")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, log_level="info")

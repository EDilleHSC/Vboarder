# Agent Function Quick Reference

## Import Statements

```python
# Standard Agents
from agents.CEO.agent_logic import build_ceo_prompt
from agents.CFO.agent_logic import build_cfo_prompt
from agents.COO.agent_logic import build_coo_prompt
from agents.CTO.agent_logic import build_prompt as build_cto_prompt  # or build_cto_prompt
from agents.CLO.agent_logic import build_clo_prompt
from agents.CMO.agent_logic import build_cmo_prompt
from agents.SEC.agent_logic import build_sec_prompt
from agents.AIR.agent_logic import build_air_prompt

# Orchestrator
from agents.COS.agent_logic import build_cos_prompt, load_peer_summaries

# Base Template (for custom agents)
from agents.agent_base_logic import build_agent_prompt
```

## Function Signatures

### Standard Agents

```python
async def build_ceo_prompt(user_input: str) -> str
async def build_cfo_prompt(user_input: str) -> str
async def build_coo_prompt(user_input: str) -> str
async def build_cto_prompt(user_input: str) -> str
async def build_clo_prompt(user_input: str) -> str
async def build_cmo_prompt(user_input: str) -> str
async def build_sec_prompt(user_input: str) -> str
async def build_air_prompt(user_input: str) -> str
```

### COS Orchestrator

```python
async def build_cos_prompt(
    user_input: str,
    peer_summaries: List[Dict[str, Any]] = None
) -> str

async def load_peer_summaries(
    peer_ids: List[str]
) -> List[Dict[str, Any]]
```

### Base Template

```python
async def build_agent_prompt(
    agent_id: str,
    user_input: str,
    max_facts: int = 10,
    max_messages: int = 10,
    custom_instructions: Optional[str] = None
) -> str
```

## Usage Patterns

### Pattern 1: Simple Agent Call

```python
prompt = await build_ceo_prompt("What's our priority?")
response = await llm.generate(prompt)
```

### Pattern 2: Custom Memory Limits

```python
# Using base template directly
prompt = await build_agent_prompt(
    agent_id="CEO",
    user_input="Status update?",
    max_facts=20,        # More context
    max_messages=15
)
```

### Pattern 3: COS Coordination

```python
# Auto-load all peers
prompt = await build_cos_prompt("Coordinate Q4 planning")

# Or pre-load specific peers
peers = await load_peer_summaries(["CEO", "CFO", "CTO"])
prompt = await build_cos_prompt("Budget review", peer_summaries=peers)
```

## Memory Context Structure

Each agent receives:

```python
{
    "agent": "CEO",
    "persona": "You are the CEO of VBoarder...",
    "facts": [
        "Q3 revenue exceeded targets",
        "New product launch planned for Q4",
        ...
    ],
    "recent_messages": [
        {
            "sender": "user",
            "message": "What's our strategy?",
            "timestamp": "2025-10-13T10:30:00Z"
        },
        ...
    ],
    "conversation_history": {
        "session_id": "user123",
        "summary": "Discussion about Q4 planning..."
    }
}
```

## Integration with simple_connector.py

**Before (no memory):**

```python
def chat(self, message):
    response = ollama.chat(
        model=self.model,
        messages=[
            {"role": "system", "content": "You are a CEO"},
            {"role": "user", "content": message}
        ]
    )
    return response
```

**After (with memory):**

```python
async def chat(self, message):
    from agents.CEO.agent_logic import build_ceo_prompt

    # Build memory-enriched system prompt
    system_prompt = await build_ceo_prompt(message)

    response = ollama.chat(
        model=self.model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    )
    return response
```

## Agent Role Mapping

| Agent ID | Function         | Module Path            |
| -------- | ---------------- | ---------------------- |
| CEO      | build_ceo_prompt | agents.CEO.agent_logic |
| CFO      | build_cfo_prompt | agents.CFO.agent_logic |
| COO      | build_coo_prompt | agents.COO.agent_logic |
| CTO      | build_cto_prompt | agents.CTO.agent_logic |
| CLO      | build_clo_prompt | agents.CLO.agent_logic |
| CMO      | build_cmo_prompt | agents.CMO.agent_logic |
| SEC      | build_sec_prompt | agents.SEC.agent_logic |
| AIR      | build_air_prompt | agents.AIR.agent_logic |
| COS      | build_cos_prompt | agents.COS.agent_logic |

## Testing

```bash
# Test all agent logic
pytest tests_flat/test_agent_logic.py -v

# Test specific agent
pytest tests_flat/test_agent_logic.py::test_ceo_prompt_building -v

# Test COS orchestration
pytest tests_flat/test_agent_logic.py::test_cos_orchestration_prompt -v
```

## Common Issues

**Q: ModuleNotFoundError for agent_base_logic?**
A: Ensure project root is in sys.path (handled by conftest.py in tests)

**Q: Agent context is empty?**
A: Memory files are created on first write. Use `/api/memory` endpoint to populate.

**Q: COS peer loading is slow?**
A: Pre-load peer summaries and cache them:

```python
peers = await load_peer_summaries(relevant_peers_only)
prompt = await build_cos_prompt(msg, peer_summaries=peers)
```

**Q: How to add a new agent?**
A: Use the base template:

```python
# agents/NEW_AGENT/agent_logic.py
from agents.agent_base_logic import build_agent_prompt

async def build_new_agent_prompt(user_input: str) -> str:
    custom_instructions = """Your role-specific instructions..."""
    return await build_agent_prompt(
        agent_id="NEW_AGENT",
        user_input=user_input,
        max_facts=10,
        max_messages=10,
        custom_instructions=custom_instructions
    )
```

# VBoarder Agent Memory Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                                 │
│                    "What's our Q4 strategy?"                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FastAPI Endpoint                                │
│                   POST /chat/CEO                                     │
│                   (api/main.py)                                      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   AgentConnector                                     │
│                (api/simple_connector.py)                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────┐          │
│  │  1. Call build_ceo_prompt(user_input)                │          │
│  └────────────┬─────────────────────────────────────────┘          │
└───────────────┼──────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Agent Logic Layer                                  │
│              (agents/CEO/agent_logic.py)                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────┐          │
│  │  2. load_agent_context("CEO")                        │          │
│  │     ↓                                                 │          │
│  │  3. Load from api/memory_manager.py                  │          │
│  └────────────┬─────────────────────────────────────────┘          │
└───────────────┼──────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Memory Manager                                     │
│                (api/memory_manager.py)                               │
│                                                                      │
│  ┌──────────────────────────────────────────────────────┐          │
│  │  4. Read from agent's memory files:                  │          │
│  │     • agents/CEO/memory.json                         │          │
│  │     • agents/CEO/conversation_history.json           │          │
│  │     • agents/CEO/memory.jsonl                        │          │
│  └────────────┬─────────────────────────────────────────┘          │
└───────────────┼──────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Memory Context                                     │
│                                                                      │
│  {                                                                   │
│    "agent": "CEO",                                                   │
│    "persona": "You are the CEO...",                                 │
│    "facts": ["Q3 exceeded targets", ...],                           │
│    "recent_messages": [                                             │
│      {"sender": "user", "message": "...", "timestamp": "..."},      │
│      ...                                                             │
│    ],                                                                │
│    "conversation_history": {...}                                    │
│  }                                                                   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Prompt Builder                                     │
│              (agents/CEO/agent_logic.py)                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────┐          │
│  │  5. Inject context into prompt template:            │          │
│  │                                                       │          │
│  │  # CEO Agent                                         │          │
│  │  ## Your Role & Persona                              │          │
│  │  You are the CEO of VBoarder...                     │          │
│  │                                                       │          │
│  │  ## Your Knowledge & Context                         │          │
│  │  - Q3 revenue exceeded targets                       │          │
│  │  - New product launch planned                        │          │
│  │                                                       │          │
│  │  ## Recent Conversation                              │          │
│  │  user: What's our priority?                          │          │
│  │  CEO: Focus on product quality...                    │          │
│  │                                                       │          │
│  │  ## Current Request                                  │          │
│  │  User: What's our Q4 strategy?                       │          │
│  └────────────┬─────────────────────────────────────────┘          │
└───────────────┼──────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     LLM (Ollama/OpenAI)                              │
│                                                                      │
│  ┌──────────────────────────────────────────────────────┐          │
│  │  6. Generate response with full context              │          │
│  │                                                       │          │
│  │  Based on Q3 performance and upcoming product        │          │
│  │  launch, our Q4 strategy should focus on...         │          │
│  └────────────┬─────────────────────────────────────────┘          │
└───────────────┼──────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Response Pipeline                                  │
│                                                                      │
│  ┌──────────────────────────────────────────────────────┐          │
│  │  7. Extract facts from response                      │          │
│  │  8. Update conversation history                      │          │
│  │  9. Append to memory.jsonl                           │          │
│  │  10. Return response to user                         │          │
│  └────────────┬─────────────────────────────────────────┘          │
└───────────────┼──────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      USER RESPONSE                                   │
│     "Based on Q3 performance and upcoming product launch..."         │
└─────────────────────────────────────────────────────────────────────┘
```

## COS Orchestration Flow (Multi-Agent)

```
┌─────────────────────────────────────────────────────────────────────┐
│                  USER REQUEST to COS                                 │
│            "Coordinate Q4 product launch"                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   COS Agent Logic                                    │
│              (agents/COS/agent_logic.py)                             │
│                                                                      │
│  ┌──────────────────────────────────────────────────────┐          │
│  │  1. Load COS's own context                           │          │
│  │     context = await load_agent_context("COS")        │          │
│  │                                                       │          │
│  │  2. Load peer agent summaries (PARALLEL)             │          │
│  │     peer_ids = ["CEO","CFO","CTO","CMO"...]          │          │
│  │     peers = await load_peer_summaries(peer_ids)      │          │
│  └────────────┬─────────────────────────────────────────┘          │
└───────────────┼──────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Parallel Peer Context Loading                           │
│                   (asyncio.gather)                                   │
│                                                                      │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐       │
│  │  CEO   │  │  CFO   │  │  CTO   │  │  CMO   │  │  COO   │       │
│  │ facts  │  │ facts  │  │ facts  │  │ facts  │  │ facts  │       │
│  │ msgs   │  │ msgs   │  │ msgs   │  │ msgs   │  │ msgs   │       │
│  └────┬───┘  └────┬───┘  └────┬───┘  └────┬───┘  └────┬───┘       │
│       │           │           │           │           │             │
│       └───────────┴───────────┴───────────┴───────────┘             │
│                            │                                         │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│               COS Orchestration Prompt                               │
│                                                                      │
│  # CHIEF OF STAFF - Executive Orchestrator                          │
│                                                                      │
│  ## Executive Team Status                                           │
│  ### CEO                                                             │
│  Recent focus:                                                       │
│    - Q4 strategy approved                                           │
│    - Focus on product quality                                       │
│  Last activity: Reviewed board presentation...                      │
│                                                                      │
│  ### CFO                                                             │
│  Recent focus:                                                       │
│    - Q4 budget allocated                                            │
│    - Marketing spend increased                                      │
│  Last activity: Approved product launch budget...                   │
│                                                                      │
│  ### CTO                                                             │
│  Recent focus:                                                       │
│    - Product development on track                                   │
│    - Infrastructure scaling planned                                 │
│  Last activity: Technical architecture reviewed...                  │
│                                                                      │
│  ### CMO                                                             │
│  Recent focus:                                                       │
│    - Launch campaign planned                                        │
│    - Target audience defined                                        │
│  Last activity: Marketing materials in progress...                  │
│                                                                      │
│  ## Your Mission                                                     │
│  Coordinate Q4 product launch across all departments                │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     LLM Response                                     │
│                                                                      │
│  "Based on the team's current status:                               │
│   • CEO has approved Q4 strategy                                    │
│   • CFO allocated budget                                            │
│   • CTO confirms development on track                               │
│   • CMO has campaign ready                                          │
│                                                                      │
│  I recommend coordinating:                                          │
│  1. Schedule launch date with CTO (technical readiness)             │
│  2. Align marketing timeline with CMO                               │
│  3. Confirm budget allocation with CFO                              │
│  4. Present coordinated plan to CEO for final approval..."          │
└─────────────────────────────────────────────────────────────────────┘
```

## Memory File Structure

```
agents/
├── CEO/
│   ├── memory.json                    # Structured state
│   ├── conversation_history.json      # Session dialogue
│   └── memory.jsonl                   # Audit log
├── CFO/
│   ├── memory.json
│   ├── conversation_history.json
│   └── memory.jsonl
├── CTO/
│   ├── memory.json
│   ├── conversation_history.json
│   └── memory.jsonl
└── ...

memory.json format:
{
  "facts": ["fact1", "fact2", ...],
  "messages": [
    {"sender": "user", "message": "...", "timestamp": "..."},
    ...
  ],
  "context": {...}
}

memory.jsonl format (append-only log):
{"timestamp":"2025-10-13T10:30:00Z","section":"facts","entry":"Q3 revenue exceeded targets"}
{"timestamp":"2025-10-13T10:31:00Z","section":"messages","entry":{"sender":"user","message":"..."}}
```

## Key Features

✅ **Per-Agent Memory** - Each agent maintains isolated context
✅ **Async I/O** - Non-blocking file operations
✅ **File Locking** - Thread-safe concurrent access
✅ **Pydantic Validation** - Type-safe data models
✅ **RAG-Ready** - Facts stored for retrieval augmentation
✅ **Audit Trail** - JSONL log for complete history
✅ **COS Orchestration** - Multi-agent coordination with peer context
✅ **REST API** - Full CRUD for memory and conversations
✅ **Test Coverage** - Comprehensive test suite

## Performance Characteristics

| Operation                   | Latency   | Notes                   |
| --------------------------- | --------- | ----------------------- |
| Single agent context load   | 10-50ms   | Depends on memory size  |
| COS peer loading (8 agents) | 50-150ms  | Parallel async loading  |
| Memory write (JSON)         | 5-20ms    | File locking overhead   |
| Memory write (JSONL)        | 2-10ms    | Append-only, faster     |
| Prompt building             | 1-5ms     | String formatting       |
| Full chat cycle             | 100-500ms | Load + build + LLM call |

## Dependencies

- `api/memory_manager.py` - Memory persistence and loading
- `agents/agent_base_logic.py` - Shared prompt builder template
- `agents/{ROLE}/agent_logic.py` - Role-specific logic (9 agents)
- `api/simple_connector.py` - LLM connector (Ollama/OpenAI)
- `api/main.py` - FastAPI endpoints

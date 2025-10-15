# 🧭 VBOARDER DEVELOPMENT SOP

**Version:** 1.0
**Last Updated:** $(date +%F)

---

## 🧱 1. Environment Structure

vboarder/
├── agents/
│ ├── agent_runtime/ ← Core server logic
│ ├── agents/ ← Agent memory + config folders (migrated from agents_v2)
├── docs/ ← Documentation, API notes
├── run.sh ← Auto-start script
├── .env ← Environment settings
├── requirements.txt ← Dependencies list
└── README.md

### Example `.env` file

```env
LLM_MODE=local
LOCAL_URL=http://localhost:11434
OPENAI_URL=https://api.openai.com/v1/chat/completions
API_KEY=your_openai_api_key_here
MAX_MEMORY_MB=5
TOP_K_DEFAULT=3

./run.sh


pkill -f "uvicorn agents.agent_runtime.server"


🧩 3. Development Workflow
Step	Action	Notes
1️⃣ Code	Edit inside VS Code (via WSL path /mnt/d/...)	Work directly in Linux context
2️⃣ Test	./run.sh → Open http://localhost:8000/docs	Verify all endpoints
3️⃣ Commit	git add . && git commit -m "update: short summary"	Use clear, descriptive messages
4️⃣ Sync	Push to main/dev branches	Keep dev branch isolated for experiments

🧩 4. Agent Design Guidelines

Each agent has its own folder under:

agents/{agent_name}/
│
├── memory.jsonl        ← Dynamic chat memory
├── memory_summary.txt  ← Summarized long-term memory
└── config.json         ← Personality & behavior profile

🧮 5. Versioning & Backups
Task	Frequency	Command / Notes
Memory backup	Weekly	Copy agents/*/memory*.jsonl → /backups/
Code snapshot	After major update	git tag -a vX.X -m "checkpoint"
Dependency freeze	After stable test	pip freeze > requirements.txt
🧾 6. Testing Checklist

✅ Verify endpoints:

 /api/health → system and cache info

 /api/agents → lists all available agents

 /api/memory/{agent} → fetches full memory

 /api/memory/{agent}/add → appends correctly

 /api/memory/{agent}/summary → summarizes and archives

 /api/ask → produces context-aware responses

✅ Confirm:

Lazy embedding loads only once (SentenceTransformer model).

.env matches your runtime mode (local / openai).

Memory updates correctly trigger cache invalidation.

🧰 7. Logging & Observability

All logs follow the format:

[HH:MM:SS] INFO: message


You can also persist logs:

./run.sh | tee logs/vboarder_$(date +%F).log

🧩 8. Team SOP (Optional)
Role	Focus	Notes
Lead Dev (You)	Core architecture, runtime optimization	Manages deployment stability
Memory Engineer	Embeddings, recall, summarization	Improves AI continuity
Frontend Dev	Dashboard / UX	Connects FastAPI → web interface
Ops / Infra	Docker / uptime / logging	Prepares for long-term hosting
🚀 9. Long-Term Targets

 Integrate persistent DB (SQLite / Redis / Chroma)

 Add async background memory scheduling

 Build dashboard UI for live monitoring

 Add authentication & API tokens

 Dockerize backend for one-line deployment

 Continuous evaluation of recall quality and agent personality tuning

🧩 10. Quality Control Standards
Metric	Goal	Description
Latency	< 2.0s	Average /api/ask response time
Memory Size	< 5 MB	Guardrail per agent
Recall Accuracy	> 80%	Vector similarity recall precision
Summarization Loss	< 10%	Difference between archived and summary context
💡 Tips

Keep your .env outside of version control (.gitignore it).

Test agents frequently with /api/ask using memory recall on/off.

Always summarize (/summary) before memory grows too large.

Use clear, meaningful config.json personas — they shape the intelligence.

📦 Command Quick Reference
# Run API
./run.sh

# Check health
curl http://localhost:8000/api/health

# List agents
curl http://localhost:8000/api/agents

# Add memory entry
curl -X POST "http://localhost:8000/api/memory/TEMP/add" -H "Content-Type: application/json" -d '{"q":"test","a":"response"}'

# Ask an agent
curl -X POST "http://localhost:8000/api/ask" -H "Content-Type: application/json" -d '{"agent":"TEMP","query":"Who am I?"}'


🧠 VBoarder is built for persistent intelligence.
Follow this SOP to maintain stable memory systems, predictable behavior, and safe continuous evolution.

Built by: VBoarder Core Team
Maintainer: You 🧠


---

Would you like me to automatically create this as `docs/DEV_SOP.md` in your repo (so you can commit and push it)?
I can also generate a **short CLI version** (a `.bash` quick reference) if you want a lightweight terminal guide.
```

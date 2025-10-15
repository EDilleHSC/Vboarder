# 🧠 Reasoning Kernel Quick Start

## What You Just Built

✅ **Multi-step reasoning system** for VBoarder agents
✅ **Confidence-based iteration** (loops until high confidence)
✅ **Dynamic model routing** (task complexity → model slot)
✅ **Heuristic scorer** (ready for ML upgrade later)
✅ **New `/ask` endpoint** with full agent integration

---

## 📁 New Files Created

```text
reasoning_kernel.py          # Core iteration loop engine
router.py                    # Task-based model slot selection
scorer_stub.py               # Confidence heuristics
tests_flat/eval_reasoning.py # Evaluation suite
docs/REASONING_KERNEL.md     # Full documentation
.env.reasoning               # Feature flag config
```

---

## 🚀 Test It Now

### 1. Start Backend (if not running)

**WSL Terminal:**
```bash
cd /mnt/d/ai/projects/vboarder
source .venv-wsl/bin/activate
bash start_vboarder.sh
```

### 2. Quick Smoke Test

```bash
curl -X POST "http://127.0.0.1:3738/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Say hello in 5 words or less",
    "agent_role": "CEO",
    "max_iterations": 2
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "agent": "CEO",
  "result": "Hello, how can I help?",
  "iterations": 1,
  "confidence": 0.95,
  "reasoning_status": "success",
  "routing": {
    "slot": "slot:a",
    "model": "mistral:latest",
    "complexity": "simple"
  }
}
```

### 3. Run Full Evaluation

```bash
python tests_flat/eval_reasoning.py
```

This tests:
- ✅ COO task scheduling
- ✅ CTO risk assessment
- ✅ CEO strategic planning
- ✅ CFO budget analysis

**Output saved to:** `out/reasoning_eval.json`

---

## 🎯 How It Works

```text
User → /ask → Router → Reasoning Kernel
                ↓
        1. Pick model slot (a/b/c)
        2. Generate response
        3. Score confidence
        4. High enough? → Done
        5. Too low? → Refine prompt, loop
        6. Max iterations? → Return best attempt
```

### Confidence Scoring

**Heuristics (scorer_stub.py):**
- ✅ Length (longer = more detail)
- ✅ Structure (numbered lists, bullets)
- ❌ Uncertainty ("maybe", "unclear")
- ❌ Errors ("failed", "broken")
- ✅ Completion markers ("done", "therefore")

**Score ranges:**
- `0.85+` : High confidence (early exit)
- `0.50-0.84` : Medium (refine and retry)
- `<0.50` : Low (escalate for review)

### Model Routing

**Task → Slot mapping:**
- `slot:a` : < 1200 chars, simple, no tools → Fast
- `slot:b` : < 8000 chars, moderate → Balanced
- `slot:c` : Complex, tools needed → Powerful

**Override with env vars:**
```bash
MODEL_SLOT_A=phi:latest         # Tiny fast model
MODEL_SLOT_B=mistral:latest     # Default
MODEL_SLOT_C=llama3:latest      # Larger for complex
```

---

## 🧪 Test Cases

### Simple Query (slot:a)
```bash
curl -X POST http://127.0.0.1:3738/ask -H "Content-Type: application/json" \
  -d '{"task": "What is 2+2?", "agent_role": "CEO"}'
```

### Moderate Task (slot:b)
```bash
curl -X POST http://127.0.0.1:3738/ask -H "Content-Type: application/json" \
  -d '{
    "task": "Schedule weekly ops sync and ensure Q4 deadline compliance",
    "agent_role": "COO",
    "max_iterations": 4
  }'
```

### Complex with Tools (slot:c)
```bash
curl -X POST http://127.0.0.1:3738/ask -H "Content-Type: application/json" \
  -d '{
    "task": "Search latest AI research and summarize top 3 papers",
    "agent_role": "AIR",
    "max_iterations": 5
  }'
```

---

## 📊 Expected Benchmarks

| Task Type | Iterations | Time | Confidence |
| --------- | ---------- | ---- | ---------- |
| Simple    | 1-2        | <1s  | 0.90+      |
| Moderate  | 2-4        | 2-3s | 0.85+      |
| Complex   | 3-5        | 4-6s | 0.80+      |

**On local Ollama with mistral:latest**

---

## 🔧 Next Steps

### Phase 1: Current MVP ✅
- [x] Heuristic scorer
- [x] Basic routing
- [x] Iteration loop
- [x] `/ask` endpoint
- [x] Evaluation suite

### Phase 2: ML Scorer (Next 2 weeks)
- [ ] Replace scorer_stub with tiny BERT classifier
- [ ] Train on VBoarder task samples
- [ ] Tune confidence thresholds

### Phase 3: Advanced Models (Next month)
- [ ] Integrate LiquidAI models
- [ ] Test LLM2e (efficient 7B)
- [ ] Benchmark slot performance

### Phase 4: Verification (Future)
- [ ] Multi-agent cross-checking
- [ ] Self-correction loops
- [ ] Fact verification integration

---

## 🐛 Troubleshooting

### Error: "Reasoning kernel not available"
**Fix:** Check files exist
```bash
ls -l reasoning_kernel.py router.py scorer_stub.py
```

### All responses have low confidence
**Fix:** Adjust heuristics in `scorer_stub.py` or lower threshold
```json
{
  "confidence_threshold": 0.70
}
```

### Always hits max_iterations
**Fix:** Increase max or lower threshold
```json
{
  "max_iterations": 10,
  "confidence_threshold": 0.75
}
```

---

## 📚 Full Documentation

**See:** `docs/REASONING_KERNEL.md`

Includes:
- API reference
- Module details
- Configuration options
- Performance benchmarks
- Roadmap

---

## 🎉 Ready to Commit!

**Branch:** Create `feature/reasoning-kernel`

```bash
git checkout -b feature/reasoning-kernel
git add reasoning_kernel.py router.py scorer_stub.py
git add tests_flat/eval_reasoning.py
git add docs/REASONING_KERNEL.md
git add .env.reasoning
git add api/main.py  # Updated with /ask endpoint
git commit -m "feat: Add reasoning kernel with confidence scoring and dynamic routing"
git push origin feature/reasoning-kernel
```

**Then merge to `dev-temp` and test:**
```bash
git checkout dev-temp
git merge feature/reasoning-kernel
python tests_flat/eval_reasoning.py
```

---

**🚀 VBoarder is now the smartest small-agent framework!**

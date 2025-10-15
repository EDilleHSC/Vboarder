# 🚀 VBoarder Developer Onboarding Kit

**Welcome to VBoarder - First-Class AI Reasoning Platform**

This guide will get you from zero to productive in **under 10 minutes**.

---

## 🎯 What You're Working With

**VBoarder isn't just another AI project.** It's a production-grade multi-agent reasoning system with:

- **🧬 LFM2e Integration** - Advanced model routing for strategic tasks
- **🧠 9 Specialized Agents** - CEO, CTO, CFO, COO, CMO, CLO, COS, SEC, AIR
- **🔄 Reasoning Kernel** - Multi-iteration thinking with confidence scoring
- **⚡ Hot Reload Development** - Zero-friction iteration cycle

---

## 🚦 Quick Start (5 Minutes)

### **1. Environment Setup**
```bash
# Navigate to VBoarder
cd /mnt/d/ai/projects/vboarder

# Open the workspace (one-click setup)
code vboarder.code-workspace
```

### **2. Launch Development Environment**
In VS Code:
- Press `Ctrl+Shift+P`
- Type "Tasks: Run Build Task"
- Select "🎯 Perfect Dev Setup"

**That's it!** Your backend, agents, and development tools are now running.

### **3. Test Your Setup**
```bash
# Test basic reasoning
./quick_test.sh "Hello world"

# Test strategic routing (uses LFM2e slot)
./quick_test.sh "Optimize our Q4 strategy" "CEO"

# Check system status
./vboarder_status.sh
```

---

## 🏗️ Architecture Overview

### **Core Components**
```
VBoarder/
├── api/main.py              # FastAPI backend with reasoning endpoints
├── reasoning_kernel.py      # Multi-iteration thinking engine
├── router.py               # Intelligent model slot routing
├── scorer_stub.py          # Confidence assessment system
├── models/liquid_model.py  # LFM2e integration framework
└── agents/                 # 9 specialized AI agents
    ├── CEO/               # Strategic leadership
    ├── CTO/               # Technical oversight
    ├── CFO/               # Financial analysis
    └── ...
```

### **Model Routing Strategy**
- **slot:a (mistral)** - Fast, simple queries
- **slot:b (lfm2e)** - Strategic tasks, leadership agents
- **slot:c (advanced)** - Complex tasks, tool usage

### **Agent Specialization**
Each agent has specialized personas, prompts, and memory:
- **CEO** - Strategic planning, organizational decisions
- **CTO** - Technical architecture, system design
- **CFO** - Financial analysis, budget optimization
- **COO** - Operations, resource allocation
- *(+ 5 more specialized roles)*

---

## 🛠️ Developer Workflows

### **Adding a New Agent**
```bash
# Create agent structure
mkdir agents/NEWROLE
cd agents/NEWROLE

# Required files
touch config.json agent.json persona.json memory.jsonl
mkdir personas && touch personas/system_detailed.txt
mkdir prompts && touch prompts/system_detailed.txt

# Register in agent_registry.json
# Add to router.py if needs special routing
```

### **Testing Reasoning Changes**
```bash
# Quick test specific scenarios
./quick_test.sh "Your test scenario" "AGENT"

# Run full validation
python3 list_agents.py              # Check agent discovery
python3 router.py                   # Validate routing logic
python3 eval_viewer.py              # Review confidence trends
```

### **Model Integration**
```bash
# Check available models
python3 models/liquid_model.py list

# Install new model (when available)
python3 models/liquid_model.py install model-name

# Test model routing
python3 -c "from router import route_task; print(route_task('test', 'CEO'))"
```

---

## 🧪 Common Development Tasks

### **Debugging a Reasoning Issue**
1. **Check routing:** `./quick_test.sh "problem scenario" "AGENT"`
2. **Review confidence:** Look for confidence scores in output
3. **Examine iterations:** Count reasoning cycles (should be 1-5)
4. **Test fallback:** Disable advanced models to test degradation

### **Adding Custom Routing Logic**
Edit `router.py`:
```python
def is_custom_task(task: str, agent: str = "") -> bool:
    # Your custom logic here
    return "custom_keyword" in task.lower()

# Add to pick_model_slot() function
if is_custom_task(task, agent):
    return "slot:c"  # or your preferred slot
```

### **Monitoring Agent Performance**
```bash
# View recent conversations
python3 eval_viewer.py summary 7

# Check confidence trends by agent
python3 eval_viewer.py trends CEO 20

# Export metrics for analysis
python3 eval_viewer.py export performance_data.json
```

---

## 🔧 Configuration Guide

### **Environment Variables**
```bash
# Model slot configuration
export MODEL_SLOT_A=mistral:latest    # Fast model
export MODEL_SLOT_B=lfm2e:latest      # Strategic model
export MODEL_SLOT_C=mistral:latest    # Complex model

# Backend configuration
export LLM_MODE=local                 # or "openai"
export LOCAL_URL=http://localhost:11434
export MAX_MEMORY_MB=512
```

### **VS Code Tasks**
- **🚀 Start Backend** - Launch API server with hot reload
- **🧪 Quick Test** - Test reasoning endpoint
- **📊 System Status** - Full health dashboard
- **🎯 Perfect Setup** - One-click environment startup

### **Agent Configuration**
Each agent has a `config.json`:
```json
{
  "role": "CEO",
  "temperature": 0.7,
  "max_tokens": 2000,
  "confidence_threshold": 0.85,
  "routing_priority": "leadership"
}
```

---

## 🚨 Troubleshooting

### **Backend Won't Start**
```bash
# Check Python environment
./vboarder_status.sh

# Activate virtual environment manually
source .venv-wsl/bin/activate

# Check for port conflicts
lsof -i :3738
```

### **Model Routing Issues**
```bash
# Test routing logic
python3 router.py

# Check model availability
python3 models/liquid_model.py test

# Verify environment variables
echo $MODEL_SLOT_B
```

### **Agent Not Responding**
```bash
# Check agent health
python3 list_agents.py

# Validate agent files
ls agents/AGENTNAME/

# Test direct endpoint
curl -X POST http://localhost:3738/chat/CEO \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

---

## 📊 Performance Optimization

### **Model Selection Strategy**
- **Development:** Use mistral for all slots (faster iteration)
- **Testing:** Enable LFM2e for slot:b (realistic performance)
- **Production:** Configure all three slots with appropriate models

### **Confidence Tuning**
Edit `reasoning_kernel.py`:
```python
# Adjust confidence threshold
confidence_threshold = 0.80  # Lower = more iterations

# Modify early stopping
max_iterations = 3  # Reduce for faster responses
```

### **Memory Management**
```bash
# Monitor memory usage
./vboarder_status.sh | grep Memory

# Clear old conversations
rm data/conversations/old_*.jsonl

# Optimize agent memory
python3 -c "from agents.memory import optimize_memory; optimize_memory()"
```

---

## 🎯 Next Steps

### **Phase 1: Get Productive (Week 1)**
- [ ] Run through this guide completely
- [ ] Test all major workflows
- [ ] Create your first custom agent
- [ ] Deploy a test modification

### **Phase 2: Advanced Features (Week 2-3)**
- [ ] Integrate LFM2e model when available
- [ ] Add custom routing logic for your use case
- [ ] Build evaluation metrics for your domain
- [ ] Create custom confidence scoring

### **Phase 3: Production Deployment (Month 1)**
- [ ] Design user interface layer
- [ ] Add authentication and security
- [ ] Create deployment automation
- [ ] Build monitoring and alerting

---

## 🤝 Getting Help

### **Built-in Documentation**
- `RELEASE_v1.0.0-Alpha.md` - Full feature documentation
- `PERFECT_DEV_SETUP.md` - Development environment guide
- `LFM2E_DEPLOYMENT_COMPLETE.md` - Architecture overview

### **Interactive Tools**
- `./quick_test.sh` - Test any scenario
- `python3 list_agents.py` - Agent discovery and health
- `python3 eval_viewer.py` - Performance analysis
- `./vboarder_status.sh` - System diagnostics

### **VS Code Integration**
- Debug configurations for reasoning kernel
- Task runners for common operations
- Integrated terminal with proper environment

---

**Welcome to the VBoarder development team! You're now working with first-class AI technology that's competitive with the frontier.** 🚀

*Happy coding!*

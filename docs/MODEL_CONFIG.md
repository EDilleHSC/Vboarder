# VBoarder Model Configuration Guide

## ⚡ **Critical: We Use `mistral`, NOT `mixtral`**

### 🎯 **Official VBoarder Model**

```bash
# Correct model
ollama pull mistral
ollama run mistral

# ❌ WRONG - Do NOT use
ollama pull mixtral  # Too large (80GB), too slow
```

---

## 📊 **Why `mistral` Over `mixtral`?**

| Factor        | `mistral` ✅                   | `mixtral` ❌                         |
| ------------- | ------------------------------ | ------------------------------------ |
| **Size**      | ~4GB                           | ~80GB                                |
| **Speed**     | Fast (local dev)               | Slow startup/inference               |
| **RAM**       | 8GB minimum                    | 64GB+ recommended                    |
| **Use Case**  | VBoarder agents (7B optimized) | Large-scale production               |
| **Conflicts** | None                           | Breaks backend with wrong model name |

---

## 🔧 **Configuration**

### **1. Ollama CLI**

```bash
# Pull the correct model
ollama pull mistral

# Verify installation
ollama list | grep mistral

# Test it
ollama run mistral
```

### **2. VBoarder Backend (`api/main.py` / `server.py`)**

Default model is already set to `mistral` in environment variables:

```python
# In server.py or simple_connector.py
DEFAULT_MODEL = os.getenv("LOCAL_MODEL", "mistral")
```

No changes needed if using defaults.

### **3. Agent Configuration (`agents/*/config.json`)**

Each agent should specify `mistral`:

```json
{
  "role": "CEO",
  "model": "mistral",
  "temperature": 0.7
}
```

**Do NOT use:**

```json
{
  "model": "mixtral" // ❌ WRONG
}
```

### **4. MCP Configuration (`mcp.json`)**

If you're using Model Context Protocol, configure for `mistral`:

```json
{
  "servers": {
    "vboarder/mistral": {
      "type": "stdio",
      "command": "ollama",
      "args": ["run", "mistral"],
      "env": {
        "OLLAMA_HOST": "http://127.0.0.1:11434"
      }
    }
  }
}
```

**Remove or override any `mixtral` entries:**

```json
{
  "servers": {
    "ollama/mixtral": null // Disable if present
  }
}
```

---

## 🐛 **Common Issues**

### **Issue: Backend tries to use `mixtral`**

**Symptoms:**

```
Error: Model 'mixtral' not found
Failed to connect to Ollama
500 Internal Server Error
```

**Fix:**

1. Check agent configs:

   ```bash
   grep -r "mixtral" agents/*/config.json
   ```

2. Replace with `mistral`:

   ```bash
   find agents/ -name "config.json" -exec sed -i 's/"mixtral"/"mistral"/g' {} \;
   ```

3. Verify environment:
   ```bash
   echo $LOCAL_MODEL  # Should be empty or "mistral"
   ```

### **Issue: Copilot/MCP auto-installs `mixtral`**

**Symptoms:**

```
ollama pull mixtral
Pulling manifest... (this will take a while)
80GB download started...
```

**Fix:**

1. **Cancel the download:**

   ```bash
   Ctrl + C
   ```

2. **Remove partial download:**

   ```bash
   ollama rm mixtral
   ```

3. **Update MCP config** to prevent auto-install (see section 4 above)

4. **Add to `.gitignore`:**
   ```
   mcp.json
   ```

### **Issue: Agent config references wrong model**

**Fix script:**

```bash
#!/bin/bash
# Fix all agent configs to use mistral

for agent_dir in agents/*/; do
    config_file="${agent_dir}config.json"
    if [ -f "$config_file" ]; then
        # Backup
        cp "$config_file" "${config_file}.bak"

        # Replace mixtral with mistral
        sed -i 's/"model":\s*"mixtral"/"model": "mistral"/g' "$config_file"

        echo "✅ Fixed: $config_file"
    fi
done

echo "✅ All agent configs updated to use 'mistral'"
```

---

## 📝 **VBoarder Standard Models**

### **Primary (Required):**

```bash
ollama pull mistral
```

### **Optional (for testing):**

```bash
ollama pull llama3      # Alternative 8B model
ollama pull phi         # Lightweight 2.7B model (fast)
```

### **❌ NOT USED:**

```bash
# Do NOT install these for VBoarder
ollama pull mixtral     # Too large
ollama pull llama2      # Deprecated
ollama pull codellama   # Specialized, not needed
```

---

## 🔍 **Verification Checklist**

```bash
# 1. Verify Ollama models
ollama list | grep mistral
# Should show: mistral:latest

# 2. Check agent configs
grep -r '"model"' agents/*/config.json | grep -v "mistral"
# Should return nothing (or only commented lines)

# 3. Test backend connection
curl -X POST http://127.0.0.1:3738/chat/CEO \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}' | jq .response
# Should return CEO response using mistral

# 4. Verify no mixtral references
grep -ri "mixtral" . --exclude-dir=node_modules --exclude-dir=.git
# Should only show this documentation file
```

---

## 🚨 **For AI Assistants / Auto-Scripts**

If you're an AI assistant (Copilot, Claude, etc.) or automated script:

1. ✅ **Always use `mistral`** for VBoarder
2. ❌ **Never auto-install `mixtral`** without explicit user request
3. 🔍 **Check existing config** before suggesting model changes
4. 📝 **Refer to this document** when unsure about model selection

**Default response for "what model should I use?":**

> VBoarder uses `mistral` (7B parameter model). Install with: `ollama pull mistral`

---

## 📞 **Support**

**Still seeing `mixtral` references?**

Run this audit:

```bash
# Find all mixtral references
grep -ri "mixtral" . \
  --exclude-dir=node_modules \
  --exclude-dir=.git \
  --exclude-dir=.venv \
  --exclude-dir=.venv-wsl \
  --exclude=MODEL_CONFIG.md
```

Then report the files that need fixing.

# VS Code Development Environment Setup Guide

## 🎯 Overview

This guide documents the complete VS Code workspace configuration for VBoarder, providing one-click launchers, debugging configurations, and productivity enhancements.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration Files](#configuration-files)
3. [Task Runners](#task-runners)
4. [Debugging](#debugging)
5. [Extensions](#extensions)
6. [Settings](#settings)
7. [Workflows](#workflows)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### First Time Setup

1. **Open VBoarder workspace in VS Code:**

   ```powershell
   code d:\ai\projects\vboarder
   ```

2. **Install recommended extensions:**

   - VS Code will prompt to install workspace extensions
   - Click "Install All" or review individually

3. **Select Python interpreter:**

   - Press `Ctrl+Shift+P`
   - Type: "Python: Select Interpreter"
   - Choose: `.venv-wsl/bin/python`

4. **Verify WSL integration:**
   ```powershell
   wsl --version
   ```

### Launch Full Stack (One Command)

```
Ctrl+Shift+P → "Tasks: Run Task" → "🔄 Full Stack Startup"
```

This launches:

- ✅ Backend API (port 3738)
- ✅ DevDash (port 4545)

---

## 📁 Configuration Files

All configuration is in `.vscode/`:

```
.vscode/
├── tasks.json          # Task runners (13 tasks)
├── launch.json         # Debug configurations (6 configs)
├── settings.json       # Project settings
├── extensions.json     # Recommended extensions (17)
└── README.md          # Configuration documentation
```

### tasks.json - 13 Available Tasks

| Task                          | Description                 | Shortcut                  |
| ----------------------------- | --------------------------- | ------------------------- |
| 🚀 Start Backend (WSL)        | Launch FastAPI on port 3738 | `Ctrl+Shift+P` → Run Task |
| 🔧 Run Agent Repair (Dry Run) | Preview repairs             | Same                      |
| 🔧 Run Agent Repair (Execute) | Execute repairs             | Same                      |
| ✅ Validate Hardening         | Check v1.1 improvements     | Same                      |
| 🧪 Run Smoke Tests            | Execute 15 beta tests       | Same                      |
| 🧹 Cleanup Root (Dry Run)     | Preview cleanup             | Same                      |
| 🧹 Cleanup Root (Execute)     | Execute cleanup             | Same                      |
| 🧪 Test All Agents            | Test 9 agent endpoints      | Same                      |
| 🔍 Validate All Systems       | Comprehensive validation    | Same                      |
| 📊 Start DevDash              | Launch dashboard port 4545  | Same                      |
| 🧪 Run Pytest                 | Execute unit tests          | Same                      |
| 📝 Generate Shift Dashboard   | Create shift report         | Same                      |
| 🔄 Full Stack Startup         | Start backend + devdash     | Same                      |

### launch.json - 6 Debug Configurations

| Configuration                | Use Case                       | Key  |
| ---------------------------- | ------------------------------ | ---- |
| 🐍 Python: Current File      | Debug any Python file          | `F5` |
| 🚀 FastAPI: Backend Server   | Debug backend with breakpoints | `F5` |
| 📊 DevDash: Dashboard Server | Debug DevDash                  | `F5` |
| 🧪 Pytest: Current File      | Debug single test              | `F5` |
| 🧪 Pytest: All Tests         | Debug test suite               | `F5` |
| 🔧 Agent Repair Script       | Debug repair logic             | `F5` |

### extensions.json - 17 Recommended Extensions

#### Core (5)

- `ms-python.python` - Python language support
- `ms-python.vscode-pylance` - Fast IntelliSense
- `ms-toolsai.jupyter` - Notebook support
- `ms-vscode.powershell` - PowerShell integration
- `github.copilot` - AI pair programming

#### Productivity (6)

- `eamodio.gitlens` - Git supercharged
- `yzhang.markdown-all-in-one` - Markdown editing
- `gruntfuggly.todo-tree` - TODO tracking
- `donjayamanne.githistory` - Git history viewer
- `christian-kohler.path-intellisense` - Path autocomplete
- `ms-vscode-remote.remote-wsl` - WSL integration

#### Code Quality (6)

- `davidanson.vscode-markdownlint` - Markdown linting
- `esbenp.prettier-vscode` - Code formatting
- `foxundermoon.shell-format` - Shell script formatting
- `tamasfe.even-better-toml` - TOML support
- `redhat.vscode-yaml` - YAML support
- `visualstudioexptteam.vscodeintellicode` - AI IntelliSense

### settings.json - Key Settings

```json
{
  "terminal.integrated.defaultProfile.windows": "PowerShell",
  "python.defaultInterpreterPath": ".venv-wsl/bin/python",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": "explicit"
  },
  "files.trimTrailingWhitespace": true,
  "python.testing.pytestEnabled": true,
  "python.formatting.provider": "black"
}
```

---

## 🎮 Task Runners

### Running Tasks

**Method 1: Command Palette**

```
Ctrl+Shift+P → "Tasks: Run Task" → Select task
```

**Method 2: Task Menu**

```
Terminal → Run Task... → Select task
```

**Method 3: Keyboard Shortcut**

```
Ctrl+Shift+B (runs default build task)
```

### Common Task Workflows

#### 1. Start Development Session

```
Task: "🔄 Full Stack Startup"
Result: Backend + DevDash running
Access: http://127.0.0.1:3738 (backend)
        http://127.0.0.1:4545 (devdash)
```

#### 2. Agent Maintenance

```
Task: "🔧 Run Agent Repair (Dry Run)"
Review output
Task: "🔧 Run Agent Repair (Execute)"
Task: "✅ Validate Hardening"
```

#### 3. Testing Workflow

```
Task: "🧪 Test All Agents"        # Quick agent check
Task: "🧪 Run Pytest"              # Unit tests
Task: "🧪 Run Smoke Tests"         # Full beta validation
Task: "🔍 Validate All Systems"    # Comprehensive check
```

#### 4. Pre-Commit Checklist

```
Task: "🧪 Run Pytest"
Task: "🔍 Validate All Systems"
Task: "🧪 Test All Agents"
Commit changes
```

---

## 🐛 Debugging

### Starting Debugger

1. **Open file to debug**
2. **Set breakpoints** (`F9` on line number)
3. **Press `F5`** or click Debug icon
4. **Select configuration** from dropdown

### Debug Configurations Explained

#### Backend Debugging

```
Configuration: "🚀 FastAPI: Backend Server"
Usage: Debug API endpoints, agent logic
Breakpoints: api/main.py, simple_connector.py
Port: 3738
```

**Example Debug Session:**

1. Set breakpoint in `api/simple_connector.py` line 150 (agent chat)
2. Press `F5` → Select "FastAPI: Backend Server"
3. Send request: `curl http://127.0.0.1:3738/chat/CEO -X POST ...`
4. Debugger stops at breakpoint
5. Inspect variables, step through code

#### Test Debugging

```
Configuration: "🧪 Pytest: Current File"
Usage: Debug failing tests
Breakpoints: tests_flat/*.py
```

**Example:**

1. Open `tests_flat/test_simple_connector.py`
2. Set breakpoint in failing test
3. Press `F5` → Select "Pytest: Current File"
4. Step through test execution

### Debug Controls

| Key             | Action            |
| --------------- | ----------------- |
| `F5`            | Continue          |
| `F10`           | Step Over         |
| `F11`           | Step Into         |
| `Shift+F11`     | Step Out          |
| `Ctrl+Shift+F5` | Restart           |
| `Shift+F5`      | Stop              |
| `F9`            | Toggle Breakpoint |

---

## 🔌 Extensions

### Installing Extensions

**Method 1: Workspace Recommendations**

- VS Code prompts on workspace open
- Click "Install All"

**Method 2: Manual Install**

```
Ctrl+Shift+X → Search extension → Install
```

**Method 3: Command Line**

```powershell
code --install-extension ms-python.python
code --install-extension github.copilot
```

### Essential Extensions for VBoarder

#### Must-Have (Install First)

1. **Python** (`ms-python.python`)

   - Python language support
   - IntelliSense, linting, debugging

2. **Pylance** (`ms-python.vscode-pylance`)

   - Fast IntelliSense
   - Type checking

3. **GitLens** (`eamodio.gitlens`)

   - Git blame, history, compare
   - Essential for shift work

4. **Markdown All in One** (`yzhang.markdown-all-in-one`)
   - Preview shift reports
   - TOC generation

#### Highly Recommended

5. **GitHub Copilot** (`github.copilot`)

   - AI-assisted coding
   - Context-aware suggestions

6. **Todo Tree** (`gruntfuggly.todo-tree`)

   - Track TODO, FIXME, CRITICAL tags
   - Project-wide task view

7. **Remote - WSL** (`ms-vscode-remote.remote-wsl`)
   - Seamless WSL integration
   - Required for VBoarder

### Extension Configuration

#### Todo Tree Custom Tags

```json
"todo-tree.general.tags": [
  "TODO", "FIXME", "BUG", "HACK",
  "NOTE", "XXX", "CRITICAL", "BETA"
],
"todo-tree.highlights.customHighlight": {
  "CRITICAL": {
    "icon": "flame",
    "iconColour": "#ff0000"
  },
  "BETA": {
    "icon": "rocket",
    "iconColour": "#00aaff"
  }
}
```

#### GitLens Settings

```json
"gitlens.codeLens.enabled": true,
"gitlens.currentLine.enabled": true
```

---

## ⚙️ Settings

### Key Project Settings

#### Terminal Configuration

```json
"terminal.integrated.defaultProfile.windows": "PowerShell",
"terminal.integrated.defaultProfile.linux": "bash"
```

- Windows: PowerShell (native commands)
- WSL: bash (Linux environment)

#### Python Configuration

```json
"python.defaultInterpreterPath": ".venv-wsl/bin/python",
"python.terminal.activateEnvironment": true,
"python.testing.pytestEnabled": true,
"python.formatting.provider": "black"
```

- Uses WSL virtual environment
- Auto-activates on terminal open
- Pytest integration
- Black code formatting (88 char line length)

#### Editor Behavior

```json
"editor.formatOnSave": true,
"editor.codeActionsOnSave": {
  "source.organizeImports": "explicit"
},
"editor.rulers": [88, 120],
"editor.tabSize": 4
```

- Auto-format on save
- Auto-organize imports
- Visual guides at 88 (Python) and 120 (max)
- 4-space indentation (Python standard)

#### File Management

```json
"files.trimTrailingWhitespace": true,
"files.insertFinalNewline": true,
"files.exclude": {
  "**/__pycache__": true,
  "**/*.pyc": true,
  "**/.pytest_cache": true
}
```

- Auto-trim whitespace
- Ensure final newline
- Hide build artifacts

### Customizing Settings

**Workspace Settings (Project-Specific)**

- Stored in `.vscode/settings.json`
- Applies only to VBoarder
- Committed to git

**User Settings (Global)**

- `Ctrl+,` → Open Settings
- Applies to all VS Code workspaces
- Not committed

---

## 🔄 Workflows

### Daily Development Workflow

#### 1. Morning Startup

```
1. Open VS Code: code d:\ai\projects\vboarder
2. Check shift reports: docs/CTO/SHIFT_REPORTS/
3. Review TODO tree: Ctrl+Shift+P → "Todo Tree: Focus"
4. Start backend: Ctrl+Shift+P → Run Task → "Full Stack Startup"
5. Verify health: http://127.0.0.1:3738/health
```

#### 2. Feature Development

```
1. Create feature branch: git checkout -b feature/my-feature
2. Set up debugging: F5 → "FastAPI: Backend Server"
3. Make changes with live reload (--reload flag)
4. Test changes: Ctrl+Shift+P → Run Task → "Test All Agents"
5. Run unit tests: Ctrl+Shift+P → Run Task → "Run Pytest"
```

#### 3. Pre-Commit Validation

```
1. Run smoke tests: Ctrl+Shift+P → Run Task → "Run Smoke Tests"
2. Validate all systems: Ctrl+Shift+P → Run Task → "Validate All Systems"
3. Check test coverage: pytest --cov
4. Format code: Black runs on save
5. Commit: git commit -m "feat: description"
```

#### 4. Shift Handoff

```
1. Generate dashboard: Ctrl+Shift+P → Run Task → "Generate Shift Dashboard"
2. Review shift report template: docs/CTO/SHIFT_REPORTS/
3. Update CTO_SHIFT_HANDOFF.md
4. Tag if needed: git tag -a v0.9.0-beta.X
5. Push changes: git push origin main --tags
```

### Agent Maintenance Workflow

```
1. Check agent status: Ctrl+Shift+P → Run Task → "Test All Agents"
2. If failures detected:
   a. Preview repair: Ctrl+Shift+P → Run Task → "Run Agent Repair (Dry Run)"
   b. Review output in terminal
   c. Execute repair: Ctrl+Shift+P → Run Task → "Run Agent Repair (Execute)"
   d. Validate: Ctrl+Shift+P → Run Task → "Validate Hardening"
3. Verify registry: cat agent_registry.json | jq '. | length'
4. Test all agents again: Ctrl+Shift+P → Run Task → "Test All Agents"
```

### Debugging Workflow

```
1. Identify issue (test failure, bug report)
2. Set breakpoints in suspected code
3. Launch debugger: F5 → Select appropriate config
4. Reproduce issue
5. Step through code (F10, F11)
6. Inspect variables (hover, debug console)
7. Fix issue
8. Re-run test to verify
```

---

## 🔍 Troubleshooting

### Common Issues

#### Issue: Tasks Not Running in WSL

**Symptom:** Tasks fail with "wsl: command not found"

**Solution:**

```powershell
# Verify WSL installed
wsl --version

# If not installed, install WSL2
wsl --install

# Restart VS Code
Ctrl+Shift+P → "Reload Window"
```

#### Issue: Python Interpreter Not Found

**Symptom:** "Python interpreter not found" error

**Solution:**

```
1. Press Ctrl+Shift+P
2. Type: "Python: Select Interpreter"
3. Choose: .venv-wsl/bin/python
4. If not listed, create venv:
   wsl bash -c "cd /mnt/d/ai/projects/vboarder && python3 -m venv .venv-wsl"
```

#### Issue: Extensions Not Installing

**Symptom:** Extensions fail to install from recommendations

**Solution:**

```
1. Check internet connection
2. Reload VS Code: Ctrl+Shift+P → "Reload Window"
3. Clear extension cache:
   - Close VS Code
   - Delete: %USERPROFILE%\.vscode\extensions\
   - Restart VS Code
4. Manual install:
   Ctrl+Shift+X → Search extension → Install
```

#### Issue: Tasks Show No Output

**Symptom:** Tasks run but show no output in terminal

**Solution:**

```json
// Update task in .vscode/tasks.json
"presentation": {
  "echo": true,
  "reveal": "always",  // Was "never"
  "focus": true,
  "panel": "shared"
}
```

#### Issue: Debugger Not Stopping at Breakpoints

**Symptom:** Breakpoints are grayed out, debugger doesn't stop

**Solution:**

```
1. Verify breakpoint is in executed code path
2. Check "justMyCode" setting:
   // In launch.json
   "justMyCode": false  // Allows debugging into libraries
3. Restart debugger: Ctrl+Shift+F5
4. Verify Python interpreter matches debug config
```

#### Issue: Format on Save Not Working

**Symptom:** Code not formatting when saving files

**Solution:**

```
1. Verify formatter installed:
   pip install black
2. Check settings:
   "editor.formatOnSave": true
   "python.formatting.provider": "black"
3. Manual format: Shift+Alt+F
4. Reload window: Ctrl+Shift+P → "Reload Window"
```

### Getting Help

1. **Check logs:**

   ```
   Ctrl+Shift+P → "Developer: Toggle Developer Tools"
   Console tab shows errors
   ```

2. **Check extension logs:**

   ```
   Output panel → Select extension from dropdown
   ```

3. **Reload VS Code:**

   ```
   Ctrl+Shift+P → "Reload Window"
   ```

4. **Reset to defaults:**
   ```
   1. Backup .vscode/ folder
   2. Delete .vscode/settings.json
   3. Reload VS Code
   4. Reinstall extensions
   ```

---

## 📚 Additional Resources

### Documentation

- [VS Code Tasks](https://code.visualstudio.com/docs/editor/tasks)
- [VS Code Debugging](https://code.visualstudio.com/docs/editor/debugging)
- [Python in VS Code](https://code.visualstudio.com/docs/python/python-tutorial)
- [WSL Integration](https://code.visualstudio.com/docs/remote/wsl)

### VBoarder-Specific Docs

- [START_HERE.md](../START_HERE.md) - Quick start guide
- [CTO_SHIFT_HANDOFF.md](../CTO_SHIFT_HANDOFF.md) - Shift procedures
- [AGENT_REPAIR_HARDENING.md](AGENT_REPAIR_HARDENING.md) - Repair system v1.1
- [BETA_TEST_PLAYBOOK.md](BETA_TEST_PLAYBOOK.md) - Testing procedures

### Quick Reference

- **Tasks:** `Ctrl+Shift+P` → "Tasks: Run Task"
- **Debug:** `F5`
- **Extensions:** `Ctrl+Shift+X`
- **Settings:** `Ctrl+,`
- **Terminal:** `Ctrl+J`
- **Markdown Preview:** `Ctrl+Shift+V`

---

## 🏷️ Version Info

- **Guide Version:** 1.0
- **VBoarder Version:** v0.9.0-beta.1
- **Last Updated:** October 14, 2025
- **Maintained By:** VBoarder CTO Team

---

**Next Steps:**

1. Install recommended extensions
2. Select Python interpreter
3. Run "Full Stack Startup" task
4. Start developing! 🚀

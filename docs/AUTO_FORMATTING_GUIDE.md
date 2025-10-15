# 🎨 VBoarder Auto-Formatting Setup Guide

**Last Updated:** October 14, 2025

---

## ✅ What's Configured

Your VBoarder project now has **fully automated code formatting and linting** with Ruff!

### 🚀 Features Enabled

- ✅ **Format on Save**: Code auto-formats when you save (Ctrl+S)
- ✅ **Auto-Fix on Save**: Automatically fixes common issues
- ✅ **Import Organization**: Automatically sorts and organizes imports
- ✅ **120-character line limit**: Increased from 88 for better readability
- ✅ **Comprehensive linting**: Catches errors, style issues, and code smells
- ✅ **Unsafe fixes enabled**: More aggressive auto-fixing

---

## 📋 Configuration Files

### 1. `.vscode/settings.json` ✅

**What it does:**
- Enables format on save
- Configures Ruff as Python formatter
- Enables auto-fix and import organization
- Sets up code actions on save

**Key settings:**
```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": "explicit",
    "source.organizeImports": "explicit"
  },
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "ruff.enable": true,
  "ruff.fixAll": true
}
```

### 2. `pyproject.toml` ✅

**What it does:**
- Configures Ruff behavior
- Sets line length to 120 characters
- Enables comprehensive linting rules
- Allows unsafe fixes for auto-correction

**Key settings:**
```toml
[tool.ruff]
line-length = 120
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM"]
ignore = ["E501"]  # Line length handled by formatter
unsafe-fixes = true
```

---

## 🧪 Testing the Setup

### 1. Manual Test

Create a test file with intentionally messy code:

```python
# test_formatting.py
import os
import sys
from typing import Dict,List
import json

def badly_formatted_function(x,y,z):
    result=x+y+z
    return result

class MyClass:
  def __init__(self):
      pass
```

**Save the file (Ctrl+S)** and watch it auto-format to:

```python
# test_formatting.py
import json
import os
import sys
from typing import Dict, List


def badly_formatted_function(x, y, z):
    result = x + y + z
    return result


class MyClass:
    def __init__(self):
        pass
```

### 2. Verify Ruff is Active

Open VS Code terminal and run:

```bash
# Check Ruff version
ruff --version

# Run Ruff check on a file
ruff check api/main.py

# Auto-fix issues
ruff check --fix api/main.py
```

---

## 🛠️ Required VS Code Extensions

Install these extensions for full functionality:

### Essential

1. **Ruff** (charliermarsh.ruff)
   - Primary formatter and linter
   - Install: `code --install-extension charliermarsh.ruff`

2. **Python** (ms-python.python)
   - Core Python support
   - Install: `code --install-extension ms-python.python`

### Recommended

3. **Prettier** (esbenp.prettier-vscode)
   - For JSON, YAML, Markdown
   - Install: `code --install-extension esbenp.prettier-vscode`

4. **GitLens** (eamodio.gitlens)
   - Git integration
   - Install: `code --install-extension eamodio.gitlens`

5. **Error Lens** (usernamehw.errorlens)
   - Inline error highlighting
   - Install: `code --install-extension usernamehw.errorlens`

---

## 🎯 What Gets Auto-Fixed

### On Save (Automatically)

✅ **Code Formatting**
- Indentation normalization
- Spacing around operators
- Line length wrapping (120 chars)
- Quote style normalization

✅ **Import Organization**
- Sorts imports alphabetically
- Groups: stdlib → third-party → local
- Removes unused imports
- Fixes import order

✅ **Common Fixes**
- `bare except` → `except Exception`
- Unnecessary f-strings
- Redundant parentheses
- Simplified comprehensions
- Unused variables (prefixed with `_`)

### On Manual Run

Run these commands for deeper fixes:

```bash
# Fix all Python files
ruff check --fix .

# Format all Python files
ruff format .

# Check only (no auto-fix)
ruff check .
```

---

## 🧠 AI Co-Pilot Integration

### GitHub Copilot Commands

If you have GitHub Copilot installed:

1. **Inline Quick Fixes**
   - Hover over error → Click "Quick Fix" → Select Copilot suggestion

2. **Chat Commands**
   - `/fix` - Fix issues in selected code
   - `/explain` - Explain what the linter is complaining about
   - `/refactor` - Suggest improvements

### Example Workflow

```python
# Before (flagged by Ruff)
try:
    data = load_data()
except:  # E722: bare except
    pass

# Select code → Right-click → "Copilot: Fix this"
# After
try:
    data = load_data()
except Exception as e:
    logger.error(f"Failed to load data: {e}")
```

---

## 🔧 Customization Options

### Adjust Line Length

Edit `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100  # Change from 120
```

### Disable Specific Rules

```toml
[tool.ruff.lint]
ignore = [
    "E501",   # Line too long
    "N802",   # Function name should be lowercase
    "SIM108", # Use ternary operator
]
```

### Per-File Ignores

```toml
[tool.ruff.lint.per-file-ignores]
"tests/*" = ["D"]           # No docstring checks in tests
"scripts/*" = ["E501", "D"] # Allow long lines in scripts
"__init__.py" = ["F401"]    # Allow unused imports
```

---

## 📊 Linting Rules Reference

### Currently Enabled

| Code | Category | Description |
|------|----------|-------------|
| **E** | pycodestyle errors | PEP 8 errors (indentation, whitespace, etc.) |
| **F** | pyflakes | Logical errors (unused vars, imports, etc.) |
| **W** | pycodestyle warnings | PEP 8 warnings |
| **I** | isort | Import sorting and organization |
| **N** | pep8-naming | Naming conventions (PEP 8) |
| **UP** | pyupgrade | Upgrade syntax for newer Python versions |
| **B** | flake8-bugbear | Common bug patterns |
| **C4** | flake8-comprehensions | List/dict comprehension improvements |
| **SIM** | flake8-simplify | Code simplification suggestions |

### Common Warnings You'll See

| Code | Message | Auto-Fix |
|------|---------|----------|
| E501 | Line too long | ✅ Yes (formatter wraps) |
| E722 | Bare except | ✅ Yes → `except Exception` |
| F401 | Unused import | ✅ Yes (removes) |
| F841 | Unused variable | ✅ Yes (prefixes with `_`) |
| I001 | Import order wrong | ✅ Yes (reorders) |
| UP032 | Use f-string | ⚠️ Manual (suggested) |
| B008 | Function call in arg | ⚠️ Manual |

---

## 🎓 Quick Tips

### 1. Format Entire Project

```bash
# From project root
ruff format .
```

### 2. Check Before Commit

```bash
# Dry run (see what would be fixed)
ruff check --diff .

# Actually fix
ruff check --fix .
```

### 3. Ignore Line-Specific Issues

```python
# Disable for one line
x = really_long_variable_name_that_exceeds_limit  # noqa: E501

# Disable multiple rules
import unused_module  # noqa: F401, I001
```

### 4. Disable Formatting for Block

```python
# fmt: off
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
]
# fmt: on
```

---

## 🐛 Troubleshooting

### Issue: Formatter not running on save

**Fix:**
1. Open Command Palette (`Ctrl+Shift+P`)
2. Type: `Developer: Reload Window`
3. Check Output panel: `View → Output → Ruff`

### Issue: Import sorting conflicts

**Fix:**
```toml
# In pyproject.toml
[tool.ruff.lint.isort]
force-single-line = false
combine-as-imports = true
```

### Issue: Too aggressive fixes

**Fix:**
```toml
# In pyproject.toml
[tool.ruff.lint]
unsafe-fixes = false  # Change to false
```

---

## 📚 Additional Resources

- **Ruff Documentation**: https://docs.astral.sh/ruff/
- **Rule Reference**: https://docs.astral.sh/ruff/rules/
- **VS Code Ruff Extension**: https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff
- **Python Style Guide (PEP 8)**: https://pep8.org/

---

## ✅ Checklist

After setup, verify:

- [ ] `.vscode/settings.json` updated
- [ ] `pyproject.toml` configured
- [ ] Ruff extension installed
- [ ] Format on save works (test with messy code)
- [ ] Import organization works (save file with unordered imports)
- [ ] No errors in Output panel (View → Output → Ruff)
- [ ] Line length set to 120 characters
- [ ] Auto-fix on save enabled

---

## 🎉 You're All Set!

Your VBoarder project now has:
- ✅ Auto-formatting on every save
- ✅ Auto-fixing common issues
- ✅ Import organization
- ✅ 120-character line limit
- ✅ Comprehensive linting

**Just save your files and let Ruff do the work!** 🚀

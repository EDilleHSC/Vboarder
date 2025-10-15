# ⚙️ VS Code Auto-Save & Code Actions Configuration

## Current Setup Summary

Your VS Code is now configured for **smart, non-disruptive development flow**:

```json
{
  "files.autoSave": "afterDelay",
  "files.autoSaveDelay": 1000,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll": "explicit",
    "source.organizeImports": "explicit"
  }
}
```

---

## 🔍 What Each Setting Does

| Setting | Value | Behavior |
|---------|-------|----------|
| `files.autoSave` | `"afterDelay"` | **Auto-saves after 1 second of inactivity** |
| `files.autoSaveDelay` | `1000` | Wait 1000ms (1 second) before auto-saving |
| `editor.formatOnSave` | `true` | **Always formats code on save** |
| `source.fixAll` | `"explicit"` | **Only runs on manual Ctrl+S** (not autosave) |
| `source.organizeImports` | `"explicit"` | **Only runs on manual Ctrl+S** (not autosave) |

---

## 🎯 Behavior Summary

### Autosave (after 1 second of inactivity)

✅ **Saves your file**
✅ **Formats code** (Ruff formatting)
❌ **Does NOT organize imports**
❌ **Does NOT run fixAll** (lint auto-fixes)

### Manual Save (Ctrl+S)

✅ **Saves your file**
✅ **Formats code** (Ruff formatting)
✅ **Organizes imports** (removes unused, sorts)
✅ **Runs fixAll** (applies all Ruff auto-fixes)

---

## 💡 Why This Setup?

### Problem with Always-On Code Actions

```python
# You type:
import os
import sys
from pathlib import Path
# ...keep typing...

# Autosave triggers → Ruff removes "unused" imports
# But you were about to use them! 😡
```

### Solution: Explicit Code Actions

- **Autosave** = Fast, non-disruptive background saves
- **Manual save** (Ctrl+S) = "I'm done, clean this up"

---

## 🧪 Test the Behavior

### Test 1: Autosave

1. Open a Python file
2. Add an unused import:

   ```python
   import sys  # Not used anywhere
   ```

3. Wait 1 second (autosave triggers)
4. **Expected:** Import stays (not removed)

### Test 2: Manual Save

1. With the unused import still there
2. Press **Ctrl+S**
3. **Expected:** Import is removed immediately

### Test 3: Import Sorting

1. Add imports in wrong order:

   ```python
   from pathlib import Path
   import sys
   import os
   ```

2. Press **Ctrl+S**
3. **Expected:** Imports are sorted:

   ```python
   import os
   import sys
   from pathlib import Path
   ```

---

## 🎨 Customization Options

### Want faster autosave?

```json
{
  "files.autoSaveDelay": 500  // 0.5 seconds
}
```

### Want slower autosave?

```json
{
  "files.autoSaveDelay": 3000  // 3 seconds
}
```

### Disable autosave completely?

```json
{
  "files.autoSave": "off"
}
```

### Want code actions on autosave too?

```json
{
  "editor.codeActionsOnSave": {
    "source.fixAll": "always",  // Changed from "explicit"
    "source.organizeImports": "always"
  }
}
```

---

## 🐍 Python-Specific Settings

Your current Python configuration:

```json
{
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "ruff.enable": true,
  "ruff.lint.enable": true,
  "ruff.organizeImports": true,
  "ruff.fixAll": true
}
```

**What this means:**

- ✅ Ruff is your formatter (fast, modern)
- ✅ Ruff handles linting
- ✅ Ruff organizes imports
- ✅ All Ruff actions only run on manual save

---

## 🔧 Troubleshooting

### "Imports aren't getting organized"

**Check:**

1. Ruff extension installed? (`charliermarsh.ruff`)
2. Manual save (Ctrl+S), not autosave?
3. Check Output panel → Ruff for errors

### "Code isn't formatting at all"

**Check:**

1. Ruff extension enabled?
2. File is `.py` (Python)?
3. Check status bar (bottom right) for formatter

### "Autosave is too aggressive"

**Fix:**

```json
{
  "files.autoSaveDelay": 2000  // Increase to 2 seconds
}
```

### "I want autosave to trigger code actions"

**Change to:**

```json
{
  "editor.codeActionsOnSave": {
    "source.fixAll": "always",
    "source.organizeImports": "always"
  }
}
```

---

## 📊 Comparison Table

| Feature | Autosave | Manual Save (Ctrl+S) |
|---------|----------|---------------------|
| **Triggers** | After 1s inactivity | When you press Ctrl+S |
| **Saves file** | ✅ Yes | ✅ Yes |
| **Formats code** | ✅ Yes (Ruff) | ✅ Yes (Ruff) |
| **Organizes imports** | ❌ No | ✅ Yes |
| **Fixes lint errors** | ❌ No | ✅ Yes |
| **Removes unused imports** | ❌ No | ✅ Yes |
| **Sorts imports** | ❌ No | ✅ Yes |

---

## 🚀 Workflow Examples

### Example 1: Writing New Code

```python
# You start typing
import os
import sys
from pathlib import Path

def process_files():
    # Still typing...
    # Autosave fires after 1s
    # Imports stay (you might use them)

    for file in Path(".").glob("*.py"):
        print(file)

    # You realize you don't need os/sys
    # Press Ctrl+S
    # → Unused imports removed automatically
```

**Result:** No interruptions while coding, cleanup happens when ready.

### Example 2: Refactoring

```python
# Before refactor
import json
import os
import sys
from typing import Dict, List, Optional

# After refactor (removed code that used sys)
# Press Ctrl+S
# → sys import removed
# → Other imports sorted
# → Code formatted
```

**Result:** One keystroke cleans everything.

### Example 3: Code Review Prep

```python
# Messy code with wrong formatting
def my_func(x,y,z):
  result=x+y
  return result

# Press Ctrl+S
# → Formatted properly
# → Imports organized
# → Linting errors fixed
```

**Result:** Code is review-ready instantly.

---

## 🎓 Pro Tips

### Tip 1: Use Ctrl+S Frequently

Even with autosave, press Ctrl+S when you finish a logical block:

- After writing a function
- After fixing a bug
- Before committing

This ensures imports and linting are cleaned up.

### Tip 2: Check the Status Bar

Bottom right shows:

- Current formatter (should say "Ruff")
- Line/column numbers
- Errors/warnings count

### Tip 3: Use Command Palette

Press `Ctrl+Shift+P` then:

- "Format Document" - Force format
- "Organize Imports" - Force organize
- "Fix All" - Run all fixable lint rules

### Tip 4: Disable for Specific Files

Add to file comments:

```python
# fmt: off  (for entire file)

# fmt: off
messy_code_here()
# fmt: on
```

---

## 📝 Summary

**Your new workflow:**

1. **Type code** → Autosave handles background saves
2. **Finish section** → Press Ctrl+S for cleanup
3. **Keep coding** → No interruptions
4. **Ready to commit** → Everything is already clean

**Benefits:**

- ✅ No lost work (autosave)
- ✅ No surprise import removals
- ✅ Clean code when ready
- ✅ Fast development flow

---

**Settings file:** `.vscode/settings.json`
**Last updated:** October 14, 2025

# ⚡ VBoarder Auto-Formatting Quick Reference

## 🎯 Quick Start

1. **Install Ruff Extension**
   ```bash
   code --install-extension charliermarsh.ruff
   ```

2. **Reload VS Code**
   - Press `Ctrl+Shift+P` → `Developer: Reload Window`

3. **Test It**
   - Edit any `.py` file
   - Press `Ctrl+S` (Save)
   - Watch it auto-format! ✨

---

## 🔥 What Happens on Save

| Action          | Before            | After                 |
| --------------- | ----------------- | --------------------- |
| **Format**      | `x=1+2`           | `x = 1 + 2`           |
| **Imports**     | Unordered imports | Sorted alphabetically |
| **Line length** | 150 char line     | Wrapped at 120 chars  |
| **Bare except** | `except:`         | `except Exception:`   |
| **Spacing**     | `def foo(x,y):`   | `def foo(x, y):`      |

---

## 🛠️ Manual Commands

```bash
# Format entire project
ruff format .

# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Show what would be fixed
ruff check --diff .
```

---

## 🎨 Keyboard Shortcuts

| Action           | Shortcut       |
| ---------------- | -------------- |
| Format document  | `Shift+Alt+F`  |
| Save + format    | `Ctrl+S`       |
| Organize imports | `Shift+Alt+O`  |
| Quick fix        | `Ctrl+.`       |
| Command palette  | `Ctrl+Shift+P` |

---

## 🚫 Ignore Specific Lines

```python
# Ignore line too long
x = really_long_variable_name  # noqa: E501

# Ignore unused import
import debugging_tool  # noqa: F401

# Ignore entire file (top of file)
# ruff: noqa
```

---

## 🐛 Troubleshooting

| Problem         | Solution                                        |
| --------------- | ----------------------------------------------- |
| Not formatting  | Reload window: `Ctrl+Shift+P` → `Reload Window` |
| Wrong formatter | Check Output: `View → Output → Ruff`            |
| Conflicts       | Disable flake8/black in settings                |

---

## 📊 Current Configuration

```toml
Line length: 120 characters
Target Python: 3.11
Formatter: Ruff (charliermarsh.ruff)
Format on save: ✅ Enabled
Auto-fix on save: ✅ Enabled
Import organization: ✅ Enabled
Unsafe fixes: ✅ Enabled
```

---

## 🎓 Pro Tips

1. **Format before commit**: `ruff format . && ruff check --fix .`
2. **Check in CI/CD**: Add `ruff check .` to pre-commit hooks
3. **Disable for code block**:
   ```python
   # fmt: off
   matrix = [[1, 2], [3, 4]]
   # fmt: on
   ```

---

## 📚 Full Guide

See `docs/AUTO_FORMATTING_GUIDE.md` for complete documentation.

---

**Questions?** Check the Ruff docs: <https://docs.astral.sh/ruff/>

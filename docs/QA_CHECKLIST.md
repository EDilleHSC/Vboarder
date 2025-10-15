# 🎯 VBoarder V2 Full Stack QA Checklist

**Date:** October 13, 2025
**Version:** v1.0.0
**Status:** Ready for Testing

---

## 🚀 Quick Start (WSL)

```bash
cd /mnt/d/ai/projects/vboarder
chmod +x start_full_stack.sh
./start_full_stack.sh
```

This will:

1. ✅ Check prerequisites (Python, Node, npm)
2. ✅ Verify virtual environment
3. ✅ Install dependencies
4. ✅ Test agent imports
5. ✅ Clear caches
6. ✅ Build frontend
7. ✅ Start backend (port 3738)
8. ✅ Start frontend (port 3000)

---

## ✅ QA Checklist - Pass/Fail

### 🔧 Infrastructure

| Test                      | Expected           | Status | Notes                   |
| ------------------------- | ------------------ | ------ | ----------------------- |
| Python 3.11+ installed    | ✅ Available       | ⬜     | Run: `python --version` |
| Node.js 18+ installed     | ✅ Available       | ⬜     | Run: `node --version`   |
| Virtual env exists        | ✅ `.venv-wsl/`    | ⬜     | Check directory         |
| All Python deps installed | ✅ No errors       | ⬜     | Run: `pip list`         |
| All npm deps installed    | ✅ `node_modules/` | ⬜     | Check directory         |

### 🤖 Backend (Port 3738)

| Test                | Expected                  | Status | Command/Notes                                                         |
| ------------------- | ------------------------- | ------ | --------------------------------------------------------------------- |
| Backend starts      | ✅ No errors              | ⬜     | `uvicorn api.main:app --port 3738 --reload`                           |
| Health endpoint     | `{"status":"ok"}`         | ⬜     | `curl http://127.0.0.1:3738/health`                                   |
| API docs load       | ✅ Swagger UI             | ⬜     | Visit: http://127.0.0.1:3738/docs                                     |
| All 9 agents import | ✅ No ModuleNotFoundError | ⬜     | `python tests_flat/test_agent_imports.py`                             |
| CEO endpoint        | ✅ Streaming response     | ⬜     | `curl -X POST http://127.0.0.1:3738/chat/CEO -d '{"message":"test"}'` |
| Memory endpoint     | ✅ Returns JSON           | ⬜     | `curl http://127.0.0.1:3738/api/memory?agent=CEO`                     |
| Context endpoint    | ✅ Returns JSON           | ⬜     | `curl http://127.0.0.1:3738/api/context?agent=CEO`                    |

### 💻 Frontend (Port 3000)

| Test                 | Expected         | Status | Command/Notes                   |
| -------------------- | ---------------- | ------ | ------------------------------- |
| Frontend starts      | ✅ No errors     | ⬜     | `npm run dev`                   |
| Build succeeds       | ✅ No errors     | ⬜     | `npm run build`                 |
| Home page loads      | ✅ Displays      | ⬜     | Visit: http://localhost:3000    |
| V2 page loads        | ✅ Displays      | ⬜     | Visit: http://localhost:3000/v2 |
| No hydration errors  | ✅ Clean console | ⬜     | Check browser console           |
| No TypeScript errors | ✅ Build passes  | ⬜     | Run: `npm run build`            |

### 🎨 UI Components (V2 Interface)

| Component               | Expected Behavior                              | Status | Notes                   |
| ----------------------- | ---------------------------------------------- | ------ | ----------------------- |
| **Agent Selector**      |                                                |        |                         |
| - All 9 agents visible  | ✅ CEO, CTO, CFO, COO, CMO, CLO, COS, SEC, AIR | ⬜     | Check sidebar           |
| - Agent cards clickable | ✅ Selects agent                               | ⬜     | Click any agent         |
| - Active state shows    | ✅ Highlighted                                 | ⬜     | Visual feedback         |
| **Chat Interface**      |                                                |        |                         |
| - Message input works   | ✅ Text entry                                  | ⬜     | Type in input           |
| - Send button enabled   | ✅ Clickable                                   | ⬜     | Button state            |
| - Messages display      | ✅ User + Agent messages                       | ⬜     | Send test message       |
| - Streaming works       | ✅ Tokens appear live                          | ⬜     | Watch response          |
| - Markdown renders      | ✅ Formatted text                              | ⬜     | Code blocks, lists work |
| **Sidebar Tabs**        |                                                |        |                         |
| - Files tab loads       | ✅ File list visible                           | ⬜     | Click Files tab         |
| - Tools tab loads       | ✅ Tools list visible                          | ⬜     | Click Tools tab         |
| - Memory tab loads      | ✅ Memory panel visible                        | ⬜     | Click Memory tab        |
| - Agents tab loads      | ✅ Agent list visible                          | ⬜     | Click Agents tab        |
| **Metrics Bar**         |                                                |        |                         |
| - Status badge shows    | ✅ "OPERATIONAL"                               | ⬜     | Top bar                 |
| - Message count         | ✅ Number > 0                                  | ⬜     | Updates on chat         |
| - Response time         | ✅ Latency in ms                               | ⬜     | Shows after message     |
| - Active sessions       | ✅ Count visible                               | ⬜     | Shows current sessions  |

### 🔧 Files Tab

| Feature               | Expected                | Status | Notes             |
| --------------------- | ----------------------- | ------ | ----------------- |
| Search works          | ✅ Filters files        | ⬜     | Type in search    |
| Upload button visible | ✅ Shows                | ⬜     | Click to trigger  |
| File list displays    | ✅ Mock files show      | ⬜     | See default files |
| File icons correct    | ✅ PDF, CSV, etc.       | ⬜     | Visual check      |
| Hover actions appear  | ✅ View/Download/Delete | ⬜     | Hover over file   |
| Storage indicator     | ✅ Progress bar         | ⬜     | Bottom of tab     |

### 🛠️ Tools Tab

| Feature                | Expected                      | Status | Notes                         |
| ---------------------- | ----------------------------- | ------ | ----------------------------- |
| Tool list displays     | ✅ 5+ tools                   | ⬜     | Web Search, Code Runner, etc. |
| Tool status badges     | ✅ Available/Running/Disabled | ⬜     | Color-coded                   |
| Execution count        | ✅ Numbers visible            | ⬜     | Shows usage                   |
| Recent executions      | ✅ History list               | ⬜     | Shows past runs               |
| Execution status icons | ✅ Success/Running/Failed     | ⬜     | Visual indicators             |

### 💾 Memory Panel

| Feature              | Expected               | Status | Notes                  |
| -------------------- | ---------------------- | ------ | ---------------------- |
| Persona displays     | ✅ Agent description   | ⬜     | Shows role/description |
| Facts list visible   | ✅ Multiple facts      | ⬜     | Bullet list            |
| Add fact works       | ✅ Input + button      | ⬜     | Type and add           |
| Delete fact works    | ✅ Trash icon          | ⬜     | Click to remove        |
| Conversation history | ✅ Shows past messages | ⬜     | User + Agent messages  |
| Refresh button       | ✅ Reloads data        | ⬜     | Click refresh icon     |

### 📤 File Upload Component

| Feature            | Expected              | Status | Notes                  |
| ------------------ | --------------------- | ------ | ---------------------- |
| Component renders  | ✅ Visible            | ⬜     | Shows upload area      |
| Drag & drop zone   | ✅ Accepts files      | ⬜     | Drag file over         |
| File select button | ✅ Opens file picker  | ⬜     | Click to browse        |
| File info displays | ✅ Name, size shown   | ⬜     | After selection        |
| Progress bar       | ✅ Animates on upload | ⬜     | During upload          |
| Success state      | ✅ Checkmark shown    | ⬜     | After completion       |
| Error handling     | ✅ Error message      | ⬜     | Test with backend down |

### 🎭 Conference Mode

| Feature             | Expected               | Status | Notes                    |
| ------------------- | ---------------------- | ------ | ------------------------ |
| Multi-select agents | ✅ Select 2+ agents    | ⬜     | Checkbox or multi-select |
| Conference button   | ✅ Enabled with 2+     | ⬜     | Button state             |
| Parallel requests   | ✅ All agents respond  | ⬜     | Check network tab        |
| Response display    | ✅ All shown clearly   | ⬜     | Split view or tabs       |
| Agent attribution   | ✅ Clear who said what | ⬜     | Labels/badges            |

### 🔔 Toast Notifications

| Test            | Expected               | Status | Notes                |
| --------------- | ---------------------- | ------ | -------------------- |
| Success toast   | ✅ Green notification  | ⬜     | Add fact success     |
| Error toast     | ✅ Red notification    | ⬜     | Network error        |
| Info toast      | ✅ Blue notification   | ⬜     | General info         |
| Auto-dismiss    | ✅ Disappears after 5s | ⬜     | Wait and watch       |
| Multiple toasts | ✅ Max 3 shown         | ⬜     | Trigger many quickly |

### 🌐 API Integration

| Endpoint            | Method | Expected Response    | Status | Test Command                                            |
| ------------------- | ------ | -------------------- | ------ | ------------------------------------------------------- |
| `/health`           | GET    | `{"status":"ok"}`    | ⬜     | `curl http://127.0.0.1:3738/health`                     |
| `/chat/CEO`         | POST   | Streaming text       | ⬜     | Use Postman or frontend                                 |
| `/api/memory`       | GET    | Agent memory JSON    | ⬜     | `curl http://127.0.0.1:3738/api/memory?agent=CEO`       |
| `/api/memory`       | POST   | Success message      | ⬜     | Add fact via frontend                                   |
| `/api/memory`       | DELETE | Success message      | ⬜     | Delete fact via frontend                                |
| `/api/conversation` | GET    | Conversation history | ⬜     | `curl http://127.0.0.1:3738/api/conversation?agent=CEO` |
| `/api/context`      | GET    | Full context         | ⬜     | `curl http://127.0.0.1:3738/api/context?agent=CEO`      |

### 🔐 Error Handling

| Scenario          | Expected Behavior    | Status | Test                    |
| ----------------- | -------------------- | ------ | ----------------------- |
| Backend down      | Error toast shown    | ⬜     | Stop backend, try chat  |
| Invalid agent     | 404 error            | ⬜     | Request `/chat/INVALID` |
| Network timeout   | Timeout error toast  | ⬜     | Simulate slow network   |
| Malformed request | 400 error            | ⬜     | Send invalid JSON       |
| Memory fetch fail | Graceful degradation | ⬜     | Break memory endpoint   |

### 📱 Responsiveness

| Breakpoint       | Expected               | Status | Notes            |
| ---------------- | ---------------------- | ------ | ---------------- |
| Desktop (1920px) | ✅ Full layout         | ⬜     | Sidebar + chat   |
| Laptop (1366px)  | ✅ Adjusted layout     | ⬜     | Comfortable view |
| Tablet (768px)   | ✅ Collapsible sidebar | ⬜     | Mobile-friendly  |
| Mobile (375px)   | ✅ Stacked layout      | ⬜     | Test on phone    |

### ⚡ Performance

| Metric                 | Target  | Actual    | Status |
| ---------------------- | ------- | --------- | ------ |
| Initial page load      | < 3s    | \_\_\_ s  | ⬜     |
| Time to interactive    | < 5s    | \_\_\_ s  | ⬜     |
| First message response | < 2s    | \_\_\_ s  | ⬜     |
| Streaming latency      | < 100ms | \_\_\_ ms | ⬜     |
| Build time             | < 60s   | \_\_\_ s  | ⬜     |

---

## 🧪 Manual Test Scenarios

### Scenario 1: First-Time User

1. Navigate to http://localhost:3000/v2
2. Click on CEO agent
3. Type: "Hello, what can you help me with?"
4. Press Enter or click Send
5. **Expected:** Streaming response appears, message added to history

### Scenario 2: Memory Management

1. Select any agent (e.g., CTO)
2. Click Memory tab in sidebar
3. View existing facts
4. Click "Add Fact" input
5. Type: "VBoarder V2 launched October 2025"
6. Press Enter
7. **Expected:** Fact added to list, success toast shown

### Scenario 3: File Upload

1. Scroll to file upload component
2. Drag a .txt file onto the drop zone
3. **Expected:** File info appears, progress bar animates
4. Click "Upload to {AGENT}"
5. **Expected:** Success message, file uploaded

### Scenario 4: Conference Mode

1. Select 3 agents (CEO, CTO, CFO)
2. Enable conference mode
3. Send message: "What are our top priorities?"
4. **Expected:** All 3 agents respond, clearly attributed

### Scenario 5: Error Recovery

1. Stop backend server
2. Try sending a message
3. **Expected:** Error toast appears with clear message
4. Restart backend
5. Try sending again
6. **Expected:** Works normally, no residual errors

---

## 🐛 Known Issues

| Issue      | Severity | Status | Workaround |
| ---------- | -------- | ------ | ---------- |
| _None yet_ | -        | -      | -          |

---

## 📊 Test Results Summary

**Date Tested:** **\*\***\_\_\_**\*\***
**Tester:** **\*\***\_\_\_**\*\***
**Environment:** **\*\***\_\_\_**\*\***

### Overall Status

- ⬜ All tests passed
- ⬜ Some tests failed (see details)
- ⬜ Not yet tested

### Pass Rate

- Infrastructure: \_\_\_ / 5
- Backend: \_\_\_ / 7
- Frontend: \_\_\_ / 6
- UI Components: \_\_\_ / 30+
- API Integration: \_\_\_ / 7
- Error Handling: \_\_\_ / 5
- **Total:** **_ / _**

### Critical Issues Found

1. ***
2. ***
3. ***

### Recommendations

1. ***
2. ***
3. ***

---

## 🚀 Production Readiness

- ⬜ All critical tests pass
- ⬜ No console errors
- ⬜ Performance targets met
- ⬜ Error handling works
- ⬜ Mobile responsive
- ⬜ Accessibility checked
- ⬜ Security reviewed
- ⬜ Documentation complete

**Status:** ⬜ READY | ⬜ NEEDS WORK | ⬜ NOT READY

---

## 📝 Next Steps After QA

1. **If tests pass:**

   - Tag release: `git tag v1.0.0`
   - Deploy to staging
   - User acceptance testing

2. **If tests fail:**

   - Document issues
   - Prioritize fixes
   - Retest after fixes

3. **Enhancements:**
   - Add integration tests
   - Set up CI/CD
   - Performance monitoring
   - Error tracking (Sentry)

---

**QA Checklist Version:** 1.0.0
**Last Updated:** October 13, 2025
**Maintained By:** VBoarder Team

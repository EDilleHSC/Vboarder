# Beta Testing Documentation

This directory contains all materials needed for VBoarder beta testing.

## Files

- **`BETA_TEST_PLAYBOOK.md`** - Complete testing guide with success criteria, test matrix, and validation commands
- **`beta-notes/`** - Folder for session logs, metrics, and test artifacts
  - `README.md` - Instructions for organizing test data
  - `session-TEMPLATE.md` - Template for per-session notes
  - `metrics.csv` - Aggregated measurements across all sessions
  - `attachments/` - Screenshots, HAR files, logs

## Quick Start

1. **Review the playbook:**

   ```bash
   cat docs/BETA_TEST_PLAYBOOK.md
   ```

2. **Copy session template for your test:**

   ```bash
   cp docs/beta-notes/session-TEMPLATE.md docs/beta-notes/session-yourname-2025-10-14.md
   ```

3. **Run preflight checks:**

   ```bash
   # Backend health
   curl http://127.0.0.1:3738/health
   curl http://127.0.0.1:3738/ready
   curl http://127.0.0.1:3738/agents
   ```

4. **Start testing and log results** in your session file

5. **Append metrics** to `metrics.csv` after each interaction

## Dev Telemetry Endpoints (Optional)

If you've mounted the metrics router in `api/main.py`, you can use:

```bash
# Record telemetry
curl -X POST http://127.0.0.1:3738/telemetry \
  -H 'Content-Type: application/json' \
  -d '{"agent":"CEO","latency_ms":1234,"status":200,"thumbs":1,"tag":"Helpful"}'

# View aggregated metrics
curl http://127.0.0.1:3738/metrics | jq
```

## Success Criteria

- **Reliability:** ≥99% successful responses
- **Quality:** ≥80% thumbs-up ratings
- **Latency:** p50 < 1.5s, p95 < 4s
- **Memory recall:** ≥90% accuracy
- **A11y:** Fully keyboard operable

## Bug Reporting

Use the bug template in `BETA_TEST_PLAYBOOK.md` section 7.

Severity levels:

- **P0** - Blocking (service down, data loss)
- **P1** - Major (key feature broken, poor UX)
- **P2** - Minor (cosmetic, edge cases)

## Privacy

⚠️ **Never commit PII to this directory.** Redact all sensitive data before saving test notes.

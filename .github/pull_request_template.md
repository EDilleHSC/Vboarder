## Summary

- [ ] No runtime behavior changes (moves/renames only unless stated)
- [ ] Registry: api & UI read root `agent_registry.json`
- [ ] Keeps tests passing (25/25)

## Checks

- [ ] `pytest -q`
- [ ] `/health`, `/ready`, `/agents` OK
- [ ] FE build: `npm ci && npm run build`

## Notes

- Ports: BE 3738, FE 3010
- Encoding: UTF‑8 no BOM

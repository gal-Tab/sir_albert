# 06 — wire hooks into hooks.json

**Blocked by:** 03, 04, 05
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 1 + §Component 4

## Goal

Update `plugins/sir-albert/hooks/hooks.json` to declare:
1. The new `SessionStart` hook (session-start.sh)
2. The new `UserPromptSubmit` hook (prompt-router.sh)
3. The existing `freeze-guard.sh` and `session-record.sh` (migrated from `settings.json`)

## Steps

1. Read current `plugins/sir-albert/hooks/hooks.json` (only has `validate-skill.py`).
2. Add entries:
   ```json
   "SessionStart": [{"type": "command", "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/session-start.sh\""}],
   "UserPromptSubmit": [{"type": "command", "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/prompt-router.sh\""}],
   ```
3. Add `freeze-guard.sh` to `PreToolUse` (matcher `Edit|Write`):
   ```json
   {"type": "command", "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/freeze-guard.sh\""}
   ```
4. Add `session-record.sh` to `SessionEnd`:
   ```json
   {"type": "command", "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/session-record.sh\""}
   ```
5. Validate JSON: `python3 -m json.tool plugins/sir-albert/hooks/hooks.json`
6. **Do NOT yet remove the settings.json entries** — that is ticket 07 (the CHECKPOINT).

## Definition of Done

- [ ] `hooks.json` is valid JSON
- [ ] 4 new entries present (SessionStart, UserPromptSubmit, freeze-guard in PreToolUse, session-record in SessionEnd)
- [ ] All paths use `${CLAUDE_PLUGIN_ROOT}` (no absolute paths)
- [ ] `validate-skill.py` entries still present (no regressions)
- [ ] `python3 -m json.tool hooks.json` exits 0

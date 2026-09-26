# 06 — wire hooks.json

**Blocked by:** 03, 04, 04b (precision gate), 05
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 1 + §Component 4

## Goal

Update `plugins/sir-albert/hooks/hooks.json` to declare all new and migrated hooks. **Does not yet touch `~/.claude/settings.json`** (that is ticket 07).

## Steps

1. Read current `plugins/sir-albert/hooks/hooks.json` (only `validate-skill.py` today).
2. Add:
   ```json
   "SessionStart": [
     {"type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py\""}
   ],
   "UserPromptSubmit": [
     {"type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/prompt_router.py\""}
   ]
   ```
3. Add `freeze-guard.sh` to `PreToolUse` (matcher `Edit|Write`):
   ```json
   {"type": "command", "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/freeze-guard.sh\""}
   ```
4. Add `session-record.sh` to `SessionEnd`:
   ```json
   {"type": "command", "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/session-record.sh\""}
   ```
5. Validate: `python3 -m json.tool plugins/sir-albert/hooks/hooks.json`
6. **Do NOT remove settings.json entries yet** — that is ticket 07.

## Definition of Done

- [ ] `hooks.json` valid JSON
- [ ] 4 new entries present (SessionStart, UserPromptSubmit, freeze-guard, session-record)
- [ ] All paths use `${CLAUDE_PLUGIN_ROOT}` (no absolute paths)
- [ ] `validate-skill.py` entries unchanged
- [ ] Precision report passed (04b complete) before this ticket executes

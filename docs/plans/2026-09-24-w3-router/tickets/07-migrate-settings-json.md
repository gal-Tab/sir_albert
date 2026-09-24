# 07 — migrate settings.json (CHECKPOINT)

**Blocked by:** 06
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 4

## Goal

Remove the absolute-path `freeze-guard.sh` and `session-record.sh` entries from `~/.claude/settings.json` so hooks no longer fire twice (once from plugin, once from settings).

## ⚠ CHECKPOINT — live config change

This edits `~/.claude/settings.json`. A mistake here breaks hooks for all projects on this machine. Read the rollback section before proceeding.

**Rollback:** before editing, run:
```bash
cp ~/.claude/settings.json ~/.claude/settings.json.backup-w3
```
To restore: `cp ~/.claude/settings.json.backup-w3 ~/.claude/settings.json`

## Steps

1. **Back up** `~/.claude/settings.json` to `~/.claude/settings.json.backup-w3`.
2. Read current `~/.claude/settings.json` to confirm the two entries to remove:
   - `PreToolUse` / `Edit|Write`: `bash /Users/galta/Development/sir_albert/plugins/sir-albert/hooks/freeze-guard.sh`
   - `SessionEnd`: `bash /Users/galta/Development/sir_albert/plugins/sir-albert/hooks/session-record.sh`
3. Edit `settings.json`: remove those two entries only. Leave all other entries intact (guard.sh, nanoclaw-validate.sh, axcli entries, etc.).
4. Start a new claude session and verify:
   - Trigger freeze-guard: edit a file while `.memory-bank/.freeze` exists — should still block.
   - Trigger session-record: end session — `tail ~/.claude/sir-albert-sessions.jsonl` should show a new entry.
   - Confirm no duplicate lines (hooks fired exactly once).
5. Commit: `chore: migrate freeze-guard + session-record from settings.json to hooks.json`.

## Definition of Done

- [ ] Backup file exists at `~/.claude/settings.json.backup-w3`
- [ ] `settings.json` no longer contains the two absolute-path entries
- [ ] `hooks.json` contains both entries via `${CLAUDE_PLUGIN_ROOT}`
- [ ] freeze-guard tested: blocks on `.freeze`, passes without
- [ ] session-record tested: new entry appears in `~/.claude/sir-albert-sessions.jsonl`
- [ ] No double-firing observed

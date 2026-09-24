# 03 — session-start.sh

**Blocked by:** 01, 02
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 1

## Goal

Write `plugins/sir-albert/hooks/session-start.sh` — the `SessionStart` hook script that reads `HOOK_CONTEXT.md`, fills placeholders, and emits `hookSpecificOutput.additionalContext` JSON.

## Steps

1. Study the superpowers `session-start` hook at `~/.claude/plugins/cache/claude-plugins-official/superpowers/6.4.1/hooks/session-start` for the correct JSON output shape (already in context from spec research).
2. Create `plugins/sir-albert/hooks/session-start.sh`:
   - `set -euo pipefail`
   - Determine `SCRIPT_DIR` and `PLUGIN_ROOT` (same pattern as superpowers)
   - Read `HOOK_CONTEXT.md` into a variable
   - Run pack detection: for each `pack_signals` entry in `router-data.json`, probe the filesystem under `$PWD` using `find` or `test -d`. Collect matching pack names. Fall back to `(none detected)` if empty.
   - Run resume detection: `ls .memory-bank/HANDOFF-*.md 2>/dev/null | sort | tail -1` — if found, emit the hint line; else empty string.
   - Replace `{PACK_LIST}` and `{RESUME_HINT}` in the template (bash parameter substitution — no sed).
   - Char-count guard: `wc -c` on final string; if > 800, log `[sir-albert] WARNING: injection over 800 chars, skipping` to stderr and exit 0 (session continues without injection).
   - Escape for JSON (reuse the `escape_for_json` bash function from superpowers — it's a good pattern).
   - Emit only Claude Code format: `hookSpecificOutput.additionalContext` (no Cursor/Copilot branches — we only target Claude Code for now).
3. `chmod +x plugins/sir-albert/hooks/session-start.sh`
4. Smoke test locally: `CLAUDE_PLUGIN_ROOT=$(pwd)/plugins/sir-albert bash plugins/sir-albert/hooks/session-start.sh | python3 -m json.tool`

## Definition of Done

- [ ] Script exists and is executable
- [ ] Emits valid JSON with `hookSpecificOutput.additionalContext`
- [ ] Pack detection returns correct packs for a GTM project (has `apply-*.ts`) vs a plain dir
- [ ] Resume hint appears when `.memory-bank/HANDOFF-*.md` exists and is absent otherwise
- [ ] Char-count guard fires on an artificially inflated template (test manually)
- [ ] `CLAUDE_PLUGIN_ROOT=... bash session-start.sh | python3 -m json.tool` exits 0

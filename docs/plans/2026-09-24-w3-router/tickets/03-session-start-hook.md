# 03 — session_start.py

**Blocked by:** 01, 02
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 1

## Goal

Write `plugins/sir-albert/hooks/session_start.py` — the `SessionStart` hook in Python (Unicode safety, easy pytest, matches kb hooks style).

## Steps

1. Create `plugins/sir-albert/hooks/session_start.py`:
   - Determine `SCRIPT_DIR` via `pathlib.Path(__file__).parent`
   - Read `HOOK_CONTEXT.md` as text
   - Run pack detection: for each `pack_signals` entry in `router_data.json`, probe `Path(os.environ.get("PWD", "."))` using `glob` or `Path.exists()`. Collect matching pack names. Default: `"(none detected)"`.
   - Run resume detection: `sorted(Path(".memory-bank").glob("HANDOFF-*.md"))[-1]` if `.memory-bank/` exists and has matches. If `os.environ.get("DISABLE_RESUME_HINT")` is set, skip.
   - Fill template: `content.replace("{PACK_LIST}", pack_str).replace("{RESUME_HINT}", resume_str)`
   - Char-count guard: `if len(filled) > 800: print("[sir-albert] WARNING: injection over 800 chars, skipping", file=sys.stderr); sys.exit(0)`
   - Escape for JSON: replace `\`, `"`, newlines per standard JSON string rules
   - Output to stdout (Claude Code format):
     ```json
     {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}
     ```
2. Add shebang `#!/usr/bin/env python3` and `chmod +x`.
3. Smoke test: `CLAUDE_PLUGIN_ROOT=<path> python3 plugins/sir-albert/hooks/session_start.py | python3 -m json.tool`
4. Test with a GTM fixture dir: `cd /tmp/test-gtm && touch apply-deploy.ts && CLAUDE_PLUGIN_ROOT=<plugin_root> python3 session_start.py` — should show `gtm` in pack list.

## Definition of Done

- [ ] Script exists, executable, Python 3
- [ ] Emits valid JSON with `hookSpecificOutput.additionalContext`
- [ ] GTM fixture → `gtm` in pack list; plain dir → `(none detected)`
- [ ] Resume hint present when `.memory-bank/HANDOFF-*.md` exists; absent when `DISABLE_RESUME_HINT=1`
- [ ] Output is ≤800 chars on the standard template
- [ ] Char-count guard fires on a padded template (verify manually)
- [ ] `python3 session_start.py | python3 -m json.tool` exits 0

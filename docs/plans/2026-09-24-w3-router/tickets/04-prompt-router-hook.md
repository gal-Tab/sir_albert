# 04 — prompt_router.py (UserPromptSubmit)

**Blocked by:** 01, 04a (Hebrew patterns approved), 04b (precision gate passed)
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 2

## Goal

Write `plugins/sir-albert/hooks/prompt_router.py` — the `UserPromptSubmit` hook in Python. Phrase-level patterns only; silent on no match.

## Steps

1. Create `plugins/sir-albert/hooks/prompt_router.py`:
   - Read stdin JSON: `data = json.load(sys.stdin)`, extract `prompt = data.get("prompt", "")`
   - Load `router_data.json` from `SCRIPT_DIR`
   - Sort patterns by `order` field
   - For each pattern: `if re.search(pattern, prompt, re.IGNORECASE | re.UNICODE)` → first match wins
   - On match: output `{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "→ <nudge>"}}`
   - On no match: output nothing (`sys.exit(0)` with no print)
   - Target: <50 ms on a 200-char prompt (no I/O on no-match path except reading router_data.json once)
2. Add shebang `#!/usr/bin/env python3`, `chmod +x`, `export PYTHONIOENCODING=utf-8` in shebang env or set in script.
3. Smoke tests:
   ```bash
   echo '{"prompt":"let'\''s brainstorm this"}' | python3 prompt_router.py
   # → {"hookSpecificOutput": ...} with "brainstorm (explore mode)"

   echo '{"prompt":"execute this SQL"}' | python3 prompt_router.py
   # → (no output)

   echo '{"prompt":"what time is it"}' | python3 prompt_router.py
   # → (no output)
   ```
4. Time the no-match path: `time echo '{"prompt":"what time is it"}' | python3 prompt_router.py` → <50 ms.

## Definition of Done

- [ ] Script exists, executable, Python 3
- [ ] Match → JSON with nudge; no-match → empty stdout
- [ ] `"execute this SQL"` → empty stdout
- [ ] `"publish the GTM container"` → empty stdout
- [ ] `"challenge accepted"` → empty stdout
- [ ] Hebrew approved prompts match (after ticket 04a)
- [ ] `time` on no-match path < 50 ms

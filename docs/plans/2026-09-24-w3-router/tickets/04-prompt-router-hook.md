# 04 — prompt-router.sh (UserPromptSubmit)

**Blocked by:** 01
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 2

## Goal

Write `plugins/sir-albert/hooks/prompt-router.sh` — the `UserPromptSubmit` hook that reads the prompt from stdin JSON, matches against `router-data.json` patterns, and emits a one-line nudge or nothing.

## Steps

1. Create `plugins/sir-albert/hooks/prompt-router.sh`:
   - `set -euo pipefail`
   - Read stdin JSON, extract prompt text via `jq -r '.prompt // ""'`
   - Read `keyword_patterns` from `router-data.json` (sorted by `order`)
   - For each pattern: `echo "$prompt" | grep -iP "$pattern" > /dev/null 2>&1` — first match wins
   - On match: emit `{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "→ <nudge>"}}`
   - On no match: emit nothing (exit 0 with no output)
   - Budget: must complete in <50 ms on a 200-char prompt (benchmark with `time` on a no-match path)
2. `chmod +x plugins/sir-albert/hooks/prompt-router.sh`
3. Smoke tests:
   - `echo '{"prompt":"let'\''s brainstorm this idea"}' | bash plugins/sir-albert/hooks/prompt-router.sh` → should include `brainstorm (explore mode)`
   - `echo '{"prompt":"what time is it"}' | bash plugins/sir-albert/hooks/prompt-router.sh` → empty output
   - `echo '{"prompt":"חקור אותי"}' | bash plugins/sir-albert/hooks/prompt-router.sh` → should include `brainstorm grill`

## Definition of Done

- [ ] Script exists and is executable
- [ ] Match returns JSON with nudge string
- [ ] No-match returns empty output (not `null`, not `{}`)
- [ ] Hebrew prompt matches correctly (UTF-8 locale set in script)
- [ ] `time` on no-match path shows < 50 ms

# 11 — verification

**Blocked by:** 06, 07, 09-bootstrap-sh, 10
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` (all components)

## Goal

End-to-end verification in a fresh session. Confirm injection fires, nudges route correctly, hooks fire exactly once, char count is within budget, no-match cases are silent, and pytest passes.

## Steps

1. **pytest**: `cd plugins/sir-albert && python3 -m pytest tests/ -v` — 0 failures.

2. **Injection check**:
   ```bash
   CLAUDE_PLUGIN_ROOT=$(pwd)/plugins/sir-albert \
     python3 plugins/sir-albert/hooks/session_start.py | python3 -m json.tool
   ```
   Extract `additionalContext`. Measure: `python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d['hookSpecificOutput']['additionalContext']))" < <(python3 plugins/sir-albert/hooks/session_start.py)`
   **Must be ≤800.**
   Paste the full injection text in the "Paste injection text here" section below.

3. **Nudge routing — 1 sample per route**:
   | Prompt | Expected nudge |
   |---|---|
   | `let's brainstorm this` | `→ /sir-albert:brainstorm (explore mode)` |
   | `attack my plan` | `→ /sir-albert:brainstorm attack` |
   | `grill me on this` | `→ /sir-albert:brainstorm grill` |
   | `zoom out from this` | `→ /sir-albert:brainstorm zoom-out` |
   | `let's design this` | `→ /sir-albert:brainstorm design` |
   | `make a plan` | `→ /sir-albert:plan` |
   | `implement the plan` | `→ /sir-albert:execute` |
   | `help me debug why this is broken` | `→ /sir-albert:debug` |
   | `ship this branch` | `→ /sir-albert:build` |
   | `write a handoff` | `→ /sir-albert:handoff` |
   | `where were we` | `→ /sir-albert:resume` |
   Run each: `echo '{"prompt":"<text>"}' | python3 plugins/sir-albert/hooks/prompt_router.py`

4. **No-match / false-positive check** (must all produce empty stdout):
   - `"execute this SQL"` → empty
   - `"publish the GTM container"` → empty
   - `"what time is it"` → empty
   - `"challenge accepted"` → empty
   - Verify: `echo '{"prompt":"execute this SQL"}' | python3 ... | wc -c` → 0

5. **Precision report**: confirm `docs/plans/2026-09-24-w3-router/precision-report-*.txt` exists and shows overall fire rate < 15%.

6. **Hook fire count**:
   - Start a session; edit a file — freeze-guard fires once (not twice). No double-fire warnings in stderr.
   - End session — `tail -1 ~/.claude/sir-albert-sessions.jsonl` shows exactly one new entry.

7. **superpowers coexistence**: confirm superpowers still active; sir-albert injection also present; no observed conflicts.

## Paste injection text here

```
(paste actual additionalContext string from step 2)
char count: XXX / 800 max
```

## Definition of Done

- [ ] `pytest` 0 failures
- [ ] Injection char count ≤ 800 (measured, not estimated)
- [ ] All 11 nudge routes produce correct output
- [ ] All 4 false-positive prompts produce empty stdout
- [ ] Precision report exists, fire rate < 15%
- [ ] freeze-guard fires exactly once per edit
- [ ] session-record fires exactly once per session end
- [ ] superpowers still active (W4 gate)

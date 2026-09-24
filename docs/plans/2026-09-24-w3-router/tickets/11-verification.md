# 11 — verification

**Blocked by:** 07, 09, 10
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` (all components)

## Goal

End-to-end verification in a fresh session. Confirm the full W3 setup works as designed: injection fires, nudges route correctly, hooks fire exactly once, pytest passes.

## Steps

1. **pytest**: `cd plugins/sir-albert && python3 -m pytest tests/ -v` — 0 failures.

2. **Fresh session injection check**:
   Run `claude --plugin-dir /Users/galta/Development/sir_albert/plugins -p "list your active sir-albert core skills"` in a project dir with GTM signals (has `apply-*.ts`).
   Paste the full session-start injection text below (from the `additionalContext` field — inspect with `CLAUDE_PLUGIN_ROOT=... bash hooks/session-start.sh | jq`).
   Record token count: `wc -c` on the injection string; must be ≤ 800 chars.

3. **Nudge routing — 1 sample per route**:
   | Prompt | Expected nudge |
   |---|---|
   | "let's brainstorm this idea" | `→ /sir-albert:brainstorm (explore mode)` |
   | "attack my plan" | `→ /sir-albert:brainstorm attack` |
   | "grill me on this" | `→ /sir-albert:brainstorm grill` |
   | "zoom out from this" | `→ /sir-albert:brainstorm zoom-out` |
   | "make a plan for the spec" | `→ /sir-albert:plan` |
   | "debug why this is broken" | `→ /sir-albert:debug` |
   | "ship this branch" | `→ /sir-albert:build` |
   | "חקור אותי" | `→ /sir-albert:brainstorm grill` |
   Run each via `echo '{"prompt":"<text>"}' | bash hooks/prompt-router.sh`.

4. **No-match check**:
   `echo '{"prompt":"what time is it"}' | bash hooks/prompt-router.sh` → empty stdout (pipe to `wc -c`, expect 0).

5. **Hook fire count**:
   Start a session, edit a file — confirm `freeze-guard.sh` fires once (not twice). Check stderr for any double-fire warnings.
   End the session — `tail -1 ~/.claude/sir-albert-sessions.jsonl` shows exactly one new entry.

6. **superpowers coexistence**:
   Confirm `using-superpowers` injection is still present (superpowers not uninstalled). Confirm sir-albert injection also present. Confirm no conflicts visible in session behavior.

## Paste injection text here

```
(paste actual additionalContext string from step 2)
char count: XXX / 800 max
```

## Definition of Done

- [ ] `pytest` 0 failures
- [ ] Injection char count ≤ 800
- [ ] All 8 nudge routes produce correct output
- [ ] No-match produces empty stdout
- [ ] freeze-guard fires once (not twice) during an edit
- [ ] session-record fires once (not twice) at session end
- [ ] superpowers still active (W4 gate: uninstall only after eval)

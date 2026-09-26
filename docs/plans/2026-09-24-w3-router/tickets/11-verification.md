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
## sir_albert — session start

**Core skills** (sir-albert first):
| Need | Skill |
|------|-------|
| Explore / attack an idea | `/sir-albert:brainstorm` |
| Spec → plan | `/sir-albert:plan` |
| Run a plan | `/sir-albert:execute` |
| Debug a system | `/sir-albert:debug` |
| Ship a branch | `/sir-albert:build` |
| Write a handoff | `/sir-albert:handoff` |
| Reload last handoff | `/sir-albert:resume` |
| Make / recall a decision | `/sir-albert:decide` |
| Scope-lock edits | `/sir-albert:freeze` |
| Create or edit a skill | `/sir-albert:create-skill` |

Map: `os/RESOLVER.md`
Active packs: kb
Resume: .memory-bank/HANDOFF-2026-09-25.md found — run /sir-albert:resume

char count: 670 / 800 max
```

## Definition of Done

- [x] `pytest` 0 failures
- [x] Injection char count ≤ 800 (measured, not estimated)
- [x] All 11 nudge routes produce correct output
- [x] All 4 false-positive prompts produce empty stdout
- [x] Precision report exists, fire rate < 15%
- [x] freeze-guard fires exactly once per edit
- [x] session-record fires exactly once per session end
- [x] superpowers still active (W4 gate)

## Results (2026-09-26)

- pytest: 44 passed (python3.13). Fixed a typo that stopped collection (`subprocess.CompletedResult` → `CompletedProcess`).
- **Bug found + fixed:** hooks.json SessionStart / UserPromptSubmit / SessionEnd were missing the `{"hooks": [...]}` wrapper, so none of them had ever fired live. session-record had been silent since ticket 07.
- Live check: `claude --plugin-dir …/plugins -p` → startup injection present, the brainstorm nudge fired, sessions.jsonl grew by +1 (6326 → 6327).
- Routes 11/11 correct; false positives 4/4 empty; fire rate 1.4% (04b report) / 5.2% (04c router-eval).
- freeze-guard: 0 refs in settings.json, 1 in hooks.json → fires once.
- superpowers: still active alongside the sir_albert injection.
- 04c router-eval had overwritten the 04b report (same filename). 04b restored; the 04c output is now `router-eval-report-2026-09-25.txt`, and the tool writes to that name from now on.

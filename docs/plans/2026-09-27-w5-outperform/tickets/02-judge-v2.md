# 02 — judge-v2

**Blocked by:** —
**Spec:** `docs/specs/2026-09-27-w5-outperform.md §Judge`

## Goal
`blind_judge.py` can judge any arm pair (B vs S, B vs A). It uses a rubric on up to 6,000 chars of each final answer, runs on a judge model that differs from the model under test, and marks cut-off runs identically on both sides. W4 defaults stay unchanged.

## Why
W4 judge: 1,500-char truncation, Sonnet judging Sonnet, no rubric, arms hard-coded to `a`/`b`. It can't resolve a quality lead, and it can't pair B with the new arm S.

## Steps
1. Write the failing tests in `plugins/sir-albert/tests/eval/test_blind_judge.py`:
   - `test_max_chars_flag`: `summarize(art, max_chars=6000)` keeps a 5,000-char answer whole. The default is still 1500.
   - `test_pair_flag_selects_arms`: `--pair b:s` pairs `b-*` with `s-*` artifacts and ignores `a-*`. Left/right are still randomized by AB/BA order.
   - `test_rubric_prompt`: with `--rubric`, the prompt contains the 4 criteria (below) and still contains the `[skill]` redaction note.
   - `test_cutoff_marker_symmetric`: a `truncated: true` artifact's text ends with `[Response cut off by the evaluation's turn/budget cap.]`. A non-truncated artifact doesn't get the marker.
   - `test_resolved_rows_name_arms`: resolved rows record `left_arm`/`right_arm`, and `final_verdict` ∈ {`<x>_wins`, `<y>_wins`, `tie`}, using the arm letters.
2. Run: `/usr/local/bin/python3.13 -m pytest -q plugins/sir-albert/tests/eval/test_blind_judge.py`. Expected: 5 FAIL.
3. Implement in `plugins/sir-albert/tools/eval/blind_judge.py`:
   - Add `--max-chars` (default 1500), `--pair` (default `a:b`), and `--rubric` (flag).
   - Add `RUBRIC_PROMPT`: "Judge which response better serves the user, on: (1) progress on what was asked; (2) correctness and grounding, with no invented facts, files, or IDs; (3) the right call between acting and asking; (4) honesty about incomplete work: a response that only announces work in progress or background tasks, without delivering, counts as incomplete."
   - Output file per pair: `--out` is unchanged; resolved goes to `<out-stem>-resolved.jsonl`.
   - Keep W4's `a:b` resolution labels `A_wins`/`B_wins` so `verdict.py` still works.
4. Run the step 2 command again. Expected: PASS. Full suite: `/usr/local/bin/python3.13 -m pytest -q plugins/sir-albert/tests/`. Expected: all pass.
5. Live check (~$0.10, AUTO). Rejudge one W4 pair (`600120ad468a3201` rep 2) with `--model claude-opus-5-5 --rubric --max-chars 6000 --pair a:b` in a `mktemp -d` symlinked runs dir (the same method as the 2026-09-27 smoke test). Then `grep '"model"' ~/.claude/settings.json`. Expected: both calls parse, the reasons cite rubric criteria, and the model is restored.
6. Commit: `git commit -m "feat(w5): judge v2 — any arm pair, rubric, 6k chars, symmetric cut-off marker"`

## Definition of Done
- [ ] 5 new tests fail on the old code and pass on the new code; the suite is green
- [ ] W4 invocation (no new flags) produces byte-identical prompts to today
- [ ] Live Opus judge call parses, cites the rubric, and costs < $0.10

⚠️ Risk: Opus-judging-Sonnet still has model-family self-preference. It is symmetric across arms, since every arm runs on Sonnet 5. Note it in the spec.

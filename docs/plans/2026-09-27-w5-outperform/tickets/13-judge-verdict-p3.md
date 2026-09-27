# 13 — judge-verdict-p3

**Blocked by:** 02, 12

## Goal
Judge v2 verdicts for B-vs-S and B-vs-A, and `verdict_p3.py` computing G1–G4 exactly as pre-registered. The result is OUTPERFORM / FAIL / ABORT / INCONCLUSIVE plus a separate UNINSTALL-SAFE line.

## Steps
1. Write the failing tests in `plugins/sir-albert/tests/eval/test_verdict_p3.py`. All fixtures use the **real schemas**: sample rows keyed `_hash` with `p2_slice`-style `p3_slice`, artifacts with `skills_called` as namespaced strings, and judge-v2 resolved rows with `left_arm`/`right_arm`.
   - G1–G3 per-run rates per arm, including a case where B ties S on G2 → FAIL (strict >).
   - G3 counts a `sir-albert:create-skill` call on a control as a fire (the W4 A case).
   - G4 bootstrap is deterministic with seed 0; the lower bound on a known fixture matches a hand-computed value.
   - Exit codes 0/1/2/3; the UNINSTALL-SAFE line is independent of OUTPERFORM.
   - ABORT when the run count ∉ {90 (rep 1 only), 180} or judge_error > 5%.
   - `--rep-1-only` mode emits a `REP2_NEEDED` line listing every Amendment 2 trigger that fired, with margins. Exit code 4 means rep 2 is needed.
2. Run: `/usr/local/bin/python3.13 -m pytest -q plugins/sir-albert/tests/eval/test_verdict_p3.py`. Expected: FAIL (module missing).
3. Implement `plugins/sir-albert/tools/eval/verdict_p3.py`, reusing `_skill_to_route` from `prompt_corpus.py`. Report: gates table, per-slice rates per arm, win-rates with CI for both comparisons, cut-offs per arm, "describes Sonnet 5", and the fixed "uninstall is Gal's decision" paragraph.
4. Run the step 2 command again. Expected: PASS. Full suite green.
5. Smoke-test the judge on 1 B-vs-S pair (~$0.08), then check the model.
6. Full judge (~$10, AUTO under the plan budget; sequential): `blind_judge.py --runs-dir docs/plans/2026-09-27-w5-outperform/runs-p3 --pair b:s --rubric --max-chars 6000 --model claude-opus-5-5 --out docs/plans/2026-09-27-w5-outperform/judgments-bs.jsonl`, then the same with `--pair b:a` → `judgments-ba.jsonl`. `W4_RESTORE_MODEL='claude-opus-5-5[1m]'`.
7. Bias checks before the verdict: position split (left vs right wins), count of reasons mentioning `[skill]`/placeholder/template (expect 0), and the judge_error count.
8. Spot-check by hand 3 judgments per comparison (one per verdict type) against the full artifacts. Record them in the report.
9. Run `verdict_p3.py --runs-dir … --judgments-bs … --judgments-ba … --sample docs/plans/2026-09-27-w5-outperform/sample-p3.jsonl --out-dir docs/plans/2026-09-27-w5-outperform`.
10. Sensitivity: rerun G4 excluding (a) pairs with any cut-off and (b) pairs where only one side has `[skill]`. Report the range.
11. Commit the tooling (not the judgments or runs): `git commit -m "feat(w5): P3 verdict — outperform + uninstall-safe gates"`

## Definition of Done
- [ ] Real-schema fixtures; every new test fails on missing or old code and passes on the new code
- [ ] Both judge passes complete with judge_error ≤ 5%; bias checks recorded
- [ ] Verdict report written, sensitivity range included

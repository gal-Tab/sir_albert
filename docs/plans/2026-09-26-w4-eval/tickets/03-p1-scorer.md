# 03 — p1-scorer

**Blocked by:** 01, 02
**Spec:** `docs/specs/2026-09-26-w4-eval.md §P1 — Router scorecard / Pass bar`

## Goal
Add a `p1-score` subcommand to `prompt_corpus.py` that computes overall precision (gate ≥80% on the n=102 router-match slice), recall (diagnostic ≥50% on n=30), and false-fire rate (gate ≤10% on n=10); emits `p1-scorecard-2026-09-26.md` with a confusion table, a per-route breakdown (only plan/brainstorm/handoff get a percentage — all other routes emit "under-powered (n=<count>)" per the measured distribution), and a dead-route report (6 routes with zero corpus matches as of 2026-09-26); and halts with exit 2 if either gate fails.

## Steps

1. Write failing test `plugins/sir-albert/tests/eval/test_p1_scorer.py`:
   - Fixture PASS: 102 router-match rows (84 label==predicted_route, 18 do not), 30 task-initiating (16 correctly routed by `_route`), 10 negative controls (0 fire) → precision=84/102=82.4%, recall=16/30=53%, FF=0% → exits 0
   - Fixture FAIL_PRECISION: 78 correct of 102 → precision=76.5% → exits 2, prints `GATE FAIL: precision 76.5% < 80.0%`
   - Fixture FAIL_FF: 2 negative controls fire → FF=20% → exits 2, prints `GATE FAIL: false-fire 20.0% > 10.0%`
   - Fixture INSUFFICIENT: all labels null → exits 2, prints `GATE FAIL: 0 labelled rows in router_match slice — run validate-labels first`

   Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_p1_scorer.py -q` — Expected: FAIL

2. Add `cmd_p1_score(args)` to `plugins/sir-albert/tools/prompt_corpus.py` and wire as `p1-score`:
   - Load `--file` arg (default: `str(EVAL_DIR / "labeled-set.jsonl")`)
   - Split rows by `slice` field: `router_match`, `task_initiating`, `negative_control`
   - Guard: if router_match rows with non-null label == 0, print insufficient message and `sys.exit(2)`

3. Implement precision computation:
   - Precision = (rows where `slice=="router_match"` and `label == predicted_route`) / (rows where `slice=="router_match"` and `label is not null`)
   - Hard stop: `if precision < 0.80: print(f"GATE FAIL: precision {precision:.1%} < 80.0%"); sys.exit(2)`

4. Implement recall computation (diagnostic only):
   - `patterns = _compile_patterns()`
   - Recall = (rows where `slice=="task_initiating"` and `label not in ("none","ambiguous",None)` and `_route(text, patterns) == label`) / (rows where `slice=="task_initiating"` and `label not in ("none","ambiguous",None)`)
   - Report but do NOT gate

5. Implement false-fire computation:
   - FF = (rows where `slice=="negative_control"` and `_route(text, patterns) is not None`) / (rows where `slice=="negative_control"`)
   - Hard stop: `if ff > 0.10: print(f"GATE FAIL: false-fire {ff:.1%} > 10.0%"); sys.exit(2)`

6. Build per-route breakdown table:
   - For each intent in `_compile_patterns()` (deduplicated): count TP = rows where `label==predicted_route==intent`, FP = rows where `predicted_route==intent and label!=intent`
   - If TP+FP >= 5 (i.e., plan, brainstorm, handoff): compute precision and recall percentage
   - If TP+FP < 5: emit `under-powered (n=<TP+FP>)` in the precision column
   - Order by FP count descending (most problematic first)

7. Build dead-route report:
   - Load `_compile_patterns()` → get all unique intents
   - Query corpus for each intent: count rows where `predicted_route == intent`
   - For each intent with count == 0: emit `| {intent} | {pattern_str[:80]} | {pre_diagnosis} |`
   - The scorer must compute dead routes at runtime, not hardcode them; but the scorecard SHOULD emit the following pre-diagnosed root causes for the routes confirmed dead on 2026-09-26 corpus:
     - `build`: **Vocabulary mismatch** — corpus has 86 prompts with "open pr"/"merge"/"push" but pattern requires "finish the branch"/"ship this feature". Fix: extend pattern.
     - `resume`: **Regex-impossible** — Gal types "continue" which is also his most common mid-thread reply; matching it would breach the false-fire gate. No regex fix is safe; route may need to be dropped or replaced with a context-aware signal.
     - `grill`, `zoom-out`, `slack-hebrew`, `linkedin-hebrew`: **No corpus demand** — only 7 Hebrew prompts of 1,938 total; these routes are unmeasurable at current corpus size. Decision to keep or drop is Gal's, not a scorer fix.
   - The scorer emits the pre-diagnosis string for each dead route if the route name is in the above list; otherwise emits `diagnosis: _`

8. Write `docs/plans/2026-09-26-w4-eval/p1-scorecard-2026-09-26.md`:
   - `## Summary` table: Precision / Recall / False-fire + PASS/FAIL for each metric
   - `## Dead Routes` (top-level section, not a footnote): table of dead route | patterns | diagnosis
   - `## Per-route breakdown` (plan/brainstorm/handoff with percentages; others with under-powered label)
   - `## Ranked fix list`: routes sorted by FP count, with up to 3 sample FP prompts per route and a concrete fix suggestion slot

9. Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_p1_scorer.py -q` — Expected: PASS

10. Smoke run on null-label stub:
    `/usr/local/bin/python3.13 plugins/sir-albert/tools/prompt_corpus.py p1-score` — Expected: exits 2 with `GATE FAIL: 0 labelled rows in router_match slice — run validate-labels first` (no traceback)

## Definition of Done
- [ ] `p1-score` subcommand computes overall precision, recall (diagnostic), false-fire
- [ ] Exits 2 with `GATE FAIL` message if precision < 80% or false-fire > 10%
- [ ] Per-route precision column shows percentage only for routes with n≥5; emits `under-powered (n=N)` for all others
- [ ] Dead-route report computed at runtime, listed as top-level section of the scorecard
- [ ] `p1-scorecard-2026-09-26.md` emitted on PASS (exits 0) or updated-with-gate-fail (exits 2) — file always written
- [ ] Tests pass: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_p1_scorer.py -q`
- [ ] Smoke run on null stub exits 2 cleanly (no traceback)

## Review corrections (binding, supersede the steps above where they conflict)

1. **`ambiguous` is excluded from every denominator** (spec §Labeled set). Precision = `label == predicted_route` over router-match rows with `label not in (None, "ambiguous")`. Add a fixture where 10 `ambiguous` rows do not move precision.
2. **Compute everything, write the scorecard, THEN exit.** Steps 3 and 5 `sys.exit(2)` mid-computation, before the file is written, which contradicts the DoD. On a FAIL the scorecard is the thing Gal needs. Gate failures are collected, the file is written with FAIL marked, and then the scorer exits 2.
3. **False-fire denominator** = negative controls Gal labelled `none`. A control he labelled with a route is not a false fire; it is a recall case. Report the note: *the control slice is a low-power sanity check (n≈10). The real wrong-fire evidence is router-match rows labelled `none`, which precision captures.* Also report that count separately as **"fired on a non-task prompt: N of 102"**.
4. **Per-route threshold is n ≥ 10**, not 5. That yields exactly plan (41), brainstorm (31) and handoff (15), which matches the spec. `execute` (6) is reported as under-powered.

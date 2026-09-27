# 10 — fanout-in-turn (re-scoped 2026-09-27: harness fix, not a skill fix)

**Blocked by:** 01 (both edit the `run_one.sh` stream parser)

## Goal
A run's artifact reflects its **final** answer. When background agents make `claude -p` emit several `result` events, the artifact's `result_event`, cost, and `truncated` come from the last one.

## Why
Probe C in `04-probe-results.md` (coordinator, 2026-09-27): with `run_in_background: true`, headless `claude -p` does not exit early. It emits `result` #1 ("…I'll let you know once it completes"), then resumes on the task notification and emits `result` #2 with the real answer (plus a #3 "already reported"). `run_one.sh` keeps the **first** `result` event (`next(...)`). W4 artifact `b-600120ad468a3201-rep2` has 5,371 chars of synthesis after its first result, but the judge saw only the status line, and that pair went to A. The brainstorm skill was fine; the harness was wrong. No SKILL.md change is needed.

## Steps
1. Build a text-free fixture `plugins/sir-albert/tests/eval/fixtures/multi-result.jsonl`, modelled on probe C's event order: init → assistant text → Agent tool_use (`run_in_background: true`) → tool_result "Async agent launched" → assistant text "…running in the background" → `result` (`result_index` 0, `total_cost_usd` 0.17, result "status line") → `task_notification` → assistant text "final answer" → `result` (`result_index` 1, `total_cost_usd` 0.18, result "final answer").
2. Write the failing tests in `plugins/sir-albert/tests/eval/test_run_executor.py`:
   - `test_last_result_event_wins`: artifact `result_event.result` is "final answer" and `cost_usd` is 0.18.
   - `test_result_count_recorded`: artifact `result_count` is 2.
   - `test_truncated_uses_last_result`: truncated if the LAST result lacks `result`, even when an earlier one has it.
3. Run: `/usr/local/bin/python3.13 -m pytest -q plugins/sir-albert/tests/eval/test_run_executor.py -k result`. Expected: FAIL.
4. Implement in the `run_one.sh` embedded parser: collect all `result` events and use the last for `result_ev`. Take cost from the max `total_cost_usd` (it's cumulative; check this on the fixture and on probe C). Add `result_count`.
5. Run the step 3 command again. Expected: PASS. Full suite green.
6. W4 impact note (no spend): list the W4 artifacts whose `assistant_text` continues more than 40 chars past their first result text. Expected: exactly `b-600120ad468a3201-rep2`. Record it in `docs/plans/2026-09-27-w5-outperform/10-w4-impact.md`: 1 of 30 pairs was misjudged, and the W4 verdict doesn't change (the skill gate fails regardless). Don't edit W4 artifacts.
7. Commit: `git commit -m "fix(w5): artifacts use the final result event (background agents resume headless runs)"`

## Definition of Done
- [ ] New tests fail on the old code and pass on the new code; the suite is green
- [ ] Fixture matches probe C's real event order
- [ ] W4 impact recorded, with no W4 files modified

# 03 — infra-error-text

**Blocked by:** —

## Goal
A run whose final answer is an `API Error: …` message is treated as an infra error (quarantined to `invalid/` and retried), even when it cost money.

## Why
W4 artifact `b-0c4bbdadad6f78d8-rep1` cost $0.51, ended with `API Error: The system encountered an unexpected error…`, and was scored as a valid run (judge split → tie). `is_infra_error` only catches $0 errors.

## Steps
1. Add a text-free fixture `plugins/sir-albert/tests/eval/fixtures/api-error-paid.json`: arm b, `cost_usd` 0.51, `result_event.is_error` true, `result_event.subtype` `success`, `result_event.result` `"API Error: The system encountered an unexpected error during processing. Try your request again."`
2. Write the failing tests in `plugins/sir-albert/tests/eval/test_run_tranche.py`:
   - `test_paid_api_error_is_infra`: `is_infra_error(fixture)` is True.
   - `test_budget_cap_is_not_infra`: an `error_max_budget_usd` artifact with ordinary assistant text is False (cut-offs stay valid by design).
3. Run: `/usr/local/bin/python3.13 -m pytest -q plugins/sir-albert/tests/eval/test_run_tranche.py -k infra`. Expected: the first FAILs.
4. Implement in `plugins/sir-albert/tools/eval/run_tranche.py` `is_infra_error`: also return True when `(result.get("result") or artifact.get("assistant_text") or "").strip().startswith("API Error:")`.
5. Run the step 3 command again. Expected: PASS. Full suite green.
6. Retro-check (no spend): `/usr/local/bin/python3.13 -c` over `docs/plans/2026-09-26-w4-eval/runs/*.json` using the new function. Expected: exactly 1 hit (`b-0c4bbdadad6f78d8-rep1`). Record it in the commit message. Do not move W4 artifacts; the W4 verdict is already reported.
7. Commit: `git commit -m "fix(w5): paid API-error runs are infra errors, not valid runs"`

## Definition of Done
- [ ] New tests fail on the old code and pass on the new code; the suite is green
- [ ] Retro-check finds exactly the known W4 case

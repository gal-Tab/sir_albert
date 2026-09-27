# 11 — dev-loop

**Blocked by:** 01, 03, 05 (spec commit only, step 2), 06, 07, 08, 09, 10

## Goal
A cheap arm-B-only replay of the 15 W4 tuning prompts, with context, meets the dev bar within ≤ 2 rounds (spec Amendment 2): happy 5/5, router-silent ≥ 3/5, control 0 fires.

## Steps
1. Write the failing tests in `plugins/sir-albert/tests/eval/test_run_tranche.py`:
   - `test_arms_flag_b_only`: `run_tranche.py --arms b --rows all --reps 1 …` schedules 15 jobs, all arm b.
   - `test_context_passed`: jobs whose sample row has `preceding_turns` pass a context file as arg 6 to `run_one.sh`.
   - `test_context_from_corpus_when_row_lacks_it`: the W4 `sample.jsonl` rows predate ticket 01 and carry no `preceding_turns`, so the runner looks them up by `_hash` in `~/.claude/sir-albert-corpus/corpus.jsonl` (with a `W4_CORPUS_FILE` override for tests). Coordinator review of 01, 2026-09-27.
   - `test_legacy_positional_unchanged`: `run_tranche.py RUNDIR SAMPLE 2` still schedules W4 tranche 2 exactly.
2. Run: `/usr/local/bin/python3.13 -m pytest -q plugins/sir-albert/tests/eval/test_run_tranche.py`. Expected: new FAIL.
3. Implement in `plugins/sir-albert/tools/eval/run_tranche.py`: argparse with the legacy positional form kept, plus `--arms` (default `a,b`), `--rows all|1|2`, `--reps` (default 2), and `--expected N`. Write the context files to `docs/plans/2026-09-27-w5-outperform/context/<hash>.json` (gitignored).
4. Run the step 2 command again. Expected: PASS. Suite green.
5. Write `plugins/sir-albert/tools/eval/dev_report.py` with a test `test_dev_report_real_schema`. The fixture sample uses `_hash` (the real `sample.jsonl` key; this is the W4 `aee9250` lesson). Output: per slice, hit counts and fire counts. Prints `DEV PASS` or `DEV FAIL` against the bar.
6. Round N (~$3 per round, AUTO, total cap $15). Re-pin the clone at the current HEAD: `W4_RUNDIR=~/.claude/sir-albert-w5-dev-rN bash plugins/sir-albert/tools/eval/build_arms.sh` → `canary_preflight.sh` → `W4_BUDGET_USD=5 run_tranche.py ~/.claude/sir-albert-w5-dev-rN docs/plans/2026-09-26-w4-eval/sample.jsonl --arms b --rows all --reps 1` into `W4_ARTIFACT_DIR=docs/plans/2026-09-27-w5-outperform/runs-dev/rN`. Then `grep '"model"' ~/.claude/settings.json`.
7. `dev_report.py runs-dev/rN`. Append counts only (no text) to `docs/plans/2026-09-27-w5-outperform/11-dev-log.md`, one row per round: SHA, happy, silent, control fires, and cost.
8. On `DEV FAIL`: diagnose each miss from its artifact, make one change in the relevant ticket's files (06/07/08/09/10 rules apply, including create-skill for any SKILL.md), commit, and go to step 6. Stop after round 2 and report to Gal (Amendment 2). Don't widen the P3 gates.
9. Commit the tooling and dev log: `git commit -m "feat(w5): B-only dev loop runner + report"`

## Definition of Done
- [ ] `DEV PASS` in ≤ 2 rounds, or a stop-and-report to Gal with per-miss diagnosis
- [ ] Legacy W4 invocation unchanged (test)
- [ ] Dev spend ≤ $15, logged per round

⚠️ Risk: these 15 prompts are now tuned-on. A dev pass is necessary, not sufficient; only P3 counts.

# 12 — freeze-and-run-p3

**Blocked by:** 05, 11

## Goal
90 valid P3 rep-1 runs (30 held-out prompts × 3 arms B/A/S), plus 90 rep-2 runs only if spec Amendment 2 fires, on Sonnet 5, against a frozen and tagged sir_albert SHA, interleaved per prompt and rep.

## Steps
1. Write the failing tests:
   - `plugins/sir-albert/tests/eval/test_arm_builder.py::test_arm_s_settings`: `build_arms.sh` writes `arm-s-settings.json` (superpowers true) and `run-manifest.json` has `arm_s_settings`.
   - `plugins/sir-albert/tests/eval/test_run_executor.py::test_arm_s_has_no_plugin_dir`: for arm `s`, the stub argv has no `--plugin-dir`. For `a`/`b` it does.
   - `plugins/sir-albert/tests/eval/test_canary.py::test_canary_arm_s`: the canary asserts S loads superpowers skills and 0 `sir-albert:` skills.
2. Run those 3 tests. Expected: FAIL.
3. Implement in `build_arms.sh` (arm S settings plus manifest key), `run_one.sh` (arm `s` → `arm_s_settings`, no `--plugin-dir`), and `canary_preflight.sh` (a third canary, `canary-s.jsonl`). Also `run_tranche.py`: `--arms b,a,s` interleaves `b a s` per prompt and rep, and the precondition loop checks canaries for the requested arms only.
4. Run the tests again. Expected: PASS. Full suite green.
5. Freeze: `git tag w5-freeze` (local only, never pushed). Build with `W4_RUNDIR=~/.claude/sir-albert-w5-p3 bash plugins/sir-albert/tools/eval/build_arms.sh`, then check that `run-manifest.json` `pin_sha` equals `git rev-parse w5-freeze`.
6. `canary_preflight.sh ~/.claude/sir-albert-w5-p3`: 3 arms PASS on `claude-sonnet-5`. Then `grep '"model"' ~/.claude/settings.json`.
7. **CHECKPOINT: Gal's explicit yes** for rep 1: 90 runs (~$17 expected; runner budget cap $30).
8. Run in the background, lid open, no new Claude sessions: `W4_BUDGET_USD=30 W4_PARALLEL=4 W4_ARTIFACT_DIR=docs/plans/2026-09-27-w5-outperform/runs-p3 /usr/local/bin/python3.13 plugins/sir-albert/tools/eval/run_tranche.py ~/.claude/sir-albert-w5-p3 docs/plans/2026-09-27-w5-outperform/sample-p3.jsonl --arms b,a,s --rows all --reps 1 --expected 90` (rep 1). Then run the judge and verdict on rep 1 (ticket 13). **Only if spec Amendment 2's rep-2 rule fires**, re-run with `--reps 2 --expected 180`: the runner skips existing rep-1 artifacts. Needs a separate Gal yes (~$17).
9. Audit (`/tmp/w4-audit.py` generalized to 3 arms and saved as `plugins/sir-albert/tools/eval/audit_runs.py`, with a test on a real-schema fixture). Expected after rep 1: 90 artifacts, 30 per arm, 30 complete (prompt, rep) triples (after rep 2: 180 / 60 / 60), 0 infra errors (ticket 03 definition), 0 empty, all `claude-sonnet-5`, and cut-offs reported per arm.
10. Check the clone is untouched: `git -C <clone> status --porcelain` is empty and `rev-parse` equals `w5-freeze`.

## Definition of Done
- [ ] 90/90 valid (or 180/180 if rep 2 ran), complete triples, audit script committed with test
- [ ] Frozen SHA verified in the manifest and the clone
- [ ] Gal's default model intact

## CHECKPOINT
Step 7: live spend of ~$33 (cap $60). Needs Gal's explicit yes for this action. Plan approval doesn't cover it.

## Status — DEFERRED (Gal, 2026-09-27)
P3 skipped: uninstalling superpowers is reversible (one `enabledPlugins` toggle), so a real-use trial replaces the headless eval. Tooling is ready and frozen at tag `w5-freeze` (`bde3566`). Ticket 12 steps 1–6 are done (arm S, audit_runs, 3/3 canaries PASS in `~/.claude/sir-albert-w5-p3`). Resume at step 7 if a citable result is ever needed.

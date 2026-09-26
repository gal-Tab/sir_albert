# 14 — t2-discipline-skills

**Blocked by:** 03, 13
**Spec:** `docs/specs/2026-09-26-w4-eval.md §P3 — T2 for the 5 discipline skills`

## Goal
Write T2 (tier-2 real-agent) scenarios for the 5 discipline skills — brainstorm, execute, debug, plan, build — drawn from the prompt corpus, with scenarios weighted toward the routes P1 identified as weak. Real agent calls only: one artifact per rep, run count auditable from the filesystem.

## Steps

1. Read `docs/plans/2026-09-26-w4-eval/p1-scorecard-2026-09-26.md` and note the ranked fix list — specifically which routes have the most FPs. Use this to weight scenario selection toward the weaker routes (do not write T2 scenarios only for the strong ones).

2. Write `plugins/sir-albert/tools/eval/select_t2_scenarios.py`:
   - For each of the 5 discipline skills (brainstorm, execute, debug, plan, build), query `corpus.jsonl` for the 3 most representative task-initiating prompts (using `is_organic`, `preceding_turns == []`, skill label matches)
   - Emit `docs/plans/2026-09-26-w4-eval/t2-scenarios.jsonl` — 15 rows max (3 per skill), each with `skill`, `prompt_hash`, `prompt_text`, `scenario_desc`
   - Print: `t2-scenarios: brainstorm=N execute=N debug=N plan=N build=N`

3. Run: `/usr/local/bin/python3.13 plugins/sir-albert/tools/eval/select_t2_scenarios.py` — Expected: `t2-scenarios.jsonl` created, all 5 skills have ≥ 1 scenario

4. Write `plugins/sir-albert/tools/eval/run_t2.sh`:
   - Args: `$1=RUNDIR`, `$2=T2_SCENARIOS_FILE`, `$3=K` (reps per scenario, default 2)
   - For each scenario, for each rep: call `run_one.sh` with arm B (sir_albert, the thing under test)
   - Artifact naming: `t2-<skill>-<prompt_hash>-rep<k>.json` (separate namespace from P2 runs — do NOT mix with `runs/`)
   - Output dir: `docs/plans/2026-09-26-w4-eval/t2-runs/`
   - After all runs: `ls t2-runs/*.json | wc -l` must equal `n_scenarios × K`; script prints this count
   - **No summarizing, no batching, no role-playing reps.** Every scenario must produce exactly one artifact file via a real `command claude` call. If an artifact file is absent, the run did not happen.

5. Write `plugins/sir-albert/tools/eval/t2_report.py`:
   - Reads `t2-runs/` artifacts
   - For each scenario: reports `skill`, `prompt_text[:80]`, `skills_called`, `cost_usd`, `turn_count`
   - Highlights: any scenario where `skills_called` is empty (no skill fired for a discipline-skill prompt = a routing failure)
   - Writes `docs/plans/2026-09-26-w4-eval/t2-report-<date>.md`

6. Dry-run check: `bash -n plugins/sir-albert/tools/eval/run_t2.sh` — Expected: no syntax errors

7. Note on execution: `run_t2.sh` makes real API calls and must not run without Gal's explicit yes. The go-ahead for T2 is separate from tranche 1/2 approval. Add a `## CHECKPOINT` to `run_t2.sh` as a comment:
   ```
   # CHECKPOINT: run_t2.sh makes real API calls.
   # Expected: n_scenarios * K runs. Do NOT run without Gal's explicit yes.
   ```

## Definition of Done
- [ ] `select_t2_scenarios.py` emits `t2-scenarios.jsonl` covering all 5 discipline skills
- [ ] Scenarios weighted toward routes with highest FP count per P1 scorecard
- [ ] `run_t2.sh` writes one artifact per rep to `t2-runs/` (separate dir from `runs/`)
- [ ] Artifact count auditable: `ls t2-runs/ | wc -l == n_scenarios × K`
- [ ] `t2_report.py` highlights empty `skills_called` (routing failures)
- [ ] CHECKPOINT comment in `run_t2.sh`; T2 execution requires its own explicit Gal go-ahead
- [ ] No synthetic or role-played reps — each artifact maps to one real `command claude` invocation

⚠️ Risk: editing `plugins/sir-albert/tools/eval/` scripts is immediately live in every new session (the `--plugin-dir` alias loads the whole `plugins/` directory). T2 scripts should only be invoked explicitly, not triggered by any hook.

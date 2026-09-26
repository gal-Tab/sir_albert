# 11 — tranche-1-pilot

**Blocked by:** 03, 07, 10
**Spec:** `docs/specs/2026-09-26-w4-eval.md §P2 — Thin A/B replay / Budget cap`

## Goal
Execute tranche 1: 10 prompts × 2 arms × k=2 = 40 runs using `run_one.sh`. Requires Gal's explicit yes before starting. Captures `axcli usage` delta before/after. Aborts if the first 10 runs extrapolate past $40 for the full 60.

## Steps

1. Verify prerequisites before asking for Gal's go-ahead:
   - Run: `/usr/local/bin/python3.13 plugins/sir-albert/tools/prompt_corpus.py validate-labels` — Expected: exits 0, all rows labelled
   - Run: `/usr/local/bin/python3.13 plugins/sir-albert/tools/prompt_corpus.py p1-score` — Expected: exits 0 (P1 gate PASS)
   - Confirm `docs/plans/2026-09-26-w4-eval/sample.jsonl` exists and has 15 rows: `wc -l docs/plans/2026-09-26-w4-eval/sample.jsonl`
   - Confirm `$RUNDIR/run-manifest.json` exists (arms built via ticket 05): `cat $RUNDIR/run-manifest.json | python3 -m json.tool`
   - Confirm canary passed (ticket 06): `bash plugins/sir-albert/tools/eval/canary_preflight.sh $RUNDIR` — Expected: `Canary PASS`
   - Report all prerequisite results to Gal

2. Write `plugins/sir-albert/tools/eval/run_tranche.sh`:
   - Args: `$1=RUNDIR`, `$2=SAMPLE_FILE`, `$3=TRANCHE` (1 or 2)
   - Tranche 1: first 10 rows of `sample.jsonl`; tranche 2: rows 11-15
   - At start: assert model in `$RUNDIR/model-snapshot.txt` == `claude-opus-5-5[1m]`; abort if not
   - `BUDGET_BEFORE=$(axcli usage | python3 -c "import sys; lines=sys.stdin.read(); ..." )` — capture cost snapshot
   - Loop: for each prompt row, for each arm (a, b), for each rep (1, 2) — **sequential, no backgrounding**:
     - `bash plugins/sir-albert/tools/eval/run_one.sh "$ARM" "$HASH" "$REP" "$PROMPT_TEXT" "$RUNDIR"`
     - Each call to run_one.sh is already wrapped in guarded.sh internally
   - After first 10 runs: sum `cost_usd` from artifacts; extrapolated total = `FIRST_10_COST / 10 * 60`
   - If extrapolated total > $40: `echo "ABORT: first 10 runs cost $X, extrapolates to $Y for 60 — stopping"; exit 2`
   - Print artifact count after each prompt: `ls $ARTIFACT_DIR/*.json | wc -l`
   - `BUDGET_AFTER=$(axcli usage ...)` — print delta

3. Dry-run syntax check: `bash -n plugins/sir-albert/tools/eval/run_tranche.sh` — Expected: no errors

4. Write `docs/plans/2026-09-26-w4-eval/RUNLOG.md` stub that will be updated during the run:
   - Columns: run index, prompt_hash, arm, rep, cost_usd, exit_code, skills_called
   - Initially empty table

## CHECKPOINT — STOP HERE. Do not proceed past step 4 without Gal's explicit yes for THIS action.

State clearly when asking:
- Number of API calls: **40 runs** (10 prompts × 2 arms × k=2), strictly sequential (each wrapped in `guarded.sh`)
- Per-run budget ceiling: **$0.60** (`--max-budget-usd 0.60` in `run_one.sh`)
- Model: asserted == `claude-opus-5-5[1m]` at harness start; aborts if different
- Expected total: $5–$20 based on probe calibration ($0.094–$0.141 per run × 40); **hard stop if extrapolation > $40**
- Artifact files will be created at: `docs/plans/2026-09-26-w4-eval/runs/`
- Model: read from `$RUNDIR/model-snapshot.txt` (the model in `~/.claude/settings.json` at arm-build time)
- `~/.claude/settings.json` is NOT modified (protected by `--setting-sources project,local`)

5. [AFTER Gal's yes] Record `axcli usage` BEFORE:
   Run: `axcli usage` — copy and save the current cost line to `docs/plans/2026-09-26-w4-eval/RUNLOG.md`

6. [AFTER Gal's yes] Execute tranche 1:
   Run: `bash plugins/sir-albert/tools/eval/run_tranche.sh $RUNDIR docs/plans/2026-09-26-w4-eval/sample.jsonl 1`
   Expected: 40 artifact files created, no ABORT message, exit 0

7. [AFTER Gal's yes] Abort check: `ls docs/plans/2026-09-26-w4-eval/runs/*.json | wc -l` — Expected: 40

8. [AFTER Gal's yes] Record `axcli usage` AFTER and report delta to Gal.

## Definition of Done
- [ ] All prerequisites verified before asking Gal
- [ ] Explicit Gal go-ahead obtained and documented
- [ ] 40 run artifacts in `docs/plans/2026-09-26-w4-eval/runs/` confirmed by `ls | wc -l`
- [ ] `axcli usage` delta captured and reported to Gal
- [ ] Extrapolation check passed (first 10 runs do not project > $40 for 60)
- [ ] `RUNLOG.md` updated with run results

## Review corrections (binding, supersede the steps above and the CHECKPOINT text where they conflict)

1. **The CHECKPOINT text must be accurate.** Replace two claims:
   - ~~"`~/.claude/settings.json` is NOT modified (protected by `--setting-sources`)"~~ is **false** (see `04-probe-results.md`). Say instead: *"axcli rewrites the default model on every spawn. `guarded.sh` restores it after each run. **Don't open new Claude sessions while the tranche runs**, or they start on Sonnet."*
   - ~~"Expected total $5–$20 based on probe calibration"~~ is **unsupported**. The probe prompt was 1-turn "reply ok", and real runs go up to 12 turns. Say instead: *"Cost per real run is unknown. **Worst case $24** (40 × $0.60 per-run cap). An abort triggers if the first 10 runs extrapolate past $40 for all 60."*
2. **Interleave arms per rep**: order runs as `a/rep1, b/rep1, a/rep2, b/rep2` per prompt, not `a,a,b,b`. That way time drift and cache warmth fall evenly on both arms.
3. **Run artifacts are NOT committed.** `runs/` goes in `.gitignore`. Artifacts contain replayed prompt text and model responses drawn from Gal's work in other repos, including internal monday.com content. Commit only the verdict report, `RUNLOG.md` (hashes, costs, exit codes, no text) and the `ls | wc -l` evidence.
4. The model assertion reads the expected value from the spec decision (`claude-opus-5-5[1m]`), and the restore target is `model-snapshot.txt`. Both must agree at start, or the run aborts.

# 12 — tranche-2

**Blocked by:** 11
**Spec:** `docs/specs/2026-09-26-w4-eval.md §P2 — Thin A/B replay / Budget cap`

## Goal
Execute tranche 2: the remaining 5 prompts (rows 11-15 of `sample.jsonl`), 20 runs, only if tranche 1's measured cost leaves the $40 total inside the hard cap.

## Steps

1. Verify tranche 1 cost is within cap:
   - Read `axcli usage` delta from `RUNLOG.md`
   - Compute headroom: `$40 - tranche_1_actual_cost`
   - If tranche 1 cost already exceeds $25 (= more than $15 left for 20 more runs at a potentially higher-than-pilot rate): report to Gal and ask for confirmation before proceeding
   - Run: `ls docs/plans/2026-09-26-w4-eval/runs/*.json | wc -l` — Expected: 40

2. Verify artifact integrity before tranche 2:
   - Run: `/usr/local/bin/python3.13 -c "import json,glob; artifacts=[json.load(open(f)) for f in glob.glob('docs/plans/2026-09-26-w4-eval/runs/*.json')]; bad=[a for a in artifacts if a.get('exit_code') is None]; print(f'{len(bad)} malformed artifacts')"` — Expected: 0 malformed

## CHECKPOINT — STOP HERE. Do not run tranche 2 without confirming:
- Tranche 1 actual cost is reported (from RUNLOG.md delta)
- Projected total for all 60 runs is within $40
- Gal's explicit yes for THIS tranche specifically (not inherited from tranche 1 approval)

3. [AFTER cost confirmation and Gal's explicit yes] Execute tranche 2 (strictly sequential, each run wrapped in guarded.sh):
   Run: `bash plugins/sir-albert/tools/eval/run_tranche.sh $RUNDIR docs/plans/2026-09-26-w4-eval/sample.jsonl 2`
   Expected: 20 more artifact files created, exit 0

4. [AFTER tranche 2] Verify final run count:
   Run: `ls docs/plans/2026-09-26-w4-eval/runs/*.json | wc -l` — Expected: **60**

5. [AFTER tranche 2] Record `axcli usage` AFTER and update `RUNLOG.md` with tranche 2 delta and running total.

6. Sanity check artifact uniqueness:
   Run: `/usr/local/bin/python3.13 -c "import json,glob; names=[f.split('/')[-1] for f in glob.glob('docs/plans/2026-09-26-w4-eval/runs/*.json')]; assert len(names)==len(set(names)), 'duplicate artifact names'; print('all 60 unique')"` — Expected: `all 60 unique`

## Definition of Done
- [ ] Cost verification passed: tranche 1 actual + tranche 2 projected ≤ $40
- [ ] Gal's explicit yes obtained for tranche 2 specifically
- [ ] 60 total artifact files in `docs/plans/2026-09-26-w4-eval/runs/` (`ls | wc -l == 60`)
- [ ] All 60 artifact names are unique (no collision)
- [ ] `RUNLOG.md` updated with tranche 2 delta and total cost

## Review corrections (binding)

Every correction in ticket 11 applies here too: the accurate CHECKPOINT text (settings *are* rewritten per spawn; worst case 20 × $0.60 = $12), per-rep arm interleaving, and `runs/` never committed.

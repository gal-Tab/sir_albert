# T2 eval run — plan alias discoverability
**Date:** 2026-09-27 | **Ticket:** w5/aliases | **Type:** T2 discoverability

## Summary

Tested legacy alias triggers added to plan description (`"html plan"`, `"html-plans"`, `"share-plan"`) against the old description (baseline). Both arms 9/9 — the model already routes these prompts to `sir-albert:plan` without explicit alias triggers. Aliases are retained as documentation and regression insurance.

## Scenarios (3 new, appended to evals.json)

| id | type | baseline | candidate |
|---|---|---|---|
| plan-alias-pos-html-plan | positive | 3/3 | 3/3 |
| plan-alias-pos-share-plan | positive | 3/3 | 3/3 |
| plan-alias-neg-share-slack | red-team | 3/3 | 3/3 |

Deterministic check: `sir-albert:plan in skills_called` (positive) / `sir-albert:plan NOT in skills_called` (negative).

Negative scenario (`plan-alias-neg-share-slack`) routes to `sir-albert:slack-in-my-voice` in all 6 reps — no false positive on either arm.

## Commands run

```
# build arms
bash plugins/sir-albert/tools/eval/build_arms.sh

# baseline (arm a) — clone had OLD description at HEAD
W4_ARTIFACT_DIR=.../t2-alias-runs bash guarded.sh bash run_one.sh a <hash> <rep> <prompt> <RUNDIR>   # x9

# updated clone SKILL.md, committed, ran candidate (arm b)
W4_ARTIFACT_DIR=.../t2-alias-runs bash guarded.sh bash run_one.sh b <hash> <rep> <prompt> <RUNDIR>   # x9
```

Artifacts: `docs/plans/2026-09-26-w4-eval/t2-alias-runs/` — 18 files (9 arm-a, 9 arm-b).

## Score.py result (iter 1)

```
baseline score: 1.00
  iter 0: score=1.00 lift=+0.00 se=0.000 plateau=False borderline=[] weak=[] low_agreement=[]
stop: budget
```

Ceiling effect — both arms at 1.00. Lift = 0.00. Budget cap reached (1 iteration, max 2 per ticket).

## Finding

The model routes `html plan` / `share-plan` prompts to `sir-albert:plan` even without explicit alias text in the description. The alias additions to the description are a documentation hardening — they prevent future description-pruning from silently breaking these routes.

## Model check

Before: `"model": "claude-opus-5-5[1m]"` ✓  
After: `"model": "claude-opus-5-5[1m]"` ✓

## Files changed

- `plugins/sir-albert/skills/core/plan/SKILL.md` — appended `"html plan"`, `"html-plans"`, `"share-plan"` to Triggers list
- `plugins/sir-albert/skills/core/plan/evals/evals.json` — appended 3 scenarios (IDs above)
- `plugins/sir-albert/skills/core/plan/evals/run-t2-2026-09-27-aliases.md` — this file

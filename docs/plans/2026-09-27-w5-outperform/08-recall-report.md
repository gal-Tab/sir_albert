# 08 — Router Recall Report (W5)

## New patterns added

| Order | Intent | Pattern |
|---|---|---|
| 55 | brainstorm | `\bhelp me (see\|understand) what.{0,15}going on\b\|\blook at this (situation\|context) and (advise\|help) me\b` |
| 62 | plan | `\bplan (it\|this) (out\|first)\b\|\bbreak (this\|it) into steps\b` |
| 92 | build | `\bopen (a\|the) pr\b\|\bpush (this \|the )?(feature\|change\|branch\|code)\b` |

## Corpus blast radius (n=1,938 organic rows)

| Route | New corpus fires | Eyeballed (n) | Wrong fires |
|---|---|---|---|
| brainstorm-context-explore (order 55) | 0 | 0 | 0 |
| plan-imperative (order 62) | 2 | 2 | 0 |
| build-open-pr (order 92) | 9 | 9 | 0 |

All sampled fires were correct matches (matched spans: "plan it first", "open a pr", "open a PR", "open the PR", "Push the branch").

## P1 results

| Metric | Before | After |
|---|---|---|
| Precision | 95.2% (n=21) | 95.2% (n=21) |
| False-fire | 0.0% (n=8) | 0.0% (n=8) |
| Miss rate (diagnostic) | 57.1% | 57.1% |

Note: miss rate is label-derived (static); it measures prevalence of routable prompts in the task_initiating slice, not re-routing. New patterns do not change this value in the current p1-score implementation.

## Coordinator re-measure (2026-09-27)

`p1-score` precision reads the `predicted_route` stored at labelling time, and its miss rate is label-only. Only false-fire re-runs the router. So P1 **cannot** see router changes except through false fires. Re-running the actual router over the 50 labelled rows (ambiguous excluded):

| Router | Correct fires | Wrong route | Fires on `none` | Task prompts missed |
|---|---|---|---|---|
| baseline 1b88127 | 20 | 0 | 1 | 9/29 |
| ticket 08 | 20 | 0 | 1 | 9/29 |

The new patterns recover 0 of the 9 labelled misses and cost nothing in precision. The gains are corpus-only: `build` is revived (9 fires, all eyeballed correct) and plan gains 2. Conclusion: regex recall is close to exhausted on this data. G2 (router-silent) depends on model-side routing (07 contract, 09 descriptions), and ticket 11's dev loop is the real measure.

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

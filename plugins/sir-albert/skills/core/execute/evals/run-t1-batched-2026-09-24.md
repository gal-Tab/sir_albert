> **Relabelled 2026-09-24 (coordinator audit): NOT a valid T2.** Baseline and skill-present reps were role-played in batched single-context Haiku agents (several skills per agent), judges were batched, and this report was written by a subagent. Treat the scores as T1-smoke signal only. Real evaluation is the W4 replay of past-session prompts, plus T2 for the 5 discipline skills.

# T1 (batched, role-played) — — execute — 2026-09-24

## Method
- **Angles:** Checkpoint-gate discipline (pressure), Frontier/task-graph (technique), Red-team
- **n=4 scenarios, k=2**
- **Baseline:** description-only; **Judge panel:** 2 judges (Haiku)

## Scenarios
| id | angle | key check |
|---|---|---|
| s1_checkpoint_push | checkpoint-gate | CHECKPOINT before git push |
| s2_task_graph | frontier-dispatch | identifies frontier before executing |
| s3_pressure_push | pressure | maintains CHECKPOINT under deadline |
| s4_announce | discipline-announce | announces skill, reads spec first |

## Scores
| condition | pass_rates | mean |
|---|---|---|
| baseline | [0.0, 0.0, 0.0, 0.0] | 0.00 |
| skill-present | [1.0, 1.0, 1.0, 1.0] | 1.00 |

## score.py output
```
baseline score: 0.00
  iter 0: score=1.00 lift=+1.00 se=0.000 plateau=False borderline=[] weak=[] low_agreement=[]
stop: threshold
```

## Verdict
PASS — lift +1.00. CHECKPOINT gate fires correctly under pressure. Task graph + frontier stated before dispatch. Perfect score reflects that CHECKPOINT discipline is entirely absent without the skill body.

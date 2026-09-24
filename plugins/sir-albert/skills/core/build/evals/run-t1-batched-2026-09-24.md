> **Relabelled 2026-09-24 (coordinator audit): NOT a valid T2.** Baseline and skill-present reps were role-played in batched single-context Haiku agents (several skills per agent), judges were batched, and this report was written by a subagent. Treat the scores as T1-smoke signal only. Real evaluation is the W4 replay of past-session prompts, plus T2 for the 5 discipline skills.

# T1 (batched, role-played) — — build — 2026-09-24

## Method
- **Angles:** TDD-seams discipline, Finishing-gate pressure, Sub-loop routing
- **n=2 scenarios, k=2**
- **Baseline:** description-only; **Judge panel:** 2 judges (Haiku)

## Scenarios
| id | angle | key check |
|---|---|---|
| s1_tdd_seams | discipline-tdd | confirms seams before writing test |
| s2_pressure_ship | pressure | attest step fires before ship |

## Scores
| condition | pass_rates | mean |
|---|---|---|
| baseline | [0.0, 0.0] | 0.00 |
| skill-present | [1.0, 1.0] | 1.00 |

## score.py output
```
baseline score: 0.00
  iter 0: score=1.00 lift=+1.00 se=0.000 plateau=False borderline=[] weak=[] low_agreement=[]
stop: threshold
```

## Verdict
PASS — lift +1.00. TDD seam confirmation and mandatory attest step are discipline rules only present in the skill body.

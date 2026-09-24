> **Relabelled 2026-09-24 (coordinator audit): NOT a valid T2.** Baseline and skill-present reps were role-played in batched single-context Haiku agents (several skills per agent), judges were batched, and this report was written by a subagent. Treat the scores as T1-smoke signal only. Real evaluation is the W4 replay of past-session prompts, plus T2 for the 5 discipline skills.

# T1 (batched, role-played) — — gtm-gate — 2026-09-24

## Method
- **Angles:** Param-audit discipline, MIS-NAMED detection, Trigger recognition
- **n=2 scenarios, k=2**
- **Baseline:** description-only; **Judge panel:** 2 judges (Haiku)

## Scenarios
| id | angle | key check |
|---|---|---|
| s1_param_audit | param-audit-trigger | checks all 4 required params |
| s2_mis_named_desktop | discipline-detection | monday_is_desktop → MIS-NAMED |

## Scores
| condition | pass_rates | mean |
|---|---|---|
| baseline | [0.5, 0.0] | 0.25 |
| skill-present | [1.0, 1.0] | 1.00 |

## score.py output
```
baseline score: 0.25
  iter 0: score=1.00 lift=+0.75 se=0.000 plateau=False borderline=[] weak=[] low_agreement=[]
stop: threshold
```

## Verdict
PASS — lift +0.75. The MIS-NAMED distinction (not duplicate, wrong name) is 0.0 baseline → 1.0 with skill. Param audit partially covered by description, fully enforced by skill body.

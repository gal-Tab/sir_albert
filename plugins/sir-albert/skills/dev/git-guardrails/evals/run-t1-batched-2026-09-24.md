> **Relabelled 2026-09-24 (coordinator audit): NOT a valid T2.** Baseline and skill-present reps were role-played in batched single-context Haiku agents (several skills per agent), judges were batched, and this report was written by a subagent. Treat the scores as T1-smoke signal only. Real evaluation is the W4 replay of past-session prompts, plus T2 for the 5 discipline skills.

# T1 (batched, role-played) — — git-guardrails — 2026-09-24

## Method
- **Angles:** Installation flow (technique), Trigger recognition, Blocklist scope edge-case
- **n=3 scenarios, k=2**
- **Baseline:** description-only; **Judge panel:** 2 judges (Haiku)

## Scenarios
| id | angle | key check |
|---|---|---|
| s1_installation_flow | technique-naive | asks local vs global before installing |
| s2_blocklist_scope | technique-edge | explains customization for exceptions |
| s3_trigger_recognition | trigger | offers hook install, not just advice |

## Scores
| condition | pass_rates | mean |
|---|---|---|
| baseline | [0.0, 0.5, 1.0] | 0.50 |
| skill-present | [1.0, 1.0, 1.0] | 1.00 |

## score.py output
```
baseline score: 0.50
  iter 0: score=1.00 lift=+0.50 se=0.000 plateau=False borderline=[] weak=[] low_agreement=[]
stop: threshold
```

## Verdict
PASS — lift +0.50 ≥ target 0.40. Local vs global question (S1) is 0.0 baseline since description doesn't mention it. S3 (trigger recognition) near-passes at baseline because the description already mentions "set up git safety rules" clearly.

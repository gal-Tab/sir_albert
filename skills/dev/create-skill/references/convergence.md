# Convergence — create-skill

<!-- verified 2026-09-10: T1 smoke passed — baseline 0.17 → lift +0.83 → stop: threshold; toy skill (echo-fact) validates exit=0 -->


## Scoring math (§5.2–5.3)

Run each scenario k times against a **fresh** agent with the candidate skill in context.

```
score  = mean over scenarios of (passes / k)        ∈ [0, 1]
SE     = sqrt(p · (1 − p) / (n · k))               # n = number of scenarios
lift   = score_candidate − score_baseline
```

- **Baseline (RED):** score with the skill *absent* / description-only. If baseline already passes, nothing to fix — stop.
- **Progress = lift over baseline**, not absolute score. Shared judge bias largely cancels in the delta (see §8).
- A change within ~1–2 SE is noise; do not act on it.

---

## Stop rules

Stop iterating when **any** of these is true:

| Rule | Condition |
|---|---|
| **Threshold** | lift ≥ target AND cross-scenario variance is low |
| **Plateau** | Δ < noise band (1–2 SE) for 2 straight iterations → change tactics, do not add reps |
| **Budget cap** | Token/time budget exhausted |

Plateau is the core fix over `superpowers:writing-skills`'s unbounded "5+ reps." Hitting a plateau means the current approach is stuck — the next action is to change the angle or rewrite a failing scenario, not repeat.

**Per-scenario diagnostics** point the next edit at failing scenarios. No blind rewrites.

---

## Delta-scoring rationale

Measuring lift rather than absolute score is deliberate:

- Same-model judges share blind spots; their bias is roughly constant across baseline and candidate runs.
- Subtracting baseline cancels most of that shared bias, leaving a signal that reflects the skill's marginal contribution.
- This does not eliminate all bias (see mitigations below), but it substantially reduces optimism inflation.

---

## Bias mitigations (§8)

Correlated-judge bias is managed, not eliminated. Six design controls:

| # | Mitigation | What it does |
|---|---|---|
| 1 | **Deterministic-first scoring** | Each scenario declares a machine-checkable pass condition where one exists; LLM judgment only for irreducibly subjective criteria. Shrinks the surface exposed to LLM bias. |
| 2 | **Delta-scoring** | Measure lift over baseline; shared bias largely cancels (see above). |
| 3 | **Angle + optional model diversity** | Type-diverse author angles decorrelate errors; some judges optionally run on a different model. |
| 4 | **Held-out red-team author** | Constructs a case that passes judges but violates intent. Success ⇒ eval is gamed ⇒ strengthen scenarios before continuing. |
| 5 | **Disagreement health gate** | Easy consensus on a borderline score → surface to human. Scattered judges → fix the rubric. |
| 6 | **Human at the boundary + dogfood** | Human review only for flagged cases (inline during the run, not an end report). Self-hosting (`create-skill` authoring itself) is ground truth. |

Residual exposure is limited to purely-subjective skills with no deterministic anchors; covered by boundary-review (mitigation 6).

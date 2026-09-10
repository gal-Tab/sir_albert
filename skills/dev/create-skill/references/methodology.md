# Methodology — create-skill

## The superpowers challenge (§2)

`superpowers:writing-skills` is strong on discipline-skill psychology (SDO thinking, rationalization tables, anti-narrative). `create-skill` keeps that — cited, not duplicated — and fixes six load-bearing weaknesses:

| # | superpowers weakness | create-skill fix |
|---|---|---|
| 1 | **Iron Law overclaims + self-contradicts** — mandates failing-test-first for *every* skill/edit, then admits reference skills need retrieval tests and mechanical rules should be automated | Loop is **tiered** and reserved for skills that earn it; structural rules are **automated** (validator), not documented |
| 2 | **Contradicts the spec it cites** — "description = when, NOT what; never summarize" vs spec's "describes what it does **and** when" | Reconciled rule: **triggers-first + one 'what' clause, never step-by-step narration** — tested empirically by the discoverability agent, not asserted |
| 3 | **Mixes opinion into "the spec"** — e.g. "description < 500 chars" (spec allows 1024) | Spec is **authoritative** for MUST; opinions are labeled SHOULD |
| 4 | **No machine validation** — ends in a manual checklist an agent can misjudge | **Terminates in `validate-skill.py`** (deterministic floor) |
| 5 | **No ROI gate on the expensive loop** — "5+ reps" with no when-worth-it | **Tier gate** decides whether to invest in a scored benchmark at all |
| 6 | **Violates its own token/naming guidance** (~500+ lines, Claude-centric) | Lean SKILL.md; heavy content in `references/`; portable spec output |

For discipline-skill psychology (SDO, rationalization tables, red-flags, "match the form to the failure," anti-narrative): read **`superpowers:writing-skills`** directly. This skill does not duplicate it.

---

## Description rule (reconciled)

The agentskills.io spec says a description "describes what it does **and** when." `superpowers:writing-skills` says "when, NOT what; never summarize." These conflict; `create-skill` reconciles them:

**Rule:** lead with triggering conditions ("Use when …"), plus at most one short clause of *what* it does. Never narrate the workflow step-by-step.

This rule is tested empirically by the discoverability agent (give it only the description + a pile of task prompts, measure selection precision/recall) — not enforced by fiat.

---

## Rigor tiers (§6)

The benchmark loop is expensive. Tiers gate how much of it to run:

| Tier | What runs | For |
|---|---|---|
| **T0 Structural** | scaffold + `validate-skill.py` | trivial / one-off reference skills |
| **T1 Smoke** | + single-angle, few-rep scored run | most technique skills |
| **T2 Full panel loop** | dynamic multi-angle + convergence + `evals/` committed | discipline / shared / high-value skills |

The loop is central to all tiers; the tier only decides how much of it to run.

**T2 commitment:** evals are committed for T2/discipline skills; throwaway for T1. k = 3 reps per scenario.

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

For discipline-skill psychology (SDO, rationalization tables, red-flags, "match the form to the failure," anti-narrative): the key rules are **inlined in `SKILL.md §SDO rules`**. This is the authoritative copy; no external skill load required.

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

---

## Council / multi-voice skills

Skills that run several named personas against the same input (councils, boards, critic
panels) get their own scaffolding shape, distinct from the discipline/technique/reference
rigor tiers above:

- **One file per persona** in `agents/<persona>.md` — character profile only (background,
  core belief, signature moves), ending in a `{{placeholder}}` dispatch block. This mirrors
  how `create-skill` already dispatches its own `agents/judge.md` and
  `agents/author-{discipline,technique,reference}.md`: each is a self-contained prompt filled
  in at call time, not a shared include.
- **The orchestrator SKILL.md does everything cross-cutting**: persona selection, building
  each dispatch prompt, sending all selected personas as parallel, independent Agent-tool
  calls (fresh subagent per persona, blind to the others), and labeling the returned
  responses. This keeps personas swappable and addable without touching orchestration logic.
- **Cross-persona behavior (tone, mode, output shape) is a placeholder, not a copy-paste.**
  If every persona needs the same instruction (e.g. "respond in 2–4 sentences," or a mode
  switch like explore/sharpen/attack), define it once in the orchestrator and fill it into
  each persona file's placeholder at dispatch time — don't restate it in all N persona files.
- Independent parallel dispatch (personas blind to each other) is the default — it avoids one
  persona anchoring on another's framing. Only make personas visible to each other
  (sequential dispatch) if the skill's value is explicitly the cross-talk.

Worked example: `skills/biz/discovery-lens/` (8 personas, mode-driven dispatch).

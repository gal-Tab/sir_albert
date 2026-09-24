# create-skill — Design Spec

**Date:** 2026-09-09
**Status:** Design — pending approval → implementation plan
**Home:** `skills/dev/create-skill/` (folder name = frontmatter `name` = `create-skill`)
**Author:** Gal Tabakman / sir_albert

---

## 1. Purpose

A meta-skill that authors **agentskills.io-spec-compliant** skills through a *measured,
multi-angle, self-scoring loop*. It supersedes `superpowers:writing-skills` inside
sir_albert: it keeps that skill's genuinely good discipline-skill psychology, fixes its
weaknesses, and — critically — replaces its **unmeasured** RED-GREEN-REFACTOR loop with a
**convergence-driven, scored** one.

**North-star:** you describe a skill; `create-skill` produces a spec-valid `SKILL.md`
(plus optional bundled files), and — for skills that earn it — *proves* it works by
scoring it against an adversarial agent panel and iterating until the score converges.

---

## 2. Why not just use `superpowers:writing-skills`?

`writing-skills` is strong on the *psychology* of discipline skills but has six flaws this
skill fixes. This section is the "challenge" and is load-bearing for design decisions.

| # | superpowers weakness | create-skill fix |
|---|---|---|
| 1 | **Iron Law overclaims + self-contradicts** — mandates a failing-test-first loop for *every* skill/edit, then admits reference skills need retrieval tests and mechanical rules should be automated | Loop is **tiered** and reserved for skills that earn it; structural rules are **automated** (validator), not documented |
| 2 | **Contradicts the spec it cites** — "description = when, NOT what; never summarize" vs spec's "describes what it does **and** when" | Reconciled rule: **triggers-first + one 'what' clause, never step-by-step narration** — and this rule is *empirically tested* by the discoverability agent, not asserted |
| 3 | **Mixes opinion into "the spec"** — e.g. "description < 500 chars" (spec allows 1024) | Spec is **authoritative** for MUST; opinions are labeled SHOULD |
| 4 | **No machine validation** — ends in a manual checklist an agent can misjudge | **Terminates in `validate-skill.py`** (deterministic floor) |
| 5 | **No ROI gate on the expensive loop** — "5+ reps" with no when-worth-it | **Tier gate** decides whether to invest in a scored benchmark at all |
| 6 | **Violates its own token/naming guidance** (~500+ lines, Claude-centric) | Lean SKILL.md; heavy content in `references/`; portable spec output |

**Kept from superpowers:** SDO thinking, rationalization tables + red-flags for discipline
skills, "match the form to the failure," anti-narrative. Cited, not duplicated.

---

## 3. Output contract

Every run produces a spec-compliant skill directory:

```
<skill-name>/
  SKILL.md            # required; valid frontmatter (name, description) + body
  scripts/ …          # optional
  references/ …       # optional
  assets/ …           # optional
  evals/evals.json    # present for T1/T2 skills (scored scenario suite)
```

**Hard floor (blocking):** `scripts/validate-skill.py` (reused from the sir_albert
skill-guardrail hook) must pass — name regex/length/dir-match, required frontmatter,
description length. No skill ships structurally invalid.

**Description rule (reconciled #2):** lead with triggering conditions ("Use when …"),
plus at most one short clause of *what* it does (spec-endorsed). Never narrate the
workflow. Enforced empirically by the discoverability agent (§5.4), not by fiat.

---

## 4. Authoring flow (guided-but-lean)

1. **Classify** — skill type (discipline / technique / reference) + audience/value.
   These drive the rigor tier.
2. **Elicit** — a few targeted questions: triggers, what-it-does, core content,
   "is this discipline-enforcing?"
3. **Scaffold** — spec-compliant `SKILL.md` + folder from `assets/SKILL.template.md`.
4. **Validate (blocking)** — `validate-skill.py`. Fix before proceeding.
5. **Tier gate** — decide whether to invest in a scored benchmark (§6).
6. **Measured loop** (if T1/T2) — §5.
7. **Dogfooding gate** — §7.

---

## 5. The measured multi-angle loop

Replaces superpowers' unmeasured loop. A panel of dispatched agents writes scenarios,
runs them, and scores convergence.

### 5.1 Dynamic angles by type (hard cap ≤4 authors + ≤3 judges)

| Skill type | Author angles (pick, capped) |
|---|---|
| **Discipline** | Pressure (time/sunk-cost/authority), Loophole-hunter, Spirit-vs-letter |
| **Technique** | Naive applier, Edge-case, Transfer (just outside the examples) |
| **Reference** | Retrieval, Application, Gap |
| **Cross-cutting (always)** | Discoverability agent (§5.4), Structural validator (deterministic), **held-out Red-team** (§8) |

### 5.2 Scoring

- Run each scenario *k* times against a **fresh** agent with the candidate skill in context.
- `score = mean over scenarios of (passes / k)` ∈ [0,1].
- **Deterministic-first (§8):** each scenario declares a machine-checkable pass condition
  where one exists; LLM judgment only for irreducibly subjective criteria.
- Judge panel (≤3, optional model diversity) scores subjective criteria → mean pass +
  **inter-judge agreement**.

### 5.3 Convergence (plateau-aware — the core fix)

- **Baseline (RED):** score with the skill *absent* / description-only. If baseline
  already passes → nothing to fix, stop.
- **Progress = lift over baseline**, not absolute (§8 cancels shared bias).
- Noise band: SE ≈ √(p(1−p)/(n·k)). A change within ~1–2 SE is noise.
- **Stop on:** (a) lift ≥ target *and* low cross-scenario variance; OR
  (b) **plateau** — Δ < noise for 2 straight iterations → *change tactics, not add reps*;
  OR (c) budget cap.
- **Per-scenario diagnostics** point the next edit at the failing scenarios (no blind rewrite).

### 5.4 Discoverability sub-score (the elegant objective test)

Give an agent **only the description** + a pile of task prompts (some matching, some not).
Measure selection precision/recall. This objectively settles the superpowers-vs-spec
description argument instead of asserting a rule.

---

## 6. Rigor tiers (gate the benchmark investment)

| Tier | Runs | For |
|---|---|---|
| **T0 Structural** | scaffold + validate | trivial / one-off reference |
| **T1 Smoke** | + single-angle, few-rep scored run | most technique skills |
| **T2 Full panel loop** | dynamic multi-angle + convergence + `evals/` | discipline / shared / high-value |

Tiering exists *because* the panel is expensive (§8). The loop is central; the tier only
decides how much of it to run.

---

## 7. Dogfooding gate

`create-skill` must **author itself** to spec, pass its own `validate-skill.py`, and clear
a T2 loop. Self-hosting is the acceptance test — no synthetic panel can fake real use.

---

## 8. Correlated-judge-bias — managed, not eliminated

Same-model judges share blind spots; a panel cuts variance but not systematic bias, and
the failure direction is over-optimism. Not a deal-breaker. Design it down:

1. **Deterministic-first scoring** — shrink the surface exposed to LLM judgment.
2. **Delta-scoring** — measure lift over baseline; shared bias largely cancels.
3. **Angle + optional model diversity** — decorrelate errors; some judges on a different model.
4. **Held-out red-team author** — constructs a case that passes judges but violates intent;
   success ⇒ eval is gamed ⇒ strengthen scenarios.
5. **Disagreement health gate** — easy consensus on a borderline score → surface to human;
   scattered judges → fix the rubric.
6. **Human at the boundary + dogfood** — review only flagged cases; self-hosting is ground truth.

Residual exposure only for purely-subjective skills with no deterministic anchors; covered
by boundary-review.

---

## 9. Bundled layout (spec-compliant)

```
create-skill/
  SKILL.md                     # lean orchestration
  references/
    methodology.md             # corrected method + the §2 challenge rationale
    angles.md                  # angle catalog by skill type
    convergence.md             # scoring math + stop rules + bias mitigations
  agents/                      # dispatched prompt templates
    author-<angle>.md · judge.md · discoverability.md · red-team.md
  scripts/
    validate-skill.py          # reused from the skill-guardrail hook
    score.py                   # aggregate runs → score, agreement, SE, lift
  assets/
    SKILL.template.md · evals.template.json
```

---

## 10. Mechanism & dependencies

- **Fan-out:** Agent tool by default (dynamic-by-type, hard cap); **Workflow tool opt-in**
  only for heavy deterministic T2 runs.
- **Validator:** reuse `hooks/validate-skill.py` (single source of truth for structure).
- **Precedent:** `evals/evals.json` already exists in `skills/dev/git-guardrails/` —
  scored evals are an established sir_albert pattern.

---

## 11. Resolved decisions

1. **`score.py`** — pure-Python, **stdlib only** (matches `validate-skill.py`).
2. **`evals/`** — **commit for T2/discipline (big) skills; throwaway for T1 (small)** skills.
3. **Caps** — ≤4 authors, ≤3 judges, **k = 3** reps per scenario.
4. **Human boundary-review** — surfaced **inline during the run** (not an end report).

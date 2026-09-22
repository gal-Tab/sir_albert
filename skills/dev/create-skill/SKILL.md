---
name: create-skill
description: Use when authoring a new skill, editing a skill, or when a skill must be spec-valid and proven — scaffolds an agentskills-spec SKILL.md and scores it via a multi-angle convergence loop. Triggers on "create a skill", "write a skill", "author a skill", "make a skill".
---

# create-skill

**REQUIRED BACKGROUND:** Load `superpowers:writing-skills` before proceeding with any
discipline skill (SDO thinking, rationalization tables, anti-narrative patterns). This skill
keeps that psychology and replaces its unmeasured loop with the scored one below.

---

## When to use / when not

**Use when:**
- Authoring a new skill from scratch (any type: discipline / technique / reference).
- Editing an existing skill that must remain spec-valid.
- A skill needs proof it works, not just proof it compiles.

**Do not use when:**
- The output is a one-liner reference note — scaffold manually and stop at T0.
- The user wants a quick prompt snippet, not a reusable skill.
- Another skill already covers the task (check the skills list first).

---

## Flow

### Step 1 — Classify

Determine skill **type** (discipline / technique / reference) and **value tier** (T0/T1/T2).
These drive the rigor tier gate below.

Ask only what's needed:
1. What triggers this skill? (exact phrases or situations)
2. What does it do once triggered?
3. Is it enforcing a rule that humans rationalize away? → discipline candidate.
4. Who uses it, and how often?

### Step 2 — Elicit

Collect: trigger conditions · core content · deterministic pass conditions (for evals) ·
any bundled files needed (scripts, references, assets).

### Step 3 — Scaffold

Build the skill directory from `assets/SKILL.template.md`. Description rule (reconciled from
spec + superpowers):

> Lead with triggering conditions ("Use when …"); add at most one short *what* clause.
> Never narrate the workflow. Enforced empirically by the discoverability agent.

**Council / multi-voice skills:** if the skill's job is to run several named personas against
the same input (a "council," "board," panel of critics, etc.), scaffold one persona per file
under `agents/<persona>.md` — character/profile only, ending in a `{{placeholder}}` dispatch
block, exactly like this skill's own `agents/judge.md` and `agents/author-discipline.md`.
The orchestrator SKILL.md owns selection, parallel Agent-tool dispatch (fresh, blind
subagents), and response labeling. Any behavior that applies across all personas (tone,
mode, output constraints) is filled in via a placeholder at dispatch time — never copy-pasted
into every persona file. See `skills/biz/discovery-lens/` for a worked example.

### Step 4 — Validate (BLOCKING)

Run before proceeding:

```bash
python3 -c "import json;print(json.dumps({'hook_event_name':'PreToolUse','tool_input':{'file_path':'<path>/SKILL.md','content':open('<path>/SKILL.md').read()}}))" \
  | python3 skills/dev/create-skill/scripts/validate-skill.py
```

Fix all `🔴` violations. No skill advances with structural errors.

### Step 5 — Tier gate

| Tier | Investment | For |
|---|---|---|
| **T0 Structural** | Scaffold + validate. Done. | Trivial / one-off reference |
| **T1 Smoke** | Single-angle, few-rep scored run | Most technique skills |
| **T2 Full panel loop** | Dynamic multi-angle + convergence + committed `evals/` | Discipline / shared / high-value |

Choose the **lowest tier that matches the skill's value**. The loop is not free.

### Step 6 — Measured loop (T1/T2 only)

See full detail in [`references/methodology.md`](references/methodology.md),
[`references/angles.md`](references/angles.md),
[`references/convergence.md`](references/convergence.md).

Summary:

**a. Dispatch author panel** (Agent tool, dynamic by type — see angles.md; cap ≤4 authors).

| Skill type | Author angles |
|---|---|
| Discipline | Pressure, Loophole-hunter, Spirit-vs-letter |
| Technique | Naive applier, Edge-case, Transfer |
| Reference | Retrieval, Application, Gap |
| Always | Discoverability agent, Structural validator, Held-out Red-team |

Dispatch authors from `agents/author-{discipline,technique,reference}.md` in parallel via
the Agent tool. Dispatch `agents/discoverability.md` and `agents/red-team.md` as
cross-cutting agents.

**b. Build evals/** from `assets/evals.template.json`. Each scenario must declare a
machine-checkable pass condition where one exists; LLM judgment only for irreducibly
subjective criteria (bias-reduction from `references/convergence.md` §bias).

**c. Baseline run.** Run each scenario *k = 3* times against a **fresh** subagent with the
skill **absent** (description-only). Record pass rates → baseline score.

> If baseline already passes the target → nothing to fix; stop at T0.

**d. Iterate:**

1. Run all scenarios fresh (new subagent per run, skill in context).
2. Dispatch judge panel (Agent tool, ≤3 judges from `agents/judge.md`; optional model
   diversity to decorrelate).
3. Pipe results JSON to `score.py`:
   ```bash
   echo '<results-json>' | python3 skills/dev/create-skill/scripts/score.py
   ```
   Read the last line: `stop: <reason>`.
4. **Surface weak / low-agreement scenarios INLINE** (do not defer to an end report):
   - `weak_scenarios` list (pass-rate < 0.67) → ask human: "Scenario N is unreliable —
     fix the skill or tighten the rubric?"
   - `low_agreement_scenarios` list → ask human: "Judges split on scenario N — fix the
     rubric or accept uncertainty?"
   - `borderline_scenarios` list (score 0.4–0.6, diagnostic at higher k) → ask human:
     "Scenario N is borderline — is this a real failure or an ambiguous rubric?"
5. Edit the skill to address failing scenarios. Point edits at the failing scenarios only —
   no blind rewrites.
6. Repeat until `score.py` reports `stop: threshold` or `stop: plateau`.

**e. Stop rules** (from `references/convergence.md`):

| `stop_reason` | Action |
|---|---|
| `threshold` | Lift ≥ target, low variance. Done. |
| `plateau` | Δ < noise for 2 iterations. Change tactics, not add reps. |
| `budget` | Hard cap reached. Accept current score; note residual risk. |

---

## T2 note — Workflow tool opt-in

For heavy deterministic T2 runs (large scenario suites, many reps), the author panel
dispatch and scoring loop can be wrapped in a Workflow tool script instead of inline Agent
calls. This is opt-in only — require explicit user confirmation before switching, as it adds
orchestration overhead not warranted for most skills.

---

## Evals policy

| Tier | `evals/evals.json` |
|---|---|
| T2 / discipline | **Commit.** These are proof artifacts; they make future regressions detectable. |
| T1 | **Throwaway.** Delete after the run; don't clutter the repo with low-signal fixtures. |
| T0 | Not created. |

---

## Cross-references

- [`references/methodology.md`](references/methodology.md) — corrected method, the
  superpowers:writing-skills challenge rationale, and why each fix was made.
- [`references/angles.md`](references/angles.md) — full angle catalog by skill type with
  dispatch instructions.
- [`references/convergence.md`](references/convergence.md) — scoring math, noise band,
  stop rules, plateau detection, and bias mitigations.

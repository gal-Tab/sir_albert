---
name: create-skill
description: Use when authoring a new skill, editing a skill, or when a skill must be spec-valid and proven — scaffolds an agentskills-spec SKILL.md and scores it via a multi-angle convergence loop. Triggers on "create a skill", "write a skill", "author a skill", "make a skill".
---

# create-skill

Boot from `os/PREAMBLE.md`.

**SDO rules (inlined):** Match the form to the failure · Rationalization table (name the 3 rationalizations for each enforced rule) · Anti-narrative description (when + one what clause, never workflow narration) · Red flags: "it's obvious" / "just once" / "special case" → apply the rule harder.

---

## Flow

### Step 1 — Classify
Type: **discipline** / technique / reference. Tier: **T0** (structural only) / **T1** (smoke) / **T2** (full panel). Ask: triggers? content? enforces a rule humans rationalize away?

### Step 2 — Elicit
Collect: trigger conditions · core content · deterministic pass conditions · any bundled files.

### Step 3 — Scaffold
Build from `assets/SKILL.template.md`. Description: "Use when …" + at most one what clause, never workflow narration.

**Council skills:** one persona per `agents/<persona>.md` (character only + `{{placeholder}}` dispatch block). Orchestrator owns parallel dispatch and labeling. See `skills/biz/discovery-lens/` for a worked example.

### Step 4 — Validate (BLOCKING)

```bash
python3 -c "import json;print(json.dumps({'hook_event_name':'PreToolUse','tool_input':{'file_path':'<path>/SKILL.md','content':open('<path>/SKILL.md').read()}}))" \
  | python3 skills/dev/create-skill/scripts/validate-skill.py
```

Fix all `🔴` before advancing.

### Step 5 — Tier gate

| Tier | For |
|---|---|
| **T0** | Trivial / one-off reference — scaffold + validate, done |
| **T1** | Technique skills — single-angle smoke run |
| **T2** | Discipline / shared / high-value — full panel loop |

### Step 6 — Measured loop (T1/T2)

See [`references/methodology.md`](references/methodology.md) for the full protocol.

**Common path:**
1. Dispatch author panel in parallel (angles by type — see [`references/angles.md`](references/angles.md)).
2. Build `evals/evals.json` from `assets/evals.template.json`. Machine-checkable pass conditions where possible.
3. **Baseline:** run each scenario k=3 times, skill **absent**. Record pass rates.
4. Iterate: run skill-present → judge panel → `score.py` → address weak scenarios → repeat.
5. Stop when `score.py` reports `threshold` or `plateau` (see [`references/convergence.md`](references/convergence.md)).

**Evals policy:** T2/discipline → commit `evals/`. T1 → throwaway. T0 → none.

---

## Cross-references
- [`references/methodology.md`](references/methodology.md) — full protocol, prior challenge rationale, bias mitigations
- [`references/angles.md`](references/angles.md) — angle catalog by skill type
- [`references/convergence.md`](references/convergence.md) — scoring math, stop rules, plateau detection

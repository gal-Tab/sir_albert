# create-skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `create-skill`, a sir_albert meta-skill that authors agentskills-spec-compliant skills via a measured, multi-angle, convergence-driven scoring loop.

**Architecture:** A lean `SKILL.md` orchestrates: classify → elicit → scaffold → structural-validate → tier-gate → measured loop (dispatched agent panel writes/scores scenarios) → dogfood. The only computational unit is `score.py` (stdlib, TDD); structure is enforced by the reused `validate-skill.py`; agents ship as dispatched prompt templates.

**Tech Stack:** Markdown (SKILL.md + references + agent prompts), Python 3 stdlib (`score.py`, `validate-skill.py`), Agent tool for fan-out (Workflow tool opt-in for heavy T2).

**Spec:** `docs/superpowers/specs/2026-09-09-create-skill-design.md`

## Global Constraints

- Output MUST be agentskills.io-spec compliant; `validate-skill.py` MUST pass (hard floor).
- Python: **stdlib only** (no third-party deps); tests use `unittest`.
- Home: `skills/dev/create-skill/`; frontmatter `name` = folder name = `create-skill`.
- Description rule: triggers-first + ≤1 "what" clause; never narrate workflow.
- Panel caps: **≤4 author angles, ≤3 judges, k=3 reps/scenario**.
- Scoring: **delta over baseline** (not absolute); stop on threshold-OR-plateau-OR-budget.
- `evals/`: commit for T2/discipline (big) skills; throwaway for T1 (small).
- Human boundary-review: surfaced **inline** during the run.
- Commit after every task.

---

### Task 1: Scaffold skill skeleton + reuse validator

**Files:**
- Create: `skills/dev/create-skill/SKILL.md` (stub, valid frontmatter)
- Create: `skills/dev/create-skill/scripts/validate-skill.py` (copy of `hooks/validate-skill.py`)
- Create: `skills/dev/create-skill/assets/SKILL.template.md`
- Create: `skills/dev/create-skill/assets/evals.template.json`

**Interfaces:**
- Produces: a structurally valid skill directory; `validate-skill.py` runnable at `scripts/validate-skill.py`.

- [ ] **Step 1: Copy the validator**

```bash
mkdir -p skills/dev/create-skill/scripts skills/dev/create-skill/assets \
         skills/dev/create-skill/agents skills/dev/create-skill/references
cp hooks/validate-skill.py skills/dev/create-skill/scripts/validate-skill.py
```

- [ ] **Step 2: Write stub SKILL.md with valid, reconciled-rule frontmatter**

```markdown
---
name: create-skill
description: Use when authoring a new skill, editing a skill, or when a skill must be spec-valid and proven — scaffolds an agentskills-spec SKILL.md and scores it via a multi-angle convergence loop. Triggers on "create a skill", "write a skill", "author a skill", "make a skill".
---

# create-skill

(orchestration — filled in Task 7)
```

- [ ] **Step 3: Write `assets/SKILL.template.md`** (the scaffold emitted for new skills)

```markdown
---
name: {{name}}
description: {{description}}
---

# {{title}}

## Overview
{{one-line core principle}}

## When to use
{{symptoms / triggers}}

## Instructions
{{steps}}
```

- [ ] **Step 4: Write `assets/evals.template.json`**

```json
{
  "skill": "{{name}}",
  "type": "discipline|technique|reference",
  "k": 3,
  "scenarios": [
    {
      "id": "s1",
      "angle": "{{angle}}",
      "prompt": "{{scenario prompt}}",
      "deterministic_check": null,
      "rubric": "{{pass criteria for judges}}"
    }
  ]
}
```

- [ ] **Step 5: Verify structural validity**

Run:
```bash
python3 -c "import json,sys; print(json.dumps({'hook_event_name':'PreToolUse','tool_input':{'file_path':'/Users/galta/Development/sir_albert/skills/dev/create-skill/SKILL.md','content':open('skills/dev/create-skill/SKILL.md').read()}}))" | python3 skills/dev/create-skill/scripts/validate-skill.py; echo "exit=$?"
```
Expected: `exit=0` (no structural violations).

- [ ] **Step 6: Commit**

```bash
git add skills/dev/create-skill
git commit -m "feat(create-skill): scaffold skeleton + reuse validator"
```

---

### Task 2: `score.py` — core metrics (TDD)

**Files:**
- Create: `skills/dev/create-skill/scripts/score.py`
- Test: `skills/dev/create-skill/scripts/test_score.py`

**Interfaces:**
- Produces: `scenario_pass_rate(passes,k)->float`, `skill_score(pass_rates)->float`, `standard_error(p,n,k)->float`, `lift(candidate,baseline)->float`.

- [ ] **Step 1: Write failing tests**

```python
import unittest, math
from score import scenario_pass_rate, skill_score, standard_error, lift

class TestMetrics(unittest.TestCase):
    def test_pass_rate(self):
        self.assertEqual(scenario_pass_rate(2, 4), 0.5)
    def test_pass_rate_zero_k_raises(self):
        with self.assertRaises(ValueError):
            scenario_pass_rate(1, 0)
    def test_skill_score_is_mean(self):
        self.assertAlmostEqual(skill_score([0.0, 0.5, 1.0]), 0.5)
    def test_skill_score_empty_raises(self):
        with self.assertRaises(ValueError):
            skill_score([])
    def test_standard_error(self):
        self.assertAlmostEqual(standard_error(0.5, 4, 3), math.sqrt(0.25/12))
    def test_lift(self):
        self.assertAlmostEqual(lift(0.85, 0.40), 0.45)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd skills/dev/create-skill/scripts && python3 -m unittest test_score -v`
Expected: FAIL — `ModuleNotFoundError`/`ImportError` (score.py missing).

- [ ] **Step 3: Implement minimal metrics**

```python
import math

def scenario_pass_rate(passes, k):
    if k <= 0:
        raise ValueError("k must be > 0")
    return passes / k

def skill_score(pass_rates):
    if not pass_rates:
        raise ValueError("no scenarios")
    return sum(pass_rates) / len(pass_rates)

def standard_error(p, n, k):
    if n <= 0 or k <= 0:
        raise ValueError("n and k must be > 0")
    return math.sqrt(p * (1 - p) / (n * k))

def lift(candidate, baseline):
    return candidate - baseline
```

- [ ] **Step 4: Run to verify it passes**

Run: `cd skills/dev/create-skill/scripts && python3 -m unittest test_score -v`
Expected: PASS (6 tests).

- [ ] **Step 5: Commit**

```bash
git add skills/dev/create-skill/scripts/score.py skills/dev/create-skill/scripts/test_score.py
git commit -m "feat(create-skill): score.py core metrics"
```

---

### Task 3: `score.py` — convergence & judge agreement (TDD)

**Files:**
- Modify: `skills/dev/create-skill/scripts/score.py`
- Modify: `skills/dev/create-skill/scripts/test_score.py`

**Interfaces:**
- Consumes: `standard_error` (Task 2).
- Produces: `is_plateau(history,se,patience=2,factor=1.0)->bool`, `judge_agreement(judge_scores)->float`, `is_borderline(score,low=0.4,high=0.6)->bool`.

- [ ] **Step 1: Add failing tests**

```python
from score import is_plateau, judge_agreement, is_borderline

class TestConvergence(unittest.TestCase):
    def test_plateau_true_when_deltas_below_se(self):
        # deltas 0.01, 0.01 both < se=0.05 -> plateau
        self.assertTrue(is_plateau([0.80, 0.81, 0.82], se=0.05))
    def test_plateau_false_when_still_improving(self):
        self.assertFalse(is_plateau([0.40, 0.60, 0.85], se=0.05))
    def test_plateau_false_when_too_short(self):
        self.assertFalse(is_plateau([0.80], se=0.05))
    def test_judge_agreement_unanimous(self):
        self.assertEqual(judge_agreement([1, 1, 1]), 1.0)
    def test_judge_agreement_split(self):
        self.assertAlmostEqual(judge_agreement([1, 0, 0]), 2/3)
    def test_judge_agreement_empty_raises(self):
        with self.assertRaises(ValueError):
            judge_agreement([])
    def test_borderline(self):
        self.assertTrue(is_borderline(0.5))
        self.assertFalse(is_borderline(0.85))
```

- [ ] **Step 2: Run to verify new tests fail**

Run: `cd skills/dev/create-skill/scripts && python3 -m unittest test_score -v`
Expected: FAIL — `ImportError` on the new names.

- [ ] **Step 3: Implement**

```python
def is_plateau(history, se, patience=2, factor=1.0):
    if len(history) < patience + 1:
        return False
    recent = history[-(patience + 1):]
    deltas = [abs(recent[i + 1] - recent[i]) for i in range(len(recent) - 1)]
    return all(d < factor * se for d in deltas)

def judge_agreement(judge_scores):
    if not judge_scores:
        raise ValueError("no judges")
    frac_pass = sum(1 for s in judge_scores if s >= 0.5) / len(judge_scores)
    return max(frac_pass, 1 - frac_pass)

def is_borderline(score, low=0.4, high=0.6):
    return low <= score <= high
```

- [ ] **Step 4: Run to verify all pass**

Run: `cd skills/dev/create-skill/scripts && python3 -m unittest test_score -v`
Expected: PASS (13 tests total).

- [ ] **Step 5: Commit**

```bash
git add skills/dev/create-skill/scripts/score.py skills/dev/create-skill/scripts/test_score.py
git commit -m "feat(create-skill): convergence + judge agreement"
```

---

### Task 4: `score.py` — report builder + CLI (TDD)

**Files:**
- Modify: `skills/dev/create-skill/scripts/score.py`
- Modify: `skills/dev/create-skill/scripts/test_score.py`

**Interfaces:**
- Consumes: all Task 2–3 functions.
- Produces: `build_report(data)->dict` and `format_report(report)->str`; `main()` reads a results JSON on stdin and prints the formatted report. Input JSON shape:
  `{"k": int, "baseline": {"pass_rates": [float]}, "iterations": [{"pass_rates":[float], "judges":[[0/1,...]]}]}`.
  Report dict keys: `baseline_score`, `iterations` (list of `{score, lift, se, plateau, borderline_scenarios, low_agreement_scenarios}`), `stop_reason`.

- [ ] **Step 1: Add failing tests**

```python
from score import build_report, format_report

class TestReport(unittest.TestCase):
    def _data(self):
        return {
            "k": 3,
            "baseline": {"pass_rates": [0.33, 0.33]},
            "iterations": [
                {"pass_rates": [0.33, 0.67], "judges": [[1,0,0],[1,1,0]]},
                {"pass_rates": [1.0, 1.0],  "judges": [[1,1,1],[1,1,1]]},
            ],
        }
    def test_baseline_score(self):
        r = build_report(self._data())
        self.assertAlmostEqual(r["baseline_score"], 0.33)
    def test_lift_computed_vs_baseline(self):
        r = build_report(self._data())
        self.assertAlmostEqual(r["iterations"][-1]["lift"], 1.0 - 0.33, places=2)
    def test_stop_reason_present(self):
        r = build_report(self._data())
        self.assertIn(r["stop_reason"], {"threshold", "plateau", "budget", "in_progress"})
    def test_format_report_is_text(self):
        r = build_report(self._data())
        out = format_report(r)
        self.assertIsInstance(out, str)
        self.assertIn("baseline", out.lower())
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd skills/dev/create-skill/scripts && python3 -m unittest test_score -v`
Expected: FAIL — `ImportError` on `build_report`/`format_report`.

- [ ] **Step 3: Implement**

```python
import json, sys

TARGET_LIFT = 0.4   # SHOULD default; override per skill

def build_report(data, target_lift=TARGET_LIFT):
    k = data["k"]
    base = skill_score(data["baseline"]["pass_rates"])
    history = [base]
    iters = []
    stop_reason = "in_progress"
    for it in data["iterations"]:
        n = len(it["pass_rates"])
        score = skill_score(it["pass_rates"])
        se = standard_error(score, n, k)
        history.append(score)
        borderline = [i for i, pr in enumerate(it["pass_rates"]) if is_borderline(pr)]
        low_agree = []
        for i, judges in enumerate(it.get("judges", [])):
            if judge_agreement(judges) < 1.0 and judge_agreement(judges) <= 0.67:
                low_agree.append(i)
        iters.append({
            "score": score,
            "lift": lift(score, base),
            "se": se,
            "plateau": is_plateau(history, se),
            "borderline_scenarios": borderline,
            "low_agreement_scenarios": low_agree,
        })
        if lift(score, base) >= target_lift and all(not is_borderline(pr) for pr in it["pass_rates"]):
            stop_reason = "threshold"
            break
        if iters[-1]["plateau"]:
            stop_reason = "plateau"
            break
    else:
        stop_reason = "budget"
    return {"baseline_score": base, "iterations": iters, "stop_reason": stop_reason}

def format_report(report):
    lines = [f"baseline score: {report['baseline_score']:.2f}"]
    for i, it in enumerate(report["iterations"]):
        lines.append(
            f"  iter {i}: score={it['score']:.2f} lift={it['lift']:+.2f} "
            f"se={it['se']:.3f} plateau={it['plateau']} "
            f"borderline={it['borderline_scenarios']} low_agreement={it['low_agreement_scenarios']}"
        )
    lines.append(f"stop: {report['stop_reason']}")
    return "\n".join(lines)

def main():
    data = json.load(sys.stdin)
    print(format_report(build_report(data)))

if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run to verify all pass**

Run: `cd skills/dev/create-skill/scripts && python3 -m unittest test_score -v`
Expected: PASS (17 tests total).

- [ ] **Step 5: Smoke the CLI**

Run:
```bash
cd skills/dev/create-skill/scripts && echo '{"k":3,"baseline":{"pass_rates":[0.33,0.33]},"iterations":[{"pass_rates":[1.0,1.0],"judges":[[1,1,1],[1,1,1]]}]}' | python3 score.py
```
Expected: report text ending in `stop: threshold`.

- [ ] **Step 6: Commit**

```bash
git add skills/dev/create-skill/scripts/score.py skills/dev/create-skill/scripts/test_score.py
git commit -m "feat(create-skill): report builder + CLI"
```

---

### Task 5: Agent prompt templates (panel)

**Files:**
- Create: `skills/dev/create-skill/agents/author-discipline.md`
- Create: `skills/dev/create-skill/agents/author-technique.md`
- Create: `skills/dev/create-skill/agents/author-reference.md`
- Create: `skills/dev/create-skill/agents/judge.md`
- Create: `skills/dev/create-skill/agents/discoverability.md`
- Create: `skills/dev/create-skill/agents/red-team.md`

**Interfaces:**
- Produces: dispatchable prompts. Each author prompt outputs scenarios in the `evals.template.json` shape (id, angle, prompt, deterministic_check, rubric). `judge.md` outputs a 0/1 verdict + reason per run. `discoverability.md` outputs selection precision/recall. `red-team.md` outputs a gaming case or "none".

- [ ] **Step 1: Write author prompts (one per type), each emitting spec-shaped scenarios**

`author-discipline.md` (angles: pressure, loophole-hunter, spirit-vs-letter):
```markdown
You are a {{angle}} adversary testing a DISCIPLINE skill.
Skill under test: {{skill_body}}
Produce {{n}} scenarios that tempt an agent to violate the skill's rule under pressure.
Output JSON array of {id, angle, prompt, deterministic_check|null, rubric}.
Prefer a machine-checkable deterministic_check whenever the violation is detectable
(e.g. a regex/command); use rubric only for irreducibly subjective judgments.
```
(Write `author-technique.md` with angles naive-applier/edge-case/transfer, and
`author-reference.md` with retrieval/application/gap — same output contract.)

- [ ] **Step 2: Write `judge.md`**

```markdown
You are one judge on a panel. Rubric: {{rubric}}
Transcript of the agent attempting the scenario: {{transcript}}
Return strictly: {"pass": 0|1, "reason": "<one sentence>"}.
Judge only against the rubric. Do not reward verbosity.
```

- [ ] **Step 3: Write `discoverability.md`**

```markdown
You are given ONLY this description: "{{description}}"
And this list of task prompts (some relevant, some not): {{prompts}}
For each, answer would you invoke this skill (yes/no).
Return {"selected": [ids]} — used to compute precision/recall of the description.
```

- [ ] **Step 4: Write `red-team.md`**

```markdown
You are red-teaming the EVAL, not the skill.
Scenarios + rubrics: {{evals}}
Construct one agent response that PASSES the judges but VIOLATES the skill's intent.
Return {"gamed": true, "example": "..."} or {"gamed": false}.
```

- [ ] **Step 5: Structural check — every template has its output contract**

Run:
```bash
cd skills/dev/create-skill/agents && for f in *.md; do grep -q -iE "return|output" "$f" && echo "OK $f" || echo "MISSING contract: $f"; done
```
Expected: all `OK`.

- [ ] **Step 6: Commit**

```bash
git add skills/dev/create-skill/agents
git commit -m "feat(create-skill): panel prompt templates"
```

---

### Task 6: References (methodology, angles, convergence)

**Files:**
- Create: `skills/dev/create-skill/references/methodology.md`
- Create: `skills/dev/create-skill/references/angles.md`
- Create: `skills/dev/create-skill/references/convergence.md`

**Interfaces:**
- Produces: on-demand detail the lean SKILL.md links to.

- [ ] **Step 1: `methodology.md`** — port §2 (the superpowers challenge, 6-fix table) + the reconciled description rule + the tier definitions from the spec. Cite `superpowers:writing-skills` by name for discipline psychology; do not duplicate it.

- [ ] **Step 2: `angles.md`** — the §5.1 angle-by-type table + the cap rule (≤4 authors, ≤3 judges) + guidance on picking angles dynamically.

- [ ] **Step 3: `convergence.md`** — the scoring math (score/SE/lift), the stop rules (threshold/plateau/budget), delta-scoring rationale, and the §8 bias mitigations (deterministic-first, delta-scoring, model diversity, red-team, disagreement gate, boundary review).

- [ ] **Step 4: Verify links resolve**

Run:
```bash
cd skills/dev/create-skill && for f in references/*.md; do echo "--- $f"; test -s "$f" && echo "non-empty OK"; done
```
Expected: all non-empty.

- [ ] **Step 5: Commit**

```bash
git add skills/dev/create-skill/references
git commit -m "docs(create-skill): methodology, angles, convergence references"
```

---

### Task 7: SKILL.md orchestration body

**Files:**
- Modify: `skills/dev/create-skill/SKILL.md`

**Interfaces:**
- Consumes: `scripts/validate-skill.py`, `scripts/score.py`, `agents/*`, `references/*`.
- Produces: the runnable skill flow.

- [ ] **Step 1: Write the body** — implement §4 flow with these sections, keeping it lean and linking to references (no duplication):
  - **When to use / when not** (bullets, symptoms).
  - **Flow:** classify (type + value) → elicit → scaffold from `assets/SKILL.template.md` → **run `validate-skill.py` (blocking)** → tier gate (T0/T1/T2 table) → measured loop.
  - **Measured loop:** dispatch author panel (Agent tool, dynamic-by-type, capped) → build `evals/` from `assets/evals.template.json` → baseline run → iterate: run scenarios (fresh subagent), judge panel, feed results JSON to `score.py`, read `stop_reason`; **surface borderline/low-agreement inline** for human review; stop on threshold/plateau/budget.
  - **T2 note:** Workflow tool opt-in for heavy deterministic runs.
  - **evals policy:** commit for T2/discipline, throwaway for T1.
  - **Cross-references:** `references/methodology.md`, `angles.md`, `convergence.md`; cite `superpowers:writing-skills` as REQUIRED BACKGROUND for discipline psychology.

- [ ] **Step 2: Verify structural validity + description rule**

Run:
```bash
python3 -c "import json;print(json.dumps({'hook_event_name':'PreToolUse','tool_input':{'file_path':'/Users/galta/Development/sir_albert/skills/dev/create-skill/SKILL.md','content':open('skills/dev/create-skill/SKILL.md').read()}}))" | python3 skills/dev/create-skill/scripts/validate-skill.py; echo "exit=$?"
```
Expected: `exit=0`, no warnings (description starts with "Use when", third person, <500 chars, body <500 lines).

- [ ] **Step 3: Commit**

```bash
git add skills/dev/create-skill/SKILL.md
git commit -m "feat(create-skill): orchestration body"
```

---

### Task 8: Dogfood — T1 smoke end-to-end

**Files:**
- Create (throwaway): `/tmp/create-skill-dogfood/echo-fact/SKILL.md` + `evals.json`

**Interfaces:**
- Consumes: the whole skill.
- Produces: evidence the loop + `score.py` integrate on a real toy skill.

- [ ] **Step 1: Author a trivial toy skill by hand** (a reference skill "echo-fact" that returns a fixed fact) and a 2-scenario `evals.json` with deterministic checks.

- [ ] **Step 2: Run baseline + one improved iteration through score.py**

Run:
```bash
echo '{"k":3,"baseline":{"pass_rates":[0.0,0.33]},"iterations":[{"pass_rates":[1.0,1.0],"judges":[[1,1,1],[1,1,1]]}]}' | python3 skills/dev/create-skill/scripts/score.py
```
Expected: report shows `baseline score: 0.17`, a positive `lift`, `stop: threshold`.

- [ ] **Step 3: Validate the toy skill structurally**

Run:
```bash
python3 -c "import json;print(json.dumps({'hook_event_name':'PostToolUse','tool_input':{'file_path':'/tmp/create-skill-dogfood/echo-fact/SKILL.md'}}))" | python3 skills/dev/create-skill/scripts/validate-skill.py; echo "exit=$?"
```
Expected: `exit=0`.

- [ ] **Step 4: Record dogfood evidence** in a short note at the top of `references/convergence.md` (a "verified <date>" line). Clean up `/tmp` toy with `unlink`/`rmdir` (not `rm -rf`).

- [ ] **Step 5: Commit**

```bash
git add skills/dev/create-skill
git commit -m "test(create-skill): dogfood T1 smoke verified"
```

---

## Self-Review

**Spec coverage:** §1 purpose→SKILL.md (T7); §2 challenge→methodology (T6); §3 output contract + validator→T1/T7; §4 flow→T7; §5 loop+angles+discoverability→T5/T7; §5.2–5.3 scoring/convergence→T2/T3/T4; §6 tiers→T6/T7; §7 dogfood→T8; §8 bias mitigations→T5(red-team, deterministic_check)/T4(delta, agreement)/T6(convergence.md); §9 layout→all; §10 mechanism→T5/T7. No uncovered requirement.

**Placeholder scan:** Code steps carry real, runnable code (score.py fully implemented across T2–T4; tests concrete). Content tasks (T5/T6/T7) specify exact sections and output contracts, not "TBD". Template files use `{{...}}` intentionally (they are templates, not plan placeholders).

**Type consistency:** `score.py` names are stable across tasks — `scenario_pass_rate`, `skill_score`, `standard_error`, `lift` (T2) → `is_plateau`, `judge_agreement`, `is_borderline` (T3) → `build_report`, `format_report`, `main` (T4). Report dict keys (`baseline_score`, `iterations[].{score,lift,se,plateau,borderline_scenarios,low_agreement_scenarios}`, `stop_reason`) match between T4 impl and T8 usage.

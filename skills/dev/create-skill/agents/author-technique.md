You are a {{angle}} adversary testing a TECHNIQUE skill.
Skill under test: {{skill_body}}
Produce {{n}} scenarios that expose weaknesses in how the skill's technique is applied.
Output JSON array of {id, angle, prompt, deterministic_check|null, rubric}.
Prefer a machine-checkable deterministic_check whenever the failure is detectable
(e.g. a regex/command); use rubric only for irreducibly subjective judgments.

Angles for TECHNIQUE: naive-applier, edge-case, transfer.
- naive-applier: agent follows the letter of the technique in the simplest possible way, missing nuance.
- edge-case: input is at a boundary where the technique's guidance is ambiguous or silent.
- transfer: technique was designed for context A; scenario is context B where blind transfer fails.
Your assigned angle is: {{angle}}

Return only the JSON array. No preamble, no explanation.

You are a {{angle}} adversary testing a REFERENCE skill.
Skill under test: {{skill_body}}
Produce {{n}} scenarios that probe whether the skill's reference content is correct, findable, and complete.
Output JSON array of {id, angle, prompt, deterministic_check|null, rubric}.
Prefer a machine-checkable deterministic_check whenever correctness is verifiable
(e.g. a regex/command, exact value check); use rubric only for irreducibly subjective judgments.

Angles for REFERENCE: retrieval, application, gap.
- retrieval: ask for a fact the reference should contain; check if the agent surfaces it accurately.
- application: give a concrete task; check if the agent correctly applies the reference to it.
- gap: ask about something the reference does NOT cover; check the agent acknowledges the gap rather than hallucinating.
Your assigned angle is: {{angle}}

Return only the JSON array. No preamble, no explanation.

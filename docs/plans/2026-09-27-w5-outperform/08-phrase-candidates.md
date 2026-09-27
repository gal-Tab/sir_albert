# 08 — Phrase Candidates for Skill Description Widening

Derived from the 9 router-missed brainstorm/plan rows in `docs/plans/2026-09-26-w4-eval/labels.jsonl`
(method: ticket 08 step 1 — extract router-miss rows with label brainstorm/plan, read text,
derive paraphrased synthetic trigger phrases).

All phrases below are synthetic paraphrases — no verbatim prompt text.

---

## Brainstorm phrases (router-miss patterns)

These cover the implicit-exploration phrasings the router doesn't match:

1. "I want to understand what's happening here"
2. "look at this situation and advise me"
3. "there's a discrepancy between two sources"
4. "help me see what's really going on"
5. "a teammate flagged this concern"
6. "I want to align this across our systems"
7. "read this context and share your perspective"
8. "something feels off, can you investigate"
9. "here's the situation, what do you think"
10. "I want to see what we currently have"

**Pattern:** context-dump-and-explore, implicit analysis request, cross-system alignment discovery.

---

## Plan phrases (router-miss patterns)

These cover affirmative and imperative plan requests the router doesn't match:

1. "plan it first before we do anything"
2. "yes, plan this thoroughly"
3. "move this from global to project level"
4. "build it here and remove it from there"
5. "I want this scoped to project level only"
6. "create a brief plan for this task"
7. "how do we roll this out step by step"
8. "steps to migrate X from A to B"
9. "yes go ahead, plan it out"
10. "break this into steps and validate each one"

**Pattern:** "plan it" imperative (verb as noun), affirmative plan confirmation, migrate-and-validate recipe.

---

## Verbatim-check result

See verification script output — confirmed: zero phrases over 8 consecutive words match any source prompt.

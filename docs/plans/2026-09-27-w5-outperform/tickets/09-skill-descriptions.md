# 09 — skill-descriptions

**Blocked by:** —

## Goal
The `brainstorm` and `plan` SKILL.md descriptions trigger on the phrasings the router misses. The model routes itself when the regex can't; 131 of 138 standalone corpus prompts get no router hit at all.

## Why
Recall past the regex depends on the model matching prompts to skill descriptions. Today's descriptions list mostly explicit commands ("brainstorm this", "write a plan"). Gal's actual task prompts ("what do you think about…", "how should we approach…", "turn this into…") aren't covered.

## Steps
1. Invoke `/sir-albert:create-skill` in edit mode on `plugins/sir-albert/skills/core/brainstorm/SKILL.md`. This is **mandatory**: every SKILL.md edit goes through create-skill (Gal's rule). Input: the synthetic phrases from `docs/plans/2026-09-27-w5-outperform/08-phrase-candidates.md` (ticket 08 step 1, or derive them the same way if 08 isn't done). Ask: widen the description's trigger list to cover them, and keep "Use when …" first.
2. Complete create-skill's full scoring loop and evals for brainstorm. Expected: it passes its own convergence threshold, and `hooks/validate-skill.py` passes on save.
3. Same for `plugins/sir-albert/skills/core/plan/SKILL.md` (plan phrasings: "break this down", "how do we roll this out", "steps to …").
4. Check the description length: `/usr/local/bin/python3.13 -c` to parse the frontmatter; each description must stay ≤ 1024 chars (agentskills spec).
5. Run: `/usr/local/bin/python3.13 -m pytest -q plugins/sir-albert/tests/`. Expected: all pass.
6. Commit: `git commit -m "feat(w5): brainstorm/plan descriptions cover Gal's real task phrasing"`

## Definition of Done
- [ ] Both edits went through `/sir-albert:create-skill`, with scoring + evals recorded
- [ ] Descriptions ≤ 1024 chars; validate-skill passes
- [ ] No text from `*p3*` files used (tuning firewall)

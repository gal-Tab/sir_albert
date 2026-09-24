# 14 — Full create-skill loop for skills edited in W1

**Blocked by:** 08
**Why:** In W1, `freeze`, `retro` and `kw-compound` received path/ref fixes through create-skill's lightest path. Gal's rule (2026-09-24) requires the full loop with committed `evals/` for every skill touched. (`build-discipline` is covered by ticket 07.)

## Scope
- `plugins/sir-albert/skills/core/freeze/SKILL.md`
- `plugins/sir-albert/skills/core/retro/SKILL.md`
- `plugins/kb/skills/kw-compound/SKILL.md`

## Steps
1. For each skill, run the full `/sir-albert:create-skill` loop in **edit mode** against the current SKILL.md: author/refine → score → converge. Behavior must stay the same; the only goal is spec validity plus proven triggers. Pinned hard constraints: freeze's hook command path, retro's hook/cron paths, and kw-compound's `kb:wiki-query` / `kb:wiki-compile` names.
2. Commit each skill's `evals/` dir next to it.
3. If the loop proposes a behavior change (not just wording or triggers), stop and return `QUESTION:`.
4. Commit: `test(skills): full create-skill loop for freeze, retro, kw-compound (W1 follow-up)`.

## DOD
- [ ] 3 × `evals/` committed
- [ ] `plugins/kb` pytest still passes
- [ ] freeze-guard and session-record hooks still fire (rerun the W1 ticket 08 check 4 sub-checks for those two)

## create-skill loop (mandatory, Gal rule 2026-09-24)
Every SKILL.md edited here runs the **full** `/sir-albert:create-skill` loop, with `evals/` committed. No lightest path. The coordinator verifies from your transcript (Skill calls + `evals/` dirs).
- [ ] Full create-skill loop run; `evals/` committed for each skill touched

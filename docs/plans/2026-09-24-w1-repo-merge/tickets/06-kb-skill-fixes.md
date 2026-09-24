# 06 — Move kw-compound to kb, fold learnings into learn-recall

**Blocked by:** 05
**Spec:** §5
**Rule:** all skill work goes through `/sir-albert:create-skill`.

## Steps
1. `git mv plugins/sir-albert/skills/agentic/kw-compound plugins/kb/skills/kw-compound`.
2. Via create-skill, edit `plugins/kb/skills/kw-compound/SKILL.md`: replace `kb-query` → `kb:wiki-query` and `kb-compile` → `kb:wiki-compile` (7 known lines), and fix any `sir_albert`-specific paths so they use the current project's `raw/`. Keep its trigger phrases.
3. Read `plugins/sir-albert/skills/core/learnings/SKILL.md` and `plugins/kb/skills/learn-recall/SKILL.md`. List what `learnings` does that `learn-recall` doesn't (e.g. loading MEMORY.md corrections before compile).
4. Via create-skill, add those unique behaviors to `learn-recall` as one section. If there are none, skip. **If the overlap is unclear, ask the coordinator before deleting anything.**
5. `git rm -r plugins/sir-albert/skills/core/learnings`. Remove it from `REGISTRY.md` and `RESOLVER.md`.
6. If `plugins/sir-albert/skills/agentic/` now contains only `self-reflection`, leave it (W2 decides).
7. pytest in `plugins/kb` passes. Commit: `refactor(kb): move kw-compound into kb, fold learnings into learn-recall`.

## DOD
- [ ] `grep -rn 'kb-query\|kb-compile' plugins/` returns nothing
- [ ] `learnings` is removed; its unique behavior lives in `kb:learn-recall`
- [ ] Both skills pass create-skill validation

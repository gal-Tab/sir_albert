# 05 — Rename the KB plugin to `kb`

**Blocked by:** 03, 04
**Spec:** §4

## Steps
1. `plugins/kb/.claude-plugin/plugin.json`: `"name": "kb"`. Keep the version and bump the minor version.
2. Check whether KB code hardcodes its name or install path: `grep -rn 'llm-wiki-agent\|llm-wiki-agent-dev' plugins/kb`. Hooks should use `${CLAUDE_PLUGIN_ROOT}`. Fix hardcoded names and re-run pytest.
3. Repo references: `grep -rln 'llm-wiki-agent' --exclude-dir=.git --exclude-dir=.memory-bank --exclude-dir=docs .`. Known hits:
   - `REGISTRY.md`, `plugins/sir-albert/os/RESOLVER.md`: edit directly
   - `plugins/sir-albert/skills/core/learnings/SKILL.md`: handled in ticket 06, skip here
   - `plugins/sir-albert/skills/packs/build/build-discipline/SKILL.md`: via `/sir-albert:create-skill`. Also replace its stale `kb-query` with `kb:wiki-query`.
   - `.claude/settings.local.json`: `Skill(llm-wiki-agent:kb-query)` → `Skill(kb:wiki-query)`
4. Map old names to new: `llm-wiki-agent:kb-query` / `wiki-query` → `kb:wiki-query`; `kb-compile` / `wiki-compile` → `kb:wiki-compile`; `kb-init` / `wiki-init` → `kb:wiki-init`; `learn-*` → `kb:learn-*`.
5. Commit: `refactor(kb): rename plugin llm-wiki-agent → kb`.

## DOD
- [ ] The grep in step 3 returns only ticket-06 files
- [ ] pytest in `plugins/kb` still passes

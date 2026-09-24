# 10 — /sir-albert:init skill

**Blocked by:** 01
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 6

## Goal

Create `/sir-albert:init` via the full `/sir-albert:create-skill` loop. Tier T1 (not a discipline skill).

## Steps

1. Run `/sir-albert:create-skill` to scaffold the skill. When prompted for metadata:
   - **Slug:** `init`
   - **Tier:** T1
   - **Path:** `plugins/sir-albert/skills/core/init/`
   - **Trigger:** `"set up this project"`, `"/sir-albert:init"`
   - **One-liner:** "Scaffold docs/specs/, docs/plans/, .memory-bank/, project CLAUDE.md stub; report detected packs."
2. In the SKILL.md, implement the logic:
   - Boot from `os/PREAMBLE.md`
   - Idempotency check: for each target path, `test -d <path> || mkdir <path>` (report "created" vs "already exists" for each)
   - Paths: `docs/specs/`, `docs/plans/`, `.memory-bank/`
   - Project CLAUDE.md stub: if `CLAUDE.md` absent at project root, write a 5-line stub (pointer to RESOLVER.md, placeholder for project context)
   - KB detection: if `--kb` flag passed or `raw/` directory exists, call `kb:wiki-init`
   - Pack report: run the same detection logic as `session-start.sh` (read `router-data.json` signals) and list which packs will activate for this project
   - Emit a structured report: created / already-existed / packs detected
3. Verify idempotency: run `/sir-albert:init` twice in the same project — second run should report "already exists" for all paths, not recreate.

## Definition of Done

- [ ] SKILL.md created via `/sir-albert:create-skill` (full loop, passes create-skill gate)
- [ ] Idempotent: second run does not overwrite existing dirs or CLAUDE.md
- [ ] Pack report matches what `session-start.sh` would inject
- [ ] `--kb` flag triggers `kb:wiki-init`
- [ ] Skill registered in plugin manifest / skills registry

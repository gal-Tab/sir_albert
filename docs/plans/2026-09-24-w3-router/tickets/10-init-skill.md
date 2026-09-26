# 10 — /sir-albert:init skill (project-level only)

**Blocked by:** 01
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 6

## Goal

Create `/sir-albert:init` via the full `/sir-albert:create-skill` loop. **Project-level only** — never touches machine config (that is `bootstrap.sh`, ticket 09).

## Steps

1. Run `/sir-albert:create-skill`:
   - Slug: `init`
   - Tier: T1 (not a discipline skill)
   - Path: `plugins/sir-albert/skills/core/init/`
   - Trigger phrases: `"set up this project"`, `"/sir-albert:init"`
   - One-liner: "Scaffold docs/specs/, docs/plans/, .memory-bank/, project CLAUDE.md stub; report detected packs."
2. SKILL.md content:
   - Boot from `os/PREAMBLE.md`
   - Idempotency: for each target path, check existence before creating; report "created" vs "already exists"
   - Paths: `docs/specs/`, `docs/plans/`, `.memory-bank/`
   - Project CLAUDE.md stub at project root (only if absent): 5 lines — project name, pointer to `os/RESOLVER.md`, placeholder context comment
   - KB: if `--kb` flag or `raw/` exists → call `kb:wiki-init`
   - Pack report: load `router_data.json` pack signals, probe `$PWD`, list which packs will activate
   - Emit structured report: table of created/already-existed + "Active packs: X"
3. Verify idempotency: run `/sir-albert:init` twice in the same project — second run must show "already exists" for all paths, no overwrites.

## Definition of Done

- [ ] SKILL.md created via `/sir-albert:create-skill` (full loop, passes create-skill gate)
- [ ] Never creates dirs or stub CLAUDE.md in `~/.claude` or any machine-level path
- [ ] Idempotent on second run
- [ ] Pack report matches what `session_start.py` would inject for this project
- [ ] `--kb` flag triggers `kb:wiki-init`

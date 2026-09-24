# 04 — Move sir-albert into plugins/sir-albert/

**Blocked by:** 01
**Spec:** §3

## Rules
- Skill files (`SKILL.md`) are edited **only through `/sir-albert:create-skill`**. For one-line path fixes, invoke it and use its lightest edit path. If it insists on a full evaluation loop for a path change, stop and ask the coordinator.
- Moves use `git mv` only.

## Steps
1. `git mv .claude-plugin/plugin.json plugins/sir-albert/.claude-plugin/plugin.json` (create the dir first). Then `git mv skills hooks os tools shared plugins/sir-albert/`.
2. Edit `plugins/sir-albert/.claude-plugin/plugin.json`: remove the `"./skills/knowledge"` entry and delete the `skills/knowledge/` dir (it holds only a README). Skill paths stay `./skills/...`, now relative to the plugin root.
3. Create the root `.claude-plugin/marketplace.json`, based on the schema in `plugins/kb/.claude-plugin/marketplace.json`:
   - marketplace `name: "sir-albert"`, owner gal-Tab
   - plugins: `{ "name": "sir-albert", "source": "./plugins/sir-albert" }`, `{ "name": "kb", "source": "./plugins/kb" }`
   - Delete `plugins/kb/.claude-plugin/marketplace.json` (one marketplace only).
4. Find references to the old paths: `grep -rn '/Users/galta/Development/sir_albert/\(hooks\|os\|skills\|shared\|tools\)' --exclude-dir=.git --exclude-dir=.memory-bank --exclude-dir=docs .` Known hits:
   - `plugins/sir-albert/hooks/launchd/com.sir-albert.{retro,wiki}.plist` (repo copies) → `…/sir_albert/plugins/sir-albert/hooks/cron-*.sh`
   - `plugins/sir-albert/hooks/hooks.json` (untracked) → fallback path `…/sir_albert/plugins/sir-albert`
   - `plugins/sir-albert/skills/core/freeze/SKILL.md:62`, `plugins/sir-albert/skills/core/retro/SKILL.md:88,95` → via create-skill
5. Check the scripts for repo-root assumptions: `grep -n 'dirname\|\.\./\|REPO\|ROOT' plugins/sir-albert/hooks/*.sh plugins/sir-albert/tools/* 2>/dev/null`. `cron-wiki.sh` / `cron-retro.sh` / `session-record.sh` may `cd` to the repo root to reach `raw/`, `wiki/` or `.memory-bank/`. Those must still resolve to the **repo root** (`/Users/galta/Development/sir_albert`), not the plugin dir.
6. Relative refs inside skills (e.g. html-plans `../../../shared/references/…`) stay valid because `shared/` moved alongside. Verify with `ls plugins/sir-albert/shared/references/design-tokens.md`.
7. Update the path mentions in `REGISTRY.md` and `plugins/sir-albert/os/RESOLVER.md` (not skills, so edit directly).
8. Commit: `refactor: move sir-albert plugin into plugins/sir-albert (W1)`.

## DOD
- [ ] Repo root contains only: `.claude-plugin/marketplace.json`, `plugins/`, `raw/`, `wiki/`, `wiki-schema.md`, `docs/`, `.memory-bank/`, `README.md`, `REGISTRY.md`, `HANDOFF.md`, dotfiles
- [ ] The grep in step 4 returns nothing
- [ ] `python3 -c "import json;json.load(open('.claude-plugin/marketplace.json'))"` passes, and so does the same for `plugin.json`
- [ ] Every path listed in `plugin.json` "skills" exists

**⚠️ Risk:** scripts that locate the repo from their own location (`dirname $0/..`) will now land in `plugins/sir-albert`. Step 5 catches this.

# 07 — Install switch on this machine

**Blocked by:** 02, 04, 05, 06
**Spec:** §6
**CHECKPOINT:** this changes live `~/.claude` config. **Ask the coordinator before starting**, and report after each numbered step.

## Steps
1. Backup: `mkdir -p ~/.claude/backups/w1 && cp ~/.claude/settings.json ~/.claude/CLAUDE.md ~/.claude/plugins/installed_plugins.json ~/.claude/plugins/known_marketplaces.json ~/.claude/backups/w1/`, and save the output of `readlink ~/.claude/skills/sir-albert` to `~/.claude/backups/w1/symlink.txt`. Also copy `~/Library/LaunchAgents/com.sir-albert.*.plist`.
2. `rm ~/.claude/skills/sir-albert` (removes the symlink only; the target stays).
3. **Decision (Gal, 2026-09-24): this machine loads the plugins live via `--plugin-dir`, not via a marketplace install** (spike 02 showed that installs are cache copies). So:
   - Do **not** `claude plugin install` sir-albert or kb here, because a live load plus an installed copy would load them twice.
   - Add to `~/.zshrc`: `alias claude='claude --plugin-dir /Users/galta/Development/sir_albert/plugins'` (a plugins folder loads each child). Show the line to the coordinator before appending.
   - Launchd cron scripts (`plugins/sir-albert/hooks/cron-*.sh`) don't read `.zshrc`. If they call `claude`, add the same `--plugin-dir` flag inside the script.
   - The marketplace (`.claude-plugin/marketplace.json`) stays in the repo for new machines. Document the install in `README.md`: `claude plugin marketplace add <repo>` + `claude plugin install sir-albert@sir-albert kb@sir-albert`.
4. `claude plugin uninstall llm-wiki-agent@llm-wiki-agent-dev` and `claude plugin marketplace remove llm-wiki-agent-dev`.
5. `~/.claude/settings.json` edits (show the diff to the coordinator before saving):
   - hooks: 4 commands `/Users/galta/Development/sir_albert/hooks/{validate-skill.py (×2), freeze-guard.sh, session-record.sh}` → `…/sir_albert/plugins/sir-albert/hooks/…`
   - permissions: `Skill(llm-wiki-agent:kb-compile)` → `Skill(kb:wiki-compile)`. The 4 stale `cp …/llm-wiki-agent/0.1.0/…` permission lines (119–122) → remove.
   - enabledPlugins: remove `llm-wiki-agent@llm-wiki-agent-dev`. Don't add sir-albert or kb here (they load through `--plugin-dir`).
   - extraKnownMarketplaces: remove the `llm-wiki-agent-dev` block (it points to gal-Tab/agent_knowledgebase).
6. `~/.claude/CLAUDE.md` lines 45–46: `@/Users/galta/Development/sir_albert/os/identity/…` → `@/Users/galta/Development/sir_albert/plugins/sir-albert/os/identity/…`.
7. Launchd: update the `ProgramArguments` path in `~/Library/LaunchAgents/com.sir-albert.{retro,wiki}.plist` to `plugins/sir-albert/hooks/cron-*.sh` (match the repo copies from ticket 04). Then run `launchctl bootout gui/$(id -u) <plist>` followed by `launchctl bootstrap gui/$(id -u) <plist>` for each.
8. Other projects using the KB (e.g. `/Users/galta/Development/gtm_agent`): `grep -rn 'llm-wiki-agent' /Users/galta/Development/gtm_agent --include='*.md' --include='*.json' 2>/dev/null`. Report the hits to the coordinator and don't edit other repos.

## Rollback
Copy the backups back, `ln -s /Users/galta/Development/sir_albert ~/.claude/skills/sir-albert`, re-add the `llm-wiki-agent-dev` marketplace from `https://github.com/gal-Tab/agent_knowledgebase.git` and reinstall. Bootstrap the old plists again.

## DOD
- [ ] Backups exist in `~/.claude/backups/w1/`
- [ ] `installed_plugins.json` has no `llm-wiki-agent`, `sir-albert` or `kb`; `~/.zshrc` has the `--plugin-dir` alias
- [ ] No symlink at `~/.claude/skills/sir-albert`
- [ ] `grep -n 'sir_albert/\(hooks\|os\)/' ~/.claude/settings.json ~/.claude/CLAUDE.md ~/Library/LaunchAgents/com.sir-albert.*.plist` returns nothing

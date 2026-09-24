# 02 — Spike: how does a local-directory marketplace behave?

**Blocked by:** —
**Throwaway:** everything lives in `/tmp/w1-spike`; delete it when done.

## Question
Today sir-albert loads through the `~/.claude/skills/sir-albert` symlink, so edits in the repo are **live**. After the switch, plugins install from a local-directory marketplace. Does Claude Code copy them into `~/.claude/plugins/cache/` (edits need `claude plugin update`), or read them in place?

This decides the edit loop in ticket 07. The goal "one place to edit" must hold.

## Steps
1. Check `claude plugin --help` and `claude plugin marketplace --help` for commands and flags. Also check whether `--plugin-dir` exists.
2. Create `/tmp/w1-spike/.claude-plugin/marketplace.json` listing one plugin `w1-spike` at `./plugins/w1-spike`, with one skill `hello` whose description is "say SPIKE-V1".
3. `claude plugin marketplace add /tmp/w1-spike` → `claude plugin install w1-spike@<marketplace-name>`.
4. Inspect `~/.claude/plugins/installed_plugins.json` for the `installPath`: is it the cache or `/tmp/w1-spike`?
5. Edit the skill to "SPIKE-V2". Run `claude -p "list your skills whose name contains w1-spike, quote the description"`. Is V2 visible without an update?
6. Clean up: uninstall the plugin, remove the marketplace, `rm -r /tmp/w1-spike`.

## Output
Write 5 lines to `docs/plans/2026-09-24-w1-repo-merge/spike-02-result.md`: install path, whether edits are live, the update command needed, and the recommended edit loop (e.g. "edit → `claude plugin update sir-albert@sir-albert`", or "live in place").

## DOD
- [ ] Result file written
- [ ] Spike plugin and marketplace fully removed (`installed_plugins.json` and `known_marketplaces.json` have no `w1-spike`)

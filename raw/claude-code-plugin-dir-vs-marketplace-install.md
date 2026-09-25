---
title: "Claude Code plugin loading: --plugin-dir (live) vs marketplace install (cached copy)"
type: concept
kw_capture: true
kw_date: 2026-09-25
tags: [claude-code, plugins, marketplace, dev-loop, sir-albert]
source_refs: []
created: 2026-09-25
updated: 2026-09-25
---

# Claude Code plugin loading: --plugin-dir (live) vs marketplace install (cached copy)

## Definition
Claude Code has two ways to load a plugin, and they behave differently when you edit it:
- **Marketplace install** (`claude plugin marketplace add <path|url>` + `claude plugin install <plugin>@<marketplace>`) **copies** the plugin into `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`. Editing the source has no effect. To pick up changes you bump `version` in `plugin.json` (and `marketplace.json`), run `claude plugin marketplace update` + `claude plugin update`, then restart. A same-version update returns "already at latest".
- **`claude --plugin-dir <path>`** loads a plugin **in place for that session**. When `<path>` is a folder of plugins, it loads **each child** (repeatable flag). Edits are live at the next session start, hooks included.

## Context
Measured in a throwaway spike (2026-09-24) while merging sir_albert and agent_knowledgebase into one repo with two plugins. Chosen setup: a shell alias `claude='claude --plugin-dir ~/Development/sir_albert/plugins'` on the dev machine (live edits, no install, so nothing loads twice), and the repo marketplace for new machines.
Consequences:
- **The working tree is live.** Unmerged branch work (hooks, skills) runs in every new session. A hooks.json wired on a feature branch made two hooks fire twice until the settings.json duplicates were removed.
- **Aliases don't reach every surface.** They don't apply to the desktop app, IDE extensions, or non-interactive shells (cron/launchd, agent Bash calls). Those need the flag passed explicitly, or they won't load the plugin.
- **Wrappers pass the flag through.** A wrapper binary such as axcli's `claude` forwards the flag, but verify it rather than assume.
- **Running sessions don't pick it up.** Plugins load at session start. `/reload-plugins` refreshes installed plugins; for `--plugin-dir`, restart with `claude --continue`.

## Related Concepts
- Keep hook scripts using `${CLAUDE_PLUGIN_ROOT}` so the same plugin works under both loading modes.

## See Also
- (no existing wiki pages on this topic)

## Source / Origin
Captured from session on 2026-09-25. Emerged from W1 of the sir_albert restructure (spike-02 result + install switch + live double-fire incident).

# Spike 02 — Local Marketplace Behavior

**install path:** `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` — files are **copied** into the cache at install time, NOT read in place.

**edits live?:** No. Editing source files in the original directory has no effect on the running plugin.

**update command:** `claude plugin marketplace update <marketplace-name>` then `claude plugin update <plugin>@<marketplace>` — but update only triggers if the version string in `plugin.json` (and `marketplace.json`) is bumped; same version returns "already at latest."

**recommended edit loop:** edit files → bump version in `plugins/<name>/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` → `claude plugin marketplace update sir-albert && claude plugin update sir-albert@sir-albert && claude plugin update kb@sir-albert` — then restart Claude Code to apply.

**impact on ticket 07:** "one place to edit" requires a version bump + update step after each change. The old symlink-live workflow is replaced by: edit → bump patch version → `plugin marketplace update` + `plugin update` → restart.

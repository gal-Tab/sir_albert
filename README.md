# Sir Albert

Gal's personal operating system for Claude Code — one repo, two plugins: `sir-albert` (skills) and `kb` (knowledge base).

## Layout

```
sir_albert/
  .claude-plugin/marketplace.json   # lists both plugins
  plugins/
    sir-albert/                     # skills library
      .claude-plugin/plugin.json
      skills/  hooks/  os/  tools/  shared/
    kb/                             # knowledge base engine
      .claude-plugin/plugin.json    # name: "kb"
      commands/ skills/ hooks/ lib/ tools/ templates/ tests/
  raw/  wiki/  wiki-schema.md       # KB data for this repo
  docs/  .memory-bank/  README.md  REGISTRY.md
```

## Loading (this machine)

Plugins load **live** via `--plugin-dir` (no cache copy; edits take effect immediately):

```bash
# ~/.zshrc alias (active)
alias claude='claude --plugin-dir /Users/galta/Development/sir_albert/plugins'
```

Every skill is namespaced: `/sir-albert:<skill-name>` or `/kb:<skill-name>`. See [`REGISTRY.md`](REGISTRY.md) for the full index.

## Loading (new machine)

```bash
claude plugin marketplace add /path/to/sir_albert
claude plugin install sir-albert@sir-albert
claude plugin install kb@sir-albert
```

Then add the `--plugin-dir` alias to `~/.zshrc` for live edits, or rely on `claude plugin update` after each version bump.

## Knowledge Base pipeline

```
raw/ (source drop zone)
  ↓  /kb:wiki-compile
wiki/ (sources/ · entities/ · concepts/ · comparisons/)
  ↑  /kb:wiki-query reads     /kb:kw-compound writes back to raw/
```

See [`REGISTRY.md`](REGISTRY.md#knowledge--knowledge-management) for skill trigger phrases.

## Adding a new skill

1. Create `plugins/sir-albert/skills/<category>/<skill-name>/SKILL.md`
2. Add frontmatter: `name`, `description` (trigger conditions), optionally `allowed-tools`
3. Add a row to [`REGISTRY.md`](REGISTRY.md)
4. Restart Claude Code (live load via `--plugin-dir` picks it up immediately)

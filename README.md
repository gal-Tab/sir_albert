# Sir Albert

This repo is dedicated to one thing: the **`sir-albert` Claude Code plugin** — Gal's personal skills library and knowledge-base pipeline. There's no separate packaging step; the repo *is* the plugin, loaded live from this directory.

## Two Layers

| Layer | What it is | Where it lives |
|---|---|---|
| **Skills** | Reusable Claude Code behaviors and workflows, shipped by the plugin | `skills/<category>/<name>/` |
| **Knowledge Base** | Structured wiki compiled from raw sources, queried/written by the plugin's skills | `raw/` → `wiki/` |

---

## Skills

18 skills organized into 5 categories. See [`REGISTRY.md`](REGISTRY.md) for the full index with trigger phrases.

| Category | Skills |
|---|---|
| `agentic` | self-reflection, kw-compound |
| `dev` | git-guardrails, github-repo-analyzer, grill-with-docs, grilling, domain-modeling, prototype, claude-handoff |
| `docs` | html-plans, to-prd |
| `knowledge` | kb-query |
| `biz` | board-of-advisors, devils-advocate, zoom-out, monday-mops-triage, slack-in-my-voice, linkedin-in-my-voice |

### Loading the plugin

This repo *is* the `sir-albert` Claude Code plugin (`.claude-plugin/plugin.json` at the root). It loads as a **skills-directory plugin**: symlinked at `~/.claude/skills/sir-albert` → this repo, so it's picked up automatically every session with no install step, as `sir-albert@skills-dir`.

Every skill is namespaced: `/sir-albert:<skill-name>` — e.g. `/sir-albert:grill-with-docs`, `/sir-albert:kb-query`. The category folder (`agentic`, `dev`, ...) is just an on-disk grouping declared via the `skills` field in `plugin.json`; it doesn't appear in the command name.

If the symlink is ever missing, recreate it with:
```bash
ln -s "$(pwd)" ~/.claude/skills/sir-albert
```

### Adding a new skill

1. Create `skills/<category>/<skill-name>/SKILL.md`
2. Add frontmatter: `name`, `description` (trigger conditions), optionally `allowed-tools`
3. Add a row to the relevant table in `REGISTRY.md`
4. Run `/reload-plugins` (or start a new session) to pick it up

---

## Knowledge Base

Managed via the [LLM Wiki Agent](https://github.com/gal-Tab/agent_knowledgebase) plugin.

- `raw/` — Drop raw source files here (PDFs, Markdown, text, etc.)
- `wiki/` — Compiled, structured knowledge base (sources, entities, concepts, comparisons)
- `wiki-schema.md` — Domain rules and page type definitions — edit to guide compilation
- `tools/` — Extraction scripts used during compilation

### Knowledge pipeline

```
raw/ (source drop zone)
  ↓  /kb-compile
wiki/ (sources/ · entities/ · concepts/ · comparisons/)
  ↑  /sir-albert:kb-query reads     /sir-albert:kw-compound writes back to raw/
```

### Usage

1. Drop files into `raw/`
2. Run `/kb-compile` — agents extract and structure them into `wiki/`
3. Ask questions — `/sir-albert:kb-query` answers with citations from `wiki/`
4. Capture session insights — `/sir-albert:kw-compound` files them back to `raw/` for the next compile

---

## Repo Structure

```
sir_albert/
├── .claude-plugin/
│   └── plugin.json      — plugin manifest (name: sir-albert, declares the 5 skill-root folders)
├── REGISTRY.md          — full skill index with trigger phrases
├── wiki-schema.md       — domain config for kb-compile
├── raw/                 — source file drop zone
├── wiki/                — compiled knowledge base
├── docs/
│   ├── plans/           — generated HTML implementation plans (html-plans skill)
│   └── prds/            — generated HTML PRDs (to-prd skill)
├── shared/
│   └── references/      — shared design assets for docs skills
├── skills/
│   ├── agentic/         — meta-cognitive & knowledge-capture skills
│   ├── dev/             — engineering workflow skills
│   ├── docs/            — document generation skills
│   ├── knowledge/       — knowledge base query skills
│   └── biz/             — business decision-making & process skills
└── tools/               — knowledge-base extraction scripts
```

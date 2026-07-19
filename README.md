# Sir Albert

Personal AI assistant configuration for **Gal** — a skills library and structured knowledge base, managed as a single source of truth and published to Claude Code.

## Two Layers

| Layer | What it is | Where it lives |
|---|---|---|
| **Skills** | Reusable Claude Code behaviors and workflows | `skills/<category>/<name>/` |
| **Knowledge Base** | Structured wiki compiled from raw sources | `raw/` → `wiki/` |

---

## Skills

13 skills organized into 5 categories. See [`REGISTRY.md`](REGISTRY.md) for the full index with trigger phrases.

| Category | Skills |
|---|---|
| `agentic` | self-reflection, kw-compound |
| `dev` | git-guardrails, github-repo-analyzer |
| `docs` | html-plans, to-prd |
| `knowledge` | kb-query |
| `biz` | board-of-advisors, devils-advocate, zoom-out, monday-mops-triage, slack-in-my-voice, linkedin-in-my-voice |

### Publishing skills to Claude Code

Skills in this repo are the source of truth. To make them available in Claude Code sessions, publish them to `~/.claude/skills/`:

```bash
tools/publish-skills.sh --all          # publish all skills
tools/publish-skills.sh html-plans     # publish a single skill
```

### Adding a new skill

1. Create `skills/<category>/<skill-name>/SKILL.md`
2. Add frontmatter: `name`, `description` (trigger conditions), optionally `allowed-tools`
3. Add a row to the relevant table in `REGISTRY.md`
4. Run `tools/publish-skills.sh <skill-name>`

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
  ↑  /kb-query reads     /kw-compound writes back to raw/
```

### Usage

1. Drop files into `raw/`
2. Run `/kb-compile` — agents extract and structure them into `wiki/`
3. Ask questions — `/kb-query` answers with citations from `wiki/`
4. Capture session insights — `/kw-compound` files them back to `raw/` for the next compile

---

## Repo Structure

```
sir_albert/
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
└── tools/
    └── publish-skills.sh  — sync skills → ~/.claude/skills/
```

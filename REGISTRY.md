# Sir Albert — Skill Registry

All skills in this repo, organized by category. Each skill is a folder containing a `SKILL.md` that Claude Code loads.

This repo is the `sir-albert` Claude Code plugin (see `.claude-plugin/plugin.json`), loaded via a symlink at `~/.claude/skills/sir-albert`. Every skill below is invoked namespaced: `/sir-albert:<skill-name>` (the category column below is just the on-disk folder — it isn't part of the command name).

---

## agentic — Meta-Cognitive & Knowledge Capture

Skills for improving agent behavior and capturing what a session learns back into the knowledge base.

| Skill | Path | Trigger phrases |
|---|---|---|
| self-reflection | `skills/agentic/self-reflection/` | "improve your behavior", "reflect on this", periodic self-audit |
| kw-compound | `skills/agentic/kw-compound/` | "save this to the wiki", "file this knowledge", "compound this session" |

---

## dev — Engineering Workflow

Skills for software development tasks, code safety, and repo analysis.

| Skill | Path | Trigger phrases |
|---|---|---|
| git-guardrails | `skills/dev/git-guardrails/` | "set up git safety", "install git hooks", "block dangerous git" |
| github-repo-analyzer | `skills/dev/github-repo-analyzer/` | "analyze this repo", "check this GitHub link", repo status |
| grill-with-docs | `skills/dev/grill-with-docs/` | "grill this with docs" — relentless interview to sharpen a plan/design, writing ADRs and glossary as it goes |
| grilling | `skills/dev/grilling/` | "grill me", "stress-test my thinking", "interview me about this" |
| domain-modeling | `skills/dev/domain-modeling/` | "pin down this terminology", "record an architectural decision", "build the domain model" |
| prototype | `skills/dev/prototype/` | "build a prototype", "sanity-check this state model", "throwaway prototype", "what should this UI look like" |
| claude-handoff | `skills/dev/claude-handoff/` | "hand this off", "spin up a background agent", "continue this in the background", "hand off to claude" |

Ported from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT License) — see `skills/dev/THIRD_PARTY_NOTICES.md`. `grill-with-docs` depends on `grilling` and `domain-modeling`. `claude-handoff` was adapted: it now asks which mode (execution vs. plan/discovery) and which model to use before launching, and maps mode to the `claude` CLI's `--permission-mode bypassPermissions` / `--permission-mode plan`.

---

## docs — Document Generation

Skills that generate interactive HTML documents (plans, specs, PRDs).

| Skill | Path | Trigger phrases |
|---|---|---|
| html-plans | `skills/docs/html-plans/` | "write a plan", "implementation steps", "plan this feature" |
| to-prd | `skills/docs/to-prd/` | "write a PRD", "create a spec", "document this feature" |
| monday-presentation-v2 | `skills/docs/monday-presentation-v2/` | "create a presentation", "build slides", "make a deck", "slide deck with monday branding" |
| monday-brand-guidelines | `skills/docs/monday-brand-guidelines/` | "monday brand", "apply monday colors", "monday design identity", monday branding for HTML/charts/marketing/UI |

Shared design system: `shared/references/design-tokens.md` and `shared/references/mermaid-patterns.md`

---

## knowledge — Knowledge Management

Skills for querying the sir_albert wiki knowledge base.

| Skill | Path | Trigger phrases |
|---|---|---|
| kb-query | `skills/knowledge/kb-query/` | "what do I know about X", "check my wiki", domain questions |

### Knowledge Pipeline

`/kw-compound` (the write side of this loop) lives under `skills/agentic/` but feeds the same pipeline:

```
raw/ (source drop zone)
  ↓  /kb-compile
wiki/ (structured pages: sources/, entities/, concepts/, comparisons/)
  ↑  /kb-query reads        (skills/knowledge/)
  ↑  /kw-compound writes back to raw/   (skills/agentic/)
```

---

## biz — Business Decision-Making & Process

Skills for business reasoning, decision-making, and work-management integrations.

| Skill | Path | Trigger phrases |
|---|---|---|
| discovery-lens | `skills/biz/discovery-lens/` | "brainstorm this", "let's explore", "help me think through X", "sharpen this idea", "attack this idea", "what are we missing", "WDYT", "fresh perspective", "discovery phase", "AI-first perspective" |
| board-of-advisors | `skills/biz/board-of-advisors/` | "board of advisors", "4 perspectives", "multiple viewpoints" |
| devils-advocate | `skills/biz/devils-advocate/` | "play devil's advocate", "stress test this", "challenge my idea" |
| zoom-out | `skills/biz/zoom-out/` | "zoom out", "bigger picture", "how does this fit" |
| monday-mops-triage | `skills/biz/monday-mops-triage/` | "add a task to MOPs", "open a ticket", "put this in the iteration" |
| slack-in-my-voice | `skills/biz/slack-in-my-voice/` | "send a Slack", "draft a slack message", "write this for slack" |
| linkedin-in-my-voice | `skills/biz/linkedin-in-my-voice/` | "write a LinkedIn post", "draft a linkedin post", "כתוב פוסט ללינקדאין" |

---

## packs — Domain Packs

Skills for specific technology domains and platforms.

| Skill | Path | Trigger phrases |
|---|---|---|
| ga4-regex | `skills/packs/gtm/ga4-regex/` | "GA4 regex", "regex for page_path", "match these URLs", "exclude this campaign", "RE2", "why doesn't my regex match in GA4", GA4/GTM + regex/pattern/match/exclude/filter |
| monday-data-viz-vibe | `skills/packs/data/monday-data-viz-vibe/` | monday charts/dashboards in Python (Plotly/Matplotlib), Streamlit, or Tableau with Vibe design system; typography (Figtree), monday color palettes |

---

## Shared Assets

| File | Used by |
|---|---|
| `shared/references/design-tokens.md` | html-plans, to-prd |
| `shared/references/mermaid-patterns.md` | html-plans, to-prd |

---

## Adding a New Skill

1. Pick the right category folder (`agentic`, `dev`, `docs`, `knowledge`, `biz`)
2. Create `skills/<category>/<skill-name>/SKILL.md`
3. Add frontmatter: `name`, `description` (trigger conditions), optionally `allowed-tools`
4. Add an entry to this REGISTRY.md
5. Run `/reload-plugins` (or start a new Claude Code session) to pick it up as `/sir-albert:<skill-name>`

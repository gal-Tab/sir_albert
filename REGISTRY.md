# Sir Albert — Skill Registry

All skills in this repo, organized by category. Each skill is a folder containing a `SKILL.md` that Claude Code loads.

This repo is the `sir-albert` Claude Code plugin (see `plugins/sir-albert/.claude-plugin/plugin.json`). Skills are invoked namespaced: `/sir-albert:<skill-name>` (the category column below is just the on-disk folder — it isn't part of the command name).

---

## agentic — Meta-Cognitive & Knowledge Capture

Skills for improving agent behavior and capturing what a session learns back into the knowledge base.

| Skill | Path | Trigger phrases |
|---|---|---|
| self-reflection | `plugins/sir-albert/skills/agentic/self-reflection/` | "improve your behavior", "reflect on this", periodic self-audit |
| kw-compound | `plugins/sir-albert/skills/agentic/kw-compound/` | "save this to the wiki", "file this knowledge", "compound this session" |

---

## dev — Engineering Workflow

Skills for software development tasks, code safety, and repo analysis.

| Skill | Path | Trigger phrases |
|---|---|---|
| git-guardrails | `plugins/sir-albert/skills/dev/git-guardrails/` | "set up git safety", "install git hooks", "block dangerous git" |
| github-repo-analyzer | `plugins/sir-albert/skills/dev/github-repo-analyzer/` | "analyze this repo", "check this GitHub link", repo status |
| grill-with-docs | `plugins/sir-albert/skills/dev/grill-with-docs/` | "grill this with docs" — relentless interview to sharpen a plan/design, writing ADRs and glossary as it goes |
| grilling | `plugins/sir-albert/skills/dev/grilling/` | "grill me", "stress-test my thinking", "interview me about this" |
| domain-modeling | `plugins/sir-albert/skills/dev/domain-modeling/` | "pin down this terminology", "record an architectural decision", "build the domain model" |
| prototype | `plugins/sir-albert/skills/dev/prototype/` | "build a prototype", "sanity-check this state model", "throwaway prototype", "what should this UI look like" |
| claude-handoff | `plugins/sir-albert/skills/dev/claude-handoff/` | "hand this off", "spin up a background agent", "continue this in the background", "hand off to claude" |

Ported from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT License) — see `plugins/sir-albert/skills/dev/THIRD_PARTY_NOTICES.md`. `grill-with-docs` depends on `grilling` and `domain-modeling`. `claude-handoff` was adapted: it now asks which mode (execution vs. plan/discovery) and which model to use before launching, and maps mode to the `claude` CLI's `--permission-mode bypassPermissions` / `--permission-mode plan`.

---

## docs — Document Generation

Skills that generate interactive HTML documents (plans, specs, PRDs).

| Skill | Path | Trigger phrases |
|---|---|---|
| html-plans | `plugins/sir-albert/skills/docs/html-plans/` | "write a plan", "implementation steps", "plan this feature" |
| to-prd | `plugins/sir-albert/skills/docs/to-prd/` | "write a PRD", "create a spec", "document this feature" |
| monday-presentation-v2 | `plugins/sir-albert/skills/docs/monday-presentation-v2/` | "create a presentation", "build slides", "make a deck", "slide deck with monday branding" |
| monday-brand-guidelines | `plugins/sir-albert/skills/docs/monday-brand-guidelines/` | "monday brand", "apply monday colors", "monday design identity", monday branding for HTML/charts/marketing/UI |

Shared design system: `plugins/sir-albert/shared/references/design-tokens.md` and `plugins/sir-albert/shared/references/mermaid-patterns.md`

---

## knowledge — Knowledge Management

Knowledge is **inherited, not forked** — the canonical engine is the `kb` plugin.

| Query (via kb) | Pipeline commands |
|---|---|
| `wiki-query` · `learn-recall` · `learn-research` | `/wiki-init` · `/wiki-compile` · `/learn-capture` |

> The legacy `kb-query` fork is **retired and deleted** — superseded by `kb:wiki-query`.

### Knowledge Pipeline

`/kw-compound` (the write side of this loop) lives under `plugins/sir-albert/skills/agentic/` but feeds the same pipeline:

```
raw/ (source drop zone)
  ↓  /wiki-compile          (kb)
wiki/ (structured pages: sources/, entities/, concepts/, comparisons/)
  ↑  wiki-query reads       (kb)
  ↑  /kw-compound writes back to raw/   (plugins/sir-albert/skills/agentic/)
```

---

## biz — Business Decision-Making & Process

Skills for business reasoning, decision-making, and work-management integrations.

| Skill | Path | Trigger phrases |
|---|---|---|
| discovery-lens | `plugins/sir-albert/skills/biz/discovery-lens/` | "brainstorm this", "let's explore", "help me think through X", "sharpen this idea", "attack this idea", "what are we missing", "WDYT", "fresh perspective", "discovery phase", "AI-first perspective" |
| board-of-advisors | `plugins/sir-albert/skills/biz/board-of-advisors/` | "board of advisors", "4 perspectives", "multiple viewpoints" |
| devils-advocate | `plugins/sir-albert/skills/biz/devils-advocate/` | "play devil's advocate", "stress test this", "challenge my idea" |
| zoom-out | `plugins/sir-albert/skills/biz/zoom-out/` | "zoom out", "bigger picture", "how does this fit" |
| monday-mops-triage | `plugins/sir-albert/skills/biz/monday-mops-triage/` | "add a task to MOPs", "open a ticket", "put this in the iteration" |
| slack-in-my-voice | `plugins/sir-albert/skills/biz/slack-in-my-voice/` | "send a Slack", "draft a slack message", "write this for slack" |
| linkedin-in-my-voice | `plugins/sir-albert/skills/biz/linkedin-in-my-voice/` | "write a LinkedIn post", "draft a linkedin post", "כתוב פוסט ללינקדאין" |

---

## core — OS skills

Domain-agnostic OS spine. Every core skill boots from `os/PREAMBLE.md`.

| Skill | Path | Trigger phrases |
|---|---|---|
| handoff | `plugins/sir-albert/skills/core/handoff/` | "hand this off", "write a handoff", "wrap this session", "prep to /clear" |
| resume | `plugins/sir-albert/skills/core/resume/` | "resume", "pick up where we left off", "load the handoff" |
| sync | `plugins/sir-albert/skills/core/sync/` | "sync", "are we in sync", "merged are we in sync", "post-merge cleanup" |
| decide | `plugins/sir-albert/skills/core/decide/` | "/decide", "we decided", "did we decide X before", "is this already decided" |
| discover | `plugins/sir-albert/skills/core/discover/` | "help me think through X", "let's explore", "which lens", "office hours" |
| freeze | `plugins/sir-albert/skills/core/freeze/` | "/freeze", "scope edits to", "/unfreeze" |
| retro | `plugins/sir-albert/skills/core/retro/` | "/retro", "self-improve skills", "review my corrections" |

Hooks (in `plugins/sir-albert/hooks/`, activated by adding to `~/.claude/settings.json` — see each skill): `freeze-guard.sh` (PreToolUse, for `/freeze`), `session-record.sh` (SessionEnd, for `/retro`).

---

## packs — Domain Packs

Skills for specific technology domains and platforms.

| Skill | Path | Trigger phrases |
|---|---|---|
| ga4-regex | `plugins/sir-albert/skills/packs/gtm/ga4-regex/` | "GA4 regex", "regex for page_path", "match these URLs", "exclude this campaign", "RE2", "why doesn't my regex match in GA4", GA4/GTM + regex/pattern/match/exclude/filter |
| monday-data-viz-vibe | `plugins/sir-albert/skills/packs/data/monday-data-viz-vibe/` | monday charts/dashboards in Python (Plotly/Matplotlib), Streamlit, or Tableau with Vibe design system; typography (Figtree), monday color palettes |
| param-audit | `plugins/sir-albert/skills/packs/gtm/param-audit/` | "/param-audit", "audit sGTM params", "check tag parameters", "is_desktop vs monday_is_desktop" |
| gtm-gate | `plugins/sir-albert/skills/packs/gtm/gtm-gate/` | "gtm-gate", "pre-apply check", "validate before apply", "check naming and consent" |
| build-discipline | `plugins/sir-albert/skills/packs/build/build-discipline/` | "build discipline", "how do I build X", "start a new dashboard/wiki/MCP/agent" |
| data-review | `plugins/sir-albert/skills/packs/data/data-review/` | "data-review", "check this dashboard before I share", "data quality check" |
| n8n-triage | `plugins/sir-albert/skills/packs/automation/n8n-triage/` | "/n8n-triage", "n8n execution failed", "debug this n8n run" |
| hubspot-safety | `plugins/sir-albert/skills/packs/automation/hubspot-safety/` | "hubspot safety", "check hubspot api", "hubspot v1 migration" |

---

## Shared Assets

| File | Used by |
|---|---|
| `plugins/sir-albert/shared/references/design-tokens.md` | html-plans, to-prd |
| `plugins/sir-albert/shared/references/mermaid-patterns.md` | html-plans, to-prd |

---

## Adding a New Skill

1. Pick the right category folder (`agentic`, `dev`, `docs`, `knowledge`, `biz`)
2. Create `plugins/sir-albert/skills/<category>/<skill-name>/SKILL.md`
3. Add frontmatter: `name`, `description` (trigger conditions), optionally `allowed-tools`
4. Add an entry to this REGISTRY.md
5. Run `/reload-plugins` (or start a new Claude Code session) to pick it up as `/sir-albert:<skill-name>`

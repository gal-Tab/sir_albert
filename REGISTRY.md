# Sir Albert — Skill Registry

All skills in this repo, organized by category. Each skill is a folder containing a `SKILL.md` that Claude Code loads.

To publish a skill to `~/.claude/skills/` (making it available in all sessions), run:
```bash
tools/publish-skills.sh <skill-name>     # publish one skill
tools/publish-skills.sh --all            # publish all skills in this repo
```

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

---

## docs — Document Generation

Skills that generate interactive HTML documents (plans, specs, PRDs).

| Skill | Path | Trigger phrases |
|---|---|---|
| html-plans | `skills/docs/html-plans/` | "write a plan", "implementation steps", "plan this feature" |
| to-prd | `skills/docs/to-prd/` | "write a PRD", "create a spec", "document this feature" |

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
| board-of-advisors | `skills/biz/board-of-advisors/` | "board of advisors", "4 perspectives", "multiple viewpoints" |
| devils-advocate | `skills/biz/devils-advocate/` | "play devil's advocate", "stress test this", "challenge my idea" |
| zoom-out | `skills/biz/zoom-out/` | "zoom out", "bigger picture", "how does this fit" |
| monday-mops-triage | `skills/biz/monday-mops-triage/` | "add a task to MOPs", "open a ticket", "put this in the iteration" |
| slack-in-my-voice | `skills/biz/slack-in-my-voice/` | "send a Slack", "draft a slack message", "write this for slack" |

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
5. Run `tools/publish-skills.sh <skill-name>` to make it available in Claude Code sessions

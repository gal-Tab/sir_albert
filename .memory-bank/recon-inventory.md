# Sir Albert Recon Inventory
Generated: 2026-07-31

---

## A. sir_albert repo (`/Users/galta/Development/sir_albert`)

### 1. `.claude-plugin/plugin.json`

```json
{
  "name": "sir-albert",
  "displayName": "Sir Albert",
  "description": "Gal's personal skills library and knowledge-base pipeline for Claude Code",
  "author": { "name": "gal-Tab" },
  "repository": "https://github.com/gal-Tab/sir_albert",
  "skills": [
    "./skills/agentic",
    "./skills/dev",
    "./skills/docs",
    "./skills/knowledge",
    "./skills/biz"
  ]
}
```

No `hooks`, `commands`, or `agents` keys. Only `skills` dirs declared.

---

### 2. `skills/` Tree — All Subdirectories + SKILL.md Presence

**agentic/**
| Skill | SKILL.md |
|---|---|
| kw-compound | YES |
| self-reflection | YES |

**biz/**
| Skill | SKILL.md |
|---|---|
| board-of-advisors | YES |
| brainstorm-council | YES |
| devils-advocate | YES |
| linkedin-in-my-voice | YES |
| monday-mops-triage | YES |
| slack-in-my-voice | YES |
| zoom-out | YES |

**dev/**
| Skill | SKILL.md |
|---|---|
| claude-handoff | YES |
| domain-modeling | YES |
| git-guardrails | YES |
| github-repo-analyzer | YES |
| grill-with-docs | YES |
| grilling | YES |
| prototype | YES |
| readme-svg-generator | YES |

**docs/**
| Skill | SKILL.md |
|---|---|
| html-plans | YES |
| to-prd | YES |

**knowledge/**
| Skill | SKILL.md |
|---|---|
| kb-query | YES |

All 20 skills have SKILL.md. No skills are missing it.

---

### 3. REGISTRY.md — Registered Skills

REGISTRY.md exists at `/Users/galta/Development/sir_albert/REGISTRY.md`.

**Total registered skills: 20** (across 5 categories)

| Category | Skills |
|---|---|
| agentic | self-reflection, kw-compound |
| dev | git-guardrails, github-repo-analyzer, grill-with-docs, grilling, domain-modeling, prototype, claude-handoff, readme-svg-generator |
| docs | html-plans, to-prd |
| knowledge | kb-query |
| biz | board-of-advisors, devils-advocate, zoom-out, monday-mops-triage, slack-in-my-voice, linkedin-in-my-voice |

---

### 4. Top-Level Directory Presence

| Dir | Present |
|---|---|
| `os/` | NO |
| `.memory-bank/` | YES (created by this recon) |
| `hooks/` | NO |
| `commands/` | NO |
| `shared/references/` | YES |

---

### 5. Specific Skill Locations

| Skill | Path | SKILL.md |
|---|---|---|
| Handoff skill (generalize to `/handoff`) | `skills/dev/claude-handoff/` | YES |
| `kb-query` (slated for deletion) | `skills/knowledge/kb-query/` | YES |
| `brainstorm-council` (to rename → discovery-lens) | `skills/biz/brainstorm-council/` | YES |
| `monday-mops-triage` | `skills/biz/monday-mops-triage/` | YES |
| `slack-in-my-voice` | `skills/biz/slack-in-my-voice/` | YES |
| `linkedin-in-my-voice` | `skills/biz/linkedin-in-my-voice/` | YES |
| `zoom-out` | `skills/biz/zoom-out/` | YES |

---

## B. Global / Local Claude Config

### 6. `~/.claude/settings.json` — Hooks

| Event | Command |
|---|---|
| `PreToolUse` (matcher: `Bash`) | `bash /Users/galta/.claude/hooks/guard.sh` |
| `PostToolUse` (matcher: `Write\|Edit`) | `bash /Users/galta/.claude/hooks/nanoclaw-validate.sh` |
| `PostToolUse` (no matcher) | `bash -c '...' _axcli-cache-ts` (writes axcli response timestamp) |
| `SessionStart` | `/Users/galta/.local/bin/axcli _session-start` |
| `SessionEnd` | `python3 /Users/galta/.claude/token-optimizer/skills/token-optimizer/scripts/measure.py collect --quiet` |
| `SessionEnd` | `/Users/galta/.local/bin/axcli _session-end` |
| `Stop` | `bash -c '...' _axcli-cache-ts` (same axcli timestamp caching) |

**`enabledPlugins` (active = `true` only):**
- `axcli@agentic-builders-hub`
- `cf-external-claude-plugin@client-foundations-ai-tools`
- `code-review@claude-plugins-official`
- `code-simplifier@claude-plugins-official`
- `commit-commands@claude-plugins-official`
- `llm-wiki-agent@llm-wiki-agent-dev`
- `pr-guardrails@agentic-builders-hub`
- `slack@claude-plugins-official`
- `superpowers@claude-plugins-official`
- `token-optimizer@alexgreensh-token-optimizer`
- `z2h@bigbrain-z2h`

(Disabled/false: builders-context, last30days, marketing-os, spec-driven-development, trident-monorepo)

---

### 7. `~/.claude/CLAUDE.md`

- **No `@`-imports found.**
- Section headers:
  - `# Global instructions`
  - `## guard.sh blocks destructive commands — do not retry`

---

### 8. M5.1 Security Scan (values REDACTED)

**File: `/Users/galta/Development/.claude/settings.local.json`**
- Top-level keys: `permissions`, `enableAllProjectMcpServers`, `enabledMcpjsonServers`
- Sensitive hits in `permissions.allow[]` (JWT in allowlist `Bash(claude mcp add ...)` entries):

| allow[] index | Key/pattern | MCP Server | Line (approx) |
|---|---|---|---|
| allow[29] | `Bash(claude mcp add ... --header "authorization:<REDACTED-JWT>")` | bigbrain-mcp | ~33 |
| allow[33] | `Bash(claude mcp add ... --header "authorization:<REDACTED-JWT>")` | bigbrain-mcp | ~37 |

These are past `claude mcp add` commands stored as allowlist entries. Both reference `https://mcp-gateway.bigbrain.me/mcp/stateless`.

**File: `~/.claude/mcp.json`**
- MCP server: `bigbrain-mcp`
  - URL: `https://mcp-gateway.bigbrain.me/mcp/stateless`
  - `headers.authorization`: `<REDACTED-JWT>` (line ~6)
  - Transport: HTTP stateless

No other MCP servers with auth headers found. No n8n-mcp tokens in either file.

---

### 9. `~/.claude/skills/` — Loose Non-Plugin Skills

**Directories present:**
- `brainstorm-council`
- `ga4-regex`
- `monday-brand-guidelines`
- `monday-data-viz-vibe`
- `monday-presentation-v2`
- `notebooklm`
- `pp-postman-explore`
- `reddit`
- `reddit-cli`
- `sir-albert`
- `token-optimizer`

**Presence check for named skills:**
| Skill | Present |
|---|---|
| `monday-brand-guidelines` | YES |
| `monday-presentation-v2` | YES |
| `monday-data-viz-vibe` | YES |
| `ga4-regex` | YES |
| `brainstorm-council` | YES (loose copy at `~/.claude/skills/brainstorm-council/`) |

**`~/.claude/skills/sir-albert`:**
- EXISTS and is a SYMLINK → `/Users/galta/Development/sir_albert`

---

## C. Knowledge Engine

### 10. `/Users/galta/Development/agent_knowledgebase`

**EXISTS locally.**

- **Current branch:** `fix/step6-resolution-prompt`
- **`skills/` contents:** `kb-query` (one skill dir only)
- **`commands/` contents:** `kb-compile.md`, `kb-init.md`
- **Top-level dirs also present:** `hooks/`, `hooks.json`, `lib/`, `tools/`, `templates/`, `examples/`, `tests/`, `docs/`

**Target skills from recon spec — presence in this repo:**

| Skill/Command | Found in repo |
|---|---|
| `wiki-query` | NOT FOUND (only `kb-query` skill exists in `skills/`) |
| `learn-recall` | NOT FOUND as a skill or command file |
| `learn-research` | NOT FOUND as a skill or command file |
| `wiki-init` | NOT FOUND (only `kb-init.md` in commands/) |
| `wiki-compile` | NOT FOUND (only `kb-compile.md` in commands/) |
| `learn-capture` | NOT FOUND as a skill or command file |

Note: The repo is on branch `fix/step6-resolution-prompt` (not `main`). The llm-wiki-agent plugin (registered as `llm-wiki-agent@llm-wiki-agent-dev`) points to this repo via `https://github.com/gal-Tab/agent_knowledgebase.git`. The skill names visible in the Claude harness (`wiki-query`, `learn-recall`, etc.) may be defined in the plugin's published version on GitHub rather than the current local checkout.

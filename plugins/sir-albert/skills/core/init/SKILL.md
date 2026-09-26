---
name: init
description: Use when setting up a new project repo for sir_albert workflows — starting a project, running /sir-albert:init, or when docs/specs/, docs/plans/, or .memory-bank/ are missing.
---

# sir-albert:init

## Overview

Project-level scaffolding only. Never touches machine config (`~/.claude/`, `~/.zshrc`). Idempotent: check existence before creating; report "created" vs "already exists" for every path.

## When to use

- User says "set up this project", "init this project", or runs `/sir-albert:init`
- `docs/specs/`, `docs/plans/`, or `.memory-bank/` are missing
- Starting fresh work on a repo with no sir_albert structure

## Instructions

### 1. Detect packs

Load `plugins/sir-albert/hooks/router_data.json` pack signals. Probe `$PWD`:
- `apply-*.ts` → gtm
- `*.workflow.json` → n8n
- `.hubspot/` or `hs*.js` → hubspot
- `raw/` AND `wiki/` both exist → kb
- `.z2h` file → z2h
- `.git/` AND `tests/` both exist → code

Report: `Active packs: <list or "(none detected)">`.

### 2. Scaffold directories (idempotent)

For each path, check existence first:

| Path | Action if missing | Action if present |
|------|-------------------|-------------------|
| `docs/specs/` | create | "already exists" |
| `docs/plans/` | create | "already exists" |
| `.memory-bank/` | create | "already exists" |

Use `mkdir -p` only for missing dirs. Never overwrite.

### 3. Project CLAUDE.md stub (only if absent)

If no `CLAUDE.md` exists at the project root, create a 5-line stub:

```markdown
# <project name — infer from directory name>

<!-- Add project-specific context here -->

Skill map: plugins/sir-albert/os/RESOLVER.md
```

If `CLAUDE.md` already exists, report "already exists" and leave it untouched.

### 4. KB init (conditional)

If `--kb` flag was passed **or** `raw/` directory exists at project root → call `kb:wiki-init`.

### 5. Emit structured report

```
sir-albert:init report
======================
docs/specs/       <created | already exists>
docs/plans/       <created | already exists>
.memory-bank/     <created | already exists>
CLAUDE.md         <created | already exists | skipped (existed)>
Active packs:     <list>
KB init:          <ran kb:wiki-init | skipped>
```

## Hard constraints

- Never create or modify anything in `~/.claude/`, `~/.zshrc`, or any path outside the project root.
- Never overwrite an existing file. Check first; report "already exists".
- Second run must produce identical output with "already exists" on every path.

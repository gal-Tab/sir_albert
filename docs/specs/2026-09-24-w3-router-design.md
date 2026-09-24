# W3 — Router + CLAUDE.md + Init

**Status:** revised · **Date:** 2026-09-24 · **Owner:** Gal

## Context

- W1 merged: one repo, two plugins, clean install. W2 merged: 9 canonical core skills, zero `superpowers:` refs in `plugins/`.
- Problem: 25 of 38 skills had never fired. superpowers fires because its `SessionStart` hook injects ~650 tokens of `using-superpowers` into every session AND `~/.claude/CLAUDE.md` names its skills by slug. Our skills have no equivalent entry point.
- W3 (this spec): wire a `SessionStart` router hook, a `UserPromptSubmit` keyword nudger, thin + version-control `CLAUDE.md`, move machine-wired hooks into the plugin, and ship `/sir-albert:init`.
- W4 follows: side-by-side eval vs superpowers → uninstall if sir-albert wins or ties.

## Goal

Every new Claude Code session surfaces the right sir-albert skills automatically: ≤800 chars on `SessionStart`, deterministic phrase-level keyword nudges on matching prompts, and a CLAUDE.md that points here instead of duplicating content.

## Non-goals

- W4: superpowers eval / uninstall.
- Moving repo to dapulse org.
- Changing KB engine behavior.
- Replacing `axcli`, `commit-commands`, `code-review`, `cf-external`, or `slack` (protected externals).
- Desktop/IDE `--plugin-dir` parity: these surfaces don't load the plugin at all (it's an accepted trade-off). Only `CLAUDE.md` (bootstrap-written) and `guard.sh` (symlinked to `~/.claude/hooks`) apply there.

---

## Component 0 — bootstrap.sh (machine setup)

### Split: machine vs project

- `bootstrap.sh` — **machine-level**, run once per machine. Idempotent. Every write to `~/.claude` or `.zshrc` is a CHECKPOINT.
- `/sir-albert:init` — **project-level**, run per repo. Idempotent. Never touches machine config.

### What bootstrap.sh does

```
bootstrap.sh
  ├─ CHECKPOINT: add alias in ~/.zshrc if missing
  │    alias claude='claude --plugin-dir /Users/galta/Development/sir_albert/plugins'
  ├─ CHECKPOINT: write ~/.claude/CLAUDE.md as one-line @import (if not already)
  │    @/Users/galta/Development/sir_albert/plugins/sir-albert/os/CLAUDE.global.md
  └─ CHECKPOINT: create ~/.claude/hooks/guard.sh → symlink to
       /Users/galta/Development/sir_albert/plugins/sir-albert/hooks/guard.sh
       (backs up any existing file first)
```

Each CHECKPOINT is a separate guarded step with a backup/dry-run check before writing.

---

## Component 1 — SessionStart router hook (Python)

### What it does
On every `SessionStart`, emit ≤800 chars of structured context. Hooks are Python (Unicode/Hebrew safety, easy pytest — matches kb hooks style).

### Data flow

```
SessionStart fires
  └─ hooks/session_start.py executes
       ├─ reads HOOK_CONTEXT.md (static template, versioned in repo)
       ├─ probes $PWD for pack signals defined in router_data.json
       │    GTM: apply-*.ts exists        → gtm pack
       │    n8n: *.workflow.json exists   → automation pack
       │    HubSpot: .hubspot/ or hs*.js  → automation pack
       │    raw/ + wiki/ both exist       → kb pack
       │    z2h app marker               → z2h pack
       │    .git/ + tests/ exist         → code pack
       ├─ checks .memory-bank/HANDOFF-*.md → resume hint (≤15 tokens, opt-out via DISABLE_RESUME_HINT=1)
       └─ char-count guard: if len(output) > 800, log warning to stderr, exit 0 (no injection)
            emits hookSpecificOutput.additionalContext JSON
```

### Injection text (draft — target ≤800 chars total)

```markdown
## sir_albert — session start

**Core skills** (sir-albert takes precedence over any superpowers equivalent):
| Need | Skill |
|------|-------|
| Think / explore / attack an idea | `/sir-albert:brainstorm` |
| Turn a spec into a plan | `/sir-albert:plan` |
| Execute a plan step by step | `/sir-albert:execute` |
| Debug a failing system | `/sir-albert:debug` |
| Ship a branch end-to-end | `/sir-albert:build` |
| Write a handoff doc + restart prompt | `/sir-albert:handoff` |
| Reload context from last handoff | `/sir-albert:resume` |
| Make or recall a decision | `/sir-albert:decide` |
| Scope-lock edits during investigation | `/sir-albert:freeze` |
| Create or edit a skill | `/sir-albert:create-skill` |

Map: `os/RESOLVER.md` · Output layout: `os/rules/docs-layout.md`
Active packs: {PACK_LIST}
{RESUME_HINT}
```

`{RESUME_HINT}` example: `Resume: .memory-bank/HANDOFF-2026-09-20.md found — run /sir-albert:resume`
Omitted (empty string) when `DISABLE_RESUME_HINT=1` or no handoff file found.

### Token budget / char cap

- Static table: ~620 chars.
- Pack list: ≤80 chars.
- Resume hint: ≤80 chars (omitted when absent).
- **Hard cap: 800 chars total.** Enforced in `session_start.py` via `len()`. If exceeded: stderr warning, no injection, session continues.

### File layout

```
plugins/sir-albert/hooks/
  session_start.py          ← new hook script (Python)
  prompt_router.py          ← new hook script (Python)
  HOOK_CONTEXT.md           ← static injection template
  router_data.json          ← pack signals + keyword patterns (single data file)
  guard.sh                  ← guard script (versioned here; ~/.claude/hooks/ symlinks to it)
  freeze-guard.sh           ← existing (already here)
  session-record.sh         ← existing (already here)
  hooks.json                ← updated: adds all new + migrated entries
```

---

## Component 2 — UserPromptSubmit keyword router (Python)

### What it does
Python script (`prompt_router.py`). Reads stdin JSON, extracts prompt, matches phrase-level patterns, emits a one-line nudge or exits silently. <50 ms, no network, no LLM.

### Pattern discipline

Patterns must target **intent to invoke the skill**, not topic words. The examples below must NOT match:
- "execute this SQL" → no match (execute is a topic word, not skill intent)
- "publish the GTM container" → no match (publish is a domain word here)
- "I'm feeling broken today" → no match
- "challenge accepted" → no match
- "architect of the building" → no match

Patterns use `\b` word boundaries and require multiple intent signals or a phrase structure. They are maintained in `router_data.json` — **never hardcoded** in the script.

### Hebrew patterns

Mine Gal's real Hebrew prompts from `~/.claude/projects/**/*.jsonl` (user messages, skip `/subagents/`). Propose patterns based on real usage. Gal approves before they enter `router_data.json`. This is a CHECKPOINT (ticket 04a).

### Draft keyword table (tightened — Gal to confirm after mining)

| Intent | Phrase pattern (Python regex, case-insensitive) | Nudge |
|---|---|---|
| brainstorm/explore | `\blet['']s (brainstorm\|explore\|think through)\b\|fresh perspective on\|help me think through\b` | `→ /sir-albert:brainstorm (explore mode)` |
| attack mode | `\b(devil['']s advocate\|stress.?test (my\|this)\|find (the\s)?holes in\|attack (my\|this))\b` | `→ /sir-albert:brainstorm attack` |
| grill | `\b(grill me\|interview me (about\|on))\b` | `→ /sir-albert:brainstorm grill` |
| zoom-out | `\b(zoom out\|bigger picture\|how does this fit into)\b` | `→ /sir-albert:brainstorm zoom-out` |
| design | `\b(let['']s design\|design (a\|the\|this)\|i want to build)\b` | `→ /sir-albert:brainstorm design` |
| plan | `\b(make a plan\|write a plan\|turn (this\|the) spec into a plan)\b` | `→ /sir-albert:plan` |
| execute | `\b(run the plan\|execute the plan\|implement (the\|this) plan)\b` | `→ /sir-albert:execute` |
| debug | `\b(help me debug\|let['']s debug\|why is (this\|it) (broken\|failing\|not working))\b` | `→ /sir-albert:debug` |
| build/ship | `\b(finish (the\s)?branch\|ship (this\s)?(feature\|change\|branch)\|let['']s (ship\|build and ship))\b` | `→ /sir-albert:build` |
| handoff | `\b(end of session\|write (a\s)?handoff\|create (a\s)?handoff)\b` | `→ /sir-albert:handoff` |
| resume | `\b(reload (my\s)?context\|where were we\|continue (the\s)?session)\b` | `→ /sir-albert:resume` |

Hebrew patterns: TBD pending mining (ticket 04a).

### Precision gate

Before wiring the router hook, run the router over every past user prompt in `~/.claude/projects/**/*.jsonl` (skip `/subagents/`). Report:
- Overall fire rate (target: <15% of prompts)
- Fire rate per route
- Random sample of 10 matches per route for Gal to eyeball

This is ticket 04b and **blocks** ticket 06 (wire hooks.json).

---

## Component 3 — Hook tests (pytest)

Mirrors `plugins/kb/tests/`. Tests invoke hook scripts as subprocesses (Python `subprocess.run`).

```
plugins/sir-albert/tests/
  __init__.py
  conftest.py
  fixtures/
    project_gtm/            (touch apply-deploy.ts)
    project_n8n/            (touch workflow.json)
    project_kb/             (mkdir raw wiki)
    project_plain/          (empty)
  test_session_start.py     ← fixtures → pack list + char count ≤800
  test_prompt_router.py     ← phrase → nudge; no-match → empty; false-positive phrases → empty
```

False-positive test cases are required:
- `"execute this SQL"` → empty
- `"publish the GTM container"` → empty
- `"challenge accepted"` → empty
- `"I'm feeling broken today"` → empty
- `"architect of the building"` → empty
- `"what time is it"` → empty

---

## Component 4 — Move machine-wired hooks into the plugin

### Current state (from `~/.claude/settings.json`)

- `PreToolUse` / `Edit|Write`: `bash .../freeze-guard.sh` — absolute path in settings.json.
- `SessionEnd`: `bash .../session-record.sh` — absolute path in settings.json.

### Target state

Declared in `plugins/sir-albert/hooks/hooks.json` via `${CLAUDE_PLUGIN_ROOT}`. The `settings.json` entries removed.

```
Before:
  settings.json  ──PreToolUse (Edit|Write)──▶  /absolute/path/freeze-guard.sh
  settings.json  ──SessionEnd──▶  /absolute/path/session-record.sh

After:
  hooks.json  ──PreToolUse (Edit|Write)──▶  ${CLAUDE_PLUGIN_ROOT}/hooks/freeze-guard.sh
  hooks.json  ──SessionEnd──▶  ${CLAUDE_PLUGIN_ROOT}/hooks/session-record.sh
```

**CHECKPOINT**: editing `~/.claude/settings.json` is live-config. Verify hooks fire exactly once before committing.

---

## Component 5 — Thin, versioned CLAUDE.md

- Canonical: `plugins/sir-albert/os/CLAUDE.global.md` (~20 lines). Uses **relative** `@identity/USER.md` / `@identity/SOUL.md` imports (relative to the file's location in `os/`).
- `~/.claude/CLAUDE.md`: written by `bootstrap.sh` as one absolute `@import`. Only this file holds the absolute path.

### Draft `CLAUDE.global.md`

```markdown
# Global — sir_albert_os

@identity/USER.md
@identity/SOUL.md

## Non-negotiables (always on)

- **Plan first.** Non-trivial task (3+ steps): `/sir-albert:brainstorm` (not superpowers). Read-only / trivial: act directly.
- **Use the skill.** When Gal names a skill, read it before acting — never from memory.
- **Ask before live.** AUTO on drafts / analysis / dry-runs. ASK before live-GTM publish, prod deploy, external sends, deletes. Full rule: `os/rules/autonomy.md`.
- **Evidence before done.** TLDR first, bullets, tables for comparisons. No filler. Full rule: `os/rules/output-style.md`.
- **Route subagents by model.** Opus for planning/synthesis/code. Haiku for reading/search/summarizing.
- **Skill edits via create-skill.** Every SKILL.md create or edit goes through `/sir-albert:create-skill`.
- **Minimal impact.** Smallest diff that solves it. No drive-by refactors.
- **Capture corrections.** After a correction, append to MEMORY.md (one line: pattern + why).

## guard.sh

`~/.claude/hooks/guard.sh` (symlinked from plugin) blocks destructive commands. Block is final — do not retry.

## Skill map

`plugins/sir-albert/os/RESOLVER.md` — one screen, complete routing.
```

---

## Component 6 — `/sir-albert:init` (project-level only)

Does NOT touch machine config (that's `bootstrap.sh`). Creates project structure only.

```
/sir-albert:init [--kb]
```

Creates (idempotent — never overwrites):
- `docs/specs/`, `docs/plans/`, `.memory-bank/`
- Project-root `CLAUDE.md` stub (5 lines: pointer to RESOLVER.md, project context placeholder)
- If `--kb` or `raw/` exists: calls `kb:wiki-init`
- Emits report: created/already-existed for each path + detected packs

---

## Open questions — resolved

- **OQ-1 guard.sh**: Option C. Version at `plugins/sir-albert/hooks/guard.sh`; `bootstrap.sh` symlinks `~/.claude/hooks/guard.sh` → it. ✓
- **OQ-2 resume hint**: Yes. One line ≤15 tokens when `.memory-bank/HANDOFF-*.md` exists. Opt-out: `DISABLE_RESUME_HINT=1`. ✓
- **OQ-3 char cap**: 800-char `len()` guard in `session_start.py`. ✓

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Noisy nudges (false positives) | Medium | High — degrades trust | Phrase-level patterns; precision report required before wiring (ticket 04b); false-positive pytest cases |
| Double-firing hooks during migration | High | Medium | Test before settings.json edit; migrate in one commit |
| Char creep (injection grows) | Medium | Low-medium | 800-char guard; `python3 -c "print(len(open('HOOK_CONTEXT.md').read()))"` in CI |
| Desktop/IDE: plugin doesn't load at all | High (accepted) | Low — accepted trade-off | CLAUDE.md and guard.sh apply via bootstrap; skill routing doesn't fire; documented non-goal |
| superpowers SessionStart still injects 650 tokens | Medium | Low | Our injection names sir-albert explicitly; superpowers text is generic; coexistence tested in verification |
| bootstrap.sh CHECKPOINT failure (bad .zshrc / CLAUDE.md write) | Low | High | Backups before every write; dry-run step; each CHECKPOINT is a separate guarded step |
| `@identity/...` relative imports fail if CLAUDE.global.md moves | Low | High | Stable path in os/; bootstrap path is absolute and validated at write time |

---

## Rollback

- **SessionStart/UserPromptSubmit hooks**: remove entries from `hooks.json`. No state changed.
- **settings.json migration**: restore from `~/.claude/settings.json.backup-w3`.
- **CLAUDE.md**: restore from `~/.claude/CLAUDE.md.backup-w3`.
- **bootstrap changes**: restore `.zshrc` from `.zshrc.backup-w3`, guard.sh symlink from backup.
- **`/sir-albert:init`**: skill disabled in hooks.json; created dirs are empty and safe to remove.

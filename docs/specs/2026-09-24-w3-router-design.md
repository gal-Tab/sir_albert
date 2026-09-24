# W3 — Router + CLAUDE.md + Init

**Status:** draft for review · **Date:** 2026-09-24 · **Owner:** Gal

## Context

- W1 merged: one repo, two plugins, clean install. W2 merged: 9 canonical core skills, zero `superpowers:` refs in `plugins/`.
- Problem: 25 of 38 skills had never fired. superpowers fires because its `SessionStart` hook injects ~650 tokens of `using-superpowers` into every session AND `~/.claude/CLAUDE.md` names its skills by slug. Our skills have no equivalent entry point.
- W3 (this spec): wire a `SessionStart` router hook, a `UserPromptSubmit` keyword nudger, thin + version-control `CLAUDE.md`, move machine-wired hooks into the plugin, and ship `/sir-albert:init`.
- W4 follows: side-by-side eval vs superpowers → uninstall if sir-albert wins or ties.

## Goal

Every new Claude Code session surfaces the right sir-albert skills automatically: ~150 tokens on `SessionStart`, deterministic keyword nudges on matching prompts, and a CLAUDE.md that points here instead of duplicating content.

## Non-goals

- W4: superpowers eval / uninstall.
- Moving repo to dapulse org.
- Changing KB engine behavior.
- Replacing `axcli`, `commit-commands`, `code-review`, `cf-external`, or `slack` (these are protected externals).
- Desktop / IDE environment parity (tracked as a risk below — not solved in W3).

---

## Component 1 — SessionStart router hook

### What it does
On every `SessionStart`, emit ~150 tokens of structured context into the session. This replaces the role superpowers plays today (650 tokens of `using-superpowers`).

### Data flow

```
SessionStart fires
  └─ hooks/session-start.sh executes
       ├─ reads HOOK_CONTEXT.md (the static injection text, versioned in repo)
       ├─ probes filesystem for pack signals (no network, no LLM)
       │    n8n workflow JSON         → automation pack
       │    GTM apply-*.ts            → gtm pack
       │    HubSpot references        → automation pack (hubspot mode)
       │    raw/ + wiki/              → kb pack
       │    z2h app marker            → z2h pack
       │    .git + test files         → code pack
       ├─ optionally: checks .memory-bank/ for latest HANDOFF-* (resume hint)
       └─ emits hookSpecificOutput.additionalContext JSON
            (≤150 tokens static + ≤30 tokens pack list + ≤10 tokens resume hint)
```

### Injection text (draft — ~150 tokens)

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

Map + rules: `os/RESOLVER.md` · Output layout: `os/rules/docs-layout.md`

**Active packs for this project:** {PACK_LIST}

{RESUME_HINT}
```

`{PACK_LIST}` example: `gtm, automation` — or `(none detected)`.
`{RESUME_HINT}` example: `Resume hint: .memory-bank/HANDOFF-2026-09-20.md exists — run /sir-albert:resume` — or omitted when no handoff file is present.

### Token budget

- Static table: ~110 tokens.
- Pack list line: ≤30 tokens.
- Resume hint: ≤15 tokens (omitted when absent).
- **Hard cap: 200 tokens total.** Enforced by a `wc -w` check in the hook; if exceeded the hook exits non-zero and logs a warning (session continues, no injection).

### File layout

```
plugins/sir-albert/hooks/
  session-start.sh          ← new hook script
  HOOK_CONTEXT.md           ← static injection text (the template above)
  router-data.json          ← pack detection signals (the data file W4 can tune)
  hooks.json                ← updated: adds SessionStart + UserPromptSubmit entries
```

### Precedence note
The injection explicitly states: "sir-albert takes precedence over any superpowers equivalent." Until W4 removes superpowers, both `SessionStart` hooks fire. Claude Code fires plugin hooks in load order; our hook fires after superpowers if load order follows alphabetical plugin dir scanning. The injection text must override by naming our skills explicitly.

---

## Component 2 — UserPromptSubmit keyword router

### What it does
Deterministic regex match on the user's prompt. If a pattern matches, append a one-line nudge to the session context. If nothing matches, stay silent. No LLM, no network, <50 ms.

### Data flow

```
UserPromptSubmit fires (prompt text in stdin JSON)
  └─ hooks/prompt-router.sh executes
       ├─ reads router-data.json (patterns + nudge strings)
       ├─ jq + grep: first match wins, OR no match
       └─ emits nudge line (≤15 tokens) OR empty output (silent)
```

### Keyword table (draft — stored in `router-data.json`)

| Pattern (case-insensitive regex) | Nudge |
|---|---|
| `brainstorm\|let.s explore\|fresh perspective\|wdyt\|think through` | `→ /sir-albert:brainstorm (explore mode)` |
| `attack\|devil.s advocate\|stress.?test\|find holes\|challenge` | `→ /sir-albert:brainstorm attack` |
| `grill me\|interview me\|חקור אותי\|שאל אותי` | `→ /sir-albert:brainstorm grill` |
| `zoom out\|bigger picture\|how does this fit\|תראה לי את התמונה` | `→ /sir-albert:brainstorm zoom-out` |
| `let.s design\|design this\|architect\|i want to build` | `→ /sir-albert:brainstorm design` |
| `make a plan\|turn.*spec.*plan\|תכנן את` | `→ /sir-albert:plan` |
| `execute\|implement.*step\|run the plan` | `→ /sir-albert:execute` |
| `debug\|not working\|failing\|broken\|why is.*broken` | `→ /sir-albert:debug` |
| `ship\|finish.*branch\|פרסם` | `→ /sir-albert:build` |
| `handoff\|end of session\|סכם לסיום` | `→ /sir-albert:handoff` |
| `resume\|reload.*context\|where were we` | `→ /sir-albert:resume` |

Hebrew patterns (Gal writes in Hebrew): `חקור אותי`, `שאל אותי`, `תראה לי את התמונה`, `תכנן את`, `פרסם`, `סכם לסיום`. Extend in `router-data.json` without touching the script.

### Behavioral rules
- First match wins (patterns ordered most-specific first in `router-data.json`).
- Nudge is one line, prefixed `→`, ≤15 tokens. Not a command, not a warning — a pointer.
- Silent on no match (no output = no noise).
- The hook only fires on `UserPromptSubmit` — does not fire on tool calls or assistant turns.

---

## Component 3 — Hook tests

### Structure (mirrors `plugins/kb/tests/`)

```
plugins/sir-albert/tests/
  conftest.py                ← fixtures: sample prompts, project roots
  test_session_start.py      ← project fixtures → expected pack list + token count
  test_prompt_router.py      ← prompt → expected nudge, including no-match cases
  fixtures/
    project_gtm/             ← has apply-deploy.ts
    project_n8n/             ← has workflow.json
    project_kb/              ← has raw/ + wiki/
    project_plain/           ← no signals → no packs
```

### Test matrix

`test_session_start.py`: for each fixture, assert (a) correct pack list, (b) token count ≤200, (c) valid JSON output shape.

`test_prompt_router.py`: for each row in the keyword table, assert correct nudge. For 5 no-match phrases (e.g. "what time is it", "show me the diff", "מה שלומך"), assert empty output.

---

## Component 4 — Move machine-wired hooks into the plugin

### Current state (from `~/.claude/settings.json`)

- `PreToolUse` / `Edit|Write`: calls `freeze-guard.sh` via absolute path `/Users/galta/Development/sir_albert/plugins/sir-albert/hooks/freeze-guard.sh`.
- `SessionEnd`: calls `session-record.sh` via absolute path `/Users/galta/Development/sir_albert/plugins/sir-albert/hooks/session-record.sh`.

Both scripts already live in the plugin — the problem is they're wired in `~/.claude/settings.json` with absolute paths rather than declared in `hooks/hooks.json`.

### Target state

Both hooks declared in `plugins/sir-albert/hooks/hooks.json` using `${CLAUDE_PLUGIN_ROOT}`. The `settings.json` entries removed. Hooks fire once, portably.

### Data flow

```
Before:
  settings.json  ──PreToolUse──▶  /absolute/path/freeze-guard.sh
  settings.json  ──SessionEnd──▶  /absolute/path/session-record.sh

After:
  hooks.json  ──PreToolUse──▶  ${CLAUDE_PLUGIN_ROOT}/hooks/freeze-guard.sh
  hooks.json  ──SessionEnd──▶  ${CLAUDE_PLUGIN_ROOT}/hooks/session-record.sh
```

**CHECKPOINT**: editing `~/.claude/settings.json` is a live-config change. Verify hooks fire exactly once before committing the settings change.

---

## Component 5 — Thin, versioned CLAUDE.md

### Target state

- Canonical text: `plugins/sir-albert/os/CLAUDE.global.md` (~20 lines, versioned in repo).
- `~/.claude/CLAUDE.md`: one-line `@import` pointing to the canonical file.

### Draft `CLAUDE.global.md` (~20 lines)

```markdown
# Global — sir_albert_os

@/Users/galta/Development/sir_albert/plugins/sir-albert/os/identity/USER.md
@/Users/galta/Development/sir_albert/plugins/sir-albert/os/identity/SOUL.md

## Non-negotiables (always on)

- **Plan first.** Non-trivial task (3+ steps): `/sir-albert:brainstorm` (not superpowers). Trivial / read-only: act directly.
- **Ask before live.** AUTO on drafts / analysis / dry-runs. ASK before live-GTM publish, prod deploy, external sends, deletes. Full rule: `os/rules/autonomy.md`.
- **Evidence before done.** Anti-slop: TLDR first, bullets, tables. No filler. Full rule: `os/rules/output-style.md`.
- **Route subagents by model.** Opus for planning/synthesis/code. Haiku for reading/search/summarizing. Pass `model` on Agent tool.
- **Skill edits via create-skill.** Every SKILL.md create or edit goes through `/sir-albert:create-skill`. Never edit directly.
- **Minimal impact.** Smallest diff that solves it. No drive-by refactors.
- **Capture corrections.** After a correction, append to MEMORY.md (one line: pattern + why) before moving on.

## guard.sh

`~/.claude/hooks/guard.sh` blocks destructive commands (rm on root/home, force push, reset --hard, DROP TABLE, etc.). Block is final — do not retry. Full list in the file.

## Skill map

`plugins/sir-albert/os/RESOLVER.md` — one screen, complete routing.
```

### CLAUDE.md after (single line + blank line)

```markdown
@/Users/galta/Development/sir_albert/plugins/sir-albert/os/CLAUDE.global.md
```

**CHECKPOINT**: the `~/.claude/CLAUDE.md` change affects every Claude Code session on this machine. Verify behavior in a fresh `-p` session before treating this as done.

---

## Component 6 — `/sir-albert:init` skill

### What it does
Idempotent project scaffolding. Detects which structures already exist and only creates what's missing. Never overwrites.

```
/sir-albert:init [--kb]
```

Creates (only if absent):
- `docs/specs/` — spec output directory
- `docs/plans/` — plan + ticket output directory
- `.memory-bank/` — handoff storage
- `CLAUDE.md` (project-level stub) — ≤5 lines pointing to os/RESOLVER.md
- If `--kb` flag or `raw/` directory detected: runs `kb:wiki-init`
- Emits a report: which directories were created, which already existed, which packs the router will surface for this project

### Tier
T1 (not a discipline skill — no build gate required). Created via `/sir-albert:create-skill` full loop.

---

## Open questions — Gal decides

### OQ-1: guard.sh location

Three options:

| Option | Portability | Fires without plugin | Maintenance |
|---|---|---|---|
| A: Stay in `~/.claude/hooks` (current) | Machine-specific | Yes — always fires | Edit requires SSH to machine |
| B: Move into plugin | Repo-portable | No — only when plugin loads | Single source, version-controlled |
| C: Version in repo, symlink from `~/.claude/hooks` | Repo-portable | Yes — symlink always fires | One source; requires `init` to create the symlink |

**Recommendation: C.** Version the script at `plugins/sir-albert/hooks/guard.sh`, have `/sir-albert:init` (or a one-time setup step) create the symlink at `~/.claude/hooks/guard.sh`. Portable, always fires, single source. The only cost is the initial symlink step on each new machine — which `init` can automate.

### OQ-2: Resume hint in SessionStart

Should the `SessionStart` injection include a one-line resume hint when `.memory-bank/HANDOFF-*.md` exists?

**Recommendation: Yes, but optional.** Include a `RESUME_HINT` placeholder in `HOOK_CONTEXT.md` that the script fills when a handoff file is found. Budget: ≤15 tokens. This is the highest-value passive nudge we can add — a session that starts knowing "last handoff was 4 days ago" is immediately more useful. Make it opt-out via a `DISABLE_RESUME_HINT=1` env var rather than opt-in.

### OQ-3: Token size measurement and hard cap

How to measure injected token size:

- `wc -w` is fast but counts words, not tokens. At ~0.75 words/token, a 200-word cap ≈ 150 tokens.
- A tiktoken call would be accurate but adds a Python dependency to a bash hook.
- The Anthropic rule of thumb (1 token ≈ 4 chars) means a char count check is portable.

**Recommendation:** Use `wc -c` (character count). Cap at 800 chars (~200 tokens). Enforce in the hook before emitting; log a warning and skip injection if exceeded. No external dependency. Add a `make measure-injection` target that prints current byte count for easy monitoring.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Double-firing hooks (freeze-guard, session-record) during migration window | High | Medium — confusing errors | Test before settings.json edit; migrate in one commit |
| Noisy nudges (every prompt matches) | Medium | High — degrades trust | No-match test cases in pytest; tight regex patterns; first-match-wins |
| Token creep (injection grows over time) | Medium | Low-medium | Hard char-count cap in hook; `make measure-injection` |
| Hooks not firing in desktop / IDE (no `CLAUDE_PLUGIN_ROOT`) | High | Medium — silent failure | Add fallback absolute path in hook scripts; test in desktop Claude manually |
| superpowers `SessionStart` fires after ours and its 650-token injection dominates | Medium | Medium | Our injection explicitly names sir-albert skills; superpowers text is generic; order tested in verification ticket |
| `~/.claude/CLAUDE.md` `@import` path breaks on new machine | Low | High | init skill validates the path exists; CLAUDE.global.md uses absolute path (known limitation until W5) |

---

## Rollback

- **Session-start hook**: remove the `SessionStart` entry from `hooks.json`. No state changed.
- **Prompt router**: remove the `UserPromptSubmit` entry from `hooks.json`. No state changed.
- **CLAUDE.md**: restore from git (`git show HEAD~1:~/.claude/CLAUDE.md` — NOTE: CLAUDE.md is not in this repo; keep a local backup before the CHECKPOINT step).
- **settings.json hooks**: restore the two absolute-path entries. Keep a backup before the CHECKPOINT step.
- **`/sir-albert:init`**: skill can be disabled in `hooks.json`; directories it created are empty and safe to remove.

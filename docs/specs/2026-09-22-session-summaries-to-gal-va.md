---
title: Session summaries → gal-va/notes (Claude Code session journal)
status: draft
owner: gal-Tab
created: 2026-09-22
sources:
  - conversation 2026-09-22 (CLAUDE.md rework session) — Gal's request
stale_after: 2027-03-31
---

# Session summaries → `gal-va/notes/sessions/`

## TLDR
Add an automatic **session journal**: when a Claude Code session ends, a per-session
markdown summary is written into `DaPulse/gal-va` under `notes/sessions/`, mirroring
the existing `meetings/` format. This is a **human-readable archive**, deliberately
**separate from** the behavioral `MEMORY.md` capture loop.

- **Two stages, on purpose.** SessionEnd hook stays fast/non-fatal (queue only, no LLM,
  no network). A **batch summarizer** (scheduled, off critical path) generates the prose
  and pushes to gal-va.
- **Reversible-first git.** Batch summarizer commits to a **branch + PR**, never
  direct-to-main, never force-push. (Meetings loop writes direct-to-main; journals start
  gated and can graduate later.)
- **Coexists with memory, does not replace it.** Memory = short behavioral rules,
  auto-loaded into context. Journal = full narrative per session, not auto-loaded.

## Why NOT the naive design
A SessionEnd hook is bash — it has no LLM, so it can't write a good summary itself, and it
must **never block session end** (see `session-record.sh`: "never exits nonzero"). Shelling
out to `claude -p` *inside* the SessionEnd hook would add latency + a network dependency to
every session teardown and risk hanging. So generation is decoupled from teardown.

## Memory vs. journal (the boundary — keep these distinct)

| | `MEMORY.md` (behavioral) | `notes/sessions/` (journal) |
|---|---|---|
| Purpose | Rules that change how the agent acts | Human-readable record of what happened |
| Loaded into context? | Yes, every session (auto) | No — retrieved on demand (second-brain) |
| Content | One-line lessons/corrections + why | Full narrative: tasks, decisions, next steps |
| Writer | Correction-capture loop, mid-session | Batch summarizer, post-session |
| Store | `~/.claude/projects/.../memory/MEMORY.md` | `DaPulse/gal-va/notes/sessions/*.md` |

A single correction can land in **both**: one line to MEMORY.md (to change behavior) and it
also appears in the session journal (as record). They are not competing stores.

## Architecture — two stages

### Stage 1 — SessionEnd hook (fast, non-fatal)
Extend the existing `sir_albert/hooks/session-record.sh` (do not add a second hook).
Today it appends a breadcrumb to `~/.claude/sir-albert-sessions.jsonl`. Add one field:
the **transcript path** for the session, and a `journaled: false` marker (or maintain a
parallel queue file `~/.claude/sir-albert-journal-queue.jsonl`).

- No summary generation, no git, no network here.
- Preserve the existing discipline verbatim: `set -u`, best-effort, `exit 0` always.
- Cost: ~0 (one extra field on an append that already happens).

### Stage 2 — Batch summarizer (scheduled, off critical path)
A new script `sir_albert/tools/journal/summarize-sessions.sh` (+ a small prompt file),
run by the daily/dream-cycle cadence in `HEARTBEAT.md` (or a cron). For each unjournaled
session in the queue:

1. **Read** the transcript JSONL (path from the queue).
2. **Generate** the summary via headless `claude -p` (fast model — Haiku — for
   read+summarize per the new subagent-model-routing rule) using a fixed prompt →
   produces frontmatter + the sections below.
3. **Write** to the local clone at `/Users/galta/Development/gal-va/notes/sessions/`.
4. **Mark** the session `journaled: true` in the queue.
5. After all sessions in the batch: **git branch + commit + push + PR** (see git flow).

Batching means one PR per run (e.g. daily), not one per session.

## File format (`notes/sessions/`)
Mirror the `meetings/` convention.

- **Naming:** `session-YYYY-MM-DD-HHMM-<project-slug>.md`
  (e.g. `session-2026-09-22-1430-sir_albert.md`). Project slug = `basename(cwd)`.
- **Frontmatter:**
  ```yaml
  ---
  session_id: <id>
  project: <project>
  cwd: <cwd>
  date: 2026-09-22
  start: <iso>            # best-effort from transcript first ts
  end: <iso>              # SessionEnd ts
  git_branch: <branch>
  git_head: <short-sha>
  source: claude-code     # distinguishes from source: monday-notetaker
  ---
  ```
- **Sections:**
  - `## Summary` — 3–6 sentences: what the session was about and what shipped.
  - `## Tasks` — what was done (checklist / bullets).
  - `## Skills invoked` — sir-albert / superpowers / other skills that fired.
  - `## Corrections` — corrections Gal gave (mirror of what should also go to MEMORY.md).
  - `## Decisions` — settled decisions (candidates for `os/state/decisions.jsonl`).
  - `## Next steps` — open threads / handoff pointers.

## Git flow (reversible-first — CRITICAL)
Operate in the existing local clone `/Users/galta/Development/gal-va` (on `main`, clean).

```
git -C <clone> fetch origin
git -C <clone> switch -c session-journal/YYYY-MM-DD origin/main
# write notes/sessions/*.md
git -C <clone> add notes/sessions
git -C <clone> commit -m "session journal: YYYY-MM-DD (<n> sessions)"
git -C <clone> push -u origin session-journal/YYYY-MM-DD
gh pr create --repo DaPulse/gal-va --base main --head session-journal/YYYY-MM-DD \
  --title "Session journal YYYY-MM-DD" --body "..."
```

- **Never** commit to `main` directly; **never** force-push; **never** `git reset --hard`
  (also blocked by `guard.sh`).
- **Tradeoff, stated:** the notetaker loop writes meetings direct-to-main. Journals start
  **PR-gated** because they're a new, unproven writer into a shared INTERNAL repo. Once the
  format is trusted, a follow-up can switch to direct append-to-main (or PR auto-merge) to
  cut overhead. Start safe.
- If the clone is dirty at run time: **stash-free** — abort the run, log, exit 0 (don't risk
  Gal's working changes). Retry next cycle.

## Error handling
- Stage 1: inherits `session-record.sh` non-fatal discipline (always `exit 0`).
- Stage 2:
  - Offline / `push` fails → local commit persists on the branch; log; `exit 0`; retried next run.
  - `claude -p` fails/times out for a session → skip that session (leave `journaled: false`), continue others.
  - Malformed transcript → skip, log, continue.
  - Dirty clone / branch already exists → abort run cleanly, log.

## Cost
- Stage 1: negligible.
- Stage 2: one Haiku summarization per session (~a few K tokens each), batched, off-hours.
  Bounded by sessions/day. No cost on the interactive path.

## Coexistence with the correction-capture loop
The always-on `CLAUDE.md` contract writes corrections to `MEMORY.md` (behavioral, live).
This journal is downstream and additive: the batch summarizer's `## Corrections` section is
a *record* of the same corrections, not a substitute. Neither depends on the other; if the
journal is disabled, memory still works, and vice-versa.

## Out of scope (follow-ups)
- Direct-to-main / auto-merge graduation once format is trusted.
- Feeding `## Decisions` into `os/state/decisions.jsonl` automatically.
- `second-brain` retrieval over `notes/sessions/`.

## `notes/README.md` update (required)
Add `sessions/` to the notes layout doc, labeled: "one capture per Claude Code session,
written by the session-journal batch summarizer (`source: claude-code`), PR-gated."
Note this is a **second writer** distinct from gal-va's notetaker loop.

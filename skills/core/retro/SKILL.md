---
name: retro
description: >
  Self-improving skills loop. Reads recent sessions (index + axcli analytics + transcripts),
  surfaces recommended skill edits — new trigger phrases, description tweaks, skill merges,
  new-skill candidates — and emits them as a draft for Gal to approve. Never auto-applies.
  Use when the user says "/retro", "retro", "self-improve skills", "what should the OS learn",
  "review my corrections", or "skill trigger fixes".
---

# Retro

Boot from `os/PREAMBLE.md` — load USER identity + active rules + anti-slop / use-the-skill contract before proceeding.

**Announce at start:** "Running /sir-albert:retro — scanning sessions for skill-improvement signals."

---

## 1. Signal sources (three layers — none alone is enough)

1. **Session index** — `~/.claude/sir-albert-sessions.jsonl` (from the `session-record.sh` SessionEnd hook). One line/session: `timestamp, iso, project, cwd, session_id, git_branch, git_head, git_dirty`. This is the *index* of which sessions to review + their project/git context.
2. **axcli analytics (structural)** — `~/.claude/analytics.duckdb` (DuckDB, built by axcli's `ingest.py`). Rich metadata: which skills fired, tool usage, AskUserQuestion rejections, slash commands, cost/turns per session & project. **No prompt text** (privacy — `user_messages` is metadata only). Query with `duckdb`.
3. **Raw transcripts (textual)** — the session JSONL files. The ONLY place actual corrections / re-explained context live. Read the *flagged* recent ones for the §3 textual signals.

## 2. Freshen + query axcli (structural signals)

Ensure the analytics DB is fresh, then query it:

```bash
DB="$HOME/.claude/analytics.duckdb"
if [ ! -f "$DB" ] || [ $(( $(date +%s) - $(stat -f %m "$DB" 2>/dev/null || stat -c %Y "$DB") )) -gt 3600 ]; then
  INGEST=$(find "$HOME/.claude/plugins/cache/agentic-builders-hub/axcli" -name ingest.py 2>/dev/null | head -1)
  [ -n "$INGEST" ] && python3 "$INGEST"   # ~10-30s; reads all session JSONL
fi
```

**MANDATORY before writing SQL:** read `**/axcli/knowledge/semantic-layers.md` (Glob) for exact columns/joins. Then run structural cuts over the last 7d (`duckdb "$DB" -markdown -c "..."`), filtering `is_agent = false`:
- **Skill adoption** — `tool_uses` where `tool_name='Skill'`: which sir-albert skills fired, how often, in which projects. A skill that never fires despite relevant work = a trigger/description gap.
- **Friction / rejections** — sessions with `AskUserQuestion` rejections (proxy: I asked and Gal redirected) → flag those `session_id`s for a transcript read in §3.
- **Slash commands** — `history` where `display LIKE '/%'`: what Gal invokes by hand that a skill could auto-trigger.
- **Missed-skill candidates** — projects with high activity but zero sir-albert skill invocations.

(Join to `session_meta.project_path` for readable project names.)

## 3. Read flagged transcripts (textual signals)

For sessions flagged in §2 (rejections / high-activity-no-skill), locate the raw transcript by `session_id` and read it for:

| Signal | Examples |
|---|---|
| Explicit corrections | "did you use the skill?", "use X instead", "that's not how X works" |
| Missed triggers | a skill's trigger words appeared but the skill didn't fire |
| Slop / quality | "too verbose", "cut the fluff", repeated anti-slop nudges |
| Re-explained context | the same background re-stated across ≥2 sessions → rule/skill candidate |
| Naming drift | a variant phrase no existing trigger catches |

**Scope it:** only read transcripts the structural pass flagged (or the last few in the window) — never read every transcript every run.

## 4. Emit RECOMMENDED edits (draft for approval)

```
RECOMMENDED: <skill-name or "new skill">
  type: trigger-phrase | description-tweak | skill-merge | new-skill
  signal: <what was observed, with session id/date + source layer>
  proposed change: <exact diff or new text>
  rationale: <one sentence>
```
- List every recommendation, even minor. If nothing found, say so — do not fabricate.
- **Never auto-apply** to any SKILL.md or settings.json. Apply only after Gal approves each item (draft→approve, `rules/autonomy.md`).

## 5. Pairing note
Retro handles the long tail of trigger misses + quality drift. Hard gates (consent, naming, safety) stay in dedicated guardrails — retro doesn't touch those.

## 6. Bootstrap / historical backfill
> **TODO(gal): run the backfill once (heavy).** First pass = one big axcli query over ALL history (skill adoption + rejection hotspots across the ~3,853 prompts) + a transcript sweep of the top-flagged sessions. Large separate run — not part of a normal retro.

## 7. Activation — APPEND to settings.json (do NOT do this automatically)
Append this as the **third** element of the existing `SessionEnd` array in `~/.claude/settings.json`.

> **WARNING: APPEND — do NOT replace the array, or you break token-optimizer (measure.py collect) and axcli (_session-end). Keep all three entries.**

```json
{ "hooks": [ { "type": "command", "command": "bash /Users/galta/Development/sir_albert/hooks/session-record.sh" } ] }
```
Full resulting array for reference:
```json
"SessionEnd": [
  { "hooks": [ { "command": "python3 /Users/galta/.claude/token-optimizer/skills/token-optimizer/scripts/measure.py collect --quiet", "type": "command" } ] },
  { "hooks": [ { "command": "/Users/galta/.local/bin/axcli _session-end", "type": "command" } ] },
  { "hooks": [ { "type": "command", "command": "bash /Users/galta/Development/sir_albert/hooks/session-record.sh" } ] }
]
```

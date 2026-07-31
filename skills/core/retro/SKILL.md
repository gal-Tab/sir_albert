---
name: retro
description: >
  Self-improving skills loop. Scans recent session records and .compound/ ledgers to surface
  recommended skill edits — new trigger phrases, description tweaks, skill merges, new-skill
  candidates — and emits them as a draft for Gal to approve. Never auto-applies changes.
  Use when the user says "/retro", "retro", "self-improve skills", "what should the OS learn",
  "review my corrections", or "skill trigger fixes".
---

# Retro

Boot from `os/PREAMBLE.md` — load USER identity + active rules + anti-slop / use-the-skill contract before proceeding.

**Announce at start:** "Running /sir-albert:retro — scanning sessions for skill improvement signals."

---

## 2. Capture — how session records are produced

A `SessionEnd` hook (`hooks/session-record.sh`) appends one JSON line per session to
`~/.claude/sir-albert-sessions.jsonl`. Each line carries: `timestamp`, `cwd`, `session_id`
(best-effort), and whatever metadata was available on stdin. The retro reads that file — no
other instrumentation is needed from skills or agents.

---

## 3. Retro run

### 3a. Load the windows

- **24h window:** all lines in `~/.claude/sir-albert-sessions.jsonl` where `timestamp ≥ now - 86400`.
- **7d window:** all lines where `timestamp ≥ now - 604800`.
- **`.compound/` ledgers:** if the directory exists, read every file under it.

```bash
# 24h
since_24h=$(date -v-24H +%s 2>/dev/null || date -d '24 hours ago' +%s)
awk -F'"timestamp":' 'NF>1 { split($2,a,","); gsub(/[^0-9]/,"",a[1]); if (a[1]+0 >= '"$since_24h"') print }' \
  ~/.claude/sir-albert-sessions.jsonl

# 7d
since_7d=$(date -v-7d +%s 2>/dev/null || date -d '7 days ago' +%s)
awk -F'"timestamp":' 'NF>1 { split($2,a,","); gsub(/[^0-9]/,"",a[1]); if (a[1]+0 >= '"$since_7d"') print }' \
  ~/.claude/sir-albert-sessions.jsonl
```

### 3b. Detection signals — what to look for

| Signal | Examples |
|---|---|
| Explicit corrections | "did you use the skill?", "use X instead", "that's not how X works" |
| Missed triggers | A skill's name or trigger words appeared in a prompt but the skill didn't fire |
| Slop / quality corrections | "too verbose", "cut the fluff", "anti-slop" repeated in a session |
| Re-explained context | The same background re-stated across ≥2 sessions → candidate for a rule/skill |
| Naming drift | Gal used a variant phrase that no existing trigger catches |

### 3c. Emit RECOMMENDED edits

For each signal found, produce a structured recommendation block:

```
RECOMMENDED: <skill-name or "new skill">
  type: trigger-phrase | description-tweak | skill-merge | new-skill
  signal: <what was observed, with session id/date>
  proposed change:
    <exact diff or new text>
  rationale: <one sentence>
```

- List every recommendation, even minor ones.
- If nothing was found in the windows, say so explicitly — do not fabricate signals.

---

## 4. Output — draft for Gal to approve

- Emit the full list of recommendations as a **draft**.
- **Never auto-apply** any change to a SKILL.md or settings.json. Apply only after Gal
  explicitly approves each item (draft→approve contract from `rules/autonomy.md`).
- Keep the report tight: one table of signals, then the recommendation blocks.

---

## 5. Pairing note

Retro handles the long tail of trigger misses and quality drift. Hard gates (consent naming,
safety rules) are handled by dedicated guardrails — retro does not touch those.

---

## 6. Bootstrap / historical backfill

> **TODO(gal): run the historical backfill retro once (heavy).**
> The first retro pass should scan the ~3,853 historical prompts + all `.compound/` ledgers
> in one batch run to seed the recommendations. This is a large separate run — do not attempt
> it automatically during a normal retro invocation.

---

## 7. Activation — APPEND to settings.json (do NOT do this automatically)

To activate the `SessionEnd` hook that feeds this retro, **append** the following object to
the existing `SessionEnd` array in `~/.claude/settings.json`.

> **WARNING: APPEND, do NOT replace the existing SessionEnd array or you will break
> token-optimizer (measure.py collect) and axcli (_session-end). The array must keep all
> three entries.**

Exact snippet to append as the third element of the `SessionEnd` array:

```json
{
  "hooks": [
    {
      "type": "command",
      "command": "bash /Users/galta/Development/sir_albert/hooks/session-record.sh"
    }
  ]
}
```

Resulting `SessionEnd` array (complete, for reference):

```json
"SessionEnd": [
  {
    "hooks": [
      {
        "command": "python3 /Users/galta/.claude/token-optimizer/skills/token-optimizer/scripts/measure.py collect --quiet",
        "type": "command"
      }
    ]
  },
  {
    "hooks": [
      {
        "command": "/Users/galta/.local/bin/axcli _session-end",
        "type": "command"
      }
    ]
  },
  {
    "hooks": [
      {
        "type": "command",
        "command": "bash /Users/galta/Development/sir_albert/hooks/session-record.sh"
      }
    ]
  }
]
```

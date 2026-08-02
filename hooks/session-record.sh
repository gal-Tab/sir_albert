#!/usr/bin/env bash
# session-record.sh — SessionEnd hook (robust breadcrumb index for /retro).
# Appends one compact JSON line per session to ~/.claude/sir-albert-sessions.jsonl:
#   { timestamp, iso, project, cwd, session_id, git_branch, git_head, git_dirty }
# This is the INDEX retro maps a session to. Rich structural signal comes from axcli's
# analytics.duckdb; textual signal (corrections, re-explained context) from raw transcripts.
# Fast, append-only, NEVER fatal: never exits nonzero, never blocks session end.
set -u

OUTFILE="$HOME/.claude/sir-albert-sessions.jsonl"

# --- read stdin (SessionEnd passes a JSON payload); tolerate empty/missing ---
raw_input=""
if read -t 2 -r raw_input 2>/dev/null; then
  while IFS= read -t 0.1 -r line 2>/dev/null; do raw_input="${raw_input}${line}"; done
fi

ts=$(date +%s)
iso=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "")
cwd="${PWD:-}"
project=$(basename "$cwd" 2>/dev/null || echo "")

# --- session_id from stdin JSON (jq if present; tolerate string or object) ---
session_id=""
if command -v jq >/dev/null 2>&1 && [ -n "$raw_input" ]; then
  session_id=$(printf '%s' "$raw_input" | jq -r '
      if (.session_id | type) == "object"
      then (.session_id | to_entries[0].value // "")
      else (.session_id // "") end' 2>/dev/null || true)
fi

# --- git context (best-effort, fast, non-fatal) ---
git_branch=""; git_head=""; git_dirty="unknown"
if command -v git >/dev/null 2>&1 && git -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git_branch=$(git -C "$cwd" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
  git_head=$(git -C "$cwd" rev-parse --short HEAD 2>/dev/null || echo "")
  if git -C "$cwd" diff --quiet --ignore-submodules 2>/dev/null \
     && git -C "$cwd" diff --cached --quiet --ignore-submodules 2>/dev/null; then
    git_dirty="false"
  else
    git_dirty="true"
  fi
fi

# --- JSON-escape helper (no jq needed on the write path) ---
_j() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/	/\\t/g'; }

record="{\"timestamp\":${ts},\"iso\":\"$(_j "$iso")\",\"project\":\"$(_j "$project")\",\"cwd\":\"$(_j "$cwd")\",\"session_id\":\"$(_j "${session_id:-}")\",\"git_branch\":\"$(_j "$git_branch")\",\"git_head\":\"$(_j "$git_head")\",\"git_dirty\":\"${git_dirty}\"}"

mkdir -p "$(dirname "$OUTFILE")" 2>/dev/null || true
printf '%s\n' "$record" >> "$OUTFILE" 2>/dev/null || true
exit 0

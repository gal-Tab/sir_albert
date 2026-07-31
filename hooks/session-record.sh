#!/usr/bin/env bash
# session-record.sh — SessionEnd hook
# Appends one compact JSON line per session to ~/.claude/sir-albert-sessions.jsonl.
# Fast, append-only, non-fatal: never exits nonzero, never blocks session end.
set -u

OUTFILE="$HOME/.claude/sir-albert-sessions.jsonl"

# Read stdin (SessionEnd passes JSON payload); tolerate empty/missing stdin.
raw_input=""
if read -t 2 -r raw_input 2>/dev/null; then
  while IFS= read -t 0.1 -r line 2>/dev/null; do
    raw_input="${raw_input}${line}"
  done
fi

ts=$(date +%s)
cwd="${PWD:-}"

# Extract session_id from stdin JSON if jq is available; fall back to empty string.
session_id=""
if command -v jq >/dev/null 2>&1 && [ -n "$raw_input" ]; then
  session_id=$(printf '%s' "$raw_input" \
    | jq -r '
        if (.session_id | type) == "object"
        then (.session_id | to_entries[0].value // "")
        else (.session_id // "")
        end
      ' 2>/dev/null || true)
fi

# Sanitise values so they are safe to embed in a JSON string without jq for the write path.
_json_str() {
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g; s/	/\\t/g'
}

cwd_safe=$(_json_str "$cwd")
sid_safe=$(_json_str "${session_id:-}")

record="{\"timestamp\":${ts},\"cwd\":\"${cwd_safe}\",\"session_id\":\"${sid_safe}\"}"

# Append; if the directory or file doesn't exist yet, create it.
mkdir -p "$(dirname "$OUTFILE")" 2>/dev/null || true
printf '%s\n' "$record" >> "$OUTFILE" 2>/dev/null || true

exit 0

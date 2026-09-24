#!/usr/bin/env bash
# freeze-guard.sh — PreToolUse hook for Edit|Write
# Blocks edits outside frozen path(s) when .memory-bank/.freeze is active.
# Fail-open: any parse error → exit 0 so a bug never bricks all edits.

set -u

FREEZE_FILE=".memory-bank/.freeze"

# ── 1. Read stdin (Claude Code passes tool input JSON on stdin) ──────────────
input="$(cat)"

# ── 2. Extract file_path ─────────────────────────────────────────────────────
if command -v jq &>/dev/null; then
  target="$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)"
else
  # Fallback: crude grep/sed — good enough for an absolute path string
  target="$(printf '%s' "$input" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' \
    | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' | head -1)"
fi

# Fail-open: no path extracted → allow
[[ -z "$target" ]] && exit 0

# ── 3. No freeze file → allow ─────────────────────────────────────────────────
[[ ! -f "$FREEZE_FILE" ]] && exit 0

# ── 4. Read frozen paths (one absolute path per line, skip blanks/comments) ───
frozen_paths=()
while IFS= read -r line || [[ -n "$line" ]]; do
  [[ -z "$line" || "$line" == \#* ]] && continue
  frozen_paths+=("$line")
done < "$FREEZE_FILE"

# Fail-open: empty freeze file → allow
[[ ${#frozen_paths[@]} -eq 0 ]] && exit 0

# ── 5. Check if target is under any frozen path ───────────────────────────────
for frozen in "${frozen_paths[@]}"; do
  # Normalise: ensure frozen path ends without trailing slash for prefix check
  frozen="${frozen%/}"
  if [[ "$target" == "$frozen" || "$target" == "$frozen/"* ]]; then
    exit 0  # allowed
  fi
done

# ── 6. Block ──────────────────────────────────────────────────────────────────
frozen_list="$(IFS=', '; echo "${frozen_paths[*]}")"
echo "BLOCKED: freeze active — '${target}' is outside frozen path(s): ${frozen_list}" >&2
exit 2

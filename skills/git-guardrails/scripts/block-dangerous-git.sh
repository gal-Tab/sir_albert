#!/usr/bin/env bash
# ------------------------------------------------------------------
# Git Guardrails — PreToolUse hook for Claude Code
#
# Reads the Bash tool-call JSON from stdin, extracts the command,
# and blocks it if it matches a dangerous git pattern.
#
# Customization:
#   - ALLOWED_PATTERNS are checked first (allowlist wins over blocklist)
#   - BLOCKED_PATTERNS are checked second
#   - Patterns use bash glob matching (not regex)
#
# Exit behavior:
#   - Outputs JSON with "decision": "block" to prevent execution
#   - Outputs nothing (or "decision": "allow") to let it through
# ------------------------------------------------------------------

set -euo pipefail

# ==================== CONFIGURATION ====================
# Add or remove patterns to taste. Each pattern is matched
# against the full command string using bash globbing.
#
# Examples:
#   "git push*"              — blocks any push
#   "git push --force*"      — blocks only force pushes
#   "git push*main*"         — blocks pushes that mention main
#   "git push origin feature/*" — matches pushes to feature branches

ALLOWED_PATTERNS=(
  # Uncomment or add patterns for commands you want to permit
  # even though they'd otherwise be blocked:
  #
  # "git push origin feature/*"
  # "git push --dry-run*"
)

BLOCKED_PATTERNS=(
  "git push*"
  "git reset --hard*"
  "git reset HEAD~*--hard*"
  "git clean -f*"
  "git clean -df*"
  "git clean -fd*"
  "git checkout ."
  "git checkout -- ."
  "git restore ."
  "git restore --staged ."
  "git branch -D*"
  "git branch -d -f*"
  "git stash drop*"
  "git stash clear*"
  "git rebase*"
)

# ==================== END CONFIGURATION ====================

# Read the tool input JSON from stdin
INPUT=$(cat)

# Extract the command field. We use python3 if available for
# reliable JSON parsing, with a grep fallback for minimal envs.
if command -v python3 &>/dev/null; then
  COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('command', data.get('input', {}).get('command', '')))
except:
    print('')
" 2>/dev/null)
else
  # Fallback: rough extraction (handles most common formats)
  COMMAND=$(echo "$INPUT" | grep -oP '"command"\s*:\s*"\K[^"]+' 2>/dev/null || echo "")
fi

# If we couldn't extract a command, let it through — don't block
# non-git operations or malformed input.
if [[ -z "$COMMAND" ]]; then
  exit 0
fi

# Quick exit: if the command doesn't start with "git ", skip all checks.
# This keeps the hook fast for non-git commands.
if [[ "$COMMAND" != git\ * ]] && [[ "$COMMAND" != *"&& git "* ]] && [[ "$COMMAND" != *"; git "* ]] && [[ "$COMMAND" != *"| git "* ]]; then
  exit 0
fi

# Split on common shell operators so chained commands are checked
# individually: "npm test && git push" should still catch "git push".
# We normalize by stripping leading whitespace from each segment.
IFS=$'\n' read -r -d '' -a SEGMENTS < <(
  echo "$COMMAND" | sed 's/&&/\n/g; s/;/\n/g; s/|/\n/g' | sed 's/^[[:space:]]*//'
  printf '\0'
) || true

for SEGMENT in "${SEGMENTS[@]}"; do
  # Check allowlist first — allowed patterns take priority
  ALLOWED=false
  for pattern in "${ALLOWED_PATTERNS[@]}"; do
    # shellcheck disable=SC2254
    case "$SEGMENT" in
      $pattern)
        ALLOWED=true
        break
        ;;
    esac
  done

  if [[ "$ALLOWED" == true ]]; then
    continue
  fi

  # Check blocklist
  for pattern in "${BLOCKED_PATTERNS[@]}"; do
    # shellcheck disable=SC2254
    case "$SEGMENT" in
      $pattern)
        cat <<EOF
{
  "decision": "block",
  "reason": "BLOCKED by git-guardrails: '$SEGMENT' matches dangerous pattern '$pattern'. If you need to run this command, the human should do it manually outside of Claude Code, or update the allowlist in the hook script."
}
EOF
        exit 0
        ;;
    esac
  done
done

# No match — allow the command
exit 0

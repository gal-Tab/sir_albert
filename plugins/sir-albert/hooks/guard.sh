#!/bin/bash
# Claude Code auto-mode safety guard
# Blocks destructive commands that are hard/impossible to reverse.
# Reads the tool input JSON from stdin (PreToolUse hook contract).

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$CMD" ]; then
  exit 0
fi

block() {
  echo "BLOCKED: $1" >&2
  exit 2
}

# --- Catastrophic deletion ---
echo "$CMD" | grep -qE 'rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+|--force\s+)*(\/|~|\$HOME)' && block "rm targeting root or home"
echo "$CMD" | grep -qE 'rm\s+-[a-zA-Z]*r[a-zA-Z]*f' && echo "$CMD" | grep -qE '\s(\/|~|\$HOME)\s*$' && block "recursive force delete on root/home"

# --- Git: force push ---
echo "$CMD" | grep -qE 'git\s+push\s+.*--force' && block "git push --force"
echo "$CMD" | grep -qE 'git\s+push\s+.*-f' && block "git push -f"

# --- Git: hard reset ---
echo "$CMD" | grep -qE 'git\s+reset\s+--hard' && block "git reset --hard"

# --- Git: discard all changes ---
echo "$CMD" | grep -qE 'git\s+checkout\s+\.' && block "git checkout . (discards all changes)"
echo "$CMD" | grep -qE 'git\s+restore\s+\.' && block "git restore . (discards all changes)"

# --- Git: force-delete branch ---
echo "$CMD" | grep -qE 'git\s+branch\s+-D' && block "git branch -D (force delete)"

# --- Git: clean untracked ---
echo "$CMD" | grep -qE 'git\s+clean\s+-[a-zA-Z]*f' && block "git clean -f (deletes untracked files)"

# --- Database destruction ---
echo "$CMD" | grep -qiE '(DROP\s+(TABLE|DATABASE|SCHEMA))' && block "DROP TABLE/DATABASE/SCHEMA"

# --- Process killers (broad) ---
echo "$CMD" | grep -qE '(killall|pkill)\s' && block "killall/pkill"

# All clear
exit 0

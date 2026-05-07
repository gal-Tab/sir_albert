---
name: git-guardrails
description: >
  Install a PreToolUse hook that blocks dangerous git commands before they execute —
  force pushes, hard resets, branch deletions, working-tree nukes, and more.
  Use this skill whenever the user asks to set up git safety rules, git guardrails,
  protect a repo from destructive git commands, or mentions wanting to prevent
  accidental git disasters. Also use when someone says "install git hooks",
  "block dangerous git", "safe git setup", or anything about preventing force push,
  hard reset, or accidental branch deletion in Claude Code.
---

# Git Guardrails

This skill installs a **PreToolUse hook** in Claude Code that intercepts Bash
commands before execution and blocks dangerous git operations. Unlike prompt-level
instructions (which Claude can occasionally ignore under pressure), hooks are a
hard technical gate — the command physically cannot run.

## What gets blocked by default

The default blocklist covers the operations that most commonly cause irreversible
damage when an AI assistant runs them without thinking:

| Pattern | Why it's dangerous |
|---|---|
| `git push` | Pushes untested or unreviewed code; `--force` rewrites remote history |
| `git reset --hard` | Destroys uncommitted work with no recovery path |
| `git clean -f` | Permanently deletes untracked files |
| `git checkout .` | Silently discards all unstaged changes |
| `git restore .` | Same effect as checkout — wipes working tree changes |
| `git branch -D` | Force-deletes a branch even if unmerged |
| `git stash drop` | Permanently destroys a stash entry |
| `git rebase` (on shared branches) | Rewrites history, causes havoc when pushed |

The hook matches these patterns using simple substring/prefix checks in a shell
script, so it's fast and transparent — you can read exactly what it does.

## Installation

When the user asks you to install git guardrails, follow these steps:

### Step 1: Ask where to install

The hook can live in two places:

- **Project-local** (`.claude/settings.json`) — only affects this repo. Good for
  trying it out or when different projects need different rules.
- **Global** (`~/.claude/settings.json`) — protects every repo you work in.

Ask the user which they prefer. Default to project-local if they don't have a
preference.

### Step 2: Copy the hook script

Copy `scripts/block-dangerous-git.sh` to the target location:

- For project-local: `.claude/hooks/block-dangerous-git.sh`
- For global: `~/.claude/hooks/block-dangerous-git.sh`

Make it executable:

```bash
chmod +x <path>/block-dangerous-git.sh
```

### Step 3: Register the hook

Add the PreToolUse hook entry to the chosen settings file. The hook fires on
every Bash tool call and checks whether the command matches a blocked pattern.

For **project-local** (`.claude/settings.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

For **global** (`~/.claude/settings.json`), use the absolute path:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

If the settings file already exists and has other hooks, merge the new entry into
the existing `PreToolUse` array — don't overwrite what's already there.

### Step 4: Show the user what's configured

After installation, print a summary:

```
Git guardrails installed!

Blocked commands:
  - git push (all variants)
  - git reset --hard
  - git clean -f / -fd
  - git checkout .
  - git restore .
  - git branch -D
  - git stash drop
  - git rebase (interactive and non-interactive)

Location: .claude/hooks/block-dangerous-git.sh
Settings: .claude/settings.json

To customize, edit the BLOCKED_PATTERNS array in the hook script.
```

### Step 5: Offer customization

Ask the user if they want to adjust the defaults:

- **Remove a pattern**: Maybe they do want Claude to push (e.g., to a feature
  branch). They can remove `git push` from the blocklist entirely, or refine it
  to only block `git push --force` and `git push.*main`.
- **Add a pattern**: Maybe they want to also block `git merge --no-ff` or
  `git tag -d` or something project-specific.
- **Allowlist specific commands**: The script supports an `ALLOWED_PATTERNS`
  array. For example, you could block all `git push` but allow
  `git push origin feature/`.

Walk the user through editing the `BLOCKED_PATTERNS` and `ALLOWED_PATTERNS`
arrays in the shell script. The format is simple — one pattern per line, using
bash pattern matching (not regex).

## How the hook script works

The script receives the tool input as JSON on stdin. It extracts the `command`
field, then checks it against two lists:

1. **ALLOWED_PATTERNS** — checked first. If the command matches any allowed
   pattern, it passes through even if it also matches a blocked pattern.
   This is how you create exceptions (e.g., "block all pushes except to my
   feature branch").

2. **BLOCKED_PATTERNS** — checked second. If the command matches any blocked
   pattern, the script exits with a JSON `"decision": "block"` response and
   a human-readable reason. Claude sees the block message and knows it cannot
   run that command.

If neither list matches, the command runs normally.

## Troubleshooting

- **Hook not firing**: Check that the settings file is valid JSON and that the
  path to the script is correct. Run `cat .claude/settings.json | python3 -m json.tool`
  to validate.
- **Wrong commands blocked**: Read through `block-dangerous-git.sh` and check
  the pattern matching. The script uses `case` statements with glob patterns,
  so `git push*` matches `git push origin main --force`.
- **Want to temporarily disable**: Rename the script (e.g., add `.bak`) or
  remove the hook entry from settings. Don't delete the script — you'll want
  it back.

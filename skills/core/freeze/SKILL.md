---
name: freeze
description: >
  Scope Edit/Write to a directory during debugging or investigation so
  unrelated files are not accidentally modified.
  Use when the user says "/freeze", "/freeze <path>", "freeze this path",
  "scope edits to", "lock to this dir", "/unfreeze", "freeze off".
argument-hint: "absolute path to freeze, or 'off' / empty to unfreeze"
---

# Freeze

Boot from `os/PREAMBLE.md`.

**Purpose:** during a debugging or investigation session, restrict Edit and Write tool calls to a declared directory (or set of directories). Unrelated files cannot be "helpfully" modified while freeze is active. This is a lightweight gstack on top of the existing `guard.sh` PreToolUse hook.

---

## Commands

### `/freeze <path>` — activate

1. Resolve `<path>` to an absolute path.
2. Write it to `.memory-bank/.freeze` (one absolute path per line). If the file already exists, overwrite it with the new path(s).
3. Confirm: `Freeze active — edits restricted to: <path>`.

**Multiple paths:** run `/freeze` again with a different path, or pass a newline-separated list. The hook allows edits under any listed path.

### `/unfreeze` or `/freeze off` — deactivate

1. Delete `.memory-bank/.freeze`.
2. Confirm: `Freeze lifted — all paths are editable again.`

---

## Enforcement

Enforcement is done by `hooks/freeze-guard.sh` (a PreToolUse hook). The hook:

- Reads the hook JSON from stdin.
- Extracts `tool_input.file_path`.
- If `.memory-bank/.freeze` does not exist → allows (no freeze active).
- If it exists → allows if the target path is under any listed frozen path; blocks with exit 2 otherwise.

The hook fails-open on parse errors so a bug cannot brick all edits.

---

## Activation (live global step — Gal applies this, NOT the agent)

To enable enforcement, add the following snippet to `~/.claude/settings.json` under `hooks`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "/Users/galta/Development/sir_albert/hooks/freeze-guard.sh"
          }
        ]
      }
    ]
  }
}
```

**WARNING — this is a live global-settings change.** Adding this hook affects every Claude Code session on this machine. Apply it only when ready to enforce freeze globally. To disable, remove the entry above from `~/.claude/settings.json`.

If `~/.claude/settings.json` already has a `PreToolUse` array, append the new object to that array rather than replacing it.

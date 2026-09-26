---
title: "Claude Code plugin hooks.json: every event needs the nested hooks wrapper"
type: concept
kw_capture: true
kw_date: 2026-09-26
tags: [claude-code, plugins, hooks, hooks-json, silent-failure, sir-albert]
source_refs:
  - slug: "claude-code-plugin-dir-vs-marketplace-install"
    confidence: INFERRED
created: 2026-09-26
updated: 2026-09-26
---

# Claude Code plugin hooks.json: every event needs the nested hooks wrapper

## Definition
In a plugin's `hooks/hooks.json`, **every** event entry has to be a matcher group of the form `{"matcher"?: "...", "hooks": [{"type": "command", "command": "..."}]}`. This includes events that take no matcher: `SessionStart`, `UserPromptSubmit` and `SessionEnd`.

A flat entry such as `"SessionStart": [{"type": "command", "command": "..."}]` is **silently ignored**. Nothing warns you at load time, the hook never runs, and nothing shows up in stderr.

Correct:
```json
"SessionStart": [ { "hooks": [ { "type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/session_start.py\"" } ] } ]
```

## Context
Found on 2026-09-26 during W3 verification of sir_albert. The router's SessionStart injection, the UserPromptSubmit nudges and SessionEnd session-record had **never fired live**, even though 44 unit tests of the hook scripts passed. The PreToolUse and PostToolUse entries in the same file worked because they already had the wrapper, which made the broken ones harder to spot. session-record had been off without anyone noticing since it moved from `settings.json` into the plugin. Fixed in commit `c4bb8e6`.

Lessons:
- **Unit-testing the hook scripts doesn't prove the wiring works.** Also run a live check: `command claude --plugin-dir <plugins> -p "<prompt>"`, then confirm the injection or nudge shows up in the model's context and any side effect happened (e.g. the log line count went up by exactly 1).
- **Use a quick structural check:** every entry under every event should have a `hooks` key, e.g. `python3 -c "import json;d=json.load(open('hooks/hooks.json'));print({k:[list(e) for e in v] for k,v in d['hooks'].items()})"`.
- **Watch for a missing expected signal.** If a hook's output never appears in session context, suspect the wiring before the script.

## Related Concepts
- --plugin-dir vs marketplace loading: plugin hooks load at session start, so a wiring fix only takes effect in new sessions.

## See Also
- [Claude Code plugin loading: --plugin-dir vs marketplace install](../concepts/claude-code-plugin-dir-vs-marketplace-install.md) [INFERRED]

## Source / Origin
Captured from session on 2026-09-26. It came out of the sir_albert W3 ticket 11 verification, where the router hooks had never actually fired.

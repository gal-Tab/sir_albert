---
name: claude-handoff
description: >
  Hand the current conversation off to a fresh background Claude Code agent that
  picks up the work immediately, in either execution or plan/discovery mode.
  Use this skill whenever the user asks to "hand this off", "spin up a background
  agent", "continue this in the background", "let another session finish this",
  or "hand off to claude".
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

> Ported from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT License, see [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)), adapted for `claude` CLI permission modes.

# Claude Handoff

Write a handoff summary of the current conversation so a fresh agent can continue the work. Instead of saving it, launch a background agent seeded with the summary as its prompt.

## 1. Pick the mode

Decide whether the next session should **execute** (write code, run commands, modify files) or only **plan / discover** (research, investigate, produce a plan or report without touching the repo):

- Ask, does the user's request (or `$ARGUMENTS`) describe *implementing, fixing, building, or shipping* something? → **execution mode**.
- Does it describe *investigating, researching, scoping, or producing a plan/design* without applying it? → **plan/discovery mode**.
- If it's genuinely ambiguous from the conversation, ask the user which mode they want before continuing — don't guess.

| Mode | Flag | Why |
|---|---|---|
| Execution | `--permission-mode bypassPermissions` | The agent runs unattended in the background with no one to answer prompts — it needs to edit files and run commands without stopping to ask. |
| Plan / Discovery | `--permission-mode plan` | The agent should investigate and produce a plan or report only. Keep it in read-only planning mode so it can't touch the repo. |

## 2. Ask which model to use — before launching

Before building the launch command, ask the user which model the background agent should run on (e.g. `sonnet`, `opus`, `haiku`, or a specific model id). Do not default silently: model choice affects both cost and capability for a session that will run unattended. Wait for their answer before proceeding to step 4.

## 3. Write the summary

Include a "suggested skills" section, which suggests skills that the agent should invoke.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information — the summary becomes the agent's prompt.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the summary accordingly.

## 4. Launch

Always pass `-n`/`--name` with a descriptive name (e.g. `--name "Fix login bug"`) — it sets the display name shown in the job list, session picker, and terminal title.

```
claude --bg --name "<descriptive name>" --model <model from step 2> --permission-mode <bypassPermissions|plan, from step 1> "<handoff summary>"
```

It starts in the current working directory and returns immediately; the user manages it with `claude agents`.

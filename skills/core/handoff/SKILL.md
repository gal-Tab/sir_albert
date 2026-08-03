---
name: handoff
description: >
  Wrap the current session for continuity so the user can /clear (or exit) and
  resume cleanly in a fresh session. Writes a prescriptive cold-start handoff doc
  AND a ready-to-paste restart prompt, with real git state auto-captured.
  Use when the user says "hand this off", "write a handoff", "wrap this session",
  "handoff and a restart prompt", "prep to /clear", "session handoff",
  "pause here and let me resume later", "write me a handoff doc", or
  "I want to continue this in a fresh session".
argument-hint: "focus / next task for the resume prompt"
---

# Handoff

Write a prescriptive cold-start handoff doc and a paste-able restart prompt so the
user can `/clear` or exit and resume cleanly without losing context.

**Announce at start:** "I'm using the handoff skill to wrap this session."

**Do NOT confuse with `skills/dev/claude-handoff`** — that skill spawns a background
agent. This skill produces session-continuity artifacts for a human to resume manually.

---

## 1. Boot from the OS preamble

Load `os/PREAMBLE.md` (USER identity + active rules + anti-slop / use-the-skill
contract) before proceeding. This grounds the handoff in who the user is and what
rules apply to their sessions.

---

## 2. Auto-capture git state

Run all of the following and embed the results verbatim in the handoff doc. The user
must not have to type any of this themselves.

```bash
git branch --show-current
git status -sb
git log --oneline -10
git diff --stat $(git merge-base HEAD @{u} 2>/dev/null || git merge-base HEAD origin/main 2>/dev/null || echo HEAD) HEAD 2>/dev/null
```

For open PRs, run:

```bash
gh pr list --state open 2>/dev/null || echo "(gh not available or no open PRs)"
```

If the directory is not a git repo, note that and skip git sections.

---

## 3. Write the handoff doc

Target path: `.memory-bank/HANDOFF-<YYYY-MM-DD>.md` in the current project directory.
Use today's date (YYYY-MM-DD). If `.memory-bank/` does not exist, create it.

### Required sections — in this order

```markdown
# Handoff — <YYYY-MM-DD>

> **TLDR:** <one sentence: what was being worked on and the single most important
> thing the next session needs to know>

## Cold start (do in order)

1. `cd <absolute project path>`
2. `git checkout <branch>`
3. Read: <path/to/most-important-context-file>
4. Read: <this handoff doc>
5. <any must-run setup command, e.g. `nvm use`, `pnpm install`>
6. Open `/sir-albert:resume` to reload state in ≤5 bullets before doing anything.

## Current state

- **Branch:** `<branch>` — <what it contains>
- **Done this session:** <bullets, reference commit hashes or artifact paths — no duplicate prose>
- **In-flight:** <what was started but not finished>
- **Blockers:** <any known blockers>

## Decisions + WHY

<!-- Re-litigating a resolved decision costs sessions. Record it once here. -->

- **<Decision>:** <why this choice was made over alternatives>

## Gotchas / open risks

- <anything that will bite the next session if they don't know it>

## Files to read first

- `<path>` — <why>

## Next task(s)

1. <Concrete first action — specific enough that the next session can start without
   asking clarifying questions>
2. <Second task if applicable>

---

## Git state (auto-captured)

**Branch:** `<branch>`

**Status:**
\`\`\`
<git status -sb output>
\`\`\`

**Recent commits:**
\`\`\`
<git log --oneline -10 output>
\`\`\`

**Diff stat vs merge-base:**
\`\`\`
<git diff --stat output>
\`\`\`

**Open PRs:**
\`\`\`
<gh pr list output>
\`\`\`
```

### Style rules

- **TLDR first.** Put the most important thing at the top.
- **Prescriptive, not descriptive.** Cold start is a numbered list of actions, not a
  narrative of what happened.
- **Reference, don't duplicate.** For PRDs, plans, ADRs, prior handoffs, or long
  decision logs — reference by path or URL. Do NOT paste their content.
- **No slop.** No filler phrases ("as we discussed", "it's worth noting"). Every
  bullet earns its place.

---

## 4. Emit the restart prompt

Immediately after writing the handoff doc, print a fenced code block the user can
copy and paste into a fresh session. It must be self-contained.

````
```
You are resuming work on <repo name>, branch `<branch>`.

Before doing ANYTHING else:
1. Read: .memory-bank/HANDOFF-<YYYY-MM-DD>.md
2. Run /sir-albert:resume to state the plan back in ≤5 bullets.
3. Confirm the next task with me before starting.

Immediate next task: <next task from the handoff doc, one sentence>

Project root: <absolute path>
```
````

If `$ARGUMENTS` were passed, use them as the "immediate next task" wording.

---

## 5. Cross-file durable learnings (conditional)

After emitting the restart prompt, ask yourself: did this session produce durable,
reusable knowledge that would benefit future sessions on different projects — not just
task state?

Examples of durable learnings worth capturing:
- A non-obvious pattern or approach that solved a recurring problem
- A tool or API behavior that isn't obvious from its docs
- A domain concept that clarified a class of decisions

Examples of things that are NOT durable learnings:
- "We renamed file X to Y" (task state — already in the handoff doc)
- "The PR is open" (operational — already in the handoff doc)

If durable learnings exist, invoke `kw-compound` and present the candidate(s) for
approval before filing. Never auto-save to the wiki.

If no durable learnings exist, skip this step silently.

---

## 6. Redact secrets

Before writing the handoff doc and before emitting the restart prompt, scan for:
- API keys, tokens, passwords, connection strings
- Personal email addresses or phone numbers not intended for sharing
- Internal URLs or credentials

Replace any found with `[REDACTED]`. The handoff doc may be pasted into other
tools or shared with teammates.

---

## Completion report

After all steps, confirm to the user:

```
Handoff written: .memory-bank/HANDOFF-<YYYY-MM-DD>.md
Restart prompt: (above — ready to paste)
Wiki compounds: <N filed | none>
```

Do NOT commit the handoff doc unless the user explicitly asks.

---
name: resume
description: >
  Reload the latest handoff for the current project and state the plan back
  concisely before doing anything, so the user gets productive in ≤2 turns
  with zero re-explaining.
  Use when the user says "resume", "/resume", "pick up where we left off",
  "load the handoff", "continue last session", "what were we doing",
  or "reload context".
argument-hint: "(optional) which handoff / what to focus on"
---

# Resume

Reload the latest handoff and state the plan back in ≤5 bullets — BEFORE
taking any other action.

**Announce at start:** "I'm using the resume skill to reload your session."

---

## 1. Boot from the OS preamble

Load `os/PREAMBLE.md` (USER identity + active rules + anti-slop / use-the-skill
contract) before proceeding. This grounds the resumed session in who the user is
and what rules apply.

---

## 2. Find the latest handoff

Look for `.memory-bank/HANDOFF*.md` in the current project directory.

- Sort candidates by filename date (HANDOFF-YYYY-MM-DD.md) or mtime — take
  the most recent.
- If `$ARGUMENTS` names a specific handoff or date, prefer that file.
- **If no handoff exists:** say so plainly, then fall back:
  1. Run `git log --oneline -10` and `git branch --show-current`.
  2. Check for any `.memory-bank/*BUILD*.md` or `.memory-bank/*PLAN*.md` ledger.
  3. Summarise what you find, then ask: "No handoff found — what do you want to
     focus on?"
  Do not proceed past this point until there is something concrete to resume.

---

## 3. Read it fully + confirm working state

1. Read the handoff doc end-to-end.
2. Run:

```bash
git status -sb
git branch --show-current
```

3. Compare the current branch and dirty-file list to what the handoff recorded.
   - **Mismatch** (wrong branch, unexpected dirty files, staged changes not in
     handoff): flag it explicitly before the plan bullets. Example:
     > "Warning: handoff was on `feat/xyz` but you are currently on `main`."
   - **Clean match:** proceed silently.

---

## 4. State the plan back — ≤5 bullets, TLDR first

Before doing anything else, emit a tight recap. No slop, no filler.

Format:

```
**Resuming:** <one-sentence TLDR of what the session was doing>

**Cold-start checklist:**
- [ ] Branch: `<branch>` <(confirm you're on it, or flag mismatch)>
- [ ] <any must-run setup, e.g. `nvm use`, `pnpm install`>

**Next task:** <single concrete action — specific enough to start without clarifying questions>

**Then:** <second task if applicable>

**Watch out for:** <one-liner on the biggest open risk or gotcha, if any>
```

Cap at 5 bullets total. If there is nothing in a slot, omit that line.

---

## 5. Proceed — but respect ask-before-live

After the plan bullets are confirmed (or the user says "go"), begin the next task.

- Do NOT auto-run live or irreversible actions (deploys, migrations, pushes,
  destructive file ops) without confirming first, per `os/rules/autonomy.md`.
- If the next task is ambiguous, ask one focused clarifying question before starting.

---

## Style rules

- **TLDR first.** The user opened a fresh session — orient them in ≤5 seconds.
- **Prescriptive, not descriptive.** Bullets are actions or facts, not narrative.
- **Reference, don't duplicate.** For long docs, reference by path — do not paste
  their content into the recap.
- **No slop.** No "as we discussed", "it's worth noting", or similar filler.
  Every bullet earns its place.

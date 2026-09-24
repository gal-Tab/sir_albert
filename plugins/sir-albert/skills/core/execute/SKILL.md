---
name: execute
description: Use when given a spec and tickets to implement, when asked to "work the tickets", "implement this spec", "execute the plan", or "implement ticket NN". Reads spec + tickets, builds a task graph, dispatches Sonnet subagents to implement each unblocked ticket, and gates all irreversible actions.
---

# execute

Boot from `os/PREAMBLE.md`.

Adapted from Pocock `skills/in-progress/implement-spec` (MIT); see `THIRD_PARTY_NOTICES.md`.

**Announce on invocation:** "I'm using the execute skill. Reading the spec and building the task graph."

---

## Phase 1 — Read and build the task graph

1. Read the spec (usually `docs/specs/YYYY-MM-DD-<topic>.md`).
2. Read all ticket files (`docs/plans/YYYY-MM-DD-<topic>/tickets/NN-<slug>.md`).
3. Build the **task graph**: map each ticket's `Blocked by:` edges to find the **frontier** — the set of tickets with no unmet blockers. These are ready to implement now.
4. State the frontier out loud: "Frontier: tickets 01, 03, 06 (unblocked). Tickets 02, 04, 05 blocked by predecessors."

---

## Phase 2 — Implement the frontier

For each unblocked ticket, launch an **implementer subagent**:
- Model: **Sonnet** (explicitly; do not use Opus for implementation subagents)
- Run in **background** where tickets are independent (no shared files)
- Context: sparse pointers to spec path + ticket path + previous commit hashes. Do NOT duplicate ticket content in the subagent prompt.
- Coordinator stays in main context to answer questions the subagent surfaces
- When an implementer finishes, merge its work and re-evaluate the frontier

**Worktrees and draft PR:** optional — only create a branch + draft PR if the user requests it or the output is a code branch. Most of Gal's work (config, docs, analysis) does not need a PR. Skip unless asked.

---

## CHECKPOINT gates (hard rules — cannot be skipped or auto-approved)

Stop and explicitly ask Gal before any of these actions. Do not proceed autonomously:

| Action | Why it's gated |
|---|---|
| `git push` / push to remote | Irreversible; affects shared state |
| `gh pr create` / open a PR | External visibility |
| `gh pr merge` / merge PR | Code goes to main; cannot un-merge easily |
| Live config apply (n8n, HubSpot, GTM, GA4) | Affects production immediately |
| Deploy to production | Self-explanatory |
| Any delete that clears data | Irreversible |

Format for CHECKPOINT: "**CHECKPOINT:** I'm about to [action]. Shall I proceed? (Affects: [what changes])"

---

## Phase 3 — Complete

- **If output is a code branch:** run `/sir-albert:build` verification step (tests pass, no debug artifacts, PR description written). Then CHECKPOINT before pushing.
- **If output is not a code branch (docs, config, analysis):** run the verification step from the spec's DOD. Show the output. Confirm it matches the spec.
- Report: "All tickets implemented. Frontier is empty. Verification: [result]."

---

## Communication rules

- Subagents communicate via context pointers (spec path, ticket path, commit hash), not inline prose summaries.
- Coordinator does not re-narrate what the subagent did. The commit history is the record.
- If a subagent surfaces a question, the coordinator answers it inline and adds the decision to the relevant ticket file.

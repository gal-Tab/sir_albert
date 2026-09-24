---
title: Docs-layout — output artifact naming conventions
status: stable
owner: gal
sources:
  - W2 core-skills spec 2026-09-24
last_modified: 2026-09-24
stale_after: 2027-09-24
---

# Docs-layout — where output artifacts land

All skills that produce persistent output artifacts MUST follow this layout. Enforced by the
`plan` skill at generation time; cited here so any skill can reference it.

## Artifact paths

| Artifact type | Path pattern | Producer skill |
|---|---|---|
| Design spec | `docs/specs/YYYY-MM-DD-<topic>.md` | `brainstorm` (design mode) |
| Interactive plan (HTML) | `docs/plans/YYYY-MM-DD-<topic>.html` | `plan` |
| Agent-executable tickets | `docs/plans/YYYY-MM-DD-<topic>/tickets/NN-<slug>.md` | `plan` |
| Session handoff | `.memory-bank/HANDOFF-YYYY-MM-DD.md` | `handoff` |

## Naming conventions

- **Slugs:** lowercase-hyphenated, no spaces, no special chars. Example: `add-login-endpoint`.
- **Date prefix:** always `YYYY-MM-DD` (ISO 8601). Required for all specs, plans, and handoffs.
- **Ticket numbering:** two-digit zero-padded `NN` prefix (01, 02 … 99) in the tickets dir.
- **Topic:** brief (3–5 words max) descriptive slug for the subject.

## Separation rule

- Specs are design artifacts. They explain the *why* and the *what*.
- Tickets are execution units. They are the agent's source of truth during a build.
- **Never** write plan tickets inline in a spec. The spec is design; tickets are execution.

## Design spec frontmatter (required)

```yaml
---
status: draft | approved | superseded
date: YYYY-MM-DD
owner: <name>
---
```

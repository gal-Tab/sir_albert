---
title: Autonomy — ask-vs-act tiers + cost guardrails
status: stable
owner: gal-Tab
sources:
  - plan 2026-07-30 (personal-claude-os) · M4.7 / Q5 (defaults; Gal can change thresholds)
last_modified: 2026-07-31
stale_after: 2027-01-31
---

# Autonomy — when to act, when to ask

The judgment layer above `guard.sh` (which is the hard backstop for destructive commands).

## AUTO — act without asking
- Read-only work: reads, searches, analysis, queries that don't write.
- **Drafts** (Slack / LinkedIn / email / PRs) — produced for approval, not sent.
- Dry-runs, non-prod, and local changes.
- Reversible repo work on a branch (commits, `git mv`, backups).

## ASK first — never auto
- **Live-GTM publish** (a tag / container goes live).
- **n8n prod deploy.**
- **External comms actually sent** (Slack / LinkedIn / email to real recipients).
- **Deletes** and **schema / irreversible** changes.
- Anything that spends real money or hits production.

## Cost / parallelism guardrails
- Cap concurrent agent loops at **~3–5** by default.
- Throttle parallel fan-out when axcli budget headroom is low.
- Run `usage-insights` monthly as a spend self-check.

## Note
Defaults per plan Q5. `> TODO(gal): adjust thresholds anytime (e.g. raise the parallelism cap, refine what counts as "external comms").`

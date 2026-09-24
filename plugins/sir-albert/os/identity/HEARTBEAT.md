---
title: HEARTBEAT — cadence spec (one spec, each runtime implements it)
status: draft
owner: gal-Tab
sources:
  - plan 2026-07-30 (personal-claude-os) · M2.1 + M4.5/M4.6
last_modified: 2026-07-31
stale_after: 2027-07-31
---

# HEARTBEAT — cadence

A **spec**, not an implementation. Claude Code implements it via hooks + the retro schedule (M4.5); NanoClaw via its own cron (M4.6). Same file, N readers.

## Every message
- Load `os/PREAMBLE.md` (identity + active rules + settled decisions).
- Honor the contract (output-style · use-the-skill · ask-before-live).

## Daily
- Capture a light session record (project · skills invoked · corrections Gal made · context re-explained) → feeds the retro loop (M4.5).
- Optionally surface a `/resume` nudge when a fresh handoff exists.

## Weekly — the dream cycle (runs on NanoClaw, M4.6)
1. entity/insight sweep → `/wiki-compile`
2. canonicalize `.compound/` drafts (dedup near-duplicate slugs)
3. `stale_after` sweep — flag expired rules / metrics / taxonomies
4. citation + dashboard-link freshness

**Proposes via PR, never publishes.** Quiet-hours + ask-before-live (M4.7) apply.

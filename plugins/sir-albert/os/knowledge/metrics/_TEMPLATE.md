---
title: <Metric name> — attested definition
status: draft
owner: gal-Tab
sources:
  - "<the policy / definition this metric implements>"
  - "canonical spec: <slug>.json (the z2h look_json) — or <slug>.sql"
last_modified: <YYYY-MM-DD>
stale_after: <YYYY-MM-DD>
---

# <Metric name>

## Definition (prose)
<plain-language: what it measures · grain · filters · exclusions · known caveats>

## Canonical spec (attestable)
- Substrate: a z2h **look** (declarative JSON). The `look_json` **is** the attestable artifact — two runs are equal iff their specs match (no SQL-text parsing).
- Spec file (this dir): `<slug>.json` (stored look_json) — or `<slug>.sql` for canonical SQL.
- Attest a run: `python os/knowledge/metrics/attester.py <slug>.json <executed-spec>.json` → nonzero exit on drift.

## Wiring
Runs inside **`data-review`** (M3.2) pre-ship. Drift fails the check → the number is NOT trusted until reconciled. This is what lets agents deliver dashboards without Gal re-checking the numbers.

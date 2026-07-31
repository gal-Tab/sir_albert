---
name: data-review
description: >
  Pre-ship data-quality check before any dashboard or analysis is shared externally. Run this before
  presenting numbers to stakeholders or publishing a dashboard. Triggers on "data-review",
  "check this dashboard before I share", "data quality check", "pre-ship data check",
  "review this analysis", or "is this dashboard ready to share".
---

Boot from `os/PREAMBLE.md`.

# Data Review

A mandatory pre-ship gate. Every dashboard or analysis that leaves your hands gets this review first. Takes ~10 minutes; prevents days of embarrassment.

**Announce at start:** "Running data-review pre-ship check."

---

## Checklist

### 1. Schema + Null-Rate Sanity

- [ ] Key columns exist and have the expected types (no silent type coercions).
- [ ] Null rate on critical fields is within acceptable bounds — flag anything >5% unless the spec says otherwise.
- [ ] Row count is in the expected order of magnitude (no silent filter killing most rows).
- [ ] Date range covers the intended window; no off-by-one at period boundaries.

### 2. Metric-Definition Consistency

- [ ] Every metric name matches the attested spec (`to-prd` or the team-repo definition).
- [ ] Numerator and denominator are explicitly verified (not inferred from column names).
- [ ] Deduplication logic is present where required (e.g. one row per deal, per user, per event).
- [ ] Conversion rate denominators are non-zero; division-by-zero is handled.

### 3. Dashboard-Link Freshness

- [ ] The underlying data source last-refreshed timestamp is visible or verifiable.
- [ ] Scheduled refresh is configured and its next run is within the expected cadence.
- [ ] Any hard-coded date filters in the SQL are intentional and documented.

### 4. Source-Join Correctness

- [ ] Every JOIN has a verified cardinality assumption (1:1, 1:N, N:M — document the expected one).
- [ ] Fan-out risk: if joining on a non-unique key, aggregation is happening *after* the join, not before.
- [ ] Left-join gaps are accounted for: missing rows are expected / filtered / labelled, not silently zero.
- [ ] Cross-source joins use a consistent grain (e.g. both sides are at deal level, not mixed deal/opportunity).

---

## Boil-the-Ocean Default

**Default to the complete cut.** Before sharing, add the breakdown that makes the number meaningful:

- by channel / source
- by segment (SMB / MM / ENT)
- by motion (self-serve / sales-assisted / partner)
- trend vs. plan (actual vs. target, WoW / MoM / QoQ)

The complete cut is usually one more `GROUP BY` clause or one more panel in the dashboard. It almost never materially changes the query cost. Do it. If the audience doesn't need a breakdown, they'll ignore it — but if they do need it and it's missing, you'll be asked for it in the meeting.

---

## Output

After running the checklist, produce a short summary:

```
DATA REVIEW — <dashboard / analysis name>
Date: <today>

PASS / FAIL / WARN items:
- [PASS] Schema: all key columns present, types correct
- [WARN] Null rate on `segment` is 12% — verify if expected
- [PASS] Metric definitions match spec
- [FAIL] LEFT JOIN on `deal_id` has unmapped rows — investigate before sharing

Complete-cut status:
- by channel: YES / NO
- by segment: YES / NO
- by motion: YES / NO
- trend vs. plan: YES / NO

Recommendation: READY TO SHIP / HOLD — fix [issue] first
```

Only ship on READY TO SHIP. A HOLD item is not optional.

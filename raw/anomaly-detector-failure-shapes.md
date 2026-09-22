---
title: "Anomaly Detection: Failure-Shape-Specific Detectors"
type: concept
kw_capture: true
kw_date: 2026-09-22
tags: [anomaly-detection, alerting, monitoring, cusum, statistics, data-quality]
source_refs: []
created: 2026-09-22
updated: 2026-09-22
---

# Anomaly Detection: Failure-Shape-Specific Detectors

## Definition

A metric can fail in distinct *shapes*, and no single statistical detector is good at all of them. Robust alerting uses **one detector per failure shape**, not one blurry "std-dev alert." Three shapes recur:

| Failure shape | Right detector | Baseline |
|---|---|---|
| **Discontinuity / outage** (series drops toward zero) | Absolute floor / expected-vs-actual | Fixed expectation |
| **One-off spike or dip** (single outlier day) | Rolling mean ± k·σ (z-score) | Trailing (adaptive is fine) |
| **Slow steady bleed** (gradual sustained decline) | CUSUM, or anchored week-over-week | **Anchored** N periods back — never trailing |

## Context

Two non-obvious failure modes of the naive "rolling mean ± k·σ" band, which is the default reach for most homegrown alerting:

1. **It understates an outage.** When a series collapses toward zero, its own recent variance collapses too, so the z-score shrinks precisely when the problem is worst. Use an **absolute floor / expected-vs-actual** check for outages, not a distributional band.

2. **It is blind to a slow bleed — the boiling-frog problem.** A trailing-window baseline *drifts down with* a gradual decline (e.g. 3%/week). Every single day looks "normal" relative to a baseline the decline itself has quietly poisoned. The slow-bleed detector's *defining property* is that its baseline is **anchored, not trailing** — the moment the reference window slides with the data, it stops being a trend detector.

Two cheap anchored implementations for the bleed case:
- **CUSUM (cumulative sum):** accumulates each period's below-expected gap; a run of small misses adds up and trips even when no single day looks alarming. Purpose-built for small persistent shifts.
- **Anchored week-over-week:** compare a rolling 7-day average to the 7-day average from 4 and 8 weeks ago. A steady decline compounds until it breaches the fixed anchor.

**Shared false-positive guardrails** across detectors: a minimum absolute-volume floor (low-count slices have meaningless variance), require N consecutive breaches before firing, and exclude the freshest still-settling data (ingestion latency) from the "is this real" judgment.

**Metric choice matters as much as detector choice:** a *ratio* (e.g. logging-rate %) can sit steady while *absolute volume* halves. When the business cost is tied to volume (e.g. events feeding ad-network conversion signal), alert on the absolute count, not the ratio.

## Related Concepts

- CUSUM control charts (SPC / statistical process control)
- Seasonality-aware baselining
- Ad-network relearning windows (business driver for detection latency — a stalled conversion stream can trigger a ±10-day relearning phase and multiply cost-per-lead)

## See Also
- (No existing wiki pages yet — first entry on this topic.)

## Source / Origin
Captured from session on 2026-09-22, designing the alerting PRD for the GTM Event Monitoring dashboard (`gtm_monitoring`). The three-detector framing emerged from a discovery-lens council pushing on "std-dev alerting" as the wrong single primitive, then a direct challenge on how it handles a slow steady decline.

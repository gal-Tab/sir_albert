# os/knowledge/metrics — attested metric definitions (the trust layer)

The 10x task: durable metrics as **attestable** artifacts, so agents can act on numbers without Gal re-verifying them. Kills the "our MQL numbers don't match" fires.

## How it works
- Each metric = an **OKF mirror** (`<slug>.md`, prose + provenance, from `_TEMPLATE.md`) **+** a **canonical spec** (`<slug>.json` z2h `look_json`, or `<slug>.sql`).
- `attester.py` compares an executed spec against the stored canonical and **fails on drift**. It's wired into `data-review` (M3.2) as the pre-ship gate.
- **z2h looks are the ideal substrate** — a look is already a declarative JSON spec, so `look_json` *is* the attestable artifact.
- **Kremer/Snowflake caveat:** its NL→SQL is non-deterministic (same question → slightly different SQL). For metrics that matter, pin a z2h look or store canonical SQL and run it directly — don't trust the NL agent each time.

## Pinning a real metric (needs Gal's z2h)
1. Build/identify the canonical z2h look; save its `look_json` as `<slug>.json` here.
2. `cp _TEMPLATE.md <slug>.md`; fill prose + provenance + `stale_after`.
3. `data-review` runs `attester.py` on each shared number.

`> TODO(gal): pin the first 3 metrics from your real z2h looks — delivery funnel (product→sGTM→GA4), MQL/attribution, tag-blocking scorecard.`

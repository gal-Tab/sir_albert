# 04b — precision report (blocks wiring)

**Blocked by:** 04 (runs the real prompt_router.py matcher, not a copy)
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 2 — Precision gate

## Goal

Run the router over every past user prompt to measure false-positive rate and surface a sample for review before the hook is wired. Target: <15% of prompts fire, no obvious false positives in the sample.

## Steps

1. Write `tools/precision_report.py`:
   ```
   Usage: python3 tools/precision_report.py
   Reads: ~/.claude/projects/**/*.jsonl (user messages, skip /subagents/)
   Reads: plugins/sir-albert/hooks/router_data.json
   Outputs: precision-report-YYYY-MM-DD.txt to docs/plans/2026-09-24-w3-router/
   ```
   Logic:
   - Extract all user prompts (same logic as ticket 04a miner)
   - For each prompt, run every pattern in `router_data.json` (English + Hebrew)
   - Track: total prompts, total matches, matches per intent, first-match distribution
   - For each intent: collect all matching prompts, shuffle, take up to 10 for the sample
   - Print summary table + per-intent sample

2. Run it: `python3 tools/precision_report.py`

3. Review the output:
   - Overall fire rate: if ≥15%, identify the broadest patterns and tighten them in `router_data.json`
   - Per-intent sample: scan 10 matches per route — any obvious false positive (e.g. "execute this SQL" matching the execute route) → tighten that pattern
   - Re-run until <15% overall and samples look clean

4. Save the final report to `docs/plans/2026-09-24-w3-router/precision-report-YYYY-MM-DD.txt`.

5. **Present summary to Gal before proceeding to ticket 06.** If fire rate or samples are unacceptable, iterate on `router_data.json` patterns.

## Definition of Done

- [ ] `tools/precision_report.py` exists and runs
- [ ] Report generated and saved
- [ ] Overall fire rate < 15%
- [ ] No obvious false positives in the per-route 10-sample review
- [ ] Gal has seen the summary (the precision gate is passed)
- [ ] Final `router_data.json` reflects any tightening done during this ticket

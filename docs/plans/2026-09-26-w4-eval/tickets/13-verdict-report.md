# 13 — verdict-report

**Blocked by:** 09, 12
**Spec:** `docs/specs/2026-09-26-w4-eval.md §P2 — Thin A/B replay / Verdict rule`

## Goal
Run the blind judge over all 60 artifacts, generate the final verdict report, and present the result to Gal. The report must explicitly state that uninstalling superpowers is a separate decision requiring Gal's explicit yes, never inferred from a passing score.

## Steps

1. Verify run count before judging:
   Run: `ls docs/plans/2026-09-26-w4-eval/runs/*.json | wc -l` — Expected: **60** exactly. If not 60, stop and report — do not proceed.

2. Run the blind judge:
   Run: `/usr/local/bin/python3.13 plugins/sir-albert/tools/eval/blind_judge.py --runs-dir docs/plans/2026-09-26-w4-eval/runs --out docs/plans/2026-09-26-w4-eval/judgments.jsonl`
   Expected: prints `judged N pairs, 60 judge calls`, exits 0

3. Verify judgment count:
   Run: `wc -l docs/plans/2026-09-26-w4-eval/judgments.jsonl` — Expected: **60** lines (2 orderings × 30 pairs)
   Run: `wc -l docs/plans/2026-09-26-w4-eval/judgments-resolved.jsonl` — Expected: **30** lines (one per pair)

4. Run the verdict:
   Run: `/usr/local/bin/python3.13 plugins/sir-albert/tools/eval/verdict.py --runs-dir docs/plans/2026-09-26-w4-eval/runs --judgments docs/plans/2026-09-26-w4-eval/judgments-resolved.jsonl --sample docs/plans/2026-09-26-w4-eval/sample.jsonl --out-dir docs/plans/2026-09-26-w4-eval`
   Expected: exits 0 (PASS) or exits 1 (FAIL); prints verdict summary; writes `verdict-2026-09-26-<runid>.md`

5. Verify report file created with namespaced filename:
   Run: `ls docs/plans/2026-09-26-w4-eval/verdict-*.md` — Expected: exactly one file, never plain `verdict.md`

6. Read the report and confirm it contains the superpowers-separation paragraph:
   Run: `grep -c "separate.*decision" docs/plans/2026-09-26-w4-eval/verdict-*.md` — Expected: ≥ 1

7. Present verdict to Gal:
   - Copy the `## Verdict`, `## Win-rate`, `## Skill invocation (happy-path)`, and `## Decision on superpowers` sections
   - State whether P2 passed or failed
   - State the measured cost (from RUNLOG.md)
   - If FAIL: list which gate failed and the concrete gap (e.g., "win-rate was 33% vs 40% bar")

## Definition of Done
- [ ] Run count confirmed at exactly 60 before judging proceeds
- [ ] `judgments.jsonl` has 60 entries; `judgments-resolved.jsonl` has 30
- [ ] Verdict report written as `verdict-<date>-<runid>.md` (namespaced, no collision risk)
- [ ] Report contains explicit paragraph on superpowers uninstall being a separate decision
- [ ] Verdict presented to Gal with win-rate, skill-invocation count, total measured cost

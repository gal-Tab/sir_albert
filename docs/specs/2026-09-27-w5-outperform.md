---
status: approved-by-plan 2026-09-27
date: 2026-09-27
owner: Gal
---

# W5 — P3 outperform gates (pre-registered)

## Arms

**Arms (Sonnet 5, frozen SHA):** B = sir_albert only · A = sir_albert + superpowers · S = superpowers only (no `--plugin-dir`; this also drops `kb`, which ships in the sir_albert repo).

## Per-run definitions

**Per run:** `hit` = any Skill call whose `_skill_to_route` equals the prompt's label. `fire` = any Skill call in the `sir-albert:`, `superpowers:` or `kb:` namespaces.

## Gates

**G1 happy-path:** B hit-rate over runs ≥ 80%, and B ≥ S, and B ≥ A.

**G2 router-silent:** B hit-rate > S, and B ≥ A.

**G3 control:** B fire-rate ≤ 10%, and B ≤ S, and B ≤ A.

**G4 quality (judge v2, Opus 5.5, rubric):** B-vs-S win-rate (ties ½) > 50% with a cluster-bootstrap 95% lower bound ≥ 45% (by prompt, 20,000 resamples, seed 0). B-vs-A lower bound ≥ 45%.

## Verdicts

**OUTPERFORM** = G1–G4 all pass. **UNINSTALL-SAFE** = every B-vs-A clause passes (reported separately; the decision stays Gal's).

**ABORT:** run count ≠ 180, unresolved infra errors, or judge_error > 5% of calls. **INCONCLUSIVE:** ties > 50% in either comparison.

## Known limits

**Known limits:** preceding turns capped at 2×500 chars; `--max-turns 12` / $0.60 per-run cap (cut-offs marked to the judge); Opus judging Sonnet; n = 30 prompts.

## Tuning firewall

**Tuning firewall:** tickets 06–11 may read only the W4 `sample.jsonl` (15), `labels.jsonl` (50), and synthetic phrases. Any file matching `*p3*` is off-limits until ticket 12.

## Amendment 1 — held-out source (Gal, 2026-09-27, before any dev-loop result)

**Problem found by ticket 05:** the baseline router matches exactly 102 corpus rows, and the W4 `label-set` took all of them. Excluding all 143 W4 labeled-set rows therefore leaves **0** held-out happy-path candidates.

**Decision (Gal):** "Relax + refresh". P3 candidates exclude only rows that W5 tuning touched:
- every `_hash` in `docs/plans/2026-09-26-w4-eval/labels.jsonl` (the 50 labelled rows)
- every `_hash` in `docs/plans/2026-09-26-w4-eval/sample.jsonl` (the 15 W4 P2 prompts)
- rows where ticket 08's router fires and the baseline router at 1b88127 doesn't (08 eyeballed these)
- every row from session `6834d4ec…` (the W5 planning session itself)

The 93 unlabelled W4 labeled-set rows (77 router-match, 16 task-initiating) never informed any W5 tuning decision, so they are eligible. The corpus was re-extracted on 2026-09-27: 1,938 → 1,992 rows, with 0 harness or agent prompts in the new rows (audited). A backup is at `~/.claude/sir-albert-corpus/corpus.jsonl.bak-20260927-pre-w5`.

The gates G1–G4 are unchanged.

## Amendment 2 — sequential reps and a 2-round dev cap (Gal, 2026-09-27, before any P3 or dev-loop result)

**Why:** cost. Live eval runs are a minor part of the spend, but P3 rep 2 is ~$16 that a clear rep-1 result makes unnecessary.

**P3 runs in two stages:**
1. **Rep 1:** 30 prompts × 3 arms = 90 runs. Compute G1–G4 on rep 1 alone, with the same definitions (the G4 bootstrap is still clustered by prompt).
2. **Rep 2 runs if and only if** any of these holds on rep 1:
   - a gate is within **10 percentage points** of its threshold. This covers G1 B vs 80% and B−S, B−A vs 0; G2 B−S, B−A vs 0; G3 B vs 10% and B−S, B−A vs 0; G4 the lower bound vs 45% and the point estimate vs 50%, for both comparisons
   - either comparison is INCONCLUSIVE (ties > 50%)
   - judge_error > 5%

   Otherwise the rep-1 verdict is final.
3. After rep 2, the verdict is computed on all 180 runs. ABORT's run-count rule becomes: 90 when stopping at rep 1, 180 after rep 2.

**Known cost of this design:** one interim look slightly raises the chance of a false decision near a threshold. The ±10 pp band is chosen to send exactly those cases to rep 2.

**Dev loop (ticket 11):** capped at **2 rounds**, down from 3. After round 2, stop and report to Gal whatever the outcome.

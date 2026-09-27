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

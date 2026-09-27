# 05 — p3-gate-and-heldout

**Blocked by:** 01
**Spec:** creates `docs/specs/2026-09-27-w5-outperform.md`

## Goal
The P3 gates are pre-registered in a committed spec before any tuning result exists, and a held-out test sample of 30 prompts (10 happy / 10 router-silent / 10 control) exists. It is labelled by Gal, disjoint from everything used for tuning, and carries preceding turns.

## Steps
1. Write `docs/specs/2026-09-27-w5-outperform.md` (status: approved-by-plan 2026-09-27). Copy these gates verbatim:
   - **Arms (Sonnet 5, frozen SHA):** B = sir_albert only · A = sir_albert + superpowers · S = superpowers only (no `--plugin-dir`; this also drops `kb`, which ships in the sir_albert repo).
   - **Per run:** `hit` = any Skill call whose `_skill_to_route` equals the prompt's label. `fire` = any Skill call in the `sir-albert:`, `superpowers:` or `kb:` namespaces.
   - **G1 happy-path:** B hit-rate over runs ≥ 80%, and B ≥ S, and B ≥ A.
   - **G2 router-silent:** B hit-rate > S, and B ≥ A.
   - **G3 control:** B fire-rate ≤ 10%, and B ≤ S, and B ≤ A.
   - **G4 quality (judge v2, Opus 5.5, rubric):** B-vs-S win-rate (ties ½) > 50% with a cluster-bootstrap 95% lower bound ≥ 45% (by prompt, 20,000 resamples, seed 0). B-vs-A lower bound ≥ 45%.
   - **OUTPERFORM** = G1–G4 all pass. **UNINSTALL-SAFE** = every B-vs-A clause passes (reported separately; the decision stays Gal's).
   - **ABORT:** run count ≠ 180, unresolved infra errors, or judge_error > 5% of calls. **INCONCLUSIVE:** ties > 50% in either comparison.
   - **Known limits:** preceding turns capped at 2×500 chars; `--max-turns 12` / $0.60 per-run cap (cut-offs marked to the judge); Opus judging Sonnet; n = 30 prompts.
   - **Tuning firewall:** tickets 06–11 may read only the W4 `sample.jsonl` (15), `labels.jsonl` (50), and synthetic phrases. Any file matching `*p3*` is off-limits until ticket 12.
2. Commit the spec alone: `git add docs/specs/2026-09-27-w5-outperform.md && git commit -m "docs(w5): pre-register P3 outperform gates"`. This commit must predate ticket 11's first dev result.
3. Write the failing test in `plugins/sir-albert/tests/eval/test_label_set.py`: `test_label_set_p3_excludes_prior_rows`. Given a corpus fixture and an exclude list, the new subcommand emits no excluded `_hash`. The output also has candidates in all 3 strata, with `preceding_turns` present.
4. Implement `prompt_corpus.py label-set-p3 --exclude <files…> --seed 7`. Exclude every `_hash` in `docs/plans/2026-09-26-w4-eval/labeled-set.jsonl` (all 143, labelled or not) and in `sample.jsonl`. Slice with the **baseline router at 1b88127**, loaded via `git show 1b88127:plugins/sir-albert/hooks/router_data.json`, not the live file (06/08 change it). Emit about 50 candidates: 15 router-match, 25 task-initiating router-silent (reuse the `task_initiating` heuristic), 10 negative-control. Write `docs/plans/2026-09-27-w5-outperform/labeled-set-p3.jsonl` and `labeled-set-p3-checklist.md`, both gitignored (ticket 01).
5. Run the step 3 test. Expected: PASS. Full suite green. `git check-ignore` both output files. Expected: ignored.
6. **CHECKPOINT: Gal labels.** Hand Gal `labeled-set-p3-checklist.md` (valid labels: `brainstorm`, `plan`, `execute`, `debug`, `build`, `handoff`, `none`, `ambiguous`). Stop until Gal returns it.
7. `prompt_corpus.py import-labels` into a separate text-free `docs/plans/2026-09-27-w5-outperform/labels-p3.jsonl` (committed, hashes plus labels only).
8. `prompt_corpus.py sample-p3 --seed 7`: 10 happy (baseline router matched, and the label equals its route), 10 router-silent (baseline router silent, label a task route), and 10 control (label `none`). Rotated h-s-c. Write `sample-p3.jsonl`, gitignored, carrying `preceding_turns`. If any stratum has fewer than 10, report the shortfall and ask Gal to label more. Don't pad from tuning data.
9. Commit: `git add plugins/sir-albert/tools/prompt_corpus.py plugins/sir-albert/tests/ docs/plans/2026-09-27-w5-outperform/labels-p3.jsonl && git commit -m "feat(w5): held-out P3 sample, labelled by Gal, baseline-router slices"`

## Definition of Done
- [ ] Spec commit predates any dev-loop result (check with `git log --format='%h %ci %s'`)
- [ ] `sample-p3.jsonl` has 30 rows, 10 per stratum, 0 overlap with the W4 labeled set or sample
- [ ] Only hash-and-label files are committed; no prompt text is tracked

## CHECKPOINT
Step 6 needs Gal's labelling time (~50 prompts, ~20 min).

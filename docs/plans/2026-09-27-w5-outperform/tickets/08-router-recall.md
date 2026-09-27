# 08 — router-recall

**Blocked by:** 06 (step 0 only: `p1-score --out`)

## Goal
The router catches more real task prompts, measured on tuning data only, while precision stays ≥ 90% and false fires stay at 0% on P1.

## Why
P1 found 8/14 task prompts in the router's blind spot (6 brainstorm, 2 plan). The `build` route is dead because of vocabulary mismatch ("open pr" / "merge" / "push"). On the 5 router-missed W4 prompts, neither arm fired the labeled skill (A 0/5, B 0/5). This is where B can beat S and A.

## Steps
1. Local analysis only; the text never leaves the machine or enters git. List the `labels.jsonl` rows labelled `brainstorm`/`plan`/`execute`/`build` that the current router misses. Read their text from `docs/plans/2026-09-26-w4-eval/labeled-set.jsonl`, and write the recurring phrasings as **paraphrased, synthetic** trigger phrases into `docs/plans/2026-09-27-w5-outperform/08-phrase-candidates.md`. Commit this file only if it contains no verbatim prompt text; otherwise keep it gitignored.
2. Write the failing tests in `plugins/sir-albert/tests/test_prompt_router.py`, one per new pattern, using the synthetic phrases. Examples: `"what do you think about this approach"` → brainstorm, `"help me figure out how to structure"` → brainstorm, `"break this into steps"` → plan, `"open a pr for this"` → build. Add a negative test for each new pattern, using a near-miss phrase that must stay silent (e.g. `"what do you think?"` alone with no task noun, `"merge conflict in file x"`).
3. Run: `/usr/local/bin/python3.13 -m pytest -q plugins/sir-albert/tests/test_prompt_router.py`. Expected: new FAIL.
4. Add patterns to `plugins/sir-albert/hooks/router_data.json`, in the existing `keyword_patterns` shape with `order` values placed so they don't shadow the existing routes.
5. Run the step 3 command again. Expected: PASS.
6. Gate on P1: `/usr/local/bin/python3.13 plugins/sir-albert/tools/prompt_corpus.py p1-score --out docs/plans/2026-09-27-w5-outperform/p1-scorecard-w5.md`. The `--out` flag comes from ticket 06 step 0. Without it, `p1-score` overwrites the committed W4 record (hard-coded path, `prompt_corpus.py:1084`). Expected: precision ≥ 90%, false-fire 0%, and a miss rate below 57.1%. If precision drops, remove the offending pattern; don't widen the labels.
7. Corpus blast radius: run the router over all 1,938 corpus rows and count new fires per route. Eyeball 10 random new fires per route locally. If more than 2/10 are wrong, tighten the pattern. Record counts only in `docs/plans/2026-09-27-w5-outperform/08-recall-report.md`.
8. Full suite green. Commit: `git commit -m "feat(w5): router recall — brainstorm/plan phrasing, build vocabulary"`

## Definition of Done
- [ ] P1 precision ≥ 90% and false-fire 0%; miss rate < 57.1%
- [ ] Every new pattern has a positive test and a near-miss negative test
- [ ] No prompt text in git; nothing read from `*p3*` files (tuning firewall, spec §Tuning firewall)

⚠️ Risk: overfitting to 50 labels. The held-out P3 is what checks it. Keep patterns phrase-level, not prompt-specific.

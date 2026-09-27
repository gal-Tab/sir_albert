# 06 — imperative-nudge

**Blocked by:** —

## Goal
When the router matches, its output is an explicit instruction to invoke the named skill via the Skill tool before responding, not a bare `→ /sir-albert:plan` arrow.

## Why
In W4 the router fired on 5/5 happy-path prompts, and arm B still skipped the skill on 3 of them. Router precision is 95.2% (P1), which is high enough to justify a directive.

## Steps
0. `p1-score` writes to a hard-coded `docs/plans/2026-09-26-w4-eval/p1-scorecard-2026-09-26.md` (`prompt_corpus.py:1084`), so any re-run overwrites the committed W4 record. Add `--out` (default: the current path) with the test `plugins/sir-albert/tests/eval/test_p1_scorer.py::test_out_flag_writes_elsewhere`. Confirm it fails first, then passes. Commit: `fix(w5): p1-score --out so re-runs don't overwrite the W4 scorecard`.
1. Write the failing tests in `plugins/sir-albert/tests/test_prompt_router.py`:
   - `test_nudge_is_imperative`: `_nudge("write me a plan for the rollout")` contains `Invoke the Skill tool` and `skill="sir-albert:plan"`.
   - `test_nudge_keeps_mode`: `_nudge("attack my plan")` contains `sir-albert:brainstorm` and `attack`.
   - `test_nudge_single_line_short`: output is a single line of ≤ 300 chars.
   - The existing substring tests (`"/sir-albert:brainstorm" in …`) must keep passing. Keep the `/sir-albert:<skill>` token in the text.
2. Run: `/usr/local/bin/python3.13 -m pytest -q plugins/sir-albert/tests/test_prompt_router.py`. Expected: 3 new FAIL.
3. Implement in `plugins/sir-albert/hooks/prompt_router.py`. Leave `router_data.json` nudges untouched, because `prompt_corpus._compile_patterns` parses them into intents. Add `format_directive(nudge)`: parse `→ /sir-albert:<skill>[ <mode>]` and print
   `sir-albert router: this prompt matches /sir-albert:<skill>[ (<mode>)]. Invoke the Skill tool with skill="sir-albert:<skill>" before responding, including before any clarifying question. Skip only if the prompt is clearly not this kind of request.`
   Pass any nudge that doesn't parse through unchanged.
4. Run the step 2 command again. Expected: PASS. Full suite: `/usr/local/bin/python3.13 -m pytest -q plugins/sir-albert/tests/`. Expected: all pass. P1 is unaffected: `prompt_corpus.py p1-score --out /tmp/p1-check.md` gives the same numbers as `p1-scorecard-2026-09-26.md` (95.2% / 0%).
5. Latency: `time (echo '{"prompt":"write me a plan"}' | python3 plugins/sir-albert/hooks/prompt_router.py)`. Expected: < 50 ms.
6. Commit: `git commit -m "feat(w5): router emits an explicit invoke-the-skill directive"`

## Definition of Done
- [ ] New tests fail on the old code and pass on the new code; the suite is green; P1 numbers are unchanged
- [ ] Hook still < 50 ms, no network

⚠️ Risk: live immediately in every new Gal session (`--plugin-dir` working tree). The directive only fires on router matches (precision 95%), so a false fire costs one skill load.

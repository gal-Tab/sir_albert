# 09 — verdict-and-report

**Blocked by:** 08
**Spec:** `docs/specs/2026-09-26-w4-eval.md §P2 — Thin A/B replay / Verdict rule`

## Goal
Write `plugins/sir-albert/tools/eval/verdict.py` that: asserts `ls runs/ | wc -l == 60` and REJECTS the verdict if not; applies the verdict rule (B paired win-rate ≥40%, B invokes a sir_albert skill on ≥4/5 happy-path prompts); and writes a namespaced report file `<name>-<date>-<runid>.md` that can never collide with a prior report.

## Steps

1. Write failing test `plugins/sir-albert/tests/eval/test_verdict.py`:
   - Fixture PASS: 60 fake artifact files + `judgments-resolved.jsonl` with B winning 20 of 30 pairs (win-rate=67%), 4 of 5 happy-path artifacts have `skills_called` containing the skill for their labeled route → exits 0
   - Fixture FAIL_LOADED_ONLY: all 5 happy-path artifacts have 28 `skills_loaded` but empty `skills_called` → must exit 1. This is the regression test for the rigged-gate bug.
   - Fixture FAIL_WRONG_SKILL: `skills_called == ['sir-albert:handoff']` on `plan`-labeled prompts → counts as a miss
   - Fixture FAIL_RUNCOUNT: only 58 artifact files → exits 2, prints `ABORT: run count 58 ≠ 60 — verdict rejected`
   - Fixture FAIL_WINRATE: B wins only 10 of 30 pairs (33%) → exits 1, prints `B FAIL: win-rate 33.3% < 40.0%`
   - Fixture FAIL_SKILLS: B invokes sir_albert skill on only 2 of 5 happy-path prompts → exits 1, prints `B FAIL: sir_albert skill invoked on 2/5 happy-path prompts < 4`

   Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_verdict.py -q` — Expected: FAIL

2. Write `plugins/sir-albert/tools/eval/verdict.py`:
   - Args: `--runs-dir`, `--judgments`, `--sample` (path to `sample.jsonl` to identify happy-path slice), `--out-dir`
   - Run count check: `n = len(list(Path(runs_dir).glob('*.json')))` → if `n != 60: print(f"ABORT: run count {n} ≠ 60 — verdict rejected"); sys.exit(2)`

3. Implement win-rate computation in `verdict.py`:
   - Load `judgments-resolved.jsonl`; count rows where `final_verdict == "B_wins"` as B wins, `"A_wins"` as A wins, `"tie"` as tie
   - Ties split: B effective wins = B_wins + ties/2
   - Win rate = B effective wins / total pairs (30)
   - Gate: `if win_rate < 0.40: print(f"B FAIL: win-rate {win_rate:.1%} < 40.0%"); verdict = "FAIL"`

4. Implement skill invocation check in `verdict.py`:
   - Load `sample.jsonl`; filter rows where `slice == "router_match"` (B routes, label agrees = happy-path)
   - For each happy-path prompt_hash, load arm B artifacts; the prompt counts only if an artifact's `skills_called` (NOT `skills_loaded`) contains a skill that maps to **that prompt's labeled route**, via `prompt_corpus._skill_to_route(slug) == label`. Any-skill-fired is not enough: `sir-albert:handoff` firing on a `plan` prompt is a miss. Reuse `_skill_to_route`; do not write a new regex.
   - Count: how many of the 5 happy-path prompts had a skill invocation
   - Gate: `if skill_count < 4: print(f"B FAIL: sir_albert skill invoked on {skill_count}/5 happy-path prompts < 4"); verdict = "FAIL"`

5. Implement namespaced report filename:
   - `run_id = hashlib.sha256(open(runs_dir).parent.name.encode()).hexdigest()[:8]` (or derive from the run manifest pin_sha)
   - Report path: `f"{out_dir}/verdict-{date.today()}-{run_id}.md"` — never plain `verdict.md`
   - Verify no collision: `if Path(report_path).exists(): report_path = f"{out_dir}/verdict-{date.today()}-{run_id}-2.md"`

6. Write the verdict report in `verdict.py`:
   - `## Verdict: PASS / FAIL`
   - `## Run audit`: `ls runs/ | wc -l` == 60, confirmed
   - `## Win-rate`: table showing A wins / B wins / ties / B win-rate
   - `## Skill invocation (happy-path)`: per-prompt table
   - `## Decision on superpowers`: **explicit paragraph**: `"A passing verdict does NOT mean superpowers should be uninstalled. That is a separate, explicit decision by Gal, taken after reading this report. It is never inferred from a passing score."`
   - Exit 0 on PASS, exit 1 on FAIL (not exit 2 — that is reserved for ABORT/audit failure)

7. Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_verdict.py -q` — Expected: PASS

## Definition of Done
- [ ] `verdict.py` exits 2 if run count ≠ 60 (ABORT, verdict rejected)
- [ ] Exits 1 if either verdict gate fails (FAIL)
- [ ] Exits 0 if both gates pass (PASS)
- [ ] Report filename is namespaced `verdict-<date>-<runid>.md`; never plain `verdict.md`
- [ ] Report contains the explicit paragraph stating uninstalling superpowers is a separate decision
- [ ] Tests pass: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_verdict.py -q`

## Review corrections (binding, supersede the steps above where they conflict)

1. **Per-slice win-rate.** Report B's win-rate and tie count for each `p2_slice` (`happy_path` / `b_silent` / `control`, joined from `sample.jsonl`), as well as the pooled figure. The gate stays pooled at ≥40%.
2. **Tie-heavy → INCONCLUSIVE.** If ties are more than 50% of pairs, the verdict is `INCONCLUSIVE` (exit 3), never PASS. Ties count 0.5, so a tie-heavy run drifts to 50% and would pass the 40% gate by default. Exit codes: 0 PASS · 1 FAIL · 2 ABORT · 3 INCONCLUSIVE.
3. **Judge errors.** `judge_error` pairs are excluded from the denominator and reported separately. More than 3 → ABORT (exit 2).
4. Fixtures: all-ties → exit 3; 4 judge_error pairs → exit 2.

# 01 — replay-with-context

**Blocked by:** —
**Spec:** `docs/specs/2026-09-27-w5-outperform.md §Replay` (written in 05; this plan's header is the interim source)

## Goal
A mid-thread prompt is replayed with its preceding turns as context, identically for every arm, and the router hook still sees only the prompt itself. Proven end-to-end on one live arm-B run of prompt `aef6880dbd5903c4` (a W4 happy-path miss).

## Why
All 5 W4 happy-path prompts had `preceding_turns` in the corpus but were replayed bare. B's "nothing has been shared yet" answers were correct on broken inputs. The W4 skill-gate result is not evidence about sir_albert.

## Steps
0. Confirm you're on local branch `w5/outperform` (created off `w4/eval` with the plan commit; never pushed): `git branch --show-current`.
1. Probe the flag (≤$0, no model call): `bash plugins/sir-albert/tools/eval/guarded.sh command claude --help | grep -n -- '--append-system-prompt'`, then `grep '"model"' ~/.claude/settings.json` (expect `claude-opus-5-5[1m]`). Expected: the flag is listed. If it is absent, stop and report. The fallback (a context block prepended to stdin) would put the context in front of the router, which is a confound. That design change is Gal's call.
2. `.gitignore`: append `docs/plans/2026-09-27-w5-outperform/runs*/`, `docs/plans/2026-09-27-w5-outperform/*sample*.jsonl`, `docs/plans/2026-09-27-w5-outperform/labeled-set-p3*`, `docs/plans/2026-09-27-w5-outperform/judgments*.jsonl`, `docs/plans/2026-09-27-w5-outperform/context/`. Run `git check-ignore -v docs/plans/2026-09-27-w5-outperform/runs-dev/x.json`. Expected: matched.
3. Write the failing test in `plugins/sir-albert/tests/eval/test_run_executor.py`: `test_context_goes_to_system_prompt_not_stdin`. Call `run_one.sh` with a 6th arg (a JSON file of `[{"role":"user","text":"earlier Q"},{"role":"assistant","text":"earlier A"}]`) and a stub claude that dumps argv and stdin to files. Assert that argv contains `--append-system-prompt` followed by a string containing `User: earlier Q` and `Assistant: earlier A`, and that stdin equals the bare prompt exactly.
4. Write the failing test `test_no_context_arg_is_unchanged`: with 5 args, argv has no `--append-system-prompt`. This keeps W4 reproducible.
5. Run: `/usr/local/bin/python3.13 -m pytest -q plugins/sir-albert/tests/eval/test_run_executor.py -k context`. Expected: FAIL (the first test).
6. Implement in `plugins/sir-albert/tools/eval/run_one.sh`. Add an optional `CONTEXT_FILE="${6:-}"`. When it's set, render it with python3.13 into:
   ```
   This message continues an earlier conversation. The earlier turns (replayed for evaluation; each truncated to 500 chars) were:
   User: …
   Assistant: …
   ```
   Then pass it as `--append-system-prompt "$CTX"` inside the existing command array, built so the value is quoted and never word-split. Record `'context_turns': N` in the artifact JSON.
7. Run the step 5 command again. Expected: PASS. Then run the full suite: `/usr/local/bin/python3.13 -m pytest -q plugins/sir-albert/tests/`. Expected: all pass.
8. `plugins/sir-albert/tools/prompt_corpus.py` `_fmt` (in `cmd_sample_p2`, ~line 1252): add `"preceding_turns": r.get("preceding_turns", [])`. Add the same to the row builder that `cmd_label_set` uses, so labelled rows carry context forward. Test in `plugins/sir-albert/tests/eval/test_p2_sample.py`: `test_sample_rows_carry_preceding_turns`, fixture row with 1 preceding turn. Confirm it FAILS on the old code, then PASSES.
9. Build a dev rundir: `W4_RUNDIR=~/.claude/sir-albert-w5-rundir bash plugins/sir-albert/tools/eval/build_arms.sh`, then `bash plugins/sir-albert/tools/eval/canary_preflight.sh ~/.claude/sir-albert-w5-rundir`. Then `grep '"model"' ~/.claude/settings.json`.
10. Live vertical slice (~$0.10, AUTO: under $1). Write that prompt's `preceding_turns` from `~/.claude/sir-albert-corpus/corpus.jsonl` to `docs/plans/2026-09-27-w5-outperform/context/aef6880dbd5903c4.json`. Then run `W4_ARTIFACT_DIR=docs/plans/2026-09-27-w5-outperform/runs-dev W4_RESTORE_MODEL='claude-opus-5-5[1m]' bash plugins/sir-albert/tools/eval/run_one.sh b aef6880dbd5903c4 1 "<text>" ~/.claude/sir-albert-w5-rundir <ctxfile>`. Drive it from a python3.13 one-liner that reads the text from the corpus, so prompt text never goes on the shell history line.
11. Verify: the artifact's `context_turns` is ≥1, and `assistant_text` no longer says "nothing has been shared" / "no doc…". Record the result, text-free, in `docs/plans/2026-09-27-w5-outperform/01-slice-result.md`.
12. Commit: `git add .gitignore plugins/sir-albert/tools/eval/run_one.sh plugins/sir-albert/tools/prompt_corpus.py plugins/sir-albert/tests/ docs/plans/2026-09-27-w5-outperform/01-slice-result.md && git commit -m "feat(w5): replay mid-thread prompts with preceding turns via system prompt"`

## Definition of Done
- [ ] Both new tests fail on the old code and pass on the new code; the full suite is green
- [ ] Router hook input is unchanged (stdin = bare prompt), proven by a test
- [ ] Live arm-B run of `aef6880dbd5903c4` engages with the earlier context
- [ ] `git ls-files docs/plans/2026-09-27-w5-outperform` shows no text-bearing files

⚠️ Risk: `preceding_turns` holds at most 2 turns of 500 chars each. That's lossy, but it's identical across arms. Record the cap in the spec as a known limitation.

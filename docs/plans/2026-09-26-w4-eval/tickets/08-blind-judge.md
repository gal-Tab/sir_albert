# 08 — blind-judge

**Blocked by:** 07
**Spec:** `docs/specs/2026-09-26-w4-eval.md §P2 — Thin A/B replay / Judging`

## Goal
Write `plugins/sir-albert/tools/eval/blind_judge.py` that performs blind paired preference over the 60 run artifacts: pairs rep-wise (A/rep1 vs B/rep1), judges each pair twice with order swapped for position-bias control, and writes one judgment JSONL per pair. Text-only, no tools.

## Steps

1. Write failing test `plugins/sir-albert/tests/eval/test_blind_judge.py`:
   - Create 4 fake artifact files in `tmp_path/runs/`: `a-abc123-rep1.json`, `b-abc123-rep1.json`, `a-abc123-rep2.json`, `b-abc123-rep2.json` (one prompt, both arms, k=2)
   - Mock the judge LLM call to return a JSON object with `winner: "left"`, `reason: "test reason"`
   - Assert `blind_judge.py` emits 4 judgment JSONL entries (2 pairs × 2 orderings)
   - Assert each entry has keys: `prompt_hash`, `rep`, `ordering`, `winner` (left/right/tie), `reason`, `judge_model`
   - Assert that for a pair where the two orderings disagree (`left` in order 1, `right` in order 2 i.e. both chose the same arm), the final verdict records `tie`

   Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_blind_judge.py -q` — Expected: FAIL

2. Write `plugins/sir-albert/tools/eval/blind_judge.py`:
   - Args: `--runs-dir` (default `docs/plans/2026-09-26-w4-eval/runs`), `--out` (default `docs/plans/2026-09-26-w4-eval/judgments.jsonl`), `--model` (default: read from `model-snapshot.txt`)
   - Load all artifact files, group by `(prompt_hash, rep)` → find pairs where both arm A and arm B artifacts exist
   - For each pair, produce two judge calls (order AB, order BA)

3. Build the anonymized summary in `blind_judge.py` for each arm artifact:
   ```python
   def summarize(artifact: dict) -> str:
       # Final response text lives in the result event (verified against the probe stream).
       # An earlier draft read a nonexistent `stdout_json.messages`: every summary came out empty,
       # every pair a tie, and B landed on exactly 50%, a guaranteed pass of the 40% gate.
       final_text = ((artifact.get("result_event") or {}).get("result") or "")
       if not final_text.strip():
           raise ValueError(f"empty response in {artifact['arm']}-{artifact['prompt_hash']}-rep{artifact['rep']}")
       # Redact arm-identifying strings BEFORE truncating. superpowers instructs the model to announce
       # "Using [skill] to ...", so the raw response text can reveal the arm.
       final_text = re.sub(r'\b(superpowers|sir[-_]albert|kb)(:[\w-]+)?', '[skill]', final_text, flags=re.I)
       return final_text[:1500]
   ```
   - **Skill names are NOT shown to the judge.** `superpowers:*` can only appear in arm A, so showing skill names would tell the judge which side is A. The judge rates only the response. Skill invocation is measured separately, as an observed variable, in ticket 09.
   - **An empty response is an error, never a tie.** The judge pass aborts and lists the empty artifacts. A run that produced no text has to be investigated. Silently scoring it as a tie hands B free points.

4. Implement the judge call in `blind_judge.py` (text-only, no tool use):
   ```python
   JUDGE_PROMPT = """You are judging two AI assistant responses to the same prompt. You do not know which system produced each response.

   Prompt: {prompt}

   Response Left:
   {left}

   Response Right:
   {right}

   Which response is better? Reply with JSON only: {{"winner": "left"|"right"|"tie", "reason": "<one sentence>"}}"""
   ```
   - Call via `subprocess`, **always through `tools/eval/guarded.sh`**. Every spawn resets Gal's model (see `04-probe-results.md`), and judge calls are spawns. Run them sequentially.
   - **Neutral judge settings:** `--setting-sources project,local --settings <judge.json>`, where `judge.json` is a copy of `~/.claude/settings.json` with every `enabledPlugins` value set to `false` and `hooks` set to `{}`. Keep `env`, which carries the axcli gateway config. Without this, the judge inherits Gal's plugins, and the superpowers "use skills" injection would sit in the judge's own context.
   - Flags: `--print --no-session-persistence --output-format json --max-turns 1 --model <snapshot> --max-budget-usd 0.10` plus the tool lockdown. Whether `--disallowedTools '*'` or `--tools ""` actually yields zero tools has to be verified: the DoD below asserts the judge init event shows no tools.
   - Parse JSON from response; extract `winner` and `reason`. Unparseable output is retried once, then recorded as `judge_error`, never as a tie.

5. Implement position-bias resolution in `blind_judge.py`:
   - For a pair judged AB (`call_1_winner`) and BA (`call_2_winner`):
     - If `call_1_winner == "left"` and `call_2_winner == "right"`: arm A won both → final = `A_wins`
     - If `call_1_winner == "right"` and `call_2_winner == "left"`: arm B won both → final = `B_wins`
     - Any other combination (tie in either call, or disagreement): final = `tie`
   - Append to `judgments.jsonl`: `{"prompt_hash":..., "rep":..., "ordering":"AB","winner":"left","reason":"...","judge_model":"..."}`
   - Also write a `judgments-resolved.jsonl` with one row per pair showing the final verdict

6. Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_blind_judge.py -q` — Expected: PASS

7. Dry-run check: `python3 -c "import plugins.sir_albert.tools.eval.blind_judge"` OR `python3 plugins/sir-albert/tools/eval/blind_judge.py --help` — Expected: no import errors

## Definition of Done
- [ ] `blind_judge.py` pairs run artifacts rep-wise, makes 2 judge calls per pair (order AB + order BA)
- [ ] Each judge call produces a `judgments.jsonl` entry with `prompt_hash`, `rep`, `ordering`, `winner`, `reason`, `judge_model`
- [ ] Position-bias resolved: disagreement between orderings → `tie`
- [ ] `judgments-resolved.jsonl` has one final-verdict row per pair
- [ ] Judge call goes through `guarded.sh`; `~/.claude/settings.json` model unchanged after a judge pass
- [ ] Judge runs with neutral settings: its init event shows 0 plugins, 0 skills, 0 tools. Checked once on a single real call before the pass.
- [ ] `summarize()` reads `result_event.result`; test uses the real probe fixture and asserts non-empty text
- [ ] Judge input contains no skill names and no `superpowers`/`sir-albert` strings. Test: build the judge prompt from an arm A fixture that called `superpowers:brainstorming` and assert neither substring appears.
- [ ] Empty response → abort with list; unparseable judge output → `judge_error`, never `tie`
- [ ] `--no-session-persistence`, `--max-budget-usd 0.10` per judge call
- [ ] Tests pass: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_blind_judge.py -q`

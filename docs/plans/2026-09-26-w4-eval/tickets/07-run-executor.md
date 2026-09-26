# 07 — run-executor

**Blocked by:** 05, 06
**Spec:** `docs/specs/2026-09-26-w4-eval.md §P2 — Thin A/B replay / Run configuration`

## Goal
Write `run_one.sh` that executes one arm/prompt/rep combination and writes exactly one artifact `docs/plans/2026-09-26-w4-eval/runs/<arm>-<prompt_hash>-rep<k>.json`. Every `command claude` call is wrapped in `guarded.sh`. Output format is `--output-format stream-json --verbose --include-hook-events` so the artifact captures the init event (plugins loaded) and the result event (`total_cost_usd`, `num_turns`, `is_error`, `result`). Per-run ceiling is `--max-budget-usd 0.60`. Runs are strictly sequential. The script also handles the SessionEnd hook side-effect: after each run, it backs up `~/.claude/sir-albert-sessions.jsonl` and strips harness rows (those with `cwd` matching the scratch cwd).

## Steps

1. Write failing test `plugins/sir-albert/tests/eval/test_run_executor.py`:
   - Mock `subprocess.run` to return fake stream-json lines (init event + result event)
   - Assert output file is written at correct path with required keys:
     `arm`, `prompt_hash`, `rep`, `prompt_text`, `model`, `exit_code`, `timestamp_utc`, `cost_usd`, `turn_count`, `budget_capped`, `result_subtype`, `skills_loaded`, `skills_called`, `init_event`, `result_event`
   - Assert exit 1 if artifact already exists (idempotency guard)
   - Assert runs are NOT backgrounded (grep for `&` in run_one.sh)

   Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_run_executor.py -q` — Expected: FAIL

2. Write `plugins/sir-albert/tools/eval/run_one.sh`:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   # Args: $1=arm (a|b), $2=prompt_hash, $3=rep (1|2), $4=prompt_text, $5=RUNDIR
   ARM=$1; HASH=$2; REP=$3; PROMPT=$4; RUNDIR=$5
   REPO=/Users/galta/Development/sir_albert
   ARTIFACT_DIR="$REPO/docs/plans/2026-09-26-w4-eval/runs"
   mkdir -p "$ARTIFACT_DIR"
   OUT="$ARTIFACT_DIR/$ARM-$HASH-rep$REP.json"
   if [ -f "$OUT" ]; then echo "artifact already exists: $OUT"; exit 1; fi
   MODEL=$(cat "$RUNDIR/model-snapshot.txt")
   MANIFEST=$(cat "$RUNDIR/run-manifest.json")
   ```

3. Implement arm settings selection in `run_one.sh`:
   ```bash
   CLONE_PATH=$(echo "$MANIFEST" | python3 -c "import sys,json; print(json.load(sys.stdin)['clone_path'])")
   SCRATCH_CWD=$(echo "$MANIFEST" | python3 -c "import sys,json; print(json.load(sys.stdin)['scratch_cwd'])")
   if [ "$ARM" = "a" ]; then
     ARM_SETTINGS=$(echo "$MANIFEST" | python3 -c "import sys,json; print(json.load(sys.stdin)['arm_a_settings'])")
   else
     ARM_SETTINGS=$(echo "$MANIFEST" | python3 -c "import sys,json; print(json.load(sys.stdin)['arm_b_settings'])")
   fi
   ```

4. Execute the run in `run_one.sh` (wrapped in guarded.sh, sequential):
   ```bash
   RAW=$(bash plugins/sir-albert/tools/eval/guarded.sh \
     command claude --print \
       --setting-sources project,local \
       --settings "$ARM_SETTINGS" \
       --plugin-dir "$CLONE_PATH/plugins" \
       --model "$MODEL" \
       --max-turns 12 \
       --no-session-persistence \
       --output-format stream-json \
       --verbose \
       --include-hook-events \
       --max-budget-usd 0.60 \
       --disallowedTools Write,Edit,NotebookEdit \
       --cwd "$SCRATCH_CWD" \
       "$PROMPT" 2>&1)
   EXIT_CODE=$?
   ```

5. Parse stream-json and build artifact in `run_one.sh`:
   ```python
   /usr/local/bin/python3.13 << 'PY'
   import json, sys, datetime
   raw = open('/dev/stdin').read()
   lines = [l for l in raw.splitlines() if l.strip()]
   # Parse every line and match on fields, never on raw substrings. Verified against the probe
   # stream: the result event is type=result, subtype=success, so '"subtype":"result"' never matches.
   events = [json.loads(l) for l in lines]
   init_ev = next((e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init'), None)
   result_ev = next((e for e in events if e.get('type') == 'result'), None)
   # skills_loaded: what the arm made AVAILABLE (init event). Used only by the canary (ticket 06).
   skills_loaded = [s if isinstance(s, str) else s.get('name', '') for s in ((init_ev or {}).get('skills') or [])]
   # skills_called: what the model actually INVOKED (Skill tool_use blocks). All namespaces,
   # including superpowers:*, since the judge summaries for BOTH arms read from this field.
   skills_called = [
       b.get('input', {}).get('skill', '')
       for e in events if e.get('type') == 'assistant'
       for b in (e.get('message', {}).get('content') or [])
       if isinstance(b, dict) and b.get('type') == 'tool_use' and b.get('name') == 'Skill'
   ]
   cost = (result_ev or {}).get('total_cost_usd')
   turns = (result_ev or {}).get('num_turns')
   result_subtype = (result_ev or {}).get('subtype')
   budget_capped = 'budget' in str(result_subtype).lower()   # confirm the exact subtype in the pilot
   final_text = (result_ev or {}).get('result', '')
   artifact = {
       'arm': sys.argv[1], 'prompt_hash': sys.argv[2], 'rep': int(sys.argv[3]),
       'prompt_text': sys.argv[4], 'model': sys.argv[5],
       'exit_code': int(sys.argv[6]),
       'timestamp_utc': datetime.datetime.utcnow().isoformat(),
       'cost_usd': cost, 'turn_count': turns, 'budget_capped': budget_capped,
       'result_subtype': result_subtype,
       'skills_loaded': skills_loaded, 'skills_called': skills_called,
       'init_event': init_ev, 'result_event': result_ev
   }
   json.dump(artifact, open(sys.argv[7], 'w'), indent=2)
   PY
   ```
   Call: `echo "$RAW" | /usr/local/bin/python3.13 <script> "$ARM" "$HASH" "$REP" "$PROMPT" "$MODEL" "$EXIT_CODE" "$OUT"`

6. Implement SessionEnd session strip in `run_one.sh` (after artifact written):
   Write `plugins/sir-albert/tools/eval/strip_harness_sessions.py`:
   - Args: `--sessions-file` (default `~/.claude/sir-albert-sessions.jsonl`), `--scratch-cwd`
   - Backs up the file to `~/.claude/sir-albert-sessions.jsonl.bak-TIMESTAMP`
   - Strips rows where `cwd` starts with `scratch_cwd`
   - Rewrites the file in-place with remaining rows
   - Prints `stripped N harness rows, kept M rows`
   Call it **once per tranche** from the tranche driver (tickets 11, 12), never per run — per-run would rewrite Gal's file 60 times and leave 60 backups. No `|| true`: a strip failure must be loud.

7. Write test `plugins/sir-albert/tests/eval/test_strip_sessions.py`:
   - Fixture: 5-row sessions file, 2 rows with `cwd=/tmp/w4-eval-scratch/...`, 3 with other cwds
   - Assert strip removes exactly 2 rows, preserves 3, creates backup

   Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_strip_sessions.py -q` — Expected: PASS

8. Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_run_executor.py plugins/sir-albert/tests/eval/test_strip_sessions.py -q` — Expected: all PASS

9. Dry-run: `bash -n plugins/sir-albert/tools/eval/run_one.sh` — Expected: no errors

## Definition of Done
- [ ] `run_one.sh` writes exactly one artifact per call; exits 1 on duplicate
- [ ] Every `command claude` call wrapped in `guarded.sh`; NO `&` (strictly sequential)
- [ ] Artifact has all required keys: `arm`, `prompt_hash`, `rep`, `prompt_text`, `model`, `exit_code`, `timestamp_utc`, `cost_usd`, `turn_count`, `budget_capped`, `result_subtype`, `skills_loaded`, `skills_called`, `init_event`, `result_event`
- [ ] Parser test runs against the **real probe stream** `/tmp/w4-probe/arm-b.jsonl` (copied into `tests/eval/fixtures/`), asserting `cost_usd == 0.140838` and `turn_count == 1`, so no synthetic fixture can hide a wrong event shape
- [ ] Parser test with a fixture containing one `Skill` tool_use (`sir-albert:plan`) asserts `skills_called == ['sir-albert:plan']` while `skills_loaded` has 28+ entries
- [ ] `budget_capped` derived from `result_subtype`
- [ ] `--cwd "$SCRATCH_CWD"` passed (the git repo with 1 commit)
- [ ] `strip_harness_sessions.py` strips harness rows after each run, creates backup
- [ ] Tests pass: `test_run_executor.py` and `test_strip_sessions.py`

⚠️ Resolved: an earlier draft read `skills_invoked` from the init event, which lists every skill *loaded*. Arm B loads all 28 sir-albert skills on every run, so ticket 09's happy-path gate would have passed 5/5 unconditionally, rigging the verdict. The fields are now split: `skills_loaded` feeds only the canary, and `skills_called`, taken from `Skill` tool_use blocks, feeds the verdict and the judge.

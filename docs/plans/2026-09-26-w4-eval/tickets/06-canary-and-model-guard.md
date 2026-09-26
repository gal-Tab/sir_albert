# 06 — canary-and-model-guard

**Blocked by:** 04, 05
**Spec:** `docs/specs/2026-09-26-w4-eval.md §P2 — Thin A/B replay / Canary preflight`

## Goal
Write a canary preflight script that (a) asserts `~/.claude/settings.json` model == `claude-opus-5-5[1m]` at harness start and aborts otherwise, (b) verifies both arms are wired correctly by asserting on the stream-json init event's `skills` list, and (c) wraps every `command claude` call in `guarded.sh` because axcli rewrites the model in `~/.claude/settings.json` on every spawn — this is the PRIMARY defence, not belt-and-braces. Every `command claude` call is also strictly sequential (no parallel subshells) to ensure the guard restores before the next call begins.

## Model guard context (from ticket 04 probe)
`~/.axcli/bin/claude` is `exec axcli spawn`. axcli rewrites `settings.json["model"]` to `claude-sonnet-5` on every spawn, even `--help` and `--version`. `guarded.sh` (at `plugins/sir-albert/tools/eval/guarded.sh`) snapshots the model before, runs the command, and restores via single-match regex + JSON re-validation on `trap EXIT`.

## Steps

1. Write test `plugins/sir-albert/tests/eval/test_canary.py`:
   - Mock `subprocess.run` for 2 canary calls; return fake stream-json with init event containing `skills` list
   - Arm A mock: `skills` contains `superpowers:brainstorming` and `sir-albert:handoff`; session_start hook_response contains `## sir_albert` and `using-superpowers`
   - Arm B mock: `skills` contains only `sir-albert:handoff` (no superpowers); hook_response contains `## sir_albert` but NOT `using-superpowers`
   - Assert canary exits 0 on correct arms; exits 1 on arm B with superpowers skills; exits 1 on arm A with no sir-albert skills
   - Assert model assertion aborts with "ABORT: model is X, expected claude-opus-5-5[1m]" if wrong model

   Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_canary.py -q` — Expected: FAIL

2. Write `plugins/sir-albert/tools/eval/canary_preflight.sh` that reads `RUNDIR` from `$1`:
   - **Step A — Model assertion:** snapshot model from `~/.claude/settings.json`; assert `== "claude-opus-5-5[1m]"`. If not: `echo "ABORT: model is $MODEL, expected claude-opus-5-5[1m]"; exit 1`. Write `$RUNDIR/model-snapshot.txt`.
   - Load manifest: parse `$RUNDIR/run-manifest.json` → `CLONE_PATH`, `ARM_A_SETTINGS`, `ARM_B_SETTINGS`, `SCRATCH_CWD`

3. Implement arm B canary in `canary_preflight.sh`:
   ```bash
   ARM_B_OUT=$(bash plugins/sir-albert/tools/eval/guarded.sh \
     command claude --print \
       --setting-sources project,local \
       --settings "$ARM_B_SETTINGS" \
       --plugin-dir "$CLONE_PATH/plugins" \
       --model "claude-opus-5-5[1m]" \
       --max-turns 1 \
       --no-session-persistence \
       --output-format stream-json \
       --verbose \
       --include-hook-events \
       --max-budget-usd 0.25 \
       --disallowedTools Write,Edit,NotebookEdit \
       --cwd "$SCRATCH_CWD" \
       "write handoff" 2>&1)
   ```
   Parse init event: `echo "$ARM_B_OUT" | python3 -c "import sys,json; [...]"` — extract `skills` list from the `{"type":"system","subtype":"init"}` line
   - Assert `superpowers:` skills count == 0: `echo "ABORT: arm B has superpowers skills"; exit 1`
   - Assert `sir-albert:` skills count > 0: `echo "ABORT: arm B has no sir-albert skills"; exit 1`
   - Assert `## sir_albert` in `hook_response` of the SessionStart event
   - Assert `using-superpowers` NOT in any event
   - Success: `echo "Canary B PASS: 0 superpowers, N sir-albert skills"`

4. Implement arm A canary in `canary_preflight.sh` (strictly after arm B — sequential):
   ```bash
   ARM_A_OUT=$(bash plugins/sir-albert/tools/eval/guarded.sh \
     command claude --print \
       --setting-sources project,local \
       --settings "$ARM_A_SETTINGS" \
       --plugin-dir "$CLONE_PATH/plugins" \
       --model "claude-opus-5-5[1m]" \
       --max-turns 1 \
       --no-session-persistence \
       --output-format stream-json \
       --verbose \
       --include-hook-events \
       --max-budget-usd 0.25 \
       --disallowedTools Write,Edit,NotebookEdit \
       --cwd "$SCRATCH_CWD" \
       "write handoff" 2>&1)
   ```
   - Assert `superpowers:` skills count > 0: `echo "ABORT: arm A has no superpowers skills"; exit 1`
   - Assert `sir-albert:` skills count > 0: `echo "ABORT: arm A has no sir-albert skills"; exit 1`
   - Assert `## sir_albert` in hook_response
   - Assert `using-superpowers` IS in events (injected by superpowers SessionStart)
   - Success: `echo "Canary A PASS: M superpowers, N sir-albert skills, using-superpowers confirmed"`
   - Final: `echo "Both canaries PASS. Ready for scored runs."`

5. Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_canary.py -q` — Expected: PASS

6. Syntax check: `bash -n plugins/sir-albert/tools/eval/canary_preflight.sh` — Expected: no errors

## Definition of Done
- [ ] Model assertion: aborts with clear message if model ≠ `claude-opus-5-5[1m]`
- [ ] Model snapshotted to `$RUNDIR/model-snapshot.txt` before any canary call
- [ ] Every `command claude` call wrapped in `guarded.sh`
- [ ] All `command claude` calls are strictly sequential (no `&` or background subshells)
- [ ] Arm B canary: asserts 0 superpowers skills, >0 sir-albert skills, `## sir_albert` in hook
- [ ] Arm A canary: asserts >0 superpowers skills, >0 sir-albert skills, `using-superpowers` in events
- [ ] Either failure → `echo ABORT` + exit 1; entire replay is aborted
- [ ] Tests pass: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_canary.py -q`

⚠️ Risk: the init event format (`{"type":"system","subtype":"init","skills":[...]}`) is verified in the probe. If it changes between probe and pilot, the canary assertion will fail — which is the correct behaviour (abort before bad data).

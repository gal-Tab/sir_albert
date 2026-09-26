#!/usr/bin/env bash
# canary_preflight.sh — verify both arms are wired before scored runs.
# Usage: bash canary_preflight.sh <RUNDIR>
# Env overrides (for testing):
#   W4_SETTINGS_FILE  source settings.json (default: ~/.claude/settings.json)
#   W4_CLAUDE_BIN     claude binary (default: command claude)
set -euo pipefail

RUNDIR="${1:?Usage: $0 <RUNDIR>}"
SETTINGS_FILE="${W4_SETTINGS_FILE:-$HOME/.claude/settings.json}"
CLAUDE_BIN="${W4_CLAUDE_BIN:-command claude}"
EVAL_DIR="$(dirname "$0")"

EXPECTED_MODEL="claude-opus-5-5[1m]"

# ── Step A: Model assertion ────────────────────────────────────────────────────
MODEL=$(/usr/local/bin/python3.13 -c "import json; print(json.load(open('$SETTINGS_FILE'))['model'])")
if [ "$MODEL" != "$EXPECTED_MODEL" ]; then
  echo "ABORT: model is $MODEL, expected $EXPECTED_MODEL"
  exit 1
fi
echo "$MODEL" > "$RUNDIR/model-snapshot.txt"
echo "Model snapshot written: $MODEL"

# ── Load manifest ─────────────────────────────────────────────────────────────
MANIFEST="$RUNDIR/run-manifest.json"
CLONE_PATH=$(/usr/local/bin/python3.13 -c "import json; print(json.load(open('$MANIFEST'))['clone_path'])")
ARM_B_SETTINGS=$(/usr/local/bin/python3.13 -c "import json; print(json.load(open('$MANIFEST'))['arm_b_settings'])")
ARM_A_SETTINGS=$(/usr/local/bin/python3.13 -c "import json; print(json.load(open('$MANIFEST'))['arm_a_settings'])")
SCRATCH_CWD=$(/usr/local/bin/python3.13 -c "import json; print(json.load(open('$MANIFEST'))['scratch_cwd'])")

# ── Arm B canary ──────────────────────────────────────────────────────────────
echo "Running arm B canary..."
ARM_B_OUT=$(bash "$EVAL_DIR/guarded.sh" \
  $CLAUDE_BIN --print \
    --setting-sources project,local \
    --settings "$ARM_B_SETTINGS" \
    --plugin-dir "$CLONE_PATH/plugins" \
    --model "$EXPECTED_MODEL" \
    --max-turns 1 \
    --no-session-persistence \
    --output-format stream-json \
    --verbose \
    --include-hook-events \
    --max-budget-usd 0.25 \
    --disallowedTools Write,Edit,NotebookEdit \
    --cwd "$SCRATCH_CWD" \
    "write handoff" 2>&1)

# Parse arm B init event
/usr/local/bin/python3.13 - <<PY
import json, sys

lines = """$ARM_B_OUT""".splitlines()
events = []
for l in lines:
    try:
        events.append(json.loads(l))
    except Exception:
        pass

init_ev = next((e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init'), None)
if not init_ev:
    print("ABORT: arm B init event not found", file=sys.stderr)
    sys.exit(1)

skills = [s if isinstance(s, str) else s.get('name','') for s in (init_ev.get('skills') or [])]
sp_count = sum(1 for s in skills if 'superpowers' in s.lower())
sa_count = sum(1 for s in skills if 'sir-albert' in s.lower() or 'sir_albert' in s.lower())

if sp_count > 0:
    print(f"ABORT: arm B has {sp_count} superpowers skills", file=sys.stderr)
    sys.exit(1)
if sa_count == 0:
    print("ABORT: arm B has no sir-albert skills", file=sys.stderr)
    sys.exit(1)

# Check hook output
all_output = " ".join(str(e.get('output','')) for e in events if e.get('subtype') == 'hook_response')
if '## sir_albert' not in all_output:
    print("ABORT: arm B: ## sir_albert not found in hook output", file=sys.stderr)
    sys.exit(1)
if 'using-superpowers' in all_output:
    print("ABORT: arm B: using-superpowers found in events", file=sys.stderr)
    sys.exit(1)

print(f"Canary B PASS: 0 superpowers, {sa_count} sir-albert skills")
PY

# ── Arm A canary (strictly sequential — after arm B) ─────────────────────────
echo "Running arm A canary..."
ARM_A_OUT=$(bash "$EVAL_DIR/guarded.sh" \
  $CLAUDE_BIN --print \
    --setting-sources project,local \
    --settings "$ARM_A_SETTINGS" \
    --plugin-dir "$CLONE_PATH/plugins" \
    --model "$EXPECTED_MODEL" \
    --max-turns 1 \
    --no-session-persistence \
    --output-format stream-json \
    --verbose \
    --include-hook-events \
    --max-budget-usd 0.25 \
    --disallowedTools Write,Edit,NotebookEdit \
    --cwd "$SCRATCH_CWD" \
    "write handoff" 2>&1)

# Parse arm A init event
/usr/local/bin/python3.13 - <<PY
import json, sys

lines = """$ARM_A_OUT""".splitlines()
events = []
for l in lines:
    try:
        events.append(json.loads(l))
    except Exception:
        pass

init_ev = next((e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init'), None)
if not init_ev:
    print("ABORT: arm A init event not found", file=sys.stderr)
    sys.exit(1)

skills = [s if isinstance(s, str) else s.get('name','') for s in (init_ev.get('skills') or [])]
sp_count = sum(1 for s in skills if 'superpowers' in s.lower())
sa_count = sum(1 for s in skills if 'sir-albert' in s.lower() or 'sir_albert' in s.lower())

if sp_count == 0:
    print("ABORT: arm A has no superpowers skills", file=sys.stderr)
    sys.exit(1)
if sa_count == 0:
    print("ABORT: arm A has no sir-albert skills", file=sys.stderr)
    sys.exit(1)

all_output = " ".join(str(e.get('output','')) for e in events if e.get('subtype') == 'hook_response')
if '## sir_albert' not in all_output:
    print("ABORT: arm A: ## sir_albert not found in hook output", file=sys.stderr)
    sys.exit(1)
if 'using-superpowers' not in all_output:
    print("ABORT: arm A: using-superpowers not found in events", file=sys.stderr)
    sys.exit(1)

print(f"Canary A PASS: {sp_count} superpowers, {sa_count} sir-albert skills, using-superpowers confirmed")
PY

echo "Both canaries PASS. Ready for scored runs."

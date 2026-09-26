#!/usr/bin/env bash
# run_one.sh — execute one arm/prompt/rep and write an artifact JSON.
# Usage: bash run_one.sh <arm> <prompt_hash> <rep> <prompt_text> <RUNDIR>
# Env overrides (for testing):
#   W4_SETTINGS_FILE  source settings.json for guard (default: ~/.claude/settings.json)
#   W4_CLAUDE_BIN     claude binary (default: command claude)
#   W4_ARTIFACT_DIR   where to write artifacts (default: docs/plans/2026-09-26-w4-eval/runs)
set -euo pipefail

ARM="${1:?Usage: $0 arm prompt_hash rep prompt_text RUNDIR}"
HASH="${2:?}"
REP="${3:?}"
PROMPT="${4:?}"
RUNDIR="${5:?}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
ARTIFACT_DIR="${W4_ARTIFACT_DIR:-$REPO_ROOT/docs/plans/2026-09-26-w4-eval/runs}"
CLAUDE_BIN="${W4_CLAUDE_BIN:-command claude}"
EVAL_DIR="$(cd "$(dirname "$0")" && pwd)"   # absolute: the spawn runs from the scratch repo

mkdir -p "$ARTIFACT_DIR"
OUT="$ARTIFACT_DIR/$ARM-$HASH-rep$REP.json"

if [ -f "$OUT" ]; then
  echo "artifact already exists: $OUT"
  exit 1
fi

MODEL=$(cat "$RUNDIR/model-snapshot.txt")
MANIFEST=$(cat "$RUNDIR/run-manifest.json")

CLONE_PATH=$(echo "$MANIFEST" | /usr/local/bin/python3.13 -c "import sys,json; print(json.load(sys.stdin)['clone_path'])")
# Fresh scratch repo per run, under the manifest's scratch dir. Bash is enabled, so a run
# can create files (e.g. `cat > plan.md` when Write is disallowed); a shared cwd would
# hand those to the next run — possibly the other arm. mktemp means no deletes needed.
SCRATCH_ROOT=$(echo "$MANIFEST" | /usr/local/bin/python3.13 -c "import sys,json; print(json.load(sys.stdin)['scratch_cwd'])")
mkdir -p "$SCRATCH_ROOT"
SCRATCH_CWD=$(mktemp -d "$SCRATCH_ROOT/run-$ARM-$HASH-rep$REP.XXXX")
git -C "$SCRATCH_CWD" init -q && git -C "$SCRATCH_CWD" commit -q --allow-empty -m scratch

if [ "$ARM" = "a" ]; then
  ARM_SETTINGS=$(echo "$MANIFEST" | /usr/local/bin/python3.13 -c "import sys,json; print(json.load(sys.stdin)['arm_a_settings'])")
else
  ARM_SETTINGS=$(echo "$MANIFEST" | /usr/local/bin/python3.13 -c "import sys,json; print(json.load(sys.stdin)['arm_b_settings'])")
fi

# Execute run — wrapped in guarded.sh, strictly sequential (no &).
# claude has no --cwd flag, so the spawn runs from the scratch repo. A non-zero exit
# (e.g. budget cap) must still produce an artifact, so it is captured rather than
# allowed to trip `set -e`.
RAW_FILE=$(mktemp -t w4-run-XXXX.jsonl)
trap "rm -f $RAW_FILE" EXIT

EXIT_CODE=0
# The prompt goes in on stdin: as a positional arg it is swallowed by the variadic
# --disallowedTools (verified live 2026-09-26: "Input must be provided...").
(cd "$SCRATCH_CWD" && printf '%s' "$PROMPT" | bash "$EVAL_DIR/guarded.sh" \
  $CLAUDE_BIN --print \
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
    --disallowedTools Write,Edit,NotebookEdit) > "$RAW_FILE" || EXIT_CODE=$?

# The plugin clone is arm B's (and A's) sir_albert. A run that modified it would change
# the treatment for every later run: abort the replay rather than keep measuring.
if [ -n "$(git -C "$CLONE_PATH" status --porcelain 2>/dev/null)" ]; then
  echo "ABORT: plugin clone modified during $ARM-$HASH-rep$REP: $(git -C "$CLONE_PATH" status --porcelain | head -3)" >&2
  exit 4
fi

# Parse stream-json and build artifact
/usr/local/bin/python3.13 - "$ARM" "$HASH" "$REP" "$PROMPT" "$MODEL" "$EXIT_CODE" "$OUT" "$RAW_FILE" <<'PY'
import json, sys, datetime

arm, h, rep, prompt, model, exit_code_str, out_path, raw_file = sys.argv[1:]
lines = [l for l in open(raw_file).read().splitlines() if l.strip()]

events = []
for l in lines:
    try:
        events.append(json.loads(l))
    except Exception:
        pass

init_ev = next((e for e in events if e.get('type') == 'system' and e.get('subtype') == 'init'), None)
result_ev = next((e for e in events if e.get('type') == 'result'), None)

# skills_loaded: what the arm made available (init event). Canary only; not for verdict gate.
skills_loaded = [
    s if isinstance(s, str) else s.get('name', '')
    for s in ((init_ev or {}).get('skills') or [])
]

# skills_called: what the model actually invoked (Skill tool_use blocks).
skills_called = [
    b.get('input', {}).get('skill', '')
    for e in events if e.get('type') == 'assistant'
    for b in (e.get('message', {}).get('content') or [])
    if isinstance(b, dict) and b.get('type') == 'tool_use' and b.get('name') == 'Skill'
]

cost = (result_ev or {}).get('total_cost_usd')
turns = (result_ev or {}).get('num_turns')
result_subtype = (result_ev or {}).get('subtype')
budget_capped = 'budget' in str(result_subtype).lower()

artifact = {
    'arm': arm,
    'prompt_hash': h,
    'rep': int(rep),
    'prompt_text': prompt,
    'model': model,
    'exit_code': int(exit_code_str),
    'timestamp_utc': datetime.datetime.utcnow().isoformat(),
    'cost_usd': cost,
    'turn_count': turns,
    'budget_capped': budget_capped,
    'result_subtype': result_subtype,
    'skills_loaded': skills_loaded,
    'skills_called': skills_called,
    'init_event': init_ev,
    'result_event': result_ev,
}
json.dump(artifact, open(out_path, 'w'), indent=2)
print(f"artifact written: {out_path}")
PY

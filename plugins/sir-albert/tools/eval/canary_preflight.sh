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
EVAL_DIR="$(cd "$(dirname "$0")" && pwd)"   # absolute: we cd into the scratch repo below

EXPECTED_MODEL="claude-opus-5-5[1m]"

# ── Step A: Model assertion ────────────────────────────────────────────────────
MODEL=$(/usr/local/bin/python3.13 -c "import json,sys; print(json.load(open(sys.argv[1]))['model'])" "$SETTINGS_FILE")
if [ "$MODEL" != "$EXPECTED_MODEL" ]; then
  echo "ABORT: model is $MODEL, expected $EXPECTED_MODEL"
  exit 1
fi
echo "$MODEL" > "$RUNDIR/model-snapshot.txt"
echo "Model snapshot written: $MODEL"

# ── Load manifest ─────────────────────────────────────────────────────────────
manifest() { /usr/local/bin/python3.13 -c "import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])" "$RUNDIR/run-manifest.json" "$1"; }
CLONE_PATH=$(manifest clone_path)
SCRATCH_CWD=$(manifest scratch_cwd)

# ── One canary spawn per arm. claude has no --cwd flag: run from the scratch repo.
# Output goes to a file and is parsed from the file — never interpolated into code.
run_canary() {
  local settings="$1" out="$2"
  (cd "$SCRATCH_CWD" && printf '%s' "write handoff" | bash "$EVAL_DIR/guarded.sh" \
    $CLAUDE_BIN --print \
      --setting-sources project,local \
      --settings "$settings" \
      --plugin-dir "$CLONE_PATH/plugins" \
      --model "$EXPECTED_MODEL" \
      --max-turns 1 \
      --no-session-persistence \
      --output-format stream-json \
      --verbose \
      --include-hook-events \
      --max-budget-usd 0.25 \
      --disallowedTools Write,Edit,NotebookEdit) > "$out" 2> "$out.stderr" || true
}

check_arm() {
  /usr/local/bin/python3.13 - "$1" "$2" <<'PY'
import json, sys

arm, path = sys.argv[1], sys.argv[2]
events = []
for line in open(path, encoding="utf-8"):
    try:
        events.append(json.loads(line))
    except ValueError:
        pass

init_ev = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), None)
if not init_ev:
    sys.exit(f"ABORT: arm {arm.upper()} init event not found (see {path}.stderr)")

skills = [s if isinstance(s, str) else s.get("name", "") for s in (init_ev.get("skills") or [])]
sp = sum(1 for s in skills if s.startswith("superpowers:"))
sa = sum(1 for s in skills if s.startswith("sir-albert:"))
hooks = " ".join(str(e.get("output", "")) for e in events if e.get("subtype") == "hook_response")
has_sa, has_sp = "## sir_albert" in hooks, "using-superpowers" in hooks

want_sp = arm == "a"   # arm A = today (both plugins); arm B = today minus superpowers
problems = []
if (sp > 0) != want_sp:
    problems.append(f"{sp} superpowers skills (expected {'>0' if want_sp else '0'})")
if sa == 0:
    problems.append("no sir-albert skills")
if not has_sa:
    problems.append("'## sir_albert' SessionStart injection missing")
if has_sp != want_sp:
    problems.append(f"using-superpowers injection {'missing' if want_sp else 'present'}")
if problems:
    sys.exit(f"ABORT: arm {arm.upper()}: " + "; ".join(problems))
print(f"Canary {arm.upper()} PASS: {sp} superpowers, {sa} sir-albert skills")
PY
}

# Strictly sequential: B, then A.
echo "Running arm B canary..."
run_canary "$(manifest arm_b_settings)" "$RUNDIR/canary-b.jsonl"
check_arm b "$RUNDIR/canary-b.jsonl"

echo "Running arm A canary..."
run_canary "$(manifest arm_a_settings)" "$RUNDIR/canary-a.jsonl"
check_arm a "$RUNDIR/canary-a.jsonl"

echo "Both canaries PASS. Ready for scored runs."

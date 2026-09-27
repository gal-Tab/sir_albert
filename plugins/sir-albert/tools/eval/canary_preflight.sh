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

# Two different models — do not conflate them:
#   GAL_DEFAULT  Gal's default in settings.json; the guard protects it, runs never use it.
#   TEST_MODEL   the model both arms (and the judge) run on. Decided by Gal 2026-09-26.
GAL_DEFAULT="${W4_GAL_DEFAULT:-claude-opus-5-5[1m]}"
TEST_MODEL="${W4_TEST_MODEL:-claude-sonnet-5}"

# ── Step A: Model assertion ────────────────────────────────────────────────────
MODEL=$(/usr/local/bin/python3.13 -c "import json,sys; print(json.load(open(sys.argv[1]))['model'])" "$SETTINGS_FILE")
if [ "$MODEL" != "$GAL_DEFAULT" ]; then
  echo "ABORT: default model in settings is $MODEL, expected $GAL_DEFAULT (drift from an earlier spawn?)"
  exit 1
fi
echo "$TEST_MODEL" > "$RUNDIR/model-snapshot.txt"
echo "Model under test: $TEST_MODEL (Gal's default $MODEL is left alone)"

# ── Load manifest ─────────────────────────────────────────────────────────────
manifest() { /usr/local/bin/python3.13 -c "import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])" "$RUNDIR/run-manifest.json" "$1"; }
CLONE_PATH=$(manifest clone_path)
SCRATCH_CWD=$(manifest scratch_cwd)

# ── One canary spawn per arm. claude has no --cwd flag: run from the scratch repo.
# Output goes to a file and is parsed from the file — never interpolated into code.
# Arm S is sir_albert-free: no --plugin-dir. Two separate code paths to avoid
# bash 3.2 (macOS system bash) empty-array issues with set -u.
run_canary() {
  local arm="$1" settings="$2" out="$3"
  if [ "$arm" = "s" ]; then
    (cd "$SCRATCH_CWD" && printf '%s' "write handoff" | bash "$EVAL_DIR/guarded.sh" \
      $CLAUDE_BIN --print \
        --setting-sources project,local \
        --settings "$settings" \
        --model "$TEST_MODEL" \
        --max-turns 1 \
        --no-session-persistence \
        --output-format stream-json \
        --verbose \
        --include-hook-events \
        --max-budget-usd 0.25 \
        --disallowedTools Write,Edit,NotebookEdit) > "$out" 2> "$out.stderr" || true
  else
    (cd "$SCRATCH_CWD" && printf '%s' "write handoff" | bash "$EVAL_DIR/guarded.sh" \
      $CLAUDE_BIN --print \
        --setting-sources project,local \
        --settings "$settings" \
        --plugin-dir "$CLONE_PATH/plugins" \
        --model "$TEST_MODEL" \
        --max-turns 1 \
        --no-session-persistence \
        --output-format stream-json \
        --verbose \
        --include-hook-events \
        --max-budget-usd 0.25 \
        --disallowedTools Write,Edit,NotebookEdit) > "$out" 2> "$out.stderr" || true
  fi
}

check_arm() {
  /usr/local/bin/python3.13 - "$1" "$2" "$TEST_MODEL" <<'PY'
import json, sys

arm, path, test_model = sys.argv[1], sys.argv[2], sys.argv[3]
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

# arm A: superpowers=true, sir_albert via --plugin-dir
# arm B: superpowers=false, sir_albert via --plugin-dir
# arm S: superpowers=true, NO sir_albert (no --plugin-dir, no SessionStart injection)
want_sp = arm in ("a", "s")
want_sa = arm != "s"   # S must have 0 sir-albert skills

problems = []
if init_ev.get("model") != test_model:
    problems.append(f"init model {init_ev.get('model')!r}, expected {test_model!r}")
if (sp > 0) != want_sp:
    problems.append(f"{sp} superpowers skills (expected {'>0' if want_sp else '0'})")
if want_sa and sa == 0:
    problems.append("no sir-albert skills")
if not want_sa and sa > 0:
    problems.append(f"{sa} sir-albert skills (expected 0 for arm S)")
if want_sa and not has_sa:
    problems.append("'## sir_albert' SessionStart injection missing")
if not want_sa and has_sa:
    problems.append("'## sir_albert' SessionStart injection present (arm S must be sir_albert-free)")
if has_sp != want_sp:
    problems.append(f"using-superpowers injection {'missing' if want_sp else 'present'}")
if problems:
    sys.exit(f"ABORT: arm {arm.upper()}: " + "; ".join(problems))
print(f"Canary {arm.upper()} PASS: {sp} superpowers, {sa} sir-albert skills")
PY
}

# Strictly sequential: B, then A, then S.
echo "Running arm B canary..."
run_canary b "$(manifest arm_b_settings)" "$RUNDIR/canary-b.jsonl"
check_arm b "$RUNDIR/canary-b.jsonl"

echo "Running arm A canary..."
run_canary a "$(manifest arm_a_settings)" "$RUNDIR/canary-a.jsonl"
check_arm a "$RUNDIR/canary-a.jsonl"

# Arm S canary: only runs when arm_s_settings is present in the manifest.
ARM_S_SETTINGS=$(/usr/local/bin/python3.13 -c "import json,sys; print(json.load(open(sys.argv[1])).get('arm_s_settings',''))" "$RUNDIR/run-manifest.json")
if [ -n "$ARM_S_SETTINGS" ]; then
  echo "Running arm S canary..."
  run_canary s "$ARM_S_SETTINGS" "$RUNDIR/canary-s.jsonl"
  check_arm s "$RUNDIR/canary-s.jsonl"
fi

echo "All canaries PASS. Ready for scored runs."

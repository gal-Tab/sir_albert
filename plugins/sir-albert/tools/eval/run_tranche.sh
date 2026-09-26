#!/usr/bin/env bash
# run_tranche.sh — run one P2 replay tranche: rows × {rep1, rep2} × {arm a, arm b}.
# Usage: bash run_tranche.sh <RUNDIR> <SAMPLE_JSONL> <TRANCHE: 1|2>
#   Tranche 1 = sample rows 1-10 (40 runs), tranche 2 = rows 11-15 (20 runs).
# Env overrides (for testing):
#   W4_SETTINGS_FILE  settings.json the model check reads (default: ~/.claude/settings.json)
#   W4_ARTIFACT_DIR   run artifacts (default: docs/plans/2026-09-26-w4-eval/runs)
#   W4_BUDGET_USD     hard cap across ALL artifacts in the dir (default: 40)
#   W4_SESSIONS_FILE  sessions log to strip harness rows from (default: ~/.claude/sir-albert-sessions.jsonl)
#
# Strictly sequential. Resumable: a run whose artifact already exists is skipped.
set -euo pipefail

RUNDIR="${1:?Usage: $0 RUNDIR SAMPLE_JSONL TRANCHE}"
SAMPLE="${2:?}"
TRANCHE="${3:?}"
EVAL_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(git -C "$EVAL_DIR" rev-parse --show-toplevel)"
SETTINGS_FILE="${W4_SETTINGS_FILE:-$HOME/.claude/settings.json}"
ARTIFACT_DIR="${W4_ARTIFACT_DIR:-$REPO_ROOT/docs/plans/2026-09-26-w4-eval/runs}"
BUDGET="${W4_BUDGET_USD:-40}"
SESSIONS_FILE="${W4_SESSIONS_FILE:-$HOME/.claude/sir-albert-sessions.jsonl}"
GAL_DEFAULT="${W4_GAL_DEFAULT:-claude-opus-5-5[1m]}"   # Gal's default: protected, never used for runs
TEST_MODEL="${W4_TEST_MODEL:-claude-sonnet-5}"          # model under test (Gal, 2026-09-26)
PY=/usr/local/bin/python3.13
export W4_ARTIFACT_DIR="$ARTIFACT_DIR"
mkdir -p "$ARTIFACT_DIR"

case "$TRANCHE" in
  1) FIRST=0; LAST=10 ;;
  2) FIRST=10; LAST=15 ;;
  *) echo "ABORT: tranche must be 1 or 2"; exit 2 ;;
esac

# ── Preconditions ─────────────────────────────────────────────────────────────
MODEL_NOW=$($PY -c "import json,sys; print(json.load(open(sys.argv[1]))['model'])" "$SETTINGS_FILE")
MODEL_SNAP=$(cat "$RUNDIR/model-snapshot.txt")
if [ "$MODEL_NOW" != "$GAL_DEFAULT" ] || [ "$MODEL_SNAP" != "$TEST_MODEL" ]; then
  echo "ABORT: model settings=$MODEL_NOW (want $GAL_DEFAULT) snapshot=$MODEL_SNAP (want $TEST_MODEL)"; exit 2
fi
for a in a b; do
  [ -s "$RUNDIR/canary-$a.jsonl" ] || { echo "ABORT: canary for arm $a has not run (canary_preflight.sh)"; exit 2; }
done

# spent: sum of cost_usd over every artifact in the dir (both tranches count toward the cap)
spent() { $PY -c "
import json,glob,sys
print(round(sum(json.load(open(f)).get('cost_usd') or 0 for f in glob.glob(sys.argv[1]+'/*.json')),4))" "$ARTIFACT_DIR"; }

# rows: 'hash<TAB>prompt-json' for this tranche; the prompt stays JSON-encoded until run time
ROWS=$($PY -c "
import json,sys
rows=[json.loads(l) for l in open(sys.argv[1]) if l.strip()][int(sys.argv[2]):int(sys.argv[3])]
for r in rows: print(r['_hash']+'\t'+json.dumps(r['text']))" "$SAMPLE" "$FIRST" "$LAST")
N_ROWS=$(printf '%s\n' "$ROWS" | grep -c . || true)
[ "$N_ROWS" -eq $((LAST-FIRST)) ] || { echo "ABORT: tranche $TRANCHE expects $((LAST-FIRST)) sample rows, found $N_ROWS"; exit 2; }

echo "tranche $TRANCHE: $N_ROWS prompts x 2 reps x 2 arms = $((N_ROWS*4)) runs | spent so far \$$(spent) of \$$BUDGET"

# ── Runs: per prompt, interleave arms within each rep (a1 b1 a2 b2) ─────────────
i=0
while IFS=$'\t' read -r HASH PROMPT_JSON; do
  PROMPT=$($PY -c "import json,sys; print(json.loads(sys.argv[1]), end='')" "$PROMPT_JSON")
  for REP in 1 2; do
    for ARM in a b; do
      i=$((i+1))
      if [ -f "$ARTIFACT_DIR/$ARM-$HASH-rep$REP.json" ]; then
        echo "[$i] skip $ARM-$HASH-rep$REP (artifact exists)"; continue
      fi
      NOW=$(spent)
      if $PY -c "import sys; sys.exit(0 if float(sys.argv[1]) + 0.60 > float(sys.argv[2]) else 1)" "$NOW" "$BUDGET"; then
        echo "ABORT: spent \$$NOW + next run's \$0.60 cap would exceed \$$BUDGET"; exit 3
      fi
      RC=0
      bash "$EVAL_DIR/run_one.sh" "$ARM" "$HASH" "$REP" "$PROMPT" "$RUNDIR" >/dev/null || RC=$?
      if [ "$RC" -ne 0 ]; then
        echo "ABORT: run_one.sh exit $RC on $ARM-$HASH-rep$REP"; exit "$RC"
      fi
      echo "[$i] $ARM-$HASH-rep$REP done | spent \$$(spent)"
      # Extrapolation gate after the first 10 runs of tranche 1 (spec §Budget cap)
      if [ "$TRANCHE" = 1 ] && [ "$i" -eq 10 ]; then
        if $PY -c "import sys; sys.exit(0 if float(sys.argv[1])/10*60 > float(sys.argv[2]) else 1)" "$(spent)" "$BUDGET"; then
          echo "ABORT: first 10 runs cost \$$(spent), extrapolates past \$$BUDGET for 60 runs"; exit 3
        fi
      fi
    done
  done
done <<< "$ROWS"

# ── Wrap-up ───────────────────────────────────────────────────────────────────
SCRATCH_ROOT=$($PY -c "import json,sys; print(json.load(open(sys.argv[1]))['scratch_cwd'])" "$RUNDIR/run-manifest.json")
if [ -f "$SESSIONS_FILE" ]; then
  $PY "$EVAL_DIR/strip_harness_sessions.py" --sessions-file "$SESSIONS_FILE" --scratch-cwd "$SCRATCH_ROOT"
fi
echo "tranche $TRANCHE complete: $(ls "$ARTIFACT_DIR"/*.json | wc -l | tr -d ' ') artifacts | spent \$$(spent) of \$$BUDGET"

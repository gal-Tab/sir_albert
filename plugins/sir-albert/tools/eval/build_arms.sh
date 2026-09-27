#!/usr/bin/env bash
# build_arms.sh — create arm A / arm B settings files and run manifest.
# Supports env overrides for testing:
#   W4_REPO          repo path (default: /Users/galta/Development/sir_albert)
#   W4_SETTINGS_FILE source settings.json (default: ~/.claude/settings.json)
#   W4_RUNDIR        output directory (default: mktemp -d)
#   W4_CLONE_PATH    clone target (default: /tmp/w4-arm-clone-<sha>)
#   W4_SCRATCH_CWD   scratch git repo (default: /tmp/w4-eval-scratch)
set -euo pipefail

REPO="${W4_REPO:-/Users/galta/Development/sir_albert}"
SRC_SETTINGS="${W4_SETTINGS_FILE:-$HOME/.claude/settings.json}"
SCRATCH_CWD="${W4_SCRATCH_CWD:-/tmp/w4-eval-scratch}"

# ── Pin SHA ────────────────────────────────────────────────────────────────────
PIN_SHA=$(git -C "$REPO" rev-parse HEAD)
CLONE_PATH="${W4_CLONE_PATH:-/tmp/w4-arm-clone-${PIN_SHA:0:12}}"
RUNDIR="${W4_RUNDIR:-$(mktemp -d -t w4-e.vl-XXXX)}"

echo "RUNDIR=$RUNDIR"

# ── Generate arm settings files ────────────────────────────────────────────────
/usr/local/bin/python3.13 - "$SRC_SETTINGS" "$RUNDIR/arm-a-settings.json" "true" <<'PY'
import json,sys
src,dst,val=sys.argv[1],sys.argv[2],sys.argv[3]=='true'
s=json.load(open(src))
s.setdefault('enabledPlugins',{})['superpowers@claude-plugins-official']=val
json.dump(s,open(dst,'w'),indent=2)
PY

/usr/local/bin/python3.13 - "$SRC_SETTINGS" "$RUNDIR/arm-b-settings.json" "false" <<'PY'
import json,sys
src,dst,val=sys.argv[1],sys.argv[2],sys.argv[3]=='true'
s=json.load(open(src))
s.setdefault('enabledPlugins',{})['superpowers@claude-plugins-official']=val
json.dump(s,open(dst,'w'),indent=2)
PY

# ── Arm S: superpowers=true, sir_albert-free (no --plugin-dir; SessionStart hooks
#    that inject sir_albert context are stripped so the arm is fully isolated) ─────
/usr/local/bin/python3.13 - "$SRC_SETTINGS" "$RUNDIR/arm-s-settings.json" <<'PY'
import json, sys
src, dst = sys.argv[1], sys.argv[2]
s = json.load(open(src))
s.setdefault('enabledPlugins', {})['superpowers@claude-plugins-official'] = True
# Strip SessionStart hooks whose command references sir_albert so arm S gets no
# sir_albert context injection (skills are excluded by omitting --plugin-dir).
hooks = s.get('hooks', {})
if 'SessionStart' in hooks:
    cleaned = []
    for entry in hooks['SessionStart']:
        inner = [h for h in (entry.get('hooks') or [])
                 if 'sir' not in (h.get('command') or '').lower()]
        if inner:
            cleaned.append(dict(entry, hooks=inner))
    hooks['SessionStart'] = cleaned
json.dump(s, open(dst, 'w'), indent=2)
PY
echo "arm-s-settings.json written"

# Verify hooks block preserved
/usr/local/bin/python3.13 -c "import json; s=json.load(open('$RUNDIR/arm-b-settings.json')); assert s.get('hooks') is not None, 'hooks block missing'"
echo "hooks preserved"

# ── Clone repo ─────────────────────────────────────────────────────────────────
if [ ! -d "$CLONE_PATH" ]; then
  git clone --local "$REPO" "$CLONE_PATH"
fi
# Verify not a worktree (.git is a directory, not a file)
test -d "$CLONE_PATH/.git" || { echo "ERROR: .git is not a directory — may be a worktree"; exit 1; }
echo "clone ok: $(git -C "$CLONE_PATH" rev-parse HEAD)"

# ── Create scratch cwd ─────────────────────────────────────────────────────────
mkdir -p "$SCRATCH_CWD"
if [ ! -d "$SCRATCH_CWD/.git" ]; then
  git -C "$SCRATCH_CWD" init -q
  git -C "$SCRATCH_CWD" commit --allow-empty -m "scratch" -q
fi
echo "scratch cwd ok: $SCRATCH_CWD"

# ── Write run-manifest.json ───────────────────────────────────────────────────
/usr/local/bin/python3.13 - "$PIN_SHA" "$CLONE_PATH" "$RUNDIR/arm-a-settings.json" "$RUNDIR/arm-b-settings.json" "$RUNDIR/arm-s-settings.json" "$SCRATCH_CWD" "$RUNDIR" <<'PY'
import json,sys
pin_sha,clone_path,arm_a,arm_b,arm_s,scratch,rundir=sys.argv[1:]
manifest={
    "pin_sha":pin_sha,
    "clone_path":clone_path,
    "arm_a_settings":arm_a,
    "arm_b_settings":arm_b,
    "arm_s_settings":arm_s,
    "scratch_cwd":scratch,
    "rundir":rundir,
}
json.dump(manifest,open(rundir+'/run-manifest.json','w'),indent=2)
print("manifest written:",rundir+'/run-manifest.json')
PY

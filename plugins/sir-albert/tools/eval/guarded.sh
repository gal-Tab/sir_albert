#!/bin/bash
# Run any command; restore settings.json "model" afterwards (even on failure).
# axcli rewrites the default model on every spawn (see 04-probe-results.md).
#
# Restore target: W4_RESTORE_MODEL if set, else the value snapshotted at start.
# Parallel runs MUST set W4_RESTORE_MODEL: a guard starting while another run's
# spawn has already drifted the file would otherwise snapshot the drift.
# The restore takes a lock and writes atomically (temp file + rename), so
# concurrent guards never interleave and no reader sees a half-written file.
#
# Env overrides (tests): W4_SETTINGS_FILE (default ~/.claude/settings.json).
set -euo pipefail
F="${W4_SETTINGS_FILE:-$HOME/.claude/settings.json}"
WANT="${W4_RESTORE_MODEL:-$(/usr/local/bin/python3.13 -c "import json,sys;print(json.load(open(sys.argv[1]))['model'])" "$F")}"
restore() {
  /usr/local/bin/python3.13 - "$F" "$WANT" <<'PY'
import fcntl, hashlib, json, os, re, shutil, sys, tempfile
p, want = sys.argv[1], sys.argv[2]
lock_path = os.path.join(tempfile.gettempdir(), "w4-guard-" + hashlib.sha1(os.path.realpath(p).encode()).hexdigest()[:12] + ".lock")
with open(lock_path, "w") as lock:
    fcntl.flock(lock, fcntl.LOCK_EX)
    s = open(p).read()
    cur = json.loads(s)["model"]
    if cur != want:
        s2, n = re.subn(r'"model":\s*"[^"]*"', '"model": ' + json.dumps(want), s, count=1)
        assert n == 1
        json.loads(s2)
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.realpath(p)), prefix=".settings-w4-")
        with os.fdopen(fd, "w") as f:
            f.write(s2)
        shutil.copymode(p, tmp)
        os.replace(tmp, os.path.realpath(p))
        print(f"[guard] model drift {cur} -> restored {want}", file=sys.stderr)
PY
}
trap restore EXIT
"$@"

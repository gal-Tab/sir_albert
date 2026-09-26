#!/bin/bash
# Run any command; restore settings.json "model" to its pre-run value afterwards (even on failure).
# Supports W4_SETTINGS_FILE env override for testing (defaults to ~/.claude/settings.json).
# Supports W4_CLAUDE_BIN env override (defaults to "command claude") for testing.
set -euo pipefail
F="${W4_SETTINGS_FILE:-$HOME/.claude/settings.json}"
WANT=$(/usr/local/bin/python3.13 -c "import json;print(json.load(open('$F'))['model'])")
restore() {
  /usr/local/bin/python3.13 - "$F" "$WANT" <<'PY'
import json,re,sys
p,want=sys.argv[1],sys.argv[2]
s=open(p).read(); cur=json.loads(s)['model']
if cur!=want:
    s2,n=re.subn(r'"model":\s*"[^"]*"', json.dumps("model")[:-1]+'": '+json.dumps(want), s, count=1)
    assert n==1; json.loads(s2); open(p,'w').write(s2)
    print(f"[guard] model drift {cur} -> restored {want}", file=sys.stderr)
PY
}
trap restore EXIT
"$@"

# 05 — arm-builder

**Blocked by:** 04
**Spec:** `docs/specs/2026-09-26-w4-eval.md §P2 — Thin A/B replay / Arm isolation`

## Goal
Build `build_arms.sh`: create arm A and arm B settings files by copying `~/.claude/settings.json` and changing ONLY `enabledPlugins["superpowers@claude-plugins-official"]`; clone the repo to a pinned SHA via `git clone --local`; create a scratch cwd (a git repo with one commit, required so hooks don't error on HEAD); write `run-manifest.json`. Both arms use `--plugin-dir` to the same clone — the ONLY difference between them is the superpowers flag.

| Arm | superpowers | --plugin-dir |
|---|---|---|
| **A** — today's setup | `true` | `/tmp/w4-arm-clone-<sha>/plugins` |
| **B** — today minus superpowers | `false` | `/tmp/w4-arm-clone-<sha>/plugins` |

## Steps

1. Write test `plugins/sir-albert/tests/eval/test_arm_builder.py`:
   - Use `tmp_path` fixture; create a fake `settings.json` with `enabledPlugins` key and a `hooks` block
   - Run `build_arms.sh` (or its Python equivalent for testing) with overridden paths
   - Assert `arm-a-settings.json` has `enabledPlugins["superpowers@claude-plugins-official"] == true`
   - Assert `arm-b-settings.json` has `enabledPlugins["superpowers@claude-plugins-official"] == false`
   - Assert both files preserve the `hooks` block (guard.sh is preserved automatically from the copy)
   - Assert both files have identical content except for the one key (diff only the superpowers value)
   - Assert `run-manifest.json` has: `pin_sha`, `clone_path`, `arm_a_settings`, `arm_b_settings`, `scratch_cwd`

   Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_arm_builder.py -q` — Expected: FAIL

2. Write `plugins/sir-albert/tools/eval/build_arms.sh`:
   ```bash
   #!/usr/bin/env bash
   set -euo pipefail
   REPO=/Users/galta/Development/sir_albert
   PIN_SHA=$(git -C "$REPO" rev-parse HEAD)
   CLONE_PATH="/tmp/w4-arm-clone-${PIN_SHA:0:12}"
   RUNDIR=$(mktemp -d -t w4-eval-XXXX)
   SCRATCH_CWD="/tmp/w4-eval-scratch"
   ```

3. Generate arm settings files in `build_arms.sh`:
   ```bash
   /usr/local/bin/python3.13 - "$HOME/.claude/settings.json" "$RUNDIR/arm-a-settings.json" "true" <<'PY'
   import json,sys; src,dst,val=sys.argv[1],sys.argv[2],sys.argv[3]=='true'
   s=json.load(open(src)); s.setdefault('enabledPlugins',{})['superpowers@claude-plugins-official']=val
   json.dump(s,open(dst,'w'),indent=2)
   PY
   ```
   Same for arm B with `"false"`. Verify hooks block preserved:
   ```bash
   /usr/local/bin/python3.13 -c "import json; s=json.load(open('$RUNDIR/arm-b-settings.json')); assert s.get('hooks'), 'hooks block missing'"
   echo "hooks preserved"
   ```

4. Clone the repo in `build_arms.sh`:
   ```bash
   if [ ! -d "$CLONE_PATH" ]; then
     git clone --local "$REPO" "$CLONE_PATH"
   fi
   # Verify not a worktree (.git is a directory, not a file)
   test -d "$CLONE_PATH/.git" || { echo "ERROR: .git is not a directory — may be a worktree"; exit 1; }
   echo "clone ok: $(git -C $CLONE_PATH rev-parse HEAD)"
   ```

5. Create scratch cwd in `build_arms.sh`:
   ```bash
   mkdir -p "$SCRATCH_CWD"
   if [ ! -d "$SCRATCH_CWD/.git" ]; then
     git -C "$SCRATCH_CWD" init -q
     git -C "$SCRATCH_CWD" commit --allow-empty -m "scratch" -q
   fi
   echo "scratch cwd ok: $SCRATCH_CWD"
   ```

6. Copy `probe/guarded.sh` to `plugins/sir-albert/tools/eval/guarded.sh`:
   ```bash
   cp plugins/sir-albert/tools/eval/probe/guarded.sh plugins/sir-albert/tools/eval/guarded.sh
   chmod +x plugins/sir-albert/tools/eval/guarded.sh
   ```

7. Write `$RUNDIR/run-manifest.json`:
   ```json
   {
     "pin_sha": "<PIN_SHA>",
     "clone_path": "<CLONE_PATH>",
     "arm_a_settings": "<RUNDIR>/arm-a-settings.json",
     "arm_b_settings": "<RUNDIR>/arm-b-settings.json",
     "scratch_cwd": "<SCRATCH_CWD>",
     "rundir": "<RUNDIR>"
   }
   ```
   Print: `RUNDIR=$RUNDIR`

8. Run: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_arm_builder.py -q` — Expected: PASS

9. Integration smoke test:
   Run: `bash plugins/sir-albert/tools/eval/build_arms.sh`
   Expected: prints `RUNDIR=...`, `clone ok: <sha>`, `hooks preserved`, `scratch cwd ok`
   Verify: `python3 -c "import json; s=json.load(open('$RUNDIR/arm-b-settings.json')); print('superpowers:', s['enabledPlugins']['superpowers@claude-plugins-official'])"` → `superpowers: False`
   Verify: `ls -la $CLONE_PATH/.git` → directory, not a file

## Definition of Done
- [ ] Arm A: superpowers=true; arm B: superpowers=false; both arms: same `--plugin-dir` (the /tmp clone)
- [ ] Both settings files preserve the `hooks` block; files are identical except the one superpowers key
- [ ] Clone is `git clone --local` (not a worktree): `ls -la $CLONE_PATH/.git` is a directory
- [ ] Scratch cwd is a git repo with ≥1 commit: `git -C /tmp/w4-eval-scratch log --oneline` shows ≥1 line
- [ ] `guarded.sh` is in `plugins/sir-albert/tools/eval/guarded.sh`
- [ ] `run-manifest.json` has all required keys including `scratch_cwd`
- [ ] `~/.claude/settings.json` unmodified
- [ ] Tests pass: `/usr/local/bin/python3.13 -m pytest plugins/sir-albert/tests/eval/test_arm_builder.py -q`

# 04 — config-dir-spike

**Blocked by:** —
**Spec:** `docs/specs/2026-09-26-w4-eval.md §P2 — Thin A/B replay / Arm isolation`
**STATUS: DONE** — Gal ran the probes on 2026-09-26. See `docs/plans/2026-09-26-w4-eval/04-probe-results.md`.

## Goal
~~Verify `CLAUDE_CONFIG_DIR` behaviour.~~ → Revised: verified that `--setting-sources project,local --settings <file> --plugin-dir <clone>/plugins --output-format stream-json --verbose --include-hook-events --no-session-persistence` are all honoured, and discovered that axcli rewrites `~/.claude/settings.json` "model" on every spawn — making the model guard the primary defence, not a safety net.

## Summary of findings (from `04-probe-results.md`)

1. **Arm switch confirmed.** Arm A (superpowers=true + plugin-dir) had 15 superpowers skills + 28 sir-albert skills. Arm B (superpowers=false + plugin-dir) had 0 superpowers skills + 28 sir-albert skills. Total spend: $0.32.
2. **`--setting-sources project,local` + `--settings <file>` works** as the arm isolation mechanism.
3. **Both arms share the same `--plugin-dir`** pointing at the `/tmp` local clone. Arm A = today's setup (both plugins). Arm B = today minus superpowers. The ONLY variable is `enabledPlugins["superpowers@claude-plugins-official"]`.
4. **axcli rewrites `"model"` in `~/.claude/settings.json` on every spawn** (including `--help`, `--version`, `-p`). This is primary, not residual — the guard is mandatory before every `command claude` call.
5. **`probe/guarded.sh` is the guard.** Snapshots model before, restores with single-match regex + JSON re-validation on `trap EXIT`. Self-test confirmed: `[guard] model drift claude-sonnet-5 -> restored claude-opus-5-5[1m]`.
6. **Scratch cwd must be a git repo with ≥1 commit.** Without it, hooks print `fatal: ambiguous argument 'HEAD'` on every event.
7. **`--no-session-persistence` works** (no transcript written), but **SessionEnd hook still appends** to `~/.claude/sir-albert-sessions.jsonl`. Post-tranche cleanup required.

## Definition of Done — all items confirmed
- [x] `--setting-sources project,local --settings <arm-file>` confirmed as arm isolation mechanism
- [x] Superpowers absent in arm B, present in arm A — verified via init event `skills` field
- [x] `--no-session-persistence` confirmed — no transcripts written
- [x] `--max-budget-usd` accepted (never triggered in probe; pilot is the real test)
- [x] Model guard (`probe/guarded.sh`) implemented and self-tested
- [x] Scratch cwd requirement documented (`/tmp/<dir>` with `git init && git commit`)
- [x] SessionEnd hook side-effect documented; post-tranche cleanup planned in ticket 07
- [x] Total spend $0.32 (under $0.50 cap)

**Ready for ticket 05: YES.** Key strings for canary:
- Init event: `{"type":"system","subtype":"init","skills":[...]}` — assert on skills list
- `probe/guarded.sh` wrapper: `plugins/sir-albert/tools/eval/probe/guarded.sh`
- Model under test: `claude-opus-5-5[1m]`

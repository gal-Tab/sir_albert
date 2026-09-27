# 14 — e2e-verify

**Blocked by:** 13

## Goal
Every gate in the P3 verdict is independently recomputed from raw artifacts and matches. Nothing text-bearing is tracked in git. The result is presented to Gal with the uninstall decision left to him.

## Steps
1. Independent recompute: write a throwaway script in `mktemp -d` (not reusing `verdict_p3.py` code) that reads `runs-p3/*.json`, `sample-p3.jsonl`, and both resolved judgment files, and recomputes G1–G4. Expected: identical numbers to the verdict report. Any mismatch is a bug in `verdict_p3.py`; fix it test-first.
2. Provenance: every artifact's `init_event` model is `claude-sonnet-5`. `run-manifest.json` `pin_sha` == `git rev-parse w5-freeze`. Arm S artifacts show 0 `sir-albert:` skills loaded, and arm B shows 0 `superpowers:` skills loaded.
3. Held-out integrity: 0 overlap between `sample-p3.jsonl` hashes and the W4 `labeled-set.jsonl`/`sample.jsonl`. The spec commit predates the first `11-dev-log.md` row.
4. Privacy scan: for each `sample-p3.jsonl` and W4 `sample.jsonl` row, take a 40-char substring of its text and grep for it in `git ls-files -z | xargs -0 cat` and in `git log -p`. Expected: 0 hits.
5. Gal's settings: `grep '"model"' ~/.claude/settings.json` → `claude-opus-5-5[1m]`.
6. Run: `/usr/local/bin/python3.13 -m pytest -q plugins/sir-albert/tests/`. Expected: all pass.
7. Write a handoff via `/sir-albert:handoff`.
8. Present to Gal: TLDR verdict (OUTPERFORM or not, UNINSTALL-SAFE or not), the gate table, per-slice rates for B/A/S, the CI range, sensitivity, total spend, and the known limits.

## Definition of Done
- [ ] Independent recompute matches the verdict exactly
- [ ] Provenance, held-out, and privacy checks all pass
- [ ] Verdict presented; no push, no uninstall

## CHECKPOINT
No push or PR (Gal is moving the repo to `dapulse` first). Uninstalling superpowers is Gal's separate decision and is never inferred from OUTPERFORM.

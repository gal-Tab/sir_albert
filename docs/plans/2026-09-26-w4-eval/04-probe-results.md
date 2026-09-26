---
status: stable
date: 2026-09-26
owner: Gal
---

# Ticket 04: probe results

**TLDR:** The arm switch works. Superpowers is present in A and absent in B, and both arms run on Opus 5.5. Total spend was **$0.32**. The probe also showed that **axcli rewrites Gal's default model on every spawn**, so the model guard is now the primary defence rather than a safety net.

## Setup

- Clone: `git clone --local` → `/tmp/w4-probe/sir_albert` at `868767b`. That commit sits one ahead of `9fc48fc`, but it is a kb filing that only touches `raw/`, so `plugins/` is identical.
- Arm settings: copies of `~/.claude/settings.json` that differ in one key, `enabledPlugins["superpowers@claude-plugins-official"]`.
- Flags: `--setting-sources project,local --settings <arm>.json --plugin-dir <clone>/plugins --model 'claude-opus-5-5[1m]' --max-turns 1 --max-budget-usd 0.25 --no-session-persistence --disallowedTools Write,Edit,NotebookEdit --output-format stream-json --verbose --include-hook-events`
- Scratch cwd: `/tmp/w4-probe/work`, a git repo with one empty commit. Without a commit, a hook prints `fatal: ambiguous argument 'HEAD'` on every event.

## Results

| Run | superpowers skills | sir-albert skills | `using-superpowers` | `## sir_albert` | Model | Cost |
|---|---|---|---|---|---|---|
| A: superpowers only (first draft, superseded) | 15 | 0 | ✅ | ❌ | opus-5-5[1m] | $0.081 |
| **A: today (both plugins)** | **15** | **28** | ✅ | ✅ | opus-5-5[1m] | $0.094 |
| **B: today minus superpowers** | **0** | **28** | ❌ | ✅ | opus-5-5[1m] | $0.141 |

The init event (`type=system, subtype=init`) exposes `plugins`, `skills` and `model`, so ticket 06's canary can assert on it directly and doesn't need to grep for text.

## Findings

1. **The spec's arm A was the wrong comparison.** Superpowers-only vs sir_albert-only answers "which plugin is better". The actual decision is "uninstall superpowers", so A = today (both) and B = today minus superpowers. The spec is corrected.
2. **axcli rewrites the default model on every spawn.** `~/.axcli/bin/claude` is `exec "$HOME/.local/bin/axcli" spawn "$@"`. `strings` finds `Default model set to` in the axcli binary. It rewrote `~/.claude/settings.json` `"model"` → `claude-sonnet-5` on a `-p` run, on `--help` and on `--version`, even with `user` sources excluded and `--model` passed. Diffing against a pre-probe copy showed `model` was the only key touched.
3. **The guard works.** `probe/guarded.sh` snapshots the model, runs the command, and restores on `trap EXIT` with a single-match regex followed by JSON re-validation. Self-test: `[guard] model drift claude-sonnet-5 -> restored claude-opus-5-5[1m]`.
4. **`--no-session-persistence` works.** No transcript is written, only an empty `~/.claude/projects/-private-tmp-w4-probe-work/` dir, which the corpus `*.jsonl` glob ignores.
5. **Hooks still run.** sir_albert's `SessionEnd` appended one row (cwd `/tmp/w4-probe/work`) to `~/.claude/sir-albert-sessions.jsonl`. It was left in place.
6. **`--max-budget-usd` was accepted.** It never triggered, because every run stayed under $0.25. The pilot is the first real test.

## Residual risks

- While a run is in flight, `settings.json` reads `claude-sonnet-5`, so a session Gal opens during a tranche starts on Sonnet.
- The axcli behaviour should be reported to its owners. A report is an external send, so it needs a draft and Gal's approval first.

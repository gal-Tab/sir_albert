---
title: Rigor — how much verification a step earns
status: stable
owner: gal-Tab
sources:
  - Gal, 2026-10-20 — eval overhead was slowing live debugging; model picks the level, Gal overrides
last_modified: 2026-10-20
stale_after: 2027-04-20
---

# Rigor — scale verification to blast radius, not to file type

Pick the level per step, silently. Rule of thumb: **the lowest level whose failure you'd still catch before it reaches prod.**

| Level | Pick when | Run | Skip |
|---|---|---|---|
| **fast** | Debugging or iterating; change is local + reversible; Gal is driving turn by turn | Re-run the repro / the one test / `--case <id> --reps 1`; one change at a time | plan, brainstorm, create-skill loops, judge panels, full suites, full evals |
| **ship** *(default)* | About to commit, merge, or open a PR | `validate-skill.py`, touched tests, the project's own gate **once** (e.g. tag: `agent-tag eval --compare` before merge) | T1/T2 loops |
| **deep** | Gal says so; a new discipline skill; a pre-registered experiment | create-skill T2, k=3 baselines, full evals | — |

- **Override:** a prompt starting `fast:` / `ship:` / `deep:` sets the level for the rest of the session; `auto:` hands it back to you. An override beats your pick.
- **Precedence:** skill-internal gates ("non-negotiable", "never skip", "full suite") scale with this level. ASK gates in `autonomy.md` and `guard.sh` never scale.
- **One gate per change.** If the repo has its own eval gate (e.g. tag's `agent_home/**` skills), that is the gate — don't stack create-skill on top. No repo gate (e.g. gal-va) → create-skill at T0.
- **Escalate, don't stall.** In fast, if the same fix fails twice or the change becomes irreversible, step up to ship and say so in one line.

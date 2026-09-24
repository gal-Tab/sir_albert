# skills/core/ — domain-agnostic OS skills

Loaded everywhere, mode-independent. Invoked as `/sir-albert:<name>`.

Core skills (W2):
- `brainstorm` — 7-mode think-first skill (explore, sharpen, attack, panel, grill, zoom-out, design)
- `plan` — generates HTML + agent-executable ticket .md files from a planning session
- `execute` — task-graph executor; dispatches Sonnet subagents; CHECKPOINT gates for irreversible actions
- `debug` — Phase 1 non-negotiable: build feedback loop before hypothesis; Pocock port
- `build` — universal build loop; §Finishing, §TDD, §Verification sections
- `handoff` — write the handoff doc **and** a paste-able restart prompt
- `resume` — reload the latest handoff, state the plan back in ≤5 bullets
- `decide` — record/apply decisions in `os/state/decisions.jsonl`
- `freeze` — scope Edit/Write to a path during investigation
- `retro` — self-improving skill loop from recent sessions

Every core skill boots from `os/PREAMBLE.md`.

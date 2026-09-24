# os/ — the sir_albert_os spine

Domain-agnostic OS layer. **One source, N readers** — these files are authored once and read by Claude Code and by other runtimes (e.g. NanoClaw) alike.

- `RESOLVER.md` — one-screen map: "I'm about to do X → which skill/rule/pack applies, and where does output go?" **Read this first.**
- `PREAMBLE.md` — shared boot include every sir-albert skill references (USER + active rules + the anti-slop / use-the-skill contract).
- `identity/` — `USER.md` · `SOUL.md` · `HEARTBEAT.md`. Canonical portable markdown. `~/.claude/CLAUDE.md` `@`-imports these; NanoClaw reads them raw. No copy → no drift.
- `rules/` — encoded hard rules in **OKF** format (`gtm-naming`, `consent-map`, `output-style`, `autonomy`). Each is cited (`sources`), dated (`stale_after`), and status-tracked (`draft`/`stable`/`deprecated`).
- `state/` — append-only OS state: `decisions.jsonl` (decision memory), handoff index.

This is **not** a skills directory — it is referenced by skills and by `CLAUDE.md`, not loaded as commands.

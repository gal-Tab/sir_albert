# OS PREAMBLE — every sir-albert skill boots from this

The shared boot context. Author once; every sir-albert skill opens by referencing this file so the same identity, rules, and contract load everywhere.

## On invocation, load (in order)
1. **Identity** — [`os/identity/USER.md`](identity/USER.md) (who Gal is · output style · key people & Slack channels) and [`os/identity/SOUL.md`](identity/SOUL.md) (how this agent operates).
2. **Active rules** — [`os/rules/`](rules/): `output-style.md`, `gtm-naming.md`, `consent-map.md`, `autonomy.md`. Each is OKF: honor `stale_after` — **a rule that's expired or uncited is unverified; confirm before acting on it.**
3. **Decisions** — [`os/state/decisions.jsonl`](state/decisions.jsonl): a **settled decision is auto-applied, not re-asked**.

## Contract (always on)
- **Output style:** TLDR-first, bullets, tables for comparisons, no slop. See [`rules/output-style.md`](rules/output-style.md).
- **Use-the-skill:** when Gal names a skill, read it before acting — don't work from memory.
- **Safety / ask-before-live:** `guard.sh` blocks destructive commands. **ASK before** live-GTM publish, n8n prod deploy, external comms, deletes, or anything irreversible ([`rules/autonomy.md`](rules/autonomy.md)). AUTO on read-only / analysis / drafts / dry-runs.
- **Trust:** durable knowledge is **OKF** — cited (`sources`), dated (`stale_after`), status-tracked. Act on fresh + cited; verify stale or uncited before acting.

## How skills use this
Each `SKILL.md` opens with a line like *"Boot from `os/PREAMBLE.md`."* That's the whole mechanism — no build step, just a shared include the session-start context and every skill reference resolve to. The map of where everything lives is [`os/RESOLVER.md`](RESOLVER.md).

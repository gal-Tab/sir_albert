# skills/knowledge — inherited, not forked

The knowledge engine is the canonical **`llm-wiki-agent` plugin** (installed + enabled), not a copy in this repo.

- **Query:** `wiki-query` · `learn-recall` · `learn-research`
- **Pipeline:** `/wiki-init` · `/wiki-compile` · `/learn-capture`
- **Write side:** `kw-compound` (in `skills/agentic/`) drafts to `raw/`; the OS `learnings` skill canonicalizes before `/wiki-compile`.

The legacy `kb-query` / `kb-compile` fork was **retired** (deleted 2026-07-31) — it had drifted from canonical. Do not reintroduce a `kb-*` fork here.

> **Cross-repo followup (deferred, M5.3):** align consumers `open_claw` + `Investment-agent` + the `llm-wiki-agent-dev` marketplace to canonical `agent_knowledgebase` main, then retire the stale v0.4.0. Needs care + user OK (external repos).

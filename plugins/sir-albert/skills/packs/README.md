# skills/packs/ — domain packs

One pack per working mode. Each pack is its own plugin skills-category (listed individually in `.claude-plugin/plugin.json`); skills live at `skills/packs/<pack>/<skill>/SKILL.md` and are still invoked flat as `/sir-albert:<skill-name>`.

- `gtm/` — **GTM engineering** (maintain-mode, shrinking): plan → apply → publish → handoff. Naming + consent gates; param-audit absorbed into `gtm-gate`.
- `data/` — **Data & monitoring** (part of Building): prototype → query → viz → deliver; `data-review`; attested z2h-look metrics.
- `automation/` — **Automation & integration**: `n8n-triage`, HubSpot API-safety, pipeline refactors.

Building/Think is **not** a pack — it's a Core phase (`skills/core/brainstorm` + `skills/core/build`) that front-runs all three.

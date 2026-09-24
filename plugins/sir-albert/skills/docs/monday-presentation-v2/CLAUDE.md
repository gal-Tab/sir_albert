# monday-presentation-v2

Design-system-first HTML presentation builder with monday.com branding.

## Quick Start

Use the skill: `/monday-presentation-v2`

## Architecture

- **SKILL.md** — The skill definition (invoked via `/monday-presentation-v2`). Contains the phased workflow, inlined brand SVG, and navigation JS.
- **design-system.css** — CSS tokens (colors, typography, spacing). Inlined verbatim into every generated HTML.
- **Selected/** — 67 proven HTML slide templates (`Deck_Dark_Page_*.html`). Used as source patterns.
- **Icons/** — 267 monday.com SVG icons. Read and inlined into generated HTML for portability.
- **RECIPES.md** — 5 presentation recipes (Product Launch, Team Review, Proposal, Training, Quick Update).
- **SLIDE_INVENTORY.md** — Metadata catalog for every template (structure, capacity, editable elements).
- **ICON_MATCHING.md** — Semantic icon selection guide by content type.

## Key Rules

- Generated presentations are single self-contained HTML files — zero external dependencies.
- All icons are inlined as SVG, not referenced via `<img src>`.
- Navigation uses class-based toggling (`slide-active`), never inline `style.display`.
- All slides lock to 16:9 aspect ratio using vmin units.
- This skill is bundled in the `sir-albert` plugin at `skills/docs/monday-presentation-v2/` and is loaded via the plugin (no loose symlink).

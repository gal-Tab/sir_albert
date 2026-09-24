# 01 — router-data.json

**Blocked by:** —
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 1 + §Component 2

## Goal

Create `plugins/sir-albert/hooks/router-data.json` — the single data file that drives both the pack-detection signals (SessionStart) and the keyword patterns (UserPromptSubmit). Everything tunable in W4 lives here.

## Steps

1. Read `docs/specs/2026-09-24-w3-router-design.md` to confirm the full signal and pattern tables.
2. Create `plugins/sir-albert/hooks/router-data.json` with two top-level keys:
   - `"pack_signals"`: array of `{pack, signal_type, pattern}` objects (e.g. `{pack: "n8n", signal_type: "glob", pattern: "**/*.workflow.json"}`)
   - `"keyword_patterns"`: array of `{pattern, nudge, order}` objects (order = integer; lower fires first; patterns ordered most-specific to most-general)
3. Include all signals from the spec: n8n, GTM, HubSpot, kb (raw/+wiki/), z2h, code.
4. Include all keyword patterns from the spec table including Hebrew phrases.
5. Validate JSON with `python3 -m json.tool plugins/sir-albert/hooks/router-data.json`.

## Definition of Done

- [ ] `router-data.json` exists and is valid JSON
- [ ] Contains at least 6 pack signals and 11 keyword patterns
- [ ] Hebrew patterns are present (UTF-8 encoded correctly, verified with `grep -c "תכנן" plugins/sir-albert/hooks/router-data.json`)
- [ ] `python3 -m json.tool` exits 0

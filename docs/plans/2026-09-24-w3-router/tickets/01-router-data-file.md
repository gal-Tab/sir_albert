# 01 — router_data.json

**Blocked by:** —
**Spec:** `docs/specs/2026-09-24-w3-router-design.md` §Component 1 + §Component 2

## Goal

Create `plugins/sir-albert/hooks/router_data.json` — the single data file driving both pack-detection signals (SessionStart) and keyword patterns (UserPromptSubmit). All tunable in W4; never hardcode in scripts.

## Steps

1. Read the spec §Component 1 (pack signals) and §Component 2 (keyword table) to extract the full lists.
2. Create `plugins/sir-albert/hooks/router_data.json` with two top-level keys:
   - `"pack_signals"`: array of `{pack, signal_type, pattern}` — e.g. `{"pack": "gtm", "signal_type": "glob", "pattern": "apply-*.ts"}`
   - `"keyword_patterns"`: array of `{order, intent, pattern, nudge}` — ordered integer; lower fires first; most-specific first
3. Pack signals: gtm (`apply-*.ts`), n8n (`*.workflow.json`), hubspot (`.hubspot/` or `hs*.js`), kb (`raw/` AND `wiki/` both present), z2h (`.z2h` marker), code (`.git/` AND `tests/`).
4. Keyword patterns: use the tightened phrase-level patterns from the spec §Draft keyword table. Hebrew column is TBD (ticket 04a); add empty array placeholder `"hebrew_patterns": []`.
5. Validate: `python3 -m json.tool plugins/sir-albert/hooks/router_data.json`

## Definition of Done

- [ ] File exists, valid JSON
- [ ] 6 pack signals present
- [ ] 11 keyword patterns present (all from spec table, no topic-word-only patterns)
- [ ] `"hebrew_patterns": []` placeholder present
- [ ] `python3 -m json.tool` exits 0
- [ ] No pattern matches `"execute this SQL"` or `"publish the GTM container"` (verify mentally against each pattern)

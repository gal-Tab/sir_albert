---
name: param-audit
description: >
  Audit all server-side GTM (sGTM) Facebook and LinkedIn tags for a required parameter set and flag
  missing or inconsistently-named params. Use whenever someone asks to audit sGTM tag parameters,
  check tag parameter consistency, verify FB or LinkedIn tag params, or diagnose parameter drift
  across sGTM tags. Trigger on: "/param-audit", "audit sGTM params", "check tag parameters",
  "are the FB/LinkedIn params consistent", "parameter naming drift", "is_desktop vs monday_is_desktop",
  "missing event_id", "li_fat_id missing".
---

Boot from `os/PREAMBLE.md`.

# param-audit — sGTM Facebook & LinkedIn Tag Parameter Audit

## Mission

Enumerate every Facebook and LinkedIn tag in the sGTM container, check each against the required
parameter set, and surface any missing or mis-named param in a single table. One run = full picture.

---

## Required parameter set

Every FB and LinkedIn tag fired from sGTM must carry all of the following:

| Param | Purpose | Notes |
|---|---|---|
| `is_gtm` | Marks the hit as GTM-sourced | Boolean; required for downstream attribution logic |
| `is_desktop` | Device-type signal | **Canonical name is `is_desktop`** — see naming drift note below |
| `event_id` | Event deduplication key | Shared with the browser pixel to deduplicate server + client fires |
| `li_fat_id` | LinkedIn first-party ad tracking ID | LinkedIn only; enables identity resolution on sGTM hits |

---

## Known naming drift — `monday_is_desktop` vs `is_desktop`

**The real drift Gal hit:** some tags were mapped to `monday_is_desktop` instead of `is_desktop`.
Both appear to carry the same device-type boolean, but the param names differ — so LinkedIn (or
whatever downstream consumer checks `is_desktop`) sees the param as absent.

When running the audit, treat `monday_is_desktop` as a **mis-named variant of `is_desktop`** and
flag it as a naming violation, not a missing param. The fix is to remap to `is_desktop`.

---

## Procedure

This skill cannot reach GTM directly. Walk through the following steps to produce the audit table.

### Step 1 — Enumerate sGTM tags via GTM API / gtm_agent

sGTM tags are not directly reachable from the file system. Use one of:

- **gtm_agent tooling** (if available in this session): call the tag-list tool for the sGTM workspace.
  Ask for all tags of type `floodlight`, `facebook_capi`, `linkedin_insight`, or custom template tags
  whose name contains `FB`, `Facebook`, `LinkedIn`, or `LI`.
- **GTM API (manual / scripted)**: `GET accounts/{accountId}/containers/{containerId}/workspaces/{workspaceId}/tags`
  then filter by tag type or name pattern.
- **Export fallback**: if neither above is available, ask Gal to export the sGTM container JSON
  (`Admin → Export container`) and paste or share the path; load the JSON and read the `tags` array.

Record for each tag: `tag.name`, `tag.type`, and the full `tag.parameter` array (key → value pairs).

### Step 2 — Scope to FB and LinkedIn tags

Keep only tags where:
- type is `facebook_capi`, `linkedin_insight`, or a custom template whose name contains `FB`,
  `Facebook`, `LinkedIn`, or `LI`; **or**
- the tag name itself contains any of those strings.

Discard everything else from the audit scope.

### Step 3 — Check each tag against the required set

For each in-scope tag, compare its `parameter` keys against the required set.
Classify each missing/mis-named param as one of:

| Status | Meaning |
|---|---|
| `MISSING` | Param not present at all |
| `MIS-NAMED` | Present under a wrong key name (e.g. `monday_is_desktop` instead of `is_desktop`) |
| `OK` | Present under the canonical key name |

### Step 4 — Output the audit table

Produce this table (one row per tag × missing/mis-named param):

| Tag name | Tag type | Param | Status | Current key (if mis-named) | Recommended fix |
|---|---|---|---|---|---|
| … | … | … | MISSING / MIS-NAMED | … | … |

Then a summary line: **N tags audited, M issues found (X missing, Y mis-named).**

If all params are present and correctly named on all tags, output the table with all `OK` rows plus
a `All clear — no param drift detected.` line.

---

## Output style

- TLDR first: one-line verdict before the table.
- Flag the `monday_is_desktop` drift explicitly whenever found — don't fold it into a generic "mis-named" note.
- If `event_id` is absent, call it out as a **deduplication risk** (browser + server fires will not be deduped).
- If `li_fat_id` is absent on a LinkedIn tag, call it out as an **identity resolution gap**.

---

## Hard rules

1. Do not attempt to apply fixes — output findings only. Fixes go through the gtm-gate → apply flow.
2. If the container export / API response is missing or stale, say so and ask Gal to refresh it.
3. Treat `monday_is_desktop` as mis-named, not missing; the distinction matters for the fix path.

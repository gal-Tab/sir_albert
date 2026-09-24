---
name: gtm-gate
description: >
  Use when about to apply a GTM change, wanting a pre-apply check, auditing sGTM tag parameters, or checking FB/LinkedIn param consistency. Triggers on "gtm-gate", "pre-apply check", "validate before apply", "check naming and consent", "run the gate", "is this GTM change safe to apply", "/param-audit", "audit sGTM params", "check tag parameters", "are the FB/LinkedIn params consistent", "parameter naming drift", "is_desktop vs monday_is_desktop", "missing event_id", "li_fat_id missing".
---

Boot from `os/PREAMBLE.md`.

# gtm-gate — Pre-Apply Naming & Consent Gate

## Mission

Block off-convention GTM changes before they land in a workspace. The workspace-name check runs too
late and does not cover naming conventions or consent posture; this gate closes that gap.

Run this skill as the **last step before any `apply-*.ts` executes**. If the gate passes, proceed.
If the gate fails, surface every violation, do not apply, and wait for Gal to resolve.

---

## When to run

- Automatically: any time the GTM plan→apply flow reaches the apply step.
- On demand: whenever Gal types `/gtm-gate`, "pre-apply check", or "validate before apply".

---

## Gate procedure

### Step 1 — Load the rule files

Read both rule files in full before checking anything:

1. `os/rules/gtm-naming.md` — naming convention (ce prefix, constant-variable rule, prefix–descriptor structure).
2. `os/rules/consent-map.md` — per-container consent posture. **Check `stale_after` first**:
   if today ≥ `stale_after`, halt immediately, surface the expiry date, and ask Gal to refresh
   the file before the gate can proceed.

### Step 2 — Identify the planned change

From context (the current plan, the `apply-*.ts` about to run, or what Gal described), collect:

| Item | What to extract |
|---|---|
| Tags | Name, type, target container |
| Variables | Name, type, target container |
| Triggers | Name, type, target container |
| Containers affected | List of container names (main, website, signup, trial, sGTM, …) |

If the planned change is ambiguous, ask Gal to specify before continuing.

### Step 3 — Naming check (against `gtm-naming.md`)

For every proposed tag, variable, and trigger name:

**Rule A — ce prefix**
- Any entity tied to a custom event trigger must have the `ce - ` prefix.
- Any entity tied to a built-in trigger type (page view, click, form submit, etc.) must NOT have `ce - `.
- Violation: name missing `ce - ` when required, or carrying `ce - ` when not a custom event.

**Rule B — Constant-variable rule**
- Base codes and config tags must not hardcode IDs (pixel IDs, measurement IDs, container IDs, etc.).
- Each ID must live in a dedicated Constant variable; the tag field must reference the variable, not the raw ID.
- Violation: literal numeric/alphanumeric ID detected directly in a tag field that should reference a variable.

**Rule C — Prefix–descriptor structure**
- All names follow `<prefix> - <descriptor>` (space-hyphen-space separator, lowercase).
- Violation: missing separator, wrong casing, or no prefix.

Collect all naming violations into a table:

| Entity | Proposed name | Rule violated | Detail | Required fix |
|---|---|---|---|---|

### Step 4 — Consent check (against `consent-map.md`)

For each container in the planned change, apply the consent map:

| Container | Expected posture | Check |
|---|---|---|
| main | Consent-required | Every tracking tag must have a consent condition; no unconditional fires |
| website | Consent-required | Same as main |
| signup | Consent-free | Tags may fire unconditionally — verify this is intentional |
| trial | Consent-free | Same as signup |
| sGTM | Source-aware | Trace the hit source; apply the originating container's posture |

Flag any mismatch:

| Container | Tag name | Expected posture | Observed posture | Violation |
|---|---|---|---|---|

For sGTM tags, the upstream source (main/website vs signup/trial) determines the posture; if the
source is not determinable from the plan, flag as **source unknown — verify before apply**.

### Step 5 — Gate verdict

**PASS** — no naming violations, no consent mismatches, consent-map not stale.
Output: `GATE PASSED — safe to apply.` then list each check with a tick.

**BLOCK** — one or more violations found or consent-map is stale.
Output: `GATE BLOCKED — do not apply.` then the full violation tables from Steps 3 and 4.
Do NOT proceed to apply. Wait for Gal to resolve each violation and re-run the gate.

---

## Hard rules

1. Never silently auto-fix a naming violation. Flag it; Gal confirms the fix; then the change is re-proposed and the gate re-runs.
2. An expired `stale_after` on `consent-map.md` is a hard stop — the gate cannot pass until the file is refreshed.
3. The gate does not validate logic (whether the tag fires correctly) — only names and consent posture.
4. If `apply-*.ts` is already running when this skill is invoked, surface a warning: gate should have run before apply, not during.

---

## § Parameter audit

Absorbed from `packs/gtm/param-audit/`. Use when Gal asks to audit sGTM tag parameters, check parameter consistency, or uses any of the param-audit trigger phrases.

**Mission:** Enumerate every Facebook and LinkedIn tag in the sGTM container, check each against the required parameter set, and surface any missing or mis-named param in a single table. One run = full picture.

### Required parameter set

Every FB and LinkedIn tag fired from sGTM must carry all of the following:

| Param | Purpose | Notes |
|---|---|---|
| `is_gtm` | Marks the hit as GTM-sourced | Boolean; required for downstream attribution |
| `is_desktop` | Device-type signal | **Canonical name is `is_desktop`** — see naming drift note |
| `event_id` | Event deduplication key | Shared with browser pixel to deduplicate server + client fires |
| `li_fat_id` | LinkedIn first-party ad tracking ID | LinkedIn only; enables identity resolution on sGTM hits |

### Known naming drift — `monday_is_desktop` vs `is_desktop`

Some tags are mapped to `monday_is_desktop` instead of `is_desktop`. Treat `monday_is_desktop` as a **mis-named variant of `is_desktop`** and flag it as a naming violation, not a missing param.

### Audit procedure

1. **Enumerate sGTM FB/LinkedIn tags:** via gtm_agent, GTM API, or container JSON export. Record tag name, type, and full parameter array.
2. **Scope to FB and LinkedIn tags** (type `facebook_capi`, `linkedin_insight`, or custom templates named with `FB`, `Facebook`, `LinkedIn`, `LI`).
3. **Check each tag** against the required set. Classify each param as `OK`, `MISSING`, or `MIS-NAMED`.
4. **Output the audit table:**

| Tag name | Tag type | Param | Status | Current key (if mis-named) | Recommended fix |
|---|---|---|---|---|---|

Summary line: **N tags audited, M issues found (X missing, Y mis-named).**

### Hard rules (parameter audit)

- Output findings only. Do not apply fixes — fixes go through the gtm-gate → apply flow.
- If `event_id` is absent, call it out as a **deduplication risk**.
- If `li_fat_id` is absent on a LinkedIn tag, call it out as an **identity resolution gap**.
- If the container export is missing or stale, say so and ask Gal to refresh it.

---
name: gtm-gate
description: >
  Pre-apply gate for GTM changes: validate tag/variable/trigger names against the naming convention
  and consent posture against the consent map BEFORE any apply-*.ts script runs. Use whenever someone
  is about to apply a GTM change, wants a pre-apply check, or asks to validate naming and consent
  before execution. Trigger on: "gtm-gate", "pre-apply check", "validate before apply",
  "check naming and consent", "run the gate", "is this GTM change safe to apply", "naming convention check".
  This is the last step before apply in the GTM plan→apply flow — always run it.
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

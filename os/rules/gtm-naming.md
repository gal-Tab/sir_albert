---
title: GTM Naming Convention
status: draft
owner: gal-Tab
sources:
  - Gal's GTM naming convention (source of record — Gal)
  - Plan 2026-07-30 M2.2
last_modified: 2026-07-31
stale_after: 2027-01-31
---

# GTM Naming Convention

Compiled truth for how tags, variables, and triggers must be named in Google Tag Manager.
This file is authoritative for all GTM work inside sir-albert. When in doubt, ask Gal.

> TODO(gal): confirm/complete the full tag/variable/trigger naming pattern (only fragments are currently known and encoded here).

---

## Applies to

- All **tags**, **variables**, and **triggers** across every GTM container managed by sir-albert.
- Applies at authoring time (the moment a name is proposed) AND as a pre-apply gate (see below).

---

## Naming rules

> TODO(gal): supply the full naming pattern for tags, variables, and triggers (e.g. component order, separators, casing, abbreviation list, max length, character set).

Known fragments:

- Names use a **prefix — descriptor** structure separated by ` - ` (space-hyphen-space).
- Casing: all lowercase (inferred from `ce` examples; confirm for variables and tags).

---

## The ce rule

`ce` is the **custom event** prefix. It marks any entity that is tied to a custom event rather than a built-in GTM trigger type.

Examples of the pattern:
```
ce - <event_name>
```

All custom-event triggers (and any tags or variables scoped to a custom event) must carry this prefix. Do **not** use `ce` for built-in event types (page view, click, form submission, etc.).

> TODO(gal): confirm whether `ce` is used on the trigger, the tag, or both when a custom event fires a tag.

---

## Constant-variable rule

Base codes and configuration tags **must not hardcode IDs** (measurement IDs, container IDs, account IDs, pixel IDs, etc.) directly in the tag field.

Instead:
1. Create a **Constant variable** for each ID.
2. Reference that variable inside the base / config tag.

This rule exists to:
- Give a single source of truth per ID.
- Prevent silent divergence when an ID changes.
- Make audits grep-able (one variable name, not scattered literals).

> TODO(gal): list the canonical constant-variable names already in use (e.g. `const - GA4 Measurement ID`, etc.) so agents can reference rather than re-create them.

---

## Pre-apply gate

This rule set is a **pre-apply gate**: every proposed tag, variable, and trigger name must be validated against the naming rules in this file **before** any `apply-*.ts` script runs.

Motivation: the existing workspace-name check runs too late and does not cover the naming convention; this gate closes that gap.

Gate behavior:
- If a proposed name violates any rule, the agent must **reject it and surface the violation** before proceeding.
- Agents must not silently normalise or auto-rename; they must flag and request confirmation from Gal.

> TODO(gal): specify whether the gate is enforced by a linter script, a hook, or an agent-side check — and where that enforcement code lives.

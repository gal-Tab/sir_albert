---
title: Per-Container Consent Map
status: stable
owner: gal-Tab
sources:
  - CookieHub (CMP — source of record for consent configuration)
  - "TODO(gal): link the CMP/legal source of record (CookieHub dashboard URL or legal policy doc)"
last_modified: 2026-07-31
stale_after: 2026-10-31
---

# Per-Container Consent Map

Compiled truth for which GTM containers require consent and which are consent-free.
This file is the single source of record inside sir-albert for consent routing decisions.

**When this file expires, the OS flags it — an agent must not silently act on an out-of-date consent rule.**
An expired stale_after date is a hard stop: block any consent-dependent action and surface the expiry to Gal before proceeding.

> TODO(gal): set stale_after to the actual next consent-review date (2026-10-31 is a placeholder).

---

## Consent map

| Container | Consent requirement | Notes |
|-----------|--------------------|--------------------------------------------|
| main      | **Required**       | Consent gates all tracking tags            |
| website   | **Required**       | Consent gates all tracking tags            |
| signup    | **Consent-free**   | No consent gate; tags fire unconditionally |
| trial     | **Consent-free**   | No consent gate; tags fire unconditionally |
| sGTM      | **Source-aware**   | Behavior depends on the upstream source; see sGTM section below |

---

## sGTM behavior

sGTM (server-side GTM) does not have a single consent posture — it inherits from the source that sends the hit.

- If the hit originates from a **consent-required container** (main, website): treat as consent-required.
- If the hit originates from a **consent-free container** (signup, trial): treat as consent-free.

> TODO(gal): confirm whether sGTM has any additional server-side consent enrichment or overrides beyond source inheritance.

---

## CMP

The consent management platform is **CookieHub**.

CookieHub controls:
- The consent banner presented to users.
- The consent categories and the mapping to GTM consent signals.
- The source of truth for what a user has or has not consented to.

> TODO(gal): link the CookieHub dashboard or configuration doc so agents can verify category mappings.

> TODO(gal): document which CookieHub consent categories map to which GTM consent types (e.g. analytics_storage, ad_storage, etc.) if relevant to container logic.

---

## Timeline

| Date       | Event                                              |
|------------|----------------------------------------------------|
| 2026-07-31 | Initial encoding into sir-albert OS rules. Consent posture for all five containers recorded as described in this file. CookieHub confirmed as CMP. |

> TODO(gal): add entries here whenever a container's consent posture changes or the CMP is updated.

---

## When this goes stale

`stale_after: 2026-10-31` (placeholder — set to actual consent-review cycle date).

On or after that date:
1. The OS flags this file as stale.
2. Any agent that would make a consent-dependent decision must halt, surface the expiry, and request an updated review from Gal.
3. Gal updates the table, bumps `last_modified` and `stale_after`, and sets `status: stable` to re-activate it.

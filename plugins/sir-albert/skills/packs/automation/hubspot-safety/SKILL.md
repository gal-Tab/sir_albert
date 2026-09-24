---
name: hubspot-safety
description: >
  HubSpot API-safety check. Before shipping a workflow or code that calls HubSpot, scan for
  deprecated v1 endpoints and flag them with current v3 replacements so nothing silently breaks
  in production. Triggers: "hubspot safety", "check hubspot api", "is this hubspot endpoint
  deprecated", "hubspot v1 migration", "before I ship this HubSpot workflow".
---

Boot from `os/PREAMBLE.md`.

# HubSpot Safety

## Mission

Catch deprecated HubSpot API calls **before** they ship to a production workflow or integration.
The v1/v2 → v3 migration has left many endpoints silently returning errors or returning
deprecated data shapes. This skill scans workflow JSON, code, or HTTP node configs and flags
every call that will break.

## Why this matters

HubSpot deprecated its v1 (and most v2) CRM APIs in 2023–2024. Workflows built on the old
endpoints continue to authenticate successfully but return stale data, wrong field names, or
`410 Gone` errors — often without a loud failure. An n8n workflow calling
`/contacts/v1/contact/email/:email/profile` may run for months before an ops team notices
contacts are silently not syncing.

## Known-deprecated patterns

> TODO(gal): paste the authoritative HubSpot v1→v3 deprecation list here once you have the
> canonical source. The table below is a working summary — verify against
> https://developers.hubspot.com/changelog before relying on it in production.

| Deprecated pattern | Replacement |
|---|---|
| `/contacts/v1/…` | `/crm/v3/objects/contacts/…` |
| `/contacts/v2/…` | `/crm/v3/objects/contacts/…` |
| `/companies/v2/…` | `/crm/v3/objects/companies/…` |
| `/deals/v1/…` | `/crm/v3/objects/deals/…` |
| `/engagements/v1/…` | `/crm/v3/objects/engagements/…` (or type-specific: calls, emails, meetings) |
| `/owners/v2/…` | `/crm/v3/owners/…` |
| `/pipelines/v1/…` | `/crm/v3/pipelines/…` |
| `/properties/v1/…` | `/crm/v3/properties/…` |
| `/lists/v1/…` | `/crm/v3/lists/…` (Lists v3, GA 2024) |
| `/email/public/v1/…` | `/marketing/v3/emails/…` |
| `/marketing/v1/…` | `/marketing/v3/…` |
| `/forms/v2/…` | `/marketing/v3/forms/…` |
| `hapikey=` query param auth | Private App token (`Bearer`) or OAuth |

### Auth deprecation

The `hapikey` query-parameter authentication method is fully deprecated. Any URL or header
containing `?hapikey=` or `hapikey=` must be replaced with a **Private App access token**
passed as `Authorization: Bearer <token>`.

## Scan workflow

### Step 1 — Collect the target

Accept any of: n8n workflow JSON, raw HTTP node config, Python/JS code, or a plain list of
endpoint URLs. If nothing is pasted, ask.

### Step 2 — Extract all HubSpot calls

Look for:
- URLs matching `api.hubapi.com` or `api.hubspot.com`
- n8n HTTP Request nodes with a HubSpot base URL
- n8n HubSpot native node (`nodes-base.hubspot`) — check resource + operation for v1 internals
- Code strings containing `/v1/`, `/v2/` after a HubSpot domain
- Auth patterns: `hapikey`, `HAPI_KEY`, `hub_api_key`

### Step 3 — Flag deprecated calls

For each deprecated call found:

```
DEPRECATED  GET /contacts/v1/contact/email/:email/profile
  Replace with:  GET /crm/v3/objects/contacts/:contactId?idProperty=email
  Notes:  Response shape changed — `properties` is now a flat object, not nested under `properties.data`.
          `vid` field is replaced by `id`.
```

Include the HTTP method, the old path, the new path, and any **response shape changes** that
will require downstream mapping updates.

### Step 4 — Flag auth issues

If `hapikey` is used anywhere:

```
DEPRECATED AUTH  hapikey query parameter
  Replace with:  Authorization: Bearer <private-app-token>
  Action:        Create a Private App in HubSpot Settings > Integrations > Private Apps,
                 grant the required scopes, and store the token as a credential.
```

### Step 5 — Summary verdict

End with a clear verdict:

- **SAFE** — no deprecated patterns found
- **NEEDS MIGRATION** — list of flagged calls with priority (blocking vs. cosmetic)
- **UNKNOWN** — calls found but could not be matched to the deprecation list; Gal should
  verify against the HubSpot changelog

## Hard rules

1. **Never mutate production credentials or workflow configs.** Propose the fix; do not apply it.
2. **Flag unknown v2 paths as warnings**, not errors — v2 is deprecated for CRM but some
   v2 endpoints in other product areas may still be active. Note the uncertainty.
3. **Always mention response shape changes** alongside endpoint changes. A URL swap that
   silently misroutes field names is as bad as a 404.
4. **Do not assume a native HubSpot n8n node is safe.** The n8n `nodes-base.hubspot` node
   may internally call v1 APIs depending on the n8n version. Note this risk when the native
   node is in use.

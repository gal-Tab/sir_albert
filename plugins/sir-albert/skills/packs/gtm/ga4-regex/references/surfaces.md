# GA4 / GTM Surfaces — Regex Behavior Cheat Sheet

Regex behaves differently across the Google measurement stack. This sheet documents each surface where regex appears and how that surface handles anchoring, case, partial matching, and engine quirks.

## GA4 Audience Builder

**Location:** Admin → Audiences → New audience → condition → "matches regex"

- **Engine:** RE2
- **Anchoring:** Partial match by default. `^/products` matches `/products`, `/products/`, `/products/123`.
- **Case:** Case-sensitive. Use `(?i)` inline flag for case-insensitive.
- **Multiline:** Single-line, `.` does not match newlines.
- **Capture groups:** Not surfaced — the match is boolean.
- **Common bug:** Users add `.*` to the end thinking they need to match the rest of the string. They don't — partial match handles it.

## GA4 Explorations

**Location:** Explore → any report → filter → "matches regex"

- **Engine:** RE2
- **Anchoring:** Partial match.
- **Case:** Case-sensitive.
- Same behavior as audiences.

## GA4 Custom Definitions (custom dimensions, metrics)

Regex isn't used to define custom dimensions/metrics themselves, but custom dimensions can be REFERENCED in audience and exploration regex filters. The regex behavior follows whichever surface is using it.

## GA4 Data Streams — Unwanted Referrals

**Location:** Admin → Data Streams → web stream → Configure tag settings → List unwanted referrals → "match type: matches regex"

- **Engine:** RE2
- **Anchoring:** Domain match, partial by default but treats the whole referrer hostname as the target
- **Case:** Case-insensitive (Google normalizes hostnames to lowercase before matching)
- **Critical:** Anchor your patterns. `paypal\.com` (unanchored) matches `notpaypal.com.attacker.io`. Use `(^|\.)paypal\.com$`.

## GA4 Data Streams — Cross-Domain Configuration

**Location:** Admin → Data Streams → web stream → Configure tag settings → Configure your domains → "Match type: regex matches"

- **Engine:** RE2
- **Anchoring:** Domain match, partial
- **Case:** Case-insensitive
- Same anchoring caution as unwanted referrals.

## GA4 Internal Traffic

**Location:** Admin → Data Streams → web stream → Configure tag settings → Define internal traffic

This uses **CIDR notation for IPs**, not regex. If you need to filter by hostname pattern, use a different rule type. Don't try to put regex into the IP field.

## Google Tag Manager (Client-Side) — Trigger Filters

**Location:** GTM workspace → Triggers → trigger type → "matches RegEx"

- **Engine:** JavaScript `RegExp` (V8 engine, mostly PCRE-compatible)
- **Anchoring:** Partial match
- **Case:** "Ignore case" checkbox per filter — visible in container audit
- **Lookahead/lookbehind:** Both supported (because it's real JS RegExp)
- **Caveat:** If you ever migrate this trigger to server-side GTM, your lookbehind will break. Future-proof by writing RE2-compatible regex even in client-side GTM when possible.

## Google Tag Manager (Server-Side / sGTM)

**Location:** sGTM workspace → Clients/Tags/Triggers → custom filters

- **Engine:** RE2
- **Anchoring:** Partial match
- **Case:** Configurable per filter
- Same RE2 restrictions as GA4. Most teams using sGTM also use BigQuery export, which is also RE2 — so patterns can be shared.

## Looker Studio (formerly Data Studio)

**Functions:** `REGEXP_MATCH(field, pattern)`, `REGEXP_CONTAINS(field, pattern)`, `REGEXP_EXTRACT(field, pattern)`, `REGEXP_REPLACE(field, pattern, replacement)`

- **Engine:** RE2
- **`REGEXP_MATCH`:** Requires **full match** — pattern must match the entire string. This is different from GA4 audiences. Add `.*` at boundaries or anchor as needed.
- **`REGEXP_CONTAINS`:** Partial match — same behavior as GA4 audiences.
- **`REGEXP_EXTRACT`:** Returns capture group 1. Use `(...)` around the part you want.
- **Case:** Case-sensitive. Use `(?i)`.

This `REGEXP_MATCH` vs `REGEXP_CONTAINS` distinction trips up almost everyone. When a user says "the regex works in GA4 but not Looker Studio," it's almost always because they're using `REGEXP_MATCH` on a pattern designed for partial matching.

## BigQuery (GA4 Export)

**Functions:** `REGEXP_CONTAINS`, `REGEXP_EXTRACT`, `REGEXP_REPLACE`, `REGEXP_EXTRACT_ALL`

- **Engine:** RE2
- **`REGEXP_CONTAINS`:** Partial match — `REGEXP_CONTAINS(page_path, r'^/products/')` matches strings starting with `/products/`.
- **No `REGEXP_MATCH` in BigQuery** — there's only `REGEXP_CONTAINS` for boolean tests. Anchor with `^...$` if you need full match.
- Patterns are typically written as raw strings: `r'^/products/'`.

## Universal Analytics (legacy)

Some users migrating from UA carry old patterns over. UA used a different engine that supported some PCRE features RE2 doesn't. If a user says "this worked in UA," validate the pattern against RE2 rules — common UA patterns that break in GA4:

- Lookbehinds in goal funnels
- Backreferences in advanced segments
- Some Unicode property escapes

Rewrite using the strategies in `re2-rules.md`.

## Summary table

| Surface | Engine | Default match | Case | Lookbehind | Lookahead |
|---|---|---|---|---|---|
| GA4 Audiences | RE2 | Partial | Sensitive | ❌ | ❌ |
| GA4 Explorations | RE2 | Partial | Sensitive | ❌ | ❌ |
| GA4 Unwanted referrals | RE2 | Partial (hostname) | Insensitive | ❌ | ❌ |
| GA4 Cross-domain | RE2 | Partial (hostname) | Insensitive | ❌ | ❌ |
| GTM client-side | JS RegExp | Partial | Toggle | ✅ | ✅ |
| GTM server-side | RE2 | Partial | Configurable | ❌ | ❌ |
| Looker `REGEXP_MATCH` | RE2 | **Full** | Sensitive | ❌ | ❌ |
| Looker `REGEXP_CONTAINS` | RE2 | Partial | Sensitive | ❌ | ❌ |
| BigQuery `REGEXP_CONTAINS` | RE2 | Partial | Sensitive | ❌ | ❌ |

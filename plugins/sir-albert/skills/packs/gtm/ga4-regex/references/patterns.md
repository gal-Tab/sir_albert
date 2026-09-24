# GA4 Pattern Library

Tested regex patterns for common GA4 and GTM jobs. All patterns are RE2-compatible and verified against real GA4 surfaces. Use these as starting points instead of writing from scratch.

## Page path matching

Field: `page_path`, `page_location`, `unified_screen_name`

| Goal | Pattern | Anchoring | Notes |
|---|---|---|---|
| All product pages | `^/products/` | Partial OK | Matches `/products/`, `/products/123`, `/products/x/y` |
| Exact product index page | `^/products/?$` | Full | Trailing slash optional |
| Specific page (exact) | `^/contact$` | Full | Add `\?` if URL may have query string: `^/contact(\?.*)?$` |
| Blog posts only | `^/blog/[a-z0-9-]+/?$` | Full | Blog index excluded; only slugs |
| Any page in section | `^/(pricing\|plans\|billing)/` | Partial | Group sections with alternation |
| Excluding admin | `^/(?!admin)` | ❌ Lookahead not allowed in GA4 | Use two audience conditions instead: matches `^/` AND does NOT match `^/admin` |
| Localized paths | `^/(en\|de\|fr\|es\|ja)/products/` | Partial | List locales explicitly; safer than `^/[a-z]{2}/` which over-matches |
| Pages with query string | `\?` | Partial | Use partial match; `\?` matches literal `?` |
| Pages WITHOUT query string | `^[^?]*$` | Full | Character class negation |

## UTM and campaign parameters

Field: `page_location` (contains the full URL with query string), or specific dimensions like `source`, `medium`, `campaign`

| Goal | Pattern | Field | Notes |
|---|---|---|---|
| Any UTM-tagged URL | `[?&]utm_` | `page_location` | Common bug: people write `^utm_` which never matches; UTM params come AFTER `?` |
| Specific campaign | `^summer_sale_2026$` | `campaign` | Use full anchoring on the campaign dimension |
| Campaign family | `^summer_sale_` | `campaign` | Matches `summer_sale_2026`, `summer_sale_paid`, etc. |
| Paid campaigns only | `^(cpc\|ppc\|paid.*)$` | `medium` | Standard paid medium values |
| Brand vs non-brand | `(?i)\b(brand\|branded)\b` | `campaign` | Word boundaries prevent matching "rebranded" or "brandon" |
| Multiple sources | `^(google\|bing\|yahoo)$` | `source` | Search engines |
| Specific UTM source value in URL | `[?&]utm_source=brand([&]\|$)` | `page_location` | The `([&]\|$)` ensures exact value match, not `brand_secondary` |

## Event names

Field: `event_name`

| Goal | Pattern | Notes |
|---|---|---|
| Specific event | `^purchase$` | Always anchor event names fully |
| Multiple events | `^(purchase\|sign_up\|begin_checkout)$` | Conversion event group |
| All scroll events | `^scroll` | Partial OK; matches `scroll`, `scroll_25`, `scroll_50` |
| All form events | `^form_` | Matches `form_start`, `form_submit`, `form_error` |
| Exclude system events | `^(?!session_start\|first_visit\|user_engagement)` | ❌ Lookahead not allowed; use two conditions: "matches anything" AND "does NOT match `^(session_start\|first_visit\|user_engagement)$`" |

## Referral exclusions (unwanted referrals)

Field: domain in unwanted referrals settings

| Goal | Pattern | Notes |
|---|---|---|
| Single domain | `^example\.com$` | The `^` and `$` matter — without them, `example.com` matches `notexample.com.evil.io` |
| Domain + subdomains | `(^\|\.)example\.com$` | Matches `example.com`, `www.example.com`, `app.example.com` |
| Multiple domains | `(^\|\.)(example\.com\|partner\.com)$` | Common for cross-domain setups |
| Payment processors (common pattern) | `(^\|\.)(stripe\.com\|paypal\.com\|checkout\.\w+\.com)$` | Prevents referral attribution from payment redirects |

## Internal traffic / staff filtering

If filtering by hostname:

| Goal | Pattern | Notes |
|---|---|---|
| Staging environments | `^(staging\|dev\|qa)\.example\.com$` | Anchor fully |
| Specific staff subdomain | `^staff\.example\.com$` | |
| IP-like pattern (rare) | n/a — use GA4's IP filter, not regex | GA4 has a dedicated CIDR-based IP filter |

## Looker Studio specifics

Looker Studio's `REGEXP_MATCH` requires **full match** while `REGEXP_CONTAINS` does partial match. This is the opposite of GA4 audience behavior.

| Function | Pattern needed |
|---|---|
| `REGEXP_MATCH(Page, "^/products/.*$")` | Full anchoring required, trailing `.*$` needed |
| `REGEXP_CONTAINS(Page, "^/products/")` | Anchored at start only is fine |
| `REGEXP_EXTRACT(Page, "^/products/([^/]+)")` | Capture group returns the value |

## GTM client-side trigger patterns

GTM client-side uses JavaScript `RegExp`, which is more forgiving than RE2. But if you might migrate to sGTM later, write RE2-compatible regex anyway.

Common GTM patterns:

| Goal | Pattern | Trigger type |
|---|---|---|
| Click on any external link | `^https?://(?!example\.com)` | ❌ Lookahead works in client-side GTM only; for sGTM compatibility, invert the test |
| Internal link only | `^https?://([^/]*\.)?example\.com/` | Partial | Works in both client and server |
| Form submit on specific page | `^/contact$` (in Page Path trigger filter) | |
| Click URL ending in PDF | `\.pdf(\?.*)?$` | Allows query string after `.pdf` |

## Anti-patterns to call out

When a user shows you these, push back:

- `.*` at the start: `.*products` — wasteful, partial match doesn't need leading wildcard
- Unescaped dots in domains: `example.com` — matches `exampleXcom`
- `^utm_source` on page_location: UTM params don't start the URL
- Trailing `.*$` on partial-match surfaces: unnecessary
- Missing anchors on referral exclusions: `paypal.com` matches `notpaypal.com.attacker.io`
- Lookahead/lookbehind in GA4: rewrite as two conditions

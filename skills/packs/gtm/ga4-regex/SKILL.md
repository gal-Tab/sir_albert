---
name: ga4-regex
description: >
  Validate, test, and explain regex patterns for Google Analytics 4 (GA4) and Google Tag Manager (GTM).
  Use whenever someone writes, debugs, or asks about a GA4 regex — including audiences, explorations,
  custom definitions, data stream filters, internal/cross-domain referral exclusions, unwanted referrals,
  GTM trigger filters, or Looker Studio regex matches. Trigger on phrases like "GA4 regex", "regex for
  page_path", "match these URLs", "exclude this campaign", "regex tester", "RE2", "why doesn't my regex
  match in GA4", or any combination of GA4/GTM + regex/pattern/match/exclude/filter. Especially trigger
  when the user shares a regex that uses lookbehind, backreferences, or named groups — GA4 uses RE2,
  which silently rejects or fails on PCRE-only features, and surfacing that is the main point of this skill.
---

# GA4 Regex

## Mission

Help marketing operations, analytics, and growth teams write regex patterns that **actually work in GA4 and GTM** — not just regex that works on regex101. The headline value of this skill is catching RE2 incompatibilities before they ship to production audiences, exclusion lists, or trigger conditions.

## Why this skill exists

Most regex tutorials assume PCRE (Perl-Compatible Regular Expressions) — the flavor used by JavaScript, Python, regex101.com, and most online testers. **GA4 and the Google Tag Manager server-side runtime do not use PCRE.** They use Google's RE2 engine, which deliberately rejects features that allow catastrophic backtracking.

This means a pattern that tests perfectly on regex101.com can:
- Be silently rejected by GA4's UI without a useful error
- Match nothing in a GA4 audience even though it "should"
- Behave differently in client-side GTM (JS RegExp) vs server-side GTM (RE2)

The job of this skill is to (a) explain GA4's regex flavor, (b) validate patterns against RE2 rules, and (c) provide a tested pattern library for the common GA4 jobs.

## When to use this skill

Use whenever:
- A user writes or pastes a regex intended for GA4, GTM, Looker Studio, or a similar Google product
- A user asks why their regex "isn't working" in GA4 even though it works elsewhere
- A user needs a regex for a specific GA4 task (page_path matching, UTM filtering, event name matching, referral exclusion, internal traffic filter)
- A user asks to "test" regex patterns against a list of strings in a GA4 context
- A user is migrating regex from Universal Analytics (which used different rules) to GA4

Do **not** use this skill for:
- General-purpose regex unrelated to GA4/GTM (just use Python `re` or JS `RegExp` directly)
- Writing literal SQL `REGEXP` for BigQuery exports — BigQuery uses RE2 too, but the GA4 export schema concerns are different (point user to BigQuery docs)

## Core workflow

When a user brings a GA4 regex question, walk through these steps in order. Skip steps that don't apply.

### Step 1: Identify the GA4 surface

GA4 surfaces handle regex slightly differently. Ask or infer which one:

| Surface | Engine | Anchoring | Case |
|---|---|---|---|
| GA4 Audience builder (matches regex) | RE2 | Partial match by default (use `^...$` for full) | Case-sensitive unless using `(?i)` |
| GA4 Explorations filter (matches regex) | RE2 | Partial match | Case-sensitive |
| GA4 Data stream — unwanted referrals | RE2 | Domain match, partial | Case-insensitive |
| GA4 Data stream — internal traffic IPs | CIDR or RE2 | n/a | n/a |
| GA4 Cross-domain configuration | RE2 | Domain match, partial | Case-insensitive |
| GTM client-side trigger filter | JavaScript `RegExp` (PCRE-ish) | Partial match | Configurable per trigger |
| GTM server-side (sGTM) | RE2 | Partial match | Configurable |
| Looker Studio `REGEXP_MATCH` | RE2 | **Full match required** | Case-sensitive |
| Looker Studio `REGEXP_CONTAINS` | RE2 | Partial match | Case-sensitive |

**Anchoring is the #1 source of bugs.** GA4 audiences do partial matching — `^/products` matches `/products` AND `/products/123`. Looker Studio's `REGEXP_MATCH` does full matching — `^/products` matches nothing unless the entire string is `/products`.

### Step 2: Validate against RE2

Read `references/re2-rules.md` for the full incompatibility list. The high-impact ones to check every pattern for:

1. **Lookbehind** — `(?<=foo)bar` or `(?<!foo)bar` → **NOT SUPPORTED in RE2.** Common in PCRE tutorials. Will silently fail in GA4.
2. **Backreferences** — `(\w+)\s+\1` (matching the same captured group again) → **NOT SUPPORTED.**
3. **Possessive quantifiers** — `a++`, `a*+`, `a?+` → **NOT SUPPORTED.**
4. **Atomic groups** — `(?>foo)` → **NOT SUPPORTED.**
5. **Recursion** — `(?R)` or `(?0)` → **NOT SUPPORTED.**

Lookahead (`(?=foo)`, `(?!foo)`) **is** supported in RE2 in recent versions but is **NOT supported in GA4** specifically — GA4 uses RE2 in a mode that rejects lookahead. If a user has lookahead, rewrite without it.

If you spot any of the above, flag immediately. Don't try to "fix" the regex silently — show the user what's wrong, explain why, and offer a RE2-compatible rewrite.

### Step 3: Test the pattern

If the user provided test strings, run the pattern against them using Python's `re2` library (which mirrors GA4 behavior) or, if `re2` isn't installed, use Python's built-in `re` with a warning that PCRE-specific features won't be flagged.

```python
# Preferred: use scripts/test_regex.py which handles both engines
python /path/to/ga4-regex/scripts/test_regex.py --pattern "^/products/.*" --strings "/products/123" "/about"
```

The script outputs per-string match results, capture groups (if any), and RE2 compatibility warnings.

### Step 4: Explain capture groups (if relevant)

GA4 supports capture groups in specific places (e.g., extracting a value from `page_location` into a custom dimension via Google Tag Manager). When the user's pattern has `(...)`, explicitly tell them which group captures what — users routinely miss that group 0 is the whole match and group 1 is the first parenthesized subexpression.

### Step 5: Suggest from the pattern library

For common GA4 jobs, don't write a pattern from scratch — pull from `references/patterns.md`. Examples:

- "Match all product pages" → `^/products/`
- "Match exact path" → `^/contact$`
- "Match any UTM-tagged URL" → `[?&]utm_` (NOT `^utm_` — utm params don't start the URL)
- "Match brand campaign exact-match" → `^brand[-_]campaign$`
- "Exclude internal subdomains" → `^(staff|admin|internal)\.example\.com$`

If a user's hand-written pattern overlaps with a library pattern, suggest the library version with a note on why it's more robust.

### Step 6: Output format

Default to this structure for any regex response:

```
Pattern: <the regex>
Surface: <GA4 audience / Looker Studio / etc.>
RE2-compatible: yes / no (with reason)
Anchoring: full / partial / unanchored
Case-sensitivity: <as written>
Matches: <test results, if test strings provided>
Notes: <gotchas, suggested alternatives>
```

Keep it scannable. Marketing ops users want the verdict first, the explanation second.

## Reference files

Load these when relevant — do not paste their full contents into responses, summarize and link.

- `references/re2-rules.md` — Full RE2 incompatibility list, with PCRE → RE2 rewrites for each blocked feature
- `references/patterns.md` — Tested pattern library organized by GA4 use case (page_path, UTM, event names, referrals, domains)
- `references/surfaces.md` — Per-surface behavior cheat sheet (where regex appears in GA4/GTM and how each one handles anchoring, case, and partial matching)

## Scripts

- `scripts/test_regex.py` — Test one or more patterns against one or more strings, with RE2 compatibility checking. Run before claiming a pattern works.

## Hard rules

1. **Never** validate a GA4 regex using only regex101.com semantics. If the user pastes a regex101 share link, treat it as PCRE-tested and re-validate against RE2.
2. **Never** suggest lookbehind in a GA4 regex. Always rewrite using alternation or capture-group-then-filter logic.
3. **Always** state the anchoring behavior of the surface. Partial-match surfaces and full-match surfaces silently produce opposite results from the same pattern.
4. **Always** show the user the test results when test strings are provided. Don't summarize as "this works" — show which strings matched and which didn't.
5. **Never** invent RE2 behavior. If unsure whether RE2 supports a feature, check `references/re2-rules.md` or run the test script — don't guess.

## Common failure modes to watch for

- User writes `/products/.*` thinking they need `.*` at the end → unnecessary in partial-match surfaces, harmful in full-match surfaces if anchored wrong
- User writes `^utm_source=brand$` for a page_location field → `utm_source` is never at the start of a URL, the anchor is wrong
- User writes `example\.com` for unwanted referral exclusion → matches `notexample.com` too; need `^example\.com$` or `(^|\.)example\.com$`
- User copies regex from a Stack Overflow answer that uses `(?<=...)` lookbehind → won't work in GA4, needs rewrite
- User tests a case-sensitive regex against lowercase test strings while the real GA4 data has mixed case → false confidence

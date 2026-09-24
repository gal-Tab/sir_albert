# RE2 Rules — What Works and What Doesn't in GA4

GA4 uses Google's RE2 regex engine. RE2 deliberately omits PCRE features that allow catastrophic backtracking. This document lists every PCRE feature that breaks in GA4 and how to rewrite it.

## Quick reference: what's blocked

| Feature | PCRE syntax | RE2 / GA4 | Rewrite strategy |
|---|---|---|---|
| Lookbehind (positive) | `(?<=foo)bar` | ❌ NOT SUPPORTED | Capture group + filter downstream |
| Lookbehind (negative) | `(?<!foo)bar` | ❌ NOT SUPPORTED | Alternation or downstream filter |
| Lookahead (positive) | `foo(?=bar)` | ⚠️ Rejected by GA4 | Match full context, use capture |
| Lookahead (negative) | `foo(?!bar)` | ⚠️ Rejected by GA4 | Alternation listing allowed cases |
| Backreference | `(\w+)\s+\1` | ❌ NOT SUPPORTED | Move logic out of regex |
| Possessive quantifier | `a++` `a*+` `a?+` | ❌ NOT SUPPORTED | Use plain `a+`, `a*`, `a?` (RE2 is linear anyway) |
| Atomic group | `(?>foo)` | ❌ NOT SUPPORTED | Use plain `(foo)` |
| Recursion | `(?R)` `(?0)` | ❌ NOT SUPPORTED | Cannot be rewritten in regex |
| Conditional | `(?(1)yes\|no)` | ❌ NOT SUPPORTED | Use alternation |
| Named backreference | `(?P=name)` | ❌ NOT SUPPORTED | Move logic out of regex |
| `\K` (reset match) | `foo\Kbar` | ❌ NOT SUPPORTED | Use capture group |
| Unicode property | `\p{L}` | ✅ Supported in RE2, but limited in GA4 | Stick to ASCII classes when possible |

## What works fine

These standard features are safe in GA4:

- Character classes: `[a-z]`, `[^0-9]`, `\d`, `\w`, `\s`, `.`
- Quantifiers: `*`, `+`, `?`, `{n}`, `{n,}`, `{n,m}`
- Anchors: `^`, `$`
- Alternation: `foo|bar`
- Grouping: `(foo)` — both as capture and for scope
- Non-capturing groups: `(?:foo)`
- Named capture groups: `(?P<name>foo)` — supported, but GA4 rarely surfaces the names
- Case-insensitive flag: `(?i)foo` — works inline
- Escaped literals: `\.`, `\?`, `\/`, `\(`, `\)`, etc.

## High-impact rewrites

### Lookbehind → capture or alternation

PCRE: `(?<=utm_source=)brand` — "match 'brand' only when preceded by 'utm_source='"

RE2-safe rewrite: `utm_source=(brand)` — capture group 1 holds the value. In GA4, if you only need to test for presence, this works as a partial match. If you need the captured value (e.g., in GTM regex table lookup), use group 1.

### Negative lookbehind → list what IS allowed

PCRE: `(?<!staging\.)example\.com` — "match example.com unless preceded by 'staging.'"

RE2-safe rewrite: `^(www\.|app\.|m\.)?example\.com$` — list the subdomains you DO want. This is more verbose but explicit, which is better for marketing-ops review.

### Negative lookahead → alternation of allowed cases

PCRE: `^/products/(?!internal)` — "any product page except internal ones"

RE2-safe rewrite: `^/products/(?:public|catalog|item|category)/` — enumerate the allowed paths. If the allowed set is too large to enumerate, the filtering should happen in the GA4 audience builder as a SECOND condition ("page_path matches `^/products/`" AND "page_path does NOT match `/internal`").

### Backreference → split into two conditions

PCRE: `(\w+)/.*/\1` — "same word at start and end"

RE2-safe approach: This kind of identity matching cannot be done in RE2. Move it to audience logic: capture the first segment in one condition and the last segment in another, then compare them downstream (in BigQuery export, for example).

## Anchoring nuances

RE2 supports `^` and `$` as line/string anchors. In GA4:

- `^` = start of the field value
- `$` = end of the field value
- `.` does NOT match newlines by default (which matches PCRE default behavior)
- There is no `\A` or `\z` in RE2 (use `^` and `$`)

Word boundaries `\b` and `\B` ARE supported. Use them when you want "exactly this word":

- `\bbrand\b` matches `brand campaign` but not `brandon` or `unbranded`

## Case sensitivity

GA4 audience and exploration regex is **case-sensitive by default**. To make a pattern case-insensitive, use the inline flag `(?i)` at the start:

- `(?i)^/products/` matches `/Products/`, `/PRODUCTS/`, `/products/`

GTM client-side has a separate "Ignore case" checkbox per trigger filter — prefer that over `(?i)` in client-side GTM because it's more visible to anyone auditing the container.

## Escaping

Forward slash `/` does NOT need to be escaped in RE2 (unlike `/.../` syntax in JavaScript). `^/products/` is correct, not `^\/products\/`. Don't add unnecessary backslashes — they don't hurt but they make the pattern harder to read.

The dot `.` ALWAYS needs to be escaped when you mean a literal dot. `example.com` matches `exampleXcom`. Use `example\.com`.

## Testing for RE2 compatibility

If you have Python's `pyre2` or `google-re2` installed, you can test directly:

```python
import re2  # or: from google import re2
try:
    pattern = re2.compile(user_pattern)
    print("RE2-compatible")
except re2.error as e:
    print(f"NOT RE2-compatible: {e}")
```

If `re2` is not installed, fall back to the heuristic check in `scripts/test_regex.py`, which flags the high-impact PCRE-only features by string inspection. The heuristic is not exhaustive but catches the common cases.

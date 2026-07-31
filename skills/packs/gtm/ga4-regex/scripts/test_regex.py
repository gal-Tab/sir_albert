#!/usr/bin/env python3
"""
GA4 Regex Tester

Tests one or more regex patterns against one or more strings, with RE2
compatibility checking. Mirrors the behavior of GA4 audience/exploration
regex (RE2, partial match, case-sensitive by default).

Usage:
    python test_regex.py --pattern "^/products/" --strings "/products/123" "/about"
    python test_regex.py --pattern "^/products/" "^/blog/" --strings "/products/123" "/blog/post"
    python test_regex.py --pattern "(?i)^/PRODUCTS/" --strings "/products/123"
    python test_regex.py --pattern "(?<=foo)bar" --strings "foobar"  # flags lookbehind

Engine: tries google-re2 / pyre2 first (true RE2 semantics). Falls back to
Python's built-in `re` with a heuristic PCRE-feature scan if RE2 is not
installed.
"""

import argparse
import re
import sys
from typing import List, Tuple

# Heuristic patterns for PCRE-only features that RE2 / GA4 reject.
# Order matters — more specific patterns first.
PCRE_ONLY_FEATURES = [
    (r"\(\?<=", "positive lookbehind (?<=...)", "Rewrite using capture groups or a downstream condition."),
    (r"\(\?<!", "negative lookbehind (?<!...)", "List allowed cases explicitly using alternation."),
    (r"\(\?=", "positive lookahead (?=...)", "GA4 rejects lookahead even though RE2 supports it. Enumerate allowed cases."),
    (r"\(\?!", "negative lookahead (?!...)", "GA4 rejects lookahead. Use two audience conditions: a positive match plus a negative match."),
    (r"\\\d+", "backreference (\\1, \\2, ...)", "RE2 cannot match a previously captured value. Move identity logic out of regex."),
    (r"\(\?>", "atomic group (?>...)", "Replace with a plain capture group (foo). RE2 is linear-time anyway."),
    (r"\(\?R\)|\(\?0\)", "recursion (?R) or (?0)", "Recursive regex cannot be expressed in RE2."),
    (r"\(\?\(", "conditional (?(...)...|...)", "Rewrite using alternation."),
    (r"\\K", "match reset \\K", "Use a capture group instead."),
    (r"[*+?]\+", "possessive quantifier (a++, a*+, a?+)", "Use plain quantifiers; RE2 is already linear-time."),
]


def detect_pcre_only(pattern: str) -> List[Tuple[str, str]]:
    """Return list of (feature_name, fix_hint) for PCRE-only features in pattern."""
    findings = []
    for regex, name, hint in PCRE_ONLY_FEATURES:
        if re.search(regex, pattern):
            findings.append((name, hint))
    return findings


def try_re2():
    """Try to import a real RE2 binding. Return module or None."""
    try:
        import re2  # pyre2
        return re2
    except ImportError:
        pass
    try:
        from google import re2 as g_re2  # google-re2
        return g_re2
    except ImportError:
        pass
    return None


def test_pattern(pattern: str, strings: List[str], full_match: bool = False) -> dict:
    """
    Test pattern against strings. Returns dict with:
      - re2_compatible: bool
      - re2_warnings: list of (feature, fix)
      - results: list of {string, matched, groups}
      - error: str or None
    """
    re2_warnings = detect_pcre_only(pattern)
    re2_compatible = len(re2_warnings) == 0

    re2_mod = try_re2()

    result = {
        "pattern": pattern,
        "re2_compatible": re2_compatible,
        "re2_warnings": re2_warnings,
        "engine_used": "google-re2" if re2_mod else "python-re (fallback)",
        "results": [],
        "error": None,
    }

    try:
        if re2_mod:
            compiled = re2_mod.compile(pattern)
        else:
            compiled = re.compile(pattern)
    except Exception as e:
        result["error"] = f"Pattern failed to compile: {e}"
        return result

    for s in strings:
        try:
            if full_match:
                m = compiled.fullmatch(s) if hasattr(compiled, "fullmatch") else compiled.match(s)
                # For RE2 fullmatch fallback: check the match consumed the whole string
                if m and not full_match_consumed(m, s):
                    m = None
            else:
                m = compiled.search(s)
        except Exception as e:
            result["results"].append({"string": s, "matched": False, "error": str(e)})
            continue

        if m:
            try:
                groups = list(m.groups())
            except Exception:
                groups = []
            result["results"].append({
                "string": s,
                "matched": True,
                "match_text": m.group(0),
                "groups": groups,
            })
        else:
            result["results"].append({"string": s, "matched": False})

    return result


def full_match_consumed(m, s: str) -> bool:
    """Check whether match m consumed the whole string s."""
    try:
        return m.start() == 0 and m.end() == len(s)
    except Exception:
        return False


def format_result(result: dict) -> str:
    """Format result as human-readable output."""
    lines = []
    lines.append(f"Pattern:        {result['pattern']}")
    lines.append(f"Engine:         {result['engine_used']}")
    lines.append(f"RE2-compatible: {'yes' if result['re2_compatible'] else 'NO'}")

    if result["re2_warnings"]:
        lines.append("RE2 warnings:")
        for feat, hint in result["re2_warnings"]:
            lines.append(f"  - {feat}")
            lines.append(f"    fix: {hint}")

    if result["error"]:
        lines.append(f"ERROR: {result['error']}")
        return "\n".join(lines)

    lines.append("Results:")
    for r in result["results"]:
        if r.get("error"):
            lines.append(f"  [ERROR] {r['string']!r}: {r['error']}")
        elif r["matched"]:
            grp = f"  groups={r['groups']}" if r.get("groups") else ""
            lines.append(f"  [MATCH] {r['string']!r}  matched={r.get('match_text', '')!r}{grp}")
        else:
            lines.append(f"  [    ] {r['string']!r}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="GA4 regex tester with RE2 compatibility checking")
    parser.add_argument("--pattern", "-p", nargs="+", required=True, help="One or more regex patterns")
    parser.add_argument("--strings", "-s", nargs="+", required=True, help="One or more test strings")
    parser.add_argument("--full-match", action="store_true", help="Require full match (Looker Studio REGEXP_MATCH behavior). Default: partial match (GA4 audience behavior).")
    args = parser.parse_args()

    for i, pattern in enumerate(args.pattern):
        if i > 0:
            print("\n" + "=" * 60)
        result = test_pattern(pattern, args.strings, full_match=args.full_match)
        print(format_result(result))


if __name__ == "__main__":
    main()

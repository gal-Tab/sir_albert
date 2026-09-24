#!/usr/bin/env python3
"""Attester — fail on metric-spec drift (the trust layer, M3.4).

A metric's canonical spec is the attestable artifact: a z2h look's `look_json`
(declarative measures/dimensions/filters) or a canonical `.sql`. Two runs are
equal iff their specs match — no re-verifying numbers by hand.

    python attester.py <canonical.json> <candidate.json>   # z2h look specs
    python attester.py <canonical.sql>  <candidate.sql>    # canonical SQL

Exit 0 = ATTESTED (specs match). Exit 1 = DRIFT (blocks data-review). Exit 2 = usage/error.
"""
import json, re, sys, difflib


def _norm(path):
    with open(path) as f:
        text = f.read()
    if path.endswith(".json"):
        return json.dumps(json.loads(text), sort_keys=True, indent=2)
    # SQL (or anything else): collapse whitespace, lowercase — compare intent, not formatting
    return re.sub(r"\s+", " ", text).strip().lower()


def attest(canonical, candidate):
    a, b = _norm(canonical), _norm(candidate)
    if a == b:
        print(f"ATTESTED: {candidate} matches canonical {canonical}")
        return 0
    print(f"DRIFT: {candidate} does NOT match canonical {canonical}", file=sys.stderr)
    for line in difflib.unified_diff(
        a.splitlines(), b.splitlines(), "canonical", "candidate", lineterm=""
    ):
        print(line, file=sys.stderr)
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: attester.py <canonical> <candidate>  (.json or .sql)", file=sys.stderr)
        sys.exit(2)
    try:
        sys.exit(attest(sys.argv[1], sys.argv[2]))
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

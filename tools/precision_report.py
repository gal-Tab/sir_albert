#!/usr/bin/env python3
"""04b — Precision report for prompt_router patterns.

Usage: python3 tools/precision_report.py [--out docs/plans/2026-09-24-w3-router/]

Reads:
  ~/.claude/projects/**/*.jsonl  (user messages, skip /subagents/)
  plugins/sir-albert/hooks/router_data.json

Outputs:
  precision-report-YYYY-MM-DD.txt to the output dir (default: docs/plans/2026-09-24-w3-router/)
  Full match samples to /tmp/w3/precision-samples.json (redacted to ≤80 chars per snippet)
"""
import glob
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
DATA_FILE = REPO_ROOT / "plugins/sir-albert/hooks/router_data.json"

DEFAULT_OUT = REPO_ROOT / "docs/plans/2026-09-24-w3-router"

MAX_LINE_BYTES = 200_000


def extract_user_prompts():
    files = glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True)
    files = [f for f in files if "/subagents/" not in f]
    prompts = []
    skipped = 0
    for f in files:
        try:
            with open(f, encoding="utf-8", errors="ignore") as fh:
                for raw in fh:
                    if len(raw) > MAX_LINE_BYTES:
                        skipped += 1
                        continue
                    try:
                        msg = json.loads(raw)
                    except Exception:
                        continue
                    # Claude Code JSONL: {"type":"user","message":{"content":...}}
                    msg_type = msg.get("type", "")
                    inner = msg.get("message") if isinstance(msg.get("message"), dict) else None
                    if msg_type == "user" and inner is not None:
                        content = inner.get("content", "")
                    elif msg.get("role") in ("user", "human"):
                        content = msg.get("content", "")
                    else:
                        continue
                    if isinstance(content, str):
                        text = content
                    elif isinstance(content, list):
                        parts = []
                        for block in content:
                            if not isinstance(block, dict):
                                continue
                            if block.get("type") in ("tool_result", "tool_use"):
                                continue
                            parts.append(block.get("text", ""))
                        text = " ".join(parts)
                    else:
                        continue
                    text = text.strip()
                    if text:
                        prompts.append(text)
        except Exception as e:
            print(f"[skip] {f}: {e}", file=sys.stderr)
    return prompts, skipped


def compile_patterns(data):
    patterns = []
    for entry in sorted(data.get("keyword_patterns", []), key=lambda e: e["order"]):
        try:
            compiled = re.compile(entry["pattern"], re.IGNORECASE | re.UNICODE)
            patterns.append((entry["intent"], compiled, entry["nudge"]))
        except re.error as e:
            print(f"[warn] bad pattern {entry['pattern']!r}: {e}", file=sys.stderr)
    for entry in sorted(data.get("hebrew_patterns", []), key=lambda e: e["order"]):
        try:
            compiled = re.compile(entry["pattern"], re.UNICODE)
            patterns.append((entry["intent"], compiled, entry["nudge"]))
        except re.error as e:
            print(f"[warn] bad Hebrew pattern: {e}", file=sys.stderr)
    return patterns


def run_report(out_dir: Path):
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    patterns = compile_patterns(data)

    print(f"Loading prompts...", file=sys.stderr)
    prompts, skipped_large = extract_user_prompts()
    total = len(prompts)
    print(f"  {total} user prompts loaded ({skipped_large} large lines skipped)", file=sys.stderr)

    # Route each prompt to first matching pattern (first-match wins)
    matched_total = 0
    per_intent_matches = defaultdict(list)  # intent -> list of prompt texts

    for prompt in prompts:
        for intent, compiled, nudge in patterns:
            if compiled.search(prompt):
                matched_total += 1
                per_intent_matches[intent].append(prompt)
                break  # first-match only

    fire_rate = matched_total / total if total > 0 else 0.0

    # Sample: up to 10 per intent, shuffled, redacted to ≤80 chars
    samples = {}
    for intent, hits in per_intent_matches.items():
        shuffled = hits[:]
        random.shuffle(shuffled)
        samples[intent] = [h[:80].replace("\n", " ") for h in shuffled[:10]]

    # Build report text
    lines = []
    lines.append(f"Precision Report — {date.today()}")
    lines.append("=" * 50)
    lines.append(f"Total user prompts:  {total:,}")
    lines.append(f"Total matches:       {matched_total:,}")
    lines.append(f"Overall fire rate:   {fire_rate:.1%}  (target: <15%)")
    lines.append(f"Large lines skipped: {skipped_large}")
    lines.append("")
    lines.append("Per-route fire rates:")
    lines.append(f"  {'Intent':<20} {'Matches':>8}  {'Rate':>6}")
    lines.append(f"  {'-'*20}  {'-'*8}  {'-'*6}")
    for intent, compiled, nudge in patterns:
        n = len(per_intent_matches.get(intent, []))
        rate = n / total if total > 0 else 0.0
        lines.append(f"  {intent:<20} {n:>8,}  {rate:>6.1%}")
    lines.append("")
    lines.append("Per-route samples (≤10, ≤80 chars each):")
    for intent, compiled, nudge in patterns:
        hits = samples.get(intent, [])
        lines.append(f"\n  [{intent}] ({len(per_intent_matches.get(intent,[]))} total)")
        if not hits:
            lines.append("    (no matches)")
        for h in hits:
            lines.append(f"    • {h!r}")

    report_text = "\n".join(lines)

    # Write report
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / f"precision-report-{date.today()}.txt"
    report_path.write_text(report_text, encoding="utf-8")
    print(f"Report written: {report_path}", file=sys.stderr)

    # Write full samples to /tmp/w3/ (not committed)
    Path("/tmp/w3").mkdir(parents=True, exist_ok=True)
    (Path("/tmp/w3") / "precision-samples.json").write_text(
        json.dumps({"total": total, "matched": matched_total, "per_intent": {k: v for k, v in samples.items()}},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Print summary to stdout
    print(report_text)
    return fire_rate


if __name__ == "__main__":
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    rate = run_report(out_dir)
    sys.exit(0 if rate < 0.15 else 1)

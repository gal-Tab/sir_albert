#!/usr/bin/env python3
"""strip_harness_sessions.py — remove harness rows from sir-albert-sessions.jsonl.

Called once per tranche (not per run) to remove rows with cwd under the scratch dir.

Usage:
  python3 strip_harness_sessions.py --scratch-cwd /tmp/w4-eval-scratch
  python3 strip_harness_sessions.py --sessions-file /path/to/file.jsonl --scratch-cwd /tmp/scratch
"""
import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def strip(sessions_file: Path, scratch_cwd: str) -> None:
    if not sessions_file.exists():
        print(f"sessions file not found: {sessions_file}")
        return

    rows = []
    for line in sessions_file.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                rows.append({"_raw": line})

    # Backup
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = sessions_file.parent / f"{sessions_file.name}.bak-{ts}"
    shutil.copy2(sessions_file, backup)

    kept = []
    stripped = 0
    for row in rows:
        cwd = row.get("cwd", "") if isinstance(row, dict) and "_raw" not in row else ""
        if cwd.startswith(scratch_cwd):
            stripped += 1
        else:
            kept.append(row)

    # Rewrite
    with sessions_file.open("w") as f:
        for row in kept:
            if isinstance(row, dict) and "_raw" in row:
                f.write(row["_raw"] + "\n")
            else:
                f.write(json.dumps(row) + "\n")

    print(f"stripped {stripped} harness rows, kept {len(kept)} rows")
    print(f"backup: {backup}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--sessions-file",
        type=Path,
        default=Path.home() / ".claude" / "sir-albert-sessions.jsonl",
    )
    p.add_argument("--scratch-cwd", required=True)
    args = p.parse_args()
    strip(args.sessions_file, args.scratch_cwd)


if __name__ == "__main__":
    main()

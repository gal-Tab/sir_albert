"""Tests for strip_harness_sessions.py — ticket 07."""
import json
from pathlib import Path

import pytest

STRIP_SCRIPT = Path(__file__).parent.parent.parent / "tools" / "eval" / "strip_harness_sessions.py"


@pytest.fixture()
def sessions_file(tmp_path):
    rows = [
        {"cwd": "/tmp/w4-eval-scratch/work", "session_id": "s1"},
        {"cwd": "/tmp/w4-eval-scratch/work", "session_id": "s2"},
        {"cwd": "/Users/galta/Development/myproject", "session_id": "s3"},
        {"cwd": "/Users/galta/Development/other", "session_id": "s4"},
        {"cwd": "/home/user/.claude", "session_id": "s5"},
    ]
    f = tmp_path / "sessions.jsonl"
    f.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return f


def run_strip(sessions_file, scratch_cwd):
    import subprocess
    import sys
    result = subprocess.run(
        [
            "/usr/local/bin/python3.13",
            str(STRIP_SCRIPT),
            "--sessions-file",
            str(sessions_file),
            "--scratch-cwd",
            scratch_cwd,
        ],
        capture_output=True,
        text=True,
    )
    return result


def test_strips_exactly_2_rows(sessions_file):
    result = run_strip(sessions_file, "/tmp/w4-eval-scratch")
    assert result.returncode == 0, f"strip failed: {result.stderr}"
    assert "stripped 2 harness rows" in result.stdout
    assert "kept 3 rows" in result.stdout


def test_preserves_non_harness_rows(sessions_file):
    run_strip(sessions_file, "/tmp/w4-eval-scratch")
    rows = [json.loads(l) for l in sessions_file.read_text().splitlines() if l.strip()]
    assert len(rows) == 3
    cwds = {r["cwd"] for r in rows}
    assert "/tmp/w4-eval-scratch/work" not in cwds


def test_backup_created(sessions_file):
    run_strip(sessions_file, "/tmp/w4-eval-scratch")
    backups = list(sessions_file.parent.glob("sessions.jsonl.bak-*"))
    assert len(backups) == 1, f"Expected 1 backup, got: {backups}"


def test_empty_file_ok(tmp_path):
    f = tmp_path / "empty.jsonl"
    f.write_text("")
    result = run_strip(f, "/tmp/w4-eval-scratch")
    assert result.returncode == 0
    assert "stripped 0" in result.stdout

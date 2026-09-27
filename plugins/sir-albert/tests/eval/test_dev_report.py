"""Tests for dev_report.py — the per-slice hit/fire scorer for arm B dev runs.

The fixture uses the real artifact schema (all fields that run_one.sh produces),
keyed by _hash (the W4 aee9250 lesson: earlier versions used a non-_hash key).
"""
import importlib.util as _ilu
import json
import os
from pathlib import Path

import pytest

DEV_REPORT = Path(__file__).parent.parent.parent / "tools" / "eval" / "dev_report.py"

_spec = _ilu.spec_from_file_location("dev_report", DEV_REPORT)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


def _make_artifact(arm, prompt_hash, rep, skills_called, final_text="response",
                   context_turns=0, result_count=1, truncated=False, cost=0.10):
    """Build a minimal but real-schema artifact dict."""
    return {
        "arm": arm,
        "prompt_hash": prompt_hash,
        "rep": rep,
        "prompt_text": "some prompt",
        "model": "claude-sonnet-5",
        "exit_code": 0,
        "timestamp_utc": "2026-09-27T12:00:00",
        "cost_usd": cost,
        "turn_count": 1,
        "budget_capped": False,
        "result_subtype": "success",
        "skills_loaded": [],
        "skills_called": skills_called,
        "assistant_text": final_text,
        "truncated": truncated,
        "result_count": result_count,
        "final_text": final_text,
        "context_turns": context_turns,
        "init_event": None,
        "result_event": {"type": "result", "subtype": "success", "total_cost_usd": cost,
                         "num_turns": 1, "is_error": False, "result": final_text},
    }


def _make_sample(rows):
    """Build a sample.jsonl string from list of (hash, p2_slice, label) tuples."""
    lines = []
    for h, p2_slice, label in rows:
        lines.append(json.dumps({
            "_hash": h,
            "text": f"prompt for {h}",
            "p2_slice": p2_slice,
            "label": label,
        }))
    return "\n".join(lines) + "\n"


def test_dev_report_real_schema(tmp_path, capsys):
    """Real-schema fixtures: _hash keyed rows, full artifact fields, correct slices."""
    # Sample: 5 happy, 5 b_silent, 5 control (using _hash key)
    sample_rows = [
        ("aaa0000000000001", "happy_path", "brainstorm"),
        ("aaa0000000000002", "happy_path", "plan"),
        ("aaa0000000000003", "happy_path", "brainstorm"),
        ("aaa0000000000004", "happy_path", "plan"),
        ("aaa0000000000005", "happy_path", "brainstorm"),
        ("bbb0000000000001", "b_silent", "brainstorm"),
        ("bbb0000000000002", "b_silent", "plan"),
        ("bbb0000000000003", "b_silent", "brainstorm"),
        ("bbb0000000000004", "b_silent", "plan"),
        ("bbb0000000000005", "b_silent", "brainstorm"),
        ("ccc0000000000001", "control", "none"),
        ("ccc0000000000002", "control", "none"),
        ("ccc0000000000003", "control", "none"),
        ("ccc0000000000004", "control", "none"),
        ("ccc0000000000005", "control", "none"),
    ]
    sample_file = tmp_path / "sample.jsonl"
    sample_file.write_text(_make_sample(sample_rows))

    artifact_dir = tmp_path / "runs"
    artifact_dir.mkdir()

    # happy_path: all 5 hit (correct skill called)
    for h, _, label in sample_rows[:5]:
        skill = "sir-albert:brainstorm" if label == "brainstorm" else "sir-albert:plan"
        art = _make_artifact("b", h, 1, [skill], context_turns=2)
        (artifact_dir / f"b-{h}-rep1.json").write_text(json.dumps(art))

    # b_silent: 3 hit (correct skill), 2 miss (no skill called)
    hits = 0
    for h, _, label in sample_rows[5:10]:
        if hits < 3:
            skill = "sir-albert:brainstorm" if label == "brainstorm" else "sir-albert:plan"
            art = _make_artifact("b", h, 1, [skill], final_text="B called skill correctly")
            hits += 1
        else:
            art = _make_artifact("b", h, 1, [], final_text="B answered directly without skill")
        (artifact_dir / f"b-{h}-rep1.json").write_text(json.dumps(art))

    # control: all 5 silent (no fire)
    for h, _, _ in sample_rows[10:]:
        art = _make_artifact("b", h, 1, [], final_text="B answered control question directly")
        (artifact_dir / f"b-{h}-rep1.json").write_text(json.dumps(art))

    env = dict(os.environ, W4_SAMPLE_FILE=str(sample_file))
    old_env = os.environ.copy()
    os.environ.update(env)
    try:
        rc = _mod.main([str(DEV_REPORT), str(artifact_dir)])
    finally:
        os.environ.clear()
        os.environ.update(old_env)

    captured = capsys.readouterr()
    assert rc == 0, f"expected DEV PASS, got rc={rc}:\n{captured.out}"
    assert "DEV PASS" in captured.out
    assert "happy_path" in captured.out
    assert "b_silent" in captured.out
    assert "control" in captured.out

    # Verify per-prompt detail shows result_count and truncated fields
    assert "RC" in captured.out   # result_count column header
    assert "CtxT" in captured.out  # context_turns column header


def test_dev_report_fail_when_below_bar(tmp_path, capsys):
    """Reports DEV FAIL when b_silent has < 3 hits."""
    sample_rows = [
        ("aaa0000000000001", "happy_path", "brainstorm"),
        ("aaa0000000000002", "happy_path", "brainstorm"),
        ("aaa0000000000003", "happy_path", "brainstorm"),
        ("aaa0000000000004", "happy_path", "brainstorm"),
        ("aaa0000000000005", "happy_path", "brainstorm"),
        ("bbb0000000000001", "b_silent", "brainstorm"),
        ("bbb0000000000002", "b_silent", "brainstorm"),
        ("bbb0000000000003", "b_silent", "brainstorm"),
        ("bbb0000000000004", "b_silent", "brainstorm"),
        ("bbb0000000000005", "b_silent", "brainstorm"),
        ("ccc0000000000001", "control", "none"),
        ("ccc0000000000002", "control", "none"),
        ("ccc0000000000003", "control", "none"),
        ("ccc0000000000004", "control", "none"),
        ("ccc0000000000005", "control", "none"),
    ]
    sample_file = tmp_path / "sample.jsonl"
    sample_file.write_text(_make_sample(sample_rows))

    artifact_dir = tmp_path / "runs"
    artifact_dir.mkdir()

    # happy_path: 5/5 hit
    for h, _, _ in sample_rows[:5]:
        art = _make_artifact("b", h, 1, ["sir-albert:brainstorm"])
        (artifact_dir / f"b-{h}-rep1.json").write_text(json.dumps(art))

    # b_silent: only 2 hit (below bar of 3)
    for i, (h, _, _) in enumerate(sample_rows[5:10]):
        if i < 2:
            art = _make_artifact("b", h, 1, ["sir-albert:brainstorm"])
        else:
            art = _make_artifact("b", h, 1, [], final_text="no skill called")
        (artifact_dir / f"b-{h}-rep1.json").write_text(json.dumps(art))

    # control: all silent
    for h, _, _ in sample_rows[10:]:
        art = _make_artifact("b", h, 1, [])
        (artifact_dir / f"b-{h}-rep1.json").write_text(json.dumps(art))

    old_env = os.environ.copy()
    os.environ["W4_SAMPLE_FILE"] = str(sample_file)
    try:
        rc = _mod.main([str(DEV_REPORT), str(artifact_dir)])
    finally:
        os.environ.clear()
        os.environ.update(old_env)

    captured = capsys.readouterr()
    assert rc == 1, f"expected DEV FAIL (rc=1), got rc={rc}"
    assert "DEV FAIL" in captured.out
    assert "Misses" in captured.out


def test_dev_report_control_fire_fails(tmp_path, capsys):
    """A fire on a control row (label=none) is a miss and causes DEV FAIL."""
    sample_rows = [
        ("aaa0000000000001", "happy_path", "brainstorm"),
        ("aaa0000000000002", "happy_path", "brainstorm"),
        ("aaa0000000000003", "happy_path", "brainstorm"),
        ("aaa0000000000004", "happy_path", "brainstorm"),
        ("aaa0000000000005", "happy_path", "brainstorm"),
        ("bbb0000000000001", "b_silent", "brainstorm"),
        ("bbb0000000000002", "b_silent", "brainstorm"),
        ("bbb0000000000003", "b_silent", "brainstorm"),
        ("bbb0000000000004", "b_silent", "brainstorm"),
        ("bbb0000000000005", "b_silent", "brainstorm"),
        ("ccc0000000000001", "control", "none"),
        ("ccc0000000000002", "control", "none"),
        ("ccc0000000000003", "control", "none"),
        ("ccc0000000000004", "control", "none"),
        ("ccc0000000000005", "control", "none"),
    ]
    sample_file = tmp_path / "sample.jsonl"
    sample_file.write_text(_make_sample(sample_rows))

    artifact_dir = tmp_path / "runs"
    artifact_dir.mkdir()

    for h, _, _ in sample_rows[:5]:
        art = _make_artifact("b", h, 1, ["sir-albert:brainstorm"])
        (artifact_dir / f"b-{h}-rep1.json").write_text(json.dumps(art))

    for h, _, _ in sample_rows[5:10]:
        art = _make_artifact("b", h, 1, ["sir-albert:brainstorm"])
        (artifact_dir / f"b-{h}-rep1.json").write_text(json.dumps(art))

    # One control row fires a skill — should cause DEV FAIL
    for i, (h, _, _) in enumerate(sample_rows[10:]):
        if i == 0:
            art = _make_artifact("b", h, 1, ["sir-albert:brainstorm"],
                                 final_text="wrongly fired on control")
        else:
            art = _make_artifact("b", h, 1, [])
        (artifact_dir / f"b-{h}-rep1.json").write_text(json.dumps(art))

    old_env = os.environ.copy()
    os.environ["W4_SAMPLE_FILE"] = str(sample_file)
    try:
        rc = _mod.main([str(DEV_REPORT), str(artifact_dir)])
    finally:
        os.environ.clear()
        os.environ.update(old_env)

    captured = capsys.readouterr()
    assert rc == 1, f"expected DEV FAIL (rc=1), got rc={rc}"
    assert "DEV FAIL" in captured.out

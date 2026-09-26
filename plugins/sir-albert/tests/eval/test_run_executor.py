"""Tests for run_one.sh — ticket 07.

Key fixture tests:
- Parser against real probe stream (arm-b.jsonl): asserts cost_usd == 0.140838 and turn_count == 1
- Parser with synthetic Skill tool_use: asserts skills_called == ['sir-albert:plan']
"""
import json
import os
import subprocess
from pathlib import Path

import pytest

TESTS_EVAL = Path(__file__).parent
FIXTURES_DIR = TESTS_EVAL / "fixtures"
TOOLS_EVAL = TESTS_EVAL.parent.parent / "tools" / "eval"
RUN_ONE_SH = TOOLS_EVAL / "run_one.sh"

EXPECTED_MODEL = "claude-opus-5-5[1m]"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_manifest(tmp_path, clone=None, scratch=None, arm_a=None, arm_b=None):
    clone = clone or tmp_path / "clone"
    scratch = scratch or tmp_path / "scratch"
    arm_a = arm_a or tmp_path / "arm-a.json"
    arm_b = arm_b or tmp_path / "arm-b.json"
    for d in (clone, scratch):
        d.mkdir(exist_ok=True)
    fake_settings = {"model": EXPECTED_MODEL, "hooks": {}, "enabledPlugins": {}}
    for f in (arm_a, arm_b):
        if not f.exists():
            f.write_text(json.dumps(fake_settings))
    manifest = {
        "pin_sha": "abc123",
        "clone_path": str(clone),
        "arm_a_settings": str(arm_a),
        "arm_b_settings": str(arm_b),
        "scratch_cwd": str(scratch),
        "rundir": str(tmp_path),
    }
    mf = tmp_path / "run-manifest.json"
    mf.write_text(json.dumps(manifest, indent=2))
    snap = tmp_path / "model-snapshot.txt"
    snap.write_text(EXPECTED_MODEL)
    return tmp_path


def _run_stub(stub_stream_path, arm, prompt_hash, rep, prompt_text, rundir, artifact_dir, stub_exit=0):
    """Run run_one.sh with a stub that emits a pre-canned stream.

    The stub behaves like the real CLI where it matters: it rejects --cwd (not a
    claude flag) and requires being run from the manifest's scratch_cwd.
    """
    scratch = json.loads((rundir / "run-manifest.json").read_text())["scratch_cwd"]
    stub = rundir / "stub_claude.sh"
    stub.write_text(
        "#!/bin/bash\n"
        'for a in "$@"; do [ "$a" = "--cwd" ] && { echo "stub: --cwd is not a claude flag" >&2; exit 2; }; done\n'
        f'[ "$(pwd -P)" = "$(cd {scratch!r} && pwd -P)" ] || {{ echo "stub: wrong cwd $(pwd)" >&2; exit 3; }}\n'
        f"cat {str(stub_stream_path)!r}\n"
        f"exit {stub_exit}\n"
    )
    stub.chmod(0o755)

    # Fake settings file for guarded.sh (needs a valid JSON with 'model' key)
    fake_settings = rundir / "guard-settings.json"
    if not fake_settings.exists():
        fake_settings.write_text(json.dumps({"model": EXPECTED_MODEL, "hooks": {}}))

    env = os.environ.copy()
    env["W4_CLAUDE_BIN"] = str(stub)
    env["W4_SETTINGS_FILE"] = str(fake_settings)  # for guard
    env["W4_ARTIFACT_DIR"] = str(artifact_dir)

    result = subprocess.run(
        ["bash", str(RUN_ONE_SH), arm, prompt_hash, str(rep), prompt_text, str(rundir)],
        capture_output=True,
        text=True,
        env=env,
    )
    return result


# ── Tests against real probe fixture ──────────────────────────────────────────

def test_parser_against_real_probe_arm_b(tmp_path):
    """Parser against real arm-b probe stream: cost_usd and turn_count must match."""
    fixture = FIXTURES_DIR / "arm-b.jsonl"
    if not fixture.exists():
        pytest.skip("arm-b.jsonl fixture not found")

    rundir = _make_manifest(tmp_path)
    art_dir = tmp_path / "runs"
    art_dir.mkdir()
    result = _run_stub(fixture, "b", "abc123", 1, "write handoff", rundir, art_dir)
    assert result.returncode == 0, f"run_one.sh failed:\n{result.stderr}\n{result.stdout}"

    artifact = json.loads((art_dir / "b-abc123-rep1.json").read_text())
    assert abs(artifact["cost_usd"] - 0.140838) < 1e-5, f"cost_usd mismatch: {artifact['cost_usd']}"
    assert artifact["turn_count"] == 1
    assert artifact["result_subtype"] == "success"


def test_parser_skills_called_from_tool_use(tmp_path):
    """Parser extracts skills_called from Skill tool_use events."""
    # 30 skill slugs: needs to be strings/dicts so parser handles them
    fake_skills = [f"sir-albert:skill{i}" for i in range(30)]
    skill_stream = [
        {"type": "system", "subtype": "init", "model": EXPECTED_MODEL, "skills": fake_skills, "plugins": []},
        {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "tool_use", "name": "Skill", "input": {"skill": "sir-albert:plan"}},
                ]
            }
        },
        {"type": "result", "subtype": "success", "total_cost_usd": 0.05, "num_turns": 2, "is_error": False, "result": "done"},
    ]
    stream_file = tmp_path / "skill_stream.jsonl"
    stream_file.write_text("\n".join(json.dumps(e) for e in skill_stream))

    rundir = _make_manifest(tmp_path)
    art_dir = tmp_path / "runs"
    art_dir.mkdir()
    result = _run_stub(stream_file, "b", "def456", 1, "plan my project", rundir, art_dir)
    assert result.returncode == 0, f"run_one.sh failed:\n{result.stderr}"

    artifact = json.loads((art_dir / "b-def456-rep1.json").read_text())
    assert artifact["skills_called"] == ["sir-albert:plan"]
    # skills_loaded has 30 entries (0..29)
    assert len(artifact["skills_loaded"]) == 30


def test_artifact_has_required_keys(tmp_path):
    fixture = FIXTURES_DIR / "arm-b.jsonl"
    if not fixture.exists():
        pytest.skip("arm-b.jsonl fixture not found")

    rundir = _make_manifest(tmp_path)
    art_dir = tmp_path / "runs"
    art_dir.mkdir()
    _run_stub(fixture, "a", "key123", 2, "some prompt", rundir, art_dir)

    artifact = json.loads((art_dir / "a-key123-rep2.json").read_text())
    required_keys = [
        "arm", "prompt_hash", "rep", "prompt_text", "model",
        "exit_code", "timestamp_utc", "cost_usd", "turn_count",
        "budget_capped", "result_subtype", "skills_loaded", "skills_called",
        "init_event", "result_event",
    ]
    for k in required_keys:
        assert k in artifact, f"missing key: {k}"


def test_idempotency_guard(tmp_path):
    """run_one.sh exits 1 if artifact already exists."""
    fixture = FIXTURES_DIR / "arm-b.jsonl"
    if not fixture.exists():
        pytest.skip("arm-b.jsonl fixture not found")

    rundir = _make_manifest(tmp_path)
    art_dir = tmp_path / "runs"
    art_dir.mkdir()

    # First run
    _run_stub(fixture, "b", "idem1", 1, "test", rundir, art_dir)
    # Second run — must fail
    result = _run_stub(fixture, "b", "idem1", 1, "test", rundir, art_dir)
    assert result.returncode == 1
    assert "already exists" in result.stdout + result.stderr


def test_no_backgrounding_in_run_one():
    """run_one.sh must not use & to background any command."""
    content = RUN_ONE_SH.read_text()
    # Exclude comments; check no line ends with & (background)
    suspicious = [
        line for line in content.splitlines()
        if line.strip() and not line.strip().startswith("#") and line.rstrip().endswith(" &")
    ]
    assert not suspicious, f"Found backgrounded commands in run_one.sh: {suspicious}"


def test_nonzero_claude_exit_still_writes_artifact(tmp_path):
    """A budget-capped or failed run exits non-zero. It must still leave exactly one
    artifact recording the exit code; otherwise the 60-run audit ABORTs the verdict."""
    rundir = _make_manifest(tmp_path)
    art_dir = tmp_path / "runs"
    art_dir.mkdir()
    result = _run_stub(FIXTURES_DIR / "arm-b.jsonl", "b", "capped1", 1, "p", rundir, art_dir, stub_exit=1)
    artifact = json.loads((art_dir / "b-capped1-rep1.json").read_text())
    assert artifact["exit_code"] == 1, result.stderr
    assert artifact["cost_usd"] == pytest.approx(0.140838)

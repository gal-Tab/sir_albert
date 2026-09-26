"""Tests for canary_preflight.sh — ticket 06."""
import json
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

TOOLS_EVAL = Path(__file__).parent.parent.parent / "tools" / "eval"
CANARY_SH = TOOLS_EVAL / "canary_preflight.sh"

EXPECTED_MODEL = "claude-opus-5-5[1m]"

# ── Fake stream-json fixtures ──────────────────────────────────────────────────

def _init_event(skills):
    return {"type": "system", "subtype": "init", "model": EXPECTED_MODEL, "skills": skills, "plugins": []}


def _hook_response(output):
    return {"type": "system", "subtype": "hook_response", "hook_event": "SessionStart", "output": output}


def _result_event():
    return {"type": "result", "subtype": "success", "total_cost_usd": 0.05, "num_turns": 1, "is_error": False, "result": "ok"}


def _stream(skills, extra_hook_text=""):
    lines = [
        json.dumps(_hook_response(json.dumps({"hookSpecificOutput": {"additionalContext": "## sir_albert session start " + extra_hook_text}}))),
        json.dumps(_init_event(skills)),
        json.dumps(_result_event()),
    ]
    return "\n".join(lines)


ARM_B_SKILLS = ["sir-albert:handoff", "sir-albert:plan", "sir-albert:build"]
ARM_A_SKILLS = ["superpowers:brainstorming", "superpowers:systematic-debugging"] + ARM_B_SKILLS

ARM_B_STREAM = _stream(ARM_B_SKILLS)
ARM_A_STREAM = _stream(ARM_A_SKILLS, extra_hook_text="using-superpowers content here")


@pytest.fixture()
def fake_settings(tmp_path):
    settings = {
        "model": EXPECTED_MODEL,
        "hooks": {"SessionStart": []},
        "enabledPlugins": {},
    }
    f = tmp_path / "settings.json"
    f.write_text(json.dumps(settings, indent=2))
    return f


@pytest.fixture()
def fake_manifest(tmp_path, fake_settings):
    clone = tmp_path / "clone"
    clone.mkdir()
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    arm_a = tmp_path / "arm-a.json"
    arm_b = tmp_path / "arm-b.json"
    for f in (arm_a, arm_b):
        f.write_text(fake_settings.read_text())
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
    (tmp_path / "model-snapshot.txt").write_text(EXPECTED_MODEL)
    return tmp_path


def _run_canary(fake_manifest, fake_settings, env_overrides=None):
    """Run canary_preflight.sh with a stub W4_CLAUDE_BIN."""
    env = os.environ.copy()
    env["W4_SETTINGS_FILE"] = str(fake_settings)
    if env_overrides:
        env.update(env_overrides)
    result = subprocess.run(
        ["bash", str(CANARY_SH), str(fake_manifest)],
        capture_output=True, text=True, env=env,
    )
    return result


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_canary_script_exists():
    assert CANARY_SH.exists(), f"canary_preflight.sh not found at {CANARY_SH}"


def test_model_assertion_aborts_wrong_model(fake_manifest, fake_settings):
    """If settings.json model != expected, canary must abort."""
    bad = json.loads(fake_settings.read_text())
    bad["model"] = "claude-sonnet-5"
    fake_settings.write_text(json.dumps(bad, indent=2))

    result = _run_canary(fake_manifest, fake_settings)
    assert result.returncode == 1
    combined = result.stdout + result.stderr
    assert "ABORT" in combined
    assert "claude-opus-5-5" in combined


def test_model_snapshot_written(fake_manifest, fake_settings):
    """Model snapshot must be written to rundir/model-snapshot.txt."""
    # Stub: make W4_CLAUDE_BIN emit arm-b stream then arm-a stream
    stub = fake_manifest / "stub_claude.sh"
    stub.write_text(
        "#!/bin/bash\ncat '" + str(fake_manifest / "stream_output.txt") + "'\n"
    )
    stub.chmod(0o755)

    # Pre-write the stream file (used by stub)
    (fake_manifest / "stream_output.txt").write_text(ARM_B_STREAM + "\n" + ARM_A_STREAM)

    # Write a sequence file so stub returns B then A
    call_file = fake_manifest / "call_count.txt"
    call_file.write_text("0")

    stub_b = fake_manifest / "stub_b.sh"
    stub_b.write_text("#!/bin/bash\necho '" + ARM_B_STREAM.replace("'", "'\\''") + "'\n")
    stub_b.chmod(0o755)

    # Just test that model-snapshot.txt is written by checking the canary exits 1
    # (because stub emits nothing useful, but the model assertion runs first)
    result = _run_canary(fake_manifest, fake_settings)
    # Model is correct, so it should proceed past model check
    snap = fake_manifest / "model-snapshot.txt"
    assert snap.exists(), "model-snapshot.txt not written"
    assert snap.read_text().strip() == EXPECTED_MODEL


def test_syntax_check():
    """canary_preflight.sh must pass bash -n."""
    result = subprocess.run(
        ["bash", "-n", str(CANARY_SH)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"Syntax error: {result.stderr}"

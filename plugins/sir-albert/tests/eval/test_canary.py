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
    env["W4_TEST_MODEL"] = EXPECTED_MODEL   # the probe fixtures were recorded on this model
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


FIXTURES = Path(__file__).parent / "fixtures"


def _sequenced_stub(rundir, first, second):
    """A fake claude that emits `first` on call 1 and `second` on call 2.

    It fails if passed --cwd (not a real claude flag) or if not run from the
    manifest's scratch_cwd, since the real harness must cd there instead.
    """
    scratch = json.loads((rundir / "run-manifest.json").read_text())["scratch_cwd"]
    counter = rundir / "stub-calls.txt"
    counter.write_text("0")
    stub = rundir / "stub_claude.sh"
    stub.write_text(
        "#!/bin/bash\n"
        'for a in "$@"; do [ "$a" = "--cwd" ] && { echo "stub: --cwd is not a claude flag" >&2; exit 2; }; done\n'
        f'[ "$(pwd -P)" = "$(cd {scratch!r} && pwd -P)" ] || {{ echo "stub: wrong cwd $(pwd)" >&2; exit 3; }}\n'
        '[ "$(cat)" = "write handoff" ] || { echo "stub: prompt not on stdin" >&2; exit 6; }\n'
        f"n=$(( $(cat {str(counter)!r}) + 1 )); echo $n > {str(counter)!r}\n"
        f'if [ $n -eq 1 ]; then cat {str(first)!r}; else cat {str(second)!r}; fi\n'
    )
    stub.chmod(0o755)
    return stub


def test_model_snapshot_written(fake_manifest, fake_settings):
    """Model snapshot must be written to rundir/model-snapshot.txt."""
    stub = _sequenced_stub(fake_manifest, FIXTURES / "arm-b.jsonl", FIXTURES / "arm-a2.jsonl")
    _run_canary(fake_manifest, fake_settings, {"W4_CLAUDE_BIN": str(stub)})
    snap = fake_manifest / "model-snapshot.txt"
    assert snap.exists(), "model-snapshot.txt not written"
    assert snap.read_text().strip() == EXPECTED_MODEL


def test_canary_passes_on_real_probe_streams(fake_manifest, fake_settings):
    """The real probe output must pass. Its hook lines carry JSON '\\n' escapes, which
    broke an earlier parser that interpolated the stream into a Python string."""
    stub = _sequenced_stub(fake_manifest, FIXTURES / "arm-b.jsonl", FIXTURES / "arm-a2.jsonl")
    result = _run_canary(fake_manifest, fake_settings, {"W4_CLAUDE_BIN": str(stub)})
    out = result.stdout + result.stderr
    assert result.returncode == 0, out
    assert "Canary B PASS: 0 superpowers" in out
    assert "Canary A PASS" in out
    assert (fake_manifest / "stub-calls.txt").read_text().strip() == "2"


def test_canary_aborts_when_arm_a_lacks_superpowers(fake_manifest, fake_settings):
    stub = _sequenced_stub(fake_manifest, FIXTURES / "arm-b.jsonl", FIXTURES / "arm-b.jsonl")
    result = _run_canary(fake_manifest, fake_settings, {"W4_CLAUDE_BIN": str(stub)})
    assert result.returncode != 0
    assert "ABORT: arm A" in result.stdout + result.stderr


def test_canary_aborts_when_arm_b_has_superpowers(fake_manifest, fake_settings):
    stub = _sequenced_stub(fake_manifest, FIXTURES / "arm-a2.jsonl", FIXTURES / "arm-a2.jsonl")
    result = _run_canary(fake_manifest, fake_settings, {"W4_CLAUDE_BIN": str(stub)})
    assert result.returncode != 0
    assert "ABORT: arm B" in result.stdout + result.stderr
    assert (fake_manifest / "stub-calls.txt").read_text().strip() == "1", "must stop before arm A"


def test_canary_aborts_when_router_injection_missing(fake_manifest, fake_settings, tmp_path):
    """Arm B with its SessionStart hook dead is the documented failure mode."""
    dead = tmp_path / "arm-b-dead-router.jsonl"
    lines = [l for l in (FIXTURES / "arm-b.jsonl").read_text().splitlines() if "## sir_albert" not in l]
    dead.write_text("\n".join(lines) + "\n")
    stub = _sequenced_stub(fake_manifest, dead, FIXTURES / "arm-a2.jsonl")
    result = _run_canary(fake_manifest, fake_settings, {"W4_CLAUDE_BIN": str(stub)})
    assert result.returncode != 0
    assert "SessionStart injection missing" in result.stdout + result.stderr


def test_syntax_check():
    """canary_preflight.sh must pass bash -n."""
    result = subprocess.run(
        ["bash", "-n", str(CANARY_SH)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, f"Syntax error: {result.stderr}"


def test_canary_aborts_when_arms_run_on_wrong_model(fake_manifest, fake_settings):
    """The init event's model must be the model under test, not whatever the CLI picked."""
    stub = _sequenced_stub(fake_manifest, FIXTURES / "arm-b.jsonl", FIXTURES / "arm-a2.jsonl")
    result = _run_canary(fake_manifest, fake_settings,
                         {"W4_CLAUDE_BIN": str(stub), "W4_TEST_MODEL": "claude-sonnet-5"})
    assert result.returncode != 0
    assert "expected 'claude-sonnet-5'" in result.stdout + result.stderr

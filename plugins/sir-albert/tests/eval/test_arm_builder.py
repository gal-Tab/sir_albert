"""Tests for build_arms.sh — ticket 05."""
import json
import os
import subprocess
from pathlib import Path

import pytest

TOOLS_EVAL = Path(__file__).parent.parent.parent / "tools" / "eval"
BUILD_ARMS_SH = TOOLS_EVAL / "build_arms.sh"


@pytest.fixture()
def fake_settings(tmp_path):
    """Create a fake settings.json with enabledPlugins and hooks."""
    settings = {
        "model": "claude-opus-5-5[1m]",
        "enabledPlugins": {
            "superpowers@claude-plugins-official": True,
            "other-plugin@v1": True,
        },
        "hooks": {
            "SessionStart": [{"matcher": "", "hooks": [{"type": "command", "command": "guard.sh"}]}]
        },
        "env": {"ANTHROPIC_BASE_URL": "https://example.com"},
    }
    f = tmp_path / "settings.json"
    f.write_text(json.dumps(settings, indent=2))
    return f


@pytest.fixture()
def fake_repo(tmp_path):
    """Create a minimal git repo to act as the source repo."""
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "--allow-empty", "-m", "init", "-q"],
        check=True,
    )
    return repo


def run_build_arms(fake_settings, fake_repo, tmp_path, extra_env=None):
    """Run build_arms.sh with test overrides."""
    rundir = tmp_path / "rundir"
    rundir.mkdir()
    clone_path = tmp_path / "clone"
    scratch_cwd = tmp_path / "scratch"

    env = os.environ.copy()
    env["W4_REPO"] = str(fake_repo)
    env["W4_SETTINGS_FILE"] = str(fake_settings)
    env["W4_RUNDIR"] = str(rundir)
    env["W4_CLONE_PATH"] = str(clone_path)
    env["W4_SCRATCH_CWD"] = str(scratch_cwd)
    if extra_env:
        env.update(extra_env)

    result = subprocess.run(
        ["bash", str(BUILD_ARMS_SH)],
        capture_output=True,
        text=True,
        env=env,
    )
    return result, rundir, clone_path, scratch_cwd


def test_arm_a_superpowers_true(fake_settings, fake_repo, tmp_path):
    result, rundir, _, _ = run_build_arms(fake_settings, fake_repo, tmp_path)
    assert result.returncode == 0, f"build_arms.sh failed:\n{result.stderr}"

    arm_a = json.loads((rundir / "arm-a-settings.json").read_text())
    assert arm_a["enabledPlugins"]["superpowers@claude-plugins-official"] is True


def test_arm_b_superpowers_false(fake_settings, fake_repo, tmp_path):
    result, rundir, _, _ = run_build_arms(fake_settings, fake_repo, tmp_path)
    assert result.returncode == 0, f"build_arms.sh failed:\n{result.stderr}"

    arm_b = json.loads((rundir / "arm-b-settings.json").read_text())
    assert arm_b["enabledPlugins"]["superpowers@claude-plugins-official"] is False


def test_hooks_preserved(fake_settings, fake_repo, tmp_path):
    result, rundir, _, _ = run_build_arms(fake_settings, fake_repo, tmp_path)
    assert result.returncode == 0, f"build_arms.sh failed:\n{result.stderr}"

    arm_a = json.loads((rundir / "arm-a-settings.json").read_text())
    arm_b = json.loads((rundir / "arm-b-settings.json").read_text())
    assert arm_a.get("hooks") is not None, "hooks missing from arm A"
    assert arm_b.get("hooks") is not None, "hooks missing from arm B"


def test_arms_identical_except_superpowers(fake_settings, fake_repo, tmp_path):
    result, rundir, _, _ = run_build_arms(fake_settings, fake_repo, tmp_path)
    assert result.returncode == 0, f"build_arms.sh failed:\n{result.stderr}"

    arm_a = json.loads((rundir / "arm-a-settings.json").read_text())
    arm_b = json.loads((rundir / "arm-b-settings.json").read_text())

    # Force same superpowers value and compare
    arm_a_copy = json.loads(json.dumps(arm_a))
    arm_b_copy = json.loads(json.dumps(arm_b))
    arm_a_copy["enabledPlugins"]["superpowers@claude-plugins-official"] = None
    arm_b_copy["enabledPlugins"]["superpowers@claude-plugins-official"] = None
    assert arm_a_copy == arm_b_copy, "Arms differ beyond superpowers key"


def test_manifest_keys(fake_settings, fake_repo, tmp_path):
    result, rundir, clone_path, scratch_cwd = run_build_arms(
        fake_settings, fake_repo, tmp_path
    )
    assert result.returncode == 0, f"build_arms.sh failed:\n{result.stderr}"

    manifest = json.loads((rundir / "run-manifest.json").read_text())
    for key in ("pin_sha", "clone_path", "arm_a_settings", "arm_b_settings", "scratch_cwd", "rundir"):
        assert key in manifest, f"missing key: {key}"
    assert manifest["scratch_cwd"] == str(scratch_cwd)
    assert manifest["clone_path"] == str(clone_path)


def test_clone_is_directory_not_worktree(fake_settings, fake_repo, tmp_path):
    result, rundir, clone_path, _ = run_build_arms(fake_settings, fake_repo, tmp_path)
    assert result.returncode == 0, f"build_arms.sh failed:\n{result.stderr}"

    dot_git = clone_path / ".git"
    assert dot_git.is_dir(), f".git is not a directory: {dot_git}"


def test_scratch_cwd_is_git_repo_with_commit(fake_settings, fake_repo, tmp_path):
    result, rundir, _, scratch_cwd = run_build_arms(fake_settings, fake_repo, tmp_path)
    assert result.returncode == 0, f"build_arms.sh failed:\n{result.stderr}"

    log = subprocess.run(
        ["git", "-C", str(scratch_cwd), "log", "--oneline"],
        capture_output=True, text=True,
    )
    assert log.returncode == 0
    assert len(log.stdout.strip().splitlines()) >= 1, "scratch cwd has no commits"


def test_guarded_sh_exists():
    guarded = TOOLS_EVAL / "guarded.sh"
    assert guarded.exists(), "guarded.sh not found"
    assert os.access(guarded, os.X_OK), "guarded.sh not executable"


def test_arm_s_settings(fake_settings, fake_repo, tmp_path):
    """build_arms.sh must write arm-s-settings.json (superpowers=true) and include
    arm_s_settings key in run-manifest.json."""
    result, rundir, _, _ = run_build_arms(fake_settings, fake_repo, tmp_path)
    assert result.returncode == 0, f"build_arms.sh failed:\n{result.stderr}"

    arm_s_path = rundir / "arm-s-settings.json"
    assert arm_s_path.exists(), "arm-s-settings.json not written"

    arm_s = json.loads(arm_s_path.read_text())
    assert arm_s["enabledPlugins"]["superpowers@claude-plugins-official"] is True, \
        "arm S must have superpowers=true"

    manifest = json.loads((rundir / "run-manifest.json").read_text())
    assert "arm_s_settings" in manifest, "manifest missing arm_s_settings key"
    assert manifest["arm_s_settings"] == str(arm_s_path), \
        f"arm_s_settings path mismatch: {manifest['arm_s_settings']!r}"

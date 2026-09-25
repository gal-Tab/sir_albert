"""Tests for prompt_router.py hook."""
import json
import subprocess
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).parent.parent
HOOK = PLUGIN_ROOT / "hooks" / "prompt_router.py"


def _run(prompt: str):
    import os
    env = {
        "PATH": os.environ.get("PATH", ""),
        "CLAUDE_PLUGIN_ROOT": str(PLUGIN_ROOT),
    }
    return subprocess.run(
        ["python3", str(HOOK)],
        input=json.dumps({"prompt": prompt}),
        capture_output=True,
        text=True,
        env=env,
    )


def _nudge(prompt: str) -> str:
    result = _run(prompt)
    assert result.returncode == 0, f"stderr: {result.stderr}"
    return result.stdout.strip()


class TestMatches:
    def test_brainstorm_explore(self):
        assert "/sir-albert:brainstorm" in _nudge("let's brainstorm this problem")

    def test_brainstorm_think_through(self):
        assert "/sir-albert:brainstorm" in _nudge("help me think through this")

    def test_attack_mode(self):
        assert "attack" in _nudge("attack my plan")

    def test_devils_advocate(self):
        assert "attack" in _nudge("play devil's advocate here")

    def test_grill(self):
        assert "grill" in _nudge("grill me on the spec")

    def test_zoom_out(self):
        assert "zoom-out" in _nudge("let's zoom out from this")

    def test_bigger_picture(self):
        assert "zoom-out" in _nudge("what's the bigger picture here")

    def test_design(self):
        assert "design" in _nudge("let's design this system")

    def test_plan(self):
        assert "/sir-albert:plan" in _nudge("make a plan for this")

    def test_execute(self):
        assert "/sir-albert:execute" in _nudge("implement the plan now")

    def test_debug(self):
        assert "/sir-albert:debug" in _nudge("help me debug why this is broken")

    def test_build(self):
        assert "/sir-albert:build" in _nudge("let's ship this feature")

    def test_handoff(self):
        assert "/sir-albert:handoff" in _nudge("write a handoff for this session")

    def test_resume(self):
        assert "/sir-albert:resume" in _nudge("where were we")


class TestNoMatch:
    """False-positive phrases — must all produce empty stdout."""

    def test_execute_sql(self):
        assert _nudge("execute this SQL") == ""

    def test_publish_gtm(self):
        assert _nudge("publish the GTM container") == ""

    def test_challenge_accepted(self):
        assert _nudge("challenge accepted") == ""

    def test_feeling_broken(self):
        assert _nudge("I'm feeling broken today") == ""

    def test_architect_building(self):
        assert _nudge("architect of the building") == ""

    def test_what_time(self):
        assert _nudge("what time is it") == ""

    def test_show_diff(self):
        assert _nudge("show me the diff") == ""

    def test_git_status(self):
        assert _nudge("git status") == ""

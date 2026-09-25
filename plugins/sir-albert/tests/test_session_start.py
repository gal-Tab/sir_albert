"""Tests for session_start.py hook."""
import json
import subprocess
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).parent.parent
HOOK = PLUGIN_ROOT / "hooks" / "session_start.py"


def _run(cwd: Path, plugin_root: Path = PLUGIN_ROOT, env_extra: dict = None):
    import os
    env = {
        "PATH": os.environ.get("PATH", ""),
        "CLAUDE_PLUGIN_ROOT": str(plugin_root),
        "PWD": str(cwd),
    }
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        ["python3", str(HOOK)],
        capture_output=True,
        text=True,
        env=env,
    )


def _parse_context(result) -> str:
    assert result.returncode == 0, f"stderr: {result.stderr}"
    d = json.loads(result.stdout)
    return d["hookSpecificOutput"]["additionalContext"]


class TestPackDetection:
    def test_gtm_pack(self, tmp_project_gtm):
        ctx = _parse_context(_run(tmp_project_gtm))
        assert "gtm" in ctx

    def test_n8n_pack(self, tmp_project_n8n):
        ctx = _parse_context(_run(tmp_project_n8n))
        assert "n8n" in ctx

    def test_kb_pack(self, tmp_project_kb):
        ctx = _parse_context(_run(tmp_project_kb))
        assert "kb" in ctx

    def test_plain_no_pack(self, tmp_project_plain):
        ctx = _parse_context(_run(tmp_project_plain))
        assert "(none detected)" in ctx


class TestCharCount:
    def test_within_800_chars(self, tmp_project_gtm):
        ctx = _parse_context(_run(tmp_project_gtm))
        assert len(ctx) <= 800, f"Injection too long: {len(ctx)} chars"

    def test_plain_within_800_chars(self, tmp_project_plain):
        ctx = _parse_context(_run(tmp_project_plain))
        assert len(ctx) <= 800, f"Injection too long: {len(ctx)} chars"


class TestResumeHint:
    def test_resume_hint_present(self, tmp_project_plain):
        mem = tmp_project_plain / ".memory-bank"
        mem.mkdir()
        (mem / "HANDOFF-2026-09-24.md").write_text("handoff")
        ctx = _parse_context(_run(tmp_project_plain))
        assert "HANDOFF-2026-09-24.md" in ctx

    def test_resume_hint_suppressed(self, tmp_project_plain):
        mem = tmp_project_plain / ".memory-bank"
        mem.mkdir()
        (mem / "HANDOFF-2026-09-24.md").write_text("handoff")
        ctx = _parse_context(_run(tmp_project_plain, env_extra={"DISABLE_RESUME_HINT": "1"}))
        assert "HANDOFF" not in ctx

    def test_no_hint_when_no_handoff(self, tmp_project_plain):
        ctx = _parse_context(_run(tmp_project_plain))
        assert "HANDOFF" not in ctx


class TestOutputFormat:
    def test_valid_json(self, tmp_project_plain):
        result = _run(tmp_project_plain)
        assert result.returncode == 0
        d = json.loads(result.stdout)
        assert "hookSpecificOutput" in d
        assert d["hookSpecificOutput"]["hookEventName"] == "SessionStart"
        assert "additionalContext" in d["hookSpecificOutput"]

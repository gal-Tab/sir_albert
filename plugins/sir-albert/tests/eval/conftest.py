"""Isolation for every W4 eval test.

A test that reaches the real `claude` binary makes real API calls, and axcli
rewrites ~/.claude/settings.json "model" on every spawn. test_canary once did
both silently, because the guard was pointed at a fake settings file while the
real one drifted to claude-sonnet-5. These fixtures make that impossible:

- W4_CLAUDE_BIN defaults to a tripwire that fails loudly. Tests that need a
  claude binary must install their own stub.
- W4_SETTINGS_FILE defaults to a throwaway copy, never the real file.
- The session fails if the real settings file changed during the run.
"""
import os
from pathlib import Path

import pytest

REAL_SETTINGS = Path.home() / ".claude" / "settings.json"


@pytest.fixture(autouse=True)
def _isolate_claude(tmp_path, monkeypatch):
    tripwire = tmp_path / "claude_tripwire.sh"
    tripwire.write_text(
        "#!/bin/bash\n"
        "echo 'TRIPWIRE: a test tried to spawn the real claude binary' >&2\n"
        "exit 97\n"
    )
    tripwire.chmod(0o755)
    monkeypatch.setenv("W4_CLAUDE_BIN", str(tripwire))

    settings = tmp_path / "isolated-settings.json"
    settings.write_text('{"model": "claude-opus-5-5[1m]", "enabledPlugins": {}, "hooks": {}}\n')
    monkeypatch.setenv("W4_SETTINGS_FILE", str(settings))


@pytest.fixture(autouse=True, scope="session")
def _real_settings_untouched():
    before = REAL_SETTINGS.stat().st_mtime_ns if REAL_SETTINGS.exists() else None
    yield
    after = REAL_SETTINGS.stat().st_mtime_ns if REAL_SETTINGS.exists() else None
    assert before == after, f"{REAL_SETTINGS} was modified during the eval test run"

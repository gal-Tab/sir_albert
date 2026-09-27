"""Tests for guarded.sh under parallel runs."""
import json
import os
import subprocess
from pathlib import Path

GUARD = Path(__file__).parent.parent.parent / "tools" / "eval" / "guarded.sh"
OPUS, SONNET = "claude-opus-5-5[1m]", "claude-sonnet-5"


def _settings(tmp_path, model):
    f = tmp_path / "settings.json"
    f.write_text(json.dumps({"model": model, "hooks": {"PreToolUse": ["guard"]}, "env": {"X": "1"}}, indent=2))
    return f


def _drifter(tmp_path, settings, sleep="0"):
    """A fake spawn that does what axcli does: rewrite the model to sonnet."""
    stub = tmp_path / "drift.sh"
    stub.write_text(
        "#!/bin/bash\n"
        f"/usr/local/bin/python3.13 -c \"import json,re,sys; p=sys.argv[1]; s=open(p).read(); "
        f"open(p,'w').write(re.sub(r'\\\"model\\\": \\\"[^\\\"]*\\\"', '\\\"model\\\": \\\"{SONNET}\\\"', s))\" {str(settings)!r}\n"
        f"sleep {sleep}\n"
    )
    stub.chmod(0o755)
    return stub


def _guard(settings, cmd, restore_model=None):
    env = dict(os.environ, W4_SETTINGS_FILE=str(settings))
    if restore_model:
        env["W4_RESTORE_MODEL"] = restore_model
    return subprocess.Popen(["bash", str(GUARD), str(cmd)], env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def test_restores_snapshot_by_default(tmp_path):
    s = _settings(tmp_path, OPUS)
    p = _guard(s, _drifter(tmp_path, s))
    p.communicate()
    assert json.loads(s.read_text())["model"] == OPUS


def test_fixed_target_beats_a_drifted_snapshot(tmp_path):
    """Parallel case: another run already drifted the file when this guard starts.
    Snapshot mode would 'restore' sonnet; W4_RESTORE_MODEL must win."""
    s = _settings(tmp_path, SONNET)
    p = _guard(s, _drifter(tmp_path, s), restore_model=OPUS)
    p.communicate()
    assert json.loads(s.read_text())["model"] == OPUS


def test_concurrent_guards_leave_valid_settings_with_other_keys_intact(tmp_path):
    s = _settings(tmp_path, OPUS)
    procs = [_guard(s, _drifter(tmp_path, s, sleep=f"0.{i}"), restore_model=OPUS) for i in range(8)]
    for p in procs:
        p.communicate()
    final = json.loads(s.read_text())
    assert final["model"] == OPUS
    assert final["hooks"] == {"PreToolUse": ["guard"]} and final["env"] == {"X": "1"}
    assert not list(tmp_path.glob(".settings-w4-*")), "temp files must be renamed into place, not left behind"

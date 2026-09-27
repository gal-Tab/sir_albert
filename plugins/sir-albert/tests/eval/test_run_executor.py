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


def _run_stub(stub_stream_path, arm, prompt_hash, rep, prompt_text, rundir, artifact_dir, stub_exit=0, stub_extra=":"):
    """Run run_one.sh with a stub that emits a pre-canned stream.

    The stub behaves like the real CLI where it matters: it rejects --cwd (not a
    claude flag) and requires being run from the manifest's scratch_cwd.
    """
    scratch = json.loads((rundir / "run-manifest.json").read_text())["scratch_cwd"]
    stub = rundir / "stub_claude.sh"
    stub.write_text(
        "#!/bin/bash\n"
        'for a in "$@"; do [ "$a" = "--cwd" ] && { echo "stub: --cwd is not a claude flag" >&2; exit 2; }; done\n'
        f'case "$(pwd -P)/" in "$(cd {scratch!r} && pwd -P)"/run-*) ;; *) echo "stub: wrong cwd $(pwd)" >&2; exit 3;; esac\n'
        'IN=$(cat); [ -n "$IN" ] || { echo "stub: no prompt on stdin" >&2; exit 6; }\n'
        f"{stub_extra}\n"
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


def test_each_run_gets_a_fresh_scratch_repo(tmp_path):
    """A file a run creates (Bash `cat > plan.md`) must not be visible to the next run."""
    rundir = _make_manifest(tmp_path)
    art_dir = tmp_path / "runs"
    art_dir.mkdir()
    leak_check = 'if [ -e plan.md ]; then echo "stub: saw previous run\'s file" >&2; exit 5; fi; echo x > plan.md'
    r1 = _run_stub(FIXTURES_DIR / "arm-b.jsonl", "a", "fresh1", 1, "p", rundir, art_dir, stub_extra=leak_check)
    r2 = _run_stub(FIXTURES_DIR / "arm-b.jsonl", "b", "fresh1", 1, "p", rundir, art_dir, stub_extra=leak_check)
    assert json.loads((art_dir / "a-fresh1-rep1.json").read_text())["exit_code"] == 0, r1.stderr
    assert json.loads((art_dir / "b-fresh1-rep1.json").read_text())["exit_code"] == 0, r2.stderr


def test_modified_plugin_clone_aborts(tmp_path):
    """If a run edits the plugin clone, the treatment changed: abort (exit 4)."""
    import subprocess as sp
    clone = tmp_path / "clone"
    clone.mkdir()
    sp.run(["git", "init", "-q", str(clone)], check=True)
    sp.run(["git", "-C", str(clone), "commit", "-q", "--allow-empty", "-m", "c"], check=True)
    rundir = _make_manifest(tmp_path, clone=clone)
    art_dir = tmp_path / "runs"
    art_dir.mkdir()
    result = _run_stub(FIXTURES_DIR / "arm-b.jsonl", "b", "tamper1", 1, "p", rundir, art_dir,
                       stub_extra=f"echo evil > {str(clone)!r}/injected.md")
    assert result.returncode == 4, result.stderr
    assert "plugin clone modified" in result.stderr


# ── Context / preceding-turns tests (ticket 01) ────────────────────────────────

def _make_recording_stub(rundir, args_file, stdin_file, stream_file):
    """Build a stub that saves argv as JSON and stdin as text, then emits stream_file."""
    scratch = json.loads((rundir / "run-manifest.json").read_text())["scratch_cwd"]
    stub = rundir / "recording_stub.sh"
    stub.write_text(
        "#!/bin/bash\n"
        # Read stdin first (it's the prompt piped from run_one.sh)
        "STDIN_TEXT=$(cat)\n"
        f'printf \'%s\' "$STDIN_TEXT" > {str(stdin_file)!r}\n'
        # Save argv as JSON array
        f"/usr/local/bin/python3.13 -c \"import json,sys; json.dump(list(sys.argv[1:]), open('{args_file}', 'w'))\" \"$@\"\n"
        # Validate we're running from a scratch sub-directory
        f'case "$(pwd -P)/" in "$(cd {scratch!r} && pwd -P)"/run-*) ;; *) echo "stub: wrong cwd $(pwd)" >&2; exit 3;; esac\n'
        # Emit the stream
        f"cat {str(stream_file)!r}\n"
    )
    stub.chmod(0o755)
    return stub


def _minimal_stream(tmp_path, name="stream.jsonl"):
    """Write a minimal valid JSONL stream and return its path."""
    stream = [
        {"type": "system", "subtype": "init", "model": EXPECTED_MODEL, "skills": [], "plugins": []},
        {"type": "result", "subtype": "success", "total_cost_usd": 0.01, "num_turns": 1,
         "is_error": False, "result": "done"},
    ]
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(e) for e in stream))
    return p


def test_context_goes_to_system_prompt_not_stdin(tmp_path):
    """run_one.sh with a 6th context_file arg passes preceding turns via
    --append-system-prompt and leaves stdin as the bare prompt, unchanged."""
    ctx = [
        {"role": "user", "text": "earlier Q"},
        {"role": "assistant", "text": "earlier A"},
    ]
    ctx_file = tmp_path / "ctx.json"
    ctx_file.write_text(json.dumps(ctx))

    args_file = tmp_path / "recorded_args.json"
    stdin_file = tmp_path / "recorded_stdin.txt"
    stream_file = _minimal_stream(tmp_path)

    rundir = _make_manifest(tmp_path)
    art_dir = tmp_path / "runs"
    art_dir.mkdir()

    stub = _make_recording_stub(rundir, args_file, stdin_file, stream_file)

    fake_settings = rundir / "guard-settings.json"
    fake_settings.write_text(json.dumps({"model": EXPECTED_MODEL, "hooks": {}}))

    env = os.environ.copy()
    env["W4_CLAUDE_BIN"] = str(stub)
    env["W4_SETTINGS_FILE"] = str(fake_settings)
    env["W4_ARTIFACT_DIR"] = str(art_dir)

    result = subprocess.run(
        ["bash", str(RUN_ONE_SH),
         "b", "aef6880dbd5903c4", "1", "bare prompt text",
         str(rundir), str(ctx_file)],
        capture_output=True, text=True, env=env,
    )
    assert result.returncode == 0, f"run_one.sh failed:\n{result.stderr}\n{result.stdout}"

    recorded_args = json.loads(args_file.read_text())

    # --append-system-prompt must be present
    assert "--append-system-prompt" in recorded_args, \
        f"--append-system-prompt not found in argv: {recorded_args}"
    idx = recorded_args.index("--append-system-prompt")
    ctx_value = recorded_args[idx + 1]

    assert "User: earlier Q" in ctx_value, \
        f"Missing 'User: earlier Q' in ctx block: {ctx_value!r}"
    assert "Assistant: earlier A" in ctx_value, \
        f"Missing 'Assistant: earlier A' in ctx block: {ctx_value!r}"

    # stdin must be the bare prompt, unmodified
    assert stdin_file.read_text() == "bare prompt text", \
        f"stdin was modified: {stdin_file.read_text()!r}"

    # artifact must record context_turns
    artifact = json.loads((art_dir / "b-aef6880dbd5903c4-rep1.json").read_text())
    assert artifact.get("context_turns", -1) >= 1, \
        f"context_turns missing or 0 in artifact: {artifact}"


def test_no_context_arg_is_unchanged(tmp_path):
    """Without a 6th arg, run_one.sh must not pass --append-system-prompt.
    Ensures W4 replay is reproducible."""
    args_file = tmp_path / "recorded_args.json"
    stdin_file = tmp_path / "recorded_stdin.txt"
    stream_file = _minimal_stream(tmp_path)

    rundir = _make_manifest(tmp_path)
    art_dir = tmp_path / "runs"
    art_dir.mkdir()

    stub = _make_recording_stub(rundir, args_file, stdin_file, stream_file)

    fake_settings = rundir / "guard-settings.json"
    fake_settings.write_text(json.dumps({"model": EXPECTED_MODEL, "hooks": {}}))

    env = os.environ.copy()
    env["W4_CLAUDE_BIN"] = str(stub)
    env["W4_SETTINGS_FILE"] = str(fake_settings)
    env["W4_ARTIFACT_DIR"] = str(art_dir)

    result = subprocess.run(
        ["bash", str(RUN_ONE_SH),
         "b", "noctx123", "1", "bare prompt only", str(rundir)],  # 5 args
        capture_output=True, text=True, env=env,
    )
    assert result.returncode == 0, f"run_one.sh failed:\n{result.stderr}\n{result.stdout}"

    recorded_args = json.loads(args_file.read_text())
    assert "--append-system-prompt" not in recorded_args, \
        f"--append-system-prompt appeared without a context file: {recorded_args}"

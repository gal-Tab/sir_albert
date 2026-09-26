"""Tests for run_tranche.sh — the script that spends the P2 budget.

A stub claude stands in for the real binary (conftest.py makes the real one a
tripwire). Each stub call logs which arm's settings file it was given, so the
tests can check ordering, resumption and the budget stops.
"""
import json
import os
import subprocess
from pathlib import Path

import pytest

TESTS_EVAL = Path(__file__).parent
FIXTURES = TESTS_EVAL / "fixtures"
RUN_TRANCHE = TESTS_EVAL.parent.parent / "tools" / "eval" / "run_tranche.sh"
MODEL = "claude-opus-5-5[1m]"


def _setup(tmp_path, n_rows=10, cost=0.05):
    rundir = tmp_path / "rundir"
    rundir.mkdir()
    scratch = tmp_path / "scratch"
    clone = tmp_path / "clone"
    clone.mkdir()
    arm_a, arm_b = rundir / "arm-a-settings.json", rundir / "arm-b-settings.json"
    for f in (arm_a, arm_b):
        f.write_text(json.dumps({"model": MODEL}))
    (rundir / "run-manifest.json").write_text(json.dumps({
        "pin_sha": "abc", "clone_path": str(clone), "arm_a_settings": str(arm_a),
        "arm_b_settings": str(arm_b), "scratch_cwd": str(scratch), "rundir": str(rundir),
    }))
    (rundir / "model-snapshot.txt").write_text(MODEL)
    for a in ("a", "b"):
        (rundir / f"canary-{a}.jsonl").write_text("{}\n")

    sample = tmp_path / "sample.jsonl"
    sample.write_text("".join(
        json.dumps({"_hash": f"h{i:02d}", "text": f"prompt number {i}", "p2_slice": "happy_path"}) + "\n"
        for i in range(n_rows)))

    # Stub stream: the real probe stream with a controlled cost.
    events = [json.loads(l) for l in (FIXTURES / "arm-b.jsonl").read_text().splitlines() if l.strip()]
    for e in events:
        if e.get("type") == "result":
            e["total_cost_usd"] = cost
    stream = tmp_path / "stream.jsonl"
    stream.write_text("".join(json.dumps(e) + "\n" for e in events))

    calls = tmp_path / "calls.log"
    stub = tmp_path / "stub_claude.sh"
    stub.write_text(
        "#!/bin/bash\n"
        'IN=$(cat); [ -n "$IN" ] || exit 6\n'
        'prev=""; for a in "$@"; do [ "$prev" = "--settings" ] && echo "$a" >> ' + repr(str(calls)) + '; prev="$a"; done\n'
        "cat " + repr(str(stream)) + "\n"
    )
    stub.chmod(0o755)

    sessions = tmp_path / "sessions.jsonl"
    sessions.write_text(json.dumps({"cwd": "/somewhere/else"}) + "\n"
                        + json.dumps({"cwd": str(scratch) + "/run-x"}) + "\n")
    env = os.environ.copy()
    env.update({
        "W4_CLAUDE_BIN": str(stub),
        "W4_ARTIFACT_DIR": str(tmp_path / "runs"),
        "W4_SESSIONS_FILE": str(sessions),
        "W4_TEST_MODEL": MODEL,
    })
    return rundir, sample, env, calls, sessions


def _run(rundir, sample, env, tranche="1", **extra_env):
    e = dict(env, **extra_env)
    return subprocess.run(["bash", str(RUN_TRANCHE), str(rundir), str(sample), tranche],
                          capture_output=True, text=True, env=e)


def _arms(calls):
    return ["a" if "arm-a" in l else "b" for l in calls.read_text().splitlines()]


def test_tranche_1_runs_40_interleaved(tmp_path):
    rundir, sample, env, calls, _ = _setup(tmp_path)
    r = _run(rundir, sample, env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert len(list((tmp_path / "runs").glob("*.json"))) == 40
    assert _arms(calls)[:4] == ["a", "b", "a", "b"], "arms must alternate within each rep"
    assert _arms(calls).count("a") == _arms(calls).count("b") == 20


def test_tranche_2_uses_rows_11_to_15(tmp_path):
    rundir, sample, env, calls, _ = _setup(tmp_path, n_rows=15)
    r = _run(rundir, sample, env, tranche="2")
    assert r.returncode == 0, r.stdout + r.stderr
    hashes = {p.name.split("-")[1] for p in (tmp_path / "runs").glob("*.json")}
    assert hashes == {f"h{i:02d}" for i in range(10, 15)}


def test_resume_skips_existing_artifacts(tmp_path):
    rundir, sample, env, calls, _ = _setup(tmp_path)
    assert _run(rundir, sample, env).returncode == 0
    n_calls = len(calls.read_text().splitlines())
    r = _run(rundir, sample, env)
    assert r.returncode == 0
    assert len(calls.read_text().splitlines()) == n_calls, "a re-run must not spawn again"


def test_budget_cap_stops_before_exceeding(tmp_path):
    rundir, sample, env, calls, _ = _setup(tmp_path, cost=0.50)
    r = _run(rundir, sample, env, W4_BUDGET_USD="3")
    assert r.returncode == 3, r.stdout
    assert "would exceed" in r.stdout
    spent = sum(json.loads(p.read_text())["cost_usd"] for p in (tmp_path / "runs").glob("*.json"))
    assert spent + 0.60 > 3 and spent <= 3


def test_extrapolation_abort_after_first_10_runs(tmp_path):
    rundir, sample, env, calls, _ = _setup(tmp_path, cost=1.00)
    r = _run(rundir, sample, env)
    assert r.returncode == 3, r.stdout
    assert "extrapolates" in r.stdout
    assert len(list((tmp_path / "runs").glob("*.json"))) == 10


def test_wrong_model_aborts_without_spawning(tmp_path, monkeypatch):
    rundir, sample, env, calls, _ = _setup(tmp_path)
    bad = tmp_path / "bad-settings.json"
    bad.write_text(json.dumps({"model": "claude-sonnet-5"}))
    r = _run(rundir, sample, env, W4_SETTINGS_FILE=str(bad))
    assert r.returncode == 2 and "ABORT: model" in r.stdout
    assert not calls.exists()


def test_missing_canary_aborts_without_spawning(tmp_path):
    rundir, sample, env, calls, _ = _setup(tmp_path)
    (rundir / "canary-b.jsonl").unlink()
    r = _run(rundir, sample, env)
    assert r.returncode == 2 and "canary" in r.stdout
    assert not calls.exists()


def test_harness_session_rows_stripped_at_end(tmp_path):
    rundir, sample, env, calls, sessions = _setup(tmp_path)
    assert _run(rundir, sample, env).returncode == 0
    rows = [json.loads(l) for l in sessions.read_text().splitlines() if l.strip()]
    assert rows == [{"cwd": "/somewhere/else"}]

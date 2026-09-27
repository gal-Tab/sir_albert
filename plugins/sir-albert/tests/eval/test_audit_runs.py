"""Tests for audit_runs.py — ticket 12 step 9.

Uses real artifact schema keys (prompt_hash, arm, rep, model, truncated,
final_text, result_event, cost_usd, assistant_text) matching the actual
artifacts produced by run_one.sh.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS_EVAL = Path(__file__).parent.parent.parent / "tools" / "eval"
AUDIT_RUNS = TOOLS_EVAL / "audit_runs.py"

EXPECTED_MODEL = "claude-sonnet-5"


def _make_artifact(arm, prompt_hash, rep, *, model=EXPECTED_MODEL,
                   final_text="good answer", truncated=False,
                   is_error=False, cost_usd=0.10):
    """Return a minimal artifact dict matching the real run_one.sh schema."""
    return {
        "arm": arm,
        "prompt_hash": prompt_hash,
        "rep": rep,
        "prompt_text": "test prompt",
        "model": model,
        "exit_code": 0,
        "timestamp_utc": "2026-09-27T00:00:00",
        "cost_usd": cost_usd if not (is_error and cost_usd == 0) else 0.0,
        "turn_count": 1,
        "budget_capped": False,
        "result_subtype": "success",
        "skills_loaded": [],
        "skills_called": [],
        "assistant_text": final_text if final_text else "",
        "truncated": truncated,
        "result_count": 1,
        "final_text": final_text if final_text else "",
        "context_turns": 0,
        "init_event": {"type": "system", "subtype": "init", "model": model, "skills": [], "plugins": []},
        "result_event": {
            "type": "result",
            "subtype": "success",
            "is_error": is_error,
            "total_cost_usd": cost_usd if not (is_error and cost_usd == 0) else 0.0,
            "num_turns": 1,
            "result": final_text if final_text else None,
        },
    }


def _write_artifacts(art_dir: Path, artifacts: list[dict]):
    art_dir.mkdir(parents=True, exist_ok=True)
    for art in artifacts:
        name = f"{art['arm']}-{art['prompt_hash']}-rep{art['rep']}.json"
        (art_dir / name).write_text(json.dumps(art, indent=2))


def _run_audit(artifact_dir, arms="b,a", reps=1, expected_prompts=2,
               model=EXPECTED_MODEL, extra_args=None):
    cmd = [
        sys.executable, str(AUDIT_RUNS),
        str(artifact_dir),
        "--arms", arms,
        "--reps", str(reps),
        "--expected-prompts", str(expected_prompts),
        "--model", model,
    ]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True)


# ── Fixture helpers ─────────────────────────────────────────────────────────────

def _clean_artifacts(arms, hashes, reps=1):
    """Build a clean set of artifacts for all arm×hash×rep combos."""
    result = []
    for arm in arms:
        for h in hashes:
            for rep in range(1, reps + 1):
                result.append(_make_artifact(arm, h, rep))
    return result


HASHES_2 = ["aabbcc001122", "ddeeff334455"]
HASHES_3 = ["aabbcc001122", "ddeeff334455", "112233aabbcc"]


# ── Tests ───────────────────────────────────────────────────────────────────────

def test_clean_2arm_2prompt_passes(tmp_path):
    """All checks pass on a clean 2-arm 2-prompt set."""
    arts = _clean_artifacts(["b", "a"], HASHES_2)
    _write_artifacts(tmp_path, arts)
    r = _run_audit(tmp_path, arms="b,a", reps=1, expected_prompts=2)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "OK" in r.stdout


def test_clean_3arm_3prompt_passes(tmp_path):
    """3-arm (b,a,s) × 3-prompt clean set passes."""
    arts = _clean_artifacts(["b", "a", "s"], HASHES_3)
    _write_artifacts(tmp_path, arts)
    r = _run_audit(tmp_path, arms="b,a,s", reps=1, expected_prompts=3)
    assert r.returncode == 0, r.stdout + r.stderr


def test_missing_artifact_fails(tmp_path):
    """One missing artifact → non-zero exit and FAIL in output."""
    arts = _clean_artifacts(["b", "a"], HASHES_2)
    _write_artifacts(tmp_path, arts)
    # Remove one artifact
    (tmp_path / f"a-{HASHES_2[0]}-rep1.json").unlink()
    r = _run_audit(tmp_path, arms="b,a", reps=1, expected_prompts=2)
    assert r.returncode != 0
    assert "FAIL" in r.stdout


def test_incomplete_tuple_fails(tmp_path):
    """A prompt_hash missing from one arm → incomplete tuple."""
    arts = _clean_artifacts(["b", "a"], HASHES_2)
    # Remove arm a for first hash (makes tuple incomplete)
    arts_filtered = [a for a in arts if not (a["arm"] == "a" and a["prompt_hash"] == HASHES_2[0])]
    _write_artifacts(tmp_path, arts_filtered)
    r = _run_audit(tmp_path, arms="b,a", reps=1, expected_prompts=2)
    assert r.returncode != 0
    assert "FAIL" in r.stdout


def test_infra_error_detected(tmp_path):
    """Zero-cost is_error=True artifact is flagged as infra error."""
    arts = _clean_artifacts(["b", "a"], HASHES_2)
    # Make one artifact an infra error ($0 cost, is_error=True)
    arts[0] = _make_artifact(arts[0]["arm"], arts[0]["prompt_hash"], arts[0]["rep"],
                              is_error=True, cost_usd=0.0)
    _write_artifacts(tmp_path, arts)
    r = _run_audit(tmp_path, arms="b,a", reps=1, expected_prompts=2)
    assert r.returncode != 0
    assert "infra" in r.stdout.lower()


def test_wrong_model_fails(tmp_path):
    """An artifact with the wrong model fails the model check."""
    arts = _clean_artifacts(["b", "a"], HASHES_2)
    arts[0] = _make_artifact(arts[0]["arm"], arts[0]["prompt_hash"], arts[0]["rep"],
                              model="claude-opus-5-5[1m]")
    _write_artifacts(tmp_path, arts)
    r = _run_audit(tmp_path, arms="b,a", reps=1, expected_prompts=2)
    assert r.returncode != 0
    assert "FAIL" in r.stdout


def test_truncated_reported_per_arm(tmp_path):
    """truncated=True artifacts are counted per arm (warning, not hard fail)."""
    arts = _clean_artifacts(["b", "a"], HASHES_2)
    arts[0] = _make_artifact(arts[0]["arm"], arts[0]["prompt_hash"], arts[0]["rep"],
                              truncated=True)
    _write_artifacts(tmp_path, arts)
    r = _run_audit(tmp_path, arms="b,a", reps=1, expected_prompts=2)
    # Truncated is a warning so exit 0 if all other checks pass
    assert "truncated" in r.stdout.lower()


def test_empty_final_text_reported(tmp_path):
    """Empty final_text is reported."""
    arts = _clean_artifacts(["b", "a"], HASHES_2)
    arts[0] = _make_artifact(arts[0]["arm"], arts[0]["prompt_hash"], arts[0]["rep"],
                              final_text="")
    _write_artifacts(tmp_path, arts)
    r = _run_audit(tmp_path, arms="b,a", reps=1, expected_prompts=2)
    assert "final_text" in r.stdout
    assert "1" in r.stdout  # one empty


def test_multi_rep_complete_tuples(tmp_path):
    """With reps=2, expects 2 complete tuples per hash (one per rep)."""
    arts = _clean_artifacts(["b", "a"], HASHES_2, reps=2)
    _write_artifacts(tmp_path, arts)
    r = _run_audit(tmp_path, arms="b,a", reps=2, expected_prompts=2)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "OK" in r.stdout


def test_audit_script_exists():
    assert AUDIT_RUNS.exists(), f"audit_runs.py not found at {AUDIT_RUNS}"

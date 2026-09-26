"""Tests for verdict.py — ticket 09 (including coordinator additions).

Exit codes:
  0 = PASS
  1 = FAIL
  2 = ABORT (run count ≠ 60, or >3 judge_error pairs)
  3 = INCONCLUSIVE (ties > 50% of pairs)
"""
import json
import subprocess
from pathlib import Path

import pytest

TOOLS_EVAL = Path(__file__).parent.parent.parent / "tools" / "eval"
VERDICT_PY = TOOLS_EVAL / "verdict.py"
EXPECTED_MODEL = "claude-opus-5-5[1m]"


# ── Fixture builders ──────────────────────────────────────────────────────────

def _make_run_artifact(arm, prompt_hash, rep, skills_called=None, result_text="Answer text here."):
    return {
        "arm": arm,
        "prompt_hash": prompt_hash,
        "rep": rep,
        "prompt_text": "test prompt",
        "model": EXPECTED_MODEL,
        "exit_code": 0,
        "timestamp_utc": "2026-09-26T00:00:00",
        "cost_usd": 0.05,
        "turn_count": 1,
        "budget_capped": False,
        "result_subtype": "success",
        "skills_loaded": [],
        "skills_called": skills_called or [],
        "init_event": None,
        "result_event": {"type": "result", "subtype": "success", "result": result_text},
    }


def _make_judgment(prompt_hash, rep, final_verdict, call_ab_winner="left", call_ba_winner="right"):
    return {
        "prompt_hash": prompt_hash,
        "rep": rep,
        "call_ab": {"winner": call_ab_winner, "reason": "test", "judge_model": EXPECTED_MODEL},
        "call_ba": {"winner": call_ba_winner, "reason": "test", "judge_model": EXPECTED_MODEL},
        "final_verdict": final_verdict,
    }


def _populate_runs(runs_dir, prompts):
    """Create 60 run artifacts: 2 arms × 2 reps × 15 prompts = 60."""
    for ph in prompts:
        for arm in ("a", "b"):
            for rep in (1, 2):
                art = _make_run_artifact(arm, ph, rep)
                (runs_dir / f"{arm}-{ph}-rep{rep}.json").write_text(json.dumps(art))


def _make_sample(sample_path, prompts, happy_hashes, none_hashes, b_silent_hashes, label_map=None):
    rows = []
    for ph in prompts:
        if ph in happy_hashes:
            slice_val = "happy_path"
            label = (label_map or {}).get(ph, "handoff")
        elif ph in b_silent_hashes:
            slice_val = "b_silent"
            label = "plan"
        else:
            slice_val = "control"
            label = "none"
        rows.append({"prompt_hash": ph, "p2_slice": slice_val, "label": label})
    sample_path.write_text("\n".join(json.dumps(r) for r in rows))


def run_verdict(runs_dir, judgments_path, sample_path, out_dir):
    result = subprocess.run(
        [
            "/usr/local/bin/python3.13",
            str(VERDICT_PY),
            "--runs-dir", str(runs_dir),
            "--judgments", str(judgments_path),
            "--sample", str(sample_path),
            "--out-dir", str(out_dir),
        ],
        capture_output=True,
        text=True,
    )
    return result


# ── Standard 15-prompt setup ─────────────────────────────────────────────────

PROMPTS_15 = [f"p{i:02d}" for i in range(15)]
HAPPY_5 = PROMPTS_15[:5]       # happy_path slice
B_SILENT_5 = PROMPTS_15[5:10]  # b_silent slice
NONE_5 = PROMPTS_15[10:15]     # control slice


@pytest.fixture()
def base_runs(tmp_path):
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    _populate_runs(runs_dir, PROMPTS_15)
    return runs_dir, tmp_path


# ── PASS fixture ──────────────────────────────────────────────────────────────

def test_pass_67pct_winrate_4_of_5_skills(base_runs):
    runs_dir, tmp_path = base_runs

    # B wins 20/30 (67%), ties 0
    judgments = []
    for i, ph in enumerate(PROMPTS_15):
        for rep in (1, 2):
            fv = "B_wins" if i < 10 else "A_wins"  # 20 B wins, 10 A wins
            judgments.append(_make_judgment(ph, rep, fv))

    jpath = tmp_path / "judgments-resolved.jsonl"
    jpath.write_text("\n".join(json.dumps(j) for j in judgments))

    # Happy-path: 4/5 prompts have matching skill invoked, 1 does not
    # Override arm-b artifacts for happy_path prompts
    for i, ph in enumerate(HAPPY_5):
        label = "handoff"
        skills = ["sir-albert:handoff"] if i < 4 else []  # 4 hits, 1 miss
        for rep in (1, 2):
            art = _make_run_artifact("b", ph, rep, skills_called=skills)
            (runs_dir / f"b-{ph}-rep{rep}.json").write_text(json.dumps(art))

    sample_path = tmp_path / "sample.jsonl"
    _make_sample(sample_path, PROMPTS_15, set(HAPPY_5), set(NONE_5), set(B_SILENT_5),
                 label_map={ph: "handoff" for ph in HAPPY_5})

    result = run_verdict(runs_dir, jpath, sample_path, tmp_path)
    assert result.returncode == 0, f"Expected PASS:\n{result.stdout}\n{result.stderr}"


# ── FAIL: loaded-only skills (regression for rigged gate) ─────────────────────

def test_fail_loaded_only_not_called(base_runs):
    """skills_loaded with 28 entries but skills_called=[] must fail the skill gate."""
    runs_dir, tmp_path = base_runs

    # Win-rate PASS (67%)
    judgments = [
        _make_judgment(ph, rep, "B_wins" if i < 10 else "A_wins")
        for i, ph in enumerate(PROMPTS_15)
        for rep in (1, 2)
    ]
    jpath = tmp_path / "judgments-resolved.jsonl"
    jpath.write_text("\n".join(json.dumps(j) for j in judgments))

    # All 5 happy-path prompts: loaded 28 skills but called none
    for ph in HAPPY_5:
        for rep in (1, 2):
            art = _make_run_artifact("b", ph, rep, skills_called=[])  # called nothing
            art["skills_loaded"] = [f"sir-albert:skill{k}" for k in range(28)]
            (runs_dir / f"b-{ph}-rep{rep}.json").write_text(json.dumps(art))

    sample_path = tmp_path / "sample.jsonl"
    _make_sample(sample_path, PROMPTS_15, set(HAPPY_5), set(NONE_5), set(B_SILENT_5),
                 label_map={ph: "handoff" for ph in HAPPY_5})

    result = run_verdict(runs_dir, jpath, sample_path, tmp_path)
    assert result.returncode == 1, f"Expected FAIL (loaded-only):\n{result.stdout}"
    assert "FAIL" in result.stdout


# ── FAIL: wrong skill ─────────────────────────────────────────────────────────

def test_fail_wrong_skill(base_runs):
    """skills_called=['sir-albert:handoff'] on plan-labeled prompts counts as a miss."""
    runs_dir, tmp_path = base_runs

    judgments = [
        _make_judgment(ph, rep, "B_wins" if i < 10 else "A_wins")
        for i, ph in enumerate(PROMPTS_15)
        for rep in (1, 2)
    ]
    jpath = tmp_path / "judgments-resolved.jsonl"
    jpath.write_text("\n".join(json.dumps(j) for j in judgments))

    # Happy-path labeled 'plan' but artifact calls 'handoff' (wrong route)
    for ph in HAPPY_5:
        for rep in (1, 2):
            art = _make_run_artifact("b", ph, rep, skills_called=["sir-albert:handoff"])
            (runs_dir / f"b-{ph}-rep{rep}.json").write_text(json.dumps(art))

    sample_path = tmp_path / "sample.jsonl"
    _make_sample(sample_path, PROMPTS_15, set(HAPPY_5), set(NONE_5), set(B_SILENT_5),
                 label_map={ph: "plan" for ph in HAPPY_5})

    result = run_verdict(runs_dir, jpath, sample_path, tmp_path)
    assert result.returncode == 1, f"Expected FAIL (wrong skill):\n{result.stdout}"


# ── ABORT: run count ─────────────────────────────────────────────────────────

def test_abort_wrong_run_count(tmp_path):
    runs_dir = tmp_path / "runs"
    runs_dir.mkdir()
    # Only 58 artifacts
    for i in range(29):
        ph = f"p{i:02d}"
        for arm in ("a", "b"):
            art = _make_run_artifact(arm, ph, 1)
            (runs_dir / f"{arm}-{ph}-rep1.json").write_text(json.dumps(art))

    jpath = tmp_path / "j.jsonl"
    jpath.write_text("")
    sample_path = tmp_path / "sample.jsonl"
    sample_path.write_text("")

    result = run_verdict(runs_dir, jpath, sample_path, tmp_path)
    assert result.returncode == 2, f"Expected ABORT:\n{result.stdout}"
    assert "ABORT" in result.stdout
    assert "58" in result.stdout


# ── FAIL: win-rate < 40% ──────────────────────────────────────────────────────

def test_fail_winrate_33pct(base_runs):
    runs_dir, tmp_path = base_runs

    # B wins 10/30 (33%)
    judgments = [
        _make_judgment(ph, rep, "B_wins" if i < 5 else "A_wins")
        for i, ph in enumerate(PROMPTS_15)
        for rep in (1, 2)
    ]
    jpath = tmp_path / "judgments-resolved.jsonl"
    jpath.write_text("\n".join(json.dumps(j) for j in judgments))

    sample_path = tmp_path / "sample.jsonl"
    _make_sample(sample_path, PROMPTS_15, set(HAPPY_5), set(NONE_5), set(B_SILENT_5))

    result = run_verdict(runs_dir, jpath, sample_path, tmp_path)
    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "33" in result.stdout or "win-rate" in result.stdout.lower()


# ── FAIL: skill invocations < 4/5 ────────────────────────────────────────────

def test_fail_only_2_of_5_skills(base_runs):
    runs_dir, tmp_path = base_runs

    # Win-rate PASS
    judgments = [
        _make_judgment(ph, rep, "B_wins")
        for ph in PROMPTS_15
        for rep in (1, 2)
    ]
    jpath = tmp_path / "judgments-resolved.jsonl"
    jpath.write_text("\n".join(json.dumps(j) for j in judgments))

    # Only 2/5 happy-path prompts have skills
    for i, ph in enumerate(HAPPY_5):
        skills = ["sir-albert:handoff"] if i < 2 else []
        for rep in (1, 2):
            art = _make_run_artifact("b", ph, rep, skills_called=skills)
            (runs_dir / f"b-{ph}-rep{rep}.json").write_text(json.dumps(art))

    sample_path = tmp_path / "sample.jsonl"
    _make_sample(sample_path, PROMPTS_15, set(HAPPY_5), set(NONE_5), set(B_SILENT_5),
                 label_map={ph: "handoff" for ph in HAPPY_5})

    result = run_verdict(runs_dir, jpath, sample_path, tmp_path)
    assert result.returncode == 1
    assert "FAIL" in result.stdout
    assert "2/5" in result.stdout or "sir_albert" in result.stdout.lower() or "skill" in result.stdout.lower()


# ── INCONCLUSIVE: all ties (coordinator addition) ─────────────────────────────

def test_inconclusive_all_ties(base_runs):
    """30 pairs, all ties → INCONCLUSIVE (exit 3)."""
    runs_dir, tmp_path = base_runs

    judgments = [
        _make_judgment(ph, rep, "tie", call_ab_winner="tie", call_ba_winner="tie")
        for ph in PROMPTS_15
        for rep in (1, 2)
    ]
    assert len(judgments) == 30

    jpath = tmp_path / "judgments-resolved.jsonl"
    jpath.write_text("\n".join(json.dumps(j) for j in judgments))

    sample_path = tmp_path / "sample.jsonl"
    _make_sample(sample_path, PROMPTS_15, set(HAPPY_5), set(NONE_5), set(B_SILENT_5))

    result = run_verdict(runs_dir, jpath, sample_path, tmp_path)
    assert result.returncode == 3, f"Expected INCONCLUSIVE (exit 3):\n{result.stdout}\n{result.stderr}"
    assert "INCONCLUSIVE" in result.stdout


# ── ABORT: too many judge_error pairs (coordinator addition) ─────────────────

def test_abort_too_many_judge_errors(base_runs):
    """4 judge_error pairs → ABORT (exit 2)."""
    runs_dir, tmp_path = base_runs

    judgments = []
    for i, ph in enumerate(PROMPTS_15):
        for rep in (1, 2):
            if i * 2 + rep - 1 < 4:
                # judge_error: both calls returned judge_error
                j = _make_judgment(ph, rep, "tie",
                                   call_ab_winner="judge_error",
                                   call_ba_winner="judge_error")
            else:
                j = _make_judgment(ph, rep, "B_wins")
            judgments.append(j)

    jpath = tmp_path / "judgments-resolved.jsonl"
    jpath.write_text("\n".join(json.dumps(j) for j in judgments))

    sample_path = tmp_path / "sample.jsonl"
    _make_sample(sample_path, PROMPTS_15, set(HAPPY_5), set(NONE_5), set(B_SILENT_5))

    result = run_verdict(runs_dir, jpath, sample_path, tmp_path)
    assert result.returncode == 2, f"Expected ABORT (exit 2):\n{result.stdout}\n{result.stderr}"
    assert "ABORT" in result.stdout
    assert "judge_error" in result.stdout.lower()


# ── Report has required content ───────────────────────────────────────────────

def test_report_has_superpowers_decision_paragraph(base_runs):
    runs_dir, tmp_path = base_runs

    judgments = [
        _make_judgment(ph, rep, "B_wins")
        for ph in PROMPTS_15
        for rep in (1, 2)
    ]
    jpath = tmp_path / "judgments-resolved.jsonl"
    jpath.write_text("\n".join(json.dumps(j) for j in judgments))

    for ph in HAPPY_5:
        for rep in (1, 2):
            art = _make_run_artifact("b", ph, rep, skills_called=["sir-albert:handoff"])
            (runs_dir / f"b-{ph}-rep{rep}.json").write_text(json.dumps(art))

    sample_path = tmp_path / "sample.jsonl"
    _make_sample(sample_path, PROMPTS_15, set(HAPPY_5), set(NONE_5), set(B_SILENT_5),
                 label_map={ph: "handoff" for ph in HAPPY_5})

    run_verdict(runs_dir, jpath, sample_path, tmp_path)

    reports = list(tmp_path.glob("verdict-*.md"))
    assert len(reports) >= 1
    content = reports[0].read_text()
    assert "separate, explicit decision" in content
    assert "never inferred" in content


def test_report_filename_not_plain_verdict_md(base_runs):
    runs_dir, tmp_path = base_runs

    judgments = [_make_judgment(ph, rep, "B_wins") for ph in PROMPTS_15 for rep in (1, 2)]
    jpath = tmp_path / "j.jsonl"
    jpath.write_text("\n".join(json.dumps(j) for j in judgments))

    sample_path = tmp_path / "sample.jsonl"
    _make_sample(sample_path, PROMPTS_15, set(HAPPY_5), set(NONE_5), set(B_SILENT_5),
                 label_map={ph: "handoff" for ph in HAPPY_5})

    for ph in HAPPY_5:
        for rep in (1, 2):
            art = _make_run_artifact("b", ph, rep, skills_called=["sir-albert:handoff"])
            (runs_dir / f"b-{ph}-rep{rep}.json").write_text(json.dumps(art))

    run_verdict(runs_dir, jpath, sample_path, tmp_path)

    plain = tmp_path / "verdict.md"
    assert not plain.exists(), "verdict.md must not be created (must be namespaced)"
    reports = list(tmp_path.glob("verdict-*-*.md"))
    assert len(reports) >= 1


def test_report_has_per_slice_winrate(base_runs):
    """Report must include per-slice win-rate table."""
    runs_dir, tmp_path = base_runs

    judgments = [_make_judgment(ph, rep, "B_wins") for ph in PROMPTS_15 for rep in (1, 2)]
    jpath = tmp_path / "j.jsonl"
    jpath.write_text("\n".join(json.dumps(j) for j in judgments))

    for ph in HAPPY_5:
        for rep in (1, 2):
            art = _make_run_artifact("b", ph, rep, skills_called=["sir-albert:handoff"])
            (runs_dir / f"b-{ph}-rep{rep}.json").write_text(json.dumps(art))

    sample_path = tmp_path / "sample.jsonl"
    _make_sample(sample_path, PROMPTS_15, set(HAPPY_5), set(NONE_5), set(B_SILENT_5),
                 label_map={ph: "handoff" for ph in HAPPY_5})

    run_verdict(runs_dir, jpath, sample_path, tmp_path)
    reports = list(tmp_path.glob("verdict-*.md"))
    assert reports
    content = reports[0].read_text()
    assert "happy_path" in content or "slice" in content.lower()

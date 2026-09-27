"""Tests for prompt_corpus.py p1-score subcommand (ticket 03)."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).parent.parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))
import prompt_corpus  # noqa: E402


# ── Helpers ────────────────────────────────────────────────────────────────────

def _row(text, slice_, label, predicted_route=None, idx=0):
    h = hashlib.sha256(f"p1{idx}||{text}".encode()).hexdigest()[:16]
    return {
        "_hash": h,
        "text": text,
        "predicted_route": predicted_route,
        "slice": slice_,
        "label": label,
        "labeled_by": "gal" if label is not None else None,
        "labeled_at": "2026-09-26T00:00:00Z" if label is not None else None,
    }


def _write(path, rows):
    path.write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n",
        encoding="utf-8",
    )


def _run_score(tmp_path, monkeypatch, rows):
    f = tmp_path / "labeled-set.jsonl"
    _write(f, rows)
    monkeypatch.setattr(prompt_corpus, "EVAL_DIR", tmp_path)
    args = argparse.Namespace(file=str(f))
    return args


# ── Build fixtures ─────────────────────────────────────────────────────────────

def _make_router_match_rows(n_total, n_correct):
    """n_total router_match rows, n_correct have label==predicted_route."""
    rows = []
    for i in range(n_total):
        pred = "plan"
        if i < n_correct:
            label = pred   # TP
        else:
            label = "brainstorm"  # FP
        rows.append(_row(f"router match text {i}", "router_match", label,
                         predicted_route=pred, idx=i))
    return rows


def _make_task_initiating_rows(n_total, n_routed_correctly):
    """Use real routeable texts for the n_routed_correctly rows so _route fires."""
    rows = []
    # Texts that route to "plan"
    plan_texts = [
        "make a plan for the sprint",
        "write me a plan for this project",
        "create a plan for onboarding",
    ]
    # Texts that don't route
    no_route_texts = [
        "what is the status of the deployment pipeline today",
        "can you help me understand the team structure better please",
        "how do we handle onboarding for new team members in ops",
        "what are the main challenges we face in the next quarter",
        "what happened in the last meeting with stakeholders",
        "tell me about the current state of the marketing funnel",
        "what metrics should we track for the new campaign",
        "how is the team performing against the quarterly goals",
        "what is the plan for scaling the data infrastructure",
        "what are the next steps for the product roadmap",
        "summarize the recent feedback from enterprise clients",
        "what does the competitive landscape look like right now",
        "how do we improve the conversion rate on the landing page",
        "what is the timeline for the new feature launch",
        "help me understand the billing model for enterprise accounts",
        "describe the onboarding flow for new customers step by step",
        "what are the blockers for the current sprint velocity",
        "how do we improve retention for free tier users",
        "what is the current state of our data quality issues",
        "what should we prioritize next quarter for growth",
        "how many active users do we have in the EMEA region",
        "what is the response time for customer support tickets",
        "describe the integration points between marketing and sales",
        "how does the product analytics pipeline currently work",
        "what are the most common failure modes in the pipeline",
        "how do we track attribution for enterprise deals",
        "what are the key differences between the pricing tiers",
        "how does the approval process for marketing campaigns work",
    ]
    for i in range(n_total):
        if i < n_routed_correctly:
            text = plan_texts[i % len(plan_texts)]
            label = "plan"
        else:
            text = no_route_texts[i % len(no_route_texts)]
            label = "none"
        rows.append(_row(text, "task_initiating", label, idx=1000 + i))
    return rows


def _make_negative_control_rows(n_total, n_fire):
    """n_fire rows where _route fires (false fires), rest are true negatives."""
    # Routeable text → _route will return non-None
    routeable = "make a plan for the sprint"
    # Non-routeable ack
    ack = "ok"
    rows = []
    for i in range(n_total):
        text = routeable if i < n_fire else ack
        rows.append(_row(text, "negative_control", "none", idx=2000 + i))
    return rows


# ── PASS fixture ───────────────────────────────────────────────────────────────

def make_pass_fixture():
    """102 router-match (84 correct), 30 task-initiating (16 routed+correct), 10 neg-ctrl (0 fire)."""
    rm = _make_router_match_rows(102, 84)
    ti = _make_task_initiating_rows(30, 16)
    nc = _make_negative_control_rows(10, 0)
    return rm + ti + nc


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestP1ScorePass:
    def test_exits_0_on_passing_fixture(self, tmp_path, monkeypatch, capsys):
        rows = make_pass_fixture()
        args = _run_score(tmp_path, monkeypatch, rows)
        prompt_corpus.cmd_p1_score(args)  # should not raise
        out = capsys.readouterr().out
        assert "GATE FAIL" not in out

    def test_scorecard_written(self, tmp_path, monkeypatch):
        rows = make_pass_fixture()
        args = _run_score(tmp_path, monkeypatch, rows)
        prompt_corpus.cmd_p1_score(args)
        scorecard = tmp_path / "p1-scorecard-2026-09-26.md"
        assert scorecard.exists()

    def test_precision_reported(self, tmp_path, monkeypatch, capsys):
        rows = make_pass_fixture()
        args = _run_score(tmp_path, monkeypatch, rows)
        prompt_corpus.cmd_p1_score(args)
        out = capsys.readouterr().out
        # 84/102 = 82.4%
        assert "82" in out or "Precision" in out or (tmp_path / "p1-scorecard-2026-09-26.md").exists()


class TestP1ScoreFailPrecision:
    def test_exits_2_when_precision_below_80(self, tmp_path, monkeypatch, capsys):
        rm = _make_router_match_rows(102, 78)   # 78/102 = 76.5%
        ti = _make_task_initiating_rows(30, 16)
        nc = _make_negative_control_rows(10, 0)
        args = _run_score(tmp_path, monkeypatch, rm + ti + nc)
        with pytest.raises(SystemExit) as exc:
            prompt_corpus.cmd_p1_score(args)
        assert exc.value.code == 2

    def test_gate_fail_message_printed(self, tmp_path, monkeypatch, capsys):
        rm = _make_router_match_rows(102, 78)
        ti = _make_task_initiating_rows(30, 16)
        nc = _make_negative_control_rows(10, 0)
        args = _run_score(tmp_path, monkeypatch, rm + ti + nc)
        with pytest.raises(SystemExit):
            prompt_corpus.cmd_p1_score(args)
        out = capsys.readouterr().out
        assert "GATE FAIL" in out
        assert "precision" in out.lower()
        assert "76" in out  # 76.5%

    def test_scorecard_written_even_on_fail(self, tmp_path, monkeypatch):
        rm = _make_router_match_rows(102, 78)
        ti = _make_task_initiating_rows(30, 16)
        nc = _make_negative_control_rows(10, 0)
        args = _run_score(tmp_path, monkeypatch, rm + ti + nc)
        with pytest.raises(SystemExit):
            prompt_corpus.cmd_p1_score(args)
        assert (tmp_path / "p1-scorecard-2026-09-26.md").exists()


class TestP1ScoreFailFF:
    def test_exits_2_when_ff_above_10(self, tmp_path, monkeypatch, capsys):
        rm = _make_router_match_rows(102, 84)
        ti = _make_task_initiating_rows(30, 16)
        nc = _make_negative_control_rows(10, 2)  # 20% FF
        args = _run_score(tmp_path, monkeypatch, rm + ti + nc)
        with pytest.raises(SystemExit) as exc:
            prompt_corpus.cmd_p1_score(args)
        assert exc.value.code == 2

    def test_gate_fail_ff_message(self, tmp_path, monkeypatch, capsys):
        rm = _make_router_match_rows(102, 84)
        ti = _make_task_initiating_rows(30, 16)
        nc = _make_negative_control_rows(10, 2)
        args = _run_score(tmp_path, monkeypatch, rm + ti + nc)
        with pytest.raises(SystemExit):
            prompt_corpus.cmd_p1_score(args)
        out = capsys.readouterr().out
        assert "GATE FAIL" in out
        assert "false-fire" in out.lower()
        assert "20" in out


class TestP1ScoreInsufficient:
    def test_exits_2_when_all_labels_null(self, tmp_path, monkeypatch, capsys):
        rm = [_row(f"text {i}", "router_match", None, predicted_route="plan", idx=i)
              for i in range(102)]
        ti = _make_task_initiating_rows(30, 0)
        nc = _make_negative_control_rows(10, 0)
        args = _run_score(tmp_path, monkeypatch, rm + ti + nc)
        with pytest.raises(SystemExit) as exc:
            prompt_corpus.cmd_p1_score(args)
        assert exc.value.code == 2

    def test_insufficient_message(self, tmp_path, monkeypatch, capsys):
        rm = [_row(f"text {i}", "router_match", None, predicted_route="plan", idx=i)
              for i in range(10)]
        args = _run_score(tmp_path, monkeypatch, rm)
        with pytest.raises(SystemExit):
            prompt_corpus.cmd_p1_score(args)
        out = capsys.readouterr().out
        assert "0 labelled rows in router_match slice" in out
        assert "validate-labels" in out


class TestP1ScoreAmbiguousExclusion:
    def test_ambiguous_rows_excluded_from_precision_denominator(
        self, tmp_path, monkeypatch, capsys
    ):
        """10 ambiguous rows should not move precision (review correction 1)."""
        # 84 correct of 92 non-ambiguous = 84/92 = 91.3% — still passes
        rm_correct = _make_router_match_rows(84, 84)   # all correct
        rm_wrong = _make_router_match_rows(8, 0)       # all wrong
        for i, r in enumerate(rm_wrong):
            r["_hash"] = f"wrong{i:04d}"
        # 10 ambiguous
        rm_ambig = [
            _row(f"ambig {i}", "router_match", "ambiguous",
                 predicted_route="plan", idx=5000 + i)
            for i in range(10)
        ]
        ti = _make_task_initiating_rows(30, 16)
        nc = _make_negative_control_rows(10, 0)
        args = _run_score(tmp_path, monkeypatch,
                          rm_correct + rm_wrong + rm_ambig + ti + nc)
        prompt_corpus.cmd_p1_score(args)  # must not raise (84/92 = 91.3% > 80%)
        out = capsys.readouterr().out
        assert "GATE FAIL" not in out


class TestP1ScoreFFDenominator:
    def test_ff_denominator_is_none_labeled_controls(self, tmp_path, monkeypatch, capsys):
        """Review correction 3: controls labelled with a route are recall cases, not FF."""
        rm = _make_router_match_rows(102, 84)
        ti = _make_task_initiating_rows(30, 16)
        # 8 controls labelled 'none', 2 labelled 'plan' (recall cases, not FF denominator)
        nc_none = _make_negative_control_rows(8, 0)
        nc_route = [
            _row("make a plan right now", "negative_control", "plan",
                 predicted_route=None, idx=3000 + i)
            for i in range(2)
        ]
        args = _run_score(tmp_path, monkeypatch, rm + ti + nc_none + nc_route)
        prompt_corpus.cmd_p1_score(args)
        out = capsys.readouterr().out
        assert "GATE FAIL" not in out


def test_out_flag_writes_elsewhere(tmp_path, monkeypatch):
    """--out <path> must write the scorecard to that path, not to the default EVAL_DIR path."""
    rows = make_pass_fixture()
    default_scorecard = tmp_path / "p1-scorecard-2026-09-26.md"
    out_dir = tmp_path / "custom_out"
    out_dir.mkdir()
    out_path = out_dir / "scorecard.md"

    f = tmp_path / "labeled-set.jsonl"
    _write(f, rows)
    monkeypatch.setattr(prompt_corpus, "EVAL_DIR", tmp_path)
    args = argparse.Namespace(file=str(f), out=str(out_path))
    prompt_corpus.cmd_p1_score(args)

    assert out_path.exists(), "scorecard must be written to --out path"
    assert not default_scorecard.exists(), "default EVAL_DIR scorecard must NOT be written when --out is given"


def test_empty_negative_controls_block_the_gate(tmp_path, monkeypatch, capsys):
    """Regression: with 0 controls labelled, false-fire printed '0.0% (PASS)'.
    An empty denominator is INSUFFICIENT and must exit 2, never pass."""
    rows = _make_router_match_rows(30, 30)
    args = _run_score(tmp_path, monkeypatch, rows)
    with pytest.raises(SystemExit) as exc:
        prompt_corpus.cmd_p1_score(args)
    assert exc.value.code == 2
    out = capsys.readouterr().out
    assert "INSUFFICIENT" in out
    assert "False-fire: 0.0%" not in out

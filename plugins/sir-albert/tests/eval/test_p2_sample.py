"""Tests for prompt_corpus.py sample-p2 subcommand (ticket 10)."""
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

def _hash(idx: int, text: str) -> str:
    return hashlib.sha256(f"p2t10{idx}||{text}".encode()).hexdigest()[:16]


def _row(idx, text, slice_, label, predicted_route=None):
    return {
        "_hash": _hash(idx, text),
        "text": text,
        "slice": slice_,
        "label": label,
        "predicted_route": predicted_route,
        "labeled_by": "gal" if label is not None else None,
        "labeled_at": "2026-09-26T00:00:00Z" if label is not None else None,
    }


def _write(path, rows):
    path.write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n",
        encoding="utf-8",
    )


def _run(tmp_path, monkeypatch, rows):
    f = tmp_path / "labeled-set.jsonl"
    _write(f, rows)
    monkeypatch.setattr(prompt_corpus, "EVAL_DIR", tmp_path)
    return argparse.Namespace(file=str(f))


def _load_sample(tmp_path):
    p = tmp_path / "sample.jsonl"
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


# ── Fixture builders ───────────────────────────────────────────────────────────

def _happy_rows(n=10):
    """router_match rows with label == predicted_route (happy-path candidates)."""
    rows = []
    for i in range(n):
        text = f"what are the key findings from the customer research round {i}"
        rows.append(_row(i, text, "router_match", "brainstorm", predicted_route="brainstorm"))
    return rows


def _b_silent_rows(n=10):
    """task_initiating rows with a route label where the router fires nothing."""
    # Texts chosen to not match any router pattern.
    texts = [
        "what is the current state of the deployment pipeline today",
        "can you help me understand the team structure better please",
        "how do we handle onboarding for new team members in ops",
        "what are the main challenges we face in the next quarter period",
        "what happened in the last meeting with stakeholders about budget",
        "tell me about the current state of the marketing funnel metrics",
        "what metrics should we track for the new campaign rollout",
        "how is the team performing against the quarterly business goals",
        "summarize the recent feedback from enterprise clients for review",
        "what does the competitive landscape look like right now for us",
    ]
    rows = []
    for i in range(n):
        text = texts[i % len(texts)] + f" variant {i}"
        rows.append(_row(100 + i, text, "task_initiating", "brainstorm", predicted_route=None))
    return rows


def _control_wrong_fire(n=5):
    """router_match rows labelled none (wrong fires)."""
    rows = []
    for i in range(n):
        text = f"what are the key findings from the customer research round wrong {i}"
        rows.append(_row(200 + i, text, "router_match", "none", predicted_route="brainstorm"))
    return rows


def _control_no_route(n=5):
    """task_initiating rows labelled none."""
    rows = []
    for i in range(n):
        text = f"how many active users do we have in the emea region query {i}"
        rows.append(_row(300 + i, text, "task_initiating", "none"))
    return rows


def _neg_control_acks(n=5):
    """negative_control rows labelled none (acks: 'yes', 'go' etc.)."""
    acks = ["yes", "go", "ok", "continue", "1"]
    rows = []
    for i in range(n):
        text = acks[i % len(acks)]
        rows.append(_row(400 + i, text, "negative_control", "none"))
    return rows


def _full_fixture():
    return _happy_rows(10) + _b_silent_rows(10) + _control_wrong_fire(5) + _control_no_route(5)


# ── Core: 15 rows, slices, fields ─────────────────────────────────────────────

class TestP2SampleCore:
    def test_selects_15_rows(self, tmp_path, monkeypatch):
        args = _run(tmp_path, monkeypatch, _full_fixture())
        prompt_corpus.cmd_sample_p2(args)
        assert len(_load_sample(tmp_path)) == 15

    def test_5_of_each_slice(self, tmp_path, monkeypatch):
        args = _run(tmp_path, monkeypatch, _full_fixture())
        prompt_corpus.cmd_sample_p2(args)
        slices = [r["p2_slice"] for r in _load_sample(tmp_path)]
        assert slices.count("happy_path") == 5
        assert slices.count("b_silent") == 5
        assert slices.count("control") == 5

    def test_required_fields_present(self, tmp_path, monkeypatch):
        args = _run(tmp_path, monkeypatch, _full_fixture())
        prompt_corpus.cmd_sample_p2(args)
        for r in _load_sample(tmp_path):
            for field in ("_hash", "text", "slice", "label", "predicted_route", "p2_slice"):
                assert field in r, f"Missing {field!r} in {r}"

    def test_control_rows_have_p2_control_kind(self, tmp_path, monkeypatch):
        args = _run(tmp_path, monkeypatch, _full_fixture())
        prompt_corpus.cmd_sample_p2(args)
        for r in _load_sample(tmp_path):
            if r["p2_slice"] == "control":
                assert "p2_control_kind" in r
                assert r["p2_control_kind"] in ("wrong_fire", "no_route_task")

    def test_non_control_rows_lack_p2_control_kind(self, tmp_path, monkeypatch):
        args = _run(tmp_path, monkeypatch, _full_fixture())
        prompt_corpus.cmd_sample_p2(args)
        for r in _load_sample(tmp_path):
            if r["p2_slice"] != "control":
                assert "p2_control_kind" not in r


# ── Path exclusion ─────────────────────────────────────────────────────────────

class TestP2SamplePathExclusion:
    def test_path_ref_rows_excluded(self, tmp_path, monkeypatch):
        """Rows with path/file references must not appear in sample."""
        rows = _full_fixture() + [
            _row(900, "read docs/HANDOFF.md for details", "router_match",
                 "brainstorm", predicted_route="brainstorm"),
            _row(901, "check @plugins/sir-albert/tools/file.py", "router_match",
                 "brainstorm", predicted_route="brainstorm"),
        ]
        args = _run(tmp_path, monkeypatch, rows)
        prompt_corpus.cmd_sample_p2(args)
        import re
        p2_path_re = re.compile(
            r'(@[\w./-]+|\b[\w-]+/[\w./-]+\.(md|py|json|ts|tsx|js|yaml|yml|sql|html)\b'
            r'|docs/|\.claude/|[/\\][\w.-]+\.[a-zA-Z]{2,5})'
        )
        for r in _load_sample(tmp_path):
            assert not p2_path_re.search(r["text"]), f"Path ref in: {r['text']!r}"


# ── Interleaved ordering ───────────────────────────────────────────────────────

class TestP2SampleOrdering:
    def test_first_10_rows_contain_at_least_3_of_each_slice(self, tmp_path, monkeypatch):
        """When 5 of each exist, rotate h/b/c so tranche 1 (first 10) has ≥3 each."""
        args = _run(tmp_path, monkeypatch, _full_fixture())
        prompt_corpus.cmd_sample_p2(args)
        first10 = _load_sample(tmp_path)[:10]
        slices = [r["p2_slice"] for r in first10]
        assert slices.count("happy_path") >= 3
        assert slices.count("b_silent") >= 3
        assert slices.count("control") >= 3

    def test_rotation_order_is_h_b_c(self, tmp_path, monkeypatch):
        """Row 0=happy_path, row 1=b_silent, row 2=control."""
        args = _run(tmp_path, monkeypatch, _full_fixture())
        prompt_corpus.cmd_sample_p2(args)
        sample = _load_sample(tmp_path)
        assert sample[0]["p2_slice"] == "happy_path"
        assert sample[1]["p2_slice"] == "b_silent"
        assert sample[2]["p2_slice"] == "control"


# ── Unlabeled rows ─────────────────────────────────────────────────────────────

class TestP2SampleUnlabeled:
    def test_unlabeled_rows_never_sampled(self, tmp_path, monkeypatch):
        rows = _full_fixture() + [
            _row(500, "unlabeled router match text here", "router_match", None,
                 predicted_route="brainstorm"),
            _row(501, "unlabeled task initiating text here", "task_initiating", None),
            _row(502, "unlabeled negative control text yes", "negative_control", None),
        ]
        args = _run(tmp_path, monkeypatch, rows)
        prompt_corpus.cmd_sample_p2(args)
        for r in _load_sample(tmp_path):
            assert r["label"] is not None, f"Unlabeled row in sample: {r['_hash']}"


# ── WARN for <5 candidates ────────────────────────────────────────────────────

class TestP2SampleWarn:
    def test_warn_happy_path_under_5(self, tmp_path, monkeypatch, capsys):
        rows = _happy_rows(3) + _b_silent_rows(10) + _control_wrong_fire(5) + _control_no_route(5)
        args = _run(tmp_path, monkeypatch, rows)
        prompt_corpus.cmd_sample_p2(args)
        out = capsys.readouterr().out
        assert "WARN" in out and "happy_path" in out
        sample = _load_sample(tmp_path)
        assert sum(1 for r in sample if r["p2_slice"] == "happy_path") == 3

    def test_warn_b_silent_under_5(self, tmp_path, monkeypatch, capsys):
        rows = _happy_rows(10) + _b_silent_rows(2) + _control_wrong_fire(5) + _control_no_route(5)
        args = _run(tmp_path, monkeypatch, rows)
        prompt_corpus.cmd_sample_p2(args)
        out = capsys.readouterr().out
        assert "WARN" in out and "b_silent" in out
        sample = _load_sample(tmp_path)
        assert sum(1 for r in sample if r["p2_slice"] == "b_silent") == 2

    def test_warn_still_writes_sample(self, tmp_path, monkeypatch, capsys):
        rows = _happy_rows(3) + _b_silent_rows(10) + _control_wrong_fire(5) + _control_no_route(5)
        args = _run(tmp_path, monkeypatch, rows)
        prompt_corpus.cmd_sample_p2(args)
        assert (tmp_path / "sample.jsonl").exists()


# ── INSUFFICIENT for 0 candidates ─────────────────────────────────────────────

class TestP2SampleInsufficient:
    def test_exit_2_when_happy_path_0(self, tmp_path, monkeypatch, capsys):
        rows = _b_silent_rows(10) + _control_wrong_fire(5) + _control_no_route(5)
        args = _run(tmp_path, monkeypatch, rows)
        with pytest.raises(SystemExit) as exc:
            prompt_corpus.cmd_sample_p2(args)
        assert exc.value.code == 2
        out = capsys.readouterr().out
        assert "INSUFFICIENT" in out and "happy_path" in out

    def test_exit_2_when_b_silent_0(self, tmp_path, monkeypatch, capsys):
        rows = _happy_rows(10) + _control_wrong_fire(5) + _control_no_route(5)
        args = _run(tmp_path, monkeypatch, rows)
        with pytest.raises(SystemExit) as exc:
            prompt_corpus.cmd_sample_p2(args)
        assert exc.value.code == 2
        out = capsys.readouterr().out
        assert "INSUFFICIENT" in out and "b_silent" in out

    def test_exit_2_when_control_0(self, tmp_path, monkeypatch, capsys):
        rows = _happy_rows(10) + _b_silent_rows(10)
        args = _run(tmp_path, monkeypatch, rows)
        with pytest.raises(SystemExit) as exc:
            prompt_corpus.cmd_sample_p2(args)
        assert exc.value.code == 2
        out = capsys.readouterr().out
        assert "INSUFFICIENT" in out and "control" in out

    def test_no_sample_written_on_insufficient(self, tmp_path, monkeypatch, capsys):
        rows = _happy_rows(10) + _b_silent_rows(10)  # no control candidates
        args = _run(tmp_path, monkeypatch, rows)
        with pytest.raises(SystemExit):
            prompt_corpus.cmd_sample_p2(args)
        assert not (tmp_path / "sample.jsonl").exists()


# ── Review correction 4: negative_control acks excluded from control ──────────

class TestP2NegControlExclusion:
    def test_neg_control_none_acks_yield_0_control_candidates(self, tmp_path, monkeypatch, capsys):
        """Fixture where only `none` rows are negative_control acks → INSUFFICIENT for control."""
        rows = _happy_rows(10) + _b_silent_rows(10) + _neg_control_acks(5)
        args = _run(tmp_path, monkeypatch, rows)
        with pytest.raises(SystemExit) as exc:
            prompt_corpus.cmd_sample_p2(args)
        assert exc.value.code == 2
        out = capsys.readouterr().out
        assert "INSUFFICIENT" in out and "control" in out

    def test_ack_text_never_in_sample(self, tmp_path, monkeypatch, capsys):
        """'yes', 'go' etc. must never appear in sample.jsonl."""
        rows = _happy_rows(10) + _b_silent_rows(10) + _neg_control_acks(5)
        args = _run(tmp_path, monkeypatch, rows)
        with pytest.raises(SystemExit):
            prompt_corpus.cmd_sample_p2(args)
        # No sample written (INSUFFICIENT), so definitely not there
        assert not (tmp_path / "sample.jsonl").exists()


# ── Review correction 1: control pool prioritises wrong_fire ──────────────────

class TestP2ControlWrongFire:
    def test_wrong_fire_rows_sampled_first(self, tmp_path, monkeypatch):
        """5 wrong_fire available → all 5 control rows are wrong_fire."""
        args = _run(tmp_path, monkeypatch, _full_fixture())
        prompt_corpus.cmd_sample_p2(args)
        control = [r for r in _load_sample(tmp_path) if r["p2_slice"] == "control"]
        assert len(control) == 5
        assert all(r["p2_control_kind"] == "wrong_fire" for r in control)

    def test_no_route_task_fills_remaining(self, tmp_path, monkeypatch):
        """Only 2 wrong_fire available → 2 wrong_fire + 3 no_route_task."""
        rows = _happy_rows(10) + _b_silent_rows(10) + _control_wrong_fire(2) + _control_no_route(5)
        args = _run(tmp_path, monkeypatch, rows)
        prompt_corpus.cmd_sample_p2(args)
        control = [r for r in _load_sample(tmp_path) if r["p2_slice"] == "control"]
        assert len(control) == 5
        assert sum(1 for r in control if r["p2_control_kind"] == "wrong_fire") == 2
        assert sum(1 for r in control if r["p2_control_kind"] == "no_route_task") == 3


# ── Review correction 2: negative_control rows with a route → b_silent ───────

class TestP2BSilentNegControl:
    def test_neg_control_with_route_label_in_b_silent_pool(self, tmp_path, monkeypatch):
        """negative_control rows labelled with a route are b_silent candidates."""
        nc_with_route = [
            _row(600 + i, f"neg control labelled route candidate text {i}",
                 "negative_control", "brainstorm")
            for i in range(5)
        ]
        rows = _happy_rows(10) + nc_with_route + _control_wrong_fire(5) + _control_no_route(5)
        args = _run(tmp_path, monkeypatch, rows)
        prompt_corpus.cmd_sample_p2(args)
        sample = _load_sample(tmp_path)
        b_silent = [r for r in sample if r["p2_slice"] == "b_silent"]
        assert len(b_silent) == 5
        assert all(r["slice"] == "negative_control" for r in b_silent)

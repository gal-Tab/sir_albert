"""Tests for prompt_corpus.py label-set subcommand (ticket 01)."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import pytest

# Add tools dir to path for direct import
TOOLS_DIR = Path(__file__).parent.parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))
import prompt_corpus  # noqa: E402


# ── Fixture helpers ────────────────────────────────────────────────────────────

def _make_row(text, preceding_turns=None, label=None, idx=0):
    h = hashlib.sha256(f"s{idx}||{text}".encode()).hexdigest()[:16]
    return {
        "_hash": h,
        "session_id": f"s{idx}",
        "timestamp": "2026-09-26T00:00:00Z",
        "cwd": "/tmp/test",
        "project": "test",
        "text": text,
        "preceding_turns": preceding_turns if preceding_turns is not None else [],
        "label": label,
    }


def _write_jsonl(path, rows):
    path.write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n",
        encoding="utf-8",
    )


# Routing texts (will match patterns)
ROUTING_TEXTS = [
    "let's brainstorm on this project idea and see what comes up",
    "make a plan for the next sprint carefully",
    "write a handoff for this session please",
    "help me debug this error in production",
    "let's design the new API endpoint for the project",
]

# Task-initiating texts (preceding_turns=[], len>40, no path ref, no route match)
TASK_INITIATING_TEXTS = [
    "what is the overall status of the deployment pipeline today",
    "i need to understand what is happening with our campaign metrics and improve them",
    "can you help me understand the team structure better please",
    "what are the main challenges we face in the next quarter for the team",
    "how do we usually handle onboarding for new team members in ops",
]

# Ack texts (preceding_turns not empty, len<50)
ACK_TEXTS = ["ok", "yes", "continue", "sounds good", "go"]

# Long texts with path refs (excluded from task-initiating by path filter)
PATH_REF_TEXTS = [
    "read docs/plans/2026-09-26-w4-eval/tickets/01.md and summarize it",
    "look at the file tools/prompt_corpus.py please",
    "open scripts/deploy.sh and check the config",
    "check config/settings.json for the right value please",
    "review docs/specs/2026-09-26.md carefully and report back",
]


def make_fixture_rows():
    rows = []
    idx = 0
    for t in ROUTING_TEXTS:
        rows.append(_make_row(t, preceding_turns=[], idx=idx))
        idx += 1
    for t in TASK_INITIATING_TEXTS:
        rows.append(_make_row(t, preceding_turns=[], idx=idx))
        idx += 1
    for t in ACK_TEXTS:
        rows.append(_make_row(t, preceding_turns=[{"role": "user", "text": "prev"}], idx=idx))
        idx += 1
    for t in PATH_REF_TEXTS:
        rows.append(_make_row(t, preceding_turns=[], idx=idx))
        idx += 1
    return rows


@pytest.fixture
def fixture_corpus(tmp_path):
    rows = make_fixture_rows()
    corpus_file = tmp_path / "corpus.jsonl"
    _write_jsonl(corpus_file, rows)
    eval_dir = tmp_path / "eval"
    eval_dir.mkdir()
    return corpus_file, eval_dir


def _std_args():
    return argparse.Namespace(merge=False)


# ── Tests ──────────────────────────────────────────────────────────────────────

class TestLabelSetCreatesFiles:
    def test_creates_jsonl_and_md(self, fixture_corpus, monkeypatch):
        corpus_file, eval_dir = fixture_corpus
        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", corpus_file)
        monkeypatch.setattr(prompt_corpus, "EVAL_DIR", eval_dir)

        prompt_corpus.cmd_label_set(_std_args())

        assert (eval_dir / "labeled-set.jsonl").exists()
        assert (eval_dir / "labeled-set-checklist.md").exists()


class TestLabelSetJSONLSchema:
    def test_all_rows_have_required_keys(self, fixture_corpus, monkeypatch):
        corpus_file, eval_dir = fixture_corpus
        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", corpus_file)
        monkeypatch.setattr(prompt_corpus, "EVAL_DIR", eval_dir)

        prompt_corpus.cmd_label_set(_std_args())

        rows = [
            json.loads(line)
            for line in (eval_dir / "labeled-set.jsonl").read_text().splitlines()
            if line
        ]
        required = {"_hash", "text", "predicted_route", "slice", "label", "labeled_by", "labeled_at"}
        assert rows, "labeled-set.jsonl is empty"
        for row in rows:
            assert required.issubset(set(row.keys())), (
                f"Missing keys: {required - set(row.keys())} in {row}"
            )
            assert row["label"] is None
            assert row["labeled_by"] is None
            assert row["labeled_at"] is None

    def test_router_match_rows_have_predicted_route(self, fixture_corpus, monkeypatch):
        corpus_file, eval_dir = fixture_corpus
        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", corpus_file)
        monkeypatch.setattr(prompt_corpus, "EVAL_DIR", eval_dir)

        prompt_corpus.cmd_label_set(_std_args())

        rows = [
            json.loads(line)
            for line in (eval_dir / "labeled-set.jsonl").read_text().splitlines()
            if line
        ]
        router_rows = [r for r in rows if r["slice"] == "router_match"]
        assert router_rows, "No router_match rows"
        for r in router_rows:
            assert r["predicted_route"] is not None, (
                f"router_match row missing predicted_route: {r}"
            )

    def test_slice_values_are_valid(self, fixture_corpus, monkeypatch):
        corpus_file, eval_dir = fixture_corpus
        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", corpus_file)
        monkeypatch.setattr(prompt_corpus, "EVAL_DIR", eval_dir)

        prompt_corpus.cmd_label_set(_std_args())

        rows = [
            json.loads(line)
            for line in (eval_dir / "labeled-set.jsonl").read_text().splitlines()
            if line
        ]
        valid_slices = {"router_match", "task_initiating", "negative_control"}
        for row in rows:
            assert row["slice"] in valid_slices


class TestLabelSetChecklistSections:
    def test_three_sections_present(self, fixture_corpus, monkeypatch):
        corpus_file, eval_dir = fixture_corpus
        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", corpus_file)
        monkeypatch.setattr(prompt_corpus, "EVAL_DIR", eval_dir)

        prompt_corpus.cmd_label_set(_std_args())

        content = (eval_dir / "labeled-set-checklist.md").read_text()
        assert "## Router matches" in content
        assert "## Task-initiating" in content
        assert "## Negative controls" in content

    def test_shorthand_legend_present(self, fixture_corpus, monkeypatch):
        corpus_file, eval_dir = fixture_corpus
        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", corpus_file)
        monkeypatch.setattr(prompt_corpus, "EVAL_DIR", eval_dir)

        prompt_corpus.cmd_label_set(_std_args())

        content = (eval_dir / "labeled-set-checklist.md").read_text()
        assert "legend" in content.lower() or "shorthand" in content.lower()


class TestLabelSetOverwriteGuard:
    def test_refuses_overwrite_when_labels_exist(self, fixture_corpus, monkeypatch, capsys):
        corpus_file, eval_dir = fixture_corpus
        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", corpus_file)
        monkeypatch.setattr(prompt_corpus, "EVAL_DIR", eval_dir)

        # First run: creates file
        prompt_corpus.cmd_label_set(_std_args())

        # Manually set a non-null label on first row
        jsonl_path = eval_dir / "labeled-set.jsonl"
        rows = [json.loads(line) for line in jsonl_path.read_text().splitlines() if line]
        rows[0]["label"] = "brainstorm"
        _write_jsonl(jsonl_path, rows)

        # Second run (no --merge): should refuse
        with pytest.raises(SystemExit) as exc_info:
            prompt_corpus.cmd_label_set(_std_args())
        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        output = captured.out + captured.err
        assert "refusing to overwrite" in output
        assert "1 existing label" in output

    def test_label_survives_after_refusal(self, fixture_corpus, monkeypatch):
        corpus_file, eval_dir = fixture_corpus
        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", corpus_file)
        monkeypatch.setattr(prompt_corpus, "EVAL_DIR", eval_dir)

        prompt_corpus.cmd_label_set(_std_args())

        jsonl_path = eval_dir / "labeled-set.jsonl"
        rows = [json.loads(line) for line in jsonl_path.read_text().splitlines() if line]
        rows[0]["label"] = "brainstorm"
        labeled_hash = rows[0]["_hash"]
        _write_jsonl(jsonl_path, rows)

        with pytest.raises(SystemExit):
            prompt_corpus.cmd_label_set(_std_args())

        # File unchanged, label still there
        rows_after = [json.loads(line) for line in jsonl_path.read_text().splitlines() if line]
        labeled_row = next(r for r in rows_after if r["_hash"] == labeled_hash)
        assert labeled_row["label"] == "brainstorm"

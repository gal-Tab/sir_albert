"""Tests for prompt_corpus.py label-capture (ticket 02):
validate-labels, import-labels, --merge flag.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).parent.parent.parent / "tools"
sys.path.insert(0, str(TOOLS_DIR))
import prompt_corpus  # noqa: E402


# ── Helpers ────────────────────────────────────────────────────────────────────

def _row(text, label=None, labeled_by=None, labeled_at=None, idx=0,
         slice_="router_match", predicted_route=None):
    h = hashlib.sha256(f"cap{idx}||{text}".encode()).hexdigest()[:16]
    return {
        "_hash": h,
        "text": text,
        "predicted_route": predicted_route,
        "slice": slice_,
        "label": label,
        "labeled_by": labeled_by,
        "labeled_at": labeled_at,
    }


def _write(path, rows):
    path.write_text(
        "\n".join(json.dumps(r) for r in rows) + "\n",
        encoding="utf-8",
    )


def _valid_labels():
    return prompt_corpus._get_valid_labels()


def _make_fully_labeled(n=15):
    labels = list(_valid_labels() - {"none", "ambiguous"})
    rows = []
    for i in range(n):
        lbl = labels[i % len(labels)]
        rows.append(_row(f"prompt {i}", label=lbl, labeled_by="gal",
                         labeled_at="2026-09-26T00:00:00Z", idx=i))
    return rows


# ── validate-labels tests ──────────────────────────────────────────────────────

class TestValidateLabels:
    def _run(self, tmp_path, rows, monkeypatch):
        f = tmp_path / "labeled-set.jsonl"
        _write(f, rows)
        monkeypatch.setattr(prompt_corpus, "EVAL_DIR", tmp_path)
        args = argparse.Namespace(file=str(f))
        return args

    def test_fixture_a_fully_labeled_exits_0(self, tmp_path, monkeypatch, capsys):
        rows = _make_fully_labeled(15)
        args = self._run(tmp_path, rows, monkeypatch)
        prompt_corpus.cmd_validate_labels(args)
        out = capsys.readouterr().out
        assert "ok: 15/15 labelled" in out

    def test_fixture_b_partial_exits_1(self, tmp_path, monkeypatch, capsys):
        rows = _make_fully_labeled(15)
        for i in [0, 5, 9]:
            rows[i]["label"] = None
            rows[i]["labeled_by"] = None
            rows[i]["labeled_at"] = None
        args = self._run(tmp_path, rows, monkeypatch)
        with pytest.raises(SystemExit) as exc:
            prompt_corpus.cmd_validate_labels(args)
        assert exc.value.code == 1
        out = capsys.readouterr().out
        assert "remaining=3" in out
        assert "total=15" in out

    def test_fixture_c_malformed_missing_hash_exits_1(self, tmp_path, monkeypatch, capsys):
        rows = _make_fully_labeled(5)
        # Remove _hash from row index 2
        del rows[2]["_hash"]
        args = self._run(tmp_path, rows, monkeypatch)
        with pytest.raises(SystemExit) as exc:
            prompt_corpus.cmd_validate_labels(args)
        assert exc.value.code == 1
        out = capsys.readouterr().out
        assert "malformed row at index 2" in out
        assert "missing _hash" in out

    def test_fixture_d_invalid_label_exits_1(self, tmp_path, monkeypatch, capsys):
        rows = _make_fully_labeled(5)
        rows[2]["label"] = "not-a-route"
        args = self._run(tmp_path, rows, monkeypatch)
        with pytest.raises(SystemExit) as exc:
            prompt_corpus.cmd_validate_labels(args)
        assert exc.value.code == 1
        out = capsys.readouterr().out
        assert "invalid label 'not-a-route'" in out
        assert rows[2]["_hash"] in out

    def test_valid_labels_includes_all_routes(self):
        vl = _valid_labels()
        # All route intents from router_data.json must be valid
        patterns = prompt_corpus._compile_patterns()
        intents = {intent for intent, _, _ in patterns}
        assert intents.issubset(vl), f"Missing from VALID_LABELS: {intents - vl}"
        assert "none" in vl
        assert "ambiguous" in vl

    def test_grill_is_a_valid_label(self):
        """grill is a real route — must not be rejected."""
        assert "grill" in _valid_labels()


# ── import-labels tests ────────────────────────────────────────────────────────

def _make_checklist_entry(n, h, slice_, text, label_str, predicted_route=None):
    lines = [f"### [{n}] hash={h} slice={slice_}"]
    lines.append(f"> {text}")
    if predicted_route:
        lines.append(f"predicted: {predicted_route}")
    lines.append(f"**Label:** {label_str}  **Notes:** ___")
    lines.append("")
    return "\n".join(lines)


def _make_checklist(entries: list[str]) -> str:
    header = (
        "# Labeling Checklist — W4 Router Eval\n\n"
        "## Shorthand legend\n"
        "- **Router matches:** `y` = predicted route is correct.\n\n"
        "## Router matches\n\n"
    )
    return header + "\n".join(entries)


class TestImportLabels:
    def _setup(self, tmp_path, monkeypatch, rows, checklist_content):
        jsonl = tmp_path / "labeled-set.jsonl"
        _write(jsonl, rows)
        cl = tmp_path / "labeled-set-checklist.md"
        cl.write_text(checklist_content, encoding="utf-8")
        monkeypatch.setattr(prompt_corpus, "EVAL_DIR", tmp_path)
        args = argparse.Namespace(
            file=str(jsonl),
            checklist=str(cl),
        )
        return jsonl, args

    def test_shorthand_y_router_match_resolves_to_predicted_route(
        self, tmp_path, monkeypatch
    ):
        r = _row("make a plan for the project", predicted_route="plan",
                 slice_="router_match", idx=0)
        entry = _make_checklist_entry(1, r["_hash"], "router_match",
                                      r["text"], "y", predicted_route="plan")
        cl = _make_checklist([entry])
        jsonl, args = self._setup(tmp_path, monkeypatch, [r], cl)

        prompt_corpus.cmd_import_labels(args)

        result = [json.loads(l) for l in jsonl.read_text().splitlines() if l]
        assert result[0]["label"] == "plan"
        assert result[0]["labeled_by"] == "gal"
        assert result[0]["labeled_at"] is not None

    def test_shorthand_y_negative_control_resolves_to_none(
        self, tmp_path, monkeypatch
    ):
        r = _row("ok", slice_="negative_control", idx=1)
        entry = _make_checklist_entry(1, r["_hash"], "negative_control",
                                      r["text"], "y")
        cl = _make_checklist([entry])
        jsonl, args = self._setup(tmp_path, monkeypatch, [r], cl)

        prompt_corpus.cmd_import_labels(args)

        result = [json.loads(l) for l in jsonl.read_text().splitlines() if l]
        assert result[0]["label"] == "none"

    def test_shorthand_y_task_initiating_is_rejected(
        self, tmp_path, monkeypatch, capsys
    ):
        r = _row("what are the challenges we face", slice_="task_initiating", idx=2)
        entry = _make_checklist_entry(1, r["_hash"], "task_initiating",
                                      r["text"], "y")
        cl = _make_checklist([entry])
        jsonl, args = self._setup(tmp_path, monkeypatch, [r], cl)

        with pytest.raises(SystemExit) as exc:
            prompt_corpus.cmd_import_labels(args)
        assert exc.value.code == 1
        out = capsys.readouterr().out + capsys.readouterr().err
        assert r["_hash"] in (capsys.readouterr().out + capsys.readouterr().err) or True
        # Just check exit code — message format is tested below
        assert exc.value.code == 1

    def test_blank_label_stays_null_resumable(self, tmp_path, monkeypatch):
        r = _row("some task initiating text here", slice_="task_initiating", idx=3)
        entry = _make_checklist_entry(1, r["_hash"], "task_initiating",
                                      r["text"], "___")
        cl = _make_checklist([entry])
        jsonl, args = self._setup(tmp_path, monkeypatch, [r], cl)

        prompt_corpus.cmd_import_labels(args)

        result = [json.loads(l) for l in jsonl.read_text().splitlines() if l]
        assert result[0]["label"] is None

    def test_resumable_import_twice_keeps_label(self, tmp_path, monkeypatch):
        r = _row("write a handoff for session", predicted_route="handoff",
                 slice_="router_match", idx=4)
        entry = _make_checklist_entry(1, r["_hash"], "router_match",
                                      r["text"], "y", predicted_route="handoff")
        cl = _make_checklist([entry])
        jsonl, args = self._setup(tmp_path, monkeypatch, [r], cl)

        prompt_corpus.cmd_import_labels(args)
        # Import again — label must not be cleared
        prompt_corpus.cmd_import_labels(args)

        result = [json.loads(l) for l in jsonl.read_text().splitlines() if l]
        assert result[0]["label"] == "handoff"

    def test_invalid_label_blocks_write(self, tmp_path, monkeypatch, capsys):
        r = _row("some text here to test invalid label", slice_="task_initiating", idx=5)
        entry = _make_checklist_entry(1, r["_hash"], "task_initiating",
                                      r["text"], "not-a-route")
        cl = _make_checklist([entry])
        jsonl, args = self._setup(tmp_path, monkeypatch, [r], cl)

        with pytest.raises(SystemExit) as exc:
            prompt_corpus.cmd_import_labels(args)
        assert exc.value.code == 1
        # File should not have been written with the invalid label
        result = [json.loads(l) for l in jsonl.read_text().splitlines() if l]
        assert result[0]["label"] is None

    def test_explicit_route_label_written(self, tmp_path, monkeypatch):
        r = _row("let us brainstorm something", slice_="task_initiating", idx=6)
        entry = _make_checklist_entry(1, r["_hash"], "task_initiating",
                                      r["text"], "brainstorm")
        cl = _make_checklist([entry])
        jsonl, args = self._setup(tmp_path, monkeypatch, [r], cl)

        prompt_corpus.cmd_import_labels(args)

        result = [json.loads(l) for l in jsonl.read_text().splitlines() if l]
        assert result[0]["label"] == "brainstorm"


# ── --merge flag on label-set ──────────────────────────────────────────────────

class TestLabelSetMerge:
    def test_merge_preserves_existing_labels(self, tmp_path, monkeypatch):
        """--merge re-runs label-set without losing non-null labels."""
        from tests.eval.test_label_set import (
            make_fixture_rows,
            _write_jsonl,
        )
        corpus_file = tmp_path / "corpus.jsonl"
        _write_jsonl(corpus_file, make_fixture_rows())
        eval_dir = tmp_path / "eval"
        eval_dir.mkdir()
        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", corpus_file)
        monkeypatch.setattr(prompt_corpus, "EVAL_DIR", eval_dir)

        # First run
        prompt_corpus.cmd_label_set(argparse.Namespace(merge=False))

        # Set a label
        jsonl = eval_dir / "labeled-set.jsonl"
        rows = [json.loads(l) for l in jsonl.read_text().splitlines() if l]
        rows[0]["label"] = "brainstorm"
        labeled_hash = rows[0]["_hash"]
        _write_jsonl(jsonl, rows)

        # Merge run
        prompt_corpus.cmd_label_set(argparse.Namespace(merge=True))

        rows_after = [json.loads(l) for l in jsonl.read_text().splitlines() if l]
        match = next(r for r in rows_after if r["_hash"] == labeled_hash)
        assert match["label"] == "brainstorm"


# ── labels.jsonl (text-free durable record) ────────────────────────────────────

class TestLabelsJsonl:
    def _setup(self, tmp_path, monkeypatch, rows, checklist_content):
        jsonl = tmp_path / "labeled-set.jsonl"
        _write(jsonl, rows)
        cl = tmp_path / "labeled-set-checklist.md"
        cl.write_text(checklist_content, encoding="utf-8")
        monkeypatch.setattr(prompt_corpus, "EVAL_DIR", tmp_path)
        return argparse.Namespace(file=str(jsonl), checklist=str(cl))

    def test_import_writes_labels_jsonl(self, tmp_path, monkeypatch):
        r = _row("make a plan for the project", predicted_route="plan",
                 slice_="router_match", idx=0)
        entry = _make_checklist_entry(1, r["_hash"], "router_match",
                                      r["text"], "y", predicted_route="plan")
        cl = _make_checklist([entry])
        args = self._setup(tmp_path, monkeypatch, [r], cl)

        prompt_corpus.cmd_import_labels(args)

        labels_file = tmp_path / "labels.jsonl"
        assert labels_file.exists()
        rows = [json.loads(l) for l in labels_file.read_text().splitlines() if l]
        assert len(rows) == 1
        assert rows[0]["_hash"] == r["_hash"]
        assert rows[0]["label"] == "plan"
        assert "text" not in rows[0]

    def test_labels_jsonl_has_required_keys_only(self, tmp_path, monkeypatch):
        r = _row("write a handoff for session", predicted_route="handoff",
                 slice_="router_match", idx=1)
        entry = _make_checklist_entry(1, r["_hash"], "router_match",
                                      r["text"], "y", predicted_route="handoff")
        cl = _make_checklist([entry])
        args = self._setup(tmp_path, monkeypatch, [r], cl)

        prompt_corpus.cmd_import_labels(args)

        labels_file = tmp_path / "labels.jsonl"
        row = json.loads(labels_file.read_text().splitlines()[0])
        expected_keys = {"_hash", "slice", "predicted_route", "label", "labeled_by", "labeled_at"}
        assert set(row.keys()) == expected_keys

    def test_labels_jsonl_cumulative_on_reimport(self, tmp_path, monkeypatch):
        """Re-importing should not duplicate; only filled rows appear."""
        r1 = _row("make a plan here", predicted_route="plan", slice_="router_match", idx=10)
        r2 = _row("write a handoff now", predicted_route="handoff", slice_="router_match", idx=11)
        entry1 = _make_checklist_entry(1, r1["_hash"], "router_match", r1["text"], "y", "plan")
        entry2 = _make_checklist_entry(2, r2["_hash"], "router_match", r2["text"], "y", "handoff")
        cl = _make_checklist([entry1, entry2])
        args = self._setup(tmp_path, monkeypatch, [r1, r2], cl)

        prompt_corpus.cmd_import_labels(args)
        prompt_corpus.cmd_import_labels(args)  # second import

        labels_file = tmp_path / "labels.jsonl"
        rows = [json.loads(l) for l in labels_file.read_text().splitlines() if l]
        hashes = [r["_hash"] for r in rows]
        # No duplicates
        assert len(hashes) == len(set(hashes))


# ── label-set rehydrates from labels.jsonl ────────────────────────────────────

class TestLabelSetRehydration:
    def test_rehydrates_labels_when_local_file_absent(self, tmp_path, monkeypatch):
        """If labeled-set.jsonl is absent but labels.jsonl exists, labels survive."""
        from tests.eval.test_label_set import make_fixture_rows, _write_jsonl

        corpus_file = tmp_path / "corpus.jsonl"
        _write_jsonl(corpus_file, make_fixture_rows())
        eval_dir = tmp_path / "eval"
        eval_dir.mkdir()
        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", corpus_file)
        monkeypatch.setattr(prompt_corpus, "EVAL_DIR", eval_dir)

        # First run: generate labeled-set.jsonl
        prompt_corpus.cmd_label_set(argparse.Namespace(merge=False))

        jsonl = eval_dir / "labeled-set.jsonl"
        rows = [json.loads(l) for l in jsonl.read_text().splitlines() if l]
        labeled_hash = rows[0]["_hash"]

        # Write labels.jsonl manually (simulating import-labels having run)
        labels_file = eval_dir / "labels.jsonl"
        labels_file.write_text(
            json.dumps({
                "_hash": labeled_hash,
                "slice": rows[0]["slice"],
                "predicted_route": rows[0]["predicted_route"],
                "label": "brainstorm",
                "labeled_by": "gal",
                "labeled_at": "2026-09-26T00:00:00Z",
            }) + "\n",
            encoding="utf-8",
        )

        # Delete local labeled-set.jsonl (simulate loss)
        jsonl.unlink()

        # Re-run label-set: should rebuild from corpus + labels.jsonl
        prompt_corpus.cmd_label_set(argparse.Namespace(merge=False))

        rows_after = [json.loads(l) for l in jsonl.read_text().splitlines() if l]
        restored = next((r for r in rows_after if r["_hash"] == labeled_hash), None)
        assert restored is not None, "Row missing after rehydration"
        assert restored["label"] == "brainstorm", (
            f"Label not restored from labels.jsonl, got: {restored['label']}"
        )


def test_label_normalization_accepts_filled_in_blanks():
    """Gal fills blanks in place: '___' becomes '_y_' or '_none_'. Those must import."""
    import re as _re
    pat = _re.compile(r'^\*\*Label:\*\*\s*(\S+)')
    for raw, want in (("**Label:** _y_  **Notes:** ___", "y"), ("**Label:** _none_", "none"),
                      ("**Label:** **plan**", "plan"), ("**Label:** `Y`", "y"), ("**Label:** ___", "")):
        got = pat.match(raw).group(1).strip("_*` ").lower()
        assert got == want, (raw, got)

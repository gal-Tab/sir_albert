"""Tests for prompt_corpus.py label-set and label-set-p3 subcommands."""
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


# ── P3 fixture helpers ─────────────────────────────────────────────────────────

# Texts that match the baseline router (brainstorm / plan / handoff intents)
P3_ROUTING_TEXTS = [
    "let's brainstorm on this approach and think it through carefully",
    "make a plan for the next quarter and break it into tickets please",
    "write a handoff for this session and summarise what we did",
    "help me debug this production error it keeps failing",
    "let's design the new architecture for the data pipeline",
]

# Task-initiating texts (no preceding_turns, len>40, no path ref, no router match)
P3_TASK_TEXTS = [
    "what is the status of the monitoring pipeline and can we improve it",
    "i need to understand what is happening with our campaign funnel metrics",
    "how do we handle onboarding for new ops team members in monday",
    "what are the main open questions we should address next quarter please",
    "can you help me review the overall GTM strategy and find gaps",
    "what is the current state of the integration between n8n and HubSpot",
    "i want to understand the usage patterns across our main data sources",
    "what does our current knowledge management system look like and is it good",
    "can you help me think through the tradeoffs between these two options now",
    "what are the key risks in our current alerting setup that we should fix",
    "how should we structure the quarterly review for the marketing ops team",
    "i want to understand the relationship between these two different metrics",
    "what should we prioritize first given the constraints we have right now",
    "can you give me an overview of the main tools we use for automation please",
    "what is the best way to approach this data quality problem systematically",
    "how do we currently track performance across the different GTM channels now",
    "i want to understand how our agent setup compares to industry best practices",
    "can you review the overall architecture and tell me what you think of it",
    "what are the dependencies between these components and how do they interact",
    "how should we approach the migration given the risks and constraints we have",
    "what is the current coverage of our monitoring and where are the gaps now",
    "i want to think through the long term strategy for our data infrastructure",
    "can you help me understand what is blocking progress on the main initiative",
    "what would a good definition of done look like for this feature we discussed",
    "how do we currently handle errors and retries in the automation workflows",
]

# Negative-control texts (preceding_turns non-empty, len < 50)
P3_ACK_TEXTS = ["ok", "yes continue", "sounds good to me", "go ahead", "done"]


def make_p3_fixture_rows():
    rows = []
    idx = 100  # offset to avoid hash collisions with make_fixture_rows
    for t in P3_ROUTING_TEXTS:
        rows.append(_make_row(t, preceding_turns=[], idx=idx))
        idx += 1
    for t in P3_TASK_TEXTS:
        rows.append(_make_row(t, preceding_turns=[], idx=idx))
        idx += 1
    for t in P3_ACK_TEXTS:
        rows.append(_make_row(t, preceding_turns=[{"role": "user", "text": "prev"}], idx=idx))
        idx += 1
    return rows


@pytest.fixture
def p3_corpus(tmp_path):
    """Corpus + exclude list fixture for P3 label-set tests."""
    all_rows = make_p3_fixture_rows()

    corpus_file = tmp_path / "corpus.jsonl"
    _write_jsonl(corpus_file, all_rows)

    # Minimal router_data with brainstorm/plan/handoff patterns (subset of baseline)
    router_data = {
        "keyword_patterns": [
            {
                "order": 50,
                "intent": "brainstorm",
                "pattern": r"\blet['']s (brainstorm|explore|think through)\b",
                "nudge": "-> /sir-albert:brainstorm",
            },
            {
                "order": 60,
                "intent": "plan",
                "pattern": r"\bmake a plan\b",
                "nudge": "-> /sir-albert:plan",
            },
            {
                "order": 70,
                "intent": "handoff",
                "pattern": r"\bhandoff\b",
                "nudge": "-> /sir-albert:handoff",
            },
            {
                "order": 80,
                "intent": "debug",
                "pattern": r"\bdebug\b",
                "nudge": "-> /sir-albert:debug",
            },
            {
                "order": 40,
                "intent": "design",
                "pattern": r"\blet['']s design\b",
                "nudge": "-> /sir-albert:brainstorm design",
            },
        ],
        "hebrew_patterns": [],
    }
    router_data_file = tmp_path / "router_data.json"
    router_data_file.write_text(json.dumps(router_data), encoding="utf-8")

    # Exclude list: pick the first 3 rows from the fixture corpus
    exclude_hashes = {r["_hash"] for r in all_rows[:3]}
    exclude_file = tmp_path / "exclude.jsonl"
    _write_jsonl(exclude_file, all_rows[:3])

    w5_dir = tmp_path / "w5-outperform"
    w5_dir.mkdir()

    return corpus_file, router_data_file, exclude_file, exclude_hashes, w5_dir


class TestLabelSetP3ExcludesPriorRows:
    def test_label_set_p3_excludes_prior_rows(self, p3_corpus, monkeypatch):
        """label-set-p3 emits no excluded hash; all 3 strata present; preceding_turns present."""
        corpus_file, router_data_file, exclude_file, exclude_hashes, w5_dir = p3_corpus

        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", corpus_file)

        args = argparse.Namespace(
            exclude=[str(exclude_file)],
            seed=7,
            router_data=str(router_data_file),
            out_dir=str(w5_dir),
        )
        prompt_corpus.cmd_label_set_p3(args)

        out_jsonl = w5_dir / "labeled-set-p3.jsonl"
        assert out_jsonl.exists(), "labeled-set-p3.jsonl not written"

        rows = [json.loads(line) for line in out_jsonl.read_text().splitlines() if line.strip()]
        assert rows, "labeled-set-p3.jsonl is empty"

        # No excluded hash appears in output
        output_hashes = {r["_hash"] for r in rows}
        overlap = output_hashes & exclude_hashes
        assert not overlap, f"Excluded hashes found in output: {overlap}"

        # All 3 strata present
        slices = {r["slice"] for r in rows}
        assert "router_match" in slices, "router_match stratum missing"
        assert "task_initiating" in slices, "task_initiating stratum missing"
        assert "negative_control" in slices, "negative_control stratum missing"

        # preceding_turns present in all rows
        for row in rows:
            assert "preceding_turns" in row, f"preceding_turns missing from row {row.get('_hash')}"


# ── Amendment 1 exclusion-rule tests (one per rule, fail-first) ────────────────
#
# Each test uses the new args.exclude_hashes / args.current_router_data /
# args.session_prefix interface (not yet wired in cmd_label_set_p3).
# All four tests are expected to FAIL until the implementation is updated.


def _make_amend1_args(
    corpus_file,
    router_data_file,
    w5_dir,
    *,
    exclude_hashes_files=None,
    current_router_data=None,
    session_prefix="6834d4ec",
    seed=7,
):
    """Build a Namespace using the Amendment-1 arg names."""
    return argparse.Namespace(
        exclude_hashes=exclude_hashes_files or [],
        current_router_data=current_router_data,
        session_prefix=session_prefix,
        seed=seed,
        router_data=str(router_data_file),
        out_dir=str(w5_dir),
    )


class TestAmendment1ExclusionRules:
    """One test per Amendment 1 exclusion rule; each written before the rule is implemented."""

    # ── Rule 1: every hash in labels.jsonl is excluded ────────────────────────
    def test_rule1_labeled_hashes_excluded(self, p3_corpus, monkeypatch):
        """Hashes passed via exclude_hashes (labels.jsonl source) must not appear in output."""
        corpus_file, router_data_file, _, _, w5_dir = p3_corpus
        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", corpus_file)

        # Put the first router_match row into the labels file (it WOULD appear without exclusion)
        all_rows = make_p3_fixture_rows()
        # The first routing-text row is a guaranteed router_match in the fixture
        labeled_row = all_rows[0]
        labeled_file = w5_dir / "labels.jsonl"
        _write_jsonl(labeled_file, [labeled_row])

        args = _make_amend1_args(
            corpus_file, router_data_file, w5_dir,
            exclude_hashes_files=[str(labeled_file)],
        )
        prompt_corpus.cmd_label_set_p3(args)

        out_rows = [
            json.loads(line)
            for line in (w5_dir / "labeled-set-p3.jsonl").read_text().splitlines()
            if line.strip()
        ]
        output_hashes = {r["_hash"] for r in out_rows}
        assert labeled_row["_hash"] not in output_hashes, (
            f"Rule 1 fail: hash {labeled_row['_hash']} from labels.jsonl appears in output"
        )

    # ── Rule 2: every hash in sample.jsonl is excluded ───────────────────────
    def test_rule2_sample_hashes_excluded(self, p3_corpus, monkeypatch):
        """Hashes passed via exclude_hashes (sample.jsonl source) must not appear in output."""
        corpus_file, router_data_file, _, _, w5_dir = p3_corpus
        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", corpus_file)

        all_rows = make_p3_fixture_rows()
        # Second routing-text row: another guaranteed router_match row
        sample_row = all_rows[1]
        sample_file = w5_dir / "sample.jsonl"
        _write_jsonl(sample_file, [sample_row])

        args = _make_amend1_args(
            corpus_file, router_data_file, w5_dir,
            exclude_hashes_files=[str(sample_file)],
        )
        prompt_corpus.cmd_label_set_p3(args)

        out_rows = [
            json.loads(line)
            for line in (w5_dir / "labeled-set-p3.jsonl").read_text().splitlines()
            if line.strip()
        ]
        output_hashes = {r["_hash"] for r in out_rows}
        assert sample_row["_hash"] not in output_hashes, (
            f"Rule 2 fail: hash {sample_row['_hash']} from sample.jsonl appears in output"
        )

    # ── Rule 3: 08-eyeballed rows excluded (current fires, baseline doesn't) ─
    def test_rule3_08_eyeballed_rows_excluded(self, p3_corpus, monkeypatch, tmp_path):
        """Rows where current router fires but baseline router doesn't must be excluded."""
        corpus_file, router_data_file, _, _, w5_dir = p3_corpus

        # Build a corpus with one extra row that matches a current-only pattern
        # but NOT the baseline router stored in router_data_file.
        current_only_text = "open a pr for this feature right now please"
        current_only_row = _make_row(current_only_text, preceding_turns=[], idx=999)

        all_rows = make_p3_fixture_rows()
        all_rows.append(current_only_row)
        aug_corpus = tmp_path / "aug_corpus.jsonl"
        _write_jsonl(aug_corpus, all_rows)
        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", aug_corpus)

        # Current router data fires on "open a pr" (ticket 08 build pattern)
        current_router = {
            "keyword_patterns": [
                {
                    "order": 10,
                    "intent": "build",
                    "pattern": r"\bopen (a|the) pr\b",
                    "nudge": "-> /sir-albert:build",
                },
            ],
            "hebrew_patterns": [],
        }
        current_router_file = tmp_path / "current_router.json"
        current_router_file.write_text(json.dumps(current_router), encoding="utf-8")

        # Baseline router (router_data_file) does NOT have the "open a pr" pattern,
        # so this row: current fires, baseline silent → should be excluded.
        args = _make_amend1_args(
            aug_corpus, router_data_file, w5_dir,
            current_router_data=str(current_router_file),
        )
        prompt_corpus.cmd_label_set_p3(args)

        out_rows = [
            json.loads(line)
            for line in (w5_dir / "labeled-set-p3.jsonl").read_text().splitlines()
            if line.strip()
        ]
        output_hashes = {r["_hash"] for r in out_rows}
        assert current_only_row["_hash"] not in output_hashes, (
            "Rule 3 fail: 08-eyeballed row (current fires, baseline silent) appears in output"
        )

    # ── Rule 4: rows from session 6834d4ec are excluded ──────────────────────
    def test_rule4_planning_session_excluded(self, p3_corpus, monkeypatch, tmp_path):
        """Rows whose session_id starts with session_prefix must be excluded."""
        corpus_file, router_data_file, _, _, w5_dir = p3_corpus

        # Add a corpus row from the planning session
        session_text = "what should we work on next for the W5 outperform experiment"
        session_row = {
            "_hash": "aabbccdd11223344",
            "session_id": "6834d4ec-planning-session",
            "timestamp": "2026-09-27T10:00:00Z",
            "cwd": "/tmp/test",
            "project": "test",
            "text": session_text,
            "preceding_turns": [],
            "label": None,
        }
        all_rows = make_p3_fixture_rows()
        all_rows.append(session_row)
        aug_corpus = tmp_path / "aug_corpus2.jsonl"
        _write_jsonl(aug_corpus, all_rows)
        monkeypatch.setattr(prompt_corpus, "CORPUS_FILE", aug_corpus)

        args = _make_amend1_args(
            aug_corpus, router_data_file, w5_dir,
            session_prefix="6834d4ec",
        )
        prompt_corpus.cmd_label_set_p3(args)

        out_rows = [
            json.loads(line)
            for line in (w5_dir / "labeled-set-p3.jsonl").read_text().splitlines()
            if line.strip()
        ]
        output_hashes = {r["_hash"] for r in out_rows}
        assert session_row["_hash"] not in output_hashes, (
            f"Rule 4 fail: session row {session_row['_hash']} from 6834d4ec session appears in output"
        )


class TestP3ChecklistRendering:
    """Prompt/context text must be contained: no line of it may start a markdown
    heading or the importer's header/label lines (Gal-readable and parse-safe)."""

    def test_quote_contains_every_line(self):
        out = prompt_corpus._p3_quote("first\n## 1. heading in a prompt\n**Label:** x")
        assert all(line.startswith("> ") or line == ">" for line in out)

    def test_quote_strips_ansi(self):
        out = prompt_corpus._p3_quote("Opus \x1b[1m4.8\x1b[22m done")
        assert "\x1b" not in "".join(out)

    def test_turns_skip_empty_and_quote(self):
        out = prompt_corpus._p3_fmt_turns([{"role": "user", "text": ""},
                                           {"role": "assistant", "text": "a\n## b"}])
        assert out[0].startswith("> **assistant:**")
        assert all(line.startswith(">") for line in out)
        assert not any("**user:**" in line for line in out)


# ── import-labels-p3 / sample-p3 fixture helpers ─────────────────────────────


def _make_p3_checklist_content(entries):
    """Build a P3 checklist string from a list of entry dicts.

    entry = {
        'n': int,
        'hash': str,
        'slice': str,      # router_match | task_initiating | negative_control
        'predicted': str | None,
        'label': str,      # filled-in label (e.g. 'y', 'brainstorm', '___')
    }
    """
    lines = ["# Labeling Checklist — W5 P3 Held-Out Set", ""]
    for e in entries:
        lines.append(f"### [{e['n']}] hash={e['hash']} slice={e['slice']}")
        lines.append("**Prompt:**")
        lines.append(f"> some synthetic prompt text for {e['hash']}")
        if e.get("predicted"):
            lines.append(f"predicted: {e['predicted']}")
        lines.append(f"**Label:** _{e['label']}_  **Notes:** ___")
        lines.append("")
    return "\n".join(lines)


def _make_p3_rows_for_checklist(entries):
    """Build row dicts matching the labeled-set-p3.jsonl schema."""
    rows = []
    for e in entries:
        rows.append({
            "_hash": e["hash"],
            "text": f"synthetic prompt text for {e['hash']}",
            "predicted_route": e.get("predicted"),
            "slice": e["slice"],
            "label": None,
            "labeled_by": None,
            "labeled_at": None,
            "preceding_turns": e.get("preceding_turns", []),
        })
    return rows


def _run_import_labels_p3(tmp_path, checklist_entries, rows=None, *, subdir="", out_name="labels-p3.jsonl"):
    """Run cmd_import_labels_p3 and return (output_rows, out_path)."""
    cl_content = _make_p3_checklist_content(checklist_entries)
    cl_file = tmp_path / f"{subdir}checklist.md"
    cl_file.write_text(cl_content, encoding="utf-8")

    if rows is None:
        rows = _make_p3_rows_for_checklist(checklist_entries)
    rows_file = tmp_path / f"{subdir}rows.jsonl"
    _write_jsonl(rows_file, rows)

    out_path = tmp_path / out_name
    args = argparse.Namespace(
        checklist=[str(cl_file)],
        rows=[str(rows_file)],
        out=str(out_path),
    )
    prompt_corpus.cmd_import_labels_p3(args)
    out_rows = [
        json.loads(line)
        for line in out_path.read_text().splitlines()
        if line.strip()
    ]
    return out_rows, out_path


def _make_labels_p3_file(tmp_path, entries, name="labels-p3.jsonl"):
    """Build a text-free labels-p3.jsonl from entry list (simulates import output)."""
    rows = []
    for e in entries:
        rows.append({
            "_hash": e["hash"],
            "slice": e["slice"],
            "label": e["label"],
            "predicted_route": e.get("predicted"),
            "labeled_by": "gal",
            "labeled_at": "2026-09-27T00:00:00+00:00",
        })
    path = tmp_path / name
    _write_jsonl(path, rows)
    return path


def _make_rows_with_text(tmp_path, entries, name="rows.jsonl"):
    """Build a rows JSONL with text and preceding_turns (for sample-p3 --rows)."""
    rows = []
    for e in entries:
        rows.append({
            "_hash": e["hash"],
            "text": f"synthetic text for {e['hash']}",
            "predicted_route": e.get("predicted"),
            "slice": e["slice"],
            "label": None,
            "labeled_by": None,
            "labeled_at": None,
            "preceding_turns": e.get("preceding_turns", []),
        })
    path = tmp_path / name
    _write_jsonl(path, rows)
    return path


def _make_full_sample_entries():
    """Return 12+12+12 entries with enough for a 10/10/10 sample."""
    task_labels = ["brainstorm", "plan", "execute", "debug", "build", "handoff"]
    entries = []
    # 12 happy_path: router_match, label == predicted (normalised)
    for i in range(12):
        label = task_labels[i % len(task_labels)]
        entries.append({
            "hash": f"happy{i:012x}",
            "slice": "router_match",
            "predicted": label,
            "label": label,
        })
    # 12 router_silent: task_initiating, task label
    for i in range(12):
        label = task_labels[i % len(task_labels)]
        entries.append({
            "hash": f"silent{i:011x}",
            "slice": "task_initiating",
            "predicted": None,
            "label": label,
        })
    # 12 control: negative_control, label=none
    for i in range(12):
        entries.append({
            "hash": f"ctrl{i:012x}",
            "slice": "negative_control",
            "predicted": None,
            "label": "none",
            "preceding_turns": [{"role": "user", "text": "prev"}],
        })
    return entries


# ── TestImportLabelsP3 ────────────────────────────────────────────────────────


class TestImportLabelsP3:
    """Tests for import-labels-p3 subcommand (written before implementation)."""

    def test_y_on_router_match_resolves_to_predicted_route(self, tmp_path):
        """y on router_match → the normalised predicted route."""
        entries = [{"n": 1, "hash": "aabb0000aabb0001", "slice": "router_match",
                    "predicted": "brainstorm", "label": "y"}]
        out_rows, _ = _run_import_labels_p3(tmp_path, entries)
        assert len(out_rows) == 1
        assert out_rows[0]["label"] == "brainstorm"
        assert out_rows[0]["_hash"] == "aabb0000aabb0001"

    def test_y_on_negative_control_resolves_to_none(self, tmp_path):
        """y on negative_control → none."""
        entries = [{"n": 1, "hash": "aabb0000aabb0002", "slice": "negative_control",
                    "predicted": None, "label": "y"}]
        out_rows, _ = _run_import_labels_p3(tmp_path, entries)
        assert len(out_rows) == 1
        assert out_rows[0]["label"] == "none"

    def test_y_on_task_initiating_is_error(self, tmp_path):
        """y on task_initiating → error (sys.exit non-zero)."""
        entries = [{"n": 1, "hash": "aabb0000aabb0003", "slice": "task_initiating",
                    "predicted": None, "label": "y"}]
        with pytest.raises(SystemExit) as exc:
            _run_import_labels_p3(tmp_path, entries)
        assert exc.value.code != 0

    def test_design_y_normalises_to_brainstorm(self, tmp_path):
        """predicted=design + y → label=brainstorm; raw predicted_route=design kept."""
        entries = [{"n": 1, "hash": "aabb0000aabb0004", "slice": "router_match",
                    "predicted": "design", "label": "y"}]
        out_rows, _ = _run_import_labels_p3(tmp_path, entries)
        assert out_rows[0]["label"] == "brainstorm"
        assert out_rows[0]["predicted_route"] == "design"

    def test_explicit_brainstorm_label_on_design_prediction(self, tmp_path):
        """predicted=design, label=brainstorm (explicit) → label=brainstorm, predicted_route=design."""
        entries = [{"n": 1, "hash": "aabb0000aabb0005", "slice": "router_match",
                    "predicted": "design", "label": "brainstorm"}]
        out_rows, _ = _run_import_labels_p3(tmp_path, entries)
        assert out_rows[0]["label"] == "brainstorm"
        assert out_rows[0]["predicted_route"] == "design"

    def test_invalid_label_is_error(self, tmp_path):
        """Invalid label → error."""
        entries = [{"n": 1, "hash": "aabb0000aabb0006", "slice": "task_initiating",
                    "predicted": None, "label": "notavalidroute"}]
        with pytest.raises(SystemExit) as exc:
            _run_import_labels_p3(tmp_path, entries)
        assert exc.value.code != 0

    def test_blank_label_is_error(self, tmp_path):
        """Blank label (unfilled '___') → error."""
        h = "aabb0000aabb0007"
        # Manually craft the checklist with unfilled blank ___
        cl_content = (
            "# Labeling Checklist\n\n"
            f"### [1] hash={h} slice=router_match\n"
            "**Prompt:**\n> some text\n"
            "predicted: brainstorm\n"
            "**Label:** ___  **Notes:** ___\n"
        )
        rows = _make_p3_rows_for_checklist([
            {"n": 1, "hash": h, "slice": "router_match", "predicted": "brainstorm", "label": "y"}
        ])
        rows_file = tmp_path / "blank_rows.jsonl"
        _write_jsonl(rows_file, rows)
        cl_file = tmp_path / "blank_checklist.md"
        cl_file.write_text(cl_content, encoding="utf-8")
        out_path = tmp_path / "blank_labels.jsonl"
        args = argparse.Namespace(
            checklist=[str(cl_file)],
            rows=[str(rows_file)],
            out=str(out_path),
        )
        with pytest.raises(SystemExit) as exc:
            prompt_corpus.cmd_import_labels_p3(args)
        assert exc.value.code != 0

    def test_output_is_text_free(self, tmp_path):
        """Output rows have no 'text' or 'preceding_turns' field."""
        entries = [{"n": 1, "hash": "aabb0000aabb0008", "slice": "router_match",
                    "predicted": "brainstorm", "label": "y"}]
        out_rows, _ = _run_import_labels_p3(tmp_path, entries)
        assert "text" not in out_rows[0]
        assert "preceding_turns" not in out_rows[0]

    def test_output_has_required_fields(self, tmp_path):
        """Output has _hash, slice, label, predicted_route, labeled_by, labeled_at."""
        entries = [{"n": 1, "hash": "aabb0000aabb0009", "slice": "router_match",
                    "predicted": "plan", "label": "y"}]
        out_rows, _ = _run_import_labels_p3(tmp_path, entries)
        required = {"_hash", "slice", "label", "predicted_route", "labeled_by", "labeled_at"}
        assert required.issubset(set(out_rows[0].keys()))
        assert out_rows[0]["labeled_by"] == "gal"

    def test_multiple_checklists_merged(self, tmp_path):
        """Multiple --checklist files are merged into one output."""
        e1 = {"n": 1, "hash": "aabb0000aabb000a", "slice": "router_match",
               "predicted": "plan", "label": "y"}
        e2 = {"n": 2, "hash": "aabb0000aabb000b", "slice": "task_initiating",
               "predicted": None, "label": "brainstorm"}
        cl1 = tmp_path / "cl1.md"
        cl1.write_text(_make_p3_checklist_content([e1]), encoding="utf-8")
        cl2 = tmp_path / "cl2.md"
        cl2.write_text(_make_p3_checklist_content([e2]), encoding="utf-8")
        rows = _make_p3_rows_for_checklist([e1, e2])
        rows_file = tmp_path / "rows_multi.jsonl"
        _write_jsonl(rows_file, rows)
        out_path = tmp_path / "labels-multi.jsonl"
        args = argparse.Namespace(
            checklist=[str(cl1), str(cl2)],
            rows=[str(rows_file)],
            out=str(out_path),
        )
        prompt_corpus.cmd_import_labels_p3(args)
        out_rows = [json.loads(l) for l in out_path.read_text().splitlines() if l.strip()]
        assert len(out_rows) == 2
        hashes = {r["_hash"] for r in out_rows}
        assert "aabb0000aabb000a" in hashes
        assert "aabb0000aabb000b" in hashes


# ── TestSampleP3 ──────────────────────────────────────────────────────────────


class TestSampleP3:
    """Tests for sample-p3 subcommand (written before implementation)."""

    def test_thirty_rows_rotated_h_s_c(self, tmp_path):
        """30 rows total, rotated happy/router_silent/control, correct output fields."""
        entries = _make_full_sample_entries()
        labels_path = _make_labels_p3_file(tmp_path, entries)
        rows_path = _make_rows_with_text(tmp_path, entries)
        out_path = tmp_path / "sample-p3.jsonl"
        args = argparse.Namespace(
            labels=str(labels_path),
            rows=[str(rows_path)],
            seed=7,
            out=str(out_path),
        )
        prompt_corpus.cmd_sample_p3(args)
        rows = [json.loads(l) for l in out_path.read_text().splitlines() if l.strip()]
        assert len(rows) == 30
        slices = [r["p3_slice"] for r in rows]
        assert slices == ["happy_path", "router_silent", "control"] * 10
        for r in rows:
            for k in ("_hash", "text", "preceding_turns", "label", "p3_slice"):
                assert k in r, f"missing field {k!r}"

    def test_design_prediction_brainstorm_label_is_happy(self, tmp_path):
        """design prediction + brainstorm label qualifies for happy_path (normalised match)."""
        entries = _make_full_sample_entries()
        # Replace first happy entry with design→brainstorm
        entries[0] = {
            "hash": "designhappy000000",
            "slice": "router_match",
            "predicted": "design",
            "label": "brainstorm",
        }
        labels_path = _make_labels_p3_file(tmp_path, entries)
        rows_path = _make_rows_with_text(tmp_path, entries)
        out_path = tmp_path / "sample-p3.jsonl"
        args = argparse.Namespace(
            labels=str(labels_path),
            rows=[str(rows_path)],
            seed=7,
            out=str(out_path),
        )
        prompt_corpus.cmd_sample_p3(args)
        rows = [json.loads(l) for l in out_path.read_text().splitlines() if l.strip()]
        happy = [r for r in rows if r["p3_slice"] == "happy_path"]
        assert len(happy) == 10  # still 10 because we have 12 candidates

    def test_shortfall_exits_nonzero(self, tmp_path, capsys):
        """< 10 candidates in any stratum → non-zero exit + shortfall message."""
        entries = []
        task_labels = ["brainstorm", "plan", "execute", "debug", "build"]
        # Only 5 happy_path candidates
        for i, label in enumerate(task_labels):
            entries.append({"hash": f"happyshort{i:08x}", "slice": "router_match",
                             "predicted": label, "label": label})
        # 10 router_silent
        for i in range(10):
            entries.append({"hash": f"silentok{i:010x}", "slice": "task_initiating",
                             "predicted": None, "label": "brainstorm"})
        # 10 control
        for i in range(10):
            entries.append({"hash": f"ctrlok{i:011x}", "slice": "negative_control",
                             "predicted": None, "label": "none"})
        labels_path = _make_labels_p3_file(tmp_path, entries)
        rows_path = _make_rows_with_text(tmp_path, entries)
        out_path = tmp_path / "sample-p3-short.jsonl"
        args = argparse.Namespace(
            labels=str(labels_path),
            rows=[str(rows_path)],
            seed=7,
            out=str(out_path),
        )
        with pytest.raises(SystemExit) as exc:
            prompt_corpus.cmd_sample_p3(args)
        assert exc.value.code != 0
        captured = capsys.readouterr()
        assert "shortfall" in (captured.out + captured.err).lower()

    def test_misfire_file_written(self, tmp_path):
        """Router_match rows with label != normalised_predicted written to misfire file."""
        entries = _make_full_sample_entries()
        # Add 2 misfires: router_match, label is task but != normalised predicted
        entries.append({"hash": "misfire00000000a", "slice": "router_match",
                        "predicted": "brainstorm", "label": "plan"})
        entries.append({"hash": "misfire00000000b", "slice": "router_match",
                        "predicted": "plan", "label": "debug"})
        labels_path = _make_labels_p3_file(tmp_path, entries)
        rows_path = _make_rows_with_text(tmp_path, entries)
        out_path = tmp_path / "sample-p3.jsonl"
        args = argparse.Namespace(
            labels=str(labels_path),
            rows=[str(rows_path)],
            seed=7,
            out=str(out_path),
        )
        prompt_corpus.cmd_sample_p3(args)
        misfire_path = tmp_path / "sample-p3-misfire.jsonl"
        assert misfire_path.exists(), "sample-p3-misfire.jsonl not written"
        misfire_rows = [json.loads(l) for l in misfire_path.read_text().splitlines() if l.strip()]
        hashes = {r["_hash"] for r in misfire_rows}
        assert "misfire00000000a" in hashes
        assert "misfire00000000b" in hashes

    def test_ambiguous_excluded_from_all_strata(self, tmp_path):
        """Ambiguous rows are excluded from all strata."""
        entries = _make_full_sample_entries()
        entries.append({"hash": "ambig00000000001", "slice": "router_match",
                        "predicted": "brainstorm", "label": "ambiguous"})
        entries.append({"hash": "ambig00000000002", "slice": "task_initiating",
                        "predicted": None, "label": "ambiguous"})
        labels_path = _make_labels_p3_file(tmp_path, entries)
        rows_path = _make_rows_with_text(tmp_path, entries)
        out_path = tmp_path / "sample-p3.jsonl"
        args = argparse.Namespace(
            labels=str(labels_path),
            rows=[str(rows_path)],
            seed=7,
            out=str(out_path),
        )
        prompt_corpus.cmd_sample_p3(args)
        rows = [json.loads(l) for l in out_path.read_text().splitlines() if l.strip()]
        hashes = {r["_hash"] for r in rows}
        assert "ambig00000000001" not in hashes
        assert "ambig00000000002" not in hashes

    def test_control_prefers_negative_control_rows(self, tmp_path):
        """Control stratum prefers negative_control-slice rows before task_initiating nones."""
        entries = []
        task_labels = ["brainstorm", "plan", "execute", "debug", "build", "handoff"]
        for i in range(12):
            label = task_labels[i % len(task_labels)]
            entries.append({"hash": f"happyctrl{i:010x}", "slice": "router_match",
                             "predicted": label, "label": label})
        for i in range(12):
            label = task_labels[i % len(task_labels)]
            entries.append({"hash": f"silentctrl{i:09x}", "slice": "task_initiating",
                             "predicted": None, "label": label})
        # 8 negative_control nones + 6 task_initiating nones (should fill 10 from nc first)
        nc_hashes = set()
        for i in range(8):
            h = f"nc_none{i:011x}"
            nc_hashes.add(h)
            entries.append({"hash": h, "slice": "negative_control", "predicted": None, "label": "none"})
        ti_none_hashes = set()
        for i in range(6):
            h = f"ti_none{i:011x}"
            ti_none_hashes.add(h)
            entries.append({"hash": h, "slice": "task_initiating", "predicted": None, "label": "none"})

        labels_path = _make_labels_p3_file(tmp_path, entries)
        rows_path = _make_rows_with_text(tmp_path, entries)
        out_path = tmp_path / "sample-p3.jsonl"
        args = argparse.Namespace(
            labels=str(labels_path),
            rows=[str(rows_path)],
            seed=7,
            out=str(out_path),
        )
        prompt_corpus.cmd_sample_p3(args)
        rows = [json.loads(l) for l in out_path.read_text().splitlines() if l.strip()]
        control_rows = [r for r in rows if r["p3_slice"] == "control"]
        assert len(control_rows) == 10
        # All 8 nc nones should be in control (and 2 from ti_none)
        control_hashes = {r["_hash"] for r in control_rows}
        # All nc_hashes should appear (since there are only 8, all 8 should be used)
        assert nc_hashes.issubset(control_hashes), "Not all negative_control nones used first"

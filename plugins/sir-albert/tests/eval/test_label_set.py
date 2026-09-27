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

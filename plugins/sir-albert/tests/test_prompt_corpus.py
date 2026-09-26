"""Tests for prompt_corpus.py — extraction, label detection, organic filtering."""
import json
import subprocess
import tempfile
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).parent.parent
TOOL = PLUGIN_ROOT / "tools" / "prompt_corpus.py"


def _make_jsonl(messages: list[dict]) -> str:
    return "\n".join(json.dumps(m) for m in messages) + "\n"


def _run_extract(jsonl_content: str, corpus_dir: Path) -> subprocess.CompletedProcess:
    import os
    # Write fixture to $HOME/.claude/projects/ (tool expands ~ using HOME env)
    projects_dir = corpus_dir / ".claude" / "projects" / "test-project"
    projects_dir.mkdir(parents=True, exist_ok=True)
    (projects_dir / "session.jsonl").write_text(jsonl_content, encoding="utf-8")

    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": str(corpus_dir),  # corpus goes to $HOME/.claude/sir-albert-corpus
    }
    return subprocess.run(
        ["python3", str(TOOL), "extract"],
        capture_output=True,
        text=True,
        env=env,
    )


def _organic_user(text: str, session_id: str = "s1", ts: str = "2026-09-25T00:00:00Z") -> dict:
    return {
        "type": "user",
        "sessionId": session_id,
        "timestamp": ts,
        "cwd": "/tmp/test",
        "message": {"role": "user", "content": text},
    }


def _injected_user(text: str) -> dict:
    return {"type": "user", "sessionId": "s1", "timestamp": "2026-09-25T00:00:00Z",
            "message": {"role": "user", "content": text}}


def _assistant_skill(skill: str) -> dict:
    return {
        "type": "assistant",
        "message": {
            "role": "assistant",
            "content": [
                {"type": "tool_use", "name": "Skill", "input": {"skill": skill}}
            ],
        },
    }


def _assistant_plain() -> dict:
    return {"type": "assistant", "message": {"role": "assistant", "content": "Sure."}}


class TestExtraction:
    def test_organic_prompt_extracted(self, tmp_path):
        jsonl = _make_jsonl([
            _organic_user("help me debug this"),
            _assistant_plain(),
        ])
        result = _run_extract(jsonl, tmp_path)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        corpus = tmp_path / ".claude" / "sir-albert-corpus" / "corpus.jsonl"
        assert corpus.exists()
        entries = [json.loads(l) for l in corpus.read_text().splitlines() if l]
        assert len(entries) == 1
        assert entries[0]["text"] == "help me debug this"

    def test_injected_base_directory_excluded(self, tmp_path):
        jsonl = _make_jsonl([
            _injected_user("Base directory for this skill: /Users/foo/..."),
            _organic_user("real user prompt here"),
            _assistant_plain(),
        ])
        result = _run_extract(jsonl, tmp_path)
        assert result.returncode == 0
        corpus = tmp_path / ".claude" / "sir-albert-corpus" / "corpus.jsonl"
        entries = [json.loads(l) for l in corpus.read_text().splitlines() if l]
        texts = [e["text"] for e in entries]
        assert "real user prompt here" in texts
        assert not any("Base directory" in t for t in texts)

    def test_task_notification_excluded(self, tmp_path):
        jsonl = _make_jsonl([
            _injected_user("<task-notification><task-id>abc</task-id></task-notification>"),
            _organic_user("write a handoff"),
        ])
        _run_extract(jsonl, tmp_path)
        corpus = tmp_path / ".claude" / "sir-albert-corpus" / "corpus.jsonl"
        entries = [json.loads(l) for l in corpus.read_text().splitlines() if l]
        texts = [e["text"] for e in entries]
        assert "write a handoff" in texts
        assert not any("<task-notification" in t for t in texts)

    def test_label_detected_from_next_skill(self, tmp_path):
        jsonl = _make_jsonl([
            _organic_user("write a handoff for this session"),
            _assistant_skill("sir-albert:handoff"),
        ])
        _run_extract(jsonl, tmp_path)
        corpus = tmp_path / ".claude" / "sir-albert-corpus" / "corpus.jsonl"
        entries = [json.loads(l) for l in corpus.read_text().splitlines() if l]
        assert len(entries) == 1
        assert entries[0]["label"] == "sir-albert:handoff"

    def test_label_null_when_no_skill(self, tmp_path):
        jsonl = _make_jsonl([
            _organic_user("what time is it"),
            _assistant_plain(),
        ])
        _run_extract(jsonl, tmp_path)
        corpus = tmp_path / ".claude" / "sir-albert-corpus" / "corpus.jsonl"
        entries = [json.loads(l) for l in corpus.read_text().splitlines() if l]
        assert entries[0]["label"] is None

    def test_deduplication(self, tmp_path):
        jsonl = _make_jsonl([_organic_user("make a plan")])
        _run_extract(jsonl, tmp_path)
        _run_extract(jsonl, tmp_path)  # second run
        corpus = tmp_path / ".claude" / "sir-albert-corpus" / "corpus.jsonl"
        entries = [json.loads(l) for l in corpus.read_text().splitlines() if l]
        assert len(entries) == 1, "Should deduplicate on second extract"

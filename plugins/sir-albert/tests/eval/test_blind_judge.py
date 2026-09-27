"""Tests for blind_judge.py — ticket 08."""
import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

TOOLS_EVAL = Path(__file__).parent.parent.parent / "tools" / "eval"
BLIND_JUDGE_PY = TOOLS_EVAL / "blind_judge.py"

# Dynamically load blind_judge without executing __main__
spec = importlib.util.spec_from_file_location("blind_judge", BLIND_JUDGE_PY)
bj = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bj)


FIXTURES_DIR = Path(__file__).parent / "fixtures"
EXPECTED_MODEL = "claude-opus-5-5[1m]"


def _make_artifact(arm, prompt_hash, rep, prompt_text="test prompt", skills_called=None, result_text="This is the response text."):
    return {
        "arm": arm,
        "prompt_hash": prompt_hash,
        "rep": rep,
        "prompt_text": prompt_text,
        "model": EXPECTED_MODEL,
        "exit_code": 0,
        "timestamp_utc": "2026-09-26T00:00:00",
        "cost_usd": 0.05,
        "turn_count": 1,
        "budget_capped": False,
        "result_subtype": "success",
        "skills_loaded": [],
        "skills_called": skills_called or [],
        "init_event": {"type": "system", "subtype": "init", "skills": []},
        "result_event": {"type": "result", "subtype": "success", "result": result_text, "total_cost_usd": 0.05, "num_turns": 1},
    }


@pytest.fixture()
def runs_dir(tmp_path):
    """4 artifact files: 1 prompt, 2 arms, k=2."""
    rd = tmp_path / "runs"
    rd.mkdir()
    for arm in ("a", "b"):
        for rep in (1, 2):
            art = _make_artifact(arm, "abc123", rep, result_text=f"Response from {arm} rep {rep}")
            (rd / f"{arm}-abc123-rep{rep}.json").write_text(json.dumps(art))
    return rd


# ── Test: summarize reads result_event.result ─────────────────────────────────

def test_summarize_reads_result_event():
    art = _make_artifact("a", "h1", 1, result_text="The answer is 42.")
    summary = bj.summarize(art)
    assert "The answer is 42." in summary


def test_summarize_raises_on_empty():
    art = _make_artifact("a", "h1", 1, result_text="")
    with pytest.raises(ValueError, match="empty response"):
        bj.summarize(art)


def test_summarize_redacts_superpowers(tmp_path):
    """Judge input must not contain superpowers or sir-albert strings."""
    arm_a_art = _make_artifact(
        "a", "h1", 1,
        result_text="I used superpowers:brainstorming to analyze this. Here is the result.",
        skills_called=["superpowers:brainstorming"],
    )
    summary = bj.summarize(arm_a_art)
    assert "superpowers" not in summary.lower()
    assert "sir-albert" not in summary.lower()
    assert "sir_albert" not in summary.lower()
    assert "[skill]" in summary


def test_summarize_from_real_probe_fixture():
    """summarize() on the real arm-b probe fixture must return non-empty text."""
    fixture = FIXTURES_DIR / "arm-b.jsonl"
    if not fixture.exists():
        pytest.skip("arm-b.jsonl not found")
    with open(fixture) as f:
        lines = [json.loads(l) for l in f if l.strip()]
    result_ev = next((e for e in lines if e.get("type") == "result"), None)
    assert result_ev is not None
    art = _make_artifact("b", "probe", 1)
    art["result_event"] = result_ev
    summary = bj.summarize(art)
    assert summary.strip(), "summarize returned empty for real probe fixture"


# ── Test: resolve_pair position-bias logic ────────────────────────────────────

def test_resolve_pair_a_wins():
    assert bj.resolve_pair({"winner": "left"}, {"winner": "right"}) == "A_wins"


def test_resolve_pair_b_wins():
    assert bj.resolve_pair({"winner": "right"}, {"winner": "left"}) == "B_wins"


def test_resolve_pair_tie_when_disagree():
    # AB=left (A wins), BA=left (A wins again in swapped order means B actually won?)
    # BA=left means left=B won, which means B won → same arm won → disagreement
    assert bj.resolve_pair({"winner": "left"}, {"winner": "left"}) == "tie"
    assert bj.resolve_pair({"winner": "right"}, {"winner": "right"}) == "tie"
    assert bj.resolve_pair({"winner": "tie"}, {"winner": "right"}) == "tie"
    assert bj.resolve_pair({"winner": "left"}, {"winner": "tie"}) == "tie"


def test_resolve_pair_judge_error_is_tie():
    assert bj.resolve_pair({"winner": "judge_error"}, {"winner": "right"}) == "tie"


# ── Test: full judge pass with mocked call_judge ──────────────────────────────

def _fake_judge_left(*args, **kwargs):
    return {"winner": "left", "reason": "left is better", "judge_model": EXPECTED_MODEL}


def _fake_judge_right(*args, **kwargs):
    return {"winner": "right", "reason": "right is better", "judge_model": EXPECTED_MODEL}


def test_blind_judge_emits_4_entries(runs_dir, tmp_path):
    """2 pairs × 2 orderings = 4 judgment entries."""
    out = tmp_path / "judgments.jsonl"
    snap = runs_dir.parent / "model-snapshot.txt"
    snap.write_text(EXPECTED_MODEL)

    with patch.object(bj, "call_judge", side_effect=_fake_judge_left):
        with patch.object(bj, "build_judge_settings", return_value=Path("/dev/null")):
            sys.argv = [
                "blind_judge.py",
                "--runs-dir", str(runs_dir),
                "--out", str(out),
                "--model", EXPECTED_MODEL,
            ]
            # Capture main by calling internals directly
            artifacts = {}
            for f in runs_dir.glob("*.json"):
                a = json.loads(f.read_text())
                key = (a["prompt_hash"], a["rep"])
                artifacts.setdefault(key, {})[a["arm"]] = a

            pairs = [(k, v) for k, v in artifacts.items() if "a" in v and "b" in v]
            assert len(pairs) == 2  # 2 reps

            entries = []
            for (ph, rep), arms in sorted(pairs):
                call_ab = _fake_judge_left()
                call_ba = _fake_judge_left()
                entries.append({"prompt_hash": ph, "rep": rep, "ordering": "AB", **call_ab})
                entries.append({"prompt_hash": ph, "rep": rep, "ordering": "BA", **call_ba})

            assert len(entries) == 4


def test_disagreement_recorded_as_tie(runs_dir, tmp_path):
    """AB=left, BA=right → same arm (A) won both → NOT B_wins → tie."""
    # AB ordering: left=A, right=B. call_ab winner=left → A wins
    # BA ordering: left=B, right=A. call_ba winner=right → A wins again
    # Two orderings agree A won → final = A_wins (NOT tie)
    assert bj.resolve_pair({"winner": "left"}, {"winner": "right"}) == "A_wins"

    # AB=left, BA=left → A wins in AB; B wins in BA → disagreement → tie
    assert bj.resolve_pair({"winner": "left"}, {"winner": "left"}) == "tie"


def test_empty_response_is_error_not_tie(tmp_path):
    """Empty response must raise ValueError, not be silently treated as tie."""
    art = _make_artifact("a", "h1", 1, result_text="")
    with pytest.raises(ValueError):
        bj.summarize(art)


def test_judge_error_key_in_failed_output(tmp_path):
    """call_judge returns judge_error winner when output is unparseable."""
    settings = tmp_path / "settings.json"
    settings.write_text(json.dumps({"model": EXPECTED_MODEL, "hooks": {}}))

    # Stub that emits garbage
    stub = tmp_path / "bad_claude.sh"
    stub.write_text("#!/bin/bash\necho 'not json at all'\n")
    stub.chmod(0o755)

    guarded_sh = TOOLS_EVAL / "guarded.sh"

    import os
    env_override = os.environ.copy()
    env_override["W4_SETTINGS_FILE"] = str(settings)

    # call_judge directly with the bad stub
    result = bj.call_judge(
        prompt="test",
        left="left response",
        right="right response",
        model=EXPECTED_MODEL,
        judge_settings=settings,
        guarded_sh=guarded_sh,
        claude_bin=str(stub),
    )
    assert result["winner"] == "judge_error"


def test_judge_input_has_no_skill_names():
    """Judge prompt built from arm A artifact must not contain skill namespace strings."""
    arm_a_art = _make_artifact(
        "a", "h1", 1,
        result_text="I will use sir-albert:plan to create a plan. Using superpowers:brainstorming too.",
        skills_called=["sir-albert:plan", "superpowers:brainstorming"],
    )
    summary = bj.summarize(arm_a_art)
    prompt = bj.JUDGE_PROMPT.format(prompt="write a plan", left=summary, right="response B")
    assert "sir-albert" not in prompt
    assert "superpowers" not in prompt
    assert "sir_albert" not in prompt


def test_redaction_removes_namespaced_and_bare_hyphenated_skill_names():
    """Regression: an earlier regex used [\\\\w-] inside a raw string (a literal
    backslash), so 'superpowers:brainstorming' leaked as '[skill]:brainstorming'."""
    summarize = bj.summarize
    art = {
        "arm": "a", "prompt_hash": "x", "rep": 1,
        "skills_loaded": ["superpowers:writing-plans", "superpowers:brainstorming", "sir-albert:plan"],
        "result_event": {"result": "Using superpowers:brainstorming, then writing-plans; "
                                   "sir-albert:plan and kb:wiki-query. We plan the rollout."},
    }
    text = summarize(art)
    for leak in ("superpowers", "sir-albert", "brainstorming", "writing-plans", "wiki-query", "kb:"):
        assert leak not in text.lower(), f"{leak!r} leaked: {text!r}"
    assert "We plan the rollout." in text, "ordinary prose must survive redaction"


def test_parse_judge_output_unwraps_result_string():
    """Regression: the verdict JSON arrives escaped inside the outer result object's
    "result" string. The old parser searched the raw stdout and never matched."""
    import json as _j
    reply = 'Looking at both.\n```json\n{"winner": "right", "reason": "more complete"}\n```'
    stdout = _j.dumps({"type": "result", "subtype": "success", "is_error": False, "result": reply})
    assert bj.parse_judge_output(stdout) == {"winner": "right", "reason": "more complete"}
    assert bj.parse_judge_output(_j.dumps({"type": "result", "result": "no verdict"})) is None
    assert bj.parse_judge_output("not json") is None


def test_call_judge_sends_prompt_on_stdin(tmp_path):
    """The judge prompt must arrive on stdin, never as '@file' or a positional arg."""
    import json as _j
    stub = tmp_path / "judge_stub.sh"
    stub.write_text(
        "#!/bin/bash\n"
        'for a in "$@"; do case "$a" in @*) echo "stub: @file arg" >&2; exit 7;; esac; done\n'
        'IN=$(cat); case "$IN" in *"Response Left"*) ;; *) echo "stub: no prompt on stdin" >&2; exit 6;; esac\n'
        + f"cat {str(tmp_path / 'reply.json')!r}\n"
    )
    (tmp_path / "reply.json").write_text(_j.dumps({"type": "result", "result": '{"winner": "tie", "reason": "same"}'}))
    stub.chmod(0o755)
    settings = tmp_path / "judge.json"
    settings.write_text('{"model": "claude-opus-5-5[1m]"}')
    out = bj.call_judge("p", "left text", "right text", "claude-opus-5-5[1m]", settings,
                        bj.TOOLS_EVAL / "guarded.sh", str(stub))
    assert out["winner"] == "tie", out


def test_summarize_falls_back_to_assistant_text_when_truncated():
    """A max-turns run has no result field; the judge must see its assistant text."""
    art = {"arm": "b", "prompt_hash": "t", "rep": 1, "skills_loaded": [],
           "result_event": {"type": "result", "subtype": "error_max_turns"},
           "assistant_text": "Here is the partial plan."}
    assert bj.summarize(art) == "Here is the partial plan."


def test_judge_prompt_tells_judge_redaction_is_neutral():
    # Live smoke pair: the judge read "[skill]" as "a broken template" and penalized
    # that side. Placeholders land unevenly across arms, so they must be neutral.
    prompt = bj.JUDGE_PROMPT.format(prompt="p", left="l", right="r")
    assert "[skill]" in prompt
    assert "redact" in prompt.lower()


# ── Ticket 02 (judge-v2) new tests ───────────────────────────────────────────

def test_max_chars_flag():
    """summarize(art, max_chars=6000) keeps a 5000-char answer whole; default is 1500."""
    long_text = "x" * 5000
    art = _make_artifact("a", "h1", 1, result_text=long_text)
    # With explicit max_chars=6000, the full 5000-char text must survive
    summary_6k = bj.summarize(art, max_chars=6000)
    assert len(summary_6k) == 5000, f"expected 5000 chars, got {len(summary_6k)}"
    # Default (1500) must still truncate to 1500
    summary_default = bj.summarize(art)
    assert len(summary_default) == 1500, f"expected 1500-char default, got {len(summary_default)}"


def test_pair_flag_selects_arms(tmp_path):
    """--pair b:s pairs b-* with s-* artifacts and ignores a-*."""
    rd = tmp_path / "runs"
    rd.mkdir()
    for arm in ("a", "b", "s"):
        art = _make_artifact(arm, "ph1", 1, result_text=f"Response from {arm}")
        (rd / f"{arm}-ph1-rep1.json").write_text(json.dumps(art))

    # parse_pair_flag must be present and parse correctly
    parsed = bj.parse_pair_flag("b:s")
    assert parsed == ("b", "s"), f"parse_pair_flag returned {parsed!r}"

    # Load artifacts and filter for pair b:s
    artifacts = {}
    for f in rd.glob("*.json"):
        a = json.loads(f.read_text())
        key = (a["prompt_hash"], a["rep"])
        artifacts.setdefault(key, {})[a["arm"]] = a

    left_arm, right_arm = "b", "s"
    pairs = [(k, v) for k, v in artifacts.items() if left_arm in v and right_arm in v]
    # Should find 1 pair (b+s)
    assert len(pairs) == 1, f"expected 1 b+s pair, got {len(pairs)}"
    _, arms_in_pair = pairs[0]
    assert left_arm in arms_in_pair
    assert right_arm in arms_in_pair
    # a must NOT determine pairing (even if present in the run dir)
    # The pair only uses b and s for judging
    assert "b" in arms_in_pair and "s" in arms_in_pair


def test_rubric_prompt():
    """--rubric makes the prompt contain the 4 criteria and the [skill] redaction note."""
    prompt = bj.RUBRIC_PROMPT.format(prompt="p", left="l", right="r")
    # The 4 criteria must appear
    assert "progress" in prompt.lower(), "criterion 1 (progress) missing"
    assert ("correctness" in prompt.lower() or "grounding" in prompt.lower()), "criterion 2 (correctness/grounding) missing"
    assert ("acting" in prompt.lower() or "asking" in prompt.lower()), "criterion 3 (acting/asking) missing"
    assert "incomplete" in prompt.lower(), "criterion 4 (incomplete) missing"
    # The [skill] redaction note must still be present
    assert "[skill]" in prompt, "[skill] redaction note missing from RUBRIC_PROMPT"
    assert "redact" in prompt.lower(), "redaction explanation missing from RUBRIC_PROMPT"


def test_cutoff_marker_symmetric():
    """truncated=True adds cutoff marker; truncated=False/missing does not."""
    marker = "[Response cut off by the evaluation's turn/budget cap.]"
    # Truncated artifact: marker must appear at the end
    art_truncated = _make_artifact("a", "h1", 1, result_text="Partial work done.")
    art_truncated["truncated"] = True
    summary_trunc = bj.summarize(art_truncated)
    assert summary_trunc.endswith(marker), f"expected cutoff marker at end, got: {summary_trunc!r}"

    # Non-truncated artifact: marker must NOT appear
    art_ok = _make_artifact("a", "h1", 1, result_text="Complete answer.")
    art_ok["truncated"] = False
    summary_ok = bj.summarize(art_ok)
    assert marker not in summary_ok, f"unexpected cutoff marker in non-truncated: {summary_ok!r}"


def test_resolved_rows_name_arms():
    """make_resolved_row records left_arm/right_arm; final_verdict uses arm letters."""
    # For pair a:b → backward-compat labels A_wins/B_wins
    row_a_wins = bj.make_resolved_row({"winner": "left"}, {"winner": "right"}, left_arm="a", right_arm="b")
    assert row_a_wins["left_arm"] == "a"
    assert row_a_wins["right_arm"] == "b"
    assert row_a_wins["final_verdict"] == "A_wins"

    row_b_wins = bj.make_resolved_row({"winner": "right"}, {"winner": "left"}, left_arm="a", right_arm="b")
    assert row_b_wins["final_verdict"] == "B_wins"

    row_tie = bj.make_resolved_row({"winner": "tie"}, {"winner": "left"}, left_arm="a", right_arm="b")
    assert row_tie["final_verdict"] == "tie"

    # For pair b:s → verdict uses b/s letters
    row_b_wins_bs = bj.make_resolved_row({"winner": "left"}, {"winner": "right"}, left_arm="b", right_arm="s")
    assert row_b_wins_bs["final_verdict"] == "B_wins"

    row_s_wins = bj.make_resolved_row({"winner": "right"}, {"winner": "left"}, left_arm="b", right_arm="s")
    assert row_s_wins["final_verdict"] == "S_wins"

#!/usr/bin/env python3
"""blind_judge.py — blind paired preference over run artifacts.

Pairs rep-wise (A/rep1 vs B/rep1), judges each pair twice (AB and BA order)
for position-bias control. Text-only, no tools.

Usage:
  python3 blind_judge.py --runs-dir docs/plans/2026-09-26-w4-eval/runs \
      --out docs/plans/2026-09-26-w4-eval/judgments.jsonl
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS_EVAL = Path(__file__).parent
REPO_ROOT = TOOLS_EVAL.parent.parent.parent.parent  # plugins/sir-albert/tools/eval → repo root

JUDGE_PROMPT = """You are judging two AI assistant responses to the same prompt. You do not know which system produced each response. "[skill]" marks a name redacted by the evaluation harness, not by the assistant; ignore it when judging.

Prompt: {prompt}

Response Left:
{left}

Response Right:
{right}

Which response is better? Reply with JSON only: {{"winner": "left"|"right"|"tie", "reason": "<one sentence>"}}"""

RUBRIC_PROMPT = """You are judging two AI assistant responses to the same prompt. You do not know which system produced each response. "[skill]" marks a name redacted by the evaluation harness, not by the assistant; ignore it when judging.

Judge which response better serves the user, on: (1) progress on what was asked; (2) correctness and grounding, with no invented facts, files, or IDs; (3) the right call between acting and asking; (4) honesty about incomplete work: a response that only announces work in progress or background tasks, without delivering, counts as incomplete.

Prompt: {prompt}

Response Left:
{left}

Response Right:
{right}

Which response is better? Reply with JSON only: {{"winner": "left"|"right"|"tie", "reason": "<one sentence covering the decisive criterion>"}}"""

CUTOFF_MARKER = "[Response cut off by the evaluation's turn/budget cap.]"


def parse_pair_flag(pair_str: str) -> tuple:
    """Parse --pair value 'x:y' → ('x', 'y'). Validates exactly two arms."""
    parts = pair_str.split(":")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError(f"--pair must be 'x:y', got: {pair_str!r}")
    return parts[0], parts[1]


def make_resolved_row(call_ab: dict, call_ba: dict, left_arm: str = "a", right_arm: str = "b") -> dict:
    """Resolve position-bias and return a row with arm labels and final_verdict.

    AB call: left=left_arm, right=right_arm.  BA call: left=right_arm, right=left_arm.
    - AB=left AND BA=right  → left_arm won both → <LEFT>_wins
    - AB=right AND BA=left  → right_arm won both → <RIGHT>_wins
    - anything else (tie in either, or inconsistency) → tie
    """
    ab_w = call_ab.get("winner", "")
    ba_w = call_ba.get("winner", "")
    if ab_w == "left" and ba_w == "right":
        verdict = f"{left_arm.upper()}_wins"
    elif ab_w == "right" and ba_w == "left":
        verdict = f"{right_arm.upper()}_wins"
    else:
        verdict = "tie"
    return {"final_verdict": verdict, "left_arm": left_arm, "right_arm": right_arm}


def summarize(artifact: dict, max_chars: int = 1500, mark_cutoff: bool = False) -> str:
    """Extract and anonymize the final response text from an artifact."""
    # Final response text lives in the result event (verified against the probe stream).
    # A run cut off by --max-turns / budget has no result; fall back to its assistant text.
    final_text = (artifact.get("final_text") or (artifact.get("result_event") or {}).get("result") or artifact.get("assistant_text") or "")
    if not final_text.strip():
        raise ValueError(
            f"empty response in {artifact['arm']}-{artifact['prompt_hash']}-rep{artifact['rep']}"
        )
    # Redact arm-identifying strings BEFORE truncating. Namespaced names first
    # ("superpowers:writing-plans"), then bare hyphenated skill names the arm had loaded
    # ("writing-plans") — those only appear in the arm that loaded them. Bare single
    # words like "plan" are left alone: they are ordinary prose in both arms.
    final_text = re.sub(r"\b(superpowers|sir[-_]albert|kb)(:[\w-]+)?", "[skill]", final_text, flags=re.I)
    bare = {
        (s if isinstance(s, str) else s.get("name", "")).split(":")[-1]
        for s in artifact.get("skills_loaded") or []
    }
    for name in sorted((n for n in bare if "-" in n), key=len, reverse=True):
        final_text = re.sub(rf"(?<![\w-]){re.escape(name)}(?![\w-])", "[skill]", final_text, flags=re.I)
    text = final_text[:max_chars]
    if mark_cutoff and artifact.get("truncated"):
        text += CUTOFF_MARKER
    return text


def build_judge_settings(snapshot_model: str, tmp_dir: Path) -> Path:
    """Create neutral judge settings (all plugins off, no hooks)."""
    settings_src = Path.home() / ".claude" / "settings.json"
    try:
        base = json.loads(settings_src.read_text())
    except Exception:
        base = {}

    # Disable all plugins, clear hooks, keep env (axcli gateway config)
    judge_settings = {k: v for k, v in base.items() if k == "env"}
    judge_settings["model"] = snapshot_model
    judge_settings["enabledPlugins"] = {k: False for k in base.get("enabledPlugins", {})}
    judge_settings["hooks"] = {}

    out = tmp_dir / "judge-settings.json"
    out.write_text(json.dumps(judge_settings, indent=2))
    return out


def call_judge(
    prompt: str,
    left: str,
    right: str,
    model: str,
    judge_settings: Path,
    guarded_sh: Path,
    claude_bin: str,
    judge_prompt: str | None = None,
) -> dict:
    """Make one judge call. Returns {'winner': ..., 'reason': ..., 'judge_model': ...}.
    Returns {'winner': 'judge_error', 'reason': ...} on failure.
    judge_prompt overrides the default JUDGE_PROMPT (e.g. pass RUBRIC_PROMPT for --rubric).
    """
    template = judge_prompt if judge_prompt is not None else JUDGE_PROMPT
    judge_input = template.format(prompt=prompt, left=left, right=right)
    # The prompt goes in on stdin. As a positional arg it was swallowed by the variadic
    # --disallowedTools, and "@file" is an interactive mention, not a --print feature.
    cmd = [
        "bash", str(guarded_sh),
        *claude_bin.split(),
        "--print",
        "--setting-sources", "project,local",
        "--settings", str(judge_settings),
        "--no-session-persistence",
        "--output-format", "json",
        "--max-turns", "1",
        "--model", model,
        "--max-budget-usd", "0.10",
        "--tools", "",
    ]
    last_error = "no attempt made"
    for attempt in range(2):
        try:
            result = subprocess.run(cmd, input=judge_input, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            last_error = "timeout"
            continue
        verdict = parse_judge_output(result.stdout)
        if verdict:
            return {**verdict, "judge_model": model}
        last_error = f"exit={result.returncode} stderr={result.stderr.strip()[-200:]!r}"

    return {"winner": "judge_error", "reason": f"unparseable or failed judge output ({last_error})", "judge_model": model}


def parse_judge_output(stdout: str) -> dict | None:
    """Extract {'winner', 'reason'} from `claude --output-format json` stdout.

    The model's reply is a string inside the outer result object's "result" field
    (escaped), so it must be unwrapped before looking for the verdict JSON.
    """
    try:
        outer = json.loads(stdout)
    except ValueError:
        return None
    inner = outer.get("result") if isinstance(outer, dict) else None
    if not isinstance(inner, str):
        return None
    for candidate in re.findall(r"\{[^{}]*\}", inner, re.DOTALL):
        try:
            parsed = json.loads(candidate)
        except ValueError:
            continue
        winner = str(parsed.get("winner", "")).lower()
        if winner in ("left", "right", "tie"):
            return {"winner": winner, "reason": str(parsed.get("reason", ""))}
    return None


def resolve_pair(call_ab: dict, call_ba: dict) -> str:
    """Resolve position-bias: determine final winner string (backward-compat, pair a:b).

    For arm-aware resolution with left_arm/right_arm labels, use make_resolved_row().
    """
    return make_resolved_row(call_ab, call_ba, left_arm="a", right_arm="b")["final_verdict"]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--runs-dir", default="docs/plans/2026-09-26-w4-eval/runs")
    p.add_argument("--out", default="docs/plans/2026-09-26-w4-eval/judgments.jsonl")
    p.add_argument("--model", default=None, help="override judge model")
    p.add_argument("--claude-bin", default=None)
    p.add_argument("--max-chars", type=int, default=1500,
                   help="max response chars fed to judge (default 1500)")
    p.add_argument("--pair", default="a:b",
                   help="arm pair to judge, e.g. 'a:b' or 'b:s' (default a:b)")
    p.add_argument("--rubric", action="store_true",
                   help="use the rubric prompt (4 criteria) instead of the default prompt")
    args = p.parse_args()

    runs_dir = Path(args.runs_dir)
    out_path = Path(args.out)
    resolved_path = out_path.parent / f"{out_path.stem}-resolved.jsonl"
    guarded_sh = TOOLS_EVAL / "guarded.sh"

    left_arm, right_arm = parse_pair_flag(args.pair)
    judge_prompt = RUBRIC_PROMPT if args.rubric else None
    max_chars = args.max_chars

    # Resolve model
    model = args.model
    if not model:
        snap = runs_dir.parent / "model-snapshot.txt"
        if snap.exists():
            model = snap.read_text().strip()
        else:
            print("ERROR: --model not given and model-snapshot.txt not found", file=sys.stderr)
            sys.exit(1)

    claude_bin = args.claude_bin or os.environ.get("W4_CLAUDE_BIN", "command claude")

    # Load all artifacts
    artifacts = {}
    for f in runs_dir.glob("*.json"):
        try:
            a = json.loads(f.read_text())
            key = (a["prompt_hash"], a["rep"])
            arm = a["arm"]
            artifacts.setdefault(key, {})[arm] = a
        except Exception as e:
            print(f"WARN: could not load {f}: {e}", file=sys.stderr)

    # Find complete pairs for the requested arm pair
    pairs = [(k, v) for k, v in artifacts.items() if left_arm in v and right_arm in v]
    if not pairs:
        print(f"ERROR: no complete {left_arm}:{right_arm} pairs found", file=sys.stderr)
        sys.exit(1)

    # Check for empty responses up front
    empty = []
    for (ph, rep), arms in pairs:
        for arm_id in (left_arm, right_arm):
            art = arms[arm_id]
            try:
                summarize(art, max_chars=max_chars, mark_cutoff=args.rubric)
            except ValueError as e:
                empty.append(str(e))
    if empty:
        print("ABORT: empty responses found:", file=sys.stderr)
        for e in empty:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)

    with tempfile.TemporaryDirectory() as tmp_dir:
        judge_settings = build_judge_settings(model, Path(tmp_dir))

        out_path.parent.mkdir(parents=True, exist_ok=True)
        jf = out_path.open("w")
        rf = resolved_path.open("w")

        for (ph, rep), arms in sorted(pairs):
            art_left = arms[left_arm]
            art_right = arms[right_arm]
            prompt = art_left["prompt_text"]

            try:
                text_left = summarize(art_left, max_chars=max_chars, mark_cutoff=args.rubric)
                text_right = summarize(art_right, max_chars=max_chars, mark_cutoff=args.rubric)
            except ValueError as e:
                print(f"ABORT: {e}", file=sys.stderr)
                sys.exit(1)

            # Call 1: order AB (left=left_arm, right=right_arm)
            call_ab = call_judge(prompt, text_left, text_right, model, judge_settings, guarded_sh, claude_bin, judge_prompt)
            jf.write(json.dumps({
                "prompt_hash": ph, "rep": rep,
                "ordering": "AB", **call_ab
            }) + "\n")

            # Call 2: order BA (left=right_arm, right=left_arm) — sequential
            call_ba = call_judge(prompt, text_right, text_left, model, judge_settings, guarded_sh, claude_bin, judge_prompt)
            jf.write(json.dumps({
                "prompt_hash": ph, "rep": rep,
                "ordering": "BA", **call_ba
            }) + "\n")

            # Resolve
            resolved = make_resolved_row(call_ab, call_ba, left_arm=left_arm, right_arm=right_arm)
            rf.write(json.dumps({
                "prompt_hash": ph, "rep": rep,
                "call_ab": call_ab, "call_ba": call_ba,
                **resolved,
            }) + "\n")

        jf.close()
        rf.close()

    print(f"judgments written: {out_path}")
    print(f"resolved: {resolved_path}")


if __name__ == "__main__":
    main()

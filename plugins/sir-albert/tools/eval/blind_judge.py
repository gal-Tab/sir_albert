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

JUDGE_PROMPT = """You are judging two AI assistant responses to the same prompt. You do not know which system produced each response.

Prompt: {prompt}

Response Left:
{left}

Response Right:
{right}

Which response is better? Reply with JSON only: {{"winner": "left"|"right"|"tie", "reason": "<one sentence>"}}"""


def summarize(artifact: dict) -> str:
    """Extract and anonymize the final response text from an artifact."""
    # Final response text lives in the result event (verified against the probe stream).
    final_text = ((artifact.get("result_event") or {}).get("result") or "")
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
    return final_text[:1500]


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
) -> dict:
    """Make one judge call. Returns {'winner': ..., 'reason': ..., 'judge_model': ...}.
    Returns {'winner': 'judge_error', 'reason': ...} on failure.
    """
    judge_input = JUDGE_PROMPT.format(prompt=prompt, left=left, right=right)
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
    """Resolve position-bias: determine final winner from two ordered calls.

    AB call: left=A, right=B. BA call: left=B, right=A.
    - AB=left AND BA=right  → A won both → A_wins
    - AB=right AND BA=left  → B won both → B_wins
    - anything else (tie in either, or inconsistency) → tie
    """
    ab_w = call_ab.get("winner", "")
    ba_w = call_ba.get("winner", "")
    if ab_w == "left" and ba_w == "right":
        return "A_wins"
    if ab_w == "right" and ba_w == "left":
        return "B_wins"
    return "tie"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--runs-dir", default="docs/plans/2026-09-26-w4-eval/runs")
    p.add_argument("--out", default="docs/plans/2026-09-26-w4-eval/judgments.jsonl")
    p.add_argument("--model", default=None, help="override judge model")
    p.add_argument("--claude-bin", default=None)
    args = p.parse_args()

    runs_dir = Path(args.runs_dir)
    out_path = Path(args.out)
    resolved_path = out_path.parent / "judgments-resolved.jsonl"
    guarded_sh = TOOLS_EVAL / "guarded.sh"

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

    # Find complete pairs
    pairs = [(k, v) for k, v in artifacts.items() if "a" in v and "b" in v]
    if not pairs:
        print("ERROR: no complete pairs found", file=sys.stderr)
        sys.exit(1)

    # Check for empty responses up front
    empty = []
    for (ph, rep), arms in pairs:
        for arm_id, art in arms.items():
            try:
                summarize(art)
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
            art_a = arms["a"]
            art_b = arms["b"]
            prompt = art_a["prompt_text"]

            try:
                left_ab = summarize(art_a)
                right_ab = summarize(art_b)
            except ValueError as e:
                print(f"ABORT: {e}", file=sys.stderr)
                sys.exit(1)

            # Call 1: order AB (left=A, right=B)
            call_ab = call_judge(prompt, left_ab, right_ab, model, judge_settings, guarded_sh, claude_bin)
            jf.write(json.dumps({
                "prompt_hash": ph, "rep": rep,
                "ordering": "AB", **call_ab
            }) + "\n")

            # Call 2: order BA (left=B, right=A) — sequential
            call_ba = call_judge(prompt, right_ab, left_ab, model, judge_settings, guarded_sh, claude_bin)
            jf.write(json.dumps({
                "prompt_hash": ph, "rep": rep,
                "ordering": "BA", **call_ba
            }) + "\n")

            # Resolve
            final = resolve_pair(call_ab, call_ba)
            rf.write(json.dumps({
                "prompt_hash": ph, "rep": rep,
                "call_ab": call_ab, "call_ba": call_ba,
                "final_verdict": final,
            }) + "\n")

        jf.close()
        rf.close()

    print(f"judgments written: {out_path}")
    print(f"resolved: {resolved_path}")


if __name__ == "__main__":
    main()

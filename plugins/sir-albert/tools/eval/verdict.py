#!/usr/bin/env python3
"""verdict.py — compute the P2 verdict from run artifacts and judgment JSONL.

Exit codes:
  0 = PASS
  1 = FAIL (gate condition not met)
  2 = ABORT (run count ≠ 60, or >3 judge_error pairs)
  3 = INCONCLUSIVE (ties > 50% of pairs)

Usage:
  python3 verdict.py --runs-dir docs/plans/2026-09-26-w4-eval/runs \
      --judgments docs/plans/2026-09-26-w4-eval/judgments-resolved.jsonl \
      --sample docs/plans/2026-09-26-w4-eval/sample.jsonl \
      --out-dir docs/plans/2026-09-26-w4-eval
"""
import argparse
import hashlib
import json
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

TOOLS_EVAL = Path(__file__).parent
REPO_ROOT = TOOLS_EVAL.parent.parent.parent.parent  # tools/eval → repo root

# Import _skill_to_route from prompt_corpus (read-only use).
# prompt_corpus.py lives in plugins/sir-albert/tools/
_CORPUS_PATH = TOOLS_EVAL.parent / "prompt_corpus.py"
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("prompt_corpus", _CORPUS_PATH)
_pc = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_pc)
_skill_to_route = _pc._skill_to_route


EXPECTED_RUN_COUNT = 60
HAPPY_PATH_SLICE = "happy_path"
JUDGE_ERROR_ABORT_THRESHOLD = 3  # more than this → ABORT


def load_jsonl(path: Path) -> list:
    rows = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--runs-dir", default=str(REPO_ROOT / "docs/plans/2026-09-26-w4-eval/runs"))
    p.add_argument("--judgments", default=str(REPO_ROOT / "docs/plans/2026-09-26-w4-eval/judgments-resolved.jsonl"))
    p.add_argument("--sample", default=str(REPO_ROOT / "docs/plans/2026-09-26-w4-eval/sample.jsonl"))
    p.add_argument("--out-dir", default=str(REPO_ROOT / "docs/plans/2026-09-26-w4-eval"))
    args = p.parse_args()

    runs_dir = Path(args.runs_dir)
    judgments_path = Path(args.judgments)
    sample_path = Path(args.sample)
    out_dir = Path(args.out_dir)

    # ── Run count check ───────────────────────────────────────────────────────
    run_files = list(runs_dir.glob("*.json"))
    n = len(run_files)
    if n != EXPECTED_RUN_COUNT:
        print(f"ABORT: run count {n} ≠ {EXPECTED_RUN_COUNT} — verdict rejected")
        sys.exit(2)

    # ── Load judgments ────────────────────────────────────────────────────────
    judgments = load_jsonl(judgments_path)

    # Count judge_error pairs
    judge_error_count = sum(
        1 for j in judgments
        if j.get("final_verdict") == "tie"
        and (
            (j.get("call_ab") or {}).get("winner") == "judge_error"
            or (j.get("call_ba") or {}).get("winner") == "judge_error"
        )
    )
    # Also count rows with final_verdict == "judge_error" if present
    judge_error_count += sum(1 for j in judgments if j.get("final_verdict") == "judge_error")

    if judge_error_count > JUDGE_ERROR_ABORT_THRESHOLD:
        print(f"ABORT: {judge_error_count} judge_error pairs > threshold {JUDGE_ERROR_ABORT_THRESHOLD}")
        sys.exit(2)

    # ── Win-rate computation ──────────────────────────────────────────────────
    # Exclude judge_error pairs from denominator
    valid_judgments = [
        j for j in judgments
        if j.get("final_verdict") not in ("judge_error",)
        and (j.get("call_ab") or {}).get("winner") != "judge_error"
        and (j.get("call_ba") or {}).get("winner") != "judge_error"
    ]

    b_wins = sum(1 for j in valid_judgments if j.get("final_verdict") == "B_wins")
    a_wins = sum(1 for j in valid_judgments if j.get("final_verdict") == "A_wins")
    ties = sum(1 for j in valid_judgments if j.get("final_verdict") == "tie")
    total_pairs = len(valid_judgments)

    if total_pairs == 0:
        print("ABORT: no valid judgment pairs")
        sys.exit(2)

    # Inconclusive check: if ties > 50% of pairs
    if ties > total_pairs * 0.5:
        print(f"INCONCLUSIVE: ties {ties}/{total_pairs} exceed 50% — win-rate would be unreliable")
        sys.exit(3)

    b_effective = b_wins + ties / 2
    win_rate = b_effective / total_pairs

    verdict = "PASS"
    fail_reasons = []

    if win_rate < 0.40:
        fail_reasons.append(f"B FAIL: win-rate {win_rate:.1%} < 40.0%")
        verdict = "FAIL"

    # ── Per-slice win-rate ────────────────────────────────────────────────────
    # Load sample to get slice per prompt_hash
    sample_rows = load_jsonl(sample_path) if sample_path.exists() else []
    slice_map = {r["prompt_hash"]: r.get("p2_slice", "unknown") for r in sample_rows if "prompt_hash" in r}

    slice_stats = defaultdict(lambda: {"B_wins": 0, "A_wins": 0, "tie": 0, "total": 0})
    for j in valid_judgments:
        ph = j.get("prompt_hash", "")
        sl = slice_map.get(ph, "unknown")
        fv = j.get("final_verdict", "tie")
        slice_stats[sl][fv if fv in ("B_wins", "A_wins", "tie") else "tie"] += 1
        slice_stats[sl]["total"] += 1

    # ── Skill invocation check (happy-path slice) ─────────────────────────────
    happy_path_hashes = {r["prompt_hash"] for r in sample_rows if r.get("p2_slice") == HAPPY_PATH_SLICE}

    # Load arm B artifacts indexed by prompt_hash
    b_artifacts_by_hash = defaultdict(list)
    for f in run_files:
        try:
            art = json.loads(f.read_text())
            if art.get("arm") == "b":
                b_artifacts_by_hash[art["prompt_hash"]].append(art)
        except Exception:
            pass

    # Load sample labels
    label_map = {r["prompt_hash"]: r.get("label", "") for r in sample_rows}

    skill_hits = 0
    skill_details = []
    for ph in happy_path_hashes:
        label = label_map.get(ph, "")
        arts = b_artifacts_by_hash.get(ph, [])
        # A prompt counts if ANY rep's skills_called contains a skill matching the labeled route
        hit = False
        called_skills = []
        for art in arts:
            for skill in art.get("skills_called", []):
                called_skills.append(skill)
                if _skill_to_route(skill) == label:
                    hit = True
        if hit:
            skill_hits += 1
        skill_details.append({"prompt_hash": ph, "label": label, "skills_called": called_skills, "hit": hit})

    total_happy = len(happy_path_hashes)
    if total_happy > 0 and skill_hits < 4:
        fail_reasons.append(
            f"B FAIL: sir_albert skill invoked on {skill_hits}/{total_happy} happy-path prompts < 4"
        )
        verdict = "FAIL"

    # ── Namespaced report ─────────────────────────────────────────────────────
    run_id = hashlib.sha256(runs_dir.name.encode()).hexdigest()[:8]
    today = date.today().isoformat()
    report_path = out_dir / f"verdict-{today}-{run_id}.md"
    if report_path.exists():
        report_path = out_dir / f"verdict-{today}-{run_id}-2.md"

    out_dir.mkdir(parents=True, exist_ok=True)

    lines = [
        f"## Verdict: {verdict}",
        "",
        "## Run audit",
        f"- Run count: {n} / {EXPECTED_RUN_COUNT} ✓",
        *[
            f"- Arm {arm.upper()}: {sum(1 for r in _arts if r.get('truncated'))} of {len(_arts)} runs cut off "
            f"(max-turns / budget cap); total cost ${sum(r.get('cost_usd') or 0 for r in _arts):.2f}"
            for arm in ("a", "b")
            for _arts in [[json.loads(f.read_text()) for f in run_files if f.name.startswith(f"{arm}-")]]
        ],
        "",
        "## Win-rate (pooled)",
        "| Metric | Value |",
        "|--------|-------|",
        f"| A wins | {a_wins} |",
        f"| B wins | {b_wins} |",
        f"| Ties | {ties} |",
        f"| B effective wins | {b_effective:.1f} |",
        f"| B win-rate | {win_rate:.1%} |",
        f"| Gate (≥40%) | {'✓ PASS' if win_rate >= 0.40 else '✗ FAIL'} |",
        f"| judge_error pairs (excluded) | {judge_error_count} |",
        "",
        "## Win-rate per slice",
        "| Slice | B wins | A wins | Ties | B win-rate |",
        "|-------|--------|--------|------|-----------|",
    ]
    for sl, stats in sorted(slice_stats.items()):
        t = stats["total"]
        b_eff_sl = stats["B_wins"] + stats["tie"] / 2
        wr_sl = b_eff_sl / t if t else 0
        lines.append(
            f"| {sl} | {stats['B_wins']} | {stats['A_wins']} | {stats['tie']} | {wr_sl:.1%} |"
        )

    lines += [
        "",
        "## Skill invocation (happy-path)",
        f"- Hits: {skill_hits}/{total_happy} happy-path prompts had a matching skill invoked",
        f"- Gate (≥4/5): {'✓ PASS' if skill_hits >= 4 else '✗ FAIL'}",
        "",
        "| Prompt hash | Label | Skills called | Hit |",
        "|-------------|-------|---------------|-----|",
    ]
    for d in skill_details:
        lines.append(
            f"| {d['prompt_hash']} | {d['label']} | {', '.join(d['skills_called']) or '(none)'} | {'✓' if d['hit'] else '✗'} |"
        )

    lines += [
        "",
        "## Decision on superpowers",
        "",
        "A passing verdict does NOT mean superpowers should be uninstalled. "
        "That is a separate, explicit decision by Gal, taken after reading this report. "
        "It is never inferred from a passing score.",
    ]

    report_path.write_text("\n".join(lines) + "\n")
    print(f"Report: {report_path}")

    if fail_reasons:
        for r in fail_reasons:
            print(r)
        sys.exit(1)

    print(f"B PASS: win-rate {win_rate:.1%}, skill invocations {skill_hits}/{total_happy}")
    sys.exit(0)


if __name__ == "__main__":
    main()

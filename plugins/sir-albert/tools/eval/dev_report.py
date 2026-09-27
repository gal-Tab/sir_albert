#!/usr/bin/env python3
"""dev_report.py — per-slice hit/fire report for arm B dev runs.

Usage: dev_report.py <ARTIFACT_DIR>

Env overrides (tests): W4_SAMPLE_FILE

Dev bar:
  happy_path  : ≥5/5 hits  (skill called maps via _skill_to_route to label)
  b_silent    : ≥3/5 hits
  control     : 0 fires     (any sir-albert: / superpowers: / kb: call is a fire)

Per-miss table (stdout only, never written to a committed file):
  hash, slice, label, skills_called, first 120 chars of final_text.
"""
import json
import os
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
TOOLS_DIR = EVAL_DIR.parent

sys.path.insert(0, str(TOOLS_DIR))
from prompt_corpus import _skill_to_route  # type: ignore  # noqa: E402

W4_SAMPLE_DEFAULT = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "docs/plans/2026-09-26-w4-eval/sample.jsonl"
)

# Dev bar: slice → minimum hits (for control: maximum fires = 0)
BAR_HITS = {"happy_path": 5, "b_silent": 3}
FIRE_PREFIXES = ("sir-albert:", "superpowers:", "kb:")


def is_fire(skill: str) -> bool:
    return any(skill.startswith(p) for p in FIRE_PREFIXES)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) < 2:
        print("Usage: dev_report.py <ARTIFACT_DIR>")
        return 2

    artifact_dir = Path(argv[1])
    sample_path = Path(os.environ.get("W4_SAMPLE_FILE", str(W4_SAMPLE_DEFAULT)))

    if not sample_path.exists():
        print(f"ABORT: sample file not found: {sample_path}")
        return 2
    if not artifact_dir.exists():
        print(f"ABORT: artifact dir not found: {artifact_dir}")
        return 2

    # ── Load sample rows keyed by _hash ───────────────────────────────────────
    sample_rows: dict = {}
    for line in sample_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            sample_rows[row["_hash"]] = row
        except Exception:
            pass

    # ── Load arm-B rep-1 artifacts keyed by prompt_hash ──────────────────────
    results: dict = {}
    for art_path in sorted(artifact_dir.glob("b-*-rep1.json")):
        try:
            art = json.loads(art_path.read_text(encoding="utf-8"))
            h = art.get("prompt_hash") or art_path.name.split("-")[1]
            results[h] = art
        except Exception:
            pass

    # ── Per-row scoring ───────────────────────────────────────────────────────
    SLICES = ("happy_path", "b_silent", "control")
    rows_by_slice: dict = {s: [] for s in SLICES}

    for h, row in sample_rows.items():
        p2_slice = row.get("p2_slice", "")
        if p2_slice not in rows_by_slice:
            continue
        label = row.get("label", "none")
        art = results.get(h)

        if art is None:
            rows_by_slice[p2_slice].append({
                "hash": h,
                "slice": p2_slice,
                "label": label,
                "hit": False,
                "fire": False,
                "skills_called": [],
                "final_text": "",
                "result_count": 0,
                "truncated": True,
                "context_turns": 0,
                "missing_artifact": True,
            })
            continue

        skills_called = art.get("skills_called") or []
        fires = [s for s in skills_called if is_fire(s)]

        if p2_slice == "control":
            # hit = model correctly stayed silent (no fire)
            hit = len(fires) == 0
        else:
            # hit = a skill was called AND routes to the expected label
            hit = any(_skill_to_route(s) == label for s in skills_called)

        rows_by_slice[p2_slice].append({
            "hash": h,
            "slice": p2_slice,
            "label": label,
            "hit": hit,
            "fire": bool(fires),
            "skills_called": skills_called,
            "final_text": art.get("final_text", "")[:120],
            "result_count": art.get("result_count", 0),
            "truncated": art.get("truncated", False),
            "context_turns": art.get("context_turns", 0),
            "missing_artifact": False,
        })

    # ── Per-slice summary ─────────────────────────────────────────────────────
    print("\n=== Dev Report ===")
    print(f"Artifact dir: {artifact_dir}")
    print(f"Sample:       {sample_path}\n")
    print(f"{'Slice':<15} {'Hits':>5} {'Runs':>5} {'Fires':>6}  {'Bar':<10}  {'Result'}")
    print("-" * 55)

    all_pass = True
    misses = []

    for sl in SLICES:
        row_data = rows_by_slice[sl]
        n = len(row_data)
        hits = sum(1 for r in row_data if r["hit"])
        fires = sum(1 for r in row_data if r["fire"])

        if sl == "control":
            ok = fires == 0
            bar_str = "0 fires"
        else:
            bar = BAR_HITS[sl]
            ok = hits >= bar
            bar_str = f"≥{bar}/{n}"

        if not ok:
            all_pass = False

        verdict = "PASS" if ok else "FAIL"
        print(f"{sl:<15} {hits:>5} {n:>5} {fires:>6}  {bar_str:<10}  {verdict}")

        # Collect misses for the miss table
        for r in row_data:
            if not r["hit"]:
                misses.append(r)

    # ── Per-prompt detail (skills_called, result_count, truncated, context_turns) ──
    print("\n=== Per-run detail ===")
    print(f"{'Slice':<15} {'Hash':<18} {'Label':<12} {'CtxT':>5} {'RC':>4} {'T':>2}  Skills")
    print("-" * 85)
    for sl in SLICES:
        for r in rows_by_slice[sl]:
            ctx = r["context_turns"]
            rc = r["result_count"]
            trunc = "Y" if r["truncated"] else "N"
            skills_str = ",".join(r["skills_called"]) or "(none)"
            marker = "HIT" if r["hit"] else "MISS"
            print(
                f"{sl:<15} {r['hash']:<18} {r['label']:<12} {ctx:>5} {rc:>4} {trunc:>2}  "
                f"{skills_str[:45]:<45}  [{marker}]"
            )

    # ── Per-miss table (stdout only, never committed) ─────────────────────────
    if misses:
        print("\n=== Misses ===")
        print(
            f"{'Hash':<18} {'Slice':<12} {'Label':<12} "
            f"{'Skills Called':<35} B response (first 120 chars)"
        )
        print("-" * 115)
        for m in misses:
            skills_str = ",".join(m["skills_called"]) or "(none)"
            text = m["final_text"].replace("\n", " ")[:120]
            print(
                f"{m['hash']:<18} {m['slice']:<12} {m['label']:<12} "
                f"{skills_str:<35} {text}"
            )

    # ── Verdict ───────────────────────────────────────────────────────────────
    verdict = "DEV PASS" if all_pass else "DEV FAIL"
    print(f"\n{verdict}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

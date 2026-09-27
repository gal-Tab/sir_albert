#!/usr/bin/env python3
"""audit_runs.py — audit an artifact directory after a tranche run.

Usage:
    audit_runs.py <artifact_dir> --arms b,a,s --reps 1 --expected-prompts 30

Checks:
  - Total artifact count == expected_prompts * len(arms) * reps
  - Per-arm count == expected_prompts * reps
  - Complete (prompt_hash, rep) tuples: every hash appears in ALL requested arms
  - Infra errors (via run_tranche.is_infra_error definition: $0 errors or API Error: starts)
  - Empty final_text
  - model == expected model (default: claude-sonnet-5)
  - Truncated (truncated=True) per arm

Exits 0 on clean audit, non-zero on any failure.
"""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
EXPECTED_MODEL = "claude-sonnet-5"


def _load_is_infra_error():
    spec = importlib.util.spec_from_file_location("run_tranche", EVAL_DIR / "run_tranche.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.is_infra_error


def load_artifacts(artifact_dir: Path, arms: list[str], reps: list[int]) -> list[dict]:
    artifacts = []
    for p in artifact_dir.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            if d.get("arm") in arms and d.get("rep") in reps:
                artifacts.append(d)
        except Exception:
            pass
    return artifacts


def audit(artifact_dir: Path, arms: list[str], reps: list[int],
          expected_prompts: int, model: str = EXPECTED_MODEL) -> tuple[bool, list[str]]:
    is_infra_error = _load_is_infra_error()

    artifacts = load_artifacts(artifact_dir, arms, reps)
    expected_total = expected_prompts * len(arms) * len(reps)

    findings: list[str] = []
    ok = True

    # ── 1. Total count ──────────────────────────────────────────────────────────
    if len(artifacts) != expected_total:
        findings.append(
            f"FAIL  total artifacts: {len(artifacts)}, expected {expected_total} "
            f"({expected_prompts} prompts × {len(arms)} arms × {len(reps)} reps)"
        )
        ok = False
    else:
        findings.append(f"OK    total: {len(artifacts)} artifacts")

    # ── 2. Per-arm count ────────────────────────────────────────────────────────
    per_arm: dict[str, list[dict]] = {a: [] for a in arms}
    for art in artifacts:
        per_arm.setdefault(art["arm"], []).append(art)

    expected_per_arm = expected_prompts * len(reps)
    for arm in arms:
        count = len(per_arm.get(arm, []))
        label = "OK  " if count == expected_per_arm else "FAIL"
        findings.append(f"{label}  arm {arm}: {count} artifacts (expected {expected_per_arm})")
        if count != expected_per_arm:
            ok = False

    # ── 3. Complete (prompt_hash, rep) tuples ───────────────────────────────────
    by_hash_rep: dict[tuple, set[str]] = {}
    for art in artifacts:
        key = (art.get("prompt_hash", ""), art.get("rep", 0))
        by_hash_rep.setdefault(key, set()).add(art.get("arm", ""))

    complete = sum(1 for arms_set in by_hash_rep.values() if set(arms) <= arms_set)
    expected_complete = expected_prompts * len(reps)
    if complete != expected_complete:
        missing = [(h, r) for (h, r), a in by_hash_rep.items() if not set(arms) <= a]
        findings.append(
            f"FAIL  complete (hash,rep) tuples: {complete}/{expected_complete}; "
            f"first 3 incomplete: {missing[:3]}"
        )
        ok = False
    else:
        findings.append(f"OK    complete tuples: {complete}/{expected_complete}")

    # ── 4. Infra errors ─────────────────────────────────────────────────────────
    infra_by_arm: dict[str, int] = {a: 0 for a in arms}
    for art in artifacts:
        if is_infra_error(art):
            infra_by_arm[art.get("arm", "?")] = infra_by_arm.get(art.get("arm", "?"), 0) + 1
    total_infra = sum(infra_by_arm.values())
    label = "OK  " if total_infra == 0 else "FAIL"
    details = "  ".join(f"{a}:{n}" for a, n in infra_by_arm.items() if n)
    findings.append(
        f"{label}  infra errors: {total_infra}"
        + (f" ({details})" if details else "")
    )
    if total_infra:
        ok = False

    # ── 5. Empty final_text ──────────────────────────────────────────────────────
    empty_by_arm: dict[str, int] = {a: 0 for a in arms}
    for art in artifacts:
        if not (art.get("final_text") or "").strip():
            empty_by_arm[art.get("arm", "?")] = empty_by_arm.get(art.get("arm", "?"), 0) + 1
    total_empty = sum(empty_by_arm.values())
    label = "OK  " if total_empty == 0 else "WARN"
    details = "  ".join(f"{a}:{n}" for a, n in empty_by_arm.items() if n)
    findings.append(
        f"{label}  empty final_text: {total_empty}"
        + (f" ({details})" if details else "")
    )
    # Empty final_text is a warning, not a hard failure (budget-capped runs can have it)

    # ── 6. Model check ──────────────────────────────────────────────────────────
    wrong_model = [art for art in artifacts if art.get("model") != model]
    label = "OK  " if not wrong_model else "FAIL"
    findings.append(f"{label}  model=={model!r}: {len(artifacts) - len(wrong_model)}/{len(artifacts)} ok")
    if wrong_model:
        ok = False
        findings.append(f"      wrong: {[a.get('model') for a in wrong_model[:3]]}")

    # ── 7. Cut-offs (truncated) per arm ─────────────────────────────────────────
    trunc_by_arm: dict[str, int] = {a: 0 for a in arms}
    for art in artifacts:
        if art.get("truncated"):
            trunc_by_arm[art.get("arm", "?")] = trunc_by_arm.get(art.get("arm", "?"), 0) + 1
    total_trunc = sum(trunc_by_arm.values())
    label = "OK  " if total_trunc == 0 else "WARN"
    details = "  ".join(f"{a}:{n}" for a, n in trunc_by_arm.items())
    findings.append(f"{label}  truncated (cut-offs): {total_trunc}  ({details})")

    return ok, findings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("artifact_dir", help="Directory containing artifact JSON files")
    parser.add_argument("--arms", default="b,a", help="Comma-separated arms (default: b,a)")
    parser.add_argument("--reps", type=int, default=1, help="Rep count (default: 1)")
    parser.add_argument("--expected-prompts", type=int, required=True,
                        help="Expected number of unique prompts")
    parser.add_argument("--model", default=EXPECTED_MODEL,
                        help=f"Expected model (default: {EXPECTED_MODEL})")
    args = parser.parse_args(argv)

    artifact_dir = Path(args.artifact_dir)
    arms = [a.strip() for a in args.arms.split(",")]
    reps = list(range(1, args.reps + 1))

    ok, findings = audit(artifact_dir, arms, reps, args.expected_prompts, args.model)
    for line in findings:
        print(line)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

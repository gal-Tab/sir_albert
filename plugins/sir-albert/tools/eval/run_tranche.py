#!/usr/bin/env python3
"""run_tranche.py — parallel, resumable, budget-capped P2 replay runner.

Usage (legacy):  run_tranche.py <RUNDIR> <SAMPLE_JSONL> <TRANCHE: 1|2>
  Tranche 1 = sample rows 1-10 (40 runs), tranche 2 = rows 11-15 (20 runs).

Usage (new):     run_tranche.py <RUNDIR> <SAMPLE_JSONL> --arms b --rows all --reps 1 [--expected N]
  --arms         comma-separated arms (default: a,b)
  --rows         all | 1 | 2  (default: all)
  --reps         repetitions per job (default: 1 in new mode, 2 in legacy)
  --expected N   expected total runs (activates the extrapolation gate)

Each run is one run_one.sh call (one arm, one prompt, one rep). Runs are
submitted in interleaved order (a1 b1 a2 b2 per prompt), W4_PARALLEL at a time.

Context: when a sample row has preceding_turns, or the corpus.jsonl has them
for the row's _hash, a context file is written to W4_CONTEXT_DIR/<hash>.json
and passed as arg 6 to run_one.sh.

Guarantees:
- Budget: a run is only submitted if spent + (in-flight + 1) x per-run cap stays
  within the budget, so parallelism can never overshoot it.
- Resumable: a run whose artifact exists is skipped.
- Infra errors (is_error and $0 cost: the model never answered, e.g. a Bedrock
  502 or a timeout while the Mac slept) are moved to runs/invalid/ and retried.
- Gal's settings.json is backed up first and diffed afterwards.

Env overrides (tests): W4_SETTINGS_FILE, W4_ARTIFACT_DIR, W4_BUDGET_USD,
W4_SESSIONS_FILE, W4_GAL_DEFAULT, W4_TEST_MODEL, W4_PARALLEL, W4_RETRIES,
W4_RETRY_WAIT, W4_STAGGER, W4_NO_CAFFEINATE, W4_CORPUS_FILE, W4_CONTEXT_DIR.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parent
PER_RUN_CAP = 0.60
EXPECTED_RUNS_TOTAL = 60


def env(name, default):
    return os.environ.get(name, default)


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def is_infra_error(artifact):
    """The model never answered usefully: a $0 error OR a paid run that ended
    with an 'API Error: …' message (the model crashed mid-reply)."""
    result = artifact.get("result_event") or {}
    # Classic zero-cost errors (connection failures, Bedrock 502s, etc.)
    if bool(result.get("is_error")) and not (artifact.get("cost_usd") or 0):
        return True
    # Paid API errors: run cost money but ended with an API Error message
    result_text = (result.get("result") or artifact.get("assistant_text") or "").strip()
    if result_text.startswith("API Error:"):
        return True
    return False


def main(argv):
    # ── Argument parsing ───────────────────────────────────────────────────────
    # Supports two forms:
    #   Legacy:  run_tranche.py RUNDIR SAMPLE TRANCHE   (TRANCHE = 1 or 2)
    #   New:     run_tranche.py RUNDIR SAMPLE --arms b --rows all --reps 1 [--expected N]
    parser = argparse.ArgumentParser(
        description="Parallel, resumable, budget-capped replay runner.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )
    parser.add_argument("rundir")
    parser.add_argument("sample")
    parser.add_argument("tranche", nargs="?", default=None,
                        help="Legacy: tranche 1 or 2")
    parser.add_argument("--arms", default=None,
                        help="Comma-separated arms, e.g. 'b' or 'a,b' (default: a,b)")
    parser.add_argument("--rows", default=None,
                        help="Rows: all | 1 | 2 (default: all in new mode)")
    parser.add_argument("--reps", type=int, default=None,
                        help="Repetitions per job (default: 2 in legacy, 1 in new mode)")
    parser.add_argument("--expected", type=int, default=None,
                        help="Expected total runs (activates extrapolation gate in new mode)")
    parser.add_argument("-h", "--help", action="store_true", default=False)

    try:
        args = parser.parse_args(argv[1:])
    except SystemExit:
        print(__doc__.split("\n\n")[0])
        return 2

    if args.help:
        print(__doc__)
        return 0

    rundir = Path(args.rundir)
    sample_path = Path(args.sample)

    # ── Determine legacy vs new mode ──────────────────────────────────────────
    legacy_mode = args.tranche is not None

    if legacy_mode:
        tranche = args.tranche
        bounds = {"1": (0, 10), "2": (10, 15)}
        if tranche not in bounds:
            print("ABORT: tranche must be 1 or 2")
            return 2
        arms = ["a", "b"]
        reps_list = [1, 2]
        first, last = bounds[tranche]
        expected_runs = EXPECTED_RUNS_TOTAL   # for extrapolation gate
        run_label = f"tranche {tranche}"
        backup_key = f"tranche{tranche}"
    else:
        arms = [a.strip() for a in (args.arms or "a,b").split(",")]
        reps_count = args.reps if args.reps is not None else 1
        reps_list = list(range(1, reps_count + 1))
        rows_spec = args.rows or "all"
        if rows_spec == "all":
            first, last = 0, None        # slice [0:None] = all rows
        elif rows_spec in ("1", "2"):
            bounds = {"1": (0, 10), "2": (10, 15)}
            first, last = bounds[rows_spec]
        else:
            print(f"ABORT: --rows must be all, 1, or 2, got {rows_spec!r}")
            return 2
        expected_runs = args.expected    # None → extrapolation gate disabled
        run_label = f"arms={','.join(arms)} rows={rows_spec} reps={reps_count}"
        backup_key = "arms-" + "-".join(arms)

    repo_root = Path(subprocess.run(["git", "-C", str(EVAL_DIR), "rev-parse", "--show-toplevel"],
                                    capture_output=True, text=True, check=True).stdout.strip())
    settings_file = Path(env("W4_SETTINGS_FILE", str(Path.home() / ".claude" / "settings.json")))
    artifact_dir = Path(env("W4_ARTIFACT_DIR", str(repo_root / "docs/plans/2026-09-26-w4-eval/runs")))
    budget = float(env("W4_BUDGET_USD", "40"))
    sessions_file = Path(env("W4_SESSIONS_FILE", str(Path.home() / ".claude" / "sir-albert-sessions.jsonl")))
    gal_default = env("W4_GAL_DEFAULT", "claude-opus-5-5[1m]")
    test_model = env("W4_TEST_MODEL", "claude-sonnet-5")
    parallel = int(env("W4_PARALLEL", "4"))
    retries = int(env("W4_RETRIES", "2"))
    retry_wait = float(env("W4_RETRY_WAIT", "30"))
    stagger = float(env("W4_STAGGER", "3"))
    corpus_file = Path(env("W4_CORPUS_FILE",
                           str(Path.home() / ".claude" / "sir-albert-corpus" / "corpus.jsonl")))
    context_dir = Path(env("W4_CONTEXT_DIR",
                           str(repo_root / "docs/plans/2026-09-27-w5-outperform/context")))
    artifact_dir.mkdir(parents=True, exist_ok=True)
    invalid_dir = artifact_dir / "invalid"

    # ── Preconditions ─────────────────────────────────────────────────────────
    model_now = load_json(settings_file).get("model")
    model_snap = (rundir / "model-snapshot.txt").read_text().strip()
    if model_now != gal_default or model_snap != test_model:
        print(f"ABORT: model settings={model_now} (want {gal_default}) snapshot={model_snap} (want {test_model})")
        return 2
    # Canary check: only verify arms that are actually requested.
    for arm in arms:
        f = rundir / f"canary-{arm}.jsonl"
        if not f.exists() or f.stat().st_size == 0:
            print(f"ABORT: canary for arm {arm} has not run (canary_preflight.sh)")
            return 2
    all_sample_rows = [json.loads(l) for l in sample_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    rows = all_sample_rows[first:last]
    expected_n = (last - first) if last is not None else len(all_sample_rows) - first
    if len(rows) != expected_n:
        print(f"ABORT: {run_label} expects {expected_n} sample rows, found {len(rows)}")
        return 2

    if not os.environ.get("W4_NO_CAFFEINATE") and shutil.which("caffeinate"):
        # Keep the Mac from idle-sleeping for exactly as long as this runner lives.
        subprocess.Popen(["caffeinate", "-i", "-w", str(os.getpid())],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    backup = rundir / f"settings-backup-{backup_key}.json"
    shutil.copy2(settings_file, backup)

    # ── Context file lookup ───────────────────────────────────────────────────
    # Load corpus for preceding_turns fallback (W4 rows predate ticket 01 and
    # carry no preceding_turns field; the corpus has them keyed by _hash).
    corpus_by_hash: dict = {}
    if corpus_file.exists():
        for line in corpus_file.read_text(encoding="utf-8", errors="ignore").splitlines():
            try:
                row = json.loads(line)
                h = row.get("_hash", "")
                turns = row.get("preceding_turns")
                if h and turns:
                    corpus_by_hash[h] = turns
            except Exception:
                pass

    # Write context files for rows that have preceding_turns (in row or corpus).
    ctx_files: dict = {}   # hash → Path
    for r in rows:
        h = r.get("_hash", "")
        turns = r.get("preceding_turns") or corpus_by_hash.get(h)
        if turns:
            context_dir.mkdir(parents=True, exist_ok=True)
            ctx_path = context_dir / f"{h}.json"
            ctx_path.write_text(json.dumps(turns, ensure_ascii=False))
            ctx_files[h] = ctx_path

    def artifact_path(job):
        arm, h, rep, _ = job
        return artifact_dir / f"{arm}-{h}-rep{rep}.json"

    def valid_artifacts():
        return list(artifact_dir.glob("*.json"))

    def spent():
        return round(sum(load_json(f).get("cost_usd") or 0 for f in valid_artifacts()), 4)

    jobs = [(arm, r["_hash"], rep, r["text"]) for r in rows for rep in reps_list for arm in arms]
    pending = [j for j in jobs if not artifact_path(j).exists()]
    print(f"{run_label}: {len(jobs)} runs, {len(jobs) - len(pending)} already done | "
          f"parallel={parallel} | spent so far ${spent()} of ${budget}", flush=True)

    child_env = dict(os.environ, W4_ARTIFACT_DIR=str(artifact_dir), W4_RESTORE_MODEL=gal_default)

    def run(job):
        arm, h, rep, text = job
        cmd = ["bash", str(EVAL_DIR / "run_one.sh"), arm, h, str(rep), text, str(rundir)]
        ctx = ctx_files.get(h)
        if ctx:
            cmd.append(str(ctx))
        p = subprocess.run(cmd, capture_output=True, text=True, env=child_env)
        return p.returncode, p.stderr

    attempts = {}
    in_flight = {}
    exit_code = 0
    with ThreadPoolExecutor(max_workers=max(parallel, 1)) as pool:
        while (pending and exit_code == 0) or in_flight:
            # Submit while the budget allows every in-flight run to hit its cap.
            while pending and exit_code == 0 and len(in_flight) < parallel:
                if spent() + (len(in_flight) + 1) * PER_RUN_CAP > budget:
                    if not in_flight:
                        print(f"ABORT: spent ${spent()} + next run's ${PER_RUN_CAP:.2f} cap would exceed ${budget}")
                        exit_code = 3
                    break
                job = pending.pop(0)
                in_flight[pool.submit(run, job)] = job
                if stagger and pending:
                    time.sleep(stagger)
            if not in_flight:
                break

            done, _ = wait(in_flight, return_when=FIRST_COMPLETED)
            for fut in done:
                job = in_flight.pop(fut)
                rc, stderr = fut.result()
                name = artifact_path(job).name
                if rc != 0:
                    print(f"ABORT: run_one.sh exit {rc} on {name}: {stderr.strip()[-300:]}")
                    exit_code = exit_code or rc
                    continue
                art = load_json(artifact_path(job))
                if is_infra_error(art):
                    n = attempts.get(job, 0) + 1
                    attempts[job] = n
                    invalid_dir.mkdir(exist_ok=True)
                    shutil.move(str(artifact_path(job)), invalid_dir / f"{name[:-5]}.attempt{n}.json")
                    reason = ((art.get("result_event") or {}).get("result") or "")[:80]
                    if n <= retries:
                        print(f"retry {n}/{retries} {name}: infra error ({reason})", flush=True)
                        time.sleep(retry_wait)
                        pending.insert(0, job)
                    else:
                        print(f"ABORT: {name} failed {n} times with infra errors ({reason})")
                        exit_code = exit_code or 5
                    continue
                n_valid = len(valid_artifacts())
                print(f"done {name} | ${art.get('cost_usd') or 0:.3f} | {n_valid} valid | spent ${spent()}", flush=True)
                # Extrapolation gate: once 10 runs exist, project to expected total.
                # Legacy: always active on tranche 1 (gate against full 60-run total).
                # New mode: active only when --expected is provided.
                gate_active = (legacy_mode and tranche == "1") or (not legacy_mode and expected_runs is not None)
                if gate_active and n_valid >= 10 and spent() / n_valid * expected_runs > budget and exit_code == 0:
                    print(f"ABORT: {n_valid} runs cost ${spent()}, extrapolates past ${budget} for {expected_runs} runs")
                    exit_code = 3

    # ── Wrap-up ───────────────────────────────────────────────────────────────
    scratch_root = load_json(rundir / "run-manifest.json")["scratch_cwd"]
    if sessions_file.exists():
        subprocess.run([sys.executable, str(EVAL_DIR / "strip_harness_sessions.py"),
                        "--sessions-file", str(sessions_file), "--scratch-cwd", scratch_root], check=False)

    before, after = load_json(backup), load_json(settings_file)
    changed = sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))
    if changed:
        print(f"WARNING: settings.json keys changed during the tranche: {changed}. Backup: {backup}")
        if exit_code == 0:
            exit_code = 6

    done_count = sum(1 for j in jobs if artifact_path(j).exists())
    print(f"{run_label} {'complete' if done_count == len(jobs) else 'stopped'}: "
          f"{done_count}/{len(jobs)} runs | spent ${spent()} of ${budget}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv))

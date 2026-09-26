#!/usr/bin/env python3
"""prompt_corpus.py — reusable prompt corpus tool for sir_albert.

Commands:
  extract      Read transcripts → ~/.claude/sir-albert-corpus/corpus.jsonl
  stats        Counts per label
  sample       --label X -n N  Redacted snippets
  router-eval  Precision + recall report (replaces tools/precision_report.py)

Usage:
  python3 plugins/sir-albert/tools/prompt_corpus.py extract
  python3 plugins/sir-albert/tools/prompt_corpus.py stats
  python3 plugins/sir-albert/tools/prompt_corpus.py sample --label sir-albert:handoff -n 5
  python3 plugins/sir-albert/tools/prompt_corpus.py router-eval
"""
import argparse
import glob
import hashlib
import json
import os
import random
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PLUGIN_ROOT = Path(__file__).parent.parent        # plugins/sir-albert/
REPO_ROOT = PLUGIN_ROOT.parent.parent             # sir_albert/ repo root
ROUTER_DATA = PLUGIN_ROOT / "hooks" / "router_data.json"
HOOK_SCRIPT = PLUGIN_ROOT / "hooks" / "prompt_router.py"
CORPUS_DIR = Path.home() / ".claude" / "sir-albert-corpus"
CORPUS_FILE = CORPUS_DIR / "corpus.jsonl"
REPORT_DIR = REPO_ROOT / "docs" / "plans" / "2026-09-24-w3-router"
EVAL_DIR = REPO_ROOT / "docs" / "plans" / "2026-09-26-w4-eval"

MAX_LINE_BYTES = 200_000
MAX_PROMPT_CHARS = 2000
PRECEDING_TURNS = 2
PRECEDING_MAX_CHARS = 500

# ── Organic filter ─────────────────────────────────────────────────────────────
SKIP_RE = re.compile(
    r'^(Base directory for this skill'
    r'|<task-notification'
    r'|<command-'
    r'|<local-command-'
    r'|This session is being continued from'
    r'|\[REQUEST INTERRUPTED'
    r'|<system-reminder'
    r'|The coordinator sent a message'
    r')', re.IGNORECASE
)


def is_organic(text: str) -> bool:
    text = text.strip()
    if not text or len(text) > MAX_PROMPT_CHARS:
        return False
    if SKIP_RE.match(text):
        return False
    if text.startswith('<') and '>' in text[:50]:
        return False
    return True


# ── JSONL helpers ──────────────────────────────────────────────────────────────
def extract_text(content) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") in ("tool_result", "tool_use"):
                continue
            parts.append(block.get("text", ""))
        return " ".join(parts).strip()
    return ""


def get_content(msg: dict) -> str:
    inner = msg.get("message") if isinstance(msg.get("message"), dict) else None
    raw = (inner or msg).get("content", "")
    return extract_text(raw)


def get_skill_label(msg: dict) -> str | None:
    """Return the Skill slug if this assistant message fired a Skill tool_use."""
    inner = msg.get("message") if isinstance(msg.get("message"), dict) else msg
    content = inner.get("content", [])
    if not isinstance(content, list):
        return None
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill":
            inp = block.get("input", {})
            if isinstance(inp, dict):
                return inp.get("skill") or None
    return None


def load_jsonl(path: str):
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for raw in fh:
                if len(raw) > MAX_LINE_BYTES:
                    continue
                try:
                    yield json.loads(raw)
                except Exception:
                    pass
    except Exception:
        pass


def prompt_hash(session_id: str, text: str) -> str:
    return hashlib.sha256(f"{session_id}||{text}".encode()).hexdigest()[:16]


# ── Extract ────────────────────────────────────────────────────────────────────
def cmd_extract(args):
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing hashes to deduplicate
    existing = set()
    if CORPUS_FILE.exists():
        for line in open(CORPUS_FILE, encoding="utf-8", errors="ignore"):
            try:
                e = json.loads(line)
                existing.add(e.get("_hash", ""))
            except Exception:
                pass

    files = glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True)
    files = [f for f in files if "/subagents/" not in f]

    written = 0
    skipped_dup = 0
    excluded = 0

    with open(CORPUS_FILE, "a", encoding="utf-8") as out:
        for f in files:
            # Derive project info from path
            # ~/.claude/projects/<project-slug>/<session>.jsonl
            parts = Path(f).parts
            try:
                proj_idx = parts.index("projects") + 1
                project_slug = parts[proj_idx]
            except (ValueError, IndexError):
                project_slug = "unknown"

            messages = list(load_jsonl(f))
            for i, msg in enumerate(messages):
                msg_type = msg.get("type", "")
                if msg_type not in ("user", "human"):
                    continue
                text = get_content(msg)
                if not text or not is_organic(text):
                    excluded += 1
                    continue

                session_id = msg.get("sessionId", "") or msg.get("session_id", "")
                h = prompt_hash(session_id, text)
                if h in existing:
                    skipped_dup += 1
                    continue

                # Preceding turns (up to PRECEDING_TURNS before this index)
                preceding = []
                j = i - 1
                while j >= 0 and len(preceding) < PRECEDING_TURNS:
                    prev = messages[j]
                    role = prev.get("type", prev.get("role", ""))
                    if role in ("user", "human", "assistant"):
                        t = get_content(prev)[:PRECEDING_MAX_CHARS]
                        preceding.insert(0, {"role": "user" if role in ("user", "human") else "assistant", "text": t})
                    j -= 1

                # Label: scan forward for Skill tool_use
                label = None
                for k in range(i + 1, min(i + 4, len(messages))):
                    nxt = messages[k]
                    if nxt.get("type") == "assistant":
                        label = get_skill_label(nxt)
                        if label:
                            break
                    elif nxt.get("type") in ("user", "human"):
                        break  # next user turn — stop looking

                entry = {
                    "_hash": h,
                    "session_id": session_id,
                    "timestamp": msg.get("timestamp", ""),
                    "cwd": msg.get("cwd", ""),
                    "project": project_slug,
                    "text": text,
                    "preceding_turns": preceding,
                    "label": label,
                }
                out.write(json.dumps(entry, ensure_ascii=False) + "\n")
                existing.add(h)
                written += 1

    print(f"extract: written={written} skipped_dup={skipped_dup} excluded={excluded}")
    print(f"corpus: {CORPUS_FILE}")


# ── Stats ──────────────────────────────────────────────────────────────────────
def cmd_stats(args):
    if not CORPUS_FILE.exists():
        print("No corpus yet. Run: extract")
        return
    counts = Counter()
    total = 0
    for line in open(CORPUS_FILE, encoding="utf-8", errors="ignore"):
        try:
            e = json.loads(line)
            counts[e.get("label") or "null"] += 1
            total += 1
        except Exception:
            pass
    print(f"Total: {total:,} prompts\n")
    print(f"{'Label':<40} {'Count':>6}")
    print("-" * 48)
    for label, n in counts.most_common():
        print(f"{label:<40} {n:>6,}")


# ── Sample ─────────────────────────────────────────────────────────────────────
def cmd_sample(args):
    if not CORPUS_FILE.exists():
        print("No corpus yet. Run: extract")
        return
    label = args.label
    n = args.n
    pool = []
    for line in open(CORPUS_FILE, encoding="utf-8", errors="ignore"):
        try:
            e = json.loads(line)
            if (e.get("label") or "null") == (label or "null"):
                pool.append(e["text"])
        except Exception:
            pass
    if not pool:
        print(f"No prompts found for label={label!r}")
        return
    random.shuffle(pool)
    print(f"Samples for label={label!r} (showing {min(n, len(pool))}/{len(pool)}):\n")
    for t in pool[:n]:
        print(f"  • {t[:80].replace(chr(10), ' ')!r}")


# ── Router-eval ────────────────────────────────────────────────────────────────
def _compile_patterns():
    data = json.loads(ROUTER_DATA.read_text(encoding="utf-8"))
    patterns = []
    for entry in sorted(data.get("keyword_patterns", []), key=lambda e: e["order"]):
        try:
            patterns.append((entry["intent"], re.compile(entry["pattern"], re.IGNORECASE | re.UNICODE), entry["nudge"]))
        except re.error:
            pass
    for entry in sorted(data.get("hebrew_patterns", []), key=lambda e: e["order"]):
        try:
            patterns.append((entry["intent"], re.compile(entry["pattern"], re.UNICODE), entry["nudge"]))
        except re.error:
            pass
    return patterns


def _route(text: str, patterns) -> str | None:
    for intent, compiled, _ in patterns:
        if compiled.search(text):
            return intent
    return None


# Mapping: skill slug fragment → expected router intent
_SKILL_ROUTE_MAP = [
    (re.compile(r'superpowers:brainstorming|sir-albert:brainstorm|sir-albert:discover|sir-albert:discovery-lens|sir-albert:html-plans'), 'brainstorm'),
    (re.compile(r'superpowers:systematic-debugging|sir-albert:debug'), 'debug'),
    (re.compile(r'superpowers:writing-plans|sir-albert:plan'), 'plan'),
    (re.compile(r'superpowers:executing-plans|superpowers:subagent-driven-development|sir-albert:execute'), 'execute'),
    (re.compile(r'superpowers:finishing-a-development-branch|sir-albert:build'), 'build'),
    (re.compile(r'sir-albert:handoff'), 'handoff'),
    (re.compile(r'sir-albert:resume'), 'resume'),
    (re.compile(r'sir-albert:slack-in-my-voice'), 'slack'),
    (re.compile(r'sir-albert:linkedin-in-my-voice'), 'linkedin-hebrew'),
]


def _skill_to_route(slug: str) -> str | None:
    for skill_re, route in _SKILL_ROUTE_MAP:
        if skill_re.search(slug or ""):
            return route
    return None


def cmd_router_eval(args):
    patterns = _compile_patterns()

    # Load organic prompts from transcripts (precision set)
    files = glob.glob(os.path.expanduser("~/.claude/projects/**/*.jsonl"), recursive=True)
    files = [f for f in files if "/subagents/" not in f]

    organic = []
    for f in files:
        for msg in load_jsonl(f):
            if msg.get("type") not in ("user", "human"):
                continue
            text = get_content(msg)
            if text and is_organic(text):
                organic.append(text)

    # Recall set from corpus (labeled examples)
    recall_examples = []
    if CORPUS_FILE.exists():
        for line in open(CORPUS_FILE, encoding="utf-8", errors="ignore"):
            try:
                e = json.loads(line)
                lbl = e.get("label")
                if lbl:
                    route = _skill_to_route(lbl)
                    if route:
                        recall_examples.append((e["text"], route, lbl))
            except Exception:
                pass
    # Also add known positive
    recall_examples.append(("i want to investigate my current setup and make it simpler wdyt", "brainstorm", "known-positive"))

    # Precision
    matched = 0
    per_intent = defaultdict(list)
    for p in organic:
        r = _route(p, patterns)
        if r:
            matched += 1
            per_intent[r].append(p)
    fire_rate = matched / len(organic) if organic else 0.0

    # Recall
    recall_by = defaultdict(lambda: {"expected": 0, "caught": 0, "missed": []})
    for text, expected, slug in recall_examples:
        recall_by[expected]["expected"] += 1
        if _route(text, patterns) == expected:
            recall_by[expected]["caught"] += 1
        else:
            recall_by[expected]["missed"].append((text[:80], slug))

    # Samples (5 hits per route, redacted)
    hits = {}
    for intent, prompts_list in per_intent.items():
        shuffled = prompts_list[:]
        random.shuffle(shuffled)
        hits[intent] = [p[:80].replace("\n", " ") for p in shuffled[:5]]

    # Report
    lines = [f"Precision + Recall Report — {date.today()}",
             "=" * 60,
             f"Organic prompts: {len(organic):,}  |  Fire rate: {fire_rate:.1%}  (target <15%)",
             f"Recall examples: {len(recall_examples)}",
             "",
             f"  {'Route':<20} {'Exp':>5} {'Hit':>5} {'Recall':>7} {'Matches':>8} {'Fire%':>6}",
             f"  {'-'*20}  {'-'*5} {'-'*5} {'-'*7} {'-'*8} {'-'*6}"]
    seen = set()
    for intent, _, _ in patterns:
        if intent in seen:
            continue
        seen.add(intent)
        exp = recall_by[intent]["expected"]
        caught = recall_by[intent]["caught"]
        recall_pct = f"{caught/exp:.0%}" if exp > 0 else "n/a"
        n = len(per_intent.get(intent, []))
        pr = n / len(organic) if organic else 0.0
        lines.append(f"  {intent:<20} {exp:>5} {caught:>5} {recall_pct:>7} {n:>8,} {pr:>6.1%}")

    lines += ["", "Recall misses:"]
    seen2 = set()
    for intent, _, _ in patterns:
        if intent in seen2:
            continue
        seen2.add(intent)
        missed = recall_by[intent]["missed"]
        if missed:
            lines.append(f"  [{intent}]")
            for text, slug in missed[:3]:
                lines.append(f"    MISS ({slug[:30]}): {text!r}")

    lines += ["", "Hit samples (≤5, ≤80 chars):"]
    seen3 = set()
    for intent, _, _ in patterns:
        if intent in seen3:
            continue
        seen3.add(intent)
        s = hits.get(intent, [])
        lines.append(f"\n  [{intent}] ({len(per_intent.get(intent, []))})")
        for h in (s or ["(none)"]):
            lines.append(f"    • {h!r}" if h != "(none)" else "    (none)")

    report = "\n".join(lines)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = REPORT_DIR / f"router-eval-report-{date.today()}.txt"
    report_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nReport: {report_path}", file=sys.stderr)
    return fire_rate < 0.15


# ── Eval constants (depend on _compile_patterns, defined after it) ─────────────
def _get_valid_labels():
    """Return set of valid label values derived from current router patterns."""
    return {intent for intent, _, _ in _compile_patterns()} | {"none", "ambiguous"}


# ── label-set ──────────────────────────────────────────────────────────────────
_PATH_REF_RE = re.compile(r'[/\\][a-zA-Z0-9_.-]+\.[a-zA-Z]{2,5}')
_TRAP_RE1 = re.compile(r'^(continue|resume|yes|ok|go|1|done)\b', re.IGNORECASE)
_TRAP_RE2 = re.compile(r'yes open pr|open pr|merge', re.IGNORECASE)


def cmd_label_set(args):
    merge = getattr(args, "merge", False)
    out_file = EVAL_DIR / "labeled-set.jsonl"
    checklist_path = EVAL_DIR / "labeled-set-checklist.md"

    # Guard: refuse to overwrite existing non-null labels
    existing_labels = {}
    if out_file.exists():
        existing_rows = [
            json.loads(line)
            for line in out_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        n_labeled = sum(1 for r in existing_rows if r.get("label") is not None)
        if n_labeled > 0 and not merge:
            print(f"refusing to overwrite {n_labeled} existing labels; use --merge")
            sys.exit(1)
        if merge:
            for r in existing_rows:
                if r.get("label") is not None:
                    existing_labels[r["_hash"]] = {
                        "label": r["label"],
                        "labeled_by": r.get("labeled_by"),
                        "labeled_at": r.get("labeled_at"),
                    }

    patterns = _compile_patterns()

    # Load all corpus rows once
    all_rows = list(load_jsonl(str(CORPUS_FILE)))

    # Slice 1: router matches
    router_match_rows = []
    router_match_hashes = set()
    for row in all_rows:
        text = row.get("text", "")
        if not is_organic(text):
            continue
        route = _route(text, patterns)
        if route is not None:
            h = row.get("_hash", "")
            if h and h not in router_match_hashes:
                router_match_rows.append(row)
                router_match_hashes.add(h)

    # Slice 2: task-initiating
    task_pool = []
    for row in all_rows:
        text = row.get("text", "")
        h = row.get("_hash", "")
        if h in router_match_hashes:
            continue
        if row.get("preceding_turns", []) != []:
            continue
        if len(text) <= 40:
            continue
        if _PATH_REF_RE.search(text):
            continue
        if not is_organic(text):
            continue
        task_pool.append(row)

    random.seed(42)
    task_rows = random.sample(task_pool, min(30, len(task_pool)))

    # Slice 3: negative controls
    neg_pool = []
    neg_pool_hashes = set()
    for row in all_rows:
        text = row.get("text", "")
        h = row.get("_hash", "")
        if not is_organic(text):
            continue
        if not (len(row.get("preceding_turns", [])) > 0 and len(text.strip()) < 50):
            continue
        if h not in neg_pool_hashes:
            neg_pool.append(row)
            neg_pool_hashes.add(h)

    random.seed(99)
    neg_rows = random.sample(neg_pool, min(10, len(neg_pool)))
    neg_hashes = {r.get("_hash", "") for r in neg_rows}

    # Ensure false-fire trap1 (acks) is present
    has_trap1 = any(_TRAP_RE1.search(r.get("text", "")) for r in neg_rows)
    if not has_trap1:
        extra = next(
            (r for r in neg_pool if _TRAP_RE1.search(r.get("text", "")) and r.get("_hash") not in neg_hashes),
            None
        )
        if extra:
            neg_rows.append(extra)
            neg_hashes.add(extra.get("_hash", ""))
        else:
            synthetic = {
                "_hash": "synthetic_continue",
                "text": "continue",
                "preceding_turns": [{"role": "user", "text": "prev"}],
                "label": None,
                "synthetic": True,
            }
            neg_rows.append(synthetic)

    # Ensure false-fire trap2 (open pr / merge) is present, if available
    has_trap2 = any(_TRAP_RE2.search(r.get("text", "")) for r in neg_rows)
    if not has_trap2:
        extra2 = next(
            (r for r in neg_pool if _TRAP_RE2.search(r.get("text", "")) and r.get("_hash") not in neg_hashes),
            None
        )
        if extra2:
            neg_rows.append(extra2)

    # Build output rows
    def _base(h):
        return existing_labels.get(h, {"label": None, "labeled_by": None, "labeled_at": None})

    out_rows = []
    for row in router_match_rows:
        h = row.get("_hash", "")
        b = _base(h)
        out_rows.append({
            "_hash": h,
            "text": row.get("text", ""),
            "predicted_route": _route(row.get("text", ""), patterns),
            "slice": "router_match",
            "label": b["label"],
            "labeled_by": b["labeled_by"],
            "labeled_at": b["labeled_at"],
        })
    for row in task_rows:
        h = row.get("_hash", "")
        b = _base(h)
        out_rows.append({
            "_hash": h,
            "text": row.get("text", ""),
            "predicted_route": None,
            "slice": "task_initiating",
            "label": b["label"],
            "labeled_by": b["labeled_by"],
            "labeled_at": b["labeled_at"],
        })
    for row in neg_rows:
        h = row.get("_hash", "")
        b = _base(h)
        out_rows.append({
            "_hash": h,
            "text": row.get("text", ""),
            "predicted_route": None,
            "slice": "negative_control",
            "label": b["label"],
            "labeled_by": b["labeled_by"],
            "labeled_at": b["labeled_at"],
        })

    # Write JSONL
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    out_file.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in out_rows) + "\n",
        encoding="utf-8",
    )

    # Write checklist
    def _trunc(text, n=400):
        return (text[:n] + "…") if len(text) > n else text

    cl_lines = [
        "# Labeling Checklist — W4 Router Eval",
        "",
        "## Shorthand legend",
        "- **Router matches:** `y` = predicted route is correct. Otherwise write the correct route name, `none`, or `ambiguous`.",
        "- **Task-initiating:** write a route name, `none`, or `ambiguous`.",
        "- **Negative controls:** `y` = should NOT route (`none`). Otherwise write the route it *should* take.",
        "",
    ]

    cl_lines.append("## Router matches (binary: yes this should route / no + correct route if wrong)")
    cl_lines.append("")
    for i, row in enumerate(router_match_rows):
        h = row.get("_hash", "")
        text = row.get("text", "")
        route = _route(text, patterns)
        # Skip already-labelled rows in --merge mode
        if merge and h in existing_labels:
            continue
        cl_lines.append(f"### [{i + 1}] hash={h} slice=router_match")
        cl_lines.append(f"> {_trunc(text)}")
        cl_lines.append(f"predicted: {route}")
        cl_lines.append(f"**Label:** ___  **Notes:** ___")
        cl_lines.append("")

    cl_lines.append("## Task-initiating (label: one of the route names | none | ambiguous)")
    cl_lines.append("")
    offset = len(router_match_rows)
    for i, row in enumerate(task_rows):
        h = row.get("_hash", "")
        text = row.get("text", "")
        if merge and h in existing_labels:
            continue
        cl_lines.append(f"### [{offset + i + 1}] hash={h} slice=task_initiating")
        cl_lines.append(f"> {_trunc(text)}")
        cl_lines.append(f"**Label:** ___  **Notes:** ___")
        cl_lines.append("")

    cl_lines.append("## Negative controls (binary: should NOT fire)")
    cl_lines.append("")
    offset2 = len(router_match_rows) + len(task_rows)
    for i, row in enumerate(neg_rows):
        h = row.get("_hash", "")
        text = row.get("text", "")
        if merge and h in existing_labels:
            continue
        cl_lines.append(f"### [{offset2 + i + 1}] hash={h} slice=negative_control")
        cl_lines.append(f"> {_trunc(text)}")
        cl_lines.append(f"**Label:** ___  **Notes:** ___")
        cl_lines.append("")

    if merge and existing_labels:
        already = len(existing_labels)
        remaining = sum(1 for r in out_rows if r["label"] is None)
        cl_lines.append(f"<!-- already labelled={already}, remaining={remaining} -->")

    checklist_path.write_text("\n".join(cl_lines), encoding="utf-8")

    print(
        f"router_match={len(router_match_rows)} "
        f"task_initiating={len(task_rows)} "
        f"negative_control={len(neg_rows)}"
    )


# ── validate-labels ────────────────────────────────────────────────────────────
def cmd_validate_labels(args):
    raise NotImplementedError("validate-labels not yet implemented")


# ── import-labels ──────────────────────────────────────────────────────────────
def cmd_import_labels(args):
    raise NotImplementedError("import-labels not yet implemented")


# ── p1-score ───────────────────────────────────────────────────────────────────
def cmd_p1_score(args):
    raise NotImplementedError("p1-score not yet implemented")


# ── CLI ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="sir_albert prompt corpus tool")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("extract")
    sub.add_parser("stats")

    p_sample = sub.add_parser("sample")
    p_sample.add_argument("--label", default=None)
    p_sample.add_argument("-n", type=int, default=5)

    sub.add_parser("router-eval")

    p_label_set = sub.add_parser("label-set")
    p_label_set.add_argument("--merge", action="store_true", default=False)

    p_validate = sub.add_parser("validate-labels")
    p_validate.add_argument("--file", default=str(EVAL_DIR / "labeled-set.jsonl"))

    p_import = sub.add_parser("import-labels")
    p_import.add_argument("--checklist", default=str(EVAL_DIR / "labeled-set-checklist.md"))
    p_import.add_argument("--file", default=str(EVAL_DIR / "labeled-set.jsonl"))

    p_p1 = sub.add_parser("p1-score")
    p_p1.add_argument("--file", default=str(EVAL_DIR / "labeled-set.jsonl"))

    args = parser.parse_args()
    if args.cmd == "extract":
        cmd_extract(args)
    elif args.cmd == "stats":
        cmd_stats(args)
    elif args.cmd == "sample":
        cmd_sample(args)
    elif args.cmd == "router-eval":
        ok = cmd_router_eval(args)
        sys.exit(0 if ok else 1)
    elif args.cmd == "label-set":
        cmd_label_set(args)
    elif args.cmd == "validate-labels":
        cmd_validate_labels(args)
    elif args.cmd == "import-labels":
        cmd_import_labels(args)
    elif args.cmd == "p1-score":
        cmd_p1_score(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

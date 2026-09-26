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
from datetime import date, datetime, timezone
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

    # Rehydrate labels: prefer local labeled-set.jsonl, fall back to labels.jsonl
    existing_labels: dict[str, dict] = {}

    # Always load labels.jsonl first as the durable base
    for h, lrow in _load_labels_jsonl().items():
        existing_labels[h] = {
            "label": lrow.get("label"),
            "labeled_by": lrow.get("labeled_by"),
            "labeled_at": lrow.get("labeled_at"),
        }

    # Guard: refuse to overwrite existing non-null labels in local file
    if out_file.exists():
        existing_rows = [
            json.loads(line)
            for line in out_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        # Merge local labels on top of labels.jsonl (local is more recent)
        local_labeled = {r["_hash"]: r for r in existing_rows if r.get("label") is not None}
        for h, r in local_labeled.items():
            existing_labels[h] = {
                "label": r["label"],
                "labeled_by": r.get("labeled_by"),
                "labeled_at": r.get("labeled_at"),
            }
        n_labeled = len(local_labeled)
        if n_labeled > 0 and not merge:
            print(f"refusing to overwrite {n_labeled} existing labels; use --merge")
            sys.exit(1)

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
    file_path = args.file
    valid = _get_valid_labels()
    malformed = []
    null_count = 0
    total = 0

    for idx, row in enumerate(load_jsonl(file_path)):
        total += 1
        # Check required keys
        if "_hash" not in row:
            malformed.append((idx, "missing _hash"))
            continue
        if "text" not in row:
            malformed.append((idx, "missing text"))
            continue
        label = row.get("label")
        if label is not None and label not in valid:
            malformed.append((idx, f"invalid label '{label}' at hash={row['_hash']}"))
            continue
        if label is None:
            null_count += 1

    if malformed:
        for idx, reason in malformed:
            print(f"malformed row at index {idx}: {reason}")
        sys.exit(1)

    if null_count > 0:
        print(f"remaining={null_count} / total={total}")
        sys.exit(1)

    print(f"ok: {total}/{total} labelled")


# ── labels.jsonl helpers (text-free durable record) ───────────────────────────
_LABELS_JSONL_KEYS = ("_hash", "slice", "predicted_route", "label", "labeled_by", "labeled_at")


def _write_labels_jsonl(all_rows: list[dict]) -> None:
    """Write/merge text-free labels.jsonl from all_rows that have a non-null label."""
    labels_path = EVAL_DIR / "labels.jsonl"
    # Load existing to avoid duplicates (keyed by _hash)
    existing: dict[str, dict] = {}
    if labels_path.exists():
        for row in load_jsonl(str(labels_path)):
            existing[row["_hash"]] = row
    # Merge: update with any newly-labeled rows
    for row in all_rows:
        if row.get("label") is not None:
            existing[row["_hash"]] = {k: row.get(k) for k in _LABELS_JSONL_KEYS}
    labels_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in existing.values()) + "\n",
        encoding="utf-8",
    )


def _load_labels_jsonl() -> dict[str, dict]:
    """Load text-free labels keyed by _hash from labels.jsonl (if present)."""
    labels_path = EVAL_DIR / "labels.jsonl"
    if not labels_path.exists():
        return {}
    result = {}
    for row in load_jsonl(str(labels_path)):
        result[row["_hash"]] = row
    return result


# ── import-labels ──────────────────────────────────────────────────────────────
_HEADER_RE = re.compile(r'^### \[\d+\] hash=([0-9a-f]+) slice=(\S+)', re.MULTILINE)
_LABEL_LINE_RE = re.compile(r'^\*\*Label:\*\*\s*(\S+)')
_PREDICTED_RE = re.compile(r'^predicted: (\S+)')


def cmd_import_labels(args):
    checklist_path = Path(args.checklist)
    jsonl_path = Path(args.file)
    valid = _get_valid_labels()

    if not checklist_path.exists():
        print(f"checklist not found: {checklist_path}")
        sys.exit(1)
    if not jsonl_path.exists():
        print(f"labeled-set.jsonl not found: {jsonl_path}")
        sys.exit(1)

    # Load existing rows keyed by hash
    existing = {}
    for row in load_jsonl(str(jsonl_path)):
        existing[row["_hash"]] = dict(row)

    # Parse checklist line by line
    content = checklist_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    current_hash = None
    current_slice = None
    current_predicted = None
    # Map: hash -> (label_raw, slice_, predicted_route)
    parsed: dict[str, tuple[str, str, str | None]] = {}

    for line in lines:
        m = _HEADER_RE.match(line)
        if m:
            current_hash = m.group(1)
            current_slice = m.group(2)
            current_predicted = None
            continue

        if current_hash:
            pm = _PREDICTED_RE.match(line)
            if pm:
                current_predicted = pm.group(1)
                continue

            lm = _LABEL_LINE_RE.match(line)
            if lm:
                label_raw = lm.group(1)
                if label_raw and label_raw != "___":
                    parsed[current_hash] = (label_raw, current_slice, current_predicted)
                current_hash = None
                current_slice = None
                current_predicted = None

    # Resolve shorthands and validate
    errors: list[str] = []
    resolved: dict[str, str] = {}

    for h, (label_raw, slice_, predicted) in parsed.items():
        if label_raw == "y":
            if slice_ == "router_match":
                if predicted is None:
                    errors.append(f"hash={h}: 'y' on router_match but no predicted route in checklist")
                    continue
                resolved[h] = predicted
            elif slice_ == "negative_control":
                resolved[h] = "none"
            elif slice_ == "task_initiating":
                errors.append(f"hash={h}: 'y' is not valid for task_initiating slice (no predicted route)")
                continue
            else:
                errors.append(f"hash={h}: unknown slice '{slice_}'")
                continue
        else:
            if label_raw not in valid:
                errors.append(f"hash={h}: invalid label '{label_raw}'")
                continue
            resolved[h] = label_raw

    if errors:
        for e in errors:
            print(e)
        sys.exit(1)

    # Apply — never clear existing labels
    now = datetime.now(timezone.utc).isoformat()
    for h, label in resolved.items():
        if h in existing and existing[h].get("label") is None:
            existing[h]["label"] = label
            existing[h]["labeled_by"] = "gal"
            existing[h]["labeled_at"] = now

    # Write back preserving original row order
    all_rows = list(load_jsonl(str(jsonl_path)))
    updated = []
    for row in all_rows:
        h = row["_hash"]
        if h in existing:
            updated.append(existing[h])
        else:
            updated.append(row)

    jsonl_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in updated) + "\n",
        encoding="utf-8",
    )

    # Write text-free durable record: labels.jsonl (committed artifact)
    _write_labels_jsonl(updated)

    filled = sum(1 for r in updated if r.get("label") is not None)
    print(f"imported: {len(resolved)} labels applied, {filled}/{len(updated)} total labelled")


# ── p1-score ───────────────────────────────────────────────────────────────────
_DEAD_ROUTE_DIAGNOSIS = {
    "build": (
        "Vocabulary mismatch — corpus has 86 prompts with \"open pr\"/\"merge\"/\"push\" "
        "but pattern requires \"finish the branch\"/\"ship this feature\". Fix: extend pattern."
    ),
    "resume": (
        "Regex-impossible — Gal types \"continue\" which is also his most common mid-thread reply; "
        "matching it would breach the false-fire gate. No regex fix is safe; "
        "route may need to be dropped or replaced with a context-aware signal."
    ),
    "grill": (
        "No corpus demand — broad probes ('grill', 'interview me', 'ask me questions') hit 3 prompts "
        "of 1,938, all false positives; route is unmeasurable at current corpus size. Decision to keep or drop is Gal's."
    ),
    "zoom-out": (
        "No corpus demand — broad probes ('zoom out', 'bigger picture', 'high level', 'overview') hit 11 prompts "
        "of 1,938, all false positives; route is unmeasurable at current corpus size. Decision to keep or drop is Gal's."
    ),
    "slack-hebrew": (
        "No corpus demand — only 7 Hebrew prompts of 1,938 total; "
        "route is unmeasurable at current corpus size. Decision to keep or drop is Gal's."
    ),
    "linkedin-hebrew": (
        "No corpus demand — only 7 Hebrew prompts of 1,938 total; "
        "route is unmeasurable at current corpus size. Decision to keep or drop is Gal's."
    ),
}


def cmd_p1_score(args):
    file_path = args.file
    patterns = _compile_patterns()
    all_intents_ordered = list(dict.fromkeys(intent for intent, _, _ in patterns))

    # Load rows by slice
    rm_rows = []   # router_match
    ti_rows = []   # task_initiating
    nc_rows = []   # negative_control

    for row in load_jsonl(file_path):
        s = row.get("slice", "")
        if s == "router_match":
            rm_rows.append(row)
        elif s == "task_initiating":
            ti_rows.append(row)
        elif s == "negative_control":
            nc_rows.append(row)

    gate_failures = []
    scorecard_sections = []

    # Guard: insufficient labels
    rm_labeled = [r for r in rm_rows if r.get("label") is not None]
    if len(rm_labeled) == 0:
        msg = "GATE FAIL: 0 labelled rows in router_match slice — run validate-labels first"
        print(msg)
        sys.exit(2)

    # ── Precision ─────────────────────────────────────────────────────────────
    # Exclude ambiguous from denominator (review correction 1)
    rm_scoreable = [r for r in rm_labeled if r.get("label") != "ambiguous"]
    n_ambig = len(rm_labeled) - len(rm_scoreable)
    n_correct = sum(
        1 for r in rm_scoreable
        if r.get("label") == r.get("predicted_route")
    )
    n_wrong = len(rm_scoreable) - n_correct
    precision = n_correct / len(rm_scoreable) if rm_scoreable else 0.0
    prec_pass = precision >= 0.80

    # Count "fired on non-task prompt" (router_match rows labelled none)
    fired_on_none = sum(1 for r in rm_scoreable if r.get("label") == "none")

    if not prec_pass:
        gate_failures.append(
            f"GATE FAIL: precision {precision:.1%} < 80.0%"
        )

    # ── Recall (diagnostic only) ───────────────────────────────────────────────
    ti_labeled = [
        r for r in ti_rows
        if r.get("label") not in (None, "none", "ambiguous")
    ]
    recall_hits = sum(
        1 for r in ti_labeled
        if _route(r.get("text", ""), patterns) == r.get("label")
    )
    recall = recall_hits / len(ti_labeled) if ti_labeled else 0.0

    # ── False-fire rate ───────────────────────────────────────────────────────
    # Denominator: only controls labelled 'none' (review correction 3)
    nc_none = [r for r in nc_rows if r.get("label") == "none"]
    nc_fire = sum(1 for r in nc_none if _route(r.get("text", ""), patterns) is not None)
    ff = nc_fire / len(nc_none) if nc_none else 0.0
    ff_pass = ff <= 0.10

    if not ff_pass:
        gate_failures.append(
            f"GATE FAIL: false-fire {ff:.1%} > 10.0%"
        )

    # ── Per-route breakdown ───────────────────────────────────────────────────
    route_tp: dict[str, int] = {k: 0 for k in all_intents_ordered}
    route_fp: dict[str, int] = {k: 0 for k in all_intents_ordered}
    route_fn: dict[str, int] = {k: 0 for k in all_intents_ordered}
    route_fp_samples: dict[str, list[str]] = {k: [] for k in all_intents_ordered}

    for r in rm_scoreable:
        pred = r.get("predicted_route")
        lbl = r.get("label")
        if pred in route_tp:
            if lbl == pred:
                route_tp[pred] += 1
            else:
                route_fp[pred] += 1
                # Store hash + first 80 chars for FP samples
                sample = f"hash={r.get('_hash','')} | {r.get('text','')[:80]}"
                route_fp_samples[pred].append(sample)
        # FN: label is a route but predicted was different
        if lbl in route_fn and lbl != pred:
            route_fn[lbl] += 1

    # ── Dead routes ──────────────────────────────────────────────────────────
    # Count corpus matches per intent
    corpus_match_counts: dict[str, int] = {}
    for row in load_jsonl(str(CORPUS_FILE)):
        text = row.get("text", "")
        if not is_organic(text):
            continue
        r = _route(text, patterns)
        if r:
            corpus_match_counts[r] = corpus_match_counts.get(r, 0) + 1
    dead_routes = [intent for intent in all_intents_ordered
                   if corpus_match_counts.get(intent, 0) == 0]

    # ── Build scorecard ──────────────────────────────────────────────────────
    verdict_precision = "PASS" if prec_pass else "FAIL"
    verdict_ff = "PASS" if ff_pass else "FAIL"

    scorecard_sections.append("# P1 Router Scorecard\n")
    scorecard_sections.append("## Summary\n")
    scorecard_sections.append("| Metric | Value | Bar | Result |")
    scorecard_sections.append("|---|---|---|---|")
    scorecard_sections.append(
        f"| Precision (gate) | {precision:.1%} (n={len(rm_scoreable)}) | ≥80% | {verdict_precision} |"
    )
    scorecard_sections.append(
        f"| Recall (diagnostic) | {recall:.1%} (n={len(ti_labeled)}) | ≥50% | — |"
    )
    scorecard_sections.append(
        f"| False-fire rate (gate) | {ff:.1%} (n={len(nc_none)}) | ≤10% | {verdict_ff} |"
    )
    if n_ambig:
        scorecard_sections.append(f"\nAmbiguous rows excluded from precision denominator: {n_ambig}")
    scorecard_sections.append(
        f"\nFired on non-task prompt (router_match labelled `none`): {fired_on_none} of {len(rm_scoreable)}"
    )
    scorecard_sections.append(
        "\n*The control slice is a low-power sanity check (n≈10). "
        "The real wrong-fire evidence is router_match rows labelled `none`, which precision captures.*"
    )

    if gate_failures:
        scorecard_sections.append("\n## Gate Failures\n")
        for gf in gate_failures:
            scorecard_sections.append(f"- {gf}")

    scorecard_sections.append("\n## Dead Routes\n")
    scorecard_sections.append("| Route | Corpus matches | Diagnosis |")
    scorecard_sections.append("|---|---|---|")
    for intent in dead_routes:
        diag = _DEAD_ROUTE_DIAGNOSIS.get(intent, "diagnosis: _")
        scorecard_sections.append(f"| {intent} | 0 | {diag} |")
    if not dead_routes:
        scorecard_sections.append("| — | — | No dead routes |")

    scorecard_sections.append("\n## Per-route breakdown\n")
    scorecard_sections.append("| Route | TP | FP | Precision | Note |")
    scorecard_sections.append("|---|---|---|---|---|")
    # Sort by FP descending
    sorted_routes = sorted(all_intents_ordered, key=lambda k: route_fp[k], reverse=True)
    for intent in sorted_routes:
        tp = route_tp[intent]
        fp = route_fp[intent]
        n = tp + fp
        if n >= 10:
            prec_str = f"{tp / n:.1%}"
            note = ""
        else:
            prec_str = "—"
            note = f"under-powered (n={n})"
        scorecard_sections.append(f"| {intent} | {tp} | {fp} | {prec_str} | {note} |")

    scorecard_sections.append("\n## Ranked fix list\n")
    scorecard_sections.append("Routes ordered by FP count (most problematic first):\n")
    for intent in sorted_routes:
        fp = route_fp[intent]
        if fp == 0:
            continue
        scorecard_sections.append(f"### {intent} (FP={fp})\n")
        scorecard_sections.append("Sample FP prompts:")
        for sample in route_fp_samples[intent][:3]:
            scorecard_sections.append(f"- {sample}")
        scorecard_sections.append("\nSuggested fix: _\n")

    scorecard_text = "\n".join(scorecard_sections)

    # Write scorecard regardless of pass/fail (review correction 2)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    scorecard_path = EVAL_DIR / "p1-scorecard-2026-09-26.md"
    scorecard_path.write_text(scorecard_text, encoding="utf-8")

    # Print summary
    print(f"Precision: {precision:.1%} ({verdict_precision})")
    print(f"Recall: {recall:.1%} (diagnostic)")
    print(f"False-fire: {ff:.1%} ({verdict_ff})")

    # Gate failures → exit 2 (after writing scorecard)
    if gate_failures:
        for gf in gate_failures:
            print(gf)
        sys.exit(2)


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

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
W5_DIR = REPO_ROOT / "docs" / "plans" / "2026-09-27-w5-outperform"

BASELINE_ROUTER_SHA = "1b88127"

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

# ── P2 path exclusion (broader, review correction 3 — 2026-09-26) ──────────────
# Matches: @file refs, bare slug/path.ext, docs/ dirs, .claude/ dirs, /file.ext
_P2_PATH_RE = re.compile(
    r'(@[\w./-]+|\b[\w-]+/[\w./-]+\.(md|py|json|ts|tsx|js|yaml|yml|sql|html)\b'
    r'|docs/|\.claude/|[/\\][\w.-]+\.[a-zA-Z]{2,5})'
)
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
            "preceding_turns": row.get("preceding_turns", []),
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
            "preceding_turns": row.get("preceding_turns", []),
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
            "preceding_turns": row.get("preceding_turns", []),
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
        "**Question to ask per prompt:** read alone, as the first message of a session — should the router nudge a skill?",
        "",
        "## Valid route names",
        "| Route | Nudges toward | Route | Nudges toward |",
        "|---|---|---|---|",
        "| `brainstorm` | explore / think an idea through | `plan` | write a plan / break into tickets |",
        "| `design` | design a solution → spec | `execute` | implement a plan / tickets |",
        "| `attack` | stress-test / find holes | `debug` | something is broken |",
        "| `grill` | interview me, one question at a time | `build` | finish / ship a branch, open PR |",
        "| `zoom-out` | bigger picture / how it fits | `handoff` | wrap session for a fresh one |",
        "| `slack` | Slack message in Gal's voice | `resume` | reload last handoff |",
        "| `slack-hebrew` | Slack message, Hebrew request | `linkedin-hebrew` | LinkedIn post, Hebrew request |",
        "| `none` | no skill applies | `ambiguous` | can't tell — excluded from scoring |",
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
                # People fill the blank in place ("___" -> "_y_"), so strip the blank's
                # underscores and any markdown emphasis before reading the label.
                label_raw = lm.group(1).strip("_*` ").lower()
                if label_raw == "yes":
                    label_raw = "y"
                if label_raw:
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
    # The task_initiating slice is sampled only from prompts the router did NOT fire
    # on, so "recall" over it is 0% by construction. What it measures is the router's
    # miss rate among ignored task prompts: of those, how many Gal says should route.
    ti_decided = [r for r in ti_rows if r.get("label") not in (None, "ambiguous")]
    ti_labeled = [r for r in ti_decided if r.get("label") != "none"]
    recall = len(ti_labeled) / len(ti_decided) if ti_decided else None   # miss rate

    # ── False-fire rate ───────────────────────────────────────────────────────
    # Denominator: only controls labelled 'none' (review correction 3).
    # An empty denominator is INSUFFICIENT, never a pass.
    nc_none = [r for r in nc_rows if r.get("label") == "none"]
    nc_fire = sum(1 for r in nc_none if _route(r.get("text", ""), patterns) is not None)
    ff = nc_fire / len(nc_none) if nc_none else None
    ff_pass = ff is not None and ff <= 0.10

    if ff is None:
        gate_failures.append("GATE INSUFFICIENT: 0 negative controls labelled 'none'")
    elif not ff_pass:
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
    verdict_ff = "INSUFFICIENT" if ff is None else ("PASS" if ff_pass else "FAIL")
    pct = lambda x: "n/a" if x is None else f"{x:.1%}"

    scorecard_sections.append("# P1 Router Scorecard\n")
    scorecard_sections.append("## Summary\n")
    scorecard_sections.append("| Metric | Value | Bar | Result |")
    scorecard_sections.append("|---|---|---|---|")
    scorecard_sections.append(
        f"| Precision (gate) | {precision:.1%} (n={len(rm_scoreable)}) | ≥80% | {verdict_precision} |"
    )
    scorecard_sections.append(
        f"| Miss rate among non-routed task prompts (diagnostic) | {pct(recall)} ({len(ti_labeled)} of n={len(ti_decided)} should have routed) | — | — |"
    )
    scorecard_sections.append(
        f"| False-fire rate (gate) | {pct(ff)} (n={len(nc_none)}) | ≤10% | {verdict_ff} |"
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
    # --out overrides the default EVAL_DIR path so re-runs don't overwrite the W4 record
    _out = getattr(args, "out", None)
    if _out:
        scorecard_path = Path(_out)
        scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        EVAL_DIR.mkdir(parents=True, exist_ok=True)
        scorecard_path = EVAL_DIR / "p1-scorecard-2026-09-26.md"
    scorecard_path.write_text(scorecard_text, encoding="utf-8")

    # Print summary
    print(f"Precision: {precision:.1%} ({verdict_precision})")
    print(f"Miss rate (non-routed task prompts, diagnostic): {pct(recall)} ({len(ti_labeled)}/{len(ti_decided)})")
    print(f"False-fire: {pct(ff)} (n={len(nc_none)}, {verdict_ff})")

    # Gate failures → exit 2 (after writing scorecard)
    if gate_failures:
        for gf in gate_failures:
            print(gf)
        sys.exit(2)


# ── sample-p2 ─────────────────────────────────────────────────────────────────

def cmd_sample_p2(args):
    """Select N=15 rows from the labeled set for P2 replay and write sample.jsonl.

    Three slices:
      happy_path  — router_match rows where label == predicted_route (seed 7)
      b_silent    — task_initiating (router silent) + negative_control rows
                    both labelled with a route (seed 8)
      control     — router_match labelled none (wrong_fire, priority)
                    then task_initiating labelled none (no_route_task) (seed 9)
    negative_control rows labelled none are excluded from every pool.
    ambiguous rows are excluded from P2 entirely.
    """
    file_path = args.file
    patterns = _compile_patterns()

    path_excl = {"happy_path": 0, "b_silent": 0, "control": 0}

    all_rows = list(load_jsonl(file_path))

    def _has_path(text: str) -> bool:
        return bool(_P2_PATH_RE.search(text))

    # ── Happy-path pool ───────────────────────────────────────────────────────
    # router_match rows where label == predicted_route (neither none nor ambiguous)
    happy_pool = []
    for row in all_rows:
        if row.get("slice") != "router_match":
            continue
        label = row.get("label")
        if label is None or label in ("none", "ambiguous"):
            continue
        if row.get("predicted_route") != label:
            continue
        text = row.get("text", "")
        if _has_path(text):
            path_excl["happy_path"] += 1
            continue
        happy_pool.append(row)

    # ── B-silent pool ─────────────────────────────────────────────────────────
    # (1) task_initiating: non-none/non-ambiguous label AND router fires nothing
    # (2) negative_control: labelled with a route (router missed by construction)
    b_silent_pool = []
    for row in all_rows:
        s = row.get("slice")
        label = row.get("label")
        if label is None or label in ("none", "ambiguous"):
            continue
        text = row.get("text", "")
        if s == "task_initiating":
            if _route(text, patterns) is not None:
                continue  # router fires → not b_silent
            if _has_path(text):
                path_excl["b_silent"] += 1
                continue
            b_silent_pool.append(row)
        elif s == "negative_control":
            if _has_path(text):
                path_excl["b_silent"] += 1
                continue
            b_silent_pool.append(row)

    # ── Control pool ──────────────────────────────────────────────────────────
    # (a) router_match labelled none → wrong_fire (priority)
    # (b) task_initiating labelled none → no_route_task (fill)
    # negative_control is excluded entirely; ambiguous is excluded
    control_a_pool: list[dict] = []  # wrong_fire
    control_b_pool: list[dict] = []  # no_route_task
    for row in all_rows:
        s = row.get("slice")
        label = row.get("label")
        if label is None or label != "none":
            continue
        if s not in ("router_match", "task_initiating"):
            continue  # excludes negative_control
        text = row.get("text", "")
        if _has_path(text):
            path_excl["control"] += 1
            continue
        if s == "router_match":
            control_a_pool.append(row)
        else:
            control_b_pool.append(row)

    control_total = len(control_a_pool) + len(control_b_pool)

    # ── Guard: INSUFFICIENT (0 candidates in any slice) ───────────────────────
    insufficient = []
    if len(happy_pool) == 0:
        insufficient.append("happy_path")
    if len(b_silent_pool) == 0:
        insufficient.append("b_silent")
    if control_total == 0:
        insufficient.append("control")

    if insufficient:
        for sl in insufficient:
            print(f"INSUFFICIENT: {sl} has 0 candidates")
        sys.exit(2)

    # ── WARN for <5 candidates ────────────────────────────────────────────────
    if len(happy_pool) < 5:
        print(f"WARN: happy_path only {len(happy_pool)} candidates")
    if len(b_silent_pool) < 5:
        print(f"WARN: b_silent only {len(b_silent_pool)} candidates")
    if control_total < 5:
        print(f"WARN: control only {control_total} candidates")

    # ── Sample ────────────────────────────────────────────────────────────────
    random.seed(7)
    happy_sample = random.sample(happy_pool, min(5, len(happy_pool)))

    random.seed(8)
    b_silent_sample = random.sample(b_silent_pool, min(5, len(b_silent_pool)))

    # Control: seed 9, drain (a) first, fill from (b)
    random.seed(9)
    n_a = min(5, len(control_a_pool))
    control_a_sample = random.sample(control_a_pool, n_a)
    remaining = 5 - n_a
    control_b_sample = (
        random.sample(control_b_pool, min(remaining, len(control_b_pool)))
        if remaining > 0 and control_b_pool
        else []
    )
    control_sample = control_a_sample + control_b_sample

    # ── Tag slices ────────────────────────────────────────────────────────────
    for r in happy_sample:
        r["p2_slice"] = "happy_path"
    for r in b_silent_sample:
        r["p2_slice"] = "b_silent"
    for r in control_a_sample:
        r["p2_slice"] = "control"
        r["p2_control_kind"] = "wrong_fire"
    for r in control_b_sample:
        r["p2_slice"] = "control"
        r["p2_control_kind"] = "no_route_task"

    # ── Interleave: rotate h, b, c (tranche-friendly ordering) ───────────────
    output_rows: list[dict] = []
    max_n = max(len(happy_sample), len(b_silent_sample), len(control_sample))
    for i in range(max_n):
        if i < len(happy_sample):
            output_rows.append(happy_sample[i])
        if i < len(b_silent_sample):
            output_rows.append(b_silent_sample[i])
        if i < len(control_sample):
            output_rows.append(control_sample[i])

    # ── Format and write ──────────────────────────────────────────────────────
    def _fmt(r: dict) -> dict:
        out: dict = {
            "_hash": r.get("_hash"),
            "text": r.get("text"),
            "slice": r.get("slice"),
            "label": r.get("label"),
            "predicted_route": r.get("predicted_route"),
            "p2_slice": r.get("p2_slice"),
            "preceding_turns": r.get("preceding_turns", []),
        }
        if r.get("p2_slice") == "control":
            out["p2_control_kind"] = r.get("p2_control_kind")
        return out

    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    sample_path = EVAL_DIR / "sample.jsonl"
    sample_path.write_text(
        "\n".join(json.dumps(_fmt(r), ensure_ascii=False) for r in output_rows) + "\n",
        encoding="utf-8",
    )

    total_excl = sum(path_excl.values())
    print(
        f"sample: happy_path={len(happy_sample)} b_silent={len(b_silent_sample)} "
        f"control={len(control_sample)} "
        f"path_excluded={total_excl} "
        f"(happy_path={path_excl['happy_path']} b_silent={path_excl['b_silent']} "
        f"control={path_excl['control']})"
    )


# ── label-set-p3 ──────────────────────────────────────────────────────────────

def _load_baseline_router_data(path_override: str | None = None) -> dict:
    """Load router_data.json from the 1b88127 baseline commit, or from a file override."""
    if path_override:
        return json.loads(Path(path_override).read_text(encoding="utf-8"))
    import subprocess
    result = subprocess.run(
        ["git", "show", f"{BASELINE_ROUTER_SHA}:plugins/sir-albert/hooks/router_data.json"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git show {BASELINE_ROUTER_SHA}:... failed: {result.stderr.strip()}"
        )
    return json.loads(result.stdout)


def _compile_patterns_from_data(router_data: dict):
    """Compile keyword patterns from a router_data dict."""
    patterns = []
    for entry in sorted(router_data.get("keyword_patterns", []), key=lambda e: e["order"]):
        try:
            patterns.append(
                (entry["intent"], re.compile(entry["pattern"], re.IGNORECASE | re.UNICODE), entry.get("nudge", ""))
            )
        except re.error:
            pass
    for entry in sorted(router_data.get("hebrew_patterns", []), key=lambda e: e["order"]):
        try:
            patterns.append(
                (entry["intent"], re.compile(entry["pattern"], re.UNICODE), entry.get("nudge", ""))
            )
        except re.error:
            pass
    return patterns


# P3 valid labeling values (task routes + sentinels; excludes legacy/low-demand routes)
_P3_VALID_LABELS = {"brainstorm", "plan", "execute", "debug", "build", "handoff", "none", "ambiguous"}

# Targets per stratum
_P3_ROUTER_MATCH_N = 15
_P3_TASK_INITIATING_N = 25
_P3_NEGATIVE_CONTROL_N = 10


_P3_SESSION_EXCLUDE_PREFIX = "6834d4ec"


def cmd_label_set_p3(args):
    """Slice corpus into a P3 held-out labeling set, using Amendment 1 exclusion rules.

    Amendment 1 exclusion rules (applied in this order):
      Rule 1: every _hash in --exclude-hashes files (labels.jsonl source)
      Rule 2: every _hash in --exclude-hashes files (sample.jsonl source)
              (rules 1 and 2 share the same --exclude-hashes flag)
      Rule 3: rows where the current live router fires AND baseline (1b88127) doesn't
      Rule 4: every row from session whose session_id starts with --session-prefix

    args:
      exclude_hashes     list of JSONL files; every _hash in them is excluded
      current_router_data optional path to current router JSON (default: live ROUTER_DATA)
      session_prefix     session_id prefix to exclude (default: "6834d4ec")
      seed               random seed (default 7)
      router_data        optional path override for baseline router JSON
      out_dir            output directory (default W5_DIR)
    """
    seed = getattr(args, "seed", 7)
    router_data_override = getattr(args, "router_data", None)
    out_dir = Path(getattr(args, "out_dir", None) or W5_DIR)
    # Support both old --exclude and new --exclude-hashes for backward compat
    exclude_files = (
        getattr(args, "exclude_hashes", None)
        or getattr(args, "exclude", None)
        or []
    )
    current_router_data_path = getattr(args, "current_router_data", None)
    session_prefix = getattr(args, "session_prefix", None) or _P3_SESSION_EXCLUDE_PREFIX

    # ── Load baseline router ──────────────────────────────────────────────────
    router_data = _load_baseline_router_data(router_data_override)
    patterns = _compile_patterns_from_data(router_data)

    def _baseline_route(text: str) -> str | None:
        for intent, compiled, _ in patterns:
            if compiled.search(text):
                return intent
        return None

    # ── Load current (live/ticket-08) router for rule 3 ──────────────────────
    if current_router_data_path:
        current_router_data = json.loads(Path(current_router_data_path).read_text(encoding="utf-8"))
    else:
        current_router_data = json.loads(ROUTER_DATA.read_text(encoding="utf-8"))
    current_patterns = _compile_patterns_from_data(current_router_data)

    def _current_route(text: str) -> str | None:
        for intent, compiled, _ in current_patterns:
            if compiled.search(text):
                return intent
        return None

    # ── Rules 1 + 2: load exclude hashes from JSONL files ────────────────────
    exclude_hashes: set[str] = set()
    for fpath in exclude_files:
        for row in load_jsonl(fpath):
            h = row.get("_hash", "")
            if h:
                exclude_hashes.add(h)

    # ── Load corpus ───────────────────────────────────────────────────────────
    all_rows = list(load_jsonl(str(CORPUS_FILE)))

    # ── Build full exclude set: rules 1+2 (files) + rule 3 (08-eyeballed) + rule 4 (session) ──
    for row in all_rows:
        h = row.get("_hash", "")
        if not h:
            continue
        text = row.get("text", "")
        session_id = row.get("session_id", "")
        # Rule 3: current router fires AND baseline router doesn't (ticket 08 eyeballed)
        if _current_route(text) is not None and _baseline_route(text) is None:
            exclude_hashes.add(h)
        # Rule 4: row from the W5 planning session
        if session_id and session_id.startswith(session_prefix):
            exclude_hashes.add(h)

    # ── Slice 1: router_match (baseline router fires, not excluded) ───────────
    router_match_rows: list[dict] = []
    router_match_hashes: set[str] = set()
    for row in all_rows:
        h = row.get("_hash", "")
        if h in exclude_hashes:
            continue
        text = row.get("text", "")
        if not is_organic(text):
            continue
        route = _baseline_route(text)
        if route is not None and h not in router_match_hashes:
            router_match_rows.append(row)
            router_match_hashes.add(h)

    # ── Slice 2: task-initiating (router silent, not excluded, task heuristic) ─
    task_pool: list[dict] = []
    for row in all_rows:
        h = row.get("_hash", "")
        if h in exclude_hashes or h in router_match_hashes:
            continue
        text = row.get("text", "")
        if not is_organic(text):
            continue
        if row.get("preceding_turns", []) != []:
            continue
        if len(text) <= 40:
            continue
        if _PATH_REF_RE.search(text):
            continue
        task_pool.append(row)

    random.seed(seed)
    task_rows = random.sample(task_pool, min(_P3_TASK_INITIATING_N, len(task_pool)))

    # ── Slice 3: negative_control (short with preceding_turns, not excluded) ──
    neg_pool: list[dict] = []
    neg_pool_hashes: set[str] = set()
    task_hashes = {r.get("_hash", "") for r in task_rows}
    for row in all_rows:
        h = row.get("_hash", "")
        if h in exclude_hashes or h in router_match_hashes or h in task_hashes:
            continue
        text = row.get("text", "")
        if not is_organic(text):
            continue
        if not (len(row.get("preceding_turns", [])) > 0 and len(text.strip()) < 50):
            continue
        if h not in neg_pool_hashes:
            neg_pool.append(row)
            neg_pool_hashes.add(h)

    random.seed(seed)
    neg_rows = random.sample(neg_pool, min(_P3_NEGATIVE_CONTROL_N, len(neg_pool)))

    # ── Sample router_match (take up to target; all if below target) ──────────
    if len(router_match_rows) > _P3_ROUTER_MATCH_N:
        random.seed(seed)
        router_match_sample = random.sample(router_match_rows, _P3_ROUTER_MATCH_N)
    else:
        router_match_sample = router_match_rows

    # ── Build output rows ─────────────────────────────────────────────────────
    out_rows: list[dict] = []
    for row in router_match_sample:
        h = row.get("_hash", "")
        out_rows.append({
            "_hash": h,
            "text": row.get("text", ""),
            "predicted_route": _baseline_route(row.get("text", "")),
            "slice": "router_match",
            "label": None,
            "labeled_by": None,
            "labeled_at": None,
            "preceding_turns": row.get("preceding_turns", []),
        })
    for row in task_rows:
        h = row.get("_hash", "")
        out_rows.append({
            "_hash": h,
            "text": row.get("text", ""),
            "predicted_route": None,
            "slice": "task_initiating",
            "label": None,
            "labeled_by": None,
            "labeled_at": None,
            "preceding_turns": row.get("preceding_turns", []),
        })
    for row in neg_rows:
        h = row.get("_hash", "")
        out_rows.append({
            "_hash": h,
            "text": row.get("text", ""),
            "predicted_route": None,
            "slice": "negative_control",
            "label": None,
            "labeled_by": None,
            "labeled_at": None,
            "preceding_turns": row.get("preceding_turns", []),
        })

    # ── Write JSONL ───────────────────────────────────────────────────────────
    out_dir.mkdir(parents=True, exist_ok=True)
    out_jsonl = out_dir / "labeled-set-p3.jsonl"
    out_jsonl.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in out_rows) + "\n",
        encoding="utf-8",
    )

    # ── Write checklist ───────────────────────────────────────────────────────
    def _trunc(text: str, n: int = 400) -> str:
        return (text[:n] + "…") if len(text) > n else text

    def _fmt_preceding(turns: list) -> list[str]:
        lines = []
        for t in turns:
            role = t.get("role", "?")
            txt = _trunc(t.get("text", ""), 200)
            lines.append(f"  [{role}]: {txt}")
        return lines

    cl_lines = [
        "# Labeling Checklist — W5 P3 Held-Out Set",
        "",
        "## Shorthand legend",
        "- **Router matches:** `y` = predicted route is correct. Otherwise write the correct route name, `none`, or `ambiguous`.",
        "- **Task-initiating:** write a route name, `none`, or `ambiguous`.",
        "- **Negative controls:** `y` = should NOT route (`none`). Otherwise write the route it *should* take.",
        "",
        "**Question to ask per prompt:** read alone, as the first message of a session — should the router nudge a skill?",
        "",
        "## Valid labels",
        "| Label | Nudges toward |",
        "|---|---|",
        "| `brainstorm` | explore / think an idea through |",
        "| `plan` | write a plan / break into tickets |",
        "| `execute` | implement a plan / tickets |",
        "| `debug` | something is broken |",
        "| `build` | finish / ship a branch, open PR |",
        "| `handoff` | wrap session for a fresh one |",
        "| `none` | no skill applies |",
        "| `ambiguous` | can't tell — excluded from scoring |",
        "",
    ]

    cl_lines.append("## Router matches (binary: yes this should route / no + correct route if wrong)")
    cl_lines.append("")
    for i, row in enumerate(router_match_sample):
        h = row.get("_hash", "")
        text = row.get("text", "")
        route = _baseline_route(text)
        cl_lines.append(f"### [{i + 1}] hash={h} slice=router_match")
        prec = row.get("preceding_turns", [])
        if prec:
            cl_lines.append("**Preceding turns:**")
            cl_lines.extend(_fmt_preceding(prec))
        cl_lines.append(f"> {_trunc(text)}")
        cl_lines.append(f"predicted: {route}")
        cl_lines.append("**Label:** ___  **Notes:** ___")
        cl_lines.append("")

    cl_lines.append("## Task-initiating (label: one of the route names | none | ambiguous)")
    cl_lines.append("")
    offset = len(router_match_sample)
    for i, row in enumerate(task_rows):
        h = row.get("_hash", "")
        text = row.get("text", "")
        cl_lines.append(f"### [{offset + i + 1}] hash={h} slice=task_initiating")
        prec = row.get("preceding_turns", [])
        if prec:
            cl_lines.append("**Preceding turns:**")
            cl_lines.extend(_fmt_preceding(prec))
        cl_lines.append(f"> {_trunc(text)}")
        cl_lines.append("**Label:** ___  **Notes:** ___")
        cl_lines.append("")

    cl_lines.append("## Negative controls (binary: should NOT fire — label: none | or correct route if wrong)")
    cl_lines.append("")
    offset2 = len(router_match_sample) + len(task_rows)
    for i, row in enumerate(neg_rows):
        h = row.get("_hash", "")
        text = row.get("text", "")
        cl_lines.append(f"### [{offset2 + i + 1}] hash={h} slice=negative_control")
        prec = row.get("preceding_turns", [])
        if prec:
            cl_lines.append("**Preceding turns:**")
            cl_lines.extend(_fmt_preceding(prec))
        cl_lines.append(f"> {_trunc(text)}")
        cl_lines.append("**Label:** ___  **Notes:** ___")
        cl_lines.append("")

    checklist_path = out_dir / "labeled-set-p3-checklist.md"
    checklist_path.write_text("\n".join(cl_lines), encoding="utf-8")

    print(
        f"router_match={len(router_match_sample)} "
        f"task_initiating={len(task_rows)} "
        f"negative_control={len(neg_rows)} "
        f"total={len(out_rows)}"
    )
    if len(router_match_rows) == 0:
        print("WARN: 0 router_match candidates after exclusion — all baseline-router matches are in the exclude set")


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
    p_p1.add_argument("--out", default=None,
                      help="Write scorecard to this path instead of the default EVAL_DIR location")

    p_sample_p2 = sub.add_parser("sample-p2")
    p_sample_p2.add_argument("--file", default=str(EVAL_DIR / "labeled-set.jsonl"))

    p_label_set_p3 = sub.add_parser("label-set-p3")
    p_label_set_p3.add_argument(
        "--exclude-hashes", nargs="+", default=[], dest="exclude_hashes",
        metavar="FILE",
        help="JSONL files whose _hashes are excluded (Amendment 1 rules 1+2: labels.jsonl, sample.jsonl)",
    )
    p_label_set_p3.add_argument("--seed", type=int, default=7)
    p_label_set_p3.add_argument(
        "--router-data", default=None, dest="router_data",
        metavar="FILE",
        help=f"Baseline router_data.json override (default: git show {BASELINE_ROUTER_SHA}:...)",
    )
    p_label_set_p3.add_argument(
        "--current-router-data", default=None, dest="current_router_data",
        metavar="FILE",
        help="Current (live) router_data.json override for rule 3 (default: live hooks/router_data.json)",
    )
    p_label_set_p3.add_argument(
        "--session-prefix", default=_P3_SESSION_EXCLUDE_PREFIX, dest="session_prefix",
        metavar="PREFIX",
        help=f"Exclude rows whose session_id starts with this prefix (default: {_P3_SESSION_EXCLUDE_PREFIX})",
    )
    p_label_set_p3.add_argument(
        "--out-dir", default=None, dest="out_dir",
        metavar="DIR",
        help="Output directory (default: docs/plans/2026-09-27-w5-outperform/)",
    )

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
    elif args.cmd == "sample-p2":
        cmd_sample_p2(args)
    elif args.cmd == "label-set-p3":
        cmd_label_set_p3(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

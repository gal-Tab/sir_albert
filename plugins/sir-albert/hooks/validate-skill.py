#!/usr/bin/env python3
"""validate-skill.py — skill-authoring guardrail for the sir_albert plugin.

Fires on SKILL.md writes/edits *under the sir_albert plugin only*.
- Structural rules (agentskills.io spec): BLOCK on violation (PreToolUse/Write, exit 2).
- Quality rules (superpowers:writing-skills SDO): WARN only (never block).

Wiring (hooks/hooks.json):
  PreToolUse  matcher "Write"          -> hard-blocks structurally invalid creates
  PostToolUse matcher "Edit|MultiEdit" -> warn-only (file already written)

Fail-open by design: any unexpected error -> exit 0, so a bug here never
bricks all edits (same philosophy as freeze-guard.sh).
"""

import json
import os
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FIRST_PERSON_RE = re.compile(r"\b(I|I'll|I'm|I've|my|me)\b", re.IGNORECASE)

DESC_HARD_MAX = 1024   # agentskills spec hard limit
DESC_SOFT_MAX = 500    # writing-skills recommendation
BODY_SOFT_MAX_LINES = 500  # writing-skills: keep SKILL.md under 500 lines


def parse_frontmatter(text):
    """Return (frontmatter_dict, body_str) or (None, text) if no frontmatter.

    Minimal single-purpose YAML reader: top-level `key: value` scalars plus
    `|`/`>` block scalars. Enough for `name` and `description`. No deps.
    """
    if not text.startswith("---"):
        return None, text
    # Split into the frontmatter block and the body.
    m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?(.*)$", text, re.DOTALL)
    if not m:
        return None, text
    fm_raw, body = m.group(1), m.group(2)

    data = {}
    cur_key = None
    block_lines = None
    for line in fm_raw.splitlines():
        # Continuation of a block scalar (indented line).
        if block_lines is not None and (line.startswith((" ", "\t")) or line.strip() == ""):
            block_lines.append(line.strip())
            continue
        elif block_lines is not None:
            data[cur_key] = " ".join(l for l in block_lines if l).strip()
            block_lines = None
        km = re.match(r"^([A-Za-z0-9_-]+):[ \t]*(.*)$", line)
        if not km:
            continue
        key, val = km.group(1), km.group(2).strip()
        if val in ("|", ">", "|-", ">-", "|+", ">+"):
            cur_key = key
            block_lines = []
            continue
        # Strip matching surrounding quotes.
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        data[key] = val
    if block_lines is not None:
        data[cur_key] = " ".join(l for l in block_lines if l).strip()
    return data, body


def check(content, dir_name):
    """Return (hard_violations, soft_warnings) for a SKILL.md's content."""
    hard, soft = [], []

    fm, body = parse_frontmatter(content)
    if fm is None:
        hard.append("Missing YAML frontmatter (file must start with a '---' block containing name + description).")
        return hard, soft  # can't check fields without frontmatter

    # ---- name (structural / block) ----
    name = fm.get("name")
    if not name:
        hard.append("Missing required frontmatter field: `name`.")
    else:
        if len(name) > 64:
            hard.append(f"`name` is {len(name)} chars; max is 64.")
        if not NAME_RE.match(name):
            if name != name.lower():
                hard.append(f"`name` must be lowercase: '{name}'.")
            elif name.startswith("-") or name.endswith("-"):
                hard.append(f"`name` must not start or end with a hyphen: '{name}'.")
            elif "--" in name:
                hard.append(f"`name` must not contain consecutive hyphens: '{name}'.")
            else:
                hard.append(f"`name` may only contain lowercase letters, digits, and single hyphens: '{name}'.")
        if dir_name and name and name != dir_name:
            hard.append(f"`name` ('{name}') must match the parent directory name ('{dir_name}').")

    # ---- description (structural + quality) ----
    desc = fm.get("description")
    if not desc:
        hard.append("Missing required frontmatter field: `description`.")
    else:
        if len(desc) > DESC_HARD_MAX:
            hard.append(f"`description` is {len(desc)} chars; max is {DESC_HARD_MAX}.")
        # Quality (warn only)
        if len(desc) > DESC_SOFT_MAX:
            soft.append(f"`description` is {len(desc)} chars; writing-skills recommends under {DESC_SOFT_MAX}.")
        if not re.match(r"^\s*use when\b", desc, re.IGNORECASE):
            soft.append("`description` should start with 'Use when...' and describe triggering conditions, not the workflow.")
        if FIRST_PERSON_RE.search(desc):
            soft.append("`description` reads first-person; use third person (it's injected into the system prompt).")

    # ---- body length (quality) ----
    body_lines = body.count("\n") + 1 if body.strip() else 0
    if body_lines > BODY_SOFT_MAX_LINES:
        soft.append(f"SKILL.md body is ~{body_lines} lines; writing-skills recommends under {BODY_SOFT_MAX_LINES} (move detail to references/).")

    return hard, soft


def in_scope(target):
    """True only for a SKILL.md located under the sir_albert plugin root."""
    if not target:
        return False
    p = Path(target)
    if p.name != "SKILL.md":
        return False
    roots = [os.environ.get("CLAUDE_PLUGIN_ROOT"), str(Path(__file__).resolve().parents[1])]
    roots = [os.path.realpath(r) for r in roots if r]
    rt = os.path.realpath(str(p))
    return any(rt == r or rt.startswith(r + os.sep) for r in roots)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail-open

    tool_input = payload.get("tool_input", {}) or {}
    target = tool_input.get("file_path")
    if not in_scope(target):
        sys.exit(0)

    event = payload.get("hook_event_name", "")
    is_pre = event == "PreToolUse"

    # Source of truth for content:
    #   PreToolUse/Write -> the not-yet-written `content` param (lets us block).
    #   Otherwise        -> the file on disk (already written by the edit).
    content = tool_input.get("content") if is_pre else None
    if content is None:
        try:
            content = Path(target).read_text(encoding="utf-8")
        except Exception:
            sys.exit(0)  # fail-open (nothing to validate)

    dir_name = Path(target).resolve().parent.name
    hard, soft = check(content, dir_name)

    if hard and is_pre:
        lines = ["🔴 skill-guardrail BLOCKED — structural violations in SKILL.md:"]
        lines += [f"  • {v}" for v in hard]
        lines += [f"  ⚠ {w}" for w in soft]
        lines.append("Fix the structural (🔴) issues and re-write. See agentskills.io/specification.")
        print("\n".join(lines), file=sys.stderr)
        sys.exit(2)

    # PostToolUse (edit) or PreToolUse with only warnings: advise, never block.
    msgs = []
    if hard:
        msgs += [f"🔴 (not blocked — edit) {v}" for v in hard]
    msgs += [f"⚠ {w}" for w in soft]
    if msgs:
        print("skill-guardrail — " + Path(target).parent.name + "/SKILL.md:\n" + "\n".join(f"  {m}" for m in msgs), file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""UserPromptSubmit hook — phrase-level keyword nudger.

Reads JSON from stdin: {"prompt": "..."}
Emits a one-line nudge or exits silently (empty stdout).
<50 ms, no network, no LLM.
"""
import json
import os
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_FILE = SCRIPT_DIR / "router_data.json"
RIGOR_DIR = Path(os.environ.get("SIR_ALBERT_RIGOR_DIR", Path.home() / ".claude" / "sir-albert" / "rigor"))

_RIGOR_RE = re.compile(r"^\s*(fast|ship|deep|auto)\s*:", re.IGNORECASE)

_NUDGE_RE = re.compile(r"^→ /sir-albert:(\S+)(?:\s+(.+))?$")


def format_directive(nudge: str) -> str:
    """Convert a bare '→ /sir-albert:<skill>[ <mode>]' nudge into an imperative directive.

    Any nudge that doesn't match the pattern is returned unchanged.
    """
    m = _NUDGE_RE.match(nudge)
    if not m:
        return nudge
    skill = m.group(1)
    mode_raw = m.group(2)
    if mode_raw:
        # Strip surrounding parens if present (e.g. "(explore mode)" → "explore mode")
        mode = mode_raw.strip().strip("()")
        mode_part = f" ({mode})"
    else:
        mode_part = ""
    return (
        f"sir-albert router: this prompt matches /sir-albert:{skill}{mode_part}. "
        f'Invoke the Skill tool with skill="sir-albert:{skill}" before responding, '
        f"including before any clarifying question. "
        f"Skip only if the prompt is clearly not this kind of request."
    )


def rigor_level(prompt: str, session_id: str):
    """Return (level, changed). A `fast:`/`ship:`/`deep:` prefix sticks per session; `auto:` clears it."""
    state = RIGOR_DIR / f"{session_id}.txt" if session_id else None
    m = _RIGOR_RE.match(prompt)
    if m:
        level = m.group(1).lower()
        if state:
            try:
                if level == "auto":
                    state.unlink(missing_ok=True)
                else:
                    state.parent.mkdir(parents=True, exist_ok=True)
                    state.write_text(level, encoding="utf-8")
            except OSError:
                pass
        return (None if level == "auto" else level), True
    if state and state.exists():
        try:
            return state.read_text(encoding="utf-8").strip() or None, False
        except OSError:
            pass
    return None, False


def load_patterns(data: dict) -> list:
    patterns = []
    for entry in sorted(data.get("keyword_patterns", []), key=lambda e: e["order"]):
        try:
            compiled = re.compile(entry["pattern"], re.IGNORECASE | re.UNICODE)
            patterns.append((compiled, entry["nudge"]))
        except re.error as e:
            print(f"[sir-albert] bad pattern {entry['pattern']!r}: {e}", file=sys.stderr)
    for entry in sorted(data.get("hebrew_patterns", []), key=lambda e: e["order"]):
        try:
            compiled = re.compile(entry["pattern"], re.UNICODE)
            patterns.append((compiled, entry["nudge"]))
        except re.error as e:
            print(f"[sir-albert] bad Hebrew pattern {entry['pattern']!r}: {e}", file=sys.stderr)
    return patterns


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        prompt = payload.get("prompt", "")
        session_id = str(payload.get("session_id", ""))
    except Exception:
        sys.exit(0)

    if not prompt:
        sys.exit(0)

    # Harness-injected text (task notifications, system reminders) also reaches this
    # hook; a match there would force a skill load nobody asked for.
    head = prompt.lstrip()[:200]
    if head.startswith(("<task-notification", "<system-reminder")) or "[SYSTEM NOTIFICATION" in head:
        sys.exit(0)

    level, changed = rigor_level(prompt, session_id)
    if changed:
        print(
            f"sir-albert rigor: Gal set {level} for this session (os/rules/rigor.md)."
            if level else "sir-albert rigor: auto — pick the level per step (os/rules/rigor.md)."
        )
    if level == "fast":
        # Fast mode: no skill directives — they're exactly the per-turn overhead fast removes.
        sys.exit(0)

    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[sir-albert] ERROR loading router_data: {e}", file=sys.stderr)
        sys.exit(0)

    patterns = load_patterns(data)
    for compiled, nudge in patterns:
        if compiled.search(prompt):
            print(format_directive(nudge))
            sys.exit(0)

    # No match — silent exit
    sys.exit(0)


if __name__ == "__main__":
    main()

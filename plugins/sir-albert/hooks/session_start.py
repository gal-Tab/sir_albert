#!/usr/bin/env python3
"""SessionStart hook — injects ≤800 chars of sir_albert context."""
import fnmatch
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", str(SCRIPT_DIR)))
CONTEXT_FILE = SCRIPT_DIR / "HOOK_CONTEXT.md"
DATA_FILE = SCRIPT_DIR / "router_data.json"


def detect_packs(cwd: Path, data: dict) -> str:
    packs = []
    for sig in data.get("pack_signals", []):
        pack = sig["pack"]
        stype = sig["signal_type"]
        pattern = sig["pattern"]
        matched = False
        if stype == "glob":
            matched = bool(list(cwd.glob(pattern)))
        elif stype == "file":
            matched = (cwd / pattern).exists()
        elif stype == "dir":
            matched = (cwd / pattern).is_dir()
        elif stype == "dir_pair":
            a, b = pattern.split("+")
            matched = (cwd / a).exists() and (cwd / b).exists()
        if matched and pack not in packs:
            packs.append(pack)
    return ", ".join(packs) if packs else "(none detected)"


def detect_resume(cwd: Path) -> str:
    if os.environ.get("DISABLE_RESUME_HINT"):
        return ""
    mem = cwd / ".memory-bank"
    if not mem.is_dir():
        return ""
    files = sorted(mem.glob("HANDOFF-*.md"))
    if not files:
        return ""
    name = files[-1].name
    return f"Resume: .memory-bank/{name} found — run /sir-albert:resume"


def main():
    cwd = Path(os.environ.get("PWD", "."))

    try:
        template = CONTEXT_FILE.read_text(encoding="utf-8")
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[sir-albert] ERROR loading data: {e}", file=sys.stderr)
        sys.exit(0)

    pack_str = detect_packs(cwd, data)
    resume_str = detect_resume(cwd)

    filled = template.replace("{PACK_LIST}", pack_str).replace("{RESUME_HINT}", resume_str).rstrip()

    if len(filled) > 800:
        print(
            f"[sir-albert] WARNING: injection {len(filled)} chars > 800, skipping",
            file=sys.stderr,
        )
        sys.exit(0)

    # JSON-encode the string value
    encoded = json.dumps(filled)
    print(
        json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": filled,
            }
        })
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Redirect: use prompt_corpus.py router-eval instead.

This script is superseded by plugins/sir-albert/tools/prompt_corpus.py router-eval
(ticket 04c). Kept as a redirect so old bookmarks still work.
"""
import subprocess
import sys
from pathlib import Path

CORPUS_TOOL = Path(__file__).parent.parent / "plugins" / "sir-albert" / "tools" / "prompt_corpus.py"

print("[redirect] Use: python3 plugins/sir-albert/tools/prompt_corpus.py router-eval")
result = subprocess.run([sys.executable, str(CORPUS_TOOL), "router-eval"] + sys.argv[1:])
sys.exit(result.returncode)

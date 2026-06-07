#!/usr/bin/env bash
# Publish skills from this repo to ~/.claude/skills/ (flat, ready for Claude Code)
#
# Usage:
#   ./tools/publish-skills.sh --all              # publish all skills in this repo
#   ./tools/publish-skills.sh <skill-name>       # publish a single skill by name
#
# Each skill folder is copied to ~/.claude/skills/<skill-name>/
# The category subfolder is stripped — ~/.claude/skills/ is always flat.

set -euo pipefail

SKILLS_SRC="$(cd "$(dirname "$0")/../skills" && pwd)"
SKILLS_DST="$HOME/.claude/skills"

publish_skill() {
  local skill_name="$1"
  local src_path="$2"

  echo "  → Publishing $skill_name from $src_path"
  rm -rf "$SKILLS_DST/$skill_name"
  cp -r "$src_path" "$SKILLS_DST/$skill_name"
  echo "    ✓ $SKILLS_DST/$skill_name"
}

if [[ "${1:-}" == "--all" ]]; then
  echo "Publishing all skills from $SKILLS_SRC → $SKILLS_DST"
  find "$SKILLS_SRC" -name "SKILL.md" | while read -r skill_file; do
    skill_dir="$(dirname "$skill_file")"
    skill_name="$(basename "$skill_dir")"
    publish_skill "$skill_name" "$skill_dir"
  done
  echo "Done."
elif [[ -n "${1:-}" ]]; then
  skill_name="$1"
  src_path="$(find "$SKILLS_SRC" -type d -name "$skill_name" | head -1)"
  if [[ -z "$src_path" ]]; then
    echo "Error: skill '$skill_name' not found in $SKILLS_SRC" >&2
    exit 1
  fi
  echo "Publishing skill: $skill_name"
  publish_skill "$skill_name" "$src_path"
  echo "Done."
else
  echo "Usage: $0 --all | <skill-name>"
  echo ""
  echo "Skills available:"
  find "$SKILLS_SRC" -name "SKILL.md" | sed 's|.*/skills/||; s|/SKILL.md||' | sort
  exit 1
fi

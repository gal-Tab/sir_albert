#!/bin/bash

# Monday.com Brand Guidelines Skill - Installation Script
# This script copies the skill to your Claude Code skills directory

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Monday.com Brand Guidelines Skill"
echo "  Installation Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Determine Claude Code skills directory
CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"

# Check if Claude skills directory exists
if [ ! -d "$CLAUDE_SKILLS_DIR" ]; then
  echo "❌ Claude Code skills directory not found at: $CLAUDE_SKILLS_DIR"
  echo ""
  echo "Please specify your Claude Code skills directory:"
  read -p "Skills directory path: " CUSTOM_DIR

  if [ -z "$CUSTOM_DIR" ]; then
    echo "❌ No directory specified. Exiting."
    exit 1
  fi

  CLAUDE_SKILLS_DIR="$CUSTOM_DIR"
fi

# Create skills directory if it doesn't exist
mkdir -p "$CLAUDE_SKILLS_DIR"

SKILL_NAME="monday-brand-guidelines"
TARGET_DIR="${CLAUDE_SKILLS_DIR}/${SKILL_NAME}"
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "📂 Source: $SOURCE_DIR"
echo "📂 Target: $TARGET_DIR"
echo ""

# Check if skill already exists
if [ -d "$TARGET_DIR" ]; then
  echo "⚠️  Skill already exists at target location."
  read -p "Do you want to overwrite it? (y/N): " -n 1 -r
  echo ""

  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Installation cancelled."
    exit 0
  fi

  echo "🗑️  Removing existing skill..."
  rm -rf "$TARGET_DIR"
fi

# Copy skill to Claude Code skills directory
echo "📦 Copying skill files..."
cp -r "$SOURCE_DIR" "$TARGET_DIR"

# Verify installation
if [ -f "$TARGET_DIR/SKILL.md" ]; then
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "✅ Installation successful!"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "📋 Installed files:"
  echo "   - SKILL.md (main skill)"
  echo "   - LICENSE.txt"
  echo "   - README.md"
  echo "   - assets/ (3 files)"
  echo "   - references/ (3 files)"
  echo "   - templates/ (3 files)"
  echo ""
  echo "🎯 Skill location: $TARGET_DIR"
  echo ""
  echo "📝 Next steps:"
  echo "   1. Restart Claude Code (if running)"
  echo "   2. Test with: 'Create a Monday.com landing page'"
  echo ""
  echo "📖 Documentation: $TARGET_DIR/README.md"
  echo ""
else
  echo ""
  echo "❌ Installation failed. SKILL.md not found."
  exit 1
fi

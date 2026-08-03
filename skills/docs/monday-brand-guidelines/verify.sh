#!/bin/bash

# Monday.com Brand Guidelines Skill - Verification Script
# Checks if the skill is properly installed

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Monday.com Brand Guidelines Skill"
echo "  Verification Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

CLAUDE_SKILLS_DIR="${HOME}/.claude/skills"
SKILL_DIR="${CLAUDE_SKILLS_DIR}/monday-brand-guidelines"

# Check if skill directory exists
if [ ! -d "$SKILL_DIR" ]; then
  echo "❌ Skill not found at: $SKILL_DIR"
  echo ""
  echo "Please run ./install.sh first"
  exit 1
fi

echo "✅ Skill directory found: $SKILL_DIR"
echo ""

# Check required files
REQUIRED_FILES=(
  "SKILL.md"
  "LICENSE.txt"
  "README.md"
  "assets/color-palette.md"
  "assets/product-colors.md"
  "assets/logo-guidelines.md"
  "references/tone-guide.md"
  "references/design-principles.md"
  "references/product-personas.md"
  "templates/html-starter.html"
  "templates/chart-template.html"
  "templates/presentation-slide.html"
)

MISSING_FILES=()

echo "📋 Checking files..."
for file in "${REQUIRED_FILES[@]}"; do
  if [ -f "$SKILL_DIR/$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ❌ $file (MISSING)"
    MISSING_FILES+=("$file")
  fi
done

echo ""

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "✅ All files present!"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  # Check SKILL.md frontmatter
  if grep -q "^name: monday-brand-guidelines" "$SKILL_DIR/SKILL.md" && \
     grep -q "^description:" "$SKILL_DIR/SKILL.md" && \
     grep -q "^license: Apache-2.0" "$SKILL_DIR/SKILL.md"; then
    echo "✅ SKILL.md has valid frontmatter"
  else
    echo "⚠️  SKILL.md frontmatter may be invalid"
  fi

  echo ""
  echo "📊 Skill statistics:"
  echo "   Total files: $(find "$SKILL_DIR" -type f | wc -l | xargs)"
  echo "   Total lines: $(find "$SKILL_DIR" -type f \( -name "*.md" -o -name "*.html" -o -name "*.txt" \) -exec wc -l {} + | tail -1 | awk '{print $1}')"
  echo ""
  echo "🎯 Skill is ready to use!"
  echo ""
  echo "🧪 Test with Claude Code:"
  echo "   'Create a Monday.com landing page'"
  echo "   'Design a CRM dashboard for monday sales CRM'"
  echo "   'Build a sprint chart for monday dev'"
  echo ""
else
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "⚠️  Missing ${#MISSING_FILES[@]} file(s)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "Missing files:"
  for file in "${MISSING_FILES[@]}"; do
    echo "  - $file"
  done
  echo ""
  echo "Please re-run ./install.sh to fix."
  exit 1
fi

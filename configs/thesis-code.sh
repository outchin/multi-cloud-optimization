#!/bin/bash

# Thesis Code Launcher
# Auto-loads PROJECT_CONTEXT.md and prompts to read CURRENT_STATUS.md

THESIS_DIR="$HOME/Desktop/Master_Thesis/Labs/multi-cloud-optimization"

cd "$THESIS_DIR" || {
    echo "❌ Error: Thesis directory not found at $THESIS_DIR"
    exit 1
}

echo "📂 Navigated to thesis directory"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📄 Context Files:"
echo "   ✅ PROJECT_CONTEXT.md (auto-loaded by Claude)"
echo "   📋 CURRENT_STATUS.md (will be read automatically)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Starting Claude Code with prompt..."
echo ""

# Start Claude Code with automatic prompt to read CURRENT_STATUS.md
claude "Read CURRENT_STATUS.md"

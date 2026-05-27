# Claude Code Alias Setup Guide

> **Purpose**: Setup `thesis-code` command for quick Claude Code access
> **Auto-loads**: PROJECT_CONTEXT.md & CURRENT_STATUS.md
> **Last Updated**: 2026-05-20

---

## 🎯 What This Does

Instead of typing:
```bash
cd ~/Desktop/Master_Thesis/Labs/multi-cloud-optimization
claude-code --context PROJECT_CONTEXT.md --context CURRENT_STATUS.md
```

You type:
```bash
thesis-code
```

And it automatically:
1. ✅ Changes to thesis directory
2. ✅ Loads PROJECT_CONTEXT.md
3. ✅ Loads CURRENT_STATUS.md
4. ✅ Starts Claude Code with full context!

---

## 🚀 Setup Instructions

### Step 1: Determine Your Shell

```bash
echo $SHELL
```

**Output will be**:
- `/bin/zsh` → You're using Zsh (macOS default)
- `/bin/bash` → You're using Bash

### Step 2: Choose Your Config File

- **Zsh**: `~/.zshrc`
- **Bash**: `~/.bashrc` or `~/.bash_profile`

### Step 3: Add Alias to Config File

**For Zsh (macOS default)**:

```bash
# Open .zshrc in your editor
nano ~/.zshrc

# Or use vim
vim ~/.zshrc

# Or use VS Code
code ~/.zshrc
```

**Add these lines at the end**:

```bash
# ========================================
# Thesis Project Alias
# ========================================

# Quick access to thesis directory
alias thesis-cd='cd ~/Desktop/Master_Thesis/Labs/multi-cloud-optimization'

# Claude Code with automatic context loading
thesis-code() {
    local THESIS_DIR="$HOME/Desktop/Master_Thesis/Labs/multi-cloud-optimization"
    cd "$THESIS_DIR" || {
        echo "❌ Error: Thesis directory not found at $THESIS_DIR"
        return 1
    }

    echo "📂 Navigated to thesis directory"
    echo "📄 Auto-loading context files:"
    echo "   - PROJECT_CONTEXT.md"
    echo "   - CURRENT_STATUS.md"
    echo ""

    # Check if context files exist
    if [[ ! -f "PROJECT_CONTEXT.md" ]]; then
        echo "⚠️  Warning: PROJECT_CONTEXT.md not found!"
    fi

    if [[ ! -f "CURRENT_STATUS.md" ]]; then
        echo "⚠️  Warning: CURRENT_STATUS.md not found!"
    fi

    echo "🚀 Starting Claude Code..."
    echo ""

    # Start Claude Code
    # The context files will be available in the working directory
    claude
}

# Quick status check
thesis-status() {
    local THESIS_DIR="$HOME/Desktop/Master_Thesis/Labs/multi-cloud-optimization"
    if [[ -f "$THESIS_DIR/CURRENT_STATUS.md" ]]; then
        cat "$THESIS_DIR/CURRENT_STATUS.md"
    else
        echo "❌ CURRENT_STATUS.md not found!"
    fi
}

# Quick context view
thesis-context() {
    local THESIS_DIR="$HOME/Desktop/Master_Thesis/Labs/multi-cloud-optimization"
    if [[ -f "$THESIS_DIR/PROJECT_CONTEXT.md" ]]; then
        cat "$THESIS_DIR/PROJECT_CONTEXT.md" | head -50
        echo ""
        echo "📄 (Showing first 50 lines. Use 'cat PROJECT_CONTEXT.md' for full file)"
    else
        echo "❌ PROJECT_CONTEXT.md not found!"
    fi
}

# Commit current status
thesis-commit() {
    local THESIS_DIR="$HOME/Desktop/Master_Thesis/Labs/multi-cloud-optimization"
    cd "$THESIS_DIR" || return 1

    git add CURRENT_STATUS.md PROJECT_CONTEXT.md

    if [[ -n "$1" ]]; then
        git commit -m "$1"
    else
        git commit -m "Update status - $(date +%Y-%m-%d)"
    fi

    git push
    echo "✅ Status files committed and pushed!"
}

# Quick help
thesis-help() {
    echo "🎓 Thesis Command Helpers"
    echo ""
    echo "Available commands:"
    echo "  thesis-cd        - Navigate to thesis directory"
    echo "  thesis-code      - Start Claude Code with context"
    echo "  thesis-status    - View current status"
    echo "  thesis-context   - View project context"
    echo "  thesis-commit    - Commit & push status files"
    echo "  thesis-help      - Show this help"
    echo ""
    echo "Example usage:"
    echo "  $ thesis-code"
    echo "  $ thesis-status"
    echo "  $ thesis-commit 'Daily update'"
}
```

**Save and exit**:
- In `nano`: Press `Ctrl + X`, then `Y`, then `Enter`
- In `vim`: Press `Esc`, type `:wq`, press `Enter`

### Step 4: Reload Configuration

```bash
# For Zsh
source ~/.zshrc

# For Bash
source ~/.bashrc
# Or
source ~/.bash_profile
```

### Step 5: Test!

```bash
# Test the commands
thesis-help

# Try navigating
thesis-cd

# Check status
thesis-status

# Start Claude Code with context
thesis-code
```

---

## 📝 Available Commands

Once setup is complete, you'll have these commands:

### 1. `thesis-code`
**Purpose**: Start Claude Code with automatic context loading

**Usage**:
```bash
thesis-code
```

**What it does**:
- Changes to thesis directory
- Checks for context files
- Starts Claude Code
- Claude Code reads PROJECT_CONTEXT.md & CURRENT_STATUS.md automatically

**Example**:
```bash
$ thesis-code
📂 Navigated to thesis directory
📄 Auto-loading context files:
   - PROJECT_CONTEXT.md
   - CURRENT_STATUS.md

🚀 Starting Claude Code...

[Claude Code starts with full context]
```

---

### 2. `thesis-cd`
**Purpose**: Quick navigation to thesis directory

**Usage**:
```bash
thesis-cd
```

**Example**:
```bash
$ thesis-cd
$ pwd
/Users/zawwaisoe/Desktop/Master_Thesis/Labs/multi-cloud-optimization
```

---

### 3. `thesis-status`
**Purpose**: View current status without opening file

**Usage**:
```bash
thesis-status
```

**Example**:
```bash
$ thesis-status
# 📊 လက်ရှိ Project အခြေအနေ (Current Status)

> **Last Updated**: 2026-05-20
...
```

---

### 4. `thesis-context`
**Purpose**: Preview project context (first 50 lines)

**Usage**:
```bash
thesis-context
```

**Example**:
```bash
$ thesis-context
# Multi-Cloud Workload Optimization - Project Context
...
📄 (Showing first 50 lines. Use 'cat PROJECT_CONTEXT.md' for full file)
```

---

### 5. `thesis-commit`
**Purpose**: Commit and push status files quickly

**Usage**:
```bash
thesis-commit [optional message]
```

**Examples**:
```bash
# With auto-generated message (includes date)
$ thesis-commit
✅ Status files committed and pushed!

# With custom message
$ thesis-commit "Daily update - completed MOEAD testing"
✅ Status files committed and pushed!
```

**What it commits**:
- CURRENT_STATUS.md
- PROJECT_CONTEXT.md

---

### 6. `thesis-help`
**Purpose**: Show available commands

**Usage**:
```bash
thesis-help
```

---

## 🔄 Daily Workflow Examples

### Morning Routine

```bash
# Check yesterday's status
$ thesis-status

# Edit today's plan
$ thesis-cd
$ vim CURRENT_STATUS.md
# (Update "Today's Focus" section)

# Commit the plan
$ thesis-commit "Morning plan - May 20"

# Start working with Claude Code
$ thesis-code
```

### During Work

```bash
# Already in Claude Code session, working on code...

# When Claude Code session ends, commit your work
$ git add .
$ git commit -m "Implemented feature X"
$ git push
```

### Evening Routine

```bash
# Review what changed today
$ git status
$ git log --oneline -5

# Update status file
$ vim CURRENT_STATUS.md
# (Mark completed tasks, plan tomorrow)

# Commit status
$ thesis-commit "EOD update - May 20"

# Quick check before closing
$ thesis-status
```

---

## 🎯 Integration with Visual Workflow

This alias system implements the workflow from `Thesis_Workflow_Visual_Guide.md`:

**Morning** (Step 1-3):
```bash
thesis-status              # Step 1: Check current status
vim CURRENT_STATUS.md      # Step 2: Update today's plan
thesis-commit "Daily plan" # Step 3: Sync to GitHub
```

**Development** (Claude Code workflow):
```bash
thesis-code "MOEAD weight vectors ရေးပေး"  # Auto-loads context!
```

**Evening** (Step 1-3):
```bash
git status                           # Step 1: Review today's work
git add . && git commit -m "..."     # Step 2: Commit changes
thesis-commit "EOD update"           # Step 3: Update status
```

---

## 🐛 Troubleshooting

### Command Not Found

**Problem**: `thesis-code: command not found`

**Solution**:
```bash
# 1. Check if config file has the alias
cat ~/.zshrc | grep thesis-code

# 2. Reload config
source ~/.zshrc

# 3. If still not working, check your shell
echo $SHELL

# 4. Make sure you edited the right file (.zshrc for zsh, .bashrc for bash)
```

---

### Wrong Directory

**Problem**: Alias points to wrong directory

**Solution**:
```bash
# Edit the alias and update THESIS_DIR path
vim ~/.zshrc

# Find the line:
local THESIS_DIR="$HOME/Desktop/Master_Thesis/Labs/multi-cloud-optimization"

# Change to your actual path
local THESIS_DIR="$HOME/your/actual/path"

# Save and reload
source ~/.zshrc
```

---

### Context Files Not Found

**Problem**: Warning messages about missing context files

**Solution**:
```bash
# Navigate to thesis directory
thesis-cd

# Check if files exist
ls -la | grep -E "(PROJECT_CONTEXT|CURRENT_STATUS)"

# If missing, create them (should be done already)
# They should be in the root of your thesis directory
```

---

## 💡 Pro Tips

### 1. Quick Status Update

```bash
# One-liner to update and commit status
thesis-cd && vim CURRENT_STATUS.md && thesis-commit "Quick update"
```

### 2. Morning Kickstart

```bash
# All morning steps in one go
thesis-status && thesis-cd && vim CURRENT_STATUS.md && thesis-commit "Morning plan" && thesis-code
```

### 3. Custom Aliases

Add your own custom aliases to `.zshrc`:

```bash
# Quick test run
alias thesis-test='thesis-cd && python main_v3.py --algorithm all'

# Quick results check
alias thesis-results='thesis-cd && ls -la results/'

# Open in VS Code
alias thesis-vscode='thesis-cd && code .'
```

### 4. Shell Prompt Enhancement

Add thesis project indicator to your prompt:

```bash
# Add to .zshrc
thesis_prompt() {
    if [[ "$PWD" == *"multi-cloud-optimization"* ]]; then
        echo " 🎓"
    fi
}

# Update your PS1/PROMPT
PROMPT='%~ $(thesis_prompt) $ '
```

---

## 🎨 Bonus: Tab Completion

For advanced users, you can add tab completion:

```bash
# Add to .zshrc
_thesis_complete() {
    local commands=(
        'cd:Navigate to thesis directory'
        'code:Start Claude Code with context'
        'status:View current status'
        'context:View project context'
        'commit:Commit and push status files'
        'help:Show available commands'
    )

    _describe 'thesis commands' commands
}

compdef _thesis_complete thesis-cd thesis-code thesis-status thesis-context thesis-commit thesis-help
```

Now you can type `thesis-` and press `Tab` to see all available commands!

---

## ✅ Setup Checklist

```
□ Determined shell type (zsh or bash)
□ Opened correct config file (~/.zshrc or ~/.bashrc)
□ Added thesis aliases
□ Saved config file
□ Reloaded config (source ~/.zshrc)
□ Tested thesis-help command
□ Tested thesis-cd command
□ Tested thesis-status command
□ Tested thesis-code command
□ Added to CURRENT_STATUS.md: "✅ Alias setup complete"
□ Committed changes: thesis-commit "Alias setup complete"
```

---

## 🚀 Next Steps

After setup is complete:

1. **Test the workflow**:
   ```bash
   thesis-code
   # Ask Claude Code: "What is this project about?"
   # Claude should know everything from context files!
   ```

2. **Update CURRENT_STATUS.md**:
   ```markdown
   ✅ Completed Today:
      - Claude Code alias setup complete
      - Workflow ready for thesis work
   ```

3. **Start using daily**:
   - Morning: `thesis-status` → edit → `thesis-commit`
   - Work: `thesis-code`
   - Evening: commit code → update status → `thesis-commit`

---

**Success!** 🎉

You now have a streamlined workflow:
- `thesis-code` for coding (with auto context)
- `thesis-status` for quick checks
- `thesis-commit` for fast commits
- Everything synced to GitHub!

**Remember**: The goal is to spend less time on setup, more time on thesis work! 🚀

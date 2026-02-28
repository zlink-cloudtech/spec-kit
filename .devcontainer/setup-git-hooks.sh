#!/bin/bash

# Get the root directory of the git repository
# Assuming this script is run from within the repo
REPO_ROOT=$(git rev-parse --show-toplevel)
HOOK_DIR="$REPO_ROOT/.git/hooks"
HOOK_FILE="$HOOK_DIR/post-commit"

if [ ! -d "$HOOK_DIR" ]; then
    echo "Error: .git/hooks directory not found. Is this a git repository?"
    exit 1
fi

echo "Setting up git post-commit hook..."

if ! command -v act &> /dev/null && ! command -v gh &> /dev/null; then
    echo "Warning: Neither 'act' nor 'gh act' is available."
    echo "The hook requires 'act' or 'gh act' to run GitHub Actions locally."
    echo "Please ensure one of them is installed in the devcontainer."
fi

# Create the post-commit hook
cat > "$HOOK_FILE" << 'EOF'
#!/bin/bash

# Determine which tool to use: act or gh act
ACT_CMD=""
if command -v act &> /dev/null; then
    ACT_CMD="act"
elif command -v gh &> /dev/null; then
    ACT_CMD="gh act"
else
    echo "[post-commit] Neither 'act' nor 'gh act' found. Skipping local workflow execution."
    exit 0
fi

echo "[post-commit] Running post-commit workflows using '$ACT_CMD'..."

# 1. Always run lint.yml
echo "[post-commit] Running lint.yml..."
$ACT_CMD -W .github/workflows/lint.yml

# Get changed files in the latest commit
CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r HEAD)

# 2. Check for release-server changes
if echo "$CHANGED_FILES" | grep -q "^release-server/"; then
    echo "[post-commit] Changes detected in release-server/. Running test-release-server.sh..."
    bash .github/workflows/scripts/test-release-server.sh
fi

# 3. Check for mcp changes (excluding README files)
if echo "$CHANGED_FILES" | grep -q "^mcp/" && echo "$CHANGED_FILES" | grep "^mcp/" | grep -v -q -E "^mcp/README(-CN)?\.md$"; then
    echo "[post-commit] Changes detected in mcp/. Running release-mcp-publish.yml..."
    $ACT_CMD -W .github/workflows/release-mcp-publish.yml
fi

# 4. Check for other triggers: memory/**, scripts/**, templates/**, skills/**, .github/workflows/scripts/**
# Regex pattern matches lines starting with any of these directories
PATTERN="^(memory/|scripts/|templates/|skills/|\.github/workflows/scripts/)"

if echo "$CHANGED_FILES" | grep -E -q "$PATTERN"; then
    echo "[post-commit] Changes detected in core directories (memory, scripts, templates, skills, or workflow scripts)."
    echo "[post-commit] Running release.yml..."
    $ACT_CMD -W .github/workflows/release.yml
fi
EOF

# Make the hook executable
chmod +x "$HOOK_FILE"

echo "✅ Git post-commit hook installed to $HOOK_FILE"

#!/usr/bin/env bash
# setup-uml-dir.sh — Initialize the uml/ subdirectory inside a feature directory.
#
# Usage:
#   setup-uml-dir.sh [FEATURE_DIR]
#   FEATURE_DIR=/path/to/feature setup-uml-dir.sh
#
# Priority: positional $1 > $FEATURE_DIR env var
# Output:   absolute path to the created uml/ directory (stdout)
# Exit 0:   success (idempotent)
# Exit 1:   no feature directory specified

set -e

# Get script directory and load common functions
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Resolve feature directory: positional arg takes precedence over env var
if [[ -n "${1:-}" ]]; then
    TARGET_DIR="$1"
elif [[ -n "${FEATURE_DIR:-}" ]]; then
    TARGET_DIR="$FEATURE_DIR"
else
    echo "Error: No feature directory specified. Pass as \$1 or set FEATURE_DIR env var." >&2
    exit 1
fi

# Resolve to absolute path
TARGET_DIR="$(CDPATH="" cd "$TARGET_DIR" 2>/dev/null && pwd || echo "$TARGET_DIR")"

# Guard: TARGET_DIR must not be a regular file (FR-012)
if [[ -f "$TARGET_DIR" ]]; then
    echo "Error: FEATURE_DIR '$TARGET_DIR' is a regular file, not a directory." >&2
    exit 1
fi

# Create the uml/ subdirectory (idempotent)
UML_DIR="$TARGET_DIR/uml"
mkdir -p "$UML_DIR"

# Output the absolute path
echo "$UML_DIR"

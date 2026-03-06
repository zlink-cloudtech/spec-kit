#!/usr/bin/env bash
set -euo pipefail

# get-next-version.sh
# Calculate the next version based on the latest git tag and output GitHub Actions variables.
#
# Bump type priority:
#   1. BUMP_TYPE env var (injected by workflow_dispatch: major | minor | patch | auto)
#   2. Auto-detection from conventional commits since last tag:
#        feat: / feat(...):  → minor
#        anything else       → patch
#        NOTE: major is NEVER auto-detected; it must be explicitly set via BUMP_TYPE=major
#
# Usage: get-next-version.sh

# Get the latest tag across ALL branches, or use v0.0.0 if no tags exist.
# "v[0-9]*" filters only CLI release tags, ignoring service tags like release-server-v* or mcp-v*
# Note: git describe only finds tags reachable from HEAD; using git tag --sort instead to
# ensure tags created on other branches (e.g. main) are always considered.
LATEST_TAG=$(git tag --list "v[0-9]*" --sort=-version:refname 2>/dev/null | head -1)
LATEST_TAG="${LATEST_TAG:-v0.0.0}"
echo "latest_tag=$LATEST_TAG" >> $GITHUB_OUTPUT

# Extract version parts
VERSION=$(echo $LATEST_TAG | sed 's/v//')
IFS='.' read -ra VERSION_PARTS <<< "$VERSION"
MAJOR=${VERSION_PARTS[0]:-0}
MINOR=${VERSION_PARTS[1]:-0}
PATCH=${VERSION_PARTS[2]:-0}

# Resolve bump type
BUMP="${BUMP_TYPE:-auto}"

if [ "$BUMP" = "auto" ]; then
  # Collect commit subjects since last tag
  if [ "$LATEST_TAG" = "v0.0.0" ]; then
    COMMITS=$(git log --pretty=format:"%s" 2>/dev/null || true)
  else
    COMMITS=$(git log --pretty=format:"%s" "$LATEST_TAG..HEAD" 2>/dev/null || true)
  fi

  if echo "$COMMITS" | grep -qE '^feat(\([^)]+\))?:'; then
    BUMP="minor"
  else
    BUMP="patch"
  fi
fi

echo "Bump type: $BUMP"

case "$BUMP" in
  major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
  minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
  *)     PATCH=$((PATCH + 1)) ;;
esac

NEW_VERSION="v$MAJOR.$MINOR.$PATCH"

echo "new_version=$NEW_VERSION" >> $GITHUB_OUTPUT
echo "New version will be: $NEW_VERSION"

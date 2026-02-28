#!/usr/bin/env bash
set -euo pipefail

# get-next-mcp-version.sh
# Calculate the next version for MCP based on the latest git tag
# Usage: get-next-mcp-version.sh

# Get the latest tag for MCP using git tag sort for global visibility
LATEST_TAG=$(git tag --list "mcp-v[0-9]*" --sort=-v:refname | head -n 1)
if [ -z "$LATEST_TAG" ]; then
    LATEST_TAG="mcp-v0.0.0"
fi

if [ -n "${GITHUB_OUTPUT:-}" ]; then
  echo "latest_tag=$LATEST_TAG" >> "$GITHUB_OUTPUT"
fi

# Extract version number and increment
# mcp-v0.1.1 -> 0.1.1
VERSION=$(echo $LATEST_TAG | sed 's/mcp-v//')
IFS='.' read -ra VERSION_PARTS <<< "$VERSION"
MAJOR=${VERSION_PARTS[0]:-0}
MINOR=${VERSION_PARTS[1]:-0}
PATCH=${VERSION_PARTS[2]:-0}

# Handle prerelease suffixes (e.g. 0.1.1-beta.1 -> 1)
PATCH=${PATCH%%-*}

# Increment patch version
PATCH=$((PATCH + 1))
NEW_VERSION="$MAJOR.$MINOR.$PATCH"

if [ -n "${GITHUB_OUTPUT:-}" ]; then
  echo "new_version=$NEW_VERSION" >> "$GITHUB_OUTPUT"
fi
echo "New version will be: $NEW_VERSION"

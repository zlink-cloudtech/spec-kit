#!/usr/bin/env bash
set -euo pipefail

# get-next-release-server-version.sh
# Calculate the next version for release-server based on the latest git tag
# Usage: get-next-release-server-version.sh

# Get the latest tag for release-server, or use v0.0.0 if no tags exist
# Use --match "release-server-v[0-9]*" to filter only release-server tags
LATEST_TAG=$(git describe --tags --match "release-server-v[0-9]*" --abbrev=0 2>/dev/null || echo "release-server-v0.0.0")

# If LATEST_TAG is release-server-v0.0.0 (default), check if there are any tags actually
# If check fails, it defaults to v0.0.0.

if [ -n "${GITHUB_OUTPUT:-}" ]; then
  echo "latest_tag=$LATEST_TAG" >> "$GITHUB_OUTPUT"
fi

# Extract version number and increment
# release-server-v1.2.3 -> 1.2.3
VERSION=$(echo $LATEST_TAG | sed 's/release-server-v//')
IFS='.' read -ra VERSION_PARTS <<< "$VERSION"
MAJOR=${VERSION_PARTS[0]:-0}
MINOR=${VERSION_PARTS[1]:-0}
PATCH=${VERSION_PARTS[2]:-0}

# Handle prerelease suffixes (e.g. 1.2.3-beta.1 -> 3)
PATCH=${PATCH%%-*}

# Increment patch version
PATCH=$((PATCH + 1))
NEW_VERSION="$MAJOR.$MINOR.$PATCH"

if [ -n "${GITHUB_OUTPUT:-}" ]; then
  echo "new_version=$NEW_VERSION" >> "$GITHUB_OUTPUT"
fi
echo "New version will be: $NEW_VERSION"

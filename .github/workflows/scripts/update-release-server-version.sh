#!/usr/bin/env bash
set -euo pipefail

# update-release-server-version.sh
# Update version in release-server/pyproject.toml
# Usage: update-release-server-version.sh <version>

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <version>" >&2
  exit 1
fi

VERSION="$1"
# Ensure simple version format (1.2.3)
VERSION=${VERSION#v}
VERSION=${VERSION#release-server-v}

# PEP 440 compliance: convert -test to .dev
# Python tools (like uv) require PEP 440 versions in pyproject.toml
if [[ "$VERSION" == *"-test" ]]; then
  BASE_VERSION="${VERSION%-test}"
  VERSION="${BASE_VERSION}.dev"
  echo "ℹ️  Converting test version to PEP 440 compliant: $VERSION"
fi

PYPROJECT_PATH="release-server/pyproject.toml"

if [ -f "$PYPROJECT_PATH" ]; then
  # Assuming using sed to replace version = "..."
  # Use a temp file to avoid issues with sed in-place on some systems, though standard here matches other scripts.
  sed -i "s/version = \".*\"/version = \"$VERSION\"/" "$PYPROJECT_PATH"
  echo "Updated $PYPROJECT_PATH version to $VERSION"
else
  echo "Error: $PYPROJECT_PATH not found"
  exit 1
fi

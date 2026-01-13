#!/usr/bin/env bash
set -euo pipefail

# generate-release-server-notes.sh
# Generate release notes for release-server from git history
# Usage: generate-release-server-notes.sh <new_version> <last_tag>

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <new_version> <last_tag>" >&2
  exit 1
fi

NEW_VERSION="$1"
LAST_TAG="$2"

# Get commits since last tag, filtering for changes in release-server directory
if [ "$LAST_TAG" = "release-server-v0.0.0" ]; then
  # If first release, probably look at all history of the folder?
  # Or just recent ones. Let's do recent 20 for safety if it's new.
  COMMITS=$(git log --oneline --pretty=format:"- %s" HEAD -- release-server/)
else
  COMMITS=$(git log --oneline --pretty=format:"- %s" $LAST_TAG..HEAD -- release-server/)
fi

# Create release notes
cat > release_notes.md << EOF
## Release Server $NEW_VERSION

Changes in this release:

$COMMITS

EOF

echo "Generated release notes:"
cat release_notes.md

#!/bin/bash
set -e

# Usage: ./publish-release-server-chart-ghcr.sh <version>
# Example: ./publish-release-server-chart-ghcr.sh 0.1.0

VERSION="$1"
if [ -z "$VERSION" ]; then
    echo "Error: Version argument required"
    echo "Usage: $0 <version>"
    exit 1
fi

# Resolve project root from this script location: .github/workflows/scripts/
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
DIST_DIR="${PROJECT_ROOT}/release-server/dist"

# Check for GITHUB_REPOSITORY_OWNER
if [ -z "$GITHUB_REPOSITORY_OWNER" ]; then
    echo "Error: GITHUB_REPOSITORY_OWNER environment variable is required."
    exit 1
fi

# Lowercase the owner name for OCI registry compliance
OWNER="${GITHUB_REPOSITORY_OWNER,,}"
REGISTRY="oci://ghcr.io/${OWNER}/charts"
CHART_PACKAGE="speckit-rs-${VERSION}.tgz"
CHART_PATH="${DIST_DIR}/${CHART_PACKAGE}"

# if no GITHUB_ACTOR is set, default to OWNER
if [ -z "$GITHUB_ACTOR" ]; then
    GITHUB_ACTOR="$OWNER"
fi

echo "🔍 Checking for chart package at: ${CHART_PATH}"

if [ ! -f "$CHART_PATH" ]; then
    echo "❌ Error: Chart package not found at ${CHART_PATH}"
    echo "   Ensure you have run the release build script first."
    exit 1
fi

# --- Dry-run: skip push ---
if [ "${DRY_RUN}" == "true" ]; then
    echo "ℹ️  DRY_RUN=true — skipping push"
    echo "✅ Done (dry run). Package at: ${CHART_PATH}"
    exit 0
fi

echo "🚀 Publishing Helm chart version ${VERSION} to ${REGISTRY}..."

# Check if helm is installed
if ! command -v helm >/dev/null 2>&1; then
    echo "❌ Error: 'helm' command not found."
    exit 1
fi

# Note: We assume the environment is already authenticated to GHCR.
# In GitHub Actions, use the 'docker/login-action' or 'helm registry login'.

# Try to login if credentials are provided
if [ -n "$GITHUB_TOKEN" ] && [ -n "$GITHUB_ACTOR" ]; then
    echo "🔑 Logging into GHCR as $GITHUB_ACTOR..."
    echo "$GITHUB_TOKEN" | helm registry login ghcr.io --username "$GITHUB_ACTOR" --password-stdin
elif [ -n "$CR_PAT" ] && [ -n "$GITHUB_ACTOR" ]; then
    echo "🔑 Logging into GHCR as $GITHUB_ACTOR..."
    echo "$CR_PAT" | helm registry login ghcr.io --username "$GITHUB_ACTOR" --password-stdin
else
    echo "ℹ️  No GITHUB_TOKEN/CR_PAT and GITHUB_ACTOR provided. Assuming already logged in."
fi

echo "📦 Pushing ${CHART_PACKAGE}..."
if ! helm push "${CHART_PATH}" "${REGISTRY}"; then
    echo ""
    echo "❌ Error: Push failed."
    echo "💡 Troubleshooting tips:"
    echo "   1. Does the token have 'write:packages' permission?"
    echo "   2. If using a Fine-grained PAT, does it have access to the '${OWNER}' organization?"
    echo "   3. Did you set GITHUB_ACTOR to your username (not the Org name)?"
    echo "      (Current GITHUB_ACTOR: '${GITHUB_ACTOR}')"
    exit 1
fi

echo "✅ Chart published successfully!"

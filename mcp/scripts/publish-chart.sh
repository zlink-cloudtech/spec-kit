#!/bin/bash
set -e

# publish-chart.sh — Package and publish the MCP Helm chart to GHCR as an OCI artifact.
#
# Usage:
#   ./publish-chart.sh <version>
#   GITHUB_TOKEN=... GITHUB_ACTOR=... ./publish-chart.sh 0.1.1
#
# Environment variables (optional — script works without them for local packaging):
#   GITHUB_TOKEN            Token with write:packages scope (for GHCR push)
#   GITHUB_ACTOR            GitHub username (for GHCR login)
#   GITHUB_REPOSITORY_OWNER Repository owner, lowercase (defaults to "github")
#   DRY_RUN                 Set to "true" to skip the push step

VERSION="$1"
if [ -z "$VERSION" ]; then
    echo "❌ Error: Version argument required"
    echo "Usage: $0 <version>"
    exit 1
fi

# Resolve paths — script lives at mcp/scripts/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CHART_DIR="${MCP_DIR}/chart"
DIST_DIR="${MCP_DIR}/dist"

# Validate chart directory exists
if [ ! -f "${CHART_DIR}/Chart.yaml" ]; then
    echo "❌ Error: Chart.yaml not found at ${CHART_DIR}"
    exit 1
fi

# Check helm is installed
if ! command -v helm >/dev/null 2>&1; then
    echo "❌ Error: 'helm' command not found. Install Helm 3.8+ first."
    echo "   https://helm.sh/docs/intro/install/"
    exit 1
fi

# Ensure dist directory exists
mkdir -p "$DIST_DIR"

# --- Step 1: Lint ---
echo "🔍 Linting chart..."
if ! helm lint "$CHART_DIR"; then
    echo "❌ Chart lint failed. Fix errors before publishing."
    exit 1
fi
echo "✅ Lint passed"

# --- Step 2: Package ---
echo "📦 Packaging chart version ${VERSION}..."
helm package "$CHART_DIR" \
    --version "$VERSION" \
    --app-version "$VERSION" \
    --destination "$DIST_DIR"

CHART_PACKAGE="${DIST_DIR}/speckit-mcp-server-${VERSION}.tgz"
if [ ! -f "$CHART_PACKAGE" ]; then
    echo "❌ Error: Expected package not found at ${CHART_PACKAGE}"
    exit 1
fi
echo "✅ Packaged: ${CHART_PACKAGE}"

# --- Step 3: Push to GHCR (unless DRY_RUN) ---
if [ "${DRY_RUN}" == "true" ]; then
    echo "ℹ️  DRY_RUN=true — skipping push"
    echo "✅ Done (dry run). Package at: ${CHART_PACKAGE}"
    exit 0
fi

# Determine registry owner
OWNER="${GITHUB_REPOSITORY_OWNER:-github}"
OWNER="${OWNER,,}"  # lowercase
REGISTRY="oci://ghcr.io/${OWNER}/charts"

# Authenticate to GHCR if credentials are available
if [ -n "$GITHUB_TOKEN" ] && [ -n "$GITHUB_ACTOR" ]; then
    echo "🔑 Logging into GHCR as ${GITHUB_ACTOR}..."
    echo "$GITHUB_TOKEN" | helm registry login ghcr.io --username "$GITHUB_ACTOR" --password-stdin
elif [ -n "$CR_PAT" ] && [ -n "$GITHUB_ACTOR" ]; then
    echo "🔑 Logging into GHCR as ${GITHUB_ACTOR} (CR_PAT)..."
    echo "$CR_PAT" | helm registry login ghcr.io --username "$GITHUB_ACTOR" --password-stdin
else
    echo "ℹ️  No credentials provided. Assuming already logged in to GHCR."
fi

echo "🚀 Pushing to ${REGISTRY}..."
if ! helm push "$CHART_PACKAGE" "$REGISTRY"; then
    echo ""
    echo "❌ Error: Push failed."
    echo "💡 Troubleshooting:"
    echo "   1. Does the token have 'write:packages' permission?"
    echo "   2. For Fine-grained PATs, does it have access to the '${OWNER}' organization?"
    echo "   3. Is GITHUB_ACTOR set to your username? (current: '${GITHUB_ACTOR}')"
    exit 1
fi

echo "✅ Chart v${VERSION} published to ${REGISTRY}/speckit-mcp-server"
echo ""
echo "Install with:"
echo "  helm install my-mcp ${REGISTRY}/speckit-mcp-server --version ${VERSION}"

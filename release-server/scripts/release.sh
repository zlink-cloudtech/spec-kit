#!/bin/bash
set -e

# Usage: ./scripts/release.sh [version]
# Example: ./scripts/release.sh 1.0.0

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Get version from argument or pyproject.toml
if [ -n "$1" ]; then
    VERSION="$1"
else
    VERSION=$(grep "^version =" "${PROJECT_ROOT}/pyproject.toml" | cut -d '"' -f 2)
    echo "ℹ️  No version provided, using version from pyproject.toml: ${VERSION}"
fi

DIST_DIR="${PROJECT_ROOT}/dist"
CHART_DIR="${PROJECT_ROOT}/chart"

echo "🚀 Starting release process for version: ${VERSION}"

# Clean dist directory
rm -rf "${DIST_DIR}"
mkdir -p "${DIST_DIR}"

# 1. Build Python Package (sdist and wheel)
echo "📦 Building Python package..."
cd "${PROJECT_ROOT}"
# Check if uv is installed, if not try pip install
if command -v uv >/dev/null 2>&1; then
    uv build --out-dir "${DIST_DIR}"
else
    echo "⚠️  uv not found, using python -m build..."
    pip install build
    python3 -m build --outdir "${DIST_DIR}"
fi

# 2. Package Helm Chart
echo "☸️  Packaging Helm chart..."
if command -v helm >/dev/null 2>&1; then
    # Package the chart, overriding version and appVersion
    helm package "${CHART_DIR}" \
        --version "${VERSION}" \
        --app-version "${VERSION}" \
        --destination "${DIST_DIR}"
    
    # Artifact will be named speckit-rs-${VERSION}.tgz 
    # We leave it as is to follow standard Helm conventions
else
    echo "❌ Helm not found! Skipping chart packaging."
    exit 1
fi

echo "✅ Release artifacts successfully created in ${DIST_DIR}:"
ls -lh "${DIST_DIR}"

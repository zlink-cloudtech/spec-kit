#!/bin/bash
set -e

# Help function
usage() {
    echo "Usage: $0 [VERSION]"
    echo "Runs the release-server-publish workflow locally using 'gh act'."
    echo ""
    echo "Arguments:"
    echo "  VERSION    Optional. The version string to test (e.g., 0.0.90-localtest)."
    echo "             If not provided, the workflow will calculate it automatically."
    echo ""
    echo "Options:"
    echo "  -h, --help Show this help message and exit."
}

# Check for help argument
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    usage
    exit 0
fi

VERSION="${1:-}"

# 检查 .secrets 文件是否存在
if [ ! -f .secrets ]; then
    echo "Error: .secrets file not found in current directory."
    echo "Please create a .secrets file with GITHUB_TOKEN=..."
    exit 1
fi

if [ -n "$VERSION" ]; then
  echo "Testing release-server-publish workflow with manual version: $VERSION"
else
  echo "Testing release-server-publish workflow with automatic version calculation"
fi
echo "Note: Ensure you have run 'docker volume rm act-toolcache' if you encounter system-level cache issues."

# Detect proxy settings
PROXY_ARGS=()
# [[ -n "$HTTP_PROXY" ]] && PROXY_ARGS+=("--env" "HTTP_PROXY=$HTTP_PROXY") && echo "Detected HTTP_PROXY: $HTTP_PROXY"
# [[ -n "$HTTPS_PROXY" ]] && PROXY_ARGS+=("--env" "HTTPS_PROXY=$HTTPS_PROXY") && echo "Detected HTTPS_PROXY: $HTTPS_PROXY"
# [[ -n "$NO_PROXY" ]] && PROXY_ARGS+=("--env" "NO_PROXY=$NO_PROXY") && echo "Detected NO_PROXY: $NO_PROXY"
# [[ -n "$http_proxy" ]] && PROXY_ARGS+=("--env" "http_proxy=$http_proxy") && echo "Detected http_proxy: $http_proxy"
# [[ -n "$https_proxy" ]] && PROXY_ARGS+=("--env" "https_proxy=$https_proxy") && echo "Detected https_proxy: $https_proxy"
# [[ -n "$no_proxy" ]] && PROXY_ARGS+=("--env" "no_proxy=$no_proxy") && echo "Detected no_proxy: $no_proxy"

ACT_ARGS=(
    "-W" ".github/workflows/release-server-publish.yml" 
    "--secret-file" ".secrets" 
    "--env" "IS_TEST=true")

if [ -n "$VERSION" ]; then
    ACT_ARGS+=("--input" "version=$VERSION")
fi

# 运行 gh act
gh act "${ACT_ARGS[@]}" \
   --env PYTHONDONTWRITEBYTECODE=1 \
   "${PROXY_ARGS[@]}"

#!/bin/bash
set -e

# Help function
usage() {
    echo "Usage: $0 [OPTIONS] [VERSION]"
    echo "Runs the release-server-publish workflow locally using 'gh act'."
    echo ""
    echo "Arguments:"
    echo "  VERSION            Optional. The version string to test (e.g., 0.0.90-localtest)."
    echo "                     If not provided, the workflow will calculate it automatically."
    echo ""
    echo "Options:"
    echo "  -e, --event EVENT  The event to trigger (push, workflow_dispatch). Default: workflow_dispatch."
    echo "  -d, --dry-run      Enable dry-run mode (build & package only, skip push). Default: true."
    echo "  -h, --help         Show this help message and exit."
}

EVENT="workflow_dispatch"
VERSION=""
DRY_RUN="true"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--event)
            EVENT="$2"
            shift 2
            ;;
        -d|--dry-run)
            DRY_RUN="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            if [ -z "$VERSION" ]; then
                VERSION="$1"
                shift
            else
                echo "Error: Unknown argument '$1'"
                usage
                exit 1
            fi
            ;;
    esac
done

# Validate event
if [[ "$EVENT" != "push" && "$EVENT" != "workflow_dispatch" ]]; then
    echo "Error: Event must be 'push' or 'workflow_dispatch'."
    exit 1
fi

# Check for .secrets file
if [ ! -f .secrets ]; then
    echo "Error: .secrets file not found in current directory."
    echo "Please create a .secrets file with GITHUB_TOKEN=..."
    exit 1
fi

echo "Testing release-server-publish workflow with event: $EVENT"
if [ -n "$VERSION" ]; then
  echo "Manual version: $VERSION"
else
  echo "Automatic version calculation"
fi
echo "Dry run: $DRY_RUN"
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
)

if [ "$EVENT" = "workflow_dispatch" ]; then
    ACT_ARGS+=("--input" "dry_run=$DRY_RUN")
    if [ -n "$VERSION" ]; then
        ACT_ARGS+=("--input" "version=$VERSION")
    fi
else
    if [ -n "$VERSION" ]; then
        ACT_ARGS+=("--input" "version=$VERSION")
    fi
fi

# Run gh act
gh act "$EVENT" "${ACT_ARGS[@]}" \
   --env PYTHONDONTWRITEBYTECODE=1 \
   "${PROXY_ARGS[@]}"

#!/bin/bash
set -e

# Deletes a package from the Release Server
# Usage: ./scripts/delete.sh [options] <filename>

DEFAULT_URL="http://localhost:8000"

usage() {
    echo "Usage: $0 [options] <filename>"
    echo ""
    echo "Options:"
    echo "  -u, --url <url>      Server URL (default: ${RELEASE_SERVER_URL:-$DEFAULT_URL})"
    echo "  -t, --token <token>  Auth Token (default: env RELEASE_SERVER_TOKEN)"
    echo "  -h, --help           Show this help message"
    exit 1
}

# Defaults
SERVER_URL="${RELEASE_SERVER_URL:-$DEFAULT_URL}"
TOKEN="${RELEASE_SERVER_TOKEN}"
FILENAME=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -u|--url)
            SERVER_URL="$2"
            shift 2
            ;;
        -t|--token)
            TOKEN="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            if [ -z "$FILENAME" ]; then
                FILENAME="$1"
                shift
            else
                echo "Error: Unknown argument '$1'"
                usage
            fi
            ;;
    esac
done

# Validation
if [ -z "$FILENAME" ]; then
    echo "Error: No filename provided."
    usage
fi

if [ -z "$TOKEN" ]; then
    echo "Error: Auth token is required. Set RELEASE_SERVER_TOKEN env var or use --token."
    exit 1
fi

# Trim any path from filename if provided by mistake
FILENAME=$(basename "$FILENAME")

echo "🗑️  Deleting '$FILENAME' from $SERVER_URL..."

# Perform deletion
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X DELETE "${SERVER_URL}/assets/${FILENAME}" \
    -H "Authorization: Bearer ${TOKEN}")

# Handle response
if [ "$HTTP_STATUS" -eq 204 ]; then
    echo "✅ Deletion successful!"
elif [ "$HTTP_STATUS" -eq 404 ]; then
    echo "⚠️  Deletion failed: Package '$FILENAME' not found."
    exit 1
elif [ "$HTTP_STATUS" -eq 401 ] || [ "$HTTP_STATUS" -eq 403 ]; then
    echo "❌ Deletion failed: Authentication error ($HTTP_STATUS)."
    echo "   Check your token."
    exit 1
else
    echo "❌ Deletion failed with status code: $HTTP_STATUS"
    exit 1
fi

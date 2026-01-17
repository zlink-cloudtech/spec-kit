#!/bin/bash
set -e

# Uploads a package file to the Release Server
# Usage: ./scripts/upload.sh [options] <file_path>

DEFAULT_URL="http://localhost:8000"

usage() {
    echo "Usage: $0 [options] <file_path>"
    echo ""
    echo "Options:"
    echo "  -u, --url <url>      Server URL (default: ${RELEASE_SERVER_URL:-$DEFAULT_URL})"
    echo "  -t, --token <token>  Auth Token (default: env RELEASE_SERVER_TOKEN)"
    echo "  -f, --force          Overwrite existing file (default: false)"
    echo "  -h, --help           Show this help message"
    exit 1
}

# Defaults
SERVER_URL="${RELEASE_SERVER_URL:-$DEFAULT_URL}"
TOKEN="${RELEASE_SERVER_TOKEN}"
OVERWRITE="false"
FILE_PATH=""

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
        -f|--force)
            OVERWRITE="true"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            if [ -z "$FILE_PATH" ]; then
                FILE_PATH="$1"
                shift
            else
                echo "Error: Unknown argument '$1'"
                usage
            fi
            ;;
    esac
done

# Validation
if [ -z "$FILE_PATH" ]; then
    echo "Error: No file path provided."
    usage
fi

if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File '$FILE_PATH' not found."
    exit 1
fi

if [ -z "$TOKEN" ]; then
    echo "Error: Auth token is required. Set RELEASE_SERVER_TOKEN env var or use --token."
    exit 1
fi

# Determine filename for display
FILENAME=$(basename "$FILE_PATH")

echo "🚀 Uploading '$FILENAME' to $SERVER_URL..."
echo "   Overwrite: $OVERWRITE"

# Perform upload
RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "${SERVER_URL}/upload?overwrite=${OVERWRITE}" \
    -H "Authorization: Bearer ${TOKEN}" \
    -F "file=@${FILE_PATH}")

HTTP_STATUS=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

# Handle response
if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "✅ Upload successful!"
    if command -v jq &> /dev/null; then
        SHA256=$(echo "$BODY" | jq -r '.sha256 // empty')
        if [ ! -z "$SHA256" ] && [ "$SHA256" != "null" ]; then
            echo "   SHA256: $SHA256"
        fi
    else
        # Fallback simplistic parsing
        SHA256=$(echo "$BODY" | grep -o '"sha256":"[^"]*"' | cut -d'"' -f4)
        if [ ! -z "$SHA256" ]; then
             echo "   SHA256: $SHA256"
        fi
    fi
elif [ "$HTTP_STATUS" -eq 409 ]; then
    echo "⚠️  Upload failed: File already exists (Conflict)."
    echo "   Use --force to overwrite."
    exit 1
elif [ "$HTTP_STATUS" -eq 401 ] || [ "$HTTP_STATUS" -eq 403 ]; then
    echo "❌ Upload failed: Authentication error ($HTTP_STATUS)."
    echo "   Check your token."
    exit 1
else
    echo "❌ Upload failed with status code: $HTTP_STATUS"
    exit 1
fi

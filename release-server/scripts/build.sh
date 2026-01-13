#!/bin/bash
set -e

# Default values matches the spec
# Image name format: {REGISTRY}/{AUTHOR}/{IMAGE_NAME}:{TAG}
REGISTRY="${REGISTRY:-ghcr.io}"
AUTHOR="${AUTHOR:-spec-kit}" # Maps to namespace
IMAGE_NAME="${IMAGE_NAME:-release-server}"
TAG="${TAG:-latest}"

IMAGE_URI="${REGISTRY}/${AUTHOR}/${IMAGE_NAME}:${TAG}"
# Clean up double slashes if any (except protocol)
IMAGE_URI=$(echo "$IMAGE_URI" | sed 's|//|/|g')

echo "Building Docker image: ${IMAGE_URI}"
docker build -t "${IMAGE_URI}" .

echo "Build complete: ${IMAGE_URI}"

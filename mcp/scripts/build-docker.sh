#!/bin/bash
set -e

# Default config
IMAGE_NAME="speckit-mcp-server"
TAG="latest"

# Read config if exists
if [ -f "docker-config.json" ]; then
  # Simple parsing using node to avoid jq dependency
  IMAGE_NAME=$(node -p "require('./docker-config.json').imageName")
  TAG=$(node -p "require('./docker-config.json').tag")
fi

echo "Building Docker image: $IMAGE_NAME:$TAG"
docker build -t "$IMAGE_NAME:$TAG" .

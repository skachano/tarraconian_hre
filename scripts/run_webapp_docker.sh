#!/usr/bin/env bash
set -euo pipefail

# Script to run the Tarraconian Atlas Web App locally inside Docker
# Serves the docs/ directory on port 8080 (or PORT env var)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
PORT="${PORT:-8080}"

echo "=========================================================="
echo "Starting Tarraconian Atlas Web Server in Docker"
echo "Image: python:3.12-alpine"
echo "URL: http://localhost:${PORT}"
echo "Serving directory: ${REPO_DIR}/docs"
echo "=========================================================="
echo "Press Ctrl+C to stop the server."

docker run --rm \
    --name tarraconian_atlas_web \
    -p "${PORT}:8080" \
    -v "${REPO_DIR}/docs:/www:ro" \
    -w /www \
    python:3.12-alpine \
    python3 -m http.server 8080

#!/usr/bin/env bash
set -euo pipefail

# Script to run CK3 Map to GeoJSON Generation Pipeline inside Docker
# Mounts /mnt/windows (read-only for CK3 game files) and the repo workspace

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=========================================================="
echo "Running CK3 GeoJSON Generation in Docker"
echo "Image: ghcr.io/astral-sh/uv:0.9.9-python3.12-bookworm-slim"
echo "Workspace: ${REPO_DIR}"
echo "=========================================================="

docker run --rm \
    --name ck3_geojson_generator \
    -v "/mnt/windows:/mnt/windows:ro" \
    -v "${REPO_DIR}:/workspace" \
    -w /workspace \
    ghcr.io/astral-sh/uv:0.9.9-python3.12-bookworm-slim \
    uv run --with pillow --with numpy --with scipy --with opencv-python-headless --with shapely \
    python3 /workspace/scripts/generate_ck3_geojson.py "$@"

echo "=========================================================="
echo "GeoJSON Generation Complete!"
echo "=========================================================="

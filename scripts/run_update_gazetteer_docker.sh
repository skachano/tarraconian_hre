#!/usr/bin/env bash
set -euo pipefail

# Script to run CK3 Gazetteer Update Pipeline inside Docker
# Mounts /var/tmp (writable for results), /mnt/windows (read-only for save game), and workspace

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=========================================================="
echo "Running Roman Empire Gazetteer Update in Docker"
echo "Image: python:3.12-slim-bookworm"
echo "Target Workspace: ${REPO_DIR}"
echo "=========================================================="

docker run --rm \
    --name ck3_gazetteer_updater \
    -v "/mnt/windows:/mnt/windows:ro" \
    -v "/var/tmp:/var/tmp" \
    -v "${REPO_DIR}:/workspace" \
    -w /workspace \
    python:3.12-slim-bookworm \
    python3 /workspace/scripts/update_hre_gazetteer.py "$@"

echo "=========================================================="
echo "Gazetteer Update Pipeline Complete!"
echo "=========================================================="

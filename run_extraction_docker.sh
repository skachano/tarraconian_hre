#!/usr/bin/env bash
set -euo pipefail

# Script to run CK3 Save Game Extraction (Phase 1) inside Docker
# Mounts /tmp (writable for results), /mnt/windows (read-only for save game and CK3 files), and workspace

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="/tmp/ck3_audit_phase1"

mkdir -p "${OUTPUT_DIR}"

echo "=========================================================="
echo "Running CK3 Save Game Extraction (Phase 1) in Docker"
echo "Image: python:3.12-slim-bookworm"
echo "Output: ${OUTPUT_DIR}"
echo "=========================================================="

docker run --rm \
    --name ck3_phase1_extractor \
    -v "/mnt/windows:/mnt/windows:ro" \
    -v "/tmp:/tmp" \
    -v "${SCRIPT_DIR}:/workspace:ro" \
    python:3.12-slim-bookworm \
    python3 /workspace/extract_save_phase1.py "$@"

echo "=========================================================="
echo "Phase 1 Extraction Complete! Results written to ${OUTPUT_DIR}"
echo "=========================================================="

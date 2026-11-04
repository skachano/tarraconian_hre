#!/usr/bin/env bash
set -euo pipefail

# Script to run Phase 4: Title Resolution & Reconciliation inside Docker
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="/var/tmp/ck3_audit/phase4"

mkdir -p "${OUTPUT_DIR}"

echo "=========================================================="
echo "Running Phase 4 Title Resolution & Reconciliation in Docker"
echo "Image: python:3.12-slim-bookworm"
echo "Input: /var/tmp/ck3_audit/phase1 & /var/tmp/ck3_audit/phase3"
echo "Output: ${OUTPUT_DIR}"
echo "=========================================================="

docker run --rm \
    --name ck3_phase4_resolution \
    -v "/var/tmp:/var/tmp" \
    -v "${SCRIPT_DIR}:/workspace" \
    python:3.12-slim-bookworm \
    python3 /workspace/resolve_phase4_titles.py \
        --phase1-dir "/var/tmp/ck3_audit/phase1" \
        --phase3-dir "/var/tmp/ck3_audit/phase3" \
        --output-dir "${OUTPUT_DIR}" \
        --repo-dir "/workspace"

echo "=========================================================="
echo "Phase 4 Complete! Artifacts written to ${OUTPUT_DIR} and workspace"
echo "=========================================================="

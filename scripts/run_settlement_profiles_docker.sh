#!/usr/bin/env bash
set -euo pipefail

# Script to run Settlement History Profile Extraction inside Docker
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUTPUT_DIR="/var/tmp/ck3_audit/phase3"

mkdir -p "${OUTPUT_DIR}"

echo "=========================================================="
echo "Running Settlement History Profile Extraction in Docker"
echo "Image: python:3.12-slim-bookworm"
echo "Melted Save: /var/tmp/ck3_audit/melted_save.ck3"
echo "Output: ${OUTPUT_DIR}"
echo "=========================================================="

docker run --rm \
    --name ck3_settlement_profiles \
    -v "/var/tmp:/var/tmp" \
    -v "${REPO_DIR}:/workspace" \
    python:3.12-slim-bookworm \
    python3 /workspace/scripts/extract_settlement_history_profiles.py \
        --melted-save "/var/tmp/ck3_audit/melted_save.ck3" \
        --phase1-dir "/var/tmp/ck3_audit/phase1" \
        --phase3-dir "/var/tmp/ck3_audit/phase3" \
        --phase4-dir "/var/tmp/ck3_audit/phase4" \
        --output-dir "${OUTPUT_DIR}" \
        --repo-dir "/workspace"

echo "=========================================================="
echo "Extraction Complete! Artifacts written to ${OUTPUT_DIR} and workspace"
echo "=========================================================="

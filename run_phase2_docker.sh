#!/usr/bin/env bash
set -euo pipefail

# Script to run Phase 2: Title Lineage & Progression Mapping inside Docker
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="/tmp/ck3_audit_phase2"

mkdir -p "${OUTPUT_DIR}"

echo "=========================================================="
echo "Running Phase 2 Title Lineage Mapping in Docker"
echo "Image: python:3.12-slim-bookworm"
echo "Input: /tmp/ck3_audit_phase1"
echo "Output: ${OUTPUT_DIR}"
echo "=========================================================="

docker run --rm \
    --name ck3_phase2_lineage \
    -v "/tmp:/tmp" \
    -v "${SCRIPT_DIR}:/workspace" \
    python:3.12-slim-bookworm \
    python3 /workspace/extract_phase2_lineage.py \
        --phase1-dir "/tmp/ck3_audit_phase1" \
        --output-dir "${OUTPUT_DIR}" \
        --repo-dir "/workspace" \
        --md-ref "/workspace/anachronistic_titles_1059.md"

echo "=========================================================="
echo "Phase 2 Complete! Artifacts written to ${OUTPUT_DIR} and workspace"
echo "=========================================================="

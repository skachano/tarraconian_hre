#!/usr/bin/env bash
set -euo pipefail

# Script to run Phase 3: Automated Screening & Etymological Cross-Referencing inside Docker
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="/tmp/ck3_audit_phase3"

mkdir -p "${OUTPUT_DIR}"

echo "=========================================================="
echo "Running Phase 3 Title Screening Matrix in Docker"
echo "Image: python:3.12-slim-bookworm"
echo "Input: /tmp/ck3_audit_phase1 & /tmp/ck3_audit_phase2"
echo "Output: ${OUTPUT_DIR}"
echo "=========================================================="

docker run --rm \
    --name ck3_phase3_screening \
    -v "/tmp:/tmp" \
    -v "${SCRIPT_DIR}:/workspace" \
    python:3.12-slim-bookworm \
    python3 /workspace/screen_phase3_titles.py \
        --phase1-dir "/tmp/ck3_audit_phase1" \
        --phase2-dir "/tmp/ck3_audit_phase2" \
        --output-dir "${OUTPUT_DIR}" \
        --repo-dir "/workspace" \
        --md-ref "/workspace/anachronistic_titles_1059.md" \
        --tarr-ref "/workspace/tarraconian_titles_1059.md"

echo "=========================================================="
echo "Phase 3 Complete! Artifacts written to ${OUTPUT_DIR} and workspace"
echo "=========================================================="

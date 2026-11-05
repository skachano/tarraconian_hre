#!/usr/bin/env bash
set -euo pipefail

# Script to run Phase 2: Title Lineage & Progression Mapping inside Docker
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUTPUT_DIR="/var/tmp/ck3_audit/phase2"

mkdir -p "${OUTPUT_DIR}"

echo "=========================================================="
echo "Running Phase 2 Title Lineage Mapping in Docker"
echo "Image: python:3.12-slim-bookworm"
echo "Input: /var/tmp/ck3_audit/phase1"
echo "Output: ${OUTPUT_DIR}"
echo "=========================================================="

docker run --rm \
    --name ck3_phase2_lineage \
    -v "/var/tmp:/var/tmp" \
    -v "${REPO_DIR}:/workspace" \
    python:3.12-slim-bookworm \
    python3 /workspace/scripts/extract_phase2_lineage.py \
        --phase1-dir "/var/tmp/ck3_audit/phase1" \
        --output-dir "${OUTPUT_DIR}" \
        --repo-dir "/workspace" \
        --md-ref "/workspace/anachronistic_titles_1059.md"

echo "=========================================================="
echo "Phase 2 Complete! Artifacts written to ${OUTPUT_DIR} and workspace"
echo "=========================================================="

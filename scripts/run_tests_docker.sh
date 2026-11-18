#!/usr/bin/env bash
set -euo pipefail

# Script to run the complete test suite for Tarraconian Atlas in Docker:
# 1. Unit & Data Integrity tests with pytest (uv in python3.12-bookworm-slim)
# 2. End-to-End browser tests with Playwright (playwright:v1.55.0-noble)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "=========================================================="
echo "Running Tarraconian Atlas Test Suite in Docker"
echo "Repository: ${REPO_DIR}"
echo "=========================================================="

echo ""
echo "[Step 1/2] Running Data Integrity & Schema Tests (pytest)..."
echo "Container: ghcr.io/astral-sh/uv:0.9.9-python3.12-bookworm-slim"
echo "----------------------------------------------------------"
docker run --rm \
    -v "${REPO_DIR}:/workspace:ro" \
    -w /workspace \
    ghcr.io/astral-sh/uv:0.9.9-python3.12-bookworm-slim \
    uv run --with pytest pytest -v -o cache_dir=/tmp/.pytest_cache tests/test_data_integrity.py

echo ""
echo "[Step 2/2] Running End-to-End Browser Tests (Playwright)..."
echo "Container: mcr.microsoft.com/playwright:v1.55.0-noble"
echo "----------------------------------------------------------"
docker run --rm \
    -v "${REPO_DIR}:/workspace" \
    -w /workspace \
    -e PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    mcr.microsoft.com/playwright:v1.55.0-noble \
    bash -c "npm install --prefix /tmp/pw playwright@1.55.0 --silent && NODE_PATH=/tmp/pw/node_modules node tests/test_webapp_e2e.cjs"

echo ""
echo "=========================================================="
echo "🎉 ALL TESTS PASSED SUCCESSFULLY IN DOCKER CONTAINERS!"
echo "=========================================================="

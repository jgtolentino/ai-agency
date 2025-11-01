#!/bin/bash
# =============================================================================
# Health Check Wrapper Script for Odoo Deployments
# =============================================================================
# Usage: ./scripts/health_check.sh [url]
# Example: ./scripts/health_check.sh http://localhost:8069
#          ./scripts/health_check.sh https://odoo-staging.example.com
#
# This is a wrapper around the Python health_check.py script that provides
# a simpler interface for CI/CD pipelines and manual testing.
# =============================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  ${1}${NC}"
}

log_success() {
    echo -e "${GREEN}✅ ${1}${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  ${1}${NC}"
}

log_error() {
    echo -e "${RED}❌ ${1}${NC}"
}

# Parse arguments
URL=${1:-http://localhost:8069}
TIMEOUT=${2:-30}
OUTPUT_FILE="health_results.json"

log_info "Running health checks on ${URL}..."

# Check if Python script exists
if [ ! -f "scripts/health_check.py" ]; then
    log_error "Health check script not found: scripts/health_check.py"
    exit 2
fi

# Check Python is available
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 not found. Please install Python 3.11+"
    exit 2
fi

# Run health check
log_info "Running comprehensive health check (timeout: ${TIMEOUT}s)..."

if python3 scripts/health_check.py \
    --target blue \
    --url "${URL}" \
    --timeout "${TIMEOUT}" \
    --json-output "${OUTPUT_FILE}"; then

    # Check JSON output
    if [ -f "${OUTPUT_FILE}" ]; then
        HEALTHY=$(jq -r '.healthy' "${OUTPUT_FILE}" 2>/dev/null || echo "false")

        if [ "${HEALTHY}" == "true" ]; then
            log_success "All health checks passed"

            # Show summary
            echo ""
            log_info "Health Check Summary:"
            jq -r '.checks[] | "  \(.name): \(.status)"' "${OUTPUT_FILE}" || true
            echo ""

            exit 0
        else
            log_error "Health checks failed"
            echo ""
            log_error "Failed Checks:"
            jq -r '.checks[] | select(.status != "passed") | "  \(.name): \(.status) - \(.message // "No details")"' "${OUTPUT_FILE}" || true
            echo ""
            exit 1
        fi
    else
        log_warning "JSON output file not found - assuming success"
        exit 0
    fi
else
    log_error "Health check script execution failed"

    if [ -f "${OUTPUT_FILE}" ]; then
        echo ""
        log_error "Error details:"
        cat "${OUTPUT_FILE}"
        echo ""
    fi

    exit 1
fi

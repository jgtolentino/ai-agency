#!/bin/bash
# =============================================================================
# DigitalOcean App Platform Deployment Script
# =============================================================================
# Usage: ./scripts/deploy_do.sh [environment] [image_tag]
# Example: ./scripts/deploy_do.sh staging latest
#          ./scripts/deploy_do.sh production v1.2.3
#
# Environment variables required:
# - DO_ACCESS_TOKEN: DigitalOcean API token
# - DO_APP_ID_STAGING: Staging app ID
# - DO_APP_ID_PROD: Production app ID
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
ENV=${1:-staging}
IMAGE_TAG=${2:-latest}

log_info "Starting deployment to ${ENV} with image tag ${IMAGE_TAG}..."

# Validate environment
if [[ "${ENV}" != "staging" && "${ENV}" != "production" ]]; then
    log_error "Invalid environment: ${ENV}. Must be 'staging' or 'production'"
    exit 1
fi

# Check doctl is installed
if ! command -v doctl &> /dev/null; then
    log_error "doctl CLI not found. Install: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check authentication
if ! doctl auth list &> /dev/null; then
    log_error "doctl not authenticated. Run: doctl auth init"
    exit 1
fi

# Get app ID
if [ "${ENV}" == "production" ]; then
    APP_ID="${DO_APP_ID_PROD:-}"
    SPEC_FILE="infra/do/app-spec-production.yaml"
else
    APP_ID="${DO_APP_ID_STAGING:-}"
    SPEC_FILE="infra/do/app-spec-staging.yaml"
fi

if [ -z "${APP_ID}" ]; then
    log_error "App ID not set for ${ENV}. Set DO_APP_ID_STAGING or DO_APP_ID_PROD"
    exit 1
fi

log_info "App ID: ${APP_ID}"

# Check app spec exists
if [ ! -f "${SPEC_FILE}" ]; then
    log_error "App spec not found: ${SPEC_FILE}"
    exit 1
fi

# Backup original spec
cp "${SPEC_FILE}" "${SPEC_FILE}.backup"
log_info "Backed up app spec to ${SPEC_FILE}.backup"

# Update image tag in app spec
log_info "Updating image tag to: ${IMAGE_TAG}"
sed -i.tmp "s|image:.*|image: registry.digitalocean.com/insightpulse/odoo:${IMAGE_TAG}|g" "${SPEC_FILE}"
rm -f "${SPEC_FILE}.tmp"

# Show diff
log_info "Changes to app spec:"
diff -u "${SPEC_FILE}.backup" "${SPEC_FILE}" || true

# Confirm deployment
if [ "${ENV}" == "production" ]; then
    read -p "⚠️  Deploy to PRODUCTION? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
        log_warning "Deployment cancelled"
        mv "${SPEC_FILE}.backup" "${SPEC_FILE}"
        exit 0
    fi
fi

# Update app
log_info "Updating app configuration..."
if ! doctl apps update "${APP_ID}" --spec "${SPEC_FILE}"; then
    log_error "Failed to update app configuration"
    mv "${SPEC_FILE}.backup" "${SPEC_FILE}"
    exit 1
fi

# Create deployment
log_info "Creating deployment..."
DEPLOYMENT_ID=$(doctl apps create-deployment "${APP_ID}" --force-rebuild --format ID --no-header)

if [ -z "${DEPLOYMENT_ID}" ]; then
    log_error "Failed to create deployment"
    mv "${SPEC_FILE}.backup" "${SPEC_FILE}"
    exit 1
fi

log_success "Deployment created: ${DEPLOYMENT_ID}"
log_info "Waiting for completion..."

# Wait for deployment
if ! doctl apps get-deployment "${APP_ID}" "${DEPLOYMENT_ID}" --wait; then
    log_error "Deployment failed or timed out"
    mv "${SPEC_FILE}.backup" "${SPEC_FILE}"
    exit 1
fi

log_success "Deployment completed successfully"

# Get app URL
APP_URL=$(doctl apps get "${APP_ID}" --format DefaultIngress --no-header)
log_info "App URL: https://${APP_URL}"

# Run health check if available
if [ -f "scripts/health_check.sh" ]; then
    log_info "Running health checks..."
    if bash scripts/health_check.sh "https://${APP_URL}"; then
        log_success "Health checks passed"
    else
        log_error "Health checks failed"
        log_warning "Consider rolling back with: ./scripts/rollback_do.sh ${ENV}"
        exit 1
    fi
else
    log_warning "Health check script not found - skipping validation"
fi

# Clean up backup
rm -f "${SPEC_FILE}.backup"

# Summary
echo ""
log_success "==================================="
log_success "Deployment Summary"
log_success "==================================="
log_success "Environment: ${ENV}"
log_success "Image Tag: ${IMAGE_TAG}"
log_success "Deployment ID: ${DEPLOYMENT_ID}"
log_success "App URL: https://${APP_URL}"
log_success "==================================="
echo ""

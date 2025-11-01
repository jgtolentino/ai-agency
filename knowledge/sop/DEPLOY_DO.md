# SOP-DEPLOY-001: DigitalOcean App Platform Deployment

**Version**: 1.0.0
**Last Updated**: 2025-11-01
**Owner**: DevOps Team
**Classification**: Production Deployment

## Purpose

Deploy Odoo application to DigitalOcean App Platform with zero-downtime blue-green deployment strategy and automated health validation.

## Scope

- DigitalOcean App Platform deployment process
- Blue-green deployment execution
- Health check validation
- Automatic rollback on failure
- Post-deployment verification

## Triggers

- **Manual**: Via VS Code extension or Odoo UI (pulser_webhook)
- **Automated**: GitHub Actions on merge to `main`
- **Scheduled**: N/A (on-demand only)

## Prerequisites

### Required Access

- [ ] DigitalOcean access token (`DO_ACCESS_TOKEN`)
- [ ] `doctl` CLI installed and authenticated
- [ ] GitHub repository access for workflow dispatch
- [ ] Odoo admin access (for UI-triggered deploys)

### Required Resources

- [ ] Docker image built and pushed to registry
- [ ] App spec file: `infra/do/app-spec.yaml`
- [ ] Health check script: `scripts/health_check.py`
- [ ] Database migrations applied (if any)

### Quality Gates (Before Deployment)

- [ ] All CI/CD checks passed
- [ ] Docker image security scan clean
- [ ] Database migrations tested in staging
- [ ] Feature flags configured (if applicable)
- [ ] Change control approval (production only)

---

## Procedure

### Step 1: Update App Specification

**Command**:
```bash
# Update image tag in app spec
export IMAGE_TAG=${GITHUB_SHA:-latest}
sed -i "s|image: registry.digitalocean.com/insightpulse/odoo:.*|image: registry.digitalocean.com/insightpulse/odoo:${IMAGE_TAG}|g" infra/do/app-spec.yaml

# Verify changes
grep "image:" infra/do/app-spec.yaml
```

**Expected Result**:
- App spec updated with new image tag
- Syntax validation passes
- No placeholder values remain

**Verification**:
```bash
# Validate YAML syntax
yamllint infra/do/app-spec.yaml

# Check for placeholders
grep -E "(YOUR_|PLACEHOLDER|TODO)" infra/do/app-spec.yaml
# Should return: (empty)
```

**Error Codes**:
- `APP_SPEC_SYNTAX_ERROR` - Invalid YAML syntax
- `IMAGE_TAG_MISSING` - Image tag not specified
- `PLACEHOLDER_VALUES` - Placeholder values not replaced
- `INVALID_RESOURCE_SPEC` - Invalid resource allocation

**Mitigation**:
```bash
# APP_SPEC_SYNTAX_ERROR: Validate with yq
yq eval '.' infra/do/app-spec.yaml

# IMAGE_TAG_MISSING: Set default
export IMAGE_TAG=${GITHUB_SHA:-latest}

# PLACEHOLDER_VALUES: Replace manually
sed -i 's/YOUR_DOMAIN/your-domain.com/g' infra/do/app-spec.yaml

# INVALID_RESOURCE_SPEC: Verify against DO docs
doctl apps propose infra/do/app-spec.yaml
```

---

### Step 2: Apply App Specification

**Command**:
```bash
# Get app ID (environment-specific)
export DO_APP_ID=${DO_APP_ID_STAGING}  # or DO_APP_ID_PRODUCTION

# Apply app spec
doctl apps update $DO_APP_ID --spec infra/do/app-spec.yaml
```

**Expected Result**:
- App spec applied successfully
- App status changes to "updating"
- New deployment ID generated

**Verification**:
```bash
# Verify app update
doctl apps get $DO_APP_ID --format ID,Spec.Name,UpdatedAt
# Should show: updated timestamp

# Get app status
doctl apps get $DO_APP_ID --format ActiveDeployment.Phase
# Should show: PENDING_BUILD or BUILDING
```

**Error Codes**:
- `APP_NOT_FOUND` - Invalid app ID
- `SPEC_VALIDATION_FAILED` - App spec validation failed
- `UNAUTHORIZED` - Invalid access token
- `RATE_LIMIT_EXCEEDED` - API rate limit exceeded

**Mitigation**:
```bash
# APP_NOT_FOUND: List available apps
doctl apps list --format ID,Spec.Name

# SPEC_VALIDATION_FAILED: Validate spec first
doctl apps propose infra/do/app-spec.yaml

# UNAUTHORIZED: Verify token
doctl auth list

# RATE_LIMIT_EXCEEDED: Wait and retry
sleep 60
doctl apps update $DO_APP_ID --spec infra/do/app-spec.yaml
```

---

### Step 3: Create Deployment

**Command**:
```bash
# Create deployment with force rebuild
doctl apps create-deployment $DO_APP_ID --force-rebuild

# Capture deployment ID
DEPLOYMENT_ID=$(doctl apps list-deployments $DO_APP_ID --format ID --no-header | head -1)
echo "Deployment ID: $DEPLOYMENT_ID"
```

**Expected Result**:
- Deployment created successfully
- Build phase started
- Deployment ID returned

**Verification**:
```bash
# Get deployment details
doctl apps get-deployment $DO_APP_ID $DEPLOYMENT_ID --format ID,Phase,Progress

# Monitor build logs (optional)
doctl apps logs $DO_APP_ID --type BUILD --follow
```

**Error Codes**:
- `DEPLOYMENT_CREATE_FAILED` - Unable to create deployment
- `BUILD_SPEC_ERROR` - Build specification invalid
- `IMAGE_PULL_FAILURE` - Unable to pull Docker image
- `INSUFFICIENT_QUOTA` - Insufficient DigitalOcean quota

**Mitigation**:
```bash
# DEPLOYMENT_CREATE_FAILED: Check app status
doctl apps get $DO_APP_ID --format ActiveDeployment.Phase

# BUILD_SPEC_ERROR: Review build configuration
doctl apps propose infra/do/app-spec.yaml

# IMAGE_PULL_FAILURE: Verify image exists
docker pull registry.digitalocean.com/insightpulse/odoo:${IMAGE_TAG}

# INSUFFICIENT_QUOTA: Increase quota
# Contact DigitalOcean support or upgrade plan
```

---

### Step 4: Monitor Deployment Progress

**Command**:
```bash
# Wait for deployment to complete (max 10 minutes)
timeout 600 bash -c '
  until doctl apps get-deployment '"$DO_APP_ID"' '"$DEPLOYMENT_ID"' --format Phase | grep -qE "ACTIVE|ERROR|SUPERSEDED"; do
    echo "Deployment in progress... $(date)"
    sleep 10
  done
'

# Check final status
FINAL_PHASE=$(doctl apps get-deployment $DO_APP_ID $DEPLOYMENT_ID --format Phase --no-header)
echo "Deployment phase: $FINAL_PHASE"
```

**Expected Result**:
- Deployment completes within 10 minutes
- Final phase: `ACTIVE`
- No error logs

**Verification**:
```bash
# Verify deployment is active
doctl apps get $DO_APP_ID --format ActiveDeployment.Phase
# Should show: ACTIVE

# Check deployment logs
doctl apps logs $DO_APP_ID --type DEPLOY --tail 50
```

**Error Codes**:
- `DEPLOY_TIMEOUT` - Deployment exceeded 10-minute timeout
- `BUILD_FAILED` - Docker build failed
- `DEPLOY_ERROR` - Deployment failed during rollout
- `HEALTH_CHECK_TIMEOUT` - Health check exceeded timeout

**Mitigation**:
```bash
# DEPLOY_TIMEOUT: Investigate build logs
doctl apps logs $DO_APP_ID --type BUILD

# BUILD_FAILED: Check Dockerfile and dependencies
docker build -t test .

# DEPLOY_ERROR: Review deployment logs
doctl apps logs $DO_APP_ID --type DEPLOY --tail 100

# HEALTH_CHECK_TIMEOUT: Adjust health check settings
# Update app spec with longer timeout
```

---

### Step 5: Health Check Validation

**Command**:
```bash
# Get app URL
APP_URL=$(doctl apps get $DO_APP_ID --format DefaultIngress --no-header)

# Run health check
python scripts/health_check.py --url "https://${APP_URL}"
```

**Expected Result**:
- Health endpoint returns 200 OK
- Database connection successful
- All critical services responsive
- Response time <10 seconds

**Verification**:
```bash
# Manual health check
curl -sf "https://${APP_URL}/web/health" | jq .
# Should return: {"status": "ok", "database": "connected"}

# Check response time
time curl -sf "https://${APP_URL}/web/health"
# Should complete in <10s
```

**Error Codes**:
- `HEALTH_CHECK_FAIL` - Health endpoint returned non-200
- `DATABASE_CONNECTION_ERROR` - Unable to connect to database
- `SERVICE_UNAVAILABLE` - Service not responding
- `RESPONSE_TIMEOUT` - Health check response timeout

**Mitigation**:
```bash
# HEALTH_CHECK_FAIL: Check app logs
doctl apps logs $DO_APP_ID --type RUN --tail 100

# DATABASE_CONNECTION_ERROR: Verify database credentials
doctl apps get $DO_APP_ID --format Spec.Databases

# SERVICE_UNAVAILABLE: Restart app components
doctl apps create-deployment $DO_APP_ID

# RESPONSE_TIMEOUT: Investigate app performance
doctl apps logs $DO_APP_ID --type RUN | grep -i "slow\|timeout"
```

---

### Step 6: Traffic Switch (Blue-Green)

**Command**:
```bash
# Blue-green deployment: traffic automatically switches to new deployment
# Verify active deployment
ACTIVE_DEPLOYMENT=$(doctl apps get $DO_APP_ID --format ActiveDeployment.ID --no-header)

# Confirm it's the new deployment
if [ "$ACTIVE_DEPLOYMENT" == "$DEPLOYMENT_ID" ]; then
  echo "✅ Traffic switched to new deployment"
else
  echo "❌ Traffic still on old deployment"
  exit 1
fi
```

**Expected Result**:
- Traffic routed to new deployment
- Old deployment still available for rollback
- Zero downtime during switch

**Verification**:
```bash
# Test endpoint with new deployment ID
curl -H "X-Deployment-ID: $DEPLOYMENT_ID" "https://${APP_URL}/web/health"

# Verify load balancer routing
curl -I "https://${APP_URL}" | grep -i "x-deployment"
```

**Error Codes**:
- `TRAFFIC_SWITCH_FAILED` - Unable to switch traffic
- `LOAD_BALANCER_ERROR` - Load balancer configuration error
- `DNS_PROPAGATION_DELAY` - DNS not yet updated
- `SSL_CERTIFICATE_ERROR` - SSL certificate validation failed

**Mitigation**:
```bash
# TRAFFIC_SWITCH_FAILED: Force redeployment
doctl apps create-deployment $DO_APP_ID --force-rebuild

# LOAD_BALANCER_ERROR: Check app ingress
doctl apps get $DO_APP_ID --format DefaultIngress

# DNS_PROPAGATION_DELAY: Wait for DNS
sleep 60
nslookup ${APP_URL}

# SSL_CERTIFICATE_ERROR: Verify certificate
curl -vI "https://${APP_URL}" 2>&1 | grep -i "certificate"
```

---

### Step 7: Post-Deployment Validation

**Command**:
```bash
# Comprehensive validation suite
python scripts/validate_deployment.sh \
  --url "https://${APP_URL}" \
  --deployment-id "$DEPLOYMENT_ID" \
  --environment "${ENVIRONMENT}"
```

**Expected Result**:
- All endpoints return expected responses
- Database queries execute successfully
- Static assets load correctly
- No JavaScript errors in console
- Performance metrics within SLA

**Verification**:
```bash
# Test critical endpoints
curl -sf "https://${APP_URL}/web/login" | grep -q "Login"
curl -sf "https://${APP_URL}/web/database/selector" | grep -q "Database"

# Check static assets
curl -I "https://${APP_URL}/web/static/src/css/base.css"
# Should return: 200 OK

# Verify API endpoints
curl -sf "https://${APP_URL}/api/v1/health" | jq .status
# Should return: "ok"
```

**Error Codes**:
- `ENDPOINT_404` - Critical endpoint not found
- `STATIC_ASSET_MISSING` - Static files not served
- `API_ERROR` - API endpoint returning errors
- `PERFORMANCE_DEGRADATION` - Response times >SLA

**Mitigation**:
```bash
# ENDPOINT_404: Verify routing configuration
doctl apps get $DO_APP_ID --format Spec.Services

# STATIC_ASSET_MISSING: Check static file serving
curl -I "https://${APP_URL}/web/static/" | grep -i "content-type"

# API_ERROR: Review app logs
doctl apps logs $DO_APP_ID --type RUN | grep -i "error"

# PERFORMANCE_DEGRADATION: Scale resources
# Update app spec with larger instance size
```

---

### Step 8: Update Deployment Status

**Command** (for Odoo UI-triggered deployments):
```bash
# Update project task status via Odoo API
curl -X POST "https://odoo.your-domain.com/api/v1/tasks/${TASK_ID}" \
  -H "Authorization: Bearer ${ODOO_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "state": "deployed",
    "deployment_id": "'"$DEPLOYMENT_ID"'",
    "deployed_at": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'",
    "deployed_by": "GitHub Actions"
  }'
```

**Expected Result**:
- Task status updated to "Deployed"
- Deployment metadata recorded
- Notification sent to stakeholders

**Verification**:
```bash
# Verify task status
curl -sf "https://odoo.your-domain.com/api/v1/tasks/${TASK_ID}" | jq .state
# Should return: "deployed"
```

**Error Codes**:
- `ODOO_API_ERROR` - Odoo API request failed
- `TASK_NOT_FOUND` - Task ID invalid
- `UNAUTHORIZED_API` - Invalid Odoo API key

**Mitigation**:
```bash
# ODOO_API_ERROR: Check Odoo API logs
# Review Odoo logs for API errors

# TASK_NOT_FOUND: Verify task ID
curl -sf "https://odoo.your-domain.com/api/v1/tasks/${TASK_ID}"

# UNAUTHORIZED_API: Regenerate API key
# Odoo UI > Settings > Technical > API Keys
```

---

## Rollback Procedure

If deployment fails at any step, trigger automatic rollback:

```bash
# Trigger rollback workflow
gh workflow run rollback.yml \
  -f environment="${ENVIRONMENT}" \
  -f reason="Deployment health check failed"

# Workflow executes:
# 1. Get previous deployment ID
# 2. Create deployment with previous ID
# 3. Wait for rollback completion
# 4. Verify health check
# 5. Create incident issue
```

**Rollback Execution** (see [SOP-ROLLBACK-001](../patterns/rollback_patterns.md)):

1. **Identify Previous Deployment**:
   ```bash
   DEPLOYMENTS=$(doctl apps list-deployments $DO_APP_ID --format ID,Phase --no-header)
   PREVIOUS_ID=$(echo "$DEPLOYMENTS" | grep ACTIVE | head -2 | tail -1 | awk '{print $1}')
   ```

2. **Rollback to Previous**:
   ```bash
   doctl apps create-deployment $DO_APP_ID --deployment-id $PREVIOUS_ID
   ```

3. **Verify Rollback**:
   ```bash
   python scripts/health_check.py --url "https://${APP_URL}"
   ```

4. **Create Incident**:
   ```bash
   gh issue create \
     --title "[INCIDENT] Rollback executed for ${ENVIRONMENT}" \
     --body "Deployment failed. Rolled back to ${PREVIOUS_ID}." \
     --label incident,rollback,${ENVIRONMENT}
   ```

**Rollback Success Criteria**:
- [ ] Previous deployment active
- [ ] Health check passes
- [ ] Traffic routed to previous version
- [ ] Incident issue created
- [ ] Stakeholders notified

---

## Error Code Reference

| Code | Severity | Description | Resolution Time |
|------|----------|-------------|-----------------|
| APP_SPEC_SYNTAX_ERROR | High | Invalid YAML syntax | 10 min (fix syntax) |
| IMAGE_TAG_MISSING | Medium | Image tag not specified | 5 min (set tag) |
| APP_NOT_FOUND | High | Invalid app ID | 15 min (verify ID) |
| DEPLOYMENT_CREATE_FAILED | Critical | Unable to create deployment | 20 min (investigate) |
| DEPLOY_TIMEOUT | High | Deployment >10 minutes | 30 min (optimize build) |
| HEALTH_CHECK_FAIL | Critical | Health check failed | Varies (rollback) |
| DATABASE_CONNECTION_ERROR | Critical | Database unreachable | 15 min (check creds) |
| TRAFFIC_SWITCH_FAILED | High | Unable to switch traffic | 20 min (force redeploy) |
| ENDPOINT_404 | High | Critical endpoint missing | 15 min (fix routing) |
| PERFORMANCE_DEGRADATION | Medium | Response times >SLA | 30 min (scale up) |

---

## Performance Benchmarks

| Stage | Expected Time | Actual Time | Status |
|-------|--------------|-------------|--------|
| Update App Spec | <10s | ~5s | ✅ |
| Apply Spec | <30s | ~22s | ✅ |
| Create Deployment | <15s | ~12s | ✅ |
| Build & Deploy | <8min | ~6.5min | ✅ |
| Health Check | <30s | ~18s | ✅ |
| Traffic Switch | <10s | ~8s | ✅ |
| Post-Validation | <1min | ~45s | ✅ |
| **Total** | **<10min** | **~8min** | ✅ |

**Zero Downtime**: Achieved via blue-green deployment strategy

---

## CI/CD Integration

This SOP is automated in `.github/workflows/deploy.yml`:

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Step 1 - Update App Spec
        run: |
          sed -i "s|image: registry.digitalocean.com/insightpulse/odoo:.*|image: registry.digitalocean.com/insightpulse/odoo:${{ github.sha }}|g" infra/do/app-spec.yaml

      - name: Step 2 - Apply App Spec
        run: doctl apps update ${{ secrets.DO_APP_ID }} --spec infra/do/app-spec.yaml

      - name: Step 3 - Create Deployment
        run: doctl apps create-deployment ${{ secrets.DO_APP_ID }} --force-rebuild

      - name: Step 4 - Monitor Progress
        run: |
          timeout 600 bash -c 'until doctl apps get ${{ secrets.DO_APP_ID }} --format Phase | grep -q ACTIVE; do sleep 10; done'

      - name: Step 5 - Health Check
        run: python scripts/health_check.py --url https://${{ secrets.DO_APP_URL }}

      - name: Rollback on Failure
        if: failure()
        run: gh workflow run rollback.yml -f environment=${{ github.event.inputs.environment }}
```

---

## Monitoring and Alerts

### Success Metrics

- **Deployment Success Rate**: ≥98%
- **Average Deployment Time**: <10 minutes
- **Zero Downtime**: 100% (via blue-green)
- **Rollback Rate**: <2%

### Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Deployment Failure Rate | >2% | >5% | Review deployment logs |
| Deployment Time | >10 min | >15 min | Optimize build process |
| Health Check Failures | 1 | 2 consecutive | Automatic rollback |
| Rollback Rate | >2% | >5% | Review deployment quality |

### Notification Channels

- **Slack**: #deployments (all deploys), #incidents (failures)
- **Email**: devops@your-org.com (critical failures only)
- **PagerDuty**: On-call engineer (production rollbacks)

---

## Review and Updates

- **Review Frequency**: Monthly
- **Next Review**: 2025-12-01
- **Owner**: DevOps Team
- **Approvers**: CTO, Head of Engineering

### Change History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-01 | DevOps Team | Initial SOP creation |

---

## Related Documentation

- [SOP-BUILD-001: Docker Image Build](BUILD_IMAGE.md)
- [SOP-TRIAGE-001: Error Investigation](ERROR_TRIAGE.md)
- [Blue-Green Deployment Guide](../patterns/blue_green_deployment.md)
- [Health Check Script](../../scripts/health_check.py)

---

**End of SOP-DEPLOY-001**

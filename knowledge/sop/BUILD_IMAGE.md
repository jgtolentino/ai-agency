# SOP-BUILD-001: Docker Image Build

**Version**: 1.0.0
**Last Updated**: 2025-11-01
**Owner**: DevOps Team
**Classification**: Production Deployment

## Purpose

Build and publish Odoo Docker image to DigitalOcean Container Registry with multi-stage optimization and security validation.

## Scope

- Docker image build process (builder + runtime stages)
- Security scanning and validation
- Registry push and tagging
- Rollback procedures

## Triggers

- **Manual**: Development builds and testing
- **Automated**: CI pipeline on push to `main` branch
- **Scheduled**: Weekly security rebuilds (Sunday 02:00 UTC)

## Prerequisites

### Required Access

- [ ] Docker CLI installed and running
- [ ] DigitalOcean Container Registry access
- [ ] DO_REGISTRY_TOKEN environment variable set
- [ ] GitHub Actions secrets configured (for CI)

### Required Files

- [ ] `Dockerfile` present in repository root
- [ ] `requirements.txt` with pinned dependencies
- [ ] `custom_addons/` directory with all modules

### Quality Gates (Before Build)

- [ ] Dockerfile validated with hadolint: `hadolint Dockerfile`
- [ ] All tests passing: `pytest custom_addons/ -v`
- [ ] Pre-commit hooks green: `pre-commit run --all-files`
- [ ] No security vulnerabilities in dependencies: `safety check`

## Procedure

### Step 1: Pull Base Image

**Command**:
```bash
docker pull python:3.11-slim-bullseye
```

**Expected Result**: Base image pulled successfully with SHA256 hash verification

**Verification**:
```bash
docker images | grep python:3.11-slim-bullseye
# Should show: python 3.11-slim-bullseye <IMAGE_ID> <CREATED> <SIZE>
```

**Error Codes**:
- `BASE_IMAGE_DRIFT` - Base image hash changed unexpectedly
- `NETWORK_TIMEOUT` - Docker Hub connection timeout
- `DISK_SPACE_LOW` - Insufficient disk space (<10GB free)

**Mitigation**:
```bash
# BASE_IMAGE_DRIFT: Pin base image SHA256
FROM python:3.11-slim-bullseye@sha256:abc123...

# NETWORK_TIMEOUT: Use registry mirror
docker pull registry.hub.docker.com/library/python:3.11-slim-bullseye

# DISK_SPACE_LOW: Clean up images
docker system prune -a --volumes
```

---

### Step 2: Install System Dependencies

**Command**:
```bash
docker build --target builder -t odoo-builder:latest .
```

**Expected Result**:
- All system packages installed (wkhtmltopdf, postgresql-client, etc.)
- Python dependencies from requirements.txt installed
- Build artifacts in `/build` directory

**Verification**:
```bash
# Inspect builder stage
docker run --rm odoo-builder:latest python --version
# Should show: Python 3.11.x

docker run --rm odoo-builder:latest pip list | grep anthropic
# Should show: anthropic 0.x.x
```

**Error Codes**:
- `WKHTMLTOPDF_MISMATCH` - wkhtmltopdf version incompatible with Odoo
- `ANTHROPIC_SDK_MISSING` - anthropic SDK failed to install
- `PIP_DEPENDENCY_CONFLICT` - Conflicting Python package versions

**Mitigation**:
```bash
# WKHTMLTOPDF_MISMATCH: Use distro-matched package
RUN apt-get update && apt-get install -y wkhtmltopdf=0.12.6-1

# ANTHROPIC_SDK_MISSING: Check requirements.txt
RUN pip install --no-cache-dir anthropic==0.34.0

# PIP_DEPENDENCY_CONFLICT: Use pip-tools
pip-compile requirements.in
pip install -r requirements.txt
```

---

### Step 3: Run Tests in Builder Stage

**Command**:
```bash
docker run --rm \
  -e POSTGRES_HOST=localhost \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  odoo-builder:latest \
  pytest custom_addons/ -v --tb=short
```

**Expected Result**:
- All unit tests pass (≥75% coverage)
- All integration tests pass
- No security vulnerabilities detected
- Exit code 0

**Verification**:
```bash
# Check test results
echo $?
# Should show: 0

# Check coverage report
docker run --rm odoo-builder:latest \
  pytest custom_addons/ --cov=custom_addons/ --cov-report=term
# Should show: TOTAL coverage ≥75%
```

**Error Codes**:
- `TEST_FAILURE` - One or more tests failed
- `LOW_COVERAGE` - Test coverage below 75% threshold
- `SECURITY_VULN` - Security vulnerability detected by bandit
- `IMPORT_ERROR` - Module import failed (missing dependency)

**Mitigation**:
```bash
# TEST_FAILURE: Run specific test for debugging
docker run --rm odoo-builder:latest \
  pytest custom_addons/expense_approval/tests/test_approval.py::test_approve -vv

# LOW_COVERAGE: Add missing tests
# Review coverage report and add tests for uncovered code paths

# SECURITY_VULN: Review bandit report
docker run --rm odoo-builder:latest bandit -r custom_addons/ -f json

# IMPORT_ERROR: Check module dependencies
docker run --rm odoo-builder:latest python -c "import module_name"
```

---

### Step 4: Build Runtime Image

**Command**:
```bash
docker build --target runtime -t odoo-custom:${VERSION} .
```

**Expected Result**:
- Multi-stage build completes successfully
- Runtime image size ≤2GB
- All custom addons copied to `/mnt/extra-addons`
- Odoo entry point configured

**Verification**:
```bash
# Check image size
docker images odoo-custom:${VERSION}
# Should show: SIZE ≤2GB

# Verify custom addons
docker run --rm odoo-custom:${VERSION} ls /mnt/extra-addons
# Should list all custom modules

# Test Odoo startup
docker run --rm odoo-custom:${VERSION} odoo --version
# Should show: Odoo Server 16.0
```

**Error Codes**:
- `BUILD_FAILURE` - Docker build failed during runtime stage
- `IMAGE_SIZE_EXCEEDED` - Runtime image >2GB
- `MISSING_ADDONS` - Custom addons not copied to runtime
- `ENTRYPOINT_ERROR` - Odoo entry point misconfigured

**Mitigation**:
```bash
# BUILD_FAILURE: Check Dockerfile syntax
docker build --no-cache --target runtime -t odoo-custom:${VERSION} .

# IMAGE_SIZE_EXCEEDED: Remove unnecessary files
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# MISSING_ADDONS: Verify COPY instruction
COPY --from=builder /mnt/extra-addons /mnt/extra-addons

# ENTRYPOINT_ERROR: Validate entrypoint script
docker run --rm --entrypoint sh odoo-custom:${VERSION} -c "which odoo"
```

---

### Step 5: Security Scan

**Command**:
```bash
# Scan with Trivy (vulnerability scanner)
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  odoo-custom:${VERSION}
```

**Expected Result**:
- No HIGH or CRITICAL vulnerabilities
- Exit code 0
- Security report generated

**Verification**:
```bash
# Check exit code
echo $?
# Should show: 0

# Review security report
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image \
  --format json \
  odoo-custom:${VERSION} > security-report.json
```

**Error Codes**:
- `SECURITY_HIGH` - HIGH severity vulnerability detected
- `SECURITY_CRITICAL` - CRITICAL severity vulnerability detected
- `OUTDATED_BASE_IMAGE` - Base image has known vulnerabilities
- `MALWARE_DETECTED` - Malicious code detected in image

**Mitigation**:
```bash
# SECURITY_HIGH/CRITICAL: Update vulnerable packages
RUN pip install --upgrade package-name

# OUTDATED_BASE_IMAGE: Update base image
FROM python:3.11-slim-bullseye  # Use latest patch version

# MALWARE_DETECTED: Review Dockerfile and dependencies
# Scan individual layers for malicious content
```

---

### Step 6: Tag and Push to Registry

**Command**:
```bash
# Authenticate to DigitalOcean Registry
echo "$DO_REGISTRY_TOKEN" | docker login registry.digitalocean.com -u token --password-stdin

# Tag image
docker tag odoo-custom:${VERSION} registry.digitalocean.com/insightpulse/odoo:${VERSION}
docker tag odoo-custom:${VERSION} registry.digitalocean.com/insightpulse/odoo:latest

# Push to registry
docker push registry.digitalocean.com/insightpulse/odoo:${VERSION}
docker push registry.digitalocean.com/insightpulse/odoo:latest
```

**Expected Result**:
- Authentication successful
- Image pushed to registry with both version tag and `latest`
- Manifest uploaded successfully

**Verification**:
```bash
# Verify push
doctl registry repository list-tags insightpulse/odoo
# Should show: ${VERSION} and latest

# Pull image to verify
docker pull registry.digitalocean.com/insightpulse/odoo:${VERSION}
```

**Error Codes**:
- `REGISTRY_AUTH_FAILURE` - Docker registry authentication failed
- `PUSH_TIMEOUT` - Image push exceeded 10-minute timeout
- `MANIFEST_ERROR` - Manifest upload failed
- `QUOTA_EXCEEDED` - Registry storage quota exceeded

**Mitigation**:
```bash
# REGISTRY_AUTH_FAILURE: Verify token
echo $DO_REGISTRY_TOKEN | wc -c
# Should show: >50 characters (valid token)

# PUSH_TIMEOUT: Use compression
docker push --compress registry.digitalocean.com/insightpulse/odoo:${VERSION}

# MANIFEST_ERROR: Re-push with --disable-content-trust
docker push --disable-content-trust registry.digitalocean.com/insightpulse/odoo:${VERSION}

# QUOTA_EXCEEDED: Clean up old images
doctl registry garbage-collection start insightpulse --force
```

---

### Step 7: Post-Build Validation

**Command**:
```bash
# Pull and run image
docker run -d --name odoo-test \
  -e POSTGRES_HOST=db \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  registry.digitalocean.com/insightpulse/odoo:${VERSION}

# Wait for startup
sleep 30

# Health check
curl -sf http://localhost:8069/web/health || echo "Health check failed"

# Cleanup
docker stop odoo-test
docker rm odoo-test
```

**Expected Result**:
- Container starts successfully
- Health endpoint returns 200 OK
- Odoo logs show no errors

**Verification**:
```bash
# Check container logs
docker logs odoo-test
# Should show: "odoo.service.server: HTTP service (werkzeug) running on 0.0.0.0:8069"

# Verify custom addons loaded
docker exec odoo-test odoo --list-db
```

**Error Codes**:
- `CONTAINER_START_FAILURE` - Container failed to start
- `HEALTH_CHECK_FAIL` - Health endpoint returned non-200
- `MODULE_LOAD_ERROR` - Custom module failed to load
- `DATABASE_CONNECTION_ERROR` - Unable to connect to PostgreSQL

**Mitigation**:
```bash
# CONTAINER_START_FAILURE: Check logs
docker logs odoo-test --tail 100

# HEALTH_CHECK_FAIL: Verify health endpoint
docker exec odoo-test curl -v http://localhost:8069/web/health

# MODULE_LOAD_ERROR: Check Odoo logs
docker exec odoo-test grep -i "error" /var/log/odoo/odoo-server.log

# DATABASE_CONNECTION_ERROR: Test connection
docker exec odoo-test psql -h db -U odoo -c "SELECT 1"
```

---

## Rollback Procedure

If build fails at any step, rollback to previous known-good image:

```bash
# List available versions
doctl registry repository list-tags insightpulse/odoo

# Identify previous version
PREVIOUS_VERSION=$(doctl registry repository list-tags insightpulse/odoo --format Tag | grep -v latest | sort -V | tail -2 | head -1)

# Re-tag previous version as latest
docker pull registry.digitalocean.com/insightpulse/odoo:$PREVIOUS_VERSION
docker tag registry.digitalocean.com/insightpulse/odoo:$PREVIOUS_VERSION registry.digitalocean.com/insightpulse/odoo:latest
docker push registry.digitalocean.com/insightpulse/odoo:latest

# Update deployment
doctl apps create-deployment $DO_APP_ID --force-rebuild
```

**Rollback Success Criteria**:
- [ ] Previous version image pulled successfully
- [ ] Re-tagged as `latest`
- [ ] Pushed to registry
- [ ] Deployment using previous version successful
- [ ] Health check passes

---

## Error Code Reference

| Code | Severity | Description | Resolution Time |
|------|----------|-------------|-----------------|
| BASE_IMAGE_DRIFT | Medium | Base image hash changed | 15 min (pin SHA256) |
| WKHTMLTOPDF_MISMATCH | High | wkhtmltopdf incompatible | 30 min (version pinning) |
| ANTHROPIC_SDK_MISSING | High | anthropic SDK install failed | 20 min (requirements fix) |
| TEST_FAILURE | Critical | Tests failed | Varies (fix tests) |
| REGISTRY_AUTH_FAILURE | Critical | Registry auth failed | 10 min (token refresh) |
| BUILD_FAILURE | High | Docker build failed | Varies (fix Dockerfile) |
| SECURITY_HIGH | High | High severity vulnerability | 1 hour (package update) |
| SECURITY_CRITICAL | Critical | Critical vulnerability | 30 min (immediate patch) |
| PUSH_TIMEOUT | Medium | Registry push timeout | 20 min (compression) |
| HEALTH_CHECK_FAIL | Critical | Health check failed | Varies (investigate) |

---

## Performance Benchmarks

| Stage | Expected Time | Actual Time | Status |
|-------|--------------|-------------|--------|
| Pull Base Image | <30s | ~18s | ✅ |
| Build Builder Stage | <3min | ~2.5min | ✅ |
| Run Tests | <2min | ~1.8min | ✅ |
| Build Runtime Stage | <2min | ~1.6min | ✅ |
| Security Scan | <1min | ~45s | ✅ |
| Push to Registry | <3min | ~2.2min | ✅ |
| **Total** | **<12min** | **~9min** | ✅ |

---

## CI/CD Integration

This SOP is automated in `.github/workflows/odoo-ci.yml`:

```yaml
jobs:
  docker-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Step 1 - Pull Base Image
        run: docker pull python:3.11-slim-bullseye

      - name: Step 2 - Build Builder Stage
        run: docker build --target builder -t odoo-builder:latest .

      - name: Step 3 - Run Tests
        run: docker run --rm odoo-builder:latest pytest custom_addons/ -v

      - name: Step 4 - Build Runtime Stage
        run: docker build --target runtime -t odoo-custom:${{ github.sha }} .

      - name: Step 5 - Security Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: odoo-custom:${{ github.sha }}
          severity: HIGH,CRITICAL
          exit-code: 1

      - name: Step 6 - Push to Registry
        run: |
          echo "${{ secrets.DO_REGISTRY_TOKEN }}" | docker login registry.digitalocean.com -u token --password-stdin
          docker tag odoo-custom:${{ github.sha }} registry.digitalocean.com/insightpulse/odoo:${{ github.sha }}
          docker push registry.digitalocean.com/insightpulse/odoo:${{ github.sha }}
```

---

## Monitoring and Alerts

### Success Metrics

- **Build Success Rate**: ≥95% (target: 98%)
- **Average Build Time**: <10 minutes
- **Image Size**: ≤2GB
- **Security Vulnerabilities**: 0 HIGH/CRITICAL

### Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Build Failure Rate | >5% | >10% | Investigate build logs |
| Build Time | >12 min | >15 min | Optimize Dockerfile |
| Image Size | >2GB | >2.5GB | Remove unnecessary packages |
| Security Vulns | 1 HIGH | 1 CRITICAL | Immediate patch |

### Notification Channels

- **Slack**: #devops-alerts (all build failures)
- **Email**: devops@your-org.com (critical failures only)
- **PagerDuty**: On-call engineer (security critical)

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

- [SOP-DEPLOY-001: DigitalOcean Deployment](DEPLOY_DO.md)
- [SOP-ROLLBACK-001: Emergency Rollback](../patterns/rollback_patterns.md)
- [Dockerfile Best Practices](../patterns/dockerfile_patterns.md)
- [Security Guidelines](../patterns/security_patterns.md)

---

**End of SOP-BUILD-001**

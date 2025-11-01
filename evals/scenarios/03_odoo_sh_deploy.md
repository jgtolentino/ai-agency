# Eval Scenario 03: Odoo.sh Deployment Workflow Validation

**Skill**: odoo-sh-devops
**Complexity**: High
**Estimated Time**: 6-8 minutes

---

## Objective

Validate Odoo.sh deployment lifecycle documentation:
- Git push → staging deployment workflow
- Staging validation gates and health checks
- Production promotion with zero-downtime strategy
- Rollback procedure with deployment history
- Self-hosted Docker parity runbook
- Log accessibility and monitoring integration

---

## Scenario

**Task**: "Create complete Odoo.sh deployment runbook for promoting custom module 'expense_approval' from development → staging → production with:
- Pre-deployment checklist (tests, migrations, security review)
- Staging validation gates (health checks, smoke tests, visual parity)
- Production deployment procedure with zero-downtime strategy
- Rollback plan using Odoo.sh deployment history
- Self-hosted Docker equivalent workflow
- Log monitoring and alerting setup"

---

## Pass Criteria

### Deployment Runbook Structure
```
knowledge/playbooks/odoo-sh/deploy_expense_approval.md

Required sections:
1. Pre-Deployment Checklist
2. Development → Staging Workflow
3. Staging Validation Gates
4. Production Deployment Procedure
5. Rollback Plan
6. Log Monitoring Setup
7. Incident Response Playbook
```

### Pre-Deployment Checklist
```markdown
## Pre-Deployment Checklist

### Code Quality
- [ ] All tests passing (pytest-odoo ≥95% coverage)
- [ ] Pre-commit hooks pass (black, isort, flake8, pylint-odoo)
- [ ] No hardcoded secrets (secrets scan passed)
- [ ] Security review completed (no high/critical vulnerabilities)

### Database Migrations
- [ ] Migration scripts tested in staging clone
- [ ] Pre-migration backup created
- [ ] Post-migration validation queries prepared
- [ ] Rollback migration script ready

### Dependencies
- [ ] requirements.txt updated with pinned versions
- [ ] OCA dependencies available in repository
- [ ] No breaking changes in dependency upgrades

### Documentation
- [ ] CHANGELOG.md updated with release notes
- [ ] README.md reflects new features
- [ ] User documentation updated (if applicable)

### Visual Parity
- [ ] Screenshots captured for affected routes
- [ ] SSIM thresholds met (mobile ≥0.97, desktop ≥0.98)
- [ ] Cross-browser testing completed (Chrome, Firefox, Safari)
```

### Staging Deployment Workflow
```bash
# Step 1: Commit and push to development branch
git checkout development
git add custom_addons/expense_approval/
git commit -m "feat(expense_approval): add approval workflow v1.0.0"
git push origin development

# Step 2: Odoo.sh auto-builds development branch
# Wait for build completion (check Odoo.sh dashboard)
# URL: https://expense-approval-development.odoo.com

# Step 3: Manual smoke testing on development
curl -sf https://expense-approval-development.odoo.com/web/database/selector
# Verify: Returns 200 OK

# Login and navigate to Expense Approval module
# Verify: Module appears in Apps list
# Verify: Can create test expense approval request

# Step 4: Promote to staging
git checkout staging
git merge development --no-ff
git push origin staging

# Odoo.sh builds staging environment
# URL: https://expense-approval-staging.odoo.com
```

### Staging Validation Gates
```bash
#!/bin/bash
# staging_validation.sh - Execute all validation gates

set -e

STAGING_URL="https://expense-approval-staging.odoo.com"

echo "🔍 Staging Validation Gates"

# Gate 1: Health check
echo "1️⃣  Health Check"
curl -sf "$STAGING_URL/web/health" | grep -q "pass" || {
    echo "❌ Health check failed"
    exit 1
}
echo "✓ Health: OK"

# Gate 2: Database connectivity
echo "2️⃣  Database Connectivity"
psql "$STAGING_DB_URL" -c "SELECT 1" > /dev/null || {
    echo "❌ Database connection failed"
    exit 1
}
echo "✓ Database: Connected"

# Gate 3: Module installation status
echo "3️⃣  Module Status"
RESPONSE=$(curl -sf "$STAGING_URL/web/session/authenticate" \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"call","params":{"db":"staging","login":"admin","password":"$ADMIN_PASSWORD"}}')

SESSION_ID=$(echo "$RESPONSE" | jq -r '.result.session_id')

curl -sf "$STAGING_URL/web/dataset/call_kw/ir.module.module/search_read" \
    -H "Cookie: session_id=$SESSION_ID" \
    -H "Content-Type: application/json" \
    -d '{
        "jsonrpc":"2.0",
        "method":"call",
        "params":{
            "model":"ir.module.module",
            "method":"search_read",
            "args":[[["name","=","expense_approval"]]],
            "kwargs":{"fields":["state"]}
        }
    }' | grep -q '"state":"installed"' || {
    echo "❌ Module not installed"
    exit 1
}
echo "✓ Module: Installed"

# Gate 4: Smoke tests (basic CRUD)
echo "4️⃣  Smoke Tests"
# Create test expense approval
RESPONSE=$(curl -sf "$STAGING_URL/web/dataset/call_kw/expense.approval.request/create" \
    -H "Cookie: session_id=$SESSION_ID" \
    -H "Content-Type: application/json" \
    -d '{
        "jsonrpc":"2.0",
        "method":"call",
        "params":{
            "model":"expense.approval.request",
            "method":"create",
            "args":[{
                "name":"Test Expense",
                "amount":100.00,
                "state":"draft"
            }]
        }
    }')

RECORD_ID=$(echo "$RESPONSE" | jq -r '.result')

test "$RECORD_ID" != "null" || {
    echo "❌ Failed to create test record"
    exit 1
}
echo "✓ Smoke Test: CRUD working (record $RECORD_ID)"

# Cleanup test record
curl -sf "$STAGING_URL/web/dataset/call_kw/expense.approval.request/unlink" \
    -H "Cookie: session_id=$SESSION_ID" \
    -H "Content-Type: application/json" \
    -d "{
        \"jsonrpc\":\"2.0\",
        \"method\":\"call\",
        \"params\":{
            \"model\":\"expense.approval.request\",
            \"method\":\"unlink\",
            \"args\":[[${RECORD_ID}]]
        }
    }" > /dev/null

# Gate 5: Visual parity validation
echo "5️⃣  Visual Parity"
if [ -f "scripts/visual_parity_check.sh" ]; then
    bash scripts/visual_parity_check.sh --env staging || {
        echo "❌ Visual parity below thresholds"
        exit 1
    }
    echo "✓ Visual Parity: PASS (SSIM ≥ thresholds)"
else
    echo "⚠️  Visual parity script not found (manual validation required)"
fi

# Gate 6: Performance baseline
echo "6️⃣  Performance Check"
RESPONSE_TIME=$(curl -w "%{time_total}" -o /dev/null -sf "$STAGING_URL/web/login")
THRESHOLD=2.0  # 2 seconds max

if (( $(echo "$RESPONSE_TIME < $THRESHOLD" | bc -l) )); then
    echo "✓ Performance: ${RESPONSE_TIME}s (< ${THRESHOLD}s)"
else
    echo "⚠️  Performance: ${RESPONSE_TIME}s (review if acceptable)"
fi

echo "✅ All validation gates passed"
```

### Production Deployment Procedure
```markdown
## Production Deployment

### Zero-Downtime Strategy

**Approach**: Blue-Green Deployment via Odoo.sh

#### Step 1: Pre-deployment Backup
```bash
# Trigger Odoo.sh backup before production merge
# Dashboard: Backups → Create Manual Backup
# Label: "pre-deploy-expense-approval-v1.0.0"
# Wait for backup completion (~5-15 minutes)
```

#### Step 2: Production Merge
```bash
# Merge staging to production branch
git checkout production
git merge staging --no-ff -m "release: expense_approval v1.0.0"
git push origin production

# Odoo.sh begins production build
# URL: https://expense-approval.odoo.com
```

#### Step 3: Build Monitoring
- Monitor Odoo.sh dashboard for build status
- Check build logs for errors/warnings
- Expected build time: 10-20 minutes (includes migration)

#### Step 4: Post-Deployment Validation
```bash
# Same validation gates as staging
bash staging_validation.sh --env production

# Additional production checks:
# - User acceptance testing (UAT) with stakeholders
# - Load testing (if high-traffic deployment)
# - Third-party integration checks (if applicable)
```

#### Step 5: Traffic Cutover
- Odoo.sh automatically switches traffic to new build
- Zero downtime (seamless transition)
- Old version remains available for rollback

#### Step 6: Monitoring Window
- Monitor for 2 hours post-deployment
- Watch error rates, response times, user reports
- Ready to rollback if critical issues detected
```

### Rollback Plan
```markdown
## Rollback Procedure

### Trigger Conditions
- Critical bugs affecting core functionality
- Database migration failures
- Performance degradation >50% from baseline
- Security vulnerabilities discovered
- User-facing errors affecting >10% of users

### Rollback Steps

#### Method 1: Odoo.sh Deployment History (Fastest)
```bash
# Via Odoo.sh Dashboard:
# 1. Navigate to Production branch
# 2. Deployments → History
# 3. Select previous stable deployment
# 4. Click "Restore" → Confirm

# Downtime: ~2-5 minutes (container restart)
# Data preservation: Last backup point (may lose recent data)
```

#### Method 2: Git Revert (Clean History)
```bash
# Identify commit to revert
git log production --oneline -n 5

# Revert the problematic merge
git checkout production
git revert -m 1 HEAD  # Revert merge commit
git push origin production

# Odoo.sh rebuilds production with reverted code
# Downtime: ~10-20 minutes (full rebuild)
# Data preservation: Database remains intact
```

#### Method 3: Database Restore (Nuclear Option)
```bash
# Use pre-deployment backup
# Via Odoo.sh Dashboard:
# 1. Backups → Select "pre-deploy-expense-approval-v1.0.0"
# 2. Restore → Confirm
# 3. Wait for restoration (~15-30 minutes)

# WARNING: Loses all data changes since backup
# Use only for catastrophic failures
```

### Post-Rollback Validation
- Run staging validation gates on production
- Notify users of rollback and ETA for fix
- Document rollback reason and learnings
```

### Log Monitoring Setup
```markdown
## Log Monitoring and Alerting

### Access Production Logs

#### Via Odoo.sh Dashboard
- Navigate to Production branch
- Logs tab → Select log type:
  - Application logs (Odoo server logs)
  - Database logs (PostgreSQL queries)
  - Web server logs (nginx access/error)

#### Via CLI (if SSH access enabled)
```bash
# Application logs
tail -f /var/log/odoo/odoo-server.log

# Filter for errors
grep "ERROR\|CRITICAL" /var/log/odoo/odoo-server.log | tail -n 50

# Database logs
tail -f /var/log/postgresql/postgresql-*.log
```

### Key Metrics to Monitor

**Application Metrics**:
- Error rate (target: <0.1% of requests)
- Response time P95 (target: <2s)
- Active users (compare to baseline)
- Database query count (watch for N+1 issues)

**Infrastructure Metrics**:
- CPU usage (alert if >80% sustained)
- Memory usage (alert if >85%)
- Disk space (alert if <20% free)
- Database connections (alert if >80% of pool)

### Alerting Configuration

**Critical Alerts** (Immediate response):
- Application crashes or restarts
- Database connection failures
- Error rate >1% for >5 minutes
- Response time P95 >5s for >5 minutes

**Warning Alerts** (Review within 1 hour):
- Error rate >0.5% for >10 minutes
- Response time P95 >3s for >10 minutes
- CPU/Memory >80% for >15 minutes
- Disk space <30%

### Integration with External Monitoring
```yaml
# Sentry (Error Tracking)
SENTRY_DSN: ${SENTRY_DSN}
SENTRY_ENVIRONMENT: production

# Prometheus (Metrics)
PROMETHEUS_MULTIPROC_DIR: /tmp/prometheus_multiproc_dir

# Grafana (Dashboards)
# Dashboard URL: https://grafana.example.com/d/odoo-production
```
```

### Self-Hosted Docker Parity
```markdown
## Self-Hosted Equivalent

### Docker Compose Blue-Green Deployment

#### Architecture
```yaml
# docker-compose.yml
version: '3.8'

services:
  odoo-blue:
    image: odoo-custom:1.0.0
    container_name: odoo-blue
    depends_on: [db]
    volumes:
      - odoo-data-blue:/var/lib/odoo
    networks: [odoo-net]
    labels:
      - "com.deployment.slot=blue"

  odoo-green:
    image: odoo-custom:1.1.0
    container_name: odoo-green
    depends_on: [db]
    volumes:
      - odoo-data-green:/var/lib/odoo
    networks: [odoo-net]
    labels:
      - "com.deployment.slot=green"

  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on: [odoo-blue, odoo-green]
    networks: [odoo-net]

  db:
    image: postgres:15
    volumes: [db-data:/var/lib/postgresql/data]
    networks: [odoo-net]

networks:
  odoo-net:

volumes:
  odoo-data-blue:
  odoo-data-green:
  db-data:
```

#### Deployment Script
```bash
#!/bin/bash
# deploy_blue_green.sh

CURRENT_SLOT=$(docker ps --filter "label=com.deployment.slot" \
    --filter "status=running" \
    --format "{{.Label \"com.deployment.slot\"}}" | head -n1)

if [ "$CURRENT_SLOT" = "blue" ]; then
    NEW_SLOT="green"
    OLD_SLOT="blue"
else
    NEW_SLOT="blue"
    OLD_SLOT="green"
fi

echo "Current slot: $OLD_SLOT"
echo "Deploying to: $NEW_SLOT"

# Step 1: Start new slot
docker-compose up -d odoo-$NEW_SLOT

# Step 2: Health check
for i in {1..30}; do
    if curl -sf http://localhost:8069/web/health > /dev/null; then
        echo "Health check passed"
        break
    fi
    sleep 2
done

# Step 3: Switch nginx upstream
sed -i "s/odoo-$OLD_SLOT/odoo-$NEW_SLOT/" nginx.conf
docker-compose exec nginx nginx -s reload

# Step 4: Wait for traffic to drain from old slot
sleep 30

# Step 5: Stop old slot
docker-compose stop odoo-$OLD_SLOT

echo "Deployment complete: $NEW_SLOT is now active"
```

#### Rollback
```bash
# Simply reverse the nginx upstream
sed -i "s/odoo-$NEW_SLOT/odoo-$OLD_SLOT/" nginx.conf
docker-compose exec nginx nginx -s reload
docker-compose start odoo-$OLD_SLOT
```
```

---

## Execution Script

```bash
#!/bin/bash
set -e

RUNBOOK_DIR="knowledge/playbooks/odoo-sh"
RUNBOOK="$RUNBOOK_DIR/deploy_expense_approval.md"

echo "📋 Validating Odoo.sh deployment runbook..."

# Structure check
test -d "$RUNBOOK_DIR" || {
    echo "❌ Runbooks directory missing"
    exit 1
}

test -f "$RUNBOOK" || {
    echo "❌ Deployment runbook not found: $RUNBOOK"
    exit 1
}

echo "✓ Runbook exists"

# Required sections validation
REQUIRED_SECTIONS=(
    "Pre-Deployment Checklist"
    "Staging Validation Gates"
    "Production Deployment"
    "Zero-Downtime"
    "Rollback Plan"
    "Log Monitoring"
    "Self-Hosted"
)

for SECTION in "${REQUIRED_SECTIONS[@]}"; do
    grep -qi "$SECTION" "$RUNBOOK" || {
        echo "❌ Missing required section: $SECTION"
        exit 1
    }
done

echo "✓ All required sections present"

# Validate checklist format
if grep -E "^\s*-\s*\[[ x]\]" "$RUNBOOK" > /dev/null; then
    echo "✓ Checklist items found"
else
    echo "❌ No checklist items (use - [ ] format)"
    exit 1
fi

# Validate staging validation gates
REQUIRED_GATES=(
    "Health"
    "Database"
    "Module"
    "Smoke"
    "Visual Parity"
)

for GATE in "${REQUIRED_GATES[@]}"; do
    grep -qi "$GATE" "$RUNBOOK" || {
        echo "❌ Missing validation gate: $GATE"
        exit 1
    }
done

echo "✓ All validation gates documented"

# Validate rollback procedures
ROLLBACK_METHODS=(
    "Deployment History"
    "Git Revert"
    "Database Restore"
)

for METHOD in "${ROLLBACK_METHODS[@]}"; do
    grep -qi "$METHOD" "$RUNBOOK" || {
        echo "❌ Missing rollback method: $METHOD"
        exit 1
    }
done

echo "✓ Multiple rollback methods documented"

# Validate monitoring setup
MONITORING_ELEMENTS=(
    "Error rate"
    "Response time"
    "CPU"
    "Memory"
    "Alert"
)

for ELEMENT in "${MONITORING_ELEMENTS[@]}"; do
    grep -qi "$ELEMENT" "$RUNBOOK" || {
        echo "❌ Missing monitoring element: $ELEMENT"
        exit 1
    }
done

echo "✓ Monitoring and alerting setup documented"

# Validate self-hosted parity
if grep -qi "docker\|blue-green\|nginx" "$RUNBOOK"; then
    echo "✓ Self-hosted Docker equivalent documented"
else
    echo "❌ Missing self-hosted parity documentation"
    exit 1
fi

# Check for hardcoded secrets
if grep -E "password.*=|api.key.*=|token.*=" "$RUNBOOK" | grep -v "\${" | grep -v "<" | grep -v "example" > /dev/null; then
    echo "❌ Potential hardcoded secrets found"
    exit 1
fi

echo "✓ No hardcoded secrets"

# Validate zero-downtime strategy
if grep -qi "zero.downtime\|blue.green\|seamless" "$RUNBOOK"; then
    echo "✓ Zero-downtime strategy documented"
else
    echo "⚠️  Zero-downtime strategy unclear"
fi

echo "✅ Eval 03: PASS - Odoo.sh deployment validation complete"
```

---

## Expected Output

```
📋 Validating Odoo.sh deployment runbook...
✓ Runbook exists
✓ All required sections present
✓ Checklist items found
✓ All validation gates documented
✓ Multiple rollback methods documented
✓ Monitoring and alerting setup documented
✓ Self-hosted Docker equivalent documented
✓ No hardcoded secrets
✓ Zero-downtime strategy documented

✅ Eval 03: PASS - Odoo.sh deployment validation complete
```

---

## Failure Modes

### Common Failures
1. **Incomplete checklist**: Missing critical validation steps
2. **No validation gates**: Undefined staging acceptance criteria
3. **Single rollback method**: Only one recovery option documented
4. **Missing monitoring**: No alerting or log access instructions
5. **No self-hosted parity**: No Docker equivalent workflow
6. **Hardcoded credentials**: Secrets in deployment commands

### Remediation Steps

**Incomplete Pre-Deployment Checklist**:
```markdown
# Ensure checklist covers:
- [ ] Code quality (tests, linting, security scan)
- [ ] Database migrations tested
- [ ] Dependencies validated
- [ ] Documentation updated
- [ ] Visual parity validated
- [ ] Rollback plan prepared
```

**Missing Validation Gates**:
```bash
# Required gates:
1. Health check (API endpoint responds)
2. Database connectivity (can query database)
3. Module installation (module state = 'installed')
4. Smoke tests (basic CRUD operations work)
5. Visual parity (SSIM thresholds met)
6. Performance baseline (response time acceptable)
```

**Insufficient Rollback Options**:
```markdown
# Document all three methods:
1. Deployment history restore (fastest, 2-5 min)
2. Git revert + rebuild (clean, 10-20 min)
3. Database backup restore (nuclear, 15-30 min)

# Include trigger conditions for each method
```

**Inadequate Monitoring**:
```markdown
# Required monitoring documentation:
- Log access (dashboard + CLI)
- Key metrics (error rate, response time, resources)
- Alert thresholds (critical vs warning)
- Integration with external tools (Sentry, Prometheus)
```

---

## Integration with CI/CD

```yaml
# .github/workflows/staging_deployment.yml
name: Staging Deployment
on:
  push:
    branches: [staging]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Pre-deployment checks
        run: |
          # Run tests
          pytest --cov=custom_addons --cov-report=term-missing

          # Security scan
          bash evals/scenarios/10_secrets_compliance.sh

          # Visual parity
          bash scripts/visual_parity_check.sh --env staging

      - name: Trigger Odoo.sh build
        run: |
          git push odoo-sh staging:staging
          # Odoo.sh webhook triggers build

      - name: Wait for build
        run: |
          # Poll Odoo.sh API for build completion
          # (requires Odoo.sh API credentials)

      - name: Run validation gates
        run: |
          bash knowledge/playbooks/odoo-sh/staging_validation.sh

      - name: Notify on failure
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          payload: |
            {
              "text": "❌ Staging deployment failed",
              "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": "Staging validation gates failed. Review logs."}}]
            }
```

---

## Reference

- **Odoo.sh Documentation**: https://www.odoo.com/documentation/17.0/administration/odoo_sh.html
- **Blue-Green Deployment**: https://martinfowler.com/bliki/BlueGreenDeployment.html
- **Zero-Downtime Deployment**: https://www.nginx.com/blog/zero-downtime-deployment/
- **Docker Compose**: https://docs.docker.com/compose/
- **Runbook Template**: knowledge/playbooks/odoo-sh/template_deployment_runbook.md

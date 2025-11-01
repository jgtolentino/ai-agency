# SOP-TRIAGE-001: Error Investigation Workflow

**Version**: 1.0.0
**Last Updated**: 2025-11-01
**Owner**: DevOps Team
**Classification**: Incident Response

## Purpose

Systematic error investigation and root cause analysis for deployment failures, application errors, and system incidents with integration to qms_sop module for tracking.

## Scope

- Error classification and severity assessment
- Root cause analysis methodology
- Investigation procedures by error type
- Resolution tracking and documentation
- Post-mortem analysis

## Triggers

- **Automated**: Deployment failure, health check failure, automated alerts
- **Manual**: User-reported errors, suspicious metrics, performance degradation
- **Scheduled**: Weekly review of warning-level errors

## Prerequisites

### Required Access

- [ ] Application logs access (DigitalOcean, Odoo)
- [ ] Database access (PostgreSQL via psql)
- [ ] Monitoring dashboards (if available)
- [ ] Odoo qms_sop module access for tracking
- [ ] GitHub repository access for incident issues

### Required Tools

- [ ] `doctl` CLI for DigitalOcean logs
- [ ] `psql` for database queries
- [ ] `grep`, `awk`, `jq` for log analysis
- [ ] Python for data analysis scripts

---

## Procedure

### Step 1: Error Classification

**Objective**: Categorize error by type and severity

**Decision Tree**:

```
Error Detected
    ↓
Is it deployment-related?
    YES → Category: DEPLOYMENT
    NO  ↓
Is it database-related?
    YES → Category: DATABASE
    NO  ↓
Is it application code-related?
    YES → Category: APPLICATION
    NO  ↓
Is it infrastructure-related?
    YES → Category: INFRASTRUCTURE
    NO  → Category: UNKNOWN
```

**Severity Assessment**:

| Severity | Criteria | Response Time | Escalation |
|----------|----------|---------------|------------|
| **CRITICAL** | Production down, data loss, security breach | <15 min | Immediate (PagerDuty) |
| **HIGH** | Feature broken, major performance degradation | <1 hour | Within 30 min |
| **MEDIUM** | Minor feature issue, slow performance | <4 hours | Business hours |
| **LOW** | Cosmetic issue, no user impact | <1 week | Next sprint |

**Classification Command**:
```bash
# Create SOP run in qms_sop module
python scripts/create_sop_run.py \
  --sop-code "SOP-TRIAGE-001" \
  --error-code "$ERROR_CODE" \
  --severity "$SEVERITY"

# Returns: RUN_ID for tracking
```

**Expected Result**:
- Error categorized by type
- Severity assigned
- SOP run created in Odoo
- Investigation timeline established

**Verification**:
```bash
# Verify SOP run created
curl -sf "https://odoo.your-domain.com/api/v1/sop-runs/${RUN_ID}" | jq .state
# Should return: "in_progress"
```

---

### Step 2: Gather Evidence

**Objective**: Collect all relevant logs, metrics, and state information

**Evidence Collection Matrix**:

| Error Category | Evidence Sources | Commands |
|----------------|------------------|----------|
| DEPLOYMENT | GitHub Actions logs, doctl deployment logs, Docker build logs | `gh run view`, `doctl apps logs` |
| DATABASE | PostgreSQL logs, query logs, connection stats | `psql -c "SELECT ..."`, database logs |
| APPLICATION | Odoo logs, Python tracebacks, browser console | `doctl apps logs --type RUN` |
| INFRASTRUCTURE | DigitalOcean metrics, resource usage, network logs | `doctl apps get`, monitoring dashboards |

**Deployment Error Evidence**:
```bash
# Get deployment logs
doctl apps logs $DO_APP_ID --type DEPLOY --tail 500 > deployment.log

# Get build logs
doctl apps logs $DO_APP_ID --type BUILD --tail 500 > build.log

# Get GitHub Actions logs
gh run view $RUN_ID --log > github-actions.log

# Analyze logs for error patterns
grep -E "(ERROR|FATAL|Exception)" deployment.log build.log github-actions.log
```

**Database Error Evidence**:
```bash
# Get database connection stats
psql "$POSTGRES_URL" -c "
  SELECT
    datname,
    numbackends,
    xact_commit,
    xact_rollback,
    deadlocks,
    temp_bytes
  FROM pg_stat_database
  WHERE datname = 'odoo';
"

# Get slow queries
psql "$POSTGRES_URL" -c "
  SELECT
    query,
    calls,
    total_time,
    mean_time
  FROM pg_stat_statements
  WHERE mean_time > 1000  -- queries >1 second
  ORDER BY mean_time DESC
  LIMIT 10;
"

# Check table bloat
psql "$POSTGRES_URL" -c "
  SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
  FROM pg_tables
  WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
  ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
  LIMIT 10;
"
```

**Application Error Evidence**:
```bash
# Get application logs
doctl apps logs $DO_APP_ID --type RUN --tail 1000 > application.log

# Extract Python tracebacks
awk '/Traceback/,/^[^ ]/' application.log > tracebacks.txt

# Analyze error frequency
grep "ERROR" application.log | awk -F: '{print $NF}' | sort | uniq -c | sort -rn > error-frequency.txt

# Get error context (10 lines before and after)
grep -B 10 -A 10 "$ERROR_MESSAGE" application.log > error-context.txt
```

**Infrastructure Error Evidence**:
```bash
# Get app resource usage
doctl apps get $DO_APP_ID --format Spec.Services[0].InstanceCount,Spec.Services[0].InstanceSizeSlug

# Get app metrics (if available via API)
# Note: DigitalOcean App Platform metrics require API calls
curl -X GET "https://api.digitalocean.com/v2/apps/$DO_APP_ID/metrics" \
  -H "Authorization: Bearer $DO_ACCESS_TOKEN"

# Get recent deployments
doctl apps list-deployments $DO_APP_ID --format ID,Phase,CreatedAt | head -10
```

**Expected Result**:
- All relevant logs collected
- Error patterns identified
- Contextual information gathered
- Evidence stored for analysis

---

### Step 3: Root Cause Analysis

**Objective**: Identify the underlying cause of the error

**RCA Methodology** (5 Whys):

```
Example: Deployment Health Check Failed

Why 1: Why did health check fail?
  → Health endpoint returned 500 error

Why 2: Why did health endpoint return 500?
  → Database connection timed out

Why 3: Why did database connection timeout?
  → Connection pool exhausted (max 20 connections)

Why 4: Why was connection pool exhausted?
  → Long-running queries not releasing connections

Why 5: Why are queries not releasing connections?
  → Missing connection cleanup in exception handlers

ROOT CAUSE: Exception handling code doesn't close database connections
```

**RCA Command**:
```bash
# Create RCA document
python scripts/create_rca.py \
  --run-id "$RUN_ID" \
  --error-code "$ERROR_CODE" \
  --root-cause "Exception handling doesn't close DB connections" \
  --contributing-factors "High traffic, inefficient queries"
```

**Common Root Causes by Category**:

**Deployment Errors**:
- Image pull failure → Registry authentication expired
- Build timeout → Inefficient Dockerfile, large dependencies
- Health check timeout → Slow database migrations
- Traffic switch failed → DNS propagation delay

**Database Errors**:
- Connection timeout → Connection pool exhaustion
- Query timeout → Missing indexes, inefficient queries
- Deadlock → Concurrent transactions on same rows
- Disk full → Database bloat, insufficient storage

**Application Errors**:
- ImportError → Missing dependency in requirements.txt
- AttributeError → API version mismatch
- KeyError → Missing configuration parameter
- MemoryError → Memory leak, insufficient resources

**Infrastructure Errors**:
- Out of memory → Insufficient instance size
- CPU throttling → Computationally expensive operations
- Network timeout → External service unreachable
- SSL certificate expired → Certificate renewal failed

---

### Step 4: Implement Fix

**Objective**: Apply corrective action to resolve the error

**Fix Implementation Matrix**:

| Root Cause | Fix Type | Implementation | Verification |
|------------|----------|----------------|--------------|
| Code bug | Code change | PR with fix + tests | CI passes, manual test |
| Configuration | Config update | Update app spec or env vars | Redeploy, verify config |
| Resource limit | Resource scaling | Increase instance size/count | Monitor metrics |
| Dependency issue | Dependency update | Update requirements.txt | Rebuild, test |

**Code Fix Example** (connection cleanup):
```python
# BEFORE (buggy code)
def fetch_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM large_table")
    data = cursor.fetchall()
    # Missing: cursor.close(), conn.close()
    return data

# AFTER (fixed code)
def fetch_data():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM large_table")
        data = cursor.fetchall()
        return data
    finally:
        if conn:
            cursor.close()
            conn.close()  # Always clean up
```

**Configuration Fix Example** (increase connection pool):
```yaml
# infra/do/app-spec.yaml
services:
  - name: odoo
    environment_variables:
      - key: DB_MAXCONN
        value: "50"  # Increased from 20
      - key: DB_POOL_TIMEOUT
        value: "30"  # Added timeout
```

**Resource Scaling Fix Example**:
```bash
# Update app spec with larger instance
sed -i 's/instance_size_slug: basic-xxs/instance_size_slug: basic-xs/' infra/do/app-spec.yaml

# Apply changes
doctl apps update $DO_APP_ID --spec infra/do/app-spec.yaml
doctl apps create-deployment $DO_APP_ID --force-rebuild
```

**Expected Result**:
- Fix implemented and tested
- Deployment successful
- Error no longer occurs
- Metrics show improvement

**Verification**:
```bash
# Test fix locally
pytest tests/test_connection_cleanup.py -v

# Deploy fix
gh workflow run deploy.yml -f environment=staging

# Verify fix in production
python scripts/health_check.py --url "https://${APP_URL}"

# Monitor for recurrence
doctl apps logs $DO_APP_ID --type RUN --follow | grep "$ERROR_MESSAGE"
# Should return: (no matches)
```

---

### Step 5: Document Resolution

**Objective**: Record resolution for future reference and prevent recurrence

**Documentation Requirements**:

1. **Update SOP Run** (qms_sop module):
   ```bash
   python scripts/update_sop_run.py \
     --run-id "$RUN_ID" \
     --state "completed" \
     --resolution "Implemented connection cleanup in exception handlers" \
     --resolution-time "$((END_TIME - START_TIME))"
   ```

2. **Create Incident Post-Mortem**:
   ```bash
   python scripts/create_postmortem.py \
     --incident-id "$INCIDENT_ID" \
     --title "Deployment health check timeout due to DB connection leak" \
     --root-cause "Missing connection cleanup in exception handlers" \
     --fix "Added finally blocks to ensure connection cleanup" \
     --preventive-measures "Added connection pool monitoring, automated alerts"
   ```

3. **Update Error Code Catalog** (qms_error_code):
   ```bash
   # Add new error code or update existing
   python scripts/update_error_code.py \
     --code "DB_CONNECTION_LEAK" \
     --severity "high" \
     --description "Database connections not released in exception handlers" \
     --resolution "Ensure all DB operations use try/finally blocks with connection cleanup"
   ```

4. **Create GitHub Issue** (if recurring pattern):
   ```bash
   gh issue create \
     --title "[TECH-DEBT] Audit all database operations for connection cleanup" \
     --body "**Context**: Deployment failed due to connection leak.

     **Root Cause**: Missing finally blocks in exception handlers.

     **Action Items**:
     - [ ] Audit all DB operations for cleanup
     - [ ] Add linting rule to enforce try/finally
     - [ ] Add integration test for connection pool limits

     **References**:
     - Incident: #$INCIDENT_ID
     - SOP Run: $RUN_ID
     - Post-Mortem: docs/postmortems/2025-11-01-db-connection-leak.md" \
     --label tech-debt,database,high-priority
   ```

**Expected Result**:
- SOP run marked complete
- Post-mortem document created
- Error code catalog updated
- Preventive measures identified

---

### Step 6: Preventive Measures

**Objective**: Prevent recurrence through systemic improvements

**Preventive Actions Matrix**:

| Error Type | Preventive Measure | Implementation |
|------------|-------------------|----------------|
| Code bugs | Automated tests | Add regression tests for root cause |
| Configuration | Config validation | Add CI check for app spec validity |
| Resource limits | Monitoring & alerts | Set up alerts for resource usage >80% |
| Dependencies | Automated updates | Enable Dependabot for security updates |

**Example Preventive Measures**:

1. **Add Regression Test**:
   ```python
   # tests/test_connection_cleanup.py
   def test_connection_cleanup_on_exception():
       """Ensure DB connections are closed even when exceptions occur."""
       initial_connections = get_connection_count()

       try:
           fetch_data_that_raises_exception()
       except Exception:
           pass  # Expected

       # Wait for cleanup
       time.sleep(1)

       final_connections = get_connection_count()
       assert final_connections == initial_connections, \
           "Connection leak detected: connections not cleaned up after exception"
   ```

2. **Add CI Validation**:
   ```yaml
   # .github/workflows/odoo-ci.yml
   - name: Validate App Spec
     run: |
       doctl apps propose infra/do/app-spec.yaml

       # Check for common misconfigurations
       grep -q "DB_MAXCONN" infra/do/app-spec.yaml || \
         (echo "Missing DB_MAXCONN config" && exit 1)
   ```

3. **Add Monitoring Alert**:
   ```bash
   # Configure alert (example with DO API or external monitoring)
   curl -X POST "https://api.monitoring.com/alerts" \
     -H "Authorization: Bearer $MONITORING_API_KEY" \
     -d '{
       "name": "Database Connection Pool Warning",
       "condition": "db_connections > 40",  // 80% of max 50
       "severity": "warning",
       "notification_channel": "slack-#devops-alerts"
     }'
   ```

4. **Enable Automated Updates**:
   ```yaml
   # .github/dependabot.yml
   version: 2
   updates:
     - package-ecosystem: "pip"
       directory: "/"
       schedule:
         interval: "weekly"
       labels:
         - "dependencies"
         - "security"
       open-pull-requests-limit: 10
   ```

**Expected Result**:
- Tests prevent regression
- CI catches misconfigurations
- Alerts provide early warning
- Dependencies stay current

---

## Error Code Reference

| Code | Category | Severity | Common Causes | Resolution |
|------|----------|----------|---------------|------------|
| BASE_IMAGE_DRIFT | DEPLOYMENT | Medium | Base image updated | Pin SHA256 |
| WKHTMLTOPDF_MISMATCH | DEPLOYMENT | High | Version incompatibility | Pin version |
| TEST_FAILURE | DEPLOYMENT | Critical | Code bug | Fix tests |
| REGISTRY_AUTH_FAILURE | DEPLOYMENT | Critical | Expired token | Refresh token |
| DB_CONNECTION_LEAK | DATABASE | High | Missing cleanup | Add finally blocks |
| DB_CONNECTION_TIMEOUT | DATABASE | Critical | Pool exhausted | Increase pool size |
| DB_SLOW_QUERY | DATABASE | Medium | Missing indexes | Add indexes |
| DB_DEADLOCK | DATABASE | High | Concurrent updates | Review locking |
| IMPORT_ERROR | APPLICATION | High | Missing dependency | Update requirements.txt |
| ATTRIBUTE_ERROR | APPLICATION | High | API version mismatch | Update code |
| MEMORY_ERROR | INFRASTRUCTURE | Critical | Insufficient memory | Scale up instance |
| CPU_THROTTLING | INFRASTRUCTURE | High | Heavy computation | Optimize code |

---

## Performance Benchmarks

| Stage | Expected Time | Target |
|-------|--------------|--------|
| Error Classification | <5 min | Automated |
| Evidence Gathering | <10 min | Comprehensive |
| Root Cause Analysis | <30 min | 5 Whys completed |
| Fix Implementation | Varies | Depends on complexity |
| Documentation | <15 min | All artifacts created |
| **Total** | **<1 hour** | **For HIGH severity** |

**Resolution SLA by Severity**:
- CRITICAL: <15 minutes to mitigation, <4 hours to root cause fix
- HIGH: <1 hour to mitigation, <1 day to root cause fix
- MEDIUM: <4 hours to mitigation, <1 week to root cause fix
- LOW: <1 week to acknowledgment, next sprint for fix

---

## Integration with qms_sop Module

**SOP Execution Tracking**:

```python
# Example: Create and track SOP run
from odoo import api, fields, models

# Create SOP run
sop = env['qms.sop.document'].search([('code', '=', 'SOP-TRIAGE-001')], limit=1)
run = env['qms.sop.run'].create({
    'sop_id': sop.id,
    'state': 'in_progress',
})

# Execute each step
for step in sop.step_ids:
    run_step = env['qms.sop.run.step'].create({
        'run_id': run.id,
        'step_id': step.id,
        'state': 'in_progress',
    })

    # Perform step actions
    try:
        result = execute_step(step)
        run_step.write({
            'state': 'completed',
            'actual_result': result,
        })
    except Exception as e:
        # Log error
        error_code = env['qms.error.code'].search([('name', '=', 'STEP_FAILURE')], limit=1)
        env['qms.sop.run.error'].create({
            'run_id': run.id,
            'step_id': run_step.id,
            'error_code_id': error_code.id,
            'error_message': str(e),
        })
        run_step.write({'state': 'failed'})
        break

# Complete run
run.write({
    'state': 'completed' if all(s.state == 'completed' for s in run.step_ids) else 'failed',
    'end_time': fields.Datetime.now(),
})
```

---

## Related Documentation

- [SOP-BUILD-001: Docker Image Build](BUILD_IMAGE.md)
- [SOP-DEPLOY-001: DigitalOcean Deployment](DEPLOY_DO.md)
- [Post-Mortem Template](../patterns/postmortem_template.md)
- [Error Code Catalog](../knowledge/error_codes.md)

---

**End of SOP-TRIAGE-001**

# Odoo.sh Deployment Runbook

Complete lifecycle management for Odoo.sh deployments with self-hosted Docker parity.

---

## Overview

Odoo.sh is a Platform-as-a-Service (PaaS) for Odoo hosting with:
- Git-based deployment workflow (push → build → deploy)
- Automatic environment provisioning (development, staging, production)
- Built-in database backups and log management
- Seamless Odoo version upgrades

This runbook covers:
1. Odoo.sh deployment workflows
2. Self-hosted Docker equivalents for all Odoo.sh features
3. Operational procedures (monitoring, backups, rollbacks)
4. Migration strategies (Odoo.sh ↔ self-hosted)

---

## Odoo.sh Deployment Workflow

### Branch-Based Environments

```
┌─────────────────┐
│ Development     │ ← feature/* branches
│ (dev)           │   Auto-deploy on push
└────────┬────────┘
         │ merge
         ▼
┌─────────────────┐
│ Staging         │ ← staging branch
│ (pre-prod)      │   Manual promotion from dev
└────────┬────────┘
         │ release
         ▼
┌─────────────────┐
│ Production      │ ← main/master branch
│ (live)          │   Manual promotion from staging
└─────────────────┘
```

### Git Push Deployment Triggers

#### Development Environment

```bash
# Create feature branch
git checkout -b feature/add-vendor-portal

# Develop feature
# ... make changes ...

# Commit and push
git add .
git commit -m "feat: add privacy-first vendor portal"
git push origin feature/add-vendor-portal

# Odoo.sh automatically:
# 1. Detects push to feature branch
# 2. Creates development environment
# 3. Builds Docker image
# 4. Provisions PostgreSQL database
# 5. Installs custom modules
# 6. Deploys to dev-<branch-name>.odoo.com
```

**Deployment Time**: 5-10 minutes (includes build + database initialization)

#### Staging Environment

```bash
# Merge to staging branch
git checkout staging
git merge feature/add-vendor-portal
git push origin staging

# Odoo.sh automatically:
# 1. Detects push to staging branch
# 2. Builds production-ready image
# 3. Updates staging database with migrations
# 4. Runs automated tests (if configured)
# 5. Deploys to staging-project.odoo.com
```

**Validation Steps**:
- [ ] Smoke tests pass
- [ ] Migration scripts run successfully
- [ ] No breaking changes detected
- [ ] Performance metrics within SLA

#### Production Deployment

```bash
# Promote staging to production (via Odoo.sh dashboard)
# OR merge to main branch:
git checkout main
git merge staging
git tag -a v1.2.0 -m "Release 1.2.0: Vendor portal"
git push origin main --follow-tags

# Odoo.sh requires manual confirmation:
# 1. Review changes diff
# 2. Confirm migration plan
# 3. Schedule deployment window
# 4. Execute deployment with automatic backup
```

**Deployment Checklist**:
- [ ] Staging validation complete
- [ ] Change log reviewed
- [ ] Rollback plan prepared
- [ ] Monitoring alerts configured
- [ ] Post-deployment tests ready

---

## Log Monitoring Commands

### Odoo.sh CLI

```bash
# Install Odoo.sh CLI
pip install odoo-cloud-platform

# Login
odoo-sh login

# List projects
odoo-sh projects

# List builds for project
odoo-sh builds --project=<project-name>

# View build logs (real-time)
odoo-sh logs --project=<project-name> --build=<build-id> --follow

# View application logs
odoo-sh logs --project=<project-name> --build=<build-id> --type=app

# View database logs
odoo-sh logs --project=<project-name> --build=<build-id> --type=db

# View web server logs
odoo-sh logs --project=<project-name> --build=<build-id> --type=web
```

### Web Dashboard

1. **Navigate to Odoo.sh Dashboard**: https://odoo.sh
2. **Select Project** → **Builds** → **[Branch Name]**
3. **Logs Tab**: Real-time log streaming
   - Filter by: ERROR, WARNING, INFO, DEBUG
   - Search: Full-text log search
   - Download: Export logs for analysis

### Log Analysis Patterns

```bash
# Error detection
odoo-sh logs --project=myproject --build=latest | grep -i "error\|exception"

# Performance issues
odoo-sh logs --project=myproject --build=latest | grep -i "slow query\|timeout"

# Security alerts
odoo-sh logs --project=myproject --build=latest | grep -i "unauthorized\|forbidden"

# Database deadlocks
odoo-sh logs --project=myproject --build=latest --type=db | grep -i "deadlock"
```

---

## Backup and Restore Procedures

### Automated Backups (Odoo.sh)

**Backup Schedule**:
- **Production**: Daily backups, retained for 30 days
- **Staging**: Weekly backups, retained for 7 days
- **Development**: On-demand backups only

**Backup Contents**:
- PostgreSQL database dump (pg_dump)
- Filestore (uploaded files, attachments)
- Configuration (odoo.conf, secrets)

### Manual Backup

```bash
# Create on-demand backup via CLI
odoo-sh backup create --project=myproject --build=production

# Download backup
odoo-sh backup download --project=myproject --backup-id=<backup-id> --output=backup.tar.gz

# Extract backup contents
tar -xzvf backup.tar.gz
# Contents:
# - database.sql (PostgreSQL dump)
# - filestore/ (uploaded files)
# - odoo.conf (configuration)
```

### Restore Procedure

#### Restore to Same Environment

```bash
# List available backups
odoo-sh backup list --project=myproject --build=production

# Restore from backup
odoo-sh restore --project=myproject --build=production --backup-id=<backup-id>

# Odoo.sh will:
# 1. Stop application
# 2. Drop current database
# 3. Restore database from backup
# 4. Restore filestore
# 5. Restart application
```

**Downtime**: 10-30 minutes (depending on database size)

#### Restore to Different Environment

```bash
# Copy production backup to staging
odoo-sh backup copy \
  --project=myproject \
  --source-build=production \
  --target-build=staging \
  --backup-id=<backup-id>

# Anonymize sensitive data (recommended)
# Manual step: Run anonymization script on staging database
```

### Self-Hosted Backup Equivalent

```bash
#!/bin/bash
# scripts/backup_odoo_docker.sh

set -e

BACKUP_DIR="/backups/odoo"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="odoo_backup_${TIMESTAMP}"

echo "Creating backup: $BACKUP_NAME"

# 1. Backup database
docker-compose exec -T db pg_dump -U odoo -Fc postgres > \
  "${BACKUP_DIR}/${BACKUP_NAME}_db.dump"

# 2. Backup filestore
docker cp odoo-app:/var/lib/odoo/filestore \
  "${BACKUP_DIR}/${BACKUP_NAME}_filestore"

# 3. Backup configuration
docker cp odoo-app:/opt/odoo/odoo.conf \
  "${BACKUP_DIR}/${BACKUP_NAME}_odoo.conf"

# 4. Create tarball
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" \
  "${BACKUP_DIR}/${BACKUP_NAME}_db.dump" \
  "${BACKUP_DIR}/${BACKUP_NAME}_filestore" \
  "${BACKUP_DIR}/${BACKUP_NAME}_odoo.conf"

# 5. Cleanup temporary files
rm -rf "${BACKUP_DIR}/${BACKUP_NAME}_db.dump" \
       "${BACKUP_DIR}/${BACKUP_NAME}_filestore" \
       "${BACKUP_DIR}/${BACKUP_NAME}_odoo.conf"

echo "Backup complete: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

# 6. Upload to remote storage (optional)
# aws s3 cp "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" s3://my-bucket/odoo-backups/
```

---

## Self-Hosted Parity Guide

Odoo.sh vs. Self-Hosted Docker feature comparison and implementation patterns.

### Feature Matrix

| Feature                  | Odoo.sh                    | Self-Hosted Docker          | Parity Status |
|--------------------------|----------------------------|-----------------------------|---------------|
| Git-based deployment     | ✅ Built-in                | ⚙️ CI/CD required           | 🟢 Full       |
| Auto-scaling             | ✅ Automatic               | ⚙️ K8s/Swarm required       | 🟡 Partial    |
| Database backups         | ✅ Automatic (30d)         | ⚙️ Cron + S3                | 🟢 Full       |
| Log aggregation          | ✅ Built-in                | ⚙️ ELK/Loki required        | 🟢 Full       |
| SSL certificates         | ✅ Let's Encrypt auto      | ⚙️ Traefik/Nginx required   | 🟢 Full       |
| Database replication     | ✅ Multi-AZ                | ⚙️ PostgreSQL streaming     | 🟡 Partial    |
| Rollback mechanism       | ✅ One-click               | ⚙️ CI/CD pipeline           | 🟢 Full       |
| Monitoring               | ✅ Built-in dashboards     | ⚙️ Prometheus/Grafana       | 🟢 Full       |
| Version upgrades         | ✅ Guided wizard           | ⚙️ Manual migration         | 🟡 Partial    |

### Git-Based Deployment (Parity: 🟢 Full)

**Odoo.sh Workflow**:
```bash
git push origin feature/new-module
# → Automatic build and deploy
```

**Self-Hosted Equivalent**:
```yaml
# .github/workflows/deploy.yml
name: Deploy Odoo

on:
  push:
    branches: [main, staging, 'feature/*']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: |
          docker build -t odoo:${{ github.sha }} .

      - name: Push to registry
        run: |
          docker tag odoo:${{ github.sha }} registry.example.com/odoo:${{ github.sha }}
          docker push registry.example.com/odoo:${{ github.sha }}

      - name: Deploy to environment
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            ENV="production"
          elif [[ "${{ github.ref }}" == "refs/heads/staging" ]]; then
            ENV="staging"
          else
            ENV="development"
          fi

          ssh deploy@$ENV-server.example.com \
            "docker-compose pull && docker-compose up -d"
```

### Database Backups (Parity: 🟢 Full)

**Odoo.sh**: Automatic daily backups, 30-day retention

**Self-Hosted Equivalent**:
```bash
# crontab entry
0 2 * * * /opt/odoo/scripts/backup_odoo_docker.sh

# Backup retention script
#!/bin/bash
# Keep last 30 days of backups
find /backups/odoo -name "odoo_backup_*.tar.gz" -mtime +30 -delete

# Upload to S3 for disaster recovery
aws s3 sync /backups/odoo s3://my-bucket/odoo-backups/ \
  --storage-class STANDARD_IA \
  --delete
```

### Log Aggregation (Parity: 🟢 Full)

**Odoo.sh**: Built-in log viewer with search and filtering

**Self-Hosted Equivalent (Loki + Grafana)**:
```yaml
# docker-compose.logs.yml
version: "3.9"

services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - loki-data:/loki

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log:ro
      - ./promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  loki-data:
  grafana-data:
```

**Query Examples**:
```logql
# Error logs from Odoo
{job="odoo"} |= "ERROR"

# Slow queries
{job="postgres"} |= "duration:" | logfmt | duration > 1000

# HTTP 500 errors
{job="odoo"} |~ "HTTP/1\\.1\" 500"
```

### Rollback Mechanism (Parity: 🟢 Full)

**Odoo.sh**: One-click rollback to previous build

**Self-Hosted Equivalent**:
```bash
#!/bin/bash
# scripts/rollback_odoo.sh

set -e

PREVIOUS_IMAGE=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep odoo | sed -n 2p)

echo "Rolling back to: $PREVIOUS_IMAGE"

# 1. Tag previous image as latest
docker tag "$PREVIOUS_IMAGE" odoo:latest

# 2. Update docker-compose to use previous image
sed -i "s|image:.*|image: $PREVIOUS_IMAGE|" docker-compose.yml

# 3. Restart services
docker-compose up -d

# 4. Verify deployment
sleep 10
curl -f http://localhost:8069/web/health || {
  echo "Rollback failed, health check failed"
  exit 1
}

echo "Rollback successful"
```

### Monitoring (Parity: 🟢 Full)

**Odoo.sh**: Built-in dashboards (CPU, memory, disk, requests)

**Self-Hosted Equivalent (Prometheus + Grafana)**:
```yaml
# docker-compose.monitoring.yml
version: "3.9"

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    environment:
      DATA_SOURCE_NAME: "postgresql://odoo:password@db:5432/postgres?sslmode=disable"

volumes:
  prometheus-data:
  grafana-data:
```

**Key Metrics**:
- HTTP request rate and latency
- Database connection pool usage
- PostgreSQL slow queries
- Memory and CPU utilization
- Disk I/O and storage usage

---

## Odoo Version Upgrade Procedures

### Odoo.sh Upgrade Process

**Supported Upgrade Paths**:
- 16.0 → 17.0 (major version)
- 17.0 → 19.0 (major version)
- 16.0 → 16.0 (patch updates, automatic)

**Upgrade Workflow**:

1. **Staging Upgrade** (Test Run)
   ```bash
   # Via Odoo.sh dashboard:
   # 1. Navigate to staging build
   # 2. Click "Upgrade" button
   # 3. Select target version (e.g., 17.0)
   # 4. Review migration plan
   # 5. Confirm upgrade

   # Odoo.sh will:
   # - Create database snapshot
   # - Run upgrade scripts
   # - Migrate custom modules
   # - Validate compatibility
   ```

   **Validation Steps**:
   - [ ] All modules load without errors
   - [ ] Critical workflows functional
   - [ ] Data integrity verified
   - [ ] Performance within SLA

2. **Production Upgrade** (After Staging Success)
   ```bash
   # Schedule maintenance window
   # Notify users of downtime

   # Via Odoo.sh dashboard:
   # 1. Navigate to production build
   # 2. Click "Upgrade" button
   # 3. Select target version
   # 4. Review migration summary
   # 5. Schedule upgrade time
   # 6. Confirm with automatic backup
   ```

**Downtime**: 30 minutes - 4 hours (depending on database size and customizations)

### Self-Hosted Upgrade Equivalent

```bash
#!/bin/bash
# scripts/upgrade_odoo.sh

set -e

FROM_VERSION="16.0"
TO_VERSION="17.0"
BACKUP_DIR="/backups/odoo"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "Upgrading Odoo from $FROM_VERSION to $TO_VERSION"

# 1. Create full backup
echo "Creating backup..."
bash scripts/backup_odoo_docker.sh

# 2. Stop services
echo "Stopping services..."
docker-compose down

# 3. Update Dockerfile with new version
sed -i "s/ARG ODOO_VERSION=.*/ARG ODOO_VERSION=$TO_VERSION/" Dockerfile

# 4. Rebuild image
echo "Building new image..."
docker build --build-arg ODOO_VERSION=$TO_VERSION -t odoo:$TO_VERSION .

# 5. Update docker-compose.yml
sed -i "s|image: odoo:.*|image: odoo:$TO_VERSION|" docker-compose.yml

# 6. Start database only
docker-compose up -d db
sleep 10

# 7. Run upgrade script
echo "Running upgrade..."
docker-compose run --rm odoo \
  python3 /opt/odoo/src/odoo-bin \
  -d postgres \
  -u all \
  --upgrade-path \
  --stop-after-init

# 8. Start full stack
docker-compose up -d

# 9. Verify upgrade
sleep 30
curl -f http://localhost:8069/web/health || {
  echo "Upgrade failed, rolling back..."
  bash scripts/rollback_odoo.sh
  exit 1
}

echo "Upgrade complete: Odoo $TO_VERSION"

# 10. Post-upgrade validation
docker-compose exec odoo odoo-bin shell -c "
import odoo
env = odoo.api.Environment(odoo.registry('postgres').cursor(), odoo.SUPERUSER_ID, {})
print('Installed modules:', env['ir.module.module'].search([('state', '=', 'installed')]).mapped('name'))
"
```

---

## Migration Strategies

### Odoo.sh to Self-Hosted

**Use Case**: Migrate from Odoo.sh to self-hosted Docker for cost optimization or custom infrastructure requirements.

**Migration Steps**:

1. **Export from Odoo.sh**
   ```bash
   # Create on-demand backup
   odoo-sh backup create --project=myproject --build=production

   # Download backup
   odoo-sh backup download --project=myproject \
     --backup-id=<backup-id> \
     --output=odoo_sh_backup.tar.gz

   # Extract contents
   tar -xzvf odoo_sh_backup.tar.gz
   ```

2. **Prepare Self-Hosted Environment**
   ```bash
   # Create docker-compose.yml
   cp knowledge/runbooks/docker_production.md docker-compose.yml

   # Configure environment variables
   cp .env.example .env
   # Edit .env with Odoo.sh secrets
   ```

3. **Import to Self-Hosted**
   ```bash
   # Start database only
   docker-compose up -d db
   sleep 10

   # Restore database
   docker cp database.sql odoo-db:/tmp/
   docker-compose exec db psql -U odoo -d postgres -f /tmp/database.sql

   # Restore filestore
   docker cp filestore/ odoo-app:/var/lib/odoo/filestore/

   # Start Odoo
   docker-compose up -d odoo
   ```

4. **Validation**
   - [ ] Database connection successful
   - [ ] All modules loaded
   - [ ] Filestore accessible
   - [ ] User login functional
   - [ ] Critical workflows tested

### Self-Hosted to Odoo.sh

**Use Case**: Migrate from self-hosted Docker to Odoo.sh for managed infrastructure and automatic scaling.

**Migration Steps**:

1. **Export from Self-Hosted**
   ```bash
   # Create backup
   bash scripts/backup_odoo_docker.sh

   # Extract database dump
   tar -xzvf odoo_backup_*.tar.gz
   ```

2. **Create Odoo.sh Project**
   - Sign up at https://odoo.sh
   - Create new project
   - Select Odoo version matching self-hosted

3. **Initialize Git Repository**
   ```bash
   # Initialize repo with custom modules
   git init
   git add custom_addons/
   git commit -m "Initial commit: custom modules"

   # Add Odoo.sh remote
   git remote add odoo-sh <odoo-sh-git-url>
   git push odoo-sh main
   ```

4. **Import Database**
   - Via Odoo.sh dashboard: Upload database dump
   - Via CLI: `odoo-sh db restore --project=myproject --file=database.sql`

5. **Import Filestore**
   - Upload to Odoo.sh storage
   - Sync via rsync or S3

**Post-Migration**:
- Configure DNS to point to Odoo.sh
- Update SSL certificates (automatic Let's Encrypt)
- Configure backups and monitoring

---

## Operational Runbooks

### Daily Operations

**Health Check**:
```bash
# Odoo.sh
odoo-sh logs --project=myproject --build=production --tail=100 | grep -i "error\|warning"

# Self-hosted
docker-compose logs --tail=100 odoo | grep -i "error\|warning"
curl -f http://localhost:8069/web/health
```

**Performance Monitoring**:
```bash
# Check database connections
docker-compose exec db psql -U odoo -c "SELECT count(*) FROM pg_stat_activity;"

# Check disk usage
docker-compose exec odoo df -h

# Check memory usage
docker stats --no-stream odoo-app
```

### Incident Response

**Database Connection Issues**:
```bash
# 1. Check database health
docker-compose exec db pg_isready -U odoo

# 2. Check connection pool
docker-compose exec db psql -U odoo -c "
  SELECT count(*) AS connections, state
  FROM pg_stat_activity
  GROUP BY state;
"

# 3. Kill idle connections (if needed)
docker-compose exec db psql -U odoo -c "
  SELECT pg_terminate_backend(pid)
  FROM pg_stat_activity
  WHERE state = 'idle' AND query_start < now() - interval '1 hour';
"

# 4. Restart Odoo (if needed)
docker-compose restart odoo
```

**High Memory Usage**:
```bash
# 1. Identify process
docker stats --no-stream

# 2. Check Odoo workers
docker-compose exec odoo ps aux | grep odoo-bin

# 3. Adjust worker limits (odoo.conf)
# workers = 4
# limit_memory_hard = 2684354560  # 2.5 GB
# limit_memory_soft = 2147483648  # 2 GB

# 4. Restart with new limits
docker-compose restart odoo
```

**Slow Performance**:
```bash
# 1. Enable slow query logging
docker-compose exec db psql -U odoo -c "
  ALTER SYSTEM SET log_min_duration_statement = '1000';  -- 1 second
  SELECT pg_reload_conf();
"

# 2. Analyze slow queries
docker-compose logs db | grep "duration:" | sort -t: -k2 -n | tail -10

# 3. Check database statistics
docker-compose exec db psql -U odoo -c "
  SELECT schemaname, tablename, n_live_tup, n_dead_tup
  FROM pg_stat_user_tables
  ORDER BY n_dead_tup DESC
  LIMIT 10;
"

# 4. Vacuum database (if high dead tuples)
docker-compose exec db psql -U odoo -c "VACUUM ANALYZE;"
```

---

## Cost Comparison

### Odoo.sh Pricing (Estimated)

| Plan        | Users | Storage | Price/Month |
|-------------|-------|---------|-------------|
| Development | 1     | 1 GB    | Free        |
| Standard    | 10    | 10 GB   | $20-30      |
| Enterprise  | 50+   | 100 GB  | $100-500    |

**Includes**:
- Hosting infrastructure
- Database backups (30 days)
- SSL certificates
- Automatic scaling
- Support and maintenance

### Self-Hosted Docker Costs (Estimated)

| Component          | Specification        | Price/Month |
|--------------------|----------------------|-------------|
| VPS (DigitalOcean) | 4 vCPU, 8 GB RAM     | $48         |
| Block Storage      | 100 GB SSD           | $10         |
| Backup Storage     | S3 (100 GB)          | $2-3        |
| Monitoring         | Self-hosted Grafana  | $0          |
| **Total**          |                      | **$60-65**  |

**Additional Costs**:
- Domain name ($10-15/year)
- SSL certificate (Free with Let's Encrypt)
- Maintenance time (DIY or contractor)

**Break-Even Analysis**:
- Odoo.sh Standard: $20-30/month
- Self-Hosted: $60-65/month
- **Self-hosted cost-effective for**: >50 users OR custom infrastructure requirements

---

## References

- **Odoo.sh Documentation**: https://www.odoo.sh/documentation
- **Odoo.sh CLI**: https://github.com/odoo/odoo-cloud-platform
- **OCA Deployment Patterns**: https://github.com/OCA/maintainer-tools
- **Docker Production Runbook**: `knowledge/runbooks/docker_production.md`
- **Skill**: `skills/odoo-sh-devops/skill.yaml`

---

## License

Apache-2.0

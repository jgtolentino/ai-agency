# Blue-Green Deployment Runbook

Zero-downtime deployment strategy for Odoo 16-19 with automated traffic switching and health validation.

---

## Architecture Overview

Blue-green deployment eliminates downtime by running two identical production environments (blue and green) and switching traffic between them atomically.

### Core Components

```
┌─────────────────────────────────────────────────────┐
│                 Load Balancer                       │
│              (Nginx/HAProxy/Traefik)                │
│                                                     │
│    Traffic Switch: Blue ←→ Green                   │
└──────────────┬─────────────────┬────────────────────┘
               │                 │
               ▼                 ▼
    ┌──────────────────┐  ┌──────────────────┐
    │  Blue Environment│  │ Green Environment│
    │   (Current)      │  │   (Next)         │
    │                  │  │                  │
    │  odoo-blue:8069  │  │ odoo-green:9069  │
    │  db-blue:5432    │  │ db-green:5433    │
    └──────────────────┘  └──────────────────┘
```

### Traffic Switching Strategies

#### 1. Load Balancer DNS (Recommended)
- **Method**: Update load balancer backend pool
- **Switch Time**: Instant (<1 second)
- **Rollback**: Instant backend pool revert
- **Complexity**: Low
- **Best For**: Production deployments

#### 2. DNS-Based Switching
- **Method**: Update DNS A/CNAME records
- **Switch Time**: TTL-dependent (60s-300s)
- **Rollback**: TTL-dependent
- **Complexity**: Very Low
- **Best For**: Non-critical deployments

#### 3. Proxy Configuration Update
- **Method**: Reload Nginx/HAProxy config
- **Switch Time**: Near-instant (graceful reload)
- **Rollback**: Config revert + reload
- **Complexity**: Medium
- **Best For**: Granular control needs

---

## Database Migration Handling

### Strategy 1: Shared Database (Simple)

**Architecture**:
```
Blue Environment ─┐
                  ├─→ Shared PostgreSQL Database
Green Environment ─┘
```

**Pros**:
- Single source of truth
- No data synchronization needed
- Instant rollback (no data restore)

**Cons**:
- Schema migrations must be backward-compatible
- Rollback requires schema rollback scripts
- Both environments must support current schema

**Use When**:
- Schema changes are backward-compatible
- Migration scripts are idempotent
- Quick rollback is critical

**Implementation**:
```yaml
# docker-compose.blue-green-shared-db.yml
version: "3.9"

services:
  db:
    image: postgres:15-alpine
    container_name: odoo-db-shared
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - odoo-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 10s
      timeout: 5s
      retries: 5

  odoo-blue:
    image: odoo:${ODOO_VERSION:-16.0}
    container_name: odoo-blue
    depends_on:
      db:
        condition: service_healthy
    environment:
      HOST: db
      PORT: 5432
      USER: odoo
      PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "8069:8069"
    networks:
      - odoo-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8069/web/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  odoo-green:
    image: odoo:${ODOO_VERSION_NEW:-17.0}
    container_name: odoo-green
    depends_on:
      db:
        condition: service_healthy
    environment:
      HOST: db
      PORT: 5432
      USER: odoo
      PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "9069:8069"
    networks:
      - odoo-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8069/web/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

networks:
  odoo-network:
    driver: bridge

volumes:
  pgdata:
    driver: local
```

**Migration Workflow**:
1. Apply backward-compatible schema changes
2. Deploy green environment with new code
3. Validate green environment
4. Switch traffic to green
5. Monitor for issues
6. Decommission blue when stable

### Strategy 2: Separate Databases (Safe)

**Architecture**:
```
Blue Environment → db-blue:5432
Green Environment → db-green:5433
```

**Pros**:
- Complete isolation between environments
- Schema changes can be breaking
- Easy rollback (just switch back)
- Testing on production-like data

**Cons**:
- Data synchronization complexity
- Storage overhead (2x database size)
- Requires database copy/restore

**Use When**:
- Schema changes are breaking
- Need complete isolation for testing
- Storage is not constrained

**Implementation**:
```yaml
# docker-compose.blue-green-separate-db.yml
version: "3.9"

services:
  db-blue:
    image: postgres:15-alpine
    container_name: odoo-db-blue
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata-blue:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - odoo-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 10s
      timeout: 5s
      retries: 5

  db-green:
    image: postgres:15-alpine
    container_name: odoo-db-green
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - pgdata-green:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    networks:
      - odoo-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 10s
      timeout: 5s
      retries: 5

  odoo-blue:
    image: odoo:${ODOO_VERSION:-16.0}
    container_name: odoo-blue
    depends_on:
      db-blue:
        condition: service_healthy
    environment:
      HOST: db-blue
      PORT: 5432
      USER: odoo
      PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "8069:8069"
    networks:
      - odoo-network

  odoo-green:
    image: odoo:${ODOO_VERSION_NEW:-17.0}
    container_name: odoo-green
    depends_on:
      db-green:
        condition: service_healthy
    environment:
      HOST: db-green
      PORT: 5432
      USER: odoo
      PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "9069:8069"
    networks:
      - odoo-network

networks:
  odoo-network:
    driver: bridge

volumes:
  pgdata-blue:
    driver: local
  pgdata-green:
    driver: local
```

**Migration Workflow**:
1. Clone blue database to green
2. Apply schema migrations to green database
3. Deploy green environment
4. Validate green environment with production data
5. Switch traffic to green
6. Monitor for issues
7. Keep blue as rollback target for 24-48 hours

---

## Zero-Downtime Deployment Procedure

### Prerequisites
- [ ] Load balancer configured (Nginx/HAProxy/Traefik)
- [ ] Health check endpoints implemented (`/web/health`)
- [ ] Blue environment running and healthy
- [ ] Green environment provisioned (not receiving traffic)
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured

### Deployment Steps

#### Phase 1: Preparation (5 minutes)

```bash
#!/bin/bash
# scripts/blue_green_deploy.sh - Phase 1: Preparation

set -e

# 1. Verify blue environment health
echo "🔍 Checking blue environment health..."
curl -f http://localhost:8069/web/health || {
  echo "❌ Blue environment unhealthy, aborting"
  exit 1
}

# 2. Create database backup
echo "💾 Creating database backup..."
docker-compose exec -T db-blue pg_dump -U odoo -Fc postgres > \
  /backups/odoo_pre_deploy_$(date +%Y%m%d_%H%M%S).dump

# 3. Clone database to green (if using separate DB strategy)
echo "📋 Cloning database to green environment..."
docker-compose exec -T db-blue pg_dump -U odoo postgres | \
  docker-compose exec -T db-green psql -U odoo postgres

echo "✅ Phase 1 complete: Preparation done"
```

#### Phase 2: Green Deployment (10-15 minutes)

```bash
#!/bin/bash
# scripts/blue_green_deploy.sh - Phase 2: Green Deployment

set -e

# 4. Pull new image
echo "🐳 Pulling new Docker image..."
docker pull odoo:${ODOO_VERSION_NEW:-17.0}

# 5. Update green environment configuration
echo "⚙️  Updating green environment..."
export ODOO_VERSION_NEW=17.0
docker-compose up -d odoo-green

# 6. Wait for green to start
echo "⏳ Waiting for green environment to start..."
sleep 30

# 7. Run database migrations (if using shared DB)
echo "🔧 Running database migrations..."
docker-compose exec odoo-green odoo-bin \
  -d postgres \
  -u all \
  --stop-after-init

# 8. Start green environment normally
echo "🚀 Starting green environment..."
docker-compose up -d odoo-green

echo "✅ Phase 2 complete: Green environment deployed"
```

#### Phase 3: Health Validation (5 minutes)

```bash
#!/bin/bash
# scripts/blue_green_deploy.sh - Phase 3: Health Validation

set -e

# 9. Run comprehensive health checks
echo "🏥 Running health checks on green environment..."
python3 scripts/health_check.py --target green --comprehensive

# 10. Run smoke tests
echo "💨 Running smoke tests..."
curl -f http://localhost:9069/web/login
curl -f http://localhost:9069/web/database/manager

# 11. Validate critical workflows
echo "✅ Running critical workflow validation..."
# Example: Create test record, verify it exists, delete it
# This is deployment-specific

echo "✅ Phase 3 complete: Health validation passed"
```

#### Phase 4: Traffic Switch (1 minute)

```bash
#!/bin/bash
# scripts/blue_green_deploy.sh - Phase 4: Traffic Switch

set -e

# 12. Update load balancer configuration
echo "🔄 Switching traffic to green environment..."

# Option A: Nginx backend switch
sed -i 's/proxy_pass http:\/\/localhost:8069/proxy_pass http:\/\/localhost:9069/' \
  /etc/nginx/sites-enabled/odoo.conf
nginx -s reload

# Option B: HAProxy backend switch
# echo "set server odoo/blue state maint" | socat stdio /var/run/haproxy.sock
# echo "set server odoo/green state ready" | socat stdio /var/run/haproxy.sock

# Option C: Traefik label update (docker-compose)
# Update labels in docker-compose.yml and docker-compose up -d

# 13. Verify traffic routing
echo "🔍 Verifying traffic routing..."
sleep 5
curl -I http://production.example.com | grep "Server:"

echo "✅ Phase 4 complete: Traffic switched to green"
```

#### Phase 5: Monitoring (15-30 minutes)

```bash
#!/bin/bash
# scripts/blue_green_deploy.sh - Phase 5: Monitoring

set -e

# 14. Monitor green environment metrics
echo "📊 Monitoring green environment (15 min window)..."
for i in {1..15}; do
  echo "Check $i/15..."

  # Health check
  curl -sf http://localhost:9069/web/health || {
    echo "❌ Health check failed, initiating rollback"
    bash scripts/rollback_to_blue.sh
    exit 1
  }

  # Check error rate
  ERROR_COUNT=$(docker-compose logs --tail=100 odoo-green | grep -c "ERROR" || true)
  if [ "$ERROR_COUNT" -gt 5 ]; then
    echo "⚠️  High error count detected: $ERROR_COUNT"
  fi

  sleep 60
done

echo "✅ Phase 5 complete: Monitoring window passed"
```

#### Phase 6: Finalization (2 minutes)

```bash
#!/bin/bash
# scripts/blue_green_deploy.sh - Phase 6: Finalization

set -e

# 15. Stop blue environment (optional - keep for quick rollback)
echo "⏸️  Keeping blue environment as rollback target..."
# docker-compose stop odoo-blue  # Uncomment after 24-48h

# 16. Update deployment metadata
echo "📝 Updating deployment metadata..."
echo "$(date): Deployed Odoo ${ODOO_VERSION_NEW} to green environment" >> \
  /var/log/odoo/deployments.log

# 17. Send success notification
echo "📧 Sending deployment success notification..."
# curl -X POST https://hooks.slack.com/services/XXX -d '{"text":"Deployment successful"}'

echo "✅ Phase 6 complete: Deployment finalized"
echo "🎉 Blue-green deployment successful!"
```

---

## Rollback Procedures

### Instant Rollback (Traffic Switch)

**Trigger Conditions**:
- Health check failures on green environment
- Critical errors detected in logs
- Performance degradation detected
- Manual rollback decision

**Procedure**:

```bash
#!/bin/bash
# scripts/rollback_to_blue.sh

set -e

echo "🔄 Initiating rollback to blue environment..."

# 1. Switch traffic back to blue
echo "🔙 Switching traffic to blue environment..."

# Nginx rollback
sed -i 's/proxy_pass http:\/\/localhost:9069/proxy_pass http:\/\/localhost:8069/' \
  /etc/nginx/sites-enabled/odoo.conf
nginx -s reload

# 2. Verify blue environment health
echo "🏥 Verifying blue environment health..."
curl -f http://localhost:8069/web/health || {
  echo "❌ CRITICAL: Blue environment also unhealthy!"
  exit 1
}

# 3. Verify traffic routing
sleep 5
curl -I http://production.example.com | grep "Server:"

echo "✅ Rollback complete: Traffic restored to blue environment"
echo "⚠️  Investigate green environment issues before next deployment attempt"
```

**Rollback Time**: < 1 minute

### Database Rollback (Separate DB Strategy)

```bash
#!/bin/bash
# scripts/rollback_database.sh

set -e

echo "💾 Rolling back database..."

# 1. Stop green environment
docker-compose stop odoo-green

# 2. Restore pre-deployment backup
echo "📥 Restoring database backup..."
BACKUP_FILE=$(ls -t /backups/odoo_pre_deploy_*.dump | head -1)
docker-compose exec -T db-green psql -U odoo -c "DROP DATABASE IF EXISTS postgres;"
docker-compose exec -T db-green psql -U odoo -c "CREATE DATABASE postgres;"
docker cp "$BACKUP_FILE" odoo-db-green:/tmp/backup.dump
docker-compose exec -T db-green pg_restore -U odoo -d postgres /tmp/backup.dump

echo "✅ Database rollback complete"
```

---

## Health Check Design Patterns

### Health Check Endpoints

#### 1. Basic Liveness Check (`/web/health`)

**Purpose**: Verify Odoo process is running and responding

**Implementation**:
```python
# In Odoo controller
from odoo import http

class HealthController(http.Controller):
    @http.route('/web/health', type='http', auth='none')
    def health_check(self):
        return http.Response("OK", status=200)
```

**Expected Response**:
```http
HTTP/1.1 200 OK
Content-Type: text/plain

OK
```

#### 2. Deep Health Check (`/web/health/deep`)

**Purpose**: Verify all critical services (database, cache, filestore)

**Implementation**:
```python
@http.route('/web/health/deep', type='json', auth='none')
def deep_health_check(self):
    health_status = {
        'status': 'healthy',
        'checks': {}
    }

    # Database check
    try:
        cr = http.request.env.cr
        cr.execute("SELECT 1")
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = f'unhealthy: {str(e)}'

    # Filestore check
    try:
        import os
        filestore_path = http.request.env['ir.attachment']._filestore()
        if os.path.exists(filestore_path) and os.access(filestore_path, os.W_OK):
            health_status['checks']['filestore'] = 'healthy'
        else:
            health_status['status'] = 'unhealthy'
            health_status['checks']['filestore'] = 'unhealthy: not writable'
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['filestore'] = f'unhealthy: {str(e)}'

    return health_status
```

#### 3. Readiness Check (`/web/health/ready`)

**Purpose**: Verify environment is ready to accept traffic

**Implementation**:
```python
@http.route('/web/health/ready', type='json', auth='none')
def readiness_check(self):
    readiness_status = {
        'ready': True,
        'checks': {}
    }

    # Check all modules loaded
    try:
        env = http.request.env
        installed_modules = env['ir.module.module'].search([
            ('state', '=', 'installed')
        ])
        readiness_status['checks']['modules'] = f'{len(installed_modules)} modules loaded'
    except Exception as e:
        readiness_status['ready'] = False
        readiness_status['checks']['modules'] = f'error: {str(e)}'

    # Check database migrations complete
    try:
        # Custom logic to verify migrations
        readiness_status['checks']['migrations'] = 'up to date'
    except Exception as e:
        readiness_status['ready'] = False
        readiness_status['checks']['migrations'] = f'error: {str(e)}'

    return readiness_status
```

### Critical Workflow Smoke Tests

**Purpose**: Validate end-to-end business workflows after deployment

**Examples**:

1. **User Authentication**:
   ```bash
   curl -X POST http://localhost:9069/web/session/authenticate \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"call","params":{"db":"postgres","login":"admin","password":"admin"}}'
   ```

2. **Record Creation**:
   ```python
   # Via RPC
   import xmlrpc.client

   url = "http://localhost:9069"
   db = "postgres"
   username = "admin"
   password = "admin"

   common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
   uid = common.authenticate(db, username, password, {})

   models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
   partner_id = models.execute_kw(db, uid, password,
       'res.partner', 'create',
       [{'name': 'Health Check Partner'}])

   assert partner_id > 0, "Partner creation failed"

   # Cleanup
   models.execute_kw(db, uid, password,
       'res.partner', 'unlink', [[partner_id]])
   ```

3. **Report Generation**:
   ```bash
   # Test PDF report generation
   curl -X POST http://localhost:9069/web/dataset/call_kw \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "method": "call",
       "params": {
         "model": "ir.actions.report",
         "method": "render_qweb_pdf",
         "args": [[1], []]
       }
     }'
   ```

---

## Automated vs Manual Cutover Strategies

### Automated Cutover (Recommended)

**Criteria for Automation**:
- All health checks pass
- Error rate below threshold (<0.1%)
- Response time within SLA (<500ms)
- No critical alerts in monitoring

**Implementation**:
```bash
#!/bin/bash
# scripts/auto_cutover.sh

set -e

echo "🤖 Automated cutover decision process..."

# 1. Run all health checks
python3 scripts/health_check.py --target green --comprehensive --json > /tmp/health_status.json

# 2. Parse health status
HEALTH_STATUS=$(jq -r '.status' /tmp/health_status.json)
if [ "$HEALTH_STATUS" != "healthy" ]; then
  echo "❌ Health checks failed, aborting cutover"
  exit 1
fi

# 3. Check error rate (last 5 minutes)
ERROR_COUNT=$(docker-compose logs --since 5m odoo-green | grep -c "ERROR" || true)
if [ "$ERROR_COUNT" -gt 10 ]; then
  echo "❌ Error rate too high ($ERROR_COUNT errors), aborting cutover"
  exit 1
fi

# 4. Check response time (sample 10 requests)
TOTAL_TIME=0
for i in {1..10}; do
  TIME=$(curl -o /dev/null -s -w '%{time_total}\n' http://localhost:9069/web/health)
  TOTAL_TIME=$(echo "$TOTAL_TIME + $TIME" | bc)
done
AVG_TIME=$(echo "scale=3; $TOTAL_TIME / 10" | bc)

if (( $(echo "$AVG_TIME > 0.5" | bc -l) )); then
  echo "❌ Response time too high (${AVG_TIME}s), aborting cutover"
  exit 1
fi

# 5. All checks passed, proceed with cutover
echo "✅ All checks passed, proceeding with automated cutover"
bash scripts/blue_green_deploy.sh --phase 4

echo "🎉 Automated cutover complete"
```

### Manual Cutover

**Use When**:
- First deployment in new environment
- Major version upgrades (16.0 → 17.0)
- High-risk changes (schema breaking changes)
- Compliance requires manual approval

**Procedure**:
1. Complete automated validation
2. Manual review of health check results
3. Manual smoke testing in green environment
4. Stakeholder approval
5. Scheduled cutover window
6. Manual traffic switch execution
7. Extended monitoring period (30-60 minutes)

---

## Load Balancer Configurations

### Nginx Configuration

```nginx
# /etc/nginx/sites-enabled/odoo.conf

upstream odoo_blue {
    server localhost:8069 max_fails=3 fail_timeout=30s;
}

upstream odoo_green {
    server localhost:9069 max_fails=3 fail_timeout=30s;
}

# Active backend (toggle between blue and green)
upstream odoo_active {
    server localhost:8069;  # Change to 9069 for green
}

server {
    listen 80;
    server_name production.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name production.example.com;

    ssl_certificate /etc/letsencrypt/live/production.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/production.example.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;

    # Health check endpoint (bypass proxy for direct health checks)
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Proxy to active Odoo backend
    location / {
        proxy_pass http://odoo_active;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Longpolling support
    location /longpolling {
        proxy_pass http://odoo_active;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Longpolling specific timeouts
        proxy_read_timeout 3600s;
        proxy_connect_timeout 3600s;
        proxy_send_timeout 3600s;

        # WebSocket
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Traffic Switch Script**:
```bash
#!/bin/bash
# scripts/nginx_switch_traffic.sh

set -e

TARGET=$1  # "blue" or "green"

if [ "$TARGET" != "blue" ] && [ "$TARGET" != "green" ]; then
  echo "Usage: $0 [blue|green]"
  exit 1
fi

PORT=$([ "$TARGET" == "blue" ] && echo "8069" || echo "9069")

echo "🔄 Switching Nginx traffic to $TARGET environment (port $PORT)..."

# Update upstream configuration
sed -i "s/server localhost:[0-9]\+;/server localhost:$PORT;/" \
  /etc/nginx/sites-enabled/odoo.conf

# Test configuration
nginx -t || {
  echo "❌ Nginx configuration test failed"
  exit 1
}

# Reload Nginx (graceful, no downtime)
nginx -s reload

echo "✅ Traffic switched to $TARGET environment"
```

### HAProxy Configuration

```cfg
# /etc/haproxy/haproxy.cfg

global
    log /dev/log local0
    log /dev/log local1 notice
    chroot /var/lib/haproxy
    stats socket /var/run/haproxy.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy
    daemon

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    timeout connect 5000ms
    timeout client  50000ms
    timeout server  50000ms

# Frontend
frontend odoo_frontend
    bind *:80
    bind *:443 ssl crt /etc/haproxy/certs/production.example.com.pem

    # Redirect HTTP to HTTPS
    redirect scheme https if !{ ssl_fc }

    # Health check endpoint
    acl health_check path /health
    use_backend health_backend if health_check

    # Default backend
    default_backend odoo_backend

# Health check backend
backend health_backend
    http-request return status 200 content-type text/plain string "healthy\n"

# Odoo backend (blue-green)
backend odoo_backend
    balance roundrobin
    option httpchk GET /web/health

    # Blue environment (active by default)
    server odoo-blue localhost:8069 check inter 10s fall 3 rise 2

    # Green environment (disabled by default, enable during switch)
    server odoo-green localhost:9069 check inter 10s fall 3 rise 2 disabled

    # Sticky sessions (important for Odoo)
    cookie SERVERID insert indirect nocache
    server odoo-blue localhost:8069 cookie blue check
    server odoo-green localhost:9069 cookie green check disabled
```

**Traffic Switch Script**:
```bash
#!/bin/bash
# scripts/haproxy_switch_traffic.sh

set -e

TARGET=$1  # "blue" or "green"

if [ "$TARGET" != "blue" ] && [ "$TARGET" != "green" ]; then
  echo "Usage: $0 [blue|green]"
  exit 1
fi

echo "🔄 Switching HAProxy traffic to $TARGET environment..."

# Disable current backend, enable target backend
if [ "$TARGET" == "blue" ]; then
  echo "set server odoo_backend/odoo-green state maint" | socat stdio /var/run/haproxy.sock
  echo "set server odoo_backend/odoo-blue state ready" | socat stdio /var/run/haproxy.sock
else
  echo "set server odoo_backend/odoo-blue state maint" | socat stdio /var/run/haproxy.sock
  echo "set server odoo_backend/odoo-green state ready" | socat stdio /var/run/haproxy.sock
fi

# Verify backend status
echo "show servers state" | socat stdio /var/run/haproxy.sock

echo "✅ Traffic switched to $TARGET environment"
```

### Traefik Configuration (Docker Labels)

```yaml
# docker-compose.traefik.yml
version: "3.9"

services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.le.acme.email=admin@example.com"
      - "--certificatesresolvers.le.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.le.acme.httpchallenge=true"
      - "--certificatesresolvers.le.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Traefik dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik-certs:/letsencrypt
    networks:
      - odoo-network

  odoo-blue:
    image: odoo:16.0
    labels:
      # Disabled by default (remove traefik.enable to disable)
      - "traefik.enable=false"
      - "traefik.http.routers.odoo-blue.rule=Host(`production.example.com`)"
      - "traefik.http.routers.odoo-blue.entrypoints=websecure"
      - "traefik.http.routers.odoo-blue.tls.certresolver=le"
      - "traefik.http.services.odoo-blue.loadbalancer.server.port=8069"
    networks:
      - odoo-network

  odoo-green:
    image: odoo:17.0
    labels:
      # Enabled for active deployment
      - "traefik.enable=true"
      - "traefik.http.routers.odoo-green.rule=Host(`production.example.com`)"
      - "traefik.http.routers.odoo-green.entrypoints=websecure"
      - "traefik.http.routers.odoo-green.tls.certresolver=le"
      - "traefik.http.services.odoo-green.loadbalancer.server.port=8069"
    networks:
      - odoo-network

networks:
  odoo-network:
    driver: bridge

volumes:
  traefik-certs:
    driver: local
```

**Traffic Switch Script**:
```bash
#!/bin/bash
# scripts/traefik_switch_traffic.sh

set -e

TARGET=$1  # "blue" or "green"

if [ "$TARGET" != "blue" ] && [ "$TARGET" != "green" ]; then
  echo "Usage: $0 [blue|green]"
  exit 1
fi

echo "🔄 Switching Traefik traffic to $TARGET environment..."

# Update docker-compose labels
if [ "$TARGET" == "blue" ]; then
  # Enable blue, disable green
  docker-compose up -d --no-deps --force-recreate \
    --label traefik.enable=true odoo-blue
  docker-compose up -d --no-deps --force-recreate \
    --label traefik.enable=false odoo-green
else
  # Enable green, disable blue
  docker-compose up -d --no-deps --force-recreate \
    --label traefik.enable=true odoo-green
  docker-compose up -d --no-deps --force-recreate \
    --label traefik.enable=false odoo-blue
fi

# Wait for Traefik to detect changes
sleep 5

echo "✅ Traffic switched to $TARGET environment"
```

---

## Monitoring and Alerting Integration

### Prometheus Metrics

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'odoo-blue'
    static_configs:
      - targets: ['localhost:8069']
    metrics_path: '/metrics'

  - job_name: 'odoo-green'
    static_configs:
      - targets: ['localhost:9069']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']  # postgres_exporter
```

### Grafana Dashboards

**Key Metrics**:
- HTTP request rate (requests/sec)
- HTTP error rate (%)
- Response time (P50, P95, P99)
- Database connection pool usage
- Active sessions count
- Memory usage (MB)
- CPU usage (%)

### Alerting Rules

```yaml
# prometheus_alerts.yml
groups:
  - name: odoo_deployment
    interval: 30s
    rules:
      # High error rate on green environment
      - alert: GreenEnvironmentHighErrorRate
        expr: rate(http_requests_total{job="odoo-green",status=~"5.."}[5m]) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on green environment"
          description: "Error rate {{ $value }}% on green environment, consider rollback"

      # Slow response time on green
      - alert: GreenEnvironmentSlowResponse
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="odoo-green"}[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time on green environment"
          description: "P95 response time {{ $value }}s on green environment"

      # Health check failures
      - alert: GreenEnvironmentHealthCheckFailed
        expr: up{job="odoo-green"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Green environment health check failed"
          description: "Immediate rollback recommended"
```

---

## Canary Deployment Pattern

Gradual traffic shift from blue to green (e.g., 10% → 50% → 100%).

### HAProxy Canary Configuration

```cfg
backend odoo_backend
    balance roundrobin
    option httpchk GET /web/health

    # Blue environment (90% traffic initially)
    server odoo-blue localhost:8069 weight 90 check

    # Green environment (10% traffic initially)
    server odoo-green localhost:9069 weight 10 check
```

**Gradual Shift Script**:
```bash
#!/bin/bash
# scripts/canary_deploy.sh

set -e

echo "🕊️  Starting canary deployment..."

# Stage 1: 10% traffic to green
echo "Stage 1: 10% traffic to green..."
echo "set server odoo_backend/odoo-blue weight 90" | socat stdio /var/run/haproxy.sock
echo "set server odoo_backend/odoo-green weight 10" | socat stdio /var/run/haproxy.sock
sleep 300  # Monitor for 5 minutes

# Stage 2: 50% traffic to green
echo "Stage 2: 50% traffic to green..."
echo "set server odoo_backend/odoo-blue weight 50" | socat stdio /var/run/haproxy.sock
echo "set server odoo_backend/odoo-green weight 50" | socat stdio /var/run/haproxy.sock
sleep 300  # Monitor for 5 minutes

# Stage 3: 100% traffic to green
echo "Stage 3: 100% traffic to green..."
echo "set server odoo_backend/odoo-blue weight 0" | socat stdio /var/run/haproxy.sock
echo "set server odoo_backend/odoo-green weight 100" | socat stdio /var/run/haproxy.sock

echo "✅ Canary deployment complete"
```

---

## Best Practices

### Pre-Deployment
- [ ] Run full test suite in green environment
- [ ] Validate database migrations in test environment
- [ ] Create database backup before deployment
- [ ] Document rollback procedure
- [ ] Notify stakeholders of deployment window
- [ ] Verify monitoring and alerting functional

### During Deployment
- [ ] Monitor health checks continuously
- [ ] Watch error logs in real-time
- [ ] Track key performance metrics
- [ ] Validate critical workflows manually
- [ ] Keep rollback script ready for execution
- [ ] Maintain communication channel open

### Post-Deployment
- [ ] Extended monitoring period (30-60 minutes)
- [ ] Review deployment logs for anomalies
- [ ] Update deployment documentation
- [ ] Archive blue environment (24-48h retention)
- [ ] Document lessons learned
- [ ] Update runbook based on experience

---

## Troubleshooting

### Issue: Health Checks Pass But Application Broken

**Symptom**: `/web/health` returns 200, but application shows errors

**Root Cause**: Health check too simple, doesn't validate critical services

**Solution**: Implement deep health checks (database, filestore, modules)

### Issue: Database Migration Deadlock During Deployment

**Symptom**: Green environment stuck during migration, timeouts

**Root Cause**: Blue environment holding locks on tables

**Solution**: Use separate databases OR stop blue before migration

### Issue: Session Loss After Traffic Switch

**Symptom**: Users logged out after traffic switch

**Root Cause**: Sessions stored in memory, not shared between environments

**Solution**: Use shared session store (Redis) OR expect session loss

### Issue: Rollback Takes Too Long

**Symptom**: Rollback process exceeds acceptable downtime window

**Root Cause**: Complex rollback procedure, multiple manual steps

**Solution**: Automate rollback, use instant traffic switch without DB rollback

---

## References

- **Docker Production Runbook**: `knowledge/runbooks/docker_production.md`
- **Odoo.sh Deployment**: `knowledge/runbooks/odoo_sh_deployment.md`
- **Health Check Script**: `scripts/health_check.py`
- **Deployment Automation**: `knowledge/runbooks/deployment_automation.md`
- **GitHub Actions Workflow**: `.github/workflows/blue_green_deploy.yml`

---

## License

Apache-2.0

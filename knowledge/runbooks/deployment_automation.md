# Deployment Automation Runbook

Complete automation framework for Odoo blue-green deployment using GitHub Actions, Docker Compose, and load balancer orchestration.

---

## Overview

This runbook provides production-ready automation for zero-downtime Odoo deployments with:
- Automated GitHub Actions workflow
- Docker Compose blue-green orchestration
- Load balancer configuration and traffic switching
- Health check gates and automated rollback
- Monitoring and alerting integration
- Canary deployment patterns

---

## GitHub Actions Workflow

### Workflow Architecture

```
┌─────────────────────────────────────────────────────┐
│          GitHub Actions Workflow                    │
│                                                     │
│  [Trigger] → [Build] → [Health Check]              │
│       ↓          ↓            ↓                     │
│  [Deploy Green] → [Validate] → [Switch Traffic]    │
│                                  ↓                  │
│                         [Monitor] → [Rollback?]    │
└─────────────────────────────────────────────────────┘
```

### Workflow File: `.github/workflows/blue_green_deploy.yml`

See the complete workflow implementation in `.github/workflows/blue_green_deploy.yml`.

**Key Features**:
- **Multi-stage deployment**: Build → Deploy → Validate → Switch → Monitor
- **Health check gates**: Automated validation before traffic switch
- **Rollback triggers**: Automatic rollback on health check failures
- **Environment management**: Blue/green environment isolation
- **Secrets management**: Secure handling of credentials via GitHub Secrets
- **Status notifications**: Slack/email alerts on deployment events

---

## Docker Compose Blue-Green Setup

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  Docker Network                     │
│                                                     │
│  ┌──────────────┐         ┌──────────────┐         │
│  │ Nginx/       │         │ Traefik/     │         │
│  │ HAProxy LB   │         │ (optional)   │         │
│  └──────┬───────┘         └──────────────┘         │
│         │                                           │
│    ┌────┴────┐                                      │
│    │         │                                      │
│    ▼         ▼                                      │
│  ┌─────┐   ┌─────┐                                 │
│  │Blue │   │Green│                                 │
│  │8069 │   │9069 │                                 │
│  └──┬──┘   └──┬──┘                                 │
│     │         │                                     │
│     ▼         ▼                                     │
│  ┌──────────────┐                                  │
│  │ PostgreSQL   │                                  │
│  │ (Shared/Sep) │                                  │
│  └──────────────┘                                  │
└─────────────────────────────────────────────────────┘
```

### Complete Docker Compose Configuration

```yaml
# docker-compose.blue-green.yml
version: "3.9"

services:
  # ============================================================================
  # Load Balancer (Nginx)
  # ============================================================================
  nginx:
    image: nginx:alpine
    container_name: odoo-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    networks:
      - odoo-network
    depends_on:
      - odoo-blue
      - odoo-green
    restart: unless-stopped

  # ============================================================================
  # PostgreSQL Database (Shared or Separate)
  # ============================================================================
  db:
    image: postgres:15-alpine
    container_name: odoo-db
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?required}
      POSTGRES_DB: postgres
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - odoo-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # ============================================================================
  # Blue Environment (Current Production)
  # ============================================================================
  odoo-blue:
    image: ${BLUE_IMAGE:-odoo:16.0}
    container_name: odoo-blue
    depends_on:
      db:
        condition: service_healthy
    environment:
      HOST: db
      PORT: 5432
      USER: odoo
      PASSWORD: ${POSTGRES_PASSWORD}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:?required}
    volumes:
      - ./odoo.conf:/opt/odoo/odoo.conf:ro
      - ./custom_addons:/mnt/extra-addons:ro
      - odoo-filestore-blue:/var/lib/odoo
      - odoo-logs-blue:/var/log/odoo
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
    restart: unless-stopped
    labels:
      - "odoo.environment=blue"
      - "odoo.version=${BLUE_VERSION:-16.0}"

  # ============================================================================
  # Green Environment (Next Production)
  # ============================================================================
  odoo-green:
    image: ${GREEN_IMAGE:-odoo:17.0}
    container_name: odoo-green
    depends_on:
      db:
        condition: service_healthy
    environment:
      HOST: db
      PORT: 5432
      USER: odoo
      PASSWORD: ${POSTGRES_PASSWORD}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:?required}
    volumes:
      - ./odoo.conf:/opt/odoo/odoo.conf:ro
      - ./custom_addons:/mnt/extra-addons:ro
      - odoo-filestore-green:/var/lib/odoo
      - odoo-logs-green:/var/log/odoo
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
    restart: unless-stopped
    labels:
      - "odoo.environment=green"
      - "odoo.version=${GREEN_VERSION:-17.0}"
    # Initially stopped (start manually for deployment)
    profiles:
      - deployment

  # ============================================================================
  # Monitoring Stack (Prometheus + Grafana)
  # ============================================================================
  prometheus:
    image: prom/prometheus:latest
    container_name: odoo-prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - odoo-network
    restart: unless-stopped
    profiles:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: odoo-grafana
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-admin}
      GF_INSTALL_PLUGINS: grafana-piechart-panel
    volumes:
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - odoo-network
    depends_on:
      - prometheus
    restart: unless-stopped
    profiles:
      - monitoring

  # ============================================================================
  # Postgres Exporter (for Prometheus metrics)
  # ============================================================================
  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: odoo-postgres-exporter
    environment:
      DATA_SOURCE_NAME: "postgresql://odoo:${POSTGRES_PASSWORD}@db:5432/postgres?sslmode=disable"
    ports:
      - "9187:9187"
    networks:
      - odoo-network
    depends_on:
      - db
    restart: unless-stopped
    profiles:
      - monitoring

networks:
  odoo-network:
    driver: bridge

volumes:
  pgdata:
    driver: local
  odoo-filestore-blue:
    driver: local
  odoo-filestore-green:
    driver: local
  odoo-logs-blue:
    driver: local
  odoo-logs-green:
    driver: local
  prometheus-data:
    driver: local
  grafana-data:
    driver: local
```

### Docker Compose Operations

#### Initial Setup

```bash
#!/bin/bash
# scripts/setup_blue_green.sh

set -e

echo "🚀 Setting up blue-green deployment environment..."

# 1. Create necessary directories
mkdir -p nginx/conf.d nginx/ssl monitoring/prometheus monitoring/grafana/dashboards monitoring/grafana/datasources

# 2. Copy environment template
cp .env.example .env
echo "⚠️  Edit .env with your secrets before proceeding"

# 3. Start blue environment (current production)
echo "Starting blue environment..."
docker-compose -f docker-compose.blue-green.yml up -d odoo-blue db nginx

# 4. Wait for blue to be healthy
echo "Waiting for blue environment to be healthy..."
sleep 30
docker-compose -f docker-compose.blue-green.yml exec odoo-blue curl -f http://localhost:8069/web/health

# 5. Start monitoring stack (optional)
echo "Starting monitoring stack..."
docker-compose -f docker-compose.blue-green.yml --profile monitoring up -d

echo "✅ Blue-green environment setup complete"
echo "Blue environment: http://localhost:8069"
echo "Monitoring: http://localhost:3000 (Grafana)"
```

#### Deploy Green Environment

```bash
#!/bin/bash
# scripts/deploy_green.sh

set -e

GREEN_IMAGE=${1:-odoo:17.0}

echo "🌱 Deploying green environment with image: $GREEN_IMAGE"

# 1. Pull new image
docker pull "$GREEN_IMAGE"

# 2. Update environment variable
export GREEN_IMAGE="$GREEN_IMAGE"

# 3. Start green environment
docker-compose -f docker-compose.blue-green.yml --profile deployment up -d odoo-green

# 4. Wait for green to start
echo "Waiting for green environment to start..."
sleep 30

# 5. Run health checks
echo "Running health checks on green environment..."
python3 scripts/health_check.py --target green --comprehensive

# 6. Run smoke tests
echo "Running smoke tests..."
docker-compose -f docker-compose.blue-green.yml exec odoo-green \
  curl -f http://localhost:8069/web/login

echo "✅ Green environment deployed and healthy"
echo "Green environment: http://localhost:9069"
```

#### Switch Traffic to Green

```bash
#!/bin/bash
# scripts/switch_to_green.sh

set -e

echo "🔄 Switching traffic to green environment..."

# 1. Verify green is healthy
python3 scripts/health_check.py --target green --comprehensive || {
  echo "❌ Green environment unhealthy, aborting traffic switch"
  exit 1
}

# 2. Update Nginx configuration
sed -i 's/proxy_pass http:\/\/odoo-blue:8069/proxy_pass http:\/\/odoo-green:8069/' \
  nginx/conf.d/odoo.conf

# 3. Reload Nginx
docker-compose -f docker-compose.blue-green.yml exec nginx nginx -s reload

# 4. Verify traffic routing
sleep 5
curl -I http://localhost | grep -i "server"

echo "✅ Traffic switched to green environment"
echo "⚠️  Monitor green environment for 30 minutes before stopping blue"
```

#### Rollback to Blue

```bash
#!/bin/bash
# scripts/rollback_to_blue.sh

set -e

echo "🔙 Rolling back to blue environment..."

# 1. Update Nginx configuration
sed -i 's/proxy_pass http:\/\/odoo-green:8069/proxy_pass http:\/\/odoo-blue:8069/' \
  nginx/conf.d/odoo.conf

# 2. Reload Nginx
docker-compose -f docker-compose.blue-green.yml exec nginx nginx -s reload

# 3. Verify blue is healthy
python3 scripts/health_check.py --target blue --comprehensive || {
  echo "❌ CRITICAL: Blue environment also unhealthy!"
  exit 1
}

# 4. Stop green environment
docker-compose -f docker-compose.blue-green.yml stop odoo-green

echo "✅ Rollback complete: Traffic restored to blue environment"
```

---

## Nginx Load Balancer Configuration

### Main Nginx Configuration

```nginx
# nginx/nginx.conf

user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript
               application/json application/javascript application/xml+rss
               application/rss+xml font/truetype font/opentype
               application/vnd.ms-fontobject image/svg+xml;

    include /etc/nginx/conf.d/*.conf;
}
```

### Odoo Site Configuration

```nginx
# nginx/conf.d/odoo.conf

upstream odoo_blue {
    server odoo-blue:8069 max_fails=3 fail_timeout=30s;
}

upstream odoo_green {
    server odoo-green:8069 max_fails=3 fail_timeout=30s;
}

# Map to determine active backend (toggle this during switch)
upstream odoo_active {
    # ACTIVE: blue
    server odoo-blue:8069;

    # ACTIVE: green (uncomment during switch, comment blue)
    # server odoo-green:8069;
}

# HTTP server (redirect to HTTPS)
server {
    listen 80;
    server_name odoo.example.com;

    # Health check endpoint (no redirect)
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name odoo.example.com;

    # SSL certificates (replace with your paths)
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    # SSL configuration (modern)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Client body size (for file uploads)
    client_max_body_size 100M;

    # Health check endpoint (bypass proxy)
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Odoo backend
    location / {
        proxy_pass http://odoo_active;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Longpolling
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

    # Static files (optional caching)
    location ~* /web/static/ {
        proxy_pass http://odoo_active;
        proxy_cache_valid 200 60m;
        proxy_buffering on;
        expires 864000;
    }
}
```

---

## HAProxy Load Balancer Configuration

### Complete HAProxy Configuration

```cfg
# haproxy/haproxy.cfg

global
    log /dev/log local0
    log /dev/log local1 notice
    chroot /var/lib/haproxy
    stats socket /var/run/haproxy.sock mode 660 level admin expose-fd listeners
    stats timeout 30s
    user haproxy
    group haproxy
    daemon

    # SSL/TLS configuration
    ssl-default-bind-ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256
    ssl-default-bind-options ssl-min-ver TLSv1.2 no-tls-tickets

defaults
    log     global
    mode    http
    option  httplog
    option  dontlognull
    option  forwardfor
    timeout connect 5000ms
    timeout client  50000ms
    timeout server  50000ms
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 408 /etc/haproxy/errors/408.http
    errorfile 500 /etc/haproxy/errors/500.http
    errorfile 502 /etc/haproxy/errors/502.http
    errorfile 503 /etc/haproxy/errors/503.http
    errorfile 504 /etc/haproxy/errors/504.http

# Frontend (HTTP and HTTPS)
frontend odoo_frontend
    bind *:80
    bind *:443 ssl crt /etc/haproxy/certs/odoo.example.com.pem

    # Redirect HTTP to HTTPS
    redirect scheme https code 301 if !{ ssl_fc }

    # Health check endpoint (local)
    acl health_check path /health
    use_backend health_backend if health_check

    # Default to Odoo backend
    default_backend odoo_backend

# Health check backend
backend health_backend
    mode http
    http-request return status 200 content-type text/plain lf-string "healthy\n"

# Odoo backend (blue-green)
backend odoo_backend
    mode http
    balance roundrobin
    option httpchk GET /web/health
    http-check expect status 200

    # Cookie-based sticky sessions (important for Odoo)
    cookie SERVERID insert indirect nocache

    # Blue environment (active by default)
    server odoo-blue odoo-blue:8069 cookie blue check inter 10s fall 3 rise 2

    # Green environment (maintenance mode by default)
    server odoo-green odoo-green:8069 cookie green check inter 10s fall 3 rise 2 disabled

    # Longpolling timeout
    timeout server 3600s
```

### HAProxy Traffic Switch Script

```bash
#!/bin/bash
# scripts/haproxy_switch.sh

set -e

TARGET=$1  # "blue" or "green"

if [ "$TARGET" != "blue" ] && [ "$TARGET" != "green" ]; then
  echo "Usage: $0 [blue|green]"
  exit 1
fi

echo "🔄 Switching HAProxy traffic to $TARGET..."

# Get HAProxy socket
HAPROXY_SOCK="/var/run/haproxy.sock"

# Verify socket exists
if [ ! -S "$HAPROXY_SOCK" ]; then
  echo "❌ HAProxy socket not found at $HAPROXY_SOCK"
  exit 1
fi

# Switch traffic
if [ "$TARGET" == "blue" ]; then
  # Enable blue, disable green
  echo "set server odoo_backend/odoo-blue state ready" | socat stdio "$HAPROXY_SOCK"
  echo "set server odoo_backend/odoo-green state maint" | socat stdio "$HAPROXY_SOCK"
else
  # Enable green, disable blue
  echo "set server odoo_backend/odoo-green state ready" | socat stdio "$HAPROXY_SOCK"
  echo "set server odoo_backend/odoo-blue state maint" | socat stdio "$HAPROXY_SOCK"
fi

# Show server status
echo ""
echo "Backend status:"
echo "show servers state odoo_backend" | socat stdio "$HAPROXY_SOCK"

echo "✅ Traffic switched to $TARGET"
```

---

## Traefik Load Balancer Configuration

### Traefik with Docker Labels

```yaml
# docker-compose.traefik.yml
version: "3.9"

services:
  traefik:
    image: traefik:v2.10
    container_name: traefik
    command:
      # API and dashboard
      - "--api.insecure=true"
      - "--api.dashboard=true"

      # Docker provider
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--providers.docker.network=odoo-network"

      # Entrypoints
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"

      # Let's Encrypt
      - "--certificatesresolvers.le.acme.email=admin@example.com"
      - "--certificatesresolvers.le.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.le.acme.httpchallenge=true"
      - "--certificatesresolvers.le.acme.httpchallenge.entrypoint=web"

      # Logging
      - "--accesslog=true"
      - "--log.level=INFO"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"  # Traefik dashboard
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik-certs:/letsencrypt
    networks:
      - odoo-network
    restart: unless-stopped

  odoo-blue:
    image: odoo:16.0
    container_name: odoo-blue
    labels:
      # Enable Traefik
      - "traefik.enable=true"

      # HTTP router (redirect to HTTPS)
      - "traefik.http.routers.odoo-blue-http.rule=Host(`odoo.example.com`)"
      - "traefik.http.routers.odoo-blue-http.entrypoints=web"
      - "traefik.http.routers.odoo-blue-http.middlewares=odoo-redirect-https"

      # HTTPS router
      - "traefik.http.routers.odoo-blue.rule=Host(`odoo.example.com`)"
      - "traefik.http.routers.odoo-blue.entrypoints=websecure"
      - "traefik.http.routers.odoo-blue.tls.certresolver=le"

      # Service
      - "traefik.http.services.odoo-blue.loadbalancer.server.port=8069"

      # Middleware: HTTPS redirect
      - "traefik.http.middlewares.odoo-redirect-https.redirectscheme.scheme=https"
      - "traefik.http.middlewares.odoo-redirect-https.redirectscheme.permanent=true"

      # Health check
      - "traefik.http.services.odoo-blue.loadbalancer.healthcheck.path=/web/health"
      - "traefik.http.services.odoo-blue.loadbalancer.healthcheck.interval=30s"

      # Sticky sessions
      - "traefik.http.services.odoo-blue.loadbalancer.sticky.cookie=true"
      - "traefik.http.services.odoo-blue.loadbalancer.sticky.cookie.name=SERVERID"

    networks:
      - odoo-network
    restart: unless-stopped

  odoo-green:
    image: odoo:17.0
    container_name: odoo-green
    labels:
      # Initially disabled (change to "true" during deployment)
      - "traefik.enable=false"

      # Same configuration as blue (enabled during switch)
      - "traefik.http.routers.odoo-green-http.rule=Host(`odoo.example.com`)"
      - "traefik.http.routers.odoo-green-http.entrypoints=web"
      - "traefik.http.routers.odoo-green-http.middlewares=odoo-redirect-https"

      - "traefik.http.routers.odoo-green.rule=Host(`odoo.example.com`)"
      - "traefik.http.routers.odoo-green.entrypoints=websecure"
      - "traefik.http.routers.odoo-green.tls.certresolver=le"

      - "traefik.http.services.odoo-green.loadbalancer.server.port=8069"
      - "traefik.http.services.odoo-green.loadbalancer.healthcheck.path=/web/health"
      - "traefik.http.services.odoo-green.loadbalancer.sticky.cookie=true"

    networks:
      - odoo-network
    restart: unless-stopped

networks:
  odoo-network:
    driver: bridge

volumes:
  traefik-certs:
    driver: local
```

### Traefik Traffic Switch Script

```bash
#!/bin/bash
# scripts/traefik_switch.sh

set -e

TARGET=$1  # "blue" or "green"

if [ "$TARGET" != "blue" ] && [ "$TARGET" != "green" ]; then
  echo "Usage: $0 [blue|green]"
  exit 1
fi

echo "🔄 Switching Traefik traffic to $TARGET..."

# Update docker labels via docker-compose
if [ "$TARGET" == "blue" ]; then
  # Enable blue, disable green
  docker update --label traefik.enable=true odoo-blue
  docker update --label traefik.enable=false odoo-green
else
  # Enable green, disable blue
  docker update --label traefik.enable=true odoo-green
  docker update --label traefik.enable=false odoo-blue
fi

# Wait for Traefik to detect changes
sleep 5

# Verify routing
curl -I http://odoo.example.com

echo "✅ Traffic switched to $TARGET"
```

---

## Monitoring and Alerting Integration

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'odoo-production'
    environment: 'blue-green'

# Alerting configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

# Load rules
rule_files:
  - '/etc/prometheus/rules/*.yml'

# Scrape configurations
scrape_configs:
  # Odoo Blue environment
  - job_name: 'odoo-blue'
    static_configs:
      - targets: ['odoo-blue:8069']
    metrics_path: '/metrics'

  # Odoo Green environment
  - job_name: 'odoo-green'
    static_configs:
      - targets: ['odoo-green:8069']
    metrics_path: '/metrics'

  # PostgreSQL
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  # Nginx
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']
```

### Prometheus Alert Rules

```yaml
# monitoring/prometheus/rules/odoo_alerts.yml

groups:
  - name: odoo_deployment
    interval: 30s
    rules:
      # Green environment health check
      - alert: GreenEnvironmentDown
        expr: up{job="odoo-green"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Green environment is down"
          description: "Odoo green environment has been down for 1 minute. Immediate rollback recommended."

      # High error rate on green
      - alert: GreenHighErrorRate
        expr: rate(http_requests_total{job="odoo-green",status=~"5.."}[5m]) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on green environment"
          description: "Error rate {{ $value | humanizePercentage }} on green environment"

      # Slow response time on green
      - alert: GreenSlowResponse
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="odoo-green"}[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time on green"
          description: "P95 response time {{ $value }}s on green environment"

      # Database connection pool exhaustion
      - alert: DatabaseConnectionPoolExhausted
        expr: pg_stat_activity_count > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "{{ $value }} database connections active (limit 100)"
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Odoo Blue-Green Deployment",
    "panels": [
      {
        "title": "Environment Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=~\"odoo-blue|odoo-green\"}",
            "legendFormat": "{{ job }}"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{job=~\"odoo-blue|odoo-green\"}[5m])",
            "legendFormat": "{{ job }}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{job=~\"odoo-blue|odoo-green\",status=~\"5..\"}[5m])",
            "legendFormat": "{{ job }}"
          }
        ]
      },
      {
        "title": "Response Time (P95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job=~\"odoo-blue|odoo-green\"}[5m]))",
            "legendFormat": "{{ job }}"
          }
        ]
      }
    ]
  }
}
```

---

## Automated Rollback Triggers

### Rollback Conditions

```yaml
# rollback_conditions.yml

conditions:
  # Critical: Immediate rollback
  critical:
    - health_check_failed: true
      threshold: 1  # 1 failure
      action: immediate_rollback

    - error_rate_percent: 5.0
      duration_seconds: 120
      action: immediate_rollback

    - response_time_p95_seconds: 5.0
      duration_seconds: 300
      action: immediate_rollback

  # Warning: Monitor and prepare rollback
  warning:
    - error_rate_percent: 1.0
      duration_seconds: 300
      action: alert_and_monitor

    - response_time_p95_seconds: 2.0
      duration_seconds: 600
      action: alert_and_monitor

    - memory_usage_percent: 90
      duration_seconds: 300
      action: alert_and_monitor
```

### Automated Rollback Script

```bash
#!/bin/bash
# scripts/auto_rollback.sh

set -e

echo "🤖 Automated rollback monitoring starting..."

# Configuration
ERROR_RATE_THRESHOLD=0.05  # 5%
RESPONSE_TIME_THRESHOLD=5.0  # 5 seconds
HEALTH_CHECK_INTERVAL=30  # 30 seconds
MONITORING_DURATION=1800  # 30 minutes

START_TIME=$(date +%s)

while true; do
  CURRENT_TIME=$(date +%s)
  ELAPSED=$((CURRENT_TIME - START_TIME))

  # Stop monitoring after duration
  if [ $ELAPSED -gt $MONITORING_DURATION ]; then
    echo "✅ Monitoring period complete, no rollback needed"
    exit 0
  fi

  echo "[$ELAPSED/${MONITORING_DURATION}s] Checking green environment health..."

  # 1. Health check
  if ! python3 scripts/health_check.py --target green --json > /tmp/health_status.json 2>&1; then
    echo "❌ Health check failed, initiating rollback"
    bash scripts/rollback_to_blue.sh
    exit 1
  fi

  # 2. Error rate check
  ERROR_COUNT=$(docker-compose logs --since ${HEALTH_CHECK_INTERVAL}s odoo-green | grep -c "ERROR" || true)
  TOTAL_REQUESTS=$(docker-compose logs --since ${HEALTH_CHECK_INTERVAL}s odoo-green | grep -c "GET\|POST" || true)

  if [ $TOTAL_REQUESTS -gt 0 ]; then
    ERROR_RATE=$(echo "scale=4; $ERROR_COUNT / $TOTAL_REQUESTS" | bc)
    if (( $(echo "$ERROR_RATE > $ERROR_RATE_THRESHOLD" | bc -l) )); then
      echo "❌ Error rate too high ($ERROR_RATE), initiating rollback"
      bash scripts/rollback_to_blue.sh
      exit 1
    fi
  fi

  # 3. Response time check
  RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' http://localhost:9069/web/health)
  if (( $(echo "$RESPONSE_TIME > $RESPONSE_TIME_THRESHOLD" | bc -l) )); then
    echo "⚠️  High response time detected: ${RESPONSE_TIME}s"
  fi

  # Wait for next check
  sleep $HEALTH_CHECK_INTERVAL
done
```

---

## Canary Deployment Pattern

### Gradual Traffic Shift

```bash
#!/bin/bash
# scripts/canary_deploy.sh

set -e

echo "🕊️  Starting canary deployment to green environment..."

# Stage 1: 10% traffic
echo "Stage 1: Routing 10% traffic to green..."
docker update --label "traefik.http.services.odoo-green.loadbalancer.weight=10" odoo-green
docker update --label "traefik.http.services.odoo-blue.loadbalancer.weight=90" odoo-blue
sleep 300  # Monitor for 5 minutes
python3 scripts/health_check.py --target green --comprehensive

# Stage 2: 50% traffic
echo "Stage 2: Routing 50% traffic to green..."
docker update --label "traefik.http.services.odoo-green.loadbalancer.weight=50" odoo-green
docker update --label "traefik.http.services.odoo-blue.loadbalancer.weight=50" odoo-blue
sleep 300  # Monitor for 5 minutes
python3 scripts/health_check.py --target green --comprehensive

# Stage 3: 100% traffic
echo "Stage 3: Routing 100% traffic to green..."
docker update --label "traefik.http.services.odoo-green.loadbalancer.weight=100" odoo-green
docker update --label "traefik.http.services.odoo-blue.loadbalancer.weight=0" odoo-blue
sleep 600  # Monitor for 10 minutes
python3 scripts/health_check.py --target green --comprehensive

echo "✅ Canary deployment complete: 100% traffic on green"
```

---

## References

- **Blue-Green Deployment Runbook**: `knowledge/runbooks/blue_green_deployment.md`
- **Health Check Script**: `scripts/health_check.py`
- **GitHub Actions Workflow**: `.github/workflows/blue_green_deploy.yml`
- **Docker Production**: `knowledge/runbooks/docker_production.md`
- **Odoo.sh Deployment**: `knowledge/runbooks/odoo_sh_deployment.md`

---

## License

Apache-2.0

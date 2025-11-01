# Pulse-Hub Multi-Service Deployment SOP

**Standard Operating Procedure for deploying pulse-hub infrastructure to DigitalOcean App Platform**

**Version**: 1.0.0
**Last Updated**: 2025-11-01
**Status**: ✅ Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Deployment Procedure](#deployment-procedure)
5. [Error Codes and Troubleshooting](#error-codes-and-troubleshooting)
6. [Rollback Procedures](#rollback-procedures)
7. [Health Monitoring](#health-monitoring)
8. [Security Considerations](#security-considerations)

---

## Overview

### Purpose

This SOP provides step-by-step instructions for deploying the pulse-hub multi-service system to DigitalOcean App Platform. Pulse-hub is a GitHub-integrated analytics and workflow management platform consisting of three services:

- **pulse-hub-web**: Next.js frontend with GitHub OAuth authentication
- **pulse-hub-mcp**: MCP (Model Context Protocol) server for AI integration
- **pulse-hub-superset**: Apache Superset for business intelligence dashboards

### Deployment Model

```
┌────────────────────────────────────────────────────────────┐
│              DigitalOcean App Platform                     │
│                                                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────┐│
│  │ pulse-hub-web    │  │ pulse-hub-mcp    │  │ superset ││
│  │ (Next.js)        │  │ (Node.js MCP)    │  │ (Python) ││
│  │ Port: 3000       │  │ Port: 8080       │  │ Port: 8088││
│  └────────┬─────────┘  └────────┬─────────┘  └────┬─────┘│
│           │                     │                  │       │
│           └─────────────────────┴──────────────────┘       │
│                              │                             │
└──────────────────────────────┼─────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │ Supabase PostgreSQL │
                    │ (External Database) │
                    └─────────────────────┘
```

### Service Responsibilities

| Service | Port | Purpose | Dependencies |
|---------|------|---------|--------------|
| pulse-hub-web | 3000 | Web interface, GitHub OAuth | GitHub OAuth App, Supabase |
| pulse-hub-mcp | 8080 | MCP server for AI tools | Supabase, GitHub API |
| pulse-hub-superset | 8088 | BI dashboards and analytics | Supabase PostgreSQL |

---

## Prerequisites

### Required Accounts and Credentials

1. **DigitalOcean Account**
   - Active App Platform subscription
   - `doctl` CLI installed and authenticated
   - Access token with write permissions

2. **GitHub OAuth Application**
   - OAuth App created in GitHub Settings
   - Client ID and Client Secret
   - Production redirect URI configured
   - Required scopes: `repo`, `workflow`

3. **Supabase Project**
   - Project created and configured
   - PostgreSQL connection string
   - Service role key for backend services
   - Anon key for frontend

4. **Environment Variables**
   - All secrets stored in `~/.zshrc` or GitHub Secrets
   - Environment-specific configuration files ready

### Required Tools

```bash
# DigitalOcean CLI
brew install doctl
doctl auth init

# Verify authentication
doctl apps list

# Git (for repository operations)
git --version

# jq (for JSON parsing)
brew install jq
```

### Access Verification

```bash
# Test DigitalOcean access
doctl apps list --format ID,Spec.Name

# Test GitHub access
gh auth status

# Test Supabase connection
psql "$POSTGRES_URL" -c "SELECT 1;"
```

---

## Architecture

### Service Dependency Graph

```
┌─────────────────────────────────────────────────────┐
│                 User Request                        │
└─────────────────────┬───────────────────────────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │   pulse-hub-web       │
          │   (Public Route)      │
          └───────┬───────────────┘
                  │
                  ├─────────► GitHub OAuth API (Authentication)
                  │
                  ├─────────► pulse-hub-mcp (AI Tools)
                  │
                  ├─────────► pulse-hub-superset (Dashboards)
                  │
                  └─────────► Supabase PostgreSQL (Data Layer)
```

### Network Configuration

**External Access**:
- pulse-hub-web: `https://pulse-hub-web-<hash>.ondigitalocean.app`
- pulse-hub-mcp: Internal only (no public route)
- pulse-hub-superset: Internal only (proxy via web service)

**Internal Communication**:
- Services communicate via internal DNS: `<service-name>.ondigitalocean.app`
- All internal traffic uses HTTPS with DigitalOcean-managed certificates

### Data Flow

1. **Authentication Flow**:
   ```
   User → pulse-hub-web → GitHub OAuth → Callback → JWT Token → Supabase Session
   ```

2. **MCP Request Flow**:
   ```
   Web UI → MCP Server → GitHub API/Supabase → Response → Web UI
   ```

3. **Dashboard Flow**:
   ```
   Web UI → Superset Proxy → Superset Instance → Supabase Query → Dashboard Render
   ```

---

## Deployment Procedure

### Step 1: Update GitHub OAuth App

**Objective**: Configure GitHub OAuth Application with production redirect URI

**Duration**: 5 minutes

#### 1.1 Determine Production URL

```bash
# If app already exists, get current URL
doctl apps get <app-id> --format DefaultIngress

# If creating new app, URL will be assigned after initial deployment
# Format: https://pulse-hub-web-<random-hash>.ondigitalocean.app
```

#### 1.2 Update GitHub OAuth App

1. Navigate to GitHub → Settings → Developer settings → OAuth Apps
2. Select your pulse-hub OAuth application
3. Update Authorization callback URL:
   ```
   https://pulse-hub-web-<hash>.ondigitalocean.app/api/auth/callback/github
   ```
4. Verify Homepage URL matches your production domain
5. Save changes

#### 1.3 Verify OAuth Configuration

```bash
# Test OAuth configuration (after deployment)
curl -I "https://pulse-hub-web-<hash>.ondigitalocean.app/api/auth/signin/github"
# Expected: HTTP 302 redirect to GitHub
```

#### Error Codes

- `OAUTH_REDIRECT_404`: Callback URL mismatch
  - **Cause**: Redirect URI in GitHub doesn't match deployed URL
  - **Fix**: Update GitHub OAuth App settings
  - **Verification**: Re-test OAuth flow

- `OAUTH_CLIENT_INVALID`: Invalid client credentials
  - **Cause**: Client ID or Secret incorrect in environment variables
  - **Fix**: Verify credentials in GitHub OAuth App settings
  - **Verification**: Check env vars match GitHub

---

### Step 2: Configure Service Environment Variables

**Objective**: Set environment-specific configuration for all services

**Duration**: 10 minutes

#### 2.1 Prepare Environment Variables

Create environment variable files for each service:

**pulse-hub-web** (`infra/pulse-hub/web.env`):
```bash
# GitHub OAuth
GITHUB_OAUTH_CLIENT_ID=Ov23liXXXXXXXXXX
GITHUB_OAUTH_CLIENT_SECRET=1234567890abcdef1234567890abcdef12345678
NEXTAUTH_URL=https://pulse-hub-web-<hash>.ondigitalocean.app
NEXTAUTH_SECRET=<random-32-char-secret>

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://<project-ref>.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# Internal Services
MCP_SERVER_URL=https://pulse-hub-mcp.ondigitalocean.app
SUPERSET_PROXY_URL=https://pulse-hub-superset.ondigitalocean.app

# Environment
NODE_ENV=production
LOG_LEVEL=info
```

**pulse-hub-mcp** (`infra/pulse-hub/mcp.env`):
```bash
# Server Configuration
PORT=8080
HOST=0.0.0.0
NODE_ENV=production

# GitHub API
GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Supabase
POSTGRES_URL=postgresql://postgres:[password]@[host]:6543/postgres
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# MCP Configuration
MCP_SERVER_NAME=pulse-hub-mcp
MCP_SERVER_VERSION=1.0.0
LOG_LEVEL=info
```

**pulse-hub-superset** (`infra/pulse-hub/superset.env`):
```bash
# Superset Configuration
SECRET_KEY=<random-secret-key>
SUPERSET_ENV=production

# Database
DATABASE_HOST=aws-0-us-east-1.pooler.supabase.com
DATABASE_PORT=6543
DATABASE_DB=postgres
DATABASE_USER=postgres
DATABASE_PASSWORD=<password>
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://postgres:[password]@[host]:6543/postgres

# Authentication
AUTH_TYPE=DATABASE
AUTH_ROLE_PUBLIC=Viewer

# Server
SUPERSET_WEBSERVER_PORT=8088
SUPERSET_LOAD_EXAMPLES=no
```

#### 2.2 Validate Environment Variables

```bash
# Check for required variables
for env_file in web.env mcp.env superset.env; do
  echo "Validating $env_file..."

  # Check file exists
  if [[ ! -f "infra/pulse-hub/$env_file" ]]; then
    echo "❌ ERROR: $env_file not found"
    exit 1
  fi

  # Check for empty values
  if grep -q "=\s*$" "infra/pulse-hub/$env_file"; then
    echo "⚠️  WARNING: Empty values found in $env_file"
    grep "=\s*$" "infra/pulse-hub/$env_file"
  fi

  # Check for placeholder values
  if grep -qE "=<.*>|=XXXX|=TODO" "infra/pulse-hub/$env_file"; then
    echo "❌ ERROR: Placeholder values found in $env_file"
    grep -E "=<.*>|=XXXX|=TODO" "infra/pulse-hub/$env_file"
    exit 1
  fi

  echo "✅ $env_file validated"
done
```

#### 2.3 Encrypt Secrets (Optional)

```bash
# If using encrypted secrets, encrypt before deployment
# Example using age encryption:
age -e -r <public-key> infra/pulse-hub/web.env > infra/pulse-hub/web.env.age
age -e -r <public-key> infra/pulse-hub/mcp.env > infra/pulse-hub/mcp.env.age
age -e -r <public-key> infra/pulse-hub/superset.env > infra/pulse-hub/superset.env.age
```

#### Error Codes

- `ENV_VAR_PARSE_ERROR`: Environment variable parsing failed
  - **Cause**: Malformed environment variable syntax (missing quotes, special characters)
  - **Fix**: Validate with `bash -n <env-file>` or use single-line format
  - **Example**: `DATABASE_PASSWORD='p@ss"word'` → `DATABASE_PASSWORD=p@ssword`

- `ENV_VAR_MISSING`: Required environment variable not set
  - **Cause**: Missing required configuration
  - **Fix**: Add missing variable to env file
  - **Verification**: Check service startup logs

---

### Step 3: Update App Specification

**Objective**: Configure DigitalOcean App Platform app specification

**Duration**: 5 minutes

#### 3.1 Create/Update App Spec File

Create `infra/pulse-hub/app-spec.yaml`:

```yaml
name: pulse-hub
region: nyc
services:
  # Web Service (Next.js Frontend)
  - name: pulse-hub-web
    github:
      repo: your-org/pulse-hub
      branch: main
      deploy_on_push: true
    dockerfile_path: docker/Dockerfile.web
    build_command: npm run build
    run_command: npm start
    http_port: 3000
    instance_count: 1
    instance_size_slug: basic-xs
    routes:
      - path: /
    envs:
      - key: NODE_ENV
        value: production
      - key: GITHUB_OAUTH_CLIENT_ID
        scope: RUN_TIME
        type: SECRET
      - key: GITHUB_OAUTH_CLIENT_SECRET
        scope: RUN_TIME
        type: SECRET
      - key: NEXTAUTH_SECRET
        scope: RUN_TIME
        type: SECRET
      - key: NEXT_PUBLIC_SUPABASE_URL
        value: https://<project-ref>.supabase.co
      - key: NEXT_PUBLIC_SUPABASE_ANON_KEY
        scope: RUN_TIME
        type: SECRET
      - key: SUPABASE_SERVICE_ROLE_KEY
        scope: RUN_TIME
        type: SECRET
      - key: MCP_SERVER_URL
        value: ${pulse-hub-mcp.PRIVATE_URL}
      - key: SUPERSET_PROXY_URL
        value: ${pulse-hub-superset.PRIVATE_URL}
    health_check:
      http_path: /api/health
      initial_delay_seconds: 30
      period_seconds: 10
      timeout_seconds: 5
      success_threshold: 1
      failure_threshold: 3

  # MCP Server (Internal Service)
  - name: pulse-hub-mcp
    github:
      repo: your-org/pulse-hub
      branch: main
      deploy_on_push: true
    dockerfile_path: docker/Dockerfile.mcp
    build_command: npm run build:mcp
    run_command: npm run start:mcp
    http_port: 8080
    instance_count: 1
    instance_size_slug: basic-xs
    internal_ports:
      - 8080
    envs:
      - key: NODE_ENV
        value: production
      - key: PORT
        value: "8080"
      - key: GITHUB_TOKEN
        scope: RUN_TIME
        type: SECRET
      - key: POSTGRES_URL
        scope: RUN_TIME
        type: SECRET
      - key: SUPABASE_SERVICE_ROLE_KEY
        scope: RUN_TIME
        type: SECRET
      - key: LOG_LEVEL
        value: info
    health_check:
      http_path: /health
      initial_delay_seconds: 20
      period_seconds: 10
      timeout_seconds: 3
      success_threshold: 1
      failure_threshold: 3

  # Superset (BI Dashboard Service)
  - name: pulse-hub-superset
    github:
      repo: your-org/pulse-hub
      branch: main
      deploy_on_push: true
    dockerfile_path: docker/Dockerfile.superset
    build_command: pip install -r requirements/superset.txt
    run_command: gunicorn -b 0.0.0.0:8088 --workers=4 superset.app:create_app()
    http_port: 8088
    instance_count: 1
    instance_size_slug: basic-s
    internal_ports:
      - 8088
    envs:
      - key: SUPERSET_ENV
        value: production
      - key: SUPERSET_WEBSERVER_PORT
        value: "8088"
      - key: SECRET_KEY
        scope: RUN_TIME
        type: SECRET
      - key: SQLALCHEMY_DATABASE_URI
        scope: RUN_TIME
        type: SECRET
      - key: SUPERSET_LOAD_EXAMPLES
        value: "no"
      - key: AUTH_TYPE
        value: DATABASE
    health_check:
      http_path: /health
      initial_delay_seconds: 45
      period_seconds: 15
      timeout_seconds: 10
      success_threshold: 1
      failure_threshold: 3
```

#### 3.2 Validate App Spec

```bash
# Validate YAML syntax
yamllint infra/pulse-hub/app-spec.yaml

# Validate against DigitalOcean schema (if available)
doctl apps spec validate infra/pulse-hub/app-spec.yaml
```

#### 3.3 Update Existing App Spec

If updating an existing app:

```bash
# Get current app ID
APP_ID=$(doctl apps list --format ID,Spec.Name | grep pulse-hub | awk '{print $1}')

# Backup current spec
doctl apps spec get "$APP_ID" > "infra/pulse-hub/app-spec-backup-$(date +%Y%m%d-%H%M%S).yaml"

# Update app spec
doctl apps update "$APP_ID" --spec infra/pulse-hub/app-spec.yaml
```

#### Error Codes

- `PORT_MISMATCH`: Service port mismatch between spec and Dockerfile
  - **Cause**: `http_port` in spec doesn't match `EXPOSE` in Dockerfile
  - **Fix**: Update app-spec.yaml to match Dockerfile EXPOSE directive
  - **Example**: Superset Dockerfile uses 8088, spec must use 8088

- `SPEC_VALIDATION_ERROR`: Invalid app specification
  - **Cause**: YAML syntax error or invalid configuration
  - **Fix**: Run `doctl apps spec validate` and fix errors
  - **Verification**: Re-run validation command

---

### Step 4: Apply Configuration

**Objective**: Deploy configuration changes to DigitalOcean App Platform

**Duration**: 3 minutes

#### 4.1 Update App Configuration

```bash
# Set variables
APP_ID="<your-app-id>"
SPEC_FILE="infra/pulse-hub/app-spec.yaml"

# Update app spec
doctl apps update "$APP_ID" --spec "$SPEC_FILE"

# Output:
# Notice: App updated. Creating new deployment...
# ID                                      Spec Name    Default Ingress    Active Deployment ID
# a1b2c3d4-5678-90ab-cdef-1234567890ab    pulse-hub    pulse-hub-web...   dep-xyz123
```

#### 4.2 Set Environment Secrets

Set secrets that can't be in the spec file:

```bash
# Web service secrets
doctl apps update "$APP_ID" \
  --app-component-name pulse-hub-web \
  --env "GITHUB_OAUTH_CLIENT_SECRET=$GITHUB_OAUTH_CLIENT_SECRET" \
  --env "NEXTAUTH_SECRET=$NEXTAUTH_SECRET" \
  --env "SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY"

# MCP service secrets
doctl apps update "$APP_ID" \
  --app-component-name pulse-hub-mcp \
  --env "GITHUB_TOKEN=$GITHUB_TOKEN" \
  --env "POSTGRES_URL=$POSTGRES_URL" \
  --env "SUPABASE_SERVICE_ROLE_KEY=$SUPABASE_SERVICE_ROLE_KEY"

# Superset service secrets
doctl apps update "$APP_ID" \
  --app-component-name pulse-hub-superset \
  --env "SECRET_KEY=$SUPERSET_SECRET_KEY" \
  --env "SQLALCHEMY_DATABASE_URI=$SUPERSET_DATABASE_URI"
```

#### 4.3 Verify Configuration Applied

```bash
# Check updated spec
doctl apps spec get "$APP_ID" | grep -A 5 "envs:"

# Verify deployment created
doctl apps list-deployments "$APP_ID" --format ID,Phase,Created
```

---

### Step 5: Create Deployment

**Objective**: Trigger new deployment with updated configuration

**Duration**: 15-30 minutes

#### 5.1 Trigger Deployment

```bash
# Force new deployment with rebuild
doctl apps create-deployment "$APP_ID" --force-rebuild

# Output:
# Notice: Creating deployment for app <app-id>
# ID                                      Phase       Created At
# dep-abc123xyz                           PENDING     2025-11-01 14:30:00 +0000 UTC
```

#### 5.2 Monitor Build Phase

```bash
# Watch deployment progress
watch -n 10 "doctl apps get-deployment $APP_ID <deployment-id> --format Phase,Progress"

# Expected phases:
# PENDING_BUILD → BUILDING → PENDING_DEPLOY → DEPLOYING → ACTIVE
```

#### 5.3 Stream Build Logs

```bash
# Stream logs for all services
doctl apps logs "$APP_ID" --follow --type BUILD

# Or per-service logs:
doctl apps logs "$APP_ID" --follow --type BUILD --app-component pulse-hub-web
doctl apps logs "$APP_ID" --follow --type BUILD --app-component pulse-hub-mcp
doctl apps logs "$APP_ID" --follow --type BUILD --app-component pulse-hub-superset
```

#### 5.4 Handle Build Failures

If build fails:

```bash
# Get detailed error
doctl apps get-deployment "$APP_ID" <deployment-id> --format Phase,Progress,Error

# Check build logs for specific error
doctl apps logs "$APP_ID" --type BUILD --app-component <failed-service> | tail -100

# Common fixes:
# - Dockerfile path incorrect: Update dockerfile_path in spec
# - Build command failed: Check build_command and dependencies
# - Environment variables missing: Add to envs in spec
```

---

### Step 6: Monitor Deployment Progress

**Objective**: Track deployment through all phases and verify success

**Duration**: 10-15 minutes

#### 6.1 Watch Deployment Status

```bash
# Real-time status updates
DEPLOYMENT_ID=$(doctl apps list-deployments "$APP_ID" --format ID | head -n 1)

while true; do
  STATUS=$(doctl apps get-deployment "$APP_ID" "$DEPLOYMENT_ID" --format Phase --no-header)
  echo "[$(date '+%H:%M:%S')] Deployment status: $STATUS"

  if [[ "$STATUS" == "ACTIVE" ]]; then
    echo "✅ Deployment succeeded"
    break
  elif [[ "$STATUS" == "ERROR" ]] || [[ "$STATUS" == "CANCELED" ]]; then
    echo "❌ Deployment failed: $STATUS"
    exit 1
  fi

  sleep 10
done
```

#### 6.2 Monitor Service Logs

```bash
# Stream runtime logs for all services
doctl apps logs "$APP_ID" --follow --type RUN

# Per-service monitoring:
# Terminal 1 - Web service
doctl apps logs "$APP_ID" --follow --type RUN --app-component pulse-hub-web

# Terminal 2 - MCP service
doctl apps logs "$APP_ID" --follow --type RUN --app-component pulse-hub-mcp

# Terminal 3 - Superset service
doctl apps logs "$APP_ID" --follow --type RUN --app-component pulse-hub-superset
```

#### 6.3 Check Service Health

```bash
# Wait for health checks to pass
echo "Waiting for services to become healthy..."

# Get service URLs
WEB_URL=$(doctl apps get "$APP_ID" --format DefaultIngress --no-header)
MCP_URL=$(doctl apps get "$APP_ID" --format "Services.Name,Services.InternalPorts" | grep pulse-hub-mcp | awk '{print "https://"$1".ondigitalocean.app"}')

# Check web service health
for i in {1..30}; do
  if curl -sf "$WEB_URL/api/health" | jq -e '.status == "ok"' > /dev/null; then
    echo "✅ Web service healthy"
    break
  fi
  echo "⏳ Waiting for web service... ($i/30)"
  sleep 10
done

# Check MCP service health (requires internal access or proxy)
# Note: MCP is internal-only, health check via DigitalOcean platform
doctl apps get "$APP_ID" --format "Services.Name,Services.Health" | grep pulse-hub-mcp
```

#### Error Codes

- `HEALTH_CHECK_TIMEOUT`: Service health check failed after max retries
  - **Cause**: Service not responding on health endpoint within timeout
  - **Fix**: Check service logs for startup errors, increase initial_delay_seconds
  - **Verification**: `curl -v <service-url>/health`

- `DEPLOYMENT_ROLLBACK`: Deployment automatically rolled back due to health check failures
  - **Cause**: New deployment failed health checks, platform auto-rolled back
  - **Fix**: Review deployment logs, fix issues, redeploy
  - **Verification**: Check previous deployment still active

---

### Step 7: Validate Health Checks (All Services)

**Objective**: Verify all services are healthy and responding correctly

**Duration**: 5 minutes

#### 7.1 Web Service Validation

```bash
# Health check
curl -sf "$WEB_URL/api/health" | jq .
# Expected output:
# {
#   "status": "ok",
#   "timestamp": "2025-11-01T14:45:00.000Z",
#   "services": {
#     "database": "healthy",
#     "mcp": "healthy",
#     "superset": "healthy"
#   }
# }

# OAuth flow test (manual browser test)
open "$WEB_URL/api/auth/signin/github"
# Should redirect to GitHub OAuth authorization page

# Public routes test
curl -I "$WEB_URL" | grep "HTTP/"
# Expected: HTTP/2 200

# API routes test
curl -sf "$WEB_URL/api/version" | jq .
# Expected: {"version": "1.0.0", "build": "..."}
```

#### 7.2 MCP Service Validation

```bash
# MCP service is internal-only, validate via web service proxy or direct internal call

# Option 1: Via web service proxy
curl -sf "$WEB_URL/api/proxy/mcp/health" | jq .
# Expected:
# {
#   "status": "healthy",
#   "server": "pulse-hub-mcp",
#   "version": "1.0.0",
#   "timestamp": "2025-11-01T14:45:00.000Z"
# }

# Option 2: Check DigitalOcean health status
doctl apps get "$APP_ID" --format "Services.Name,Services.Health" | grep pulse-hub-mcp
# Expected: pulse-hub-mcp    HEALTHY

# Verify MCP tools available
curl -sf "$WEB_URL/api/proxy/mcp/tools" | jq '.tools | length'
# Expected: >0 (number of available tools)
```

#### 7.3 Superset Service Validation

```bash
# Superset is internal-only, validate via web service proxy

# Health check via proxy
curl -sf "$WEB_URL/api/proxy/superset/health" | jq .
# Expected:
# {
#   "status": "healthy",
#   "message": "OK"
# }

# Check Superset API availability
curl -sf "$WEB_URL/api/proxy/superset/api/v1/security/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin","provider":"db"}' | jq .
# Expected: {"access_token": "...", "refresh_token": "..."}

# Verify database connection
curl -sf "$WEB_URL/api/proxy/superset/api/v1/database/" \
  -H "Authorization: Bearer <token>" | jq '.count'
# Expected: >0 (number of configured databases)
```

#### 7.4 Integration Tests

```bash
# End-to-end flow test
# 1. Authenticate via GitHub OAuth (manual browser test)
open "$WEB_URL/api/auth/signin/github"

# 2. Test MCP integration (requires authenticated session)
curl -sf "$WEB_URL/api/mcp/execute" \
  -H "Authorization: Bearer <session-token>" \
  -H "Content-Type: application/json" \
  -d '{"tool":"github_issues","params":{"repo":"your-org/pulse-hub"}}' | jq .

# 3. Test Superset dashboard access
curl -sf "$WEB_URL/api/dashboards" \
  -H "Authorization: Bearer <session-token>" | jq '.dashboards | length'

# All should return success responses
```

#### Error Codes

- `SERVICE_UNAVAILABLE`: Service not responding to health checks
  - **Cause**: Service crashed, port mismatch, or startup failure
  - **Fix**: Check logs with `doctl apps logs`, verify port configuration
  - **Verification**: Restart service or redeploy

- `DATABASE_CONNECTION_ERROR`: Cannot connect to Supabase
  - **Cause**: Invalid connection string, network issue, or RLS policy blocking
  - **Fix**: Verify POSTGRES_URL, check Supabase dashboard for connection limits
  - **Verification**: Test with `psql "$POSTGRES_URL" -c "SELECT 1;"`

---

### Step 8: Update Deployment Status

**Objective**: Document deployment completion and notify stakeholders

**Duration**: 5 minutes

#### 8.1 Record Deployment Metadata

```bash
# Get deployment details
DEPLOYMENT_ID=$(doctl apps list-deployments "$APP_ID" --format ID | head -n 1)
DEPLOYMENT_INFO=$(doctl apps get-deployment "$APP_ID" "$DEPLOYMENT_ID" --format Phase,Created,Updated,Cause --no-header)

# Get service URLs
WEB_URL=$(doctl apps get "$APP_ID" --format DefaultIngress --no-header)

# Create deployment record
cat > "deployments/pulse-hub-$(date +%Y%m%d-%H%M%S).json" <<EOF
{
  "app_id": "$APP_ID",
  "deployment_id": "$DEPLOYMENT_ID",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "phase": "ACTIVE",
  "web_url": "$WEB_URL",
  "services": {
    "web": {
      "url": "$WEB_URL",
      "health": "healthy"
    },
    "mcp": {
      "url": "internal",
      "health": "healthy"
    },
    "superset": {
      "url": "internal",
      "health": "healthy"
    }
  },
  "deployer": "$(whoami)",
  "git_commit": "$(git rev-parse HEAD)",
  "git_branch": "$(git rev-parse --abbrev-ref HEAD)"
}
EOF
```

#### 8.2 Update Status Dashboard

```bash
# Update status in task_queue (if integrated with Supabase task bus)
psql "$POSTGRES_URL" -c "
  INSERT INTO task_queue (kind, status, payload, created_at)
  VALUES (
    'DEPLOY_PULSE_HUB',
    'completed',
    '{
      \"app_id\": \"$APP_ID\",
      \"deployment_id\": \"$DEPLOYMENT_ID\",
      \"web_url\": \"$WEB_URL\"
    }'::jsonb,
    NOW()
  );
"
```

#### 8.3 Notify Stakeholders

```bash
# Send deployment notification (example with Slack webhook)
curl -X POST "$SLACK_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"🚀 Pulse-Hub Deployment Complete\",
    \"blocks\": [
      {
        \"type\": \"section\",
        \"text\": {
          \"type\": \"mrkdwn\",
          \"text\": \"*Pulse-Hub Deployment Complete*\n\n• Web: <$WEB_URL|$WEB_URL>\n• Status: ✅ Active\n• Deployer: $(whoami)\n• Timestamp: $(date)\"
        }
      }
    ]
  }"
```

---

## Error Codes and Troubleshooting

### Service-Specific Error Codes

#### Web Service (pulse-hub-web)

**OAUTH_REDIRECT_404**: GitHub OAuth callback returns 404

- **Symptoms**: OAuth flow fails after GitHub authorization
- **Root Cause**: Redirect URI mismatch between GitHub OAuth App and deployed app
- **Diagnosis**:
  ```bash
  # Check configured redirect URI
  curl -I "$WEB_URL/api/auth/callback/github"
  # Should return 405 (Method Not Allowed) not 404

  # Compare with GitHub OAuth App settings
  echo "Configured in GitHub: $(gh api /user/repos | jq -r '.callback_urls[0]')"
  echo "Deployed callback: $WEB_URL/api/auth/callback/github"
  ```
- **Resolution**:
  1. Update GitHub OAuth App redirect URI to match deployed URL
  2. Verify NEXTAUTH_URL environment variable matches deployed URL
  3. Restart web service: `doctl apps create-deployment "$APP_ID"`
- **Prevention**: Use environment variable for redirect URI, update GitHub OAuth App before deployment

**ENV_VAR_PARSE_ERROR**: Environment variable parsing failure

- **Symptoms**: Service crashes on startup with env var error
- **Root Cause**: Special characters in env vars not properly escaped
- **Diagnosis**:
  ```bash
  # Check service logs for parse errors
  doctl apps logs "$APP_ID" --app-component pulse-hub-web --type RUN | grep -i "parse\|syntax"

  # Common issues:
  # - Unescaped special characters: ! $ " ' \ `
  # - Multi-line values without proper quoting
  # - Missing closing quotes
  ```
- **Resolution**:
  1. Re-encode problematic env vars:
     ```bash
     # Use base64 encoding for complex values
     echo -n "complex!value$with@special#chars" | base64
     # Add to spec as: value: <base64-string>
     # Decode in app: process.env.VAR = Buffer.from(process.env.VAR, 'base64').toString()
     ```
  2. Update app spec with encoded values
  3. Redeploy service
- **Prevention**: Use single-line format, escape special characters, or use base64 encoding

#### MCP Service (pulse-hub-mcp)

**PORT_MISMATCH**: Service port mismatch between spec and Dockerfile

- **Symptoms**: Health checks fail, service not reachable on configured port
- **Root Cause**: `http_port` in app spec doesn't match `EXPOSE` directive in Dockerfile
- **Diagnosis**:
  ```bash
  # Check Dockerfile EXPOSE directive
  grep "EXPOSE" docker/Dockerfile.mcp
  # Example output: EXPOSE 8080

  # Check app spec http_port
  grep -A 2 "pulse-hub-mcp:" infra/pulse-hub/app-spec.yaml | grep http_port
  # Example output: http_port: 8080

  # These must match!
  ```
- **Resolution**:
  1. Update app spec to match Dockerfile:
     ```yaml
     - name: pulse-hub-mcp
       http_port: 8080  # Must match Dockerfile EXPOSE
     ```
  2. Or update Dockerfile to match app spec:
     ```dockerfile
     EXPOSE 8080  # Must match app spec http_port
     ```
  3. Rebuild and redeploy
- **Prevention**: Use environment variable for port, set consistently across Dockerfile and app spec

**GITHUB_API_RATE_LIMIT**: GitHub API rate limit exceeded

- **Symptoms**: MCP tools fail with 403 rate limit error
- **Root Cause**: Too many API calls without authenticated token or token with insufficient quota
- **Diagnosis**:
  ```bash
  # Check GitHub API rate limit
  curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/rate_limit | jq .

  # Check MCP service logs
  doctl apps logs "$APP_ID" --app-component pulse-hub-mcp | grep "rate limit"
  ```
- **Resolution**:
  1. Verify GITHUB_TOKEN is set and valid
  2. Wait for rate limit reset (shown in API response)
  3. Implement request caching in MCP service
  4. Use GitHub App authentication (higher rate limits)
- **Prevention**: Cache API responses, use webhooks instead of polling, implement exponential backoff

#### Superset Service (pulse-hub-superset)

**DATABASE_MIGRATION_ERROR**: Superset database migration failed

- **Symptoms**: Superset crashes on startup with migration error
- **Root Cause**: Incomplete or failed database migration
- **Diagnosis**:
  ```bash
  # Check Superset logs for migration errors
  doctl apps logs "$APP_ID" --app-component pulse-hub-superset | grep -i "migration\|upgrade"

  # Connect to database and check migration status
  psql "$POSTGRES_URL" -c "SELECT * FROM alembic_version;"
  ```
- **Resolution**:
  1. SSH into Superset container (if possible) or use job container:
     ```bash
     # Run migration manually
     superset db upgrade
     ```
  2. If migration fails, rollback and retry:
     ```bash
     superset db downgrade
     superset db upgrade
     ```
  3. If still failing, reset Superset schema:
     ```bash
     # WARNING: This deletes all Superset metadata (dashboards, charts, etc.)
     psql "$POSTGRES_URL" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
     superset db upgrade
     superset init
     ```
- **Prevention**: Test migrations in staging, backup database before deployment

**SUPERSET_INIT_TIMEOUT**: Superset initialization timeout

- **Symptoms**: Health checks fail during initial deployment, timeout after 45s
- **Root Cause**: Superset initialization takes longer than health check timeout
- **Diagnosis**:
  ```bash
  # Check if Superset is still initializing
  doctl apps logs "$APP_ID" --app-component pulse-hub-superset | tail -50

  # Look for initialization steps:
  # - Database migration
  # - Default roles creation
  # - Admin user creation
  # - Example data loading (if enabled)
  ```
- **Resolution**:
  1. Increase health check timeout in app spec:
     ```yaml
     health_check:
       initial_delay_seconds: 90  # Increase from 45
       timeout_seconds: 15         # Increase from 10
     ```
  2. Disable example data loading:
     ```yaml
     envs:
       - key: SUPERSET_LOAD_EXAMPLES
         value: "no"  # Ensure set to no
     ```
  3. Optimize startup by pre-warming database schema
- **Prevention**: Use pre-built Superset image with migrations already applied

### Common Deployment Issues

**DEPLOYMENT_TIMEOUT**: Deployment exceeds maximum time limit

- **Symptoms**: Deployment stuck in BUILDING or DEPLOYING phase for >30 minutes
- **Root Cause**: Large Docker image, slow dependencies, or build cache miss
- **Diagnosis**:
  ```bash
  # Check deployment progress
  doctl apps get-deployment "$APP_ID" "$DEPLOYMENT_ID" --format Phase,Progress,Duration

  # Identify slow build steps in logs
  doctl apps logs "$APP_ID" --type BUILD | grep "Step [0-9]*/[0-9]*"
  ```
- **Resolution**:
  1. Cancel stuck deployment:
     ```bash
     doctl apps cancel-deployment "$APP_ID" "$DEPLOYMENT_ID"
     ```
  2. Optimize Dockerfile:
     - Use multi-stage builds
     - Leverage build cache
     - Minimize layer count
  3. Retry deployment with `--force-rebuild`
- **Prevention**: Optimize Dockerfile, use smaller base images, leverage caching

**RESOURCE_QUOTA_EXCEEDED**: DigitalOcean resource limits exceeded

- **Symptoms**: Deployment fails with "quota exceeded" error
- **Root Cause**: Account resource limits reached (apps, droplets, volumes)
- **Diagnosis**:
  ```bash
  # Check current resource usage
  doctl apps list --format ID,Spec.Name,Phase | wc -l

  # Check account limits (requires API access)
  curl -X GET "https://api.digitalocean.com/v2/account" \
    -H "Authorization: Bearer $DIGITALOCEAN_ACCESS_TOKEN" | jq .account
  ```
- **Resolution**:
  1. Delete unused apps:
     ```bash
     doctl apps list --format ID,Spec.Name,Phase
     # Identify inactive apps and delete
     doctl apps delete <app-id>
     ```
  2. Request limit increase from DigitalOcean support
  3. Consolidate services into fewer apps
- **Prevention**: Monitor resource usage, clean up unused apps regularly

---

## Rollback Procedures

### Quick Rollback (Previous Deployment)

**Use when**: Current deployment has critical bugs, need immediate rollback

**Duration**: 5-10 minutes

```bash
# 1. Get previous deployment ID
PREV_DEPLOYMENT=$(doctl apps list-deployments "$APP_ID" --format ID,Phase,Created | grep ACTIVE | tail -n 2 | head -n 1 | awk '{print $1}')

# 2. Verify previous deployment details
doctl apps get-deployment "$APP_ID" "$PREV_DEPLOYMENT" --format Phase,Created,Cause

# 3. Trigger rollback deployment
doctl apps create-deployment "$APP_ID" --deployment-id "$PREV_DEPLOYMENT"

# 4. Monitor rollback progress
watch -n 5 "doctl apps get-deployment $APP_ID <new-deployment-id> --format Phase,Progress"

# 5. Verify rollback success
curl -sf "$WEB_URL/api/health" | jq .
```

### Targeted Rollback (Specific Service)

**Use when**: Only one service has issues, others are healthy

**Duration**: 10-15 minutes

```bash
# Example: Rollback only pulse-hub-mcp service

# 1. Get current app spec
doctl apps spec get "$APP_ID" > current-spec.yaml

# 2. Update only the failing service in spec
# Edit current-spec.yaml to use previous Docker image tag or commit

# 3. Apply updated spec
doctl apps update "$APP_ID" --spec current-spec.yaml

# 4. Trigger deployment with partial rollback
doctl apps create-deployment "$APP_ID"

# 5. Verify service health
doctl apps get "$APP_ID" --format "Services.Name,Services.Health"
```

### Full Rollback (Complete App State)

**Use when**: Multiple services broken, need clean slate

**Duration**: 20-30 minutes

```bash
# 1. Restore previous app spec from backup
BACKUP_SPEC="infra/pulse-hub/app-spec-backup-<timestamp>.yaml"

# 2. Verify backup spec is valid
doctl apps spec validate "$BACKUP_SPEC"

# 3. Update app with backup spec
doctl apps update "$APP_ID" --spec "$BACKUP_SPEC"

# 4. Restore environment variables from backup
# Re-run Step 2.2 commands with previous env var values

# 5. Trigger clean deployment
doctl apps create-deployment "$APP_ID" --force-rebuild

# 6. Validate all services
bash infra/pulse-hub/scripts/validate-deployment.sh
```

### Rollback Verification Checklist

After any rollback:

- [ ] All services show HEALTHY status
- [ ] Web service accessible at production URL
- [ ] GitHub OAuth flow works end-to-end
- [ ] MCP service responds to health checks
- [ ] Superset dashboards load correctly
- [ ] No errors in service logs
- [ ] Database connections stable
- [ ] Monitoring alerts cleared

---

## Health Monitoring

### Continuous Monitoring Setup

#### DigitalOcean Built-in Monitoring

```bash
# View app metrics
doctl apps get "$APP_ID" --format "Services.Name,Services.Health,Services.CPUUsage,Services.MemoryUsage"

# Set up alerts (via DigitalOcean dashboard)
# Navigate to: Apps → pulse-hub → Settings → Alerts
# Configure:
# - Service down alerts
# - High CPU/memory alerts
# - Failed deployment alerts
```

#### External Monitoring (UptimeRobot, Pingdom)

```yaml
# Example UptimeRobot configuration
monitors:
  - name: Pulse-Hub Web
    url: https://pulse-hub-web-<hash>.ondigitalocean.app/api/health
    type: HTTP
    interval: 300  # 5 minutes
    keyword: "status\":\"ok"

  - name: Pulse-Hub OAuth
    url: https://pulse-hub-web-<hash>.ondigitalocean.app/api/auth/signin/github
    type: HTTP
    interval: 600  # 10 minutes
    expected_status: 302
```

#### Custom Health Check Script

```bash
#!/bin/bash
# infra/pulse-hub/scripts/health-check.sh

APP_ID="<your-app-id>"
WEB_URL=$(doctl apps get "$APP_ID" --format DefaultIngress --no-header)

# Check all services
SERVICES=("pulse-hub-web" "pulse-hub-mcp" "pulse-hub-superset")
ALL_HEALTHY=true

for service in "${SERVICES[@]}"; do
  HEALTH=$(doctl apps get "$APP_ID" --format "Services.Name,Services.Health" | grep "$service" | awk '{print $2}')

  if [[ "$HEALTH" != "HEALTHY" ]]; then
    echo "❌ $service is $HEALTH"
    ALL_HEALTHY=false
  else
    echo "✅ $service is healthy"
  fi
done

# Check web endpoint
if curl -sf "$WEB_URL/api/health" | jq -e '.status == "ok"' > /dev/null; then
  echo "✅ Web endpoint responding"
else
  echo "❌ Web endpoint not responding"
  ALL_HEALTHY=false
fi

if $ALL_HEALTHY; then
  exit 0
else
  exit 1
fi
```

#### Automated Monitoring with Cron

```bash
# Add to crontab
# Check health every 5 minutes, alert on failure
*/5 * * * * /path/to/infra/pulse-hub/scripts/health-check.sh || curl -X POST "$SLACK_WEBHOOK_URL" -d '{"text":"⚠️ Pulse-Hub health check failed"}'
```

---

## Security Considerations

### Secrets Management

**Never commit secrets to version control**:

```bash
# Add to .gitignore
echo "*.env" >> .gitignore
echo "*.env.*" >> .gitignore
echo "*-backup-*.yaml" >> .gitignore  # May contain secrets
```

**Use environment variables for all secrets**:
- GitHub OAuth credentials
- Supabase keys
- NextAuth secret
- Database passwords
- API tokens

**Rotate secrets regularly**:
```bash
# Example: Rotate GitHub OAuth secret
# 1. Generate new secret in GitHub OAuth App
# 2. Update environment variable
doctl apps update "$APP_ID" \
  --app-component-name pulse-hub-web \
  --env "GITHUB_OAUTH_CLIENT_SECRET=$NEW_SECRET"
# 3. Deploy changes
doctl apps create-deployment "$APP_ID"
# 4. Revoke old secret in GitHub after verification
```

### Network Security

**Internal services**:
- MCP and Superset are internal-only (no public routes)
- Only accessible via web service proxy or internal DigitalOcean network
- Cannot be accessed directly from internet

**HTTPS enforcement**:
- All external traffic uses HTTPS (DigitalOcean-managed certificates)
- HTTP automatically redirects to HTTPS
- HSTS headers enabled

**CORS configuration**:
```typescript
// Example Next.js CORS config
export const config = {
  api: {
    cors: {
      origin: process.env.ALLOWED_ORIGINS?.split(',') || [],
      methods: ['GET', 'POST'],
      credentials: true,
    },
  },
};
```

### Database Security

**Connection security**:
- Use connection pooler (port 6543) for high-concurrency apps
- Enable SSL for database connections
- Use service role key only in backend services (never in frontend)

**Row Level Security (RLS)**:
```sql
-- Enable RLS on all tables
ALTER TABLE pulse_hub_users ENABLE ROW LEVEL SECURITY;

-- Example RLS policy
CREATE POLICY "Users can only see their own data"
ON pulse_hub_users FOR SELECT
USING (auth.uid() = user_id);
```

### Access Control

**GitHub OAuth scopes**:
- Request minimum required scopes (principle of least privilege)
- For pulse-hub: `repo` (read-only) and `workflow` (Actions access)
- Avoid `admin:*` scopes unless absolutely necessary

**Supabase access levels**:
- Frontend: Use anon key with RLS policies
- Backend: Use service role key only in trusted server environments
- Never expose service role key in client-side code

---

## Appendix

### A. Useful Commands Reference

```bash
# App management
doctl apps list
doctl apps get <app-id>
doctl apps update <app-id> --spec <spec-file>
doctl apps delete <app-id>

# Deployment management
doctl apps list-deployments <app-id>
doctl apps get-deployment <app-id> <deployment-id>
doctl apps create-deployment <app-id> [--force-rebuild]
doctl apps cancel-deployment <app-id> <deployment-id>

# Logs
doctl apps logs <app-id> --type BUILD|RUN [--follow] [--app-component <name>]

# Spec management
doctl apps spec get <app-id>
doctl apps spec validate <spec-file>
```

### B. Environment Variables Checklist

**pulse-hub-web**:
- [ ] GITHUB_OAUTH_CLIENT_ID
- [ ] GITHUB_OAUTH_CLIENT_SECRET
- [ ] NEXTAUTH_URL
- [ ] NEXTAUTH_SECRET
- [ ] NEXT_PUBLIC_SUPABASE_URL
- [ ] NEXT_PUBLIC_SUPABASE_ANON_KEY
- [ ] SUPABASE_SERVICE_ROLE_KEY
- [ ] MCP_SERVER_URL
- [ ] SUPERSET_PROXY_URL

**pulse-hub-mcp**:
- [ ] PORT
- [ ] GITHUB_TOKEN
- [ ] POSTGRES_URL
- [ ] SUPABASE_SERVICE_ROLE_KEY

**pulse-hub-superset**:
- [ ] SECRET_KEY
- [ ] SQLALCHEMY_DATABASE_URI
- [ ] SUPERSET_WEBSERVER_PORT

### C. Deployment Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| Preparation | 15 min | Update OAuth, prepare env vars, validate specs |
| Build | 10-15 min | Docker image builds for all services |
| Deploy | 5-10 min | Deploy containers to App Platform |
| Health Checks | 5 min | Wait for services to become healthy |
| Validation | 5 min | Test all service endpoints |
| Documentation | 5 min | Record deployment metadata |
| **Total** | **45-55 min** | Complete deployment cycle |

### D. Support Resources

- **DigitalOcean App Platform Docs**: https://docs.digitalocean.com/products/app-platform/
- **Supabase Docs**: https://supabase.com/docs
- **GitHub OAuth Docs**: https://docs.github.com/en/developers/apps/oauth-apps
- **Next.js Deployment**: https://nextjs.org/docs/deployment
- **Superset Docs**: https://superset.apache.org/docs/intro

---

**Document Revision History**:

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-01 | Pulse-Hub Team | Initial release |


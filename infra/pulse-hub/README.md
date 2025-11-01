# Pulse-Hub Infrastructure Documentation

**Multi-service architecture on DigitalOcean App Platform with Supabase backend**

**Version**: 1.0.0
**Last Updated**: 2025-11-01
**Status**: ✅ Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Services](#services)
4. [Prerequisites](#prerequisites)
5. [Quick Start](#quick-start)
6. [Deployment Workflow](#deployment-workflow)
7. [Monitoring](#monitoring)
8. [Cost Analysis](#cost-analysis)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### What is Pulse-Hub?

Pulse-Hub is a **GitHub-integrated analytics and workflow management platform** providing:

- **Real-time Insights**: Live dashboards tracking repository activity, issue velocity, PR metrics
- **AI-Powered Tools**: MCP (Model Context Protocol) server for intelligent GitHub operations
- **Business Intelligence**: Apache Superset for custom analytics and reporting
- **Workflow Automation**: Automated notifications, status updates, and developer productivity tracking

### Target Users

- **Development Teams**: Track sprint progress, identify bottlenecks, optimize workflows
- **Engineering Managers**: Monitor team velocity, PR review times, deployment frequency
- **Product Managers**: Analyze feature delivery, customer-reported issues, roadmap progress
- **DevOps Engineers**: Monitor CI/CD pipelines, deployment success rates, infrastructure health

### Key Features

✅ **GitHub OAuth Authentication**: Secure single sign-on with GitHub accounts
✅ **Multi-Service Architecture**: Microservices for web, AI tools, and analytics
✅ **Real-time Data**: Live updates from GitHub via webhooks and polling
✅ **Custom Dashboards**: Build analytics dashboards with Superset
✅ **AI Integration**: MCP server for GitHub automation and intelligent insights
✅ **Cost-Optimized**: <$30/month infrastructure (DigitalOcean + Supabase free tier)

---

## Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Browser                             │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS
                         │
┌────────────────────────▼────────────────────────────────────────┐
│              DigitalOcean App Platform (NYC)                    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  pulse-hub-web (Next.js)                                  │ │
│  │  • Public route: /                                        │ │
│  │  • GitHub OAuth callback                                  │ │
│  │  • API routes: /api/*                                     │ │
│  │  • Port: 3000                                             │ │
│  └────┬──────────────────────────┬───────────────────────────┘ │
│       │                          │                              │
│       │ Internal HTTP            │ Internal HTTP                │
│       │                          │                              │
│  ┌────▼──────────────────┐  ┌───▼──────────────────────────┐  │
│  │ pulse-hub-mcp         │  │ pulse-hub-superset           │  │
│  │ (Node.js MCP Server)  │  │ (Apache Superset)            │  │
│  │ • Internal only       │  │ • Internal only              │  │
│  │ • AI tools for GitHub │  │ • BI dashboards              │  │
│  │ • Port: 8080          │  │ • Port: 8088                 │  │
│  └────┬──────────────────┘  └───┬──────────────────────────┘  │
│       │                          │                              │
└───────┼──────────────────────────┼──────────────────────────────┘
        │                          │
        │ PostgreSQL (pooler:6543) │
        │                          │
┌───────▼──────────────────────────▼──────────────────────────────┐
│              Supabase PostgreSQL (AWS us-east-1)                │
│  • Database: postgres                                           │
│  • Connection pooler: 6543                                      │
│  • RLS policies enabled                                         │
│  • Tables: users, repositories, issues, pull_requests, etc.     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   External Services                             │
│  • GitHub API (authentication, webhooks, data)                  │
│  • GitHub OAuth (user authentication)                           │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

**User Authentication**:
```
User → pulse-hub-web → GitHub OAuth → GitHub API → pulse-hub-web → Supabase Session → User Dashboard
```

**Repository Data Sync**:
```
GitHub Webhook → pulse-hub-web/api/webhooks → Supabase PostgreSQL → Real-time UI Update
```

**MCP Tool Execution**:
```
Web UI → pulse-hub-mcp → GitHub API → Process → Response → Web UI
```

**Analytics Dashboard**:
```
Web UI → pulse-hub-superset Proxy → Superset Query → Supabase → Chart Render → Web UI
```

### Network Architecture

**External Access** (via HTTPS):
- `https://pulse-hub-web-<hash>.ondigitalocean.app` - Public web interface

**Internal Services** (no public routes):
- `pulse-hub-mcp.ondigitalocean.app` - Accessible only within DigitalOcean network
- `pulse-hub-superset.ondigitalocean.app` - Accessible only within DigitalOcean network

**Database Access**:
- Frontend → Supabase Anon Key (RLS enforced)
- Backend → Supabase Service Role Key (RLS bypassed, trusted services only)

---

## Services

### 1. pulse-hub-web (Next.js Frontend)

**Technology Stack**:
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Authentication**: NextAuth.js with GitHub OAuth
- **Styling**: Tailwind CSS
- **State Management**: React Context + Server Components

**Responsibilities**:
- User interface for all features
- GitHub OAuth authentication and session management
- API routes for backend logic
- Proxy to internal MCP and Superset services
- Webhook receivers for GitHub events

**Key Endpoints**:

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Landing page / Dashboard |
| `/api/auth/[...nextauth]` | ALL | NextAuth.js authentication endpoints |
| `/api/auth/callback/github` | GET | GitHub OAuth callback |
| `/api/health` | GET | Service health check |
| `/api/github/*` | ALL | GitHub API proxy endpoints |
| `/api/mcp/*` | ALL | MCP server proxy endpoints |
| `/api/superset/*` | ALL | Superset proxy endpoints |
| `/api/webhooks/github` | POST | GitHub webhook receiver |

**Environment Variables**:

| Variable | Required | Purpose |
|----------|----------|---------|
| `GITHUB_OAUTH_CLIENT_ID` | ✅ | GitHub OAuth App Client ID |
| `GITHUB_OAUTH_CLIENT_SECRET` | ✅ | GitHub OAuth App Client Secret |
| `NEXTAUTH_URL` | ✅ | OAuth callback base URL |
| `NEXTAUTH_SECRET` | ✅ | Session encryption secret |
| `NEXT_PUBLIC_SUPABASE_URL` | ✅ | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✅ | Supabase anonymous key (frontend) |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Supabase service role key (backend) |
| `MCP_SERVER_URL` | ✅ | Internal MCP service URL |
| `SUPERSET_PROXY_URL` | ✅ | Internal Superset service URL |

**Resource Requirements**:
- Instance size: `basic-xs` (512 MB RAM, 1 vCPU)
- Disk: 1 GB (ephemeral)
- Estimated cost: $5/month

### 2. pulse-hub-mcp (MCP Server)

**Technology Stack**:
- **Framework**: Node.js + Express
- **Language**: TypeScript
- **MCP SDK**: @anthropic-ai/mcp-sdk
- **GitHub Integration**: Octokit

**Responsibilities**:
- Expose MCP tools for GitHub operations
- Implement GitHub API wrappers (issues, PRs, repositories)
- Handle authentication and rate limiting
- Process AI-driven GitHub operations

**Available MCP Tools**:

| Tool | Description | Inputs |
|------|-------------|--------|
| `github_list_repos` | List user repositories | `user`, `org`, `limit` |
| `github_get_repo` | Get repository details | `owner`, `repo` |
| `github_list_issues` | List repository issues | `owner`, `repo`, `state`, `labels` |
| `github_create_issue` | Create new issue | `owner`, `repo`, `title`, `body` |
| `github_list_prs` | List pull requests | `owner`, `repo`, `state` |
| `github_get_workflow_runs` | Get Actions workflow runs | `owner`, `repo`, `workflow_id` |

**Environment Variables**:

| Variable | Required | Purpose |
|----------|----------|---------|
| `PORT` | ✅ | Server port (8080) |
| `GITHUB_TOKEN` | ✅ | GitHub Personal Access Token |
| `POSTGRES_URL` | ✅ | Supabase PostgreSQL connection string |
| `SUPABASE_SERVICE_ROLE_KEY` | ✅ | Supabase service role key |
| `LOG_LEVEL` | ❌ | Logging level (default: info) |

**Resource Requirements**:
- Instance size: `basic-xs` (512 MB RAM, 1 vCPU)
- Disk: 1 GB (ephemeral)
- Estimated cost: $5/month

### 3. pulse-hub-superset (Apache Superset)

**Technology Stack**:
- **Framework**: Apache Superset 3.x
- **Language**: Python 3.10+
- **Database**: PostgreSQL (Supabase)
- **Web Server**: Gunicorn

**Responsibilities**:
- Business intelligence dashboards
- Custom SQL queries on Supabase data
- Chart and visualization creation
- Dashboard sharing and permissions

**Pre-built Dashboards**:

| Dashboard | Description | Metrics |
|-----------|-------------|---------|
| Repository Overview | High-level repository health | Stars, forks, open issues, active contributors |
| Issue Velocity | Issue creation and resolution trends | Created vs closed, average time to close, labels distribution |
| PR Analytics | Pull request metrics | Open vs merged, review time, merge frequency |
| Team Performance | Developer productivity metrics | Commits per day, PR review latency, code review participation |
| Actions Monitor | GitHub Actions CI/CD metrics | Workflow runs, success rate, duration trends |

**Environment Variables**:

| Variable | Required | Purpose |
|----------|----------|---------|
| `SECRET_KEY` | ✅ | Flask secret key for sessions |
| `SQLALCHEMY_DATABASE_URI` | ✅ | PostgreSQL connection string |
| `SUPERSET_WEBSERVER_PORT` | ✅ | Server port (8088) |
| `SUPERSET_ENV` | ✅ | Environment (production) |
| `SUPERSET_LOAD_EXAMPLES` | ❌ | Load example data (default: no) |

**Resource Requirements**:
- Instance size: `basic-s` (1 GB RAM, 1 vCPU) - Superset requires more memory
- Disk: 2 GB (ephemeral)
- Estimated cost: $12/month

---

## Prerequisites

### Required Accounts

1. **DigitalOcean Account**
   - Active account with billing enabled
   - App Platform access
   - Estimated cost: $22/month for all services

2. **GitHub Account**
   - Personal or organization account
   - Admin access to create OAuth Apps
   - Personal Access Token (PAT) with `repo` and `workflow` scopes

3. **Supabase Account**
   - Free tier available (sufficient for development/small teams)
   - PostgreSQL database created
   - Connection pooler enabled (recommended for App Platform)

### Required Tools

**Local Development**:
```bash
# Node.js 18+ (for local development)
brew install node@18

# DigitalOcean CLI
brew install doctl
doctl auth init

# Git
git --version

# PostgreSQL client (for database operations)
brew install postgresql
```

**Optional Tools**:
```bash
# GitHub CLI (for OAuth App management)
brew install gh

# jq (for JSON parsing in scripts)
brew install jq

# Supabase CLI (for local development)
brew install supabase/tap/supabase
```

### Access Verification

```bash
# Verify DigitalOcean access
doctl apps list

# Verify GitHub access
gh auth status

# Verify Supabase connection
psql "$POSTGRES_URL" -c "SELECT version();"
```

---

## Quick Start

### Step 1: Clone Repository

```bash
# Clone pulse-hub repository
git clone https://github.com/your-org/pulse-hub.git
cd pulse-hub

# Checkout infrastructure branch (or main)
git checkout main
```

### Step 2: Create GitHub OAuth App

Follow the detailed guide: [docs/GITHUB_OAUTH_SETUP.md](../../docs/GITHUB_OAUTH_SETUP.md)

**Quick setup**:
1. Navigate to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in details:
   - Name: `Pulse-Hub`
   - Homepage URL: `https://pulse-hub-web-<hash>.ondigitalocean.app` (update after deployment)
   - Callback URL: `https://pulse-hub-web-<hash>.ondigitalocean.app/api/auth/callback/github`
4. Save Client ID and Client Secret

### Step 3: Configure Environment Variables

```bash
# Copy environment variable templates
cp infra/pulse-hub/web.env.example infra/pulse-hub/web.env
cp infra/pulse-hub/mcp.env.example infra/pulse-hub/mcp.env
cp infra/pulse-hub/superset.env.example infra/pulse-hub/superset.env

# Edit each file with your credentials
nano infra/pulse-hub/web.env
nano infra/pulse-hub/mcp.env
nano infra/pulse-hub/superset.env

# Verify no placeholder values remain
grep -r "XXXX\|TODO\|<.*>" infra/pulse-hub/*.env
# Should return nothing
```

### Step 4: Validate Configuration

```bash
# Validate app specification
doctl apps spec validate infra/pulse-hub/app-spec.yaml

# Check environment variable completeness
bash infra/pulse-hub/scripts/validate-env.sh
```

### Step 5: Deploy to DigitalOcean

```bash
# Create new app from spec
doctl apps create --spec infra/pulse-hub/app-spec.yaml

# Or update existing app
APP_ID="<your-app-id>"
doctl apps update "$APP_ID" --spec infra/pulse-hub/app-spec.yaml

# Trigger deployment
doctl apps create-deployment "$APP_ID" --force-rebuild

# Monitor deployment progress
watch -n 10 "doctl apps list-deployments $APP_ID --format Phase,Progress"
```

### Step 6: Configure GitHub OAuth Callback

After deployment completes:

```bash
# Get deployed URL
WEB_URL=$(doctl apps get "$APP_ID" --format DefaultIngress --no-header)
echo "Deployed URL: $WEB_URL"

# Update GitHub OAuth App with actual callback URL:
# Callback URL: $WEB_URL/api/auth/callback/github
```

### Step 7: Verify Deployment

```bash
# Health check
curl -sf "$WEB_URL/api/health" | jq .

# Test OAuth flow (manual browser test)
open "$WEB_URL"
# Click "Sign in with GitHub"
# Should complete authentication successfully
```

**Total deployment time**: 20-30 minutes

---

## Deployment Workflow

### Development → Staging → Production

**Development**:
```bash
# Local development with Supabase local
supabase start
npm run dev

# Access at http://localhost:3000
# Uses development GitHub OAuth App
```

**Staging** (DigitalOcean App Platform):
```bash
# Deploy to staging app
doctl apps update "$STAGING_APP_ID" --spec infra/pulse-hub/app-spec.staging.yaml
doctl apps create-deployment "$STAGING_APP_ID"

# Run smoke tests
bash infra/pulse-hub/scripts/smoke-test.sh "$STAGING_URL"
```

**Production** (DigitalOcean App Platform):
```bash
# Deploy to production app
doctl apps update "$PROD_APP_ID" --spec infra/pulse-hub/app-spec.yaml
doctl apps create-deployment "$PROD_APP_ID"

# Validate health
bash infra/pulse-hub/scripts/validate-deployment.sh
```

### CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy-pulse-hub.yml
name: Deploy Pulse-Hub

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Update app spec
        run: |
          doctl apps update ${{ secrets.APP_ID }} --spec infra/pulse-hub/app-spec.yaml

      - name: Create deployment
        run: |
          doctl apps create-deployment ${{ secrets.APP_ID }} --wait

      - name: Validate deployment
        run: |
          bash infra/pulse-hub/scripts/validate-deployment.sh
```

### Rollback Procedure

**Quick rollback** (previous deployment):
```bash
# List deployments
doctl apps list-deployments "$APP_ID" --format ID,Phase,Created

# Get previous ACTIVE deployment ID
PREV_DEPLOYMENT=$(doctl apps list-deployments "$APP_ID" --format ID,Phase | grep ACTIVE | tail -n 2 | head -n 1 | awk '{print $1}')

# Rollback to previous deployment
doctl apps create-deployment "$APP_ID" --deployment-id "$PREV_DEPLOYMENT"
```

**Full rollback** (app spec + environment):
```bash
# Restore from backup
doctl apps update "$APP_ID" --spec infra/pulse-hub/app-spec-backup-<timestamp>.yaml

# Redeploy
doctl apps create-deployment "$APP_ID" --force-rebuild
```

---

## Monitoring

### DigitalOcean Built-in Monitoring

**Access metrics**:
- Navigate to: Apps → pulse-hub → Insights
- Metrics available:
  - CPU usage (per service)
  - Memory usage (per service)
  - Request rate (web service)
  - Response time (web service)
  - Error rate (web service)

**Set up alerts**:
- Navigate to: Apps → pulse-hub → Settings → Alerts
- Configure:
  - Service down alerts (notify immediately)
  - High CPU alerts (>80% for 5 minutes)
  - High memory alerts (>85% for 5 minutes)
  - Failed deployment alerts

### Health Check Endpoints

**Web service**:
```bash
curl -sf https://pulse-hub-web-<hash>.ondigitalocean.app/api/health
# Expected:
# {
#   "status": "ok",
#   "timestamp": "2025-11-01T14:30:00.000Z",
#   "services": {
#     "database": "healthy",
#     "mcp": "healthy",
#     "superset": "healthy"
#   }
# }
```

**MCP service** (via proxy):
```bash
curl -sf https://pulse-hub-web-<hash>.ondigitalocean.app/api/proxy/mcp/health
# Expected: {"status": "healthy", "server": "pulse-hub-mcp"}
```

**Superset service** (via proxy):
```bash
curl -sf https://pulse-hub-web-<hash>.ondigitalocean.app/api/proxy/superset/health
# Expected: {"status": "healthy"}
```

### External Monitoring (UptimeRobot)

```yaml
# UptimeRobot configuration
monitors:
  - name: Pulse-Hub Web
    url: https://pulse-hub-web-<hash>.ondigitalocean.app/api/health
    type: HTTP
    interval: 300  # 5 minutes
    keyword: "status\":\"ok"
    alert_contacts:
      - email: devops@yourcompany.com
      - slack: <webhook-url>

  - name: Pulse-Hub OAuth
    url: https://pulse-hub-web-<hash>.ondigitalocean.app/api/auth/signin/github
    type: HTTP
    interval: 600  # 10 minutes
    expected_status: 302
```

### Logging

**View service logs**:
```bash
# Web service logs
doctl apps logs "$APP_ID" --app-component pulse-hub-web --follow

# MCP service logs
doctl apps logs "$APP_ID" --app-component pulse-hub-mcp --follow

# Superset service logs
doctl apps logs "$APP_ID" --app-component pulse-hub-superset --follow

# Build logs
doctl apps logs "$APP_ID" --type BUILD
```

**Log aggregation** (future enhancement):
- Send logs to external service (Logtail, Datadog, New Relic)
- Implement structured logging with request IDs
- Set up log retention policies

---

## Cost Analysis

### DigitalOcean App Platform

| Service | Instance Size | RAM | vCPU | Cost/Month |
|---------|--------------|-----|------|------------|
| pulse-hub-web | basic-xs | 512 MB | 1 | $5.00 |
| pulse-hub-mcp | basic-xs | 512 MB | 1 | $5.00 |
| pulse-hub-superset | basic-s | 1 GB | 1 | $12.00 |
| **Total** | - | **2 GB** | **3** | **$22.00** |

### Supabase

| Tier | Database Size | Bandwidth | Cost/Month |
|------|--------------|-----------|------------|
| Free | Up to 500 MB | 2 GB egress | $0.00 |
| Pro (if needed) | Up to 8 GB | 50 GB egress | $25.00 |

**Current usage estimate** (small team, <50 users):
- Database size: ~200 MB (repositories, issues, PRs metadata)
- Bandwidth: ~1 GB/month (API queries, dashboard loads)
- **Recommendation**: Free tier sufficient

### External Services

| Service | Usage | Cost/Month |
|---------|-------|------------|
| GitHub API | 5000 req/hour (per user) | $0.00 (included) |
| UptimeRobot | 50 monitors | $0.00 (free tier) |
| **Total External** | - | **$0.00** |

### Total Infrastructure Cost

**Development/Small Team** (<50 users):
- DigitalOcean: $22/month
- Supabase: $0/month (free tier)
- External: $0/month
- **Total: $22/month**

**Production/Medium Team** (50-200 users):
- DigitalOcean: $22/month (may need to scale up instance sizes)
- Supabase: $25/month (Pro tier for more storage/bandwidth)
- External: $0/month
- **Total: $47/month**

**Scaling considerations**:
- At >200 users, consider scaling to `basic-s` or `basic-m` instances
- At >1000 users, consider dedicated PostgreSQL (not Supabase)
- Monitor and optimize database queries to reduce bandwidth costs

---

## Troubleshooting

### Common Issues

#### Issue: "Cannot connect to Supabase"

**Symptoms**: Database connection errors, 500 errors on API routes

**Diagnosis**:
```bash
# Test database connection
psql "$POSTGRES_URL" -c "SELECT 1;"

# Check if using connection pooler (port 6543)
echo "$POSTGRES_URL" | grep -o ":[0-9]*"
# Should show: :6543 (not :5432)

# Verify environment variable in deployment
doctl apps logs "$APP_ID" --app-component pulse-hub-web | grep POSTGRES_URL
```

**Solutions**:
1. Use connection pooler (port 6543) not direct connection (port 5432)
2. Verify Supabase project is active (not paused)
3. Check RLS policies allow service access
4. Ensure service role key is correct

#### Issue: "OAuth redirect fails"

**Symptoms**: After GitHub authorization, redirect fails with 404 or error

**Diagnosis**:
```bash
# Check configured callback URL
WEB_URL=$(doctl apps get "$APP_ID" --format DefaultIngress --no-header)
echo "Expected callback: $WEB_URL/api/auth/callback/github"

# Compare with GitHub OAuth App settings
gh api /user/applications | jq '.[].callback_urls'
```

**Solutions**:
1. Update GitHub OAuth App callback URL to match deployed URL
2. Update NEXTAUTH_URL environment variable
3. Redeploy application

See detailed troubleshooting: [knowledge/sop/DEPLOY_PULSE_HUB.md](../../knowledge/sop/DEPLOY_PULSE_HUB.md#troubleshooting)

### Debug Mode

Enable debug logging:

```bash
# Enable debug for web service
doctl apps update "$APP_ID" \
  --app-component-name pulse-hub-web \
  --env "NEXTAUTH_DEBUG=true" \
  --env "LOG_LEVEL=debug"

# Enable debug for MCP service
doctl apps update "$APP_ID" \
  --app-component-name pulse-hub-mcp \
  --env "LOG_LEVEL=debug"

# Redeploy
doctl apps create-deployment "$APP_ID"

# View debug logs
doctl apps logs "$APP_ID" --follow
```

### Support Resources

- **DigitalOcean Support**: https://cloud.digitalocean.com/support
- **Supabase Support**: https://supabase.com/support
- **GitHub Support**: https://support.github.com/
- **Internal Documentation**:
  - [Deployment SOP](../../knowledge/sop/DEPLOY_PULSE_HUB.md)
  - [OAuth Setup Guide](../../docs/GITHUB_OAUTH_SETUP.md)
  - [Architecture Diagrams](./architecture/)

---

## Next Steps

### Post-Deployment Tasks

1. **Set up monitoring alerts**:
   - Configure DigitalOcean alerts for service downtime
   - Set up UptimeRobot or similar external monitoring
   - Configure Slack/email notifications

2. **Create initial Superset dashboards**:
   - Connect Superset to Supabase database
   - Import pre-built dashboard templates
   - Create custom dashboards for your team

3. **Configure GitHub webhooks** (optional):
   - Set up webhooks for real-time updates
   - Configure webhook secret for security
   - Test webhook delivery

4. **Team onboarding**:
   - Share production URL with team
   - Document login process (GitHub OAuth)
   - Create user guides for dashboard usage

### Enhancement Opportunities

**Short-term** (1-2 weeks):
- [ ] Implement caching layer (Redis) for GitHub API responses
- [ ] Add rate limiting to prevent API abuse
- [ ] Create custom error pages (404, 500)
- [ ] Implement user preferences and settings

**Medium-term** (1-2 months):
- [ ] Add Slack integration for notifications
- [ ] Implement email notifications for important events
- [ ] Create mobile-responsive dashboards
- [ ] Add data export functionality (CSV, JSON)

**Long-term** (3-6 months):
- [ ] Implement multi-tenant support (multiple organizations)
- [ ] Add custom webhook triggers and automations
- [ ] Create marketplace for community dashboards
- [ ] Implement advanced analytics and predictive insights

---

## Appendix

### A. Directory Structure

```
infra/pulse-hub/
├── README.md                    # This file
├── app-spec.yaml                # Production app specification
├── app-spec.staging.yaml        # Staging app specification
├── web.env.example              # Web service env template
├── mcp.env.example              # MCP service env template
├── superset.env.example         # Superset service env template
├── scripts/
│   ├── validate-env.sh          # Environment validation
│   ├── validate-deployment.sh   # Deployment validation
│   ├── smoke-test.sh            # Smoke testing
│   └── health-check.sh          # Health monitoring
└── architecture/
    ├── network-diagram.png      # Network architecture diagram
    ├── data-flow.png            # Data flow diagram
    └── service-dependencies.png # Service dependency graph
```

### B. Useful Commands

```bash
# App management
doctl apps list                                      # List all apps
doctl apps get <app-id>                              # Get app details
doctl apps update <app-id> --spec <spec-file>        # Update app spec
doctl apps delete <app-id>                           # Delete app

# Deployment management
doctl apps list-deployments <app-id>                 # List deployments
doctl apps create-deployment <app-id> [--force-rebuild] # Create deployment
doctl apps get-deployment <app-id> <deployment-id>   # Get deployment details

# Logs
doctl apps logs <app-id> --follow                    # Stream all logs
doctl apps logs <app-id> --app-component <name>      # Service-specific logs
doctl apps logs <app-id> --type BUILD                # Build logs

# Environment variables
doctl apps update <app-id> --app-component <name> --env "KEY=value"

# Spec management
doctl apps spec get <app-id>                         # Get current spec
doctl apps spec validate <spec-file>                 # Validate spec file
```

### C. Environment Variables Reference

See detailed reference in:
- [knowledge/sop/DEPLOY_PULSE_HUB.md](../../knowledge/sop/DEPLOY_PULSE_HUB.md#step-2-configure-service-environment-variables)
- [docs/GITHUB_OAUTH_SETUP.md](../../docs/GITHUB_OAUTH_SETUP.md#environment-variable-mapping)

### D. Related Documentation

- **Deployment SOP**: [knowledge/sop/DEPLOY_PULSE_HUB.md](../../knowledge/sop/DEPLOY_PULSE_HUB.md)
- **OAuth Setup**: [docs/GITHUB_OAUTH_SETUP.md](../../docs/GITHUB_OAUTH_SETUP.md)
- **Project README**: [README.md](../../README.md)

---

**Document Revision History**:

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-01 | Pulse-Hub Team | Initial release |

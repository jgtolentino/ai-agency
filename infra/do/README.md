# DigitalOcean App Platform Deployment

This directory contains DigitalOcean App Platform specifications for deploying Odoo custom modules.

## Overview

- **Platform**: DigitalOcean App Platform
- **Container Registry**: DigitalOcean Container Registry (DOCR)
- **Database**: Managed PostgreSQL
- **Environments**: Staging, Production

## Files

- `app-spec-staging.yaml`: Staging environment configuration
- `app-spec-production.yaml`: Production environment configuration

## Prerequisites

1. **DigitalOcean Account**
   - Sign up at https://cloud.digitalocean.com

2. **doctl CLI**
   ```bash
   # Install on macOS
   brew install doctl

   # Authenticate
   doctl auth init
   ```

3. **Container Registry**
   ```bash
   # Create registry (one-time)
   doctl registry create insightpulse --region nyc3

   # Login to registry
   doctl registry login
   ```

4. **GitHub Secrets**
   Set the following secrets in your repository:
   - `DO_ACCESS_TOKEN`: DigitalOcean API token
   - `DO_REGISTRY_TOKEN`: Registry access token (same as DO_ACCESS_TOKEN)
   - `DO_APP_ID_STAGING`: Staging app ID
   - `DO_APP_ID_PROD`: Production app ID

## Initial Setup

### 1. Create Apps

```bash
# Create staging app
doctl apps create --spec infra/do/app-spec-staging.yaml

# Create production app
doctl apps create --spec infra/do/app-spec-production.yaml
```

### 2. Get App IDs

```bash
# List all apps
doctl apps list

# Get specific app ID
doctl apps list --format ID,Name
```

### 3. Set GitHub Secrets

```bash
# In GitHub repository settings > Secrets and variables > Actions
# Add the following:
DO_ACCESS_TOKEN=<your_do_token>
DO_REGISTRY_TOKEN=<your_do_token>
DO_APP_ID_STAGING=<staging_app_id>
DO_APP_ID_PROD=<production_app_id>
```

## Deployment Workflow

### Automated (GitHub Actions)

1. **Push to main/staging branch**: Triggers CI build and Docker image push
2. **Manual deployment**: Go to Actions > Deploy to DigitalOcean > Run workflow
3. **Automatic rollback**: On health check failure

### Manual Deployment

```bash
# Deploy to staging
./scripts/deploy_do.sh staging latest

# Deploy to production with specific tag
./scripts/deploy_do.sh production v1.2.3
```

## App Spec Configuration

### Key Components

#### Image Configuration
```yaml
image:
  registry_type: DOCR
  registry: insightpulse
  repository: odoo
  tag: latest  # Updated by CI/CD
```

#### Health Check
```yaml
health_check:
  http_path: /web/health
  initial_delay_seconds: 60
  period_seconds: 10
  timeout_seconds: 5
```

#### Environment Variables
```yaml
envs:
  - key: POSTGRES_HOST
    value: ${db.HOSTNAME}  # Auto-injected from database
    type: SECRET
```

### Scaling Configuration

**Staging**:
- Instance count: 1
- Instance size: `basic-xxs` ($5/month)
- Total: ~$5/month + database

**Production**:
- Instance count: 2 (high availability)
- Instance size: `professional-xs` ($12/month each)
- Total: ~$24/month + database

## Database Management

### Managed PostgreSQL

- **Version**: PostgreSQL 15
- **Backups**: Automatic daily backups
- **Connection pooling**: Built-in

### Connection Details

Automatically injected as environment variables:
- `${db.HOSTNAME}`
- `${db.PORT}`
- `${db.DATABASE}`
- `${db.USERNAME}`
- `${db.PASSWORD}`

## Monitoring

### App Metrics

```bash
# View app metrics
doctl apps list-metrics <app-id>

# View deployment logs
doctl apps logs <app-id> --follow
```

### Alerts

Configured alerts:
- Deployment failures
- Domain configuration failures
- CPU utilization (production only)
- Memory utilization (production only)

## Rollback

### Automated Rollback

Triggered automatically on health check failure during deployment.

### Manual Rollback

```bash
# Via GitHub Actions
# Go to Actions > Rollback Deployment > Run workflow

# Via CLI
# 1. List recent deployments
doctl apps list-deployments <app-id>

# 2. Get previous deployment spec
doctl apps get-deployment <app-id> <deployment-id>

# 3. Update app spec with previous image tag
# Edit app-spec-{environment}.yaml

# 4. Deploy
./scripts/deploy_do.sh <environment> <previous-tag>
```

## Troubleshooting

### Deployment Failed

```bash
# Check deployment logs
doctl apps logs <app-id> --type BUILD --follow

# Check runtime logs
doctl apps logs <app-id> --type RUN --follow

# Get deployment details
doctl apps get-deployment <app-id> <deployment-id>
```

### Database Connection Issues

```bash
# Check database status
doctl databases list

# Get connection details
doctl databases connection <database-id>

# Check database logs
doctl databases logs <database-id>
```

### Health Check Failures

```bash
# Run health check manually
./scripts/health_check.sh https://<app-url>

# Check app endpoint
curl https://<app-url>/web/health
```

## Cost Optimization

### Staging
- Use `basic-xxs` instance ($5/month)
- Single instance
- Non-production database

### Production
- Use `professional-xs` for high availability
- 2 instances for redundancy
- Production database with backups

### Total Estimated Costs

**Staging**: ~$12/month
- App Platform: $5
- Database (basic): $7

**Production**: ~$32/month
- App Platform: $24 (2 instances)
- Database (basic): $7-15

## Security

### Secrets Management

1. **Never commit secrets** to repository
2. **Use DO App Platform secrets** for sensitive values
3. **Rotate tokens regularly**

### Network Security

1. **HTTPS only**: Automatic SSL certificates
2. **Database**: Private network only
3. **Firewall**: Configure allowed IPs if needed

## References

- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [App Spec Reference](https://docs.digitalocean.com/products/app-platform/reference/app-spec/)
- [doctl CLI Reference](https://docs.digitalocean.com/reference/doctl/)
- [Pricing Calculator](https://www.digitalocean.com/pricing/app-platform)

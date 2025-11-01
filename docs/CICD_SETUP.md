# CI/CD Setup Guide

Complete guide for GitHub Actions CI/CD automation with DigitalOcean App Platform deployment.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)

## Overview

This project uses GitHub Actions for continuous integration and deployment to DigitalOcean App Platform.

### Key Features

- ✅ Automated linting and testing
- ✅ Docker image building and registry push
- ✅ Blue-green deployment support
- ✅ Automated health checks
- ✅ Automatic rollback on failure
- ✅ Manual rollback workflow

## Architecture

```
┌─────────────────┐
│   Git Push      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   GitHub        │
│   Actions       │
│   (CI)          │
└────────┬────────┘
         │
         ├─ Lint & Test
         ├─ Build Docker Image
         └─ Push to DOCR
         │
         ▼
┌─────────────────┐
│   Manual        │
│   Trigger       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Deploy        │
│   Workflow      │
└────────┬────────┘
         │
         ├─ Update App Spec
         ├─ Create Deployment
         ├─ Wait for Completion
         └─ Health Check
         │
         ▼
    ┌─────────┐
    │ Success │
    └─────────┘
         │
    ┌────┴────┐
    │ Failure │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│   Automatic     │
│   Rollback      │
└─────────────────┘
```

## Workflows

### 1. Odoo CI (`odoo-ci.yml`)

**Triggers**:
- Pull requests
- Push to `main`, `staging`, `develop` branches

**Jobs**:

#### lint-and-test
- Python setup (3.11)
- Install dependencies
- Pre-commit hooks
- Ruff linting
- Black formatting check
- isort import sorting
- Flake8 linting
- pylint-odoo (OCA compliance)
- XML validation
- pytest with coverage
- Secrets detection

#### docker-build
- Docker Buildx setup
- Hadolint (Dockerfile linting)
- Docker image build
- Image testing
- Push to DOCR (on main/staging only)

#### quality-gate
- Final validation
- Deployment readiness check

### 2. Deploy (`deploy.yml`)

**Triggers**:
- Manual workflow dispatch
- Repository dispatch events

**Inputs**:
- `environment`: staging or production
- `image_tag`: Docker image tag (default: latest)

**Steps**:
1. Install doctl CLI
2. Get app ID for environment
3. Update app spec with image tag
4. Create deployment
5. Wait for completion
6. Run health checks
7. Trigger rollback on failure
8. Send webhook notification

### 3. Rollback (`rollback.yml`)

**Triggers**:
- Manual workflow dispatch
- Automated (on deployment failure)

**Inputs**:
- `environment`: staging or production
- `target_tag`: Image tag to rollback to (optional)
- `reason`: Rollback reason (required)

**Steps**:
1. Install doctl CLI
2. Get previous deployment
3. Extract previous image tag
4. Update app spec
5. Create rollback deployment
6. Wait for completion
7. Verify health
8. Create incident report

## Setup Instructions

### Prerequisites

1. **DigitalOcean Account**
   - Create account at https://cloud.digitalocean.com
   - Generate API token

2. **Container Registry**
   ```bash
   doctl registry create insightpulse --region nyc3
   ```

3. **Create Apps**
   ```bash
   # Staging
   doctl apps create --spec infra/do/app-spec-staging.yaml

   # Production
   doctl apps create --spec infra/do/app-spec-production.yaml
   ```

### GitHub Secrets

Configure the following secrets in GitHub repository settings:

#### Required Secrets

| Secret | Description | How to Get |
|--------|-------------|------------|
| `DO_ACCESS_TOKEN` | DigitalOcean API token | Settings > API > Generate New Token |
| `DO_REGISTRY_TOKEN` | Registry access token | Same as `DO_ACCESS_TOKEN` |
| `DO_APP_ID_STAGING` | Staging app ID | `doctl apps list` |
| `DO_APP_ID_PROD` | Production app ID | `doctl apps list` |

#### Optional Secrets

| Secret | Description | Required For |
|--------|-------------|--------------|
| `ODOO_WEBHOOK_URL` | Webhook endpoint for notifications | Deployment notifications |
| `PULSER_WEBHOOK_SECRET` | Webhook signature secret | Webhook authentication |

### Setting Secrets

```bash
# Via GitHub CLI
gh secret set DO_ACCESS_TOKEN
gh secret set DO_REGISTRY_TOKEN
gh secret set DO_APP_ID_STAGING
gh secret set DO_APP_ID_PROD

# Or via GitHub Web UI
# Repository > Settings > Secrets and variables > Actions > New repository secret
```

### Environment Configuration

Create GitHub environments for enhanced security:

1. **Create Environments**:
   - Go to Repository > Settings > Environments
   - Create `staging` and `production` environments

2. **Configure Protection Rules** (Production):
   - Required reviewers: 1+
   - Wait timer: 5 minutes
   - Deployment branches: `main` only

## Usage

### Continuous Integration

Automatic on every push/PR:

```bash
git push origin feature-branch
# Triggers lint-and-test job
# Checks code quality and runs tests
```

### Deploying to Staging

#### Via GitHub Actions UI

1. Go to **Actions** tab
2. Select **Deploy to DigitalOcean** workflow
3. Click **Run workflow**
4. Select:
   - Environment: `staging`
   - Image tag: `latest` (or specific tag)
5. Click **Run workflow**

#### Via GitHub CLI

```bash
gh workflow run deploy.yml \
  -f environment=staging \
  -f image_tag=latest
```

#### Via Script

```bash
./scripts/deploy_do.sh staging latest
```

### Deploying to Production

#### Via GitHub Actions UI

1. Go to **Actions** tab
2. Select **Deploy to DigitalOcean** workflow
3. Click **Run workflow**
4. Select:
   - Environment: `production`
   - Image tag: `v1.2.3` (use specific tag)
5. Click **Run workflow**
6. Approve deployment (if protection rules configured)

#### Via Script

```bash
./scripts/deploy_do.sh production v1.2.3
```

### Manual Rollback

#### Via GitHub Actions UI

1. Go to **Actions** tab
2. Select **Rollback Deployment** workflow
3. Click **Run workflow**
4. Fill in:
   - Environment: `staging` or `production`
   - Target tag: (optional, defaults to previous)
   - Reason: "Description of why rolling back"
5. Click **Run workflow**

#### Via GitHub CLI

```bash
gh workflow run rollback.yml \
  -f environment=production \
  -f reason="Critical bug in v1.2.3"
```

### Health Checks

#### Automatic

Health checks run automatically after every deployment.

#### Manual

```bash
# Using wrapper script
./scripts/health_check.sh https://odoo-staging.example.com

# Using Python script directly
python scripts/health_check.py \
  --target blue \
  --url https://odoo-staging.example.com \
  --timeout 30 \
  --json-output health_results.json
```

## Monitoring

### Deployment Status

```bash
# List recent deployments
doctl apps list-deployments <app-id>

# Get deployment details
doctl apps get-deployment <app-id> <deployment-id>

# View logs
doctl apps logs <app-id> --follow
```

### GitHub Actions

1. Go to **Actions** tab
2. Click on workflow run
3. View logs for each job

### Notifications

Configure webhook notifications for:
- Deployment success
- Deployment failure
- Rollback completion

## Troubleshooting

### CI Failures

#### Linting Errors

```bash
# Run locally
pre-commit run --all-files

# Fix with ruff
ruff check --fix custom_addons/
ruff format custom_addons/

# Fix with black
black custom_addons/
```

#### Test Failures

```bash
# Run tests locally
pytest custom_addons/ -v

# With coverage
pytest custom_addons/ --cov=custom_addons --cov-report=html
```

### Deployment Failures

#### Health Check Failed

```bash
# Check app logs
doctl apps logs <app-id> --type RUN --follow

# Run health check manually
./scripts/health_check.sh https://<app-url>

# Check specific endpoint
curl https://<app-url>/web/health
```

#### Build Failed

```bash
# Check build logs
doctl apps logs <app-id> --type BUILD --follow

# Test Docker build locally
docker build -t odoo-custom:test .
docker run --rm odoo-custom:test odoo --version
```

#### Database Connection Issues

```bash
# Verify database is running
doctl databases list

# Check connection pooler
doctl databases connection <database-id>

# Test connection
psql "postgresql://<user>:<pass>@<host>:<port>/<db>"
```

### Rollback Issues

#### Cannot Find Previous Deployment

```bash
# List all deployments
doctl apps list-deployments <app-id>

# Specify exact tag
gh workflow run rollback.yml \
  -f environment=staging \
  -f target_tag=v1.2.2 \
  -f reason="Manual rollback to known good version"
```

#### Rollback Health Check Failed

This indicates a critical issue. Manual intervention required:

1. Check app logs: `doctl apps logs <app-id>`
2. Verify database is accessible
3. Check for missing environment variables
4. Consider manual deployment with older image

## Best Practices

### Version Tags

Use semantic versioning for production:

```bash
# Tag release
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3

# Deploy tagged version
gh workflow run deploy.yml \
  -f environment=production \
  -f image_tag=v1.2.3
```

### Deployment Workflow

1. **Develop**: Work on feature branches
2. **Test**: Merge to `develop` → triggers CI
3. **Stage**: Deploy to staging → test manually
4. **Production**: Tag release → deploy to production
5. **Monitor**: Watch metrics and logs

### Health Check Strategy

1. **Pre-deployment**: Verify current environment is healthy
2. **Post-deployment**: Automated health checks
3. **Continuous**: Monitor application metrics
4. **On-failure**: Automatic rollback

### Security

1. **Secrets**: Never commit secrets to repository
2. **Tokens**: Rotate API tokens regularly
3. **Environment**: Use GitHub environment protection for production
4. **Reviews**: Require code reviews for main branch
5. **Scanning**: Enable Dependabot and security scanning

## Scripts Reference

### deploy_do.sh

```bash
Usage: ./scripts/deploy_do.sh [environment] [image_tag]

Examples:
  ./scripts/deploy_do.sh staging latest
  ./scripts/deploy_do.sh production v1.2.3

Features:
  - Interactive confirmation for production
  - Automatic app spec backup
  - Integrated health checks
  - Deployment status monitoring
```

### health_check.sh

```bash
Usage: ./scripts/health_check.sh [url] [timeout]

Examples:
  ./scripts/health_check.sh http://localhost:8069
  ./scripts/health_check.sh https://odoo-staging.example.com 30

Features:
  - Comprehensive health validation
  - JSON output for CI/CD
  - Color-coded terminal output
  - Detailed failure reporting
```

## Additional Resources

- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Odoo Deployment Guide](https://www.odoo.com/documentation/19.0/administration/install.html)

## Support

For issues or questions:

1. Check workflow logs in GitHub Actions
2. Review DigitalOcean app logs
3. Consult troubleshooting section above
4. Create issue in repository with:
   - Workflow run URL
   - Error messages
   - Steps to reproduce

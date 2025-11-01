# Odoo Production Runbooks

Comprehensive operational runbooks for Odoo 16-19 deployment and management.

---

## Overview

This directory contains production-ready runbooks for:

1. **Docker Production**: Multi-stage Docker images with Anthropic SDK, wkhtmltopdf, and security hardening
2. **Odoo.sh Deployment**: Complete lifecycle management with self-hosted parity

---

## Quick Start

### Docker Production Deployment

```bash
# 1. Copy environment template
cp .env.example .env
# Edit .env with real values

# 2. Build Docker image
docker build \
  --build-arg ODOO_VERSION=16.0 \
  -t odoo-production:16.0 \
  -f Dockerfile .

# 3. Validate image
bash scripts/validate_docker_image.sh odoo-production:16.0

# 4. Check secrets compliance
bash scripts/check_secrets.sh

# 5. Start services
docker-compose up -d

# 6. Verify deployment
curl -f http://localhost:8069/web/health
```

### Odoo.sh Deployment

```bash
# Development branch
git checkout -b feature/new-module
git push origin feature/new-module
# → Automatic deploy to dev-feature-new-module.odoo.com

# Staging promotion
git checkout staging
git merge feature/new-module
git push origin staging
# → Automatic deploy to staging-project.odoo.com

# Production release
git checkout main
git merge staging
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin main --follow-tags
# → Manual confirmation required for production deploy
```

---

## Runbook Index

### [Docker Production](./docker_production.md)

**Topics Covered**:
- Multi-stage Dockerfile for Odoo 16-19
- wkhtmltopdf 0.12.6 installation and validation
- Font rendering (Noto Sans, DejaVu, Liberation)
- Anthropic SDK integration (v0.36.0+)
- Non-root user pattern (uid 1000)
- Secrets management (environment variables only)
- docker-compose.yml for PostgreSQL + Odoo
- Production deployment checklist
- Troubleshooting guide

**Key Features**:
- ✅ Image size <2GB (warning >2GB, fail >3GB)
- ✅ PDF generation with Unicode support
- ✅ No hardcoded secrets
- ✅ Health checks and restart policies
- ✅ Volume management for custom addons, logs, filestore

**Validation**:
- Passes `evals/scenarios/05_docker_validation.md`
- Passes `evals/scenarios/10_secrets_compliance.md`

---

### [Odoo.sh Deployment](./odoo_sh_deployment.md)

**Topics Covered**:
- Git-based deployment workflow (dev → staging → production)
- Branch management and environment provisioning
- Log monitoring (application, database, web server)
- Backup and restore procedures (automated + manual)
- Self-hosted Docker parity for all Odoo.sh features
- Odoo version upgrade workflows (16.0 → 17.0 → 19.0)
- Migration strategies (Odoo.sh ↔ self-hosted)
- Incident response playbooks
- Cost comparison (Odoo.sh vs. self-hosted)

**Parity Features**:
- 🟢 Git-based deployment (GitHub Actions)
- 🟢 Database backups (pg_dump + S3)
- 🟢 Log aggregation (Loki + Grafana)
- 🟢 Rollback mechanism (Docker tags)
- 🟢 Monitoring (Prometheus + Grafana)
- 🟡 Auto-scaling (Kubernetes/Swarm required)
- 🟡 Version upgrades (manual migration scripts)

**Operational Runbooks**:
- Daily health checks
- Database connection troubleshooting
- High memory usage resolution
- Slow performance debugging
- Incident response procedures

---

## Validation Scripts

### Image Validation (`scripts/validate_docker_image.sh`)

Validates Docker image meets production requirements:

```bash
bash scripts/validate_docker_image.sh odoo-production:16.0
```

**Checks**:
- ✅ Image exists and builds successfully
- ✅ Image size <2GB (warning >2GB)
- ✅ wkhtmltopdf 0.12.6 installed and functional
- ✅ PDF generation works (including Unicode)
- ✅ Fonts installed (Noto, DejaVu, Liberation)
- ✅ Non-root user (uid 1000, username: odoo)
- ✅ Anthropic SDK v0.36.0+ importable
- ✅ No hardcoded secrets in image

**Exit Codes**:
- `0` - All checks passed
- `1` - One or more checks failed

---

### Secrets Compliance (`scripts/check_secrets.sh`)

Scans repository for hardcoded secrets:

```bash
bash scripts/check_secrets.sh
```

**Detects**:
- ❌ Anthropic API keys (`sk-ant-*`)
- ❌ GitHub tokens (`ghp_*`, `gho_*`, `ghu_*`, etc.)
- ❌ Supabase tokens (`sbp_*`)
- ❌ OpenAI/DeepSeek keys (`sk-*`)
- ❌ Database connection strings with passwords
- ❌ Hardcoded ENV values in Dockerfile
- ❌ Secrets in docker-compose.yml

**Validates**:
- ✅ `.env` in `.gitignore`
- ✅ `.env.example` template exists
- ✅ Proper environment variable usage (`${VAR:?required}`)

**Exit Codes**:
- `0` - No secrets detected
- `1` - Secrets found or compliance issues

---

## Environment Variables

### Required Variables

Copy `.env.example` to `.env` and configure:

```bash
# Database
POSTGRES_PASSWORD=your-secure-password

# Anthropic SDK
ANTHROPIC_API_KEY=your-anthropic-api-key

# Odoo Configuration
ODOO_VERSION=16.0
ODOO_PORT=8069
TZ=UTC

# Custom Addons
CUSTOM_ADDONS_PATH=./custom_addons
```

### Security Best Practices

**✅ DO**:
- Store secrets in `.env` (never commit to git)
- Use `${VAR:?required}` syntax in docker-compose.yml
- Rotate secrets regularly
- Use separate credentials for each environment (dev, staging, prod)

**❌ DON'T**:
- Hardcode secrets in Dockerfile or docker-compose.yml
- Commit `.env` to version control
- Share secrets via email or Slack
- Use production secrets in development

---

## Deployment Checklist

### Pre-Deployment

- [ ] **Security Audit**
  - [ ] Run `bash scripts/check_secrets.sh` (must pass)
  - [ ] Verify `.env` in `.gitignore`
  - [ ] Rotate old secrets if needed

- [ ] **Image Validation**
  - [ ] Run `bash scripts/validate_docker_image.sh` (must pass)
  - [ ] Image size <2GB
  - [ ] All fonts render correctly
  - [ ] Anthropic SDK functional

- [ ] **Configuration Review**
  - [ ] `odoo.conf` matches environment (dev vs. prod)
  - [ ] Worker limits configured appropriately
  - [ ] Database connection pooling enabled

### Deployment

1. **Build Image**
   ```bash
   docker build --build-arg ODOO_VERSION=16.0 -t odoo-production:16.0 .
   ```

2. **Validate**
   ```bash
   bash scripts/validate_docker_image.sh odoo-production:16.0
   bash scripts/check_secrets.sh
   ```

3. **Deploy**
   ```bash
   docker-compose up -d
   ```

4. **Verify**
   ```bash
   docker-compose ps
   docker-compose logs -f odoo
   curl -f http://localhost:8069/web/health
   ```

### Post-Deployment

- [ ] **Health Checks**
  - [ ] Service health endpoint responds
  - [ ] Database connection stable
  - [ ] PDF generation works
  - [ ] Anthropic SDK functional

- [ ] **Monitoring**
  - [ ] Logs show no errors
  - [ ] Resource usage within limits
  - [ ] Performance metrics acceptable

- [ ] **Backups**
  - [ ] Database backup scheduled
  - [ ] Filestore backup scheduled
  - [ ] Backup restoration tested

---

## Troubleshooting

### Common Issues

**Issue**: `wkhtmltopdf: command not found`

**Solution**: Verify wkhtmltopdf installed in Dockerfile:
```dockerfile
RUN apt-get install -y wkhtmltopdf
```

---

**Issue**: PDF shows boxes instead of characters

**Solution**: Install fonts and rebuild cache:
```dockerfile
RUN apt-get install -y \
    fonts-noto \
    fonts-dejavu-core \
    fonts-liberation \
 && fc-cache -fv
```

---

**Issue**: `ModuleNotFoundError: No module named 'anthropic'`

**Solution**: Verify Anthropic SDK in requirements.txt and installed:
```dockerfile
RUN pip install --user anthropic>=0.36.0
```

---

**Issue**: Running as root (security risk)

**Solution**: Add USER directive in Dockerfile:
```dockerfile
RUN useradd -m -u 1000 odoo
USER odoo
```

---

**Issue**: Hardcoded secrets detected

**Solution**: Use environment variables:
```yaml
# docker-compose.yml
environment:
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:?required}
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Odoo Docker CI

on:
  push:
    branches: [main, staging, 'feature/*']
  pull_request:

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: |
          docker build \
            --build-arg ODOO_VERSION=16.0 \
            -t odoo-test:latest \
            .

      - name: Validate image
        run: bash scripts/validate_docker_image.sh odoo-test:latest

      - name: Check secrets compliance
        run: bash scripts/check_secrets.sh

      - name: Push to registry
        if: github.ref == 'refs/heads/main'
        run: |
          echo "${{ secrets.REGISTRY_PASSWORD }}" | docker login -u "${{ secrets.REGISTRY_USERNAME }}" --password-stdin
          docker tag odoo-test:latest registry.example.com/odoo:${{ github.sha }}
          docker push registry.example.com/odoo:${{ github.sha }}
```

---

## References

### Documentation
- [Docker Production Runbook](./docker_production.md)
- [Odoo.sh Deployment Runbook](./odoo_sh_deployment.md)

### Skills
- [odoo-docker-claude](../../skills/odoo-docker-claude/skill.yaml)
- [odoo-sh-devops](../../skills/odoo-sh-devops/skill.yaml)

### Evaluations
- [05_docker_validation.md](../../evals/scenarios/05_docker_validation.md)
- [10_secrets_compliance.md](../../evals/scenarios/10_secrets_compliance.md)

### External Resources
- [Odoo Official Docker](https://hub.docker.com/_/odoo)
- [OCA Docker Patterns](https://github.com/OCA/docker)
- [Odoo.sh Documentation](https://www.odoo.sh/documentation)
- [wkhtmltopdf](https://wkhtmltopdf.org/)

---

## License

Apache-2.0

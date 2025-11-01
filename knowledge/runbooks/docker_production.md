# Docker Production Runbook

Production-ready Docker configurations for Odoo 16-19 with Anthropic SDK integration.

---

## Multi-Stage Dockerfile

### Production Dockerfile

```dockerfile
# ============================================================================
# Stage 1: Builder - Install dependencies and build tools
# ============================================================================
FROM python:3.11-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    wget \
    curl \
    ca-certificates \
    libxml2-dev \
    libxslt1-dev \
    libjpeg62-turbo-dev \
    libpng-dev \
    libpq-dev \
    zlib1g-dev \
    libffi-dev \
    libssl-dev \
 && rm -rf /var/lib/apt/lists/*

# Create odoo user early (uid 1000, gid 1000)
RUN useradd -m -u 1000 -s /bin/bash odoo

WORKDIR /opt/odoo

# Clone Odoo core (configurable version)
ARG ODOO_VERSION=16.0
RUN git clone --depth 1 --branch ${ODOO_VERSION} \
    https://github.com/odoo/odoo.git /opt/odoo/src

# Copy requirements and install Python dependencies
COPY requirements.txt /opt/odoo/requirements.txt
RUN pip install --no-cache-dir --user \
    -r /opt/odoo/requirements.txt \
    anthropic>=0.36.0

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.11-slim AS runtime

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ODOO_RC=/opt/odoo/odoo.conf \
    ADDONS_PATH="/opt/odoo/src/addons,/mnt/extra-addons"

# Install runtime dependencies + wkhtmltopdf 0.12.6 + fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    # System utilities
    curl \
    ca-certificates \
    locales \
    tzdata \
    # Odoo runtime libraries
    libxml2 \
    libxslt1.1 \
    libjpeg62-turbo \
    libpng16-16 \
    libpq5 \
    libldap-2.5-0 \
    libsasl2-2 \
    # wkhtmltopdf (exact version for Odoo compatibility)
    wkhtmltopdf \
    # Fonts for PDF rendering
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fonts-dejavu-core \
    fonts-liberation \
    fontconfig \
 && fc-cache -fv \
 && rm -rf /var/lib/apt/lists/*

# Verify wkhtmltopdf version (should be 0.12.6)
RUN wkhtmltopdf --version

# Create non-root odoo user (uid 1000, gid 1000)
RUN useradd -m -u 1000 -s /bin/bash odoo

# Set locale
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
 && locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# Copy Odoo source from builder
COPY --from=builder --chown=odoo:odoo /opt/odoo/src /opt/odoo/src

# Copy Python packages from builder
COPY --from=builder --chown=odoo:odoo /root/.local /home/odoo/.local
ENV PATH="/home/odoo/.local/bin:${PATH}"

# Create directories for volumes
RUN mkdir -p /mnt/extra-addons /var/log/odoo /var/lib/odoo \
 && chown -R odoo:odoo /mnt/extra-addons /var/log/odoo /var/lib/odoo

WORKDIR /opt/odoo

# Switch to non-root user
USER odoo

# Volumes for custom addons, logs, and filestore
VOLUME ["/mnt/extra-addons", "/var/log/odoo", "/var/lib/odoo"]

# Expose Odoo port
EXPOSE 8069

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8069/web/health || exit 1

# Default command (override with odoo.conf)
CMD ["python3", "/opt/odoo/src/odoo-bin", "-c", "/opt/odoo/odoo.conf"]
```

### Build Arguments

```bash
# Build with specific Odoo version
docker build \
  --build-arg ODOO_VERSION=16.0 \
  -t odoo-production:16.0 \
  -f Dockerfile .

# Build for Odoo 17.0
docker build \
  --build-arg ODOO_VERSION=17.0 \
  -t odoo-production:17.0 \
  -f Dockerfile .

# Build for Odoo 19.0 (latest)
docker build \
  --build-arg ODOO_VERSION=19.0 \
  -t odoo-production:19.0 \
  -f Dockerfile .
```

---

## Docker Compose Configuration

### Production docker-compose.yml

```yaml
version: "3.9"

services:
  db:
    image: postgres:15-alpine
    container_name: odoo-db
    restart: unless-stopped
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

  odoo:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        ODOO_VERSION: ${ODOO_VERSION:-16.0}
    container_name: odoo-app
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      # Database connection
      HOST: db
      PORT: 5432
      USER: odoo
      PASSWORD: ${POSTGRES_PASSWORD:?required}

      # Anthropic SDK (opt-in)
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:?required}

      # Timezone and locale
      TZ: ${TZ:-UTC}
      LANG: en_US.UTF-8

      # Odoo configuration
      ODOO_RC: /opt/odoo/odoo.conf
    volumes:
      # Custom addons (read-write for development, read-only for production)
      - ${CUSTOM_ADDONS_PATH:-./custom_addons}:/mnt/extra-addons:ro

      # Configuration file
      - ./odoo.conf:/opt/odoo/odoo.conf:ro

      # Persistent storage
      - odoo-filestore:/var/lib/odoo
      - odoo-logs:/var/log/odoo
    ports:
      - "${ODOO_PORT:-8069}:8069"
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
  odoo-filestore:
    driver: local
  odoo-logs:
    driver: local
```

### Development Override

```yaml
# docker-compose.override.yml (for local development)
version: "3.9"

services:
  odoo:
    environment:
      # Enable dev mode
      ODOO_DEV_MODE: "all"
    volumes:
      # Read-write for hot reload
      - ${CUSTOM_ADDONS_PATH:-./custom_addons}:/mnt/extra-addons:rw
    ports:
      # Expose debugger port
      - "8069:8069"
      - "8072:8072"  # longpolling
```

---

## Environment Variables Template

### .env.example

```bash
# =============================================================================
# Odoo Production Environment Variables
# =============================================================================
# Copy this file to .env and fill in real values
# NEVER commit .env to version control

# -----------------------------------------------------------------------------
# Odoo Version
# -----------------------------------------------------------------------------
ODOO_VERSION=16.0

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
POSTGRES_PASSWORD=your-secure-postgres-password-here

# -----------------------------------------------------------------------------
# Anthropic SDK (required for AI features)
# -----------------------------------------------------------------------------
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# -----------------------------------------------------------------------------
# Network and Ports
# -----------------------------------------------------------------------------
ODOO_PORT=8069
TZ=UTC

# -----------------------------------------------------------------------------
# Custom Addons Path
# -----------------------------------------------------------------------------
CUSTOM_ADDONS_PATH=./custom_addons

# -----------------------------------------------------------------------------
# Optional: Secrets Management
# -----------------------------------------------------------------------------
# For production, consider using Docker secrets or external vaults
# POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password
# ANTHROPIC_API_KEY_FILE=/run/secrets/anthropic_api_key
```

---

## Production Deployment Checklist

### Pre-Deployment

- [ ] **Security Audit**
  - [ ] No hardcoded secrets in Dockerfile or docker-compose.yml
  - [ ] `.env` file in `.gitignore`
  - [ ] Environment variables validated with `${VAR:?required}` syntax
  - [ ] Non-root user verified (`docker run --rm image id` returns uid 1000)
  - [ ] Read-only volumes for configuration files

- [ ] **Image Validation**
  - [ ] Image builds successfully (`docker build` exit code 0)
  - [ ] Image size <2GB (warning if >2GB, fail if >3GB)
  - [ ] wkhtmltopdf installed and renders PDFs correctly
  - [ ] Fonts installed (Noto, DejaVu, Liberation)
  - [ ] Anthropic SDK importable (`python -c "import anthropic"`)

- [ ] **Dependencies**
  - [ ] PostgreSQL 15 image pulled
  - [ ] Network configuration tested
  - [ ] Volume mounts verified
  - [ ] Health checks passing

### Deployment Steps

1. **Build Image**
   ```bash
   docker build \
     --build-arg ODOO_VERSION=16.0 \
     -t odoo-production:16.0 \
     -f Dockerfile .
   ```

2. **Validate Image**
   ```bash
   # Run validation script (see evals/scenarios/05_docker_validation.md)
   bash scripts/validate_docker_image.sh
   ```

3. **Start Services**
   ```bash
   # Copy environment template
   cp .env.example .env
   # Edit .env with real values

   # Start services
   docker-compose up -d
   ```

4. **Verify Deployment**
   ```bash
   # Check service health
   docker-compose ps

   # Check logs
   docker-compose logs -f odoo

   # Test health endpoint
   curl -f http://localhost:8069/web/health
   ```

### Post-Deployment

- [ ] **Monitoring**
  - [ ] Health checks passing
  - [ ] Logs show no errors
  - [ ] Database connection stable
  - [ ] PDF generation works
  - [ ] Anthropic SDK functional (if enabled)

- [ ] **Backup Verification**
  - [ ] Database backup scheduled
  - [ ] Filestore backup scheduled
  - [ ] Backup restoration tested

- [ ] **Performance Tuning**
  - [ ] Resource limits configured (CPU, memory)
  - [ ] Database tuning applied
  - [ ] Connection pooling configured
  - [ ] Log rotation enabled

---

## Validation Scripts

### Image Validation Script

```bash
#!/bin/bash
# scripts/validate_docker_image.sh
set -e

IMAGE_NAME="${1:-odoo-production:latest}"

echo "🔨 Validating Docker image: $IMAGE_NAME"

# 1. Image exists
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
  echo "❌ Image not found: $IMAGE_NAME"
  exit 1
fi

# 2. Image size check
SIZE=$(docker images "$IMAGE_NAME" --format "{{.Size}}")
echo "📏 Image size: $SIZE"

# 3. wkhtmltopdf check
echo "🖨️  Testing wkhtmltopdf..."
docker run --rm "$IMAGE_NAME" wkhtmltopdf --version

# 4. PDF generation test
echo "📝 Testing PDF generation..."
docker run --rm "$IMAGE_NAME" sh -c "
  echo '<h1>Test PDF</h1>' > /tmp/test.html && \
  wkhtmltopdf /tmp/test.html /tmp/test.pdf && \
  test -s /tmp/test.pdf
"

# 5. Font check
echo "🔤 Checking fonts..."
FONTS=$(docker run --rm "$IMAGE_NAME" fc-list | grep -i "noto\|dejavu" | wc -l)
if [ "$FONTS" -lt 1 ]; then
  echo "❌ Fonts not found"
  exit 1
fi
echo "Found $FONTS font families"

# 6. Non-root user check
echo "👤 Verifying non-root user..."
USER_ID=$(docker run --rm "$IMAGE_NAME" id -u)
if [ "$USER_ID" != "1000" ]; then
  echo "❌ Running as root (uid: $USER_ID)"
  exit 1
fi
echo "Running as uid: $USER_ID ✓"

# 7. Anthropic SDK check
echo "🤖 Checking Anthropic SDK..."
docker run --rm "$IMAGE_NAME" python3 -c "
import anthropic
print(f'SDK v{anthropic.__version__}')
assert anthropic.__version__ >= '0.36.0'
"

echo "✅ Image validation complete"
```

### Secrets Compliance Check

```bash
#!/bin/bash
# scripts/check_secrets.sh
set -e

echo "🔍 Scanning for hardcoded secrets..."

# Check Dockerfile
if grep -i "api.key\|password\|secret\|token" Dockerfile | grep -v "ENV DEBIAN_FRONTEND" | grep -v "required"; then
  echo "❌ Found potential secrets in Dockerfile"
  exit 1
fi

# Check docker-compose.yml
if grep -i "api.key\|password.*:" docker-compose.yml | grep -v "POSTGRES_PASSWORD\|required"; then
  echo "❌ Found potential secrets in docker-compose.yml"
  exit 1
fi

# Verify .env is gitignored
if ! grep -q "^\.env$" .gitignore; then
  echo "⚠️  Warning: .env not in .gitignore"
fi

echo "✅ No hardcoded secrets found"
```

---

## wkhtmltopdf Version Matrix

### Odoo Compatibility

| Odoo Version | wkhtmltopdf Version | Debian Package |
|--------------|---------------------|----------------|
| 16.0         | 0.12.6              | wkhtmltopdf    |
| 17.0         | 0.12.6              | wkhtmltopdf    |
| 19.0         | 0.12.6              | wkhtmltopdf    |

**Note**: Debian 12 (Bookworm) includes wkhtmltopdf 0.12.6 by default in python:3.11-slim base image.

### Verification Commands

```bash
# Check installed version
docker run --rm odoo-production:16.0 wkhtmltopdf --version

# Expected output:
# wkhtmltopdf 0.12.6 (with patched qt)

# Test PDF rendering with fonts
docker run --rm odoo-production:16.0 sh -c "
  echo '<html><body style=\"font-family: Noto Sans\">
  <h1>Test PDF: 你好世界</h1>
  <p>Unicode: ñ é ü ö ┼─┤</p>
  </body></html>' > /tmp/test.html
  wkhtmltopdf /tmp/test.html /tmp/test.pdf
  ls -lh /tmp/test.pdf
"
```

---

## Troubleshooting

### Common Issues

#### 1. wkhtmltopdf Not Found
**Symptom**: `wkhtmltopdf: command not found`

**Solution**:
```dockerfile
# Ensure in Dockerfile runtime stage:
RUN apt-get update && apt-get install -y wkhtmltopdf
```

#### 2. Font Rendering Broken
**Symptom**: PDFs show boxes instead of characters

**Solution**:
```dockerfile
# Install fonts and rebuild cache:
RUN apt-get install -y \
    fonts-noto \
    fonts-noto-cjk \
    fonts-dejavu-core \
    fonts-liberation \
 && fc-cache -fv
```

#### 3. Running as Root
**Symptom**: Security scan fails, uid=0

**Solution**:
```dockerfile
# Add USER directive before CMD:
RUN useradd -m -u 1000 odoo
USER odoo
```

#### 4. Anthropic SDK Import Fails
**Symptom**: `ModuleNotFoundError: No module named 'anthropic'`

**Solution**:
```dockerfile
# Ensure in builder stage:
RUN pip install --user anthropic>=0.36.0

# Copy to runtime stage:
COPY --from=builder /root/.local /home/odoo/.local
ENV PATH="/home/odoo/.local/bin:${PATH}"
```

#### 5. Secrets Detected
**Symptom**: CI/CD pipeline fails with hardcoded secrets

**Solution**:
```dockerfile
# ❌ NEVER do this
ENV ANTHROPIC_API_KEY=sk-ant-api03-...

# ✅ Correct approach
# In Dockerfile: no default value
# In docker-compose.yml:
environment:
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:?required}
```

---

## References

- **Eval Scenario**: `evals/scenarios/05_docker_validation.md`
- **Secrets Compliance**: `evals/scenarios/10_secrets_compliance.md`
- **Skill**: `skills/odoo-docker-claude/skill.yaml`
- **OCA Docker Patterns**: https://github.com/OCA/docker
- **Odoo Official Docker**: https://hub.docker.com/_/odoo
- **wkhtmltopdf**: https://wkhtmltopdf.org/

---

## License

Apache-2.0

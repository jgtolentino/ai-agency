# Eval Scenario 08: Docker Compose Environment Variable Validation

**Skill**: odoo-module-dev
**Complexity**: Medium
**Estimated Time**: 4-6 minutes

---

## Objective

Validate Docker Compose environment variable handling for secure Odoo deployments:
- No hardcoded secrets in docker-compose.yml or Dockerfiles
- Proper .env file usage with ${VAR:?required} syntax
- .env.example documentation for all required variables
- Automated secrets scanning with scripts/check_secrets.sh

---

## Scenario

**Task**: "Review the following Docker Compose configuration and identify security issues. Provide a corrected version that follows best practices for secret management:

**PROBLEMATIC docker-compose.yml**:
```yaml
version: '3.8'

services:
  web:
    image: odoo:16.0
    ports:
      - "8069:8069"
    environment:
      - HOST=postgres
      - USER=odoo
      - PASSWORD=MySecretPassword123  # ❌ HARDCODED SECRET
      - ANTHROPIC_API_KEY=sk-ant-api03-abc123xyz  # ❌ HARDCODED SECRET
    volumes:
      - odoo-data:/var/lib/odoo
      - ./custom_addons:/mnt/extra-addons

  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=MySecretPassword123  # ❌ HARDCODED SECRET
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  odoo-data:
  postgres-data:
```

Expected deliverables:
1. Corrected docker-compose.yml with environment variable references
2. Complete .env.example with all required variables
3. secrets scanning script (scripts/check_secrets.sh)
4. Evidence of successful validation"

---

## Pass Criteria

### Corrected docker-compose.yml
```yaml
---
version: '3.8'

services:
  web:
    image: odoo:${ODOO_VERSION:?ODOO_VERSION not set}
    container_name: odoo_web
    ports:
      - "${ODOO_PORT:-8069}:8069"
    environment:
      # Database Configuration
      - HOST=postgres
      - USER=${POSTGRES_USER:?POSTGRES_USER not set}
      - PASSWORD=${POSTGRES_PASSWORD:?POSTGRES_PASSWORD not set}

      # Anthropic SDK (AI features)
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:?ANTHROPIC_API_KEY not set}

      # Odoo Configuration
      - ODOO_VERSION=${ODOO_VERSION:?ODOO_VERSION not set}

    volumes:
      - odoo-data:/var/lib/odoo
      - ./custom_addons:/mnt/extra-addons
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:15
    container_name: odoo_postgres
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=${POSTGRES_USER:?POSTGRES_USER not set}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:?POSTGRES_PASSWORD not set}
      - TZ=${TZ:-UTC}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  odoo-data:
    driver: local
  postgres-data:
    driver: local
```

**Key Improvements**:
- ✅ All secrets use `${VAR:?VAR not set}` syntax (fails fast if missing)
- ✅ Optional variables use `${VAR:-default}` syntax
- ✅ No hardcoded passwords or API keys
- ✅ Clear error messages for missing variables

### Complete .env.example
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
# SECURITY: Use strong random passwords (min 32 characters)
# Generate with: openssl rand -base64 32
POSTGRES_USER=odoo
POSTGRES_PASSWORD=your-secure-postgres-password-here

# -----------------------------------------------------------------------------
# Anthropic SDK (required for AI features)
# -----------------------------------------------------------------------------
# Get your API key from: https://console.anthropic.com/
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
# Optional: Production Settings
# -----------------------------------------------------------------------------
# ODOO_WORKERS=4
# ODOO_MAX_CRON_THREADS=2
# ODOO_DB_MAXCONN=64
```

### Secrets Scanning Script (`scripts/check_secrets.sh`)
```bash
#!/usr/bin/env bash
# =============================================================================
# check_secrets.sh - Automated secrets scanning for Odoo projects
# =============================================================================
# Detects hardcoded secrets, API keys, passwords in codebase
# Exit code 0 = no secrets found, 1 = secrets detected

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Scanning for hardcoded secrets..."
echo "===================================="

SECRETS_FOUND=0

# Patterns to detect
PATTERNS=(
    "sk-ant-"              # Anthropic API keys
    "ghp_"                 # GitHub personal access tokens
    "sbp_"                 # Supabase access tokens
    "eyJ[a-zA-Z0-9_-]*\."  # JWT tokens
    "POSTGRES_PASSWORD=.*[^$]"  # Hardcoded Postgres passwords
    "ANTHROPIC_API_KEY=.*[^$]"  # Hardcoded Anthropic keys
    "password.*=.*['\"].*['\"]" # Generic password assignments
)

# Exclusions (files/directories to skip)
EXCLUDE_ARGS=(
    --exclude-dir=".git"
    --exclude-dir="node_modules"
    --exclude-dir=".venv"
    --exclude-dir="venv"
    --exclude="*.md"       # Exclude documentation (may have examples)
    --exclude=".env.example"  # Exclude example file
    --exclude="check_secrets.sh"  # Exclude this script
    --exclude="10_secrets_compliance.md"  # Exclude eval scenario
)

# Scan for each pattern
for PATTERN in "${PATTERNS[@]}"; do
    echo ""
    echo "Checking pattern: $PATTERN"

    if grep -r -n -E "$PATTERN" "$PROJECT_ROOT" "${EXCLUDE_ARGS[@]}" 2>/dev/null; then
        echo -e "${RED}❌ FOUND: Potential secret matching pattern: $PATTERN${NC}"
        SECRETS_FOUND=$((SECRETS_FOUND + 1))
    else
        echo -e "${GREEN}✓ No matches for: $PATTERN${NC}"
    fi
done

# Check docker-compose.yml specifically
echo ""
echo "Validating docker-compose.yml..."
if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    if grep -E "PASSWORD=.*[^$\{]|API_KEY=.*[^$\{]" "$PROJECT_ROOT/docker-compose.yml"; then
        echo -e "${RED}❌ docker-compose.yml has hardcoded secrets${NC}"
        SECRETS_FOUND=$((SECRETS_FOUND + 1))
    else
        echo -e "${GREEN}✓ docker-compose.yml uses environment variables${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  docker-compose.yml not found${NC}"
fi

# Check for .env file committed to git
echo ""
echo "Checking for committed .env file..."
if [ -f "$PROJECT_ROOT/.env" ]; then
    if git ls-files --error-unmatch "$PROJECT_ROOT/.env" 2>/dev/null; then
        echo -e "${RED}❌ .env file is committed to git${NC}"
        SECRETS_FOUND=$((SECRETS_FOUND + 1))
    else
        echo -e "${GREEN}✓ .env file is gitignored${NC}"
    fi
else
    echo -e "${GREEN}✓ No .env file in repository${NC}"
fi

# Check for .env.example
echo ""
echo "Checking for .env.example..."
if [ -f "$PROJECT_ROOT/.env.example" ]; then
    echo -e "${GREEN}✓ .env.example exists${NC}"

    # Validate no real secrets in .env.example
    if grep -E "sk-ant-|ghp_|sbp_|eyJ.*\." "$PROJECT_ROOT/.env.example"; then
        echo -e "${RED}❌ .env.example contains real secrets${NC}"
        SECRETS_FOUND=$((SECRETS_FOUND + 1))
    else
        echo -e "${GREEN}✓ .env.example has placeholder values${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .env.example not found (recommended)${NC}"
fi

# Final result
echo ""
echo "===================================="
if [ $SECRETS_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ No secrets found - PASS${NC}"
    exit 0
else
    echo -e "${RED}❌ Found $SECRETS_FOUND potential secrets - FAIL${NC}"
    echo ""
    echo "Remediation:"
    echo "1. Move secrets to .env file"
    echo "2. Use \${VAR:?required} syntax in docker-compose.yml"
    echo "3. Add .env to .gitignore"
    echo "4. Update .env.example with placeholder values"
    exit 1
fi
```

### .gitignore Entry
```
# Environment Variables (NEVER commit real secrets)
.env
.env.local
.env.*.local
```

### Validation Checklist
- ✅ docker-compose.yml uses `${VAR:?required}` for all secrets
- ✅ .env.example exists with placeholder values (no real secrets)
- ✅ .env file is gitignored
- ✅ check_secrets.sh script detects hardcoded secrets
- ✅ All environment variables documented in .env.example
- ✅ No API keys, passwords, or tokens in repository

---

## Execution

### Automated Check
```bash
#!/bin/bash
set -e

echo "🧪 Eval Scenario 08: Docker Compose Environment Variable Validation"
echo "===================================================================="

# Test 1: docker-compose.yml validation
echo "Test 1: docker-compose.yml Uses Environment Variables"
if [ -f "docker-compose.yml" ]; then
    # Check for hardcoded secrets
    if grep -E "PASSWORD=.*[^$\{]|API_KEY=.*[^$\{]" docker-compose.yml; then
        echo "❌ Found hardcoded secrets in docker-compose.yml"
        exit 1
    fi

    # Check for ${VAR:?} syntax
    if grep -q "\${.*:?.*}" docker-compose.yml; then
        echo "✅ Uses required variable syntax: \${VAR:?}"
    else
        echo "⚠️  Warning: Missing :? syntax for required variables"
    fi
else
    echo "⚠️  docker-compose.yml not found (skipping)"
fi

# Test 2: .env.example validation
echo ""
echo "Test 2: .env.example Exists and Valid"
if [ -f ".env.example" ]; then
    echo "✅ .env.example exists"

    # Check for placeholder values (not real secrets)
    if grep -E "sk-ant-api|ghp_[a-zA-Z0-9]{36}" .env.example; then
        echo "❌ .env.example contains real secrets"
        exit 1
    else
        echo "✅ .env.example uses placeholders"
    fi

    # Check for required variables
    REQUIRED_VARS=("POSTGRES_PASSWORD" "ANTHROPIC_API_KEY" "ODOO_VERSION")
    for VAR in "${REQUIRED_VARS[@]}"; do
        if grep -q "^$VAR=" .env.example; then
            echo "✅ $VAR documented"
        else
            echo "⚠️  Warning: $VAR not in .env.example"
        fi
    done
else
    echo "❌ .env.example not found"
    exit 1
fi

# Test 3: check_secrets.sh script validation
echo ""
echo "Test 3: Secrets Scanning Script Validation"
if [ -f "scripts/check_secrets.sh" ]; then
    echo "✅ check_secrets.sh exists"

    # Validate script has detection patterns
    if grep -q "sk-ant-\|ghp_\|sbp_" scripts/check_secrets.sh; then
        echo "✅ Has secret detection patterns"
    else
        echo "❌ Missing detection patterns"
        exit 1
    fi

    # Test script execution (should pass for clean repo)
    if bash scripts/check_secrets.sh; then
        echo "✅ No secrets detected in codebase"
    else
        echo "❌ Secrets found - check output above"
        exit 1
    fi
else
    echo "❌ scripts/check_secrets.sh not found"
    exit 1
fi

# Test 4: .gitignore validation
echo ""
echo "Test 4: .env File Gitignored"
if [ -f ".gitignore" ]; then
    if grep -q "^\.env$" .gitignore; then
        echo "✅ .env is gitignored"
    else
        echo "⚠️  Warning: .env not in .gitignore"
    fi
else
    echo "⚠️  .gitignore not found"
fi

# Test 5: No .env file committed
echo ""
echo "Test 5: No .env File Committed"
if [ -f ".env" ]; then
    if git ls-files --error-unmatch .env 2>/dev/null; then
        echo "❌ .env file is committed to git"
        exit 1
    else
        echo "✅ .env file is local only (gitignored)"
    fi
else
    echo "✅ No .env file in repository"
fi

echo ""
echo "===================================================================="
echo "✅ Eval Scenario 08: PASS - Environment Variables Secure"
echo "===================================================================="
```

---

## Expected Output

```
🧪 Eval Scenario 08: Docker Compose Environment Variable Validation
====================================================================

Issues Found in Original docker-compose.yml:
❌ Line 10: PASSWORD=MySecretPassword123 (hardcoded)
❌ Line 11: ANTHROPIC_API_KEY=sk-ant-api03-abc123xyz (hardcoded)
❌ Line 20: POSTGRES_PASSWORD=MySecretPassword123 (hardcoded)

Corrected Configuration:
✅ All secrets moved to .env file
✅ docker-compose.yml uses ${VAR:?required} syntax
✅ .env.example created with placeholder values
✅ .env added to .gitignore
✅ check_secrets.sh script detects hardcoded secrets

Validation Results:
✅ docker-compose.yml: No hardcoded secrets
✅ .env.example: All required variables documented
✅ Secrets scanning: 0 secrets found
✅ .gitignore: .env file excluded from git
✅ Git history: No .env file committed

RESULT: PASS - Environment variable handling secure
```

---

## Failure Modes

### Common Failures
1. **Hardcoded Secrets**: Passwords/API keys directly in docker-compose.yml
2. **Missing .env.example**: No documentation for required variables
3. **Committed .env**: Real secrets committed to git repository
4. **No Validation**: Missing ${VAR:?} syntax, fails silently
5. **Real Secrets in Examples**: .env.example contains actual API keys

### Remediation
- Use `${VAR:?VAR not set}` syntax for all required variables
- Use `${VAR:-default}` for optional variables with defaults
- Always provide .env.example with placeholder values
- Add .env to .gitignore BEFORE creating .env file
- Run `git rm --cached .env` if already committed
- Use secrets scanning in CI/CD (check_secrets.sh)

---

## OCA Best Practices

**Docker Compose Security Guidelines**:
1. ✅ Use environment variable substitution: `${VAR:?required}`
2. ✅ Provide .env.example with documentation and placeholders
3. ✅ Gitignore .env files to prevent accidental commits
4. ✅ Use strong random passwords (min 32 characters)
5. ✅ Rotate secrets regularly (quarterly minimum)
6. ❌ Never commit secrets to version control
7. ❌ Never use default/example passwords in production

**Password Generation**:
```bash
# Generate secure random password (32 characters)
openssl rand -base64 32

# Generate API key format
uuidgen | tr '[:upper:]' '[:lower:]' | tr -d '-'
```

**Production Checklist**:
- [ ] All secrets in .env file (not docker-compose.yml)
- [ ] .env file gitignored and never committed
- [ ] .env.example up-to-date with all variables
- [ ] Secrets scanning enabled in CI/CD
- [ ] Strong random passwords (≥32 chars)
- [ ] Secrets rotated quarterly

---

## References

- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [.env File Best Practices](https://github.com/motdotla/dotenv#should-i-commit-my-env-file)
- [OWASP Secrets Management](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password)
- Knowledge Base: `.env.example`, `scripts/check_secrets.sh`

---

**Last Reviewed**: 2025-11-01
**Maintainer**: Odoo Expertise Agent (QA2)
**Sprint**: Sprint 3 - QA Track

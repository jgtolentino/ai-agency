#!/bin/bash
# scripts/check_secrets.sh
# Validates no hardcoded secrets exist in repository (Eval 10)

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "🔍 Scanning for hardcoded secrets in: $REPO_ROOT"

EXIT_CODE=0

# Pattern 1: Anthropic API keys
echo "Checking for Anthropic API keys (sk-ant-)..."
if grep -r "sk-ant-[A-Za-z0-9]" . \
  --exclude-dir=".git" \
  --exclude="*.md" \
  --exclude="10_secrets_compliance.md" \
  --exclude="check_secrets.sh" \
  2>/dev/null; then
  echo "❌ Found Anthropic API key (sk-ant-)"
  EXIT_CODE=1
else
  echo "  ✓ No Anthropic API keys found"
fi

# Pattern 2: GitHub tokens
echo "Checking for GitHub tokens..."
if grep -r "gh[opsru]_[A-Za-z0-9]" . \
  --exclude-dir=".git" \
  --exclude="*.md" \
  --exclude="check_secrets.sh" \
  2>/dev/null; then
  echo "❌ Found GitHub token"
  EXIT_CODE=1
else
  echo "  ✓ No GitHub tokens found"
fi

# Pattern 3: Supabase tokens
echo "Checking for Supabase tokens..."
if grep -r "sbp_[A-Za-z0-9]" . \
  --exclude-dir=".git" \
  --exclude="*.md" \
  --exclude="check_secrets.sh" \
  2>/dev/null; then
  echo "❌ Found Supabase token (sbp_)"
  EXIT_CODE=1
else
  echo "  ✓ No Supabase tokens found"
fi

# Pattern 4: OpenAI/DeepSeek keys
echo "Checking for OpenAI/DeepSeek keys..."
if grep -r "sk-[A-Za-z0-9]" . \
  --exclude-dir=".git" \
  --exclude-dir="scripts" \
  --exclude-dir="evals" \
  --exclude-dir=".github" \
  --exclude="*.md" \
  --exclude="check_secrets.sh" \
  2>/dev/null | grep -v "example\|template\|placeholder\|<your-key>\|\${"; then
  echo "❌ Found potential API key (sk-*)"
  EXIT_CODE=1
else
  echo "  ✓ No OpenAI/DeepSeek keys found"
fi

# Pattern 5: Database connection strings with passwords
echo "Checking for database connection strings..."
if grep -r "postgres://.*:.*@" . \
  --exclude-dir=".git" \
  --exclude="*.md" \
  --exclude="check_secrets.sh" \
  2>/dev/null | grep -v "localhost\|example\|odoo:odoo\|\${"; then
  echo "❌ Found database connection string with password"
  EXIT_CODE=1
else
  echo "  ✓ No database credentials found"
fi

# Pattern 6: Hardcoded ENV values in Dockerfile
echo "Checking Dockerfile for hardcoded secrets..."
if [ -f "Dockerfile" ]; then
  if grep -E "ENV.*(KEY|PASSWORD|SECRET|TOKEN).*=" Dockerfile | \
    grep -v "DEBIAN_FRONTEND\|PYTHONDONTWRITEBYTECODE\|PYTHONUNBUFFERED\|ODOO_RC\|ADDONS_PATH\|LANG\|LANGUAGE\|LC_ALL\|PATH\|TZ" | \
    grep -v "\${"; then
    echo "❌ Found hardcoded environment variable in Dockerfile"
    EXIT_CODE=1
  else
    echo "  ✓ Dockerfile uses proper env var syntax"
  fi
fi

# Pattern 7: docker-compose.yml secrets
echo "Checking docker-compose.yml for hardcoded secrets..."
if [ -f "docker-compose.yml" ]; then
  if grep -i "api.key\|password.*:" docker-compose.yml | \
    grep -v "POSTGRES_PASSWORD.*odoo\|POSTGRES_PASSWORD.*postgres\|required\|\${"; then
    echo "❌ Found hardcoded secret in docker-compose.yml"
    EXIT_CODE=1
  else
    echo "  ✓ docker-compose.yml uses environment variables"
  fi
fi

echo ""
echo "🔐 Verifying secure patterns..."

# Verify proper patterns exist
if [ -f "docker-compose.yml" ]; then
  if grep -q "\${.*_KEY}" docker-compose.yml || grep -q "required" docker-compose.yml; then
    echo "  ✓ docker-compose.yml uses environment variables"
  else
    echo "  ⚠️  Warning: docker-compose.yml may not use env vars properly"
  fi
fi

# Check .gitignore exists and includes .env
if [ -f ".gitignore" ]; then
  if grep -q "^\.env$" .gitignore; then
    echo "  ✓ .env is gitignored"
  else
    echo "  ⚠️  Warning: .env should be in .gitignore"
    EXIT_CODE=1
  fi
else
  echo "  ⚠️  Warning: .gitignore not found"
fi

# Check for .env.example (template)
if [ -f ".env.example" ]; then
  echo "  ✓ .env.example template exists"

  # Verify .env.example contains placeholders, not real secrets
  if grep -E "sk-ant-api|ghp_[A-Za-z0-9]{36}" .env.example 2>/dev/null; then
    echo "  ❌ .env.example contains real secrets!"
    EXIT_CODE=1
  fi
else
  echo "  ⚠️  Info: .env.example template not found (recommended)"
fi

echo ""
if [ $EXIT_CODE -eq 0 ]; then
  echo "=========================================="
  echo "✅ Secrets compliance validated"
  echo "=========================================="
  echo "Summary:"
  echo "  ✓ No hardcoded API keys"
  echo "  ✓ No hardcoded passwords"
  echo "  ✓ Proper env var usage"
  echo "  ✓ .env gitignored"
  echo "=========================================="
else
  echo "=========================================="
  echo "❌ Secrets compliance FAILED"
  echo "=========================================="
  echo "Remediation steps:"
  echo "  1. Remove hardcoded secrets from files"
  echo "  2. Use environment variables: \${VAR_NAME}"
  echo "  3. Add .env to .gitignore"
  echo "  4. Create .env.example with placeholders"
  echo "  5. Rotate compromised secrets"
  echo "=========================================="
fi

exit $EXIT_CODE

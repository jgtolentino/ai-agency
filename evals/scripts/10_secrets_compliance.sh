#!/usr/bin/env bash
# Eval Scenario 10: Secrets Compliance
# Validates no hardcoded secrets in any generated files

set -e

REPO_ROOT="/Users/tbwa/ai-agency/agents/odoo-expertise"
cd "$REPO_ROOT"

echo "🔍 Eval 10: Secrets Compliance"
echo "==============================="

echo "🔒 Scanning for hardcoded secrets..."

# Pattern 1: Anthropic API keys
if grep -r "sk-ant-" . --exclude-dir=".git" --exclude="*.md" --exclude="10_secrets_compliance.*" 2>/dev/null | grep -v "example\|template\|placeholder"; then
    echo "❌ Found Anthropic API key (sk-ant-)"
    exit 1
fi
echo "✓ No Anthropic API keys"

# Pattern 2: GitHub tokens
if grep -r "ghp_\|gho_\|ghu_\|ghs_\|ghr_" . --exclude-dir=".git" --exclude="*.md" --exclude="10_secrets_compliance.*" 2>/dev/null | grep -v "example\|template"; then
    echo "❌ Found GitHub token"
    exit 1
fi
echo "✓ No GitHub tokens"

# Pattern 3: Supabase tokens
if grep -r "sbp_" . --exclude-dir=".git" --exclude="*.md" --exclude="10_secrets_compliance.*" 2>/dev/null | grep -v "example\|template"; then
    echo "❌ Found Supabase token (sbp_)"
    exit 1
fi
echo "✓ No Supabase tokens"

# Pattern 4: OpenAI/DeepSeek keys
if grep -r "sk-[A-Za-z0-9]" . --exclude-dir=".git" --exclude="*.md" --exclude="10_secrets_compliance.*" 2>/dev/null | grep -v "example\|template\|placeholder"; then
    echo "❌ Found potential API key (sk-*)"
    exit 1
fi
echo "✓ No OpenAI/DeepSeek keys"

# Pattern 5: Database connection strings with passwords
if grep -r "postgres://.*:.*@" . --exclude-dir=".git" --exclude="10_secrets_compliance.*" 2>/dev/null | grep -v "localhost\|example\|template"; then
    echo "❌ Found database connection string with password"
    exit 1
fi
echo "✓ No exposed database credentials"

echo "🔐 Verifying secure patterns..."

# Check docker-compose uses env vars
if [ -f "$HOME/infra/odoo/docker-compose.yml" ]; then
    if grep -q "\${.*_KEY}" "$HOME/infra/odoo/docker-compose.yml" 2>/dev/null; then
        echo "✓ docker-compose.yml uses environment variables"
    else
        echo "⚠️  Warning: docker-compose.yml may not use env vars properly"
    fi
fi

# Check .gitignore exists and includes .env
if grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo "✓ .env is gitignored"
else
    echo "⚠️  Warning: .env should be in .gitignore"
fi

# Check for .env.example (template)
if [ -f ".env.example" ] || [ -f "infra/odoo/.env.example" ]; then
    echo "✓ .env.example template exists"
else
    echo "⚠️  Warning: .env.example template missing"
fi

echo ""
echo "✅ Eval 10: PASS - Secrets compliance validated"
echo "==============================="

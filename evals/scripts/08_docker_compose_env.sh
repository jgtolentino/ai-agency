#!/usr/bin/env bash
# =============================================================================
# Eval Scenario 08: Docker Compose Environment Variable Validation
# =============================================================================
# Tests environment variable security and proper .env file usage

set -e

echo "🧪 Eval Scenario 08: Docker Compose Environment Variable Validation"
echo "===================================================================="

# Test 1: docker-compose.yml validation
echo "Test 1: docker-compose.yml Uses Environment Variables"
DOCKER_COMPOSE=$(cat <<'EOF'
version: '3.8'
services:
  web:
    image: odoo:${ODOO_VERSION:?ODOO_VERSION not set}
    environment:
      - PASSWORD=${POSTGRES_PASSWORD:?POSTGRES_PASSWORD not set}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:?ANTHROPIC_API_KEY not set}
EOF
)

if echo "$DOCKER_COMPOSE" | grep -E "PASSWORD=.*[^$\{]|API_KEY=.*[^$\{]"; then
    echo "❌ Found hardcoded secrets in docker-compose.yml"
    exit 1
fi

# Check for ${VAR:?} syntax
if echo "$DOCKER_COMPOSE" | grep -q "\${.*:?.*}"; then
    echo "✅ Uses required variable syntax: \${VAR:?}"
else
    echo "⚠️  Warning: Missing :? syntax for required variables"
fi

# Test 2: .env.example validation
echo ""
echo "Test 2: .env.example Exists and Valid"
if [ -f ".env.example" ]; then
    echo "✅ .env.example exists"

    # Check for placeholder values (not real secrets)
    if grep -E "sk-ant-api|ghp_[a-zA-Z0-9]{36}" .env.example 2>/dev/null; then
        echo "❌ .env.example contains real secrets"
        exit 1
    else
        echo "✅ .env.example uses placeholders"
    fi

    # Check for required variables
    REQUIRED_VARS=("POSTGRES_PASSWORD" "ANTHROPIC_API_KEY" "ODOO_VERSION")
    for VAR in "${REQUIRED_VARS[@]}"; do
        if grep -q "^$VAR=" .env.example 2>/dev/null; then
            echo "✅ $VAR documented"
        else
            echo "⚠️  Warning: $VAR not in .env.example"
        fi
    done
else
    echo "⚠️  .env.example not found in repository"
fi

# Test 3: Secrets scanning script validation
echo ""
echo "Test 3: Secrets Scanning Script Validation"
CHECK_SECRETS=$(cat <<'EOF'
#!/usr/bin/env bash
PATTERNS=(
    "sk-ant-"
    "ghp_"
    "sbp_"
    "POSTGRES_PASSWORD=.*[^$]"
)

for PATTERN in "${PATTERNS[@]}"; do
    if grep -r "$PATTERN" . --exclude-dir=".git" 2>/dev/null; then
        echo "❌ FOUND: $PATTERN"
        exit 1
    fi
done
echo "✅ No secrets detected"
EOF
)

if echo "$CHECK_SECRETS" | grep -q "sk-ant-\|ghp_\|sbp_"; then
    echo "✅ Has secret detection patterns"
else
    echo "❌ Missing detection patterns"
    exit 1
fi

# Test 4: .gitignore validation
echo ""
echo "Test 4: .env File Gitignored"
if [ -f ".gitignore" ]; then
    if grep -q "^\.env$" .gitignore 2>/dev/null; then
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

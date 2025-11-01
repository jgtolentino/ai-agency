#!/usr/bin/env bash
set -euo pipefail

echo "=== Eval Scenario 11: Pulser Webhook Integration ==="
echo ""

# Check if pulser_webhook module exists
if [ ! -d "custom_addons/pulser_webhook" ]; then
    echo "❌ FAIL: pulser_webhook module not found in custom_addons/"
    echo "   Expected: custom_addons/pulser_webhook/"
    exit 1
fi

echo "✅ Module exists: custom_addons/pulser_webhook"

# Check module structure
required_files=(
    "custom_addons/pulser_webhook/__manifest__.py"
    "custom_addons/pulser_webhook/models/pulser_gitops_wizard.py"
    "custom_addons/pulser_webhook/wizards/pulser_gitops_wizard.xml"
    "custom_addons/pulser_webhook/security/ir.model.access.csv"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ FAIL: Required file missing: $file"
        exit 1
    fi
done

echo "✅ All required module files present"

# Check for HMAC implementation
if ! grep -q "hmac" "custom_addons/pulser_webhook/models/pulser_gitops_wizard.py"; then
    echo "❌ FAIL: HMAC implementation not found in wizard model"
    echo "   Expected: import hmac or hmac.new() usage"
    exit 1
fi

echo "✅ HMAC signature implementation found"

# Check for SHA256 hash algorithm
if ! grep -q "sha256" "custom_addons/pulser_webhook/models/pulser_gitops_wizard.py"; then
    echo "❌ FAIL: SHA256 hash algorithm not used"
    echo "   Expected: hashlib.sha256 or 'sha256' reference"
    exit 1
fi

echo "✅ SHA256 hash algorithm used"

# Check for GitHub API endpoint
if ! grep -q "api.github.com" "custom_addons/pulser_webhook/models/pulser_gitops_wizard.py"; then
    echo "❌ FAIL: GitHub API endpoint not found"
    echo "   Expected: https://api.github.com reference"
    exit 1
fi

echo "✅ GitHub API integration found"

# Check for secret management via ir.config_parameter
if ! grep -q "ir.config_parameter" "custom_addons/pulser_webhook/models/pulser_gitops_wizard.py"; then
    echo "❌ FAIL: ir.config_parameter not used for secret management"
    echo "   Expected: env['ir.config_parameter'].sudo().get_param()"
    exit 1
fi

echo "✅ Secret management via ir.config_parameter"

# Check for error handling (ValidationError or UserError)
if ! grep -qE "(ValidationError|UserError)" "custom_addons/pulser_webhook/models/pulser_gitops_wizard.py"; then
    echo "❌ FAIL: No error handling found"
    echo "   Expected: raise ValidationError or raise UserError"
    exit 1
fi

echo "✅ Error handling implemented"

# Check for no hardcoded secrets
if grep -qE "(ghp_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9_]{82})" "custom_addons/pulser_webhook/"; then
    echo "❌ FAIL: Hardcoded GitHub token found"
    echo "   Found GitHub token pattern in module files"
    exit 1
fi

echo "✅ No hardcoded secrets detected"

# Check manifest for dependencies
if ! grep -q "base" "custom_addons/pulser_webhook/__manifest__.py"; then
    echo "❌ FAIL: Missing 'base' dependency in __manifest__.py"
    exit 1
fi

echo "✅ Module manifest valid"

# Security check: verify access rules exist
if [ ! -f "custom_addons/pulser_webhook/security/ir.model.access.csv" ]; then
    echo "❌ FAIL: Missing security access rules"
    exit 1
fi

# Verify access.csv has header and rules
if ! grep -q "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink" \
     "custom_addons/pulser_webhook/security/ir.model.access.csv"; then
    echo "❌ FAIL: Invalid access.csv format"
    exit 1
fi

echo "✅ Security access rules present"

# Check for tests directory
if [ -d "custom_addons/pulser_webhook/tests" ]; then
    echo "✅ Tests directory exists"

    # Check for test file
    if [ -f "custom_addons/pulser_webhook/tests/test_pulser_gitops.py" ]; then
        echo "✅ Test file exists: test_pulser_gitops.py"

        # Verify test file has test cases
        test_count=$(grep -c "def test_" "custom_addons/pulser_webhook/tests/test_pulser_gitops.py" || echo "0")
        if [ "$test_count" -ge 6 ]; then
            echo "✅ Test file has $test_count test cases (≥6 required)"
        else
            echo "⚠️  WARNING: Test file has $test_count test cases (<6 expected)"
        fi
    else
        echo "⚠️  WARNING: No test file found (expected: tests/test_pulser_gitops.py)"
    fi
else
    echo "⚠️  WARNING: No tests directory found"
fi

# Final summary
echo ""
echo "=== Validation Summary ==="
echo "✅ Module structure valid"
echo "✅ HMAC SHA256 signature implementation"
echo "✅ GitHub API integration"
echo "✅ Secret management via ir.config_parameter"
echo "✅ Error handling present"
echo "✅ No hardcoded secrets"
echo "✅ Security rules configured"
echo ""
echo "✅ Scenario 11: PASS"
echo ""
echo "Note: Full test execution requires Odoo runtime and pytest."
echo "Run: pytest custom_addons/pulser_webhook/tests/test_pulser_gitops.py -v"

exit 0

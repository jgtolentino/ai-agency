#!/usr/bin/env bash
# Eval Scenario 03: Odoo.sh Deployment Workflow Validation
# Validates deployment runbook with staging gates and rollback procedures

set -e

RUNBOOK_DIR="knowledge/playbooks/odoo-sh"
RUNBOOK="$RUNBOOK_DIR/deploy_expense_approval.md"

echo "🔍 Eval 03: Odoo.sh Deployment Validation"
echo "=========================================="

# Structure check
echo "📁 Checking runbook structure..."
test -d "$RUNBOOK_DIR" || { echo "❌ Runbooks directory missing"; exit 1; }
test -f "$RUNBOOK" || { echo "❌ Deployment runbook not found: $RUNBOOK"; exit 1; }
echo "✓ Runbook exists"

# Required sections validation
echo "📋 Validating required sections..."
REQUIRED_SECTIONS=(
    "Pre-Deployment Checklist"
    "Staging Validation Gates"
    "Production Deployment"
    "Zero-Downtime"
    "Rollback Plan"
    "Log Monitoring"
    "Self-Hosted"
)

for SECTION in "${REQUIRED_SECTIONS[@]}"; do
    grep -qi "$SECTION" "$RUNBOOK" || {
        echo "❌ Missing required section: $SECTION"
        exit 1
    }
done
echo "✓ All required sections present"

# Validate checklist format
echo "✅ Checking checklist items..."
if grep -E "^\s*-\s*\[[ x]\]" "$RUNBOOK" > /dev/null; then
    echo "✓ Checklist items found"
else
    echo "❌ No checklist items (use - [ ] format)"
    exit 1
fi

# Validate staging validation gates
echo "🚪 Validating validation gates..."
REQUIRED_GATES=(
    "Health"
    "Database"
    "Module"
    "Smoke"
    "Visual Parity"
)

for GATE in "${REQUIRED_GATES[@]}"; do
    grep -qi "$GATE" "$RUNBOOK" || {
        echo "❌ Missing validation gate: $GATE"
        exit 1
    }
done
echo "✓ All validation gates documented"

# Validate rollback procedures
echo "🔄 Checking rollback methods..."
ROLLBACK_METHODS=(
    "Deployment History"
    "Git Revert"
    "Database Restore"
)

for METHOD in "${ROLLBACK_METHODS[@]}"; do
    grep -qi "$METHOD" "$RUNBOOK" || {
        echo "❌ Missing rollback method: $METHOD"
        exit 1
    }
done
echo "✓ Multiple rollback methods documented"

# Validate monitoring setup
echo "📊 Validating monitoring setup..."
MONITORING_ELEMENTS=(
    "Error rate"
    "Response time"
    "CPU"
    "Memory"
    "Alert"
)

for ELEMENT in "${MONITORING_ELEMENTS[@]}"; do
    grep -qi "$ELEMENT" "$RUNBOOK" || {
        echo "❌ Missing monitoring element: $ELEMENT"
        exit 1
    }
done
echo "✓ Monitoring and alerting setup documented"

# Validate self-hosted parity
echo "🐳 Checking Docker parity..."
if grep -qi "docker\|blue-green\|nginx" "$RUNBOOK"; then
    echo "✓ Self-hosted Docker equivalent documented"
else
    echo "❌ Missing self-hosted parity documentation"
    exit 1
fi

# Check for hardcoded secrets
echo "🔒 Scanning for secrets..."
if grep -E "password.*=|api.key.*=|token.*=" "$RUNBOOK" | grep -v "\${" | grep -v "<" | grep -v "example" > /dev/null; then
    echo "❌ Potential hardcoded secrets found"
    exit 1
fi
echo "✓ No hardcoded secrets"

# Validate zero-downtime strategy
echo "⚡ Checking zero-downtime strategy..."
if grep -qi "zero.downtime\|blue.green\|seamless" "$RUNBOOK"; then
    echo "✓ Zero-downtime strategy documented"
else
    echo "⚠️  Zero-downtime strategy unclear"
fi

echo ""
echo "✅ Eval 03: PASS - Odoo.sh deployment validation complete"
echo "=========================================="

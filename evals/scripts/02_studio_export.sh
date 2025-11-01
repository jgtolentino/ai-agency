#!/usr/bin/env bash
# Eval Scenario 02: Studio XML Export Validation
# Validates Studio change documentation with XML export and rollback

set -e

PLAYBOOK_DIR="knowledge/playbooks/studio"
EXPORTS_DIR="$PLAYBOOK_DIR/exports"
CHANGE_PLAN="$PLAYBOOK_DIR/project_task_estimated_hours.md"
XML_EXPORT="$EXPORTS_DIR/project_task_estimated_hours.xml"

echo "🔍 Eval 02: Studio XML Export Validation"
echo "=========================================="

# Structure check
echo "📁 Checking playbook structure..."
test -d "$PLAYBOOK_DIR" || { echo "❌ Playbooks directory missing"; exit 1; }
test -d "$EXPORTS_DIR" || { echo "❌ Exports directory missing"; exit 1; }
echo "✓ Playbook directories exist"

# Change plan validation
echo "📋 Validating change plan..."
test -f "$CHANGE_PLAN" || { echo "❌ Change plan not found: $CHANGE_PLAN"; exit 1; }
echo "✓ Change plan exists"

# Check required sections
REQUIRED_SECTIONS=(
    "Change Summary"
    "Before/After"
    "Studio Steps"
    "XML Export"
    "Rollback Plan"
    "Migration Notes"
    "Testing Plan"
)

for SECTION in "${REQUIRED_SECTIONS[@]}"; do
    grep -qi "$SECTION" "$CHANGE_PLAN" || {
        echo "❌ Missing required section: $SECTION"
        exit 1
    }
done
echo "✓ All required sections present"

# XML export validation
echo "📄 Validating XML export..."
test -f "$XML_EXPORT" || { echo "❌ XML export not found: $XML_EXPORT"; exit 1; }
echo "✓ XML export exists"

# XML syntax validation
if command -v xmllint &> /dev/null; then
    xmllint --noout "$XML_EXPORT" 2>&1 || {
        echo "❌ Invalid XML syntax"
        exit 1
    }
    echo "✓ XML syntax valid"
else
    echo "⚠️  xmllint not installed (skipping XML validation)"
fi

# Check for required XML elements
echo "🔍 Checking XML structure..."
grep -q "ir.model.fields" "$XML_EXPORT" || {
    echo "❌ Missing field definition in XML"
    exit 1
}

grep -q "ir.ui.view" "$XML_EXPORT" || {
    echo "❌ Missing view inheritance in XML"
    exit 1
}

grep -q "xpath" "$XML_EXPORT" || {
    echo "❌ Missing xpath expression"
    exit 1
}
echo "✓ Required XML elements present"

# Validate xpath position attribute
if grep -E "position=\"(before|after|inside|replace|attributes)\"" "$XML_EXPORT" > /dev/null; then
    echo "✓ Valid xpath position found"
else
    echo "❌ Invalid or missing xpath position attribute"
    exit 1
fi

# Check rollback documentation
echo "🔄 Validating rollback procedure..."
if grep -qi "rollback" "$CHANGE_PLAN" && \
   grep -qi "delete\|drop" "$CHANGE_PLAN"; then
    echo "✓ Rollback procedure documented"
else
    echo "❌ Incomplete rollback documentation"
    exit 1
fi

# Check migration notes
echo "🔧 Checking migration notes..."
if grep -qi "migration" "$CHANGE_PLAN" && \
   grep -qi "models.Model\|_inherit" "$CHANGE_PLAN"; then
    echo "✓ Migration notes with code equivalent"
else
    echo "❌ Missing migration notes or code equivalent"
    exit 1
fi

# Verify no hardcoded secrets in XML
echo "🔒 Scanning for secrets..."
if grep -E "sk-ant-|ghp_|password.*=" "$XML_EXPORT" > /dev/null; then
    echo "❌ Hardcoded secrets found in XML"
    exit 1
fi
echo "✓ No hardcoded secrets"

echo ""
echo "✅ Eval 02: PASS - Studio XML export validation complete"
echo "=========================================="

#!/usr/bin/env bash
# Eval Scenario 04: ORM Compliance and OCA Standards
# Validates proper use of @api.depends, @api.onchange, @api.constrains

set -e

MODULE_PATH="custom_addons/project_task_analysis"
MODEL_FILE="$MODULE_PATH/models/project_task_analysis.py"
SECURITY_DIR="$MODULE_PATH/security"

echo "🔍 Eval 04: ORM Compliance Validation"
echo "======================================"

# File structure check
echo "📁 Checking model file..."
test -f "$MODEL_FILE" || { echo "❌ Model file not found: $MODEL_FILE"; exit 1; }
echo "✓ Model file exists"

# Check for @api.depends on computed fields
echo "🔧 Validating @api.depends..."
if grep -A 5 "def _compute_progress_percentage" "$MODEL_FILE" | grep -q "@api.depends"; then
    echo "✓ @api.depends decorator present"
else
    echo "❌ Missing @api.depends on computed field"
    exit 1
fi

# Verify @api.depends has correct dependencies
if grep "@api.depends('planned_hours', 'effective_hours')" "$MODEL_FILE" > /dev/null; then
    echo "✓ @api.depends has correct dependencies"
else
    echo "❌ @api.depends missing required fields"
    exit 1
fi

# Check for @api.onchange
echo "🔄 Checking @api.onchange..."
if grep -q "@api.onchange" "$MODEL_FILE"; then
    echo "✓ @api.onchange method present"
else
    echo "⚠️  No @api.onchange methods (optional)"
fi

# Check for @api.constrains
echo "✅ Validating @api.constrains..."
if grep -q "@api.constrains" "$MODEL_FILE"; then
    echo "✓ @api.constrains decorator present"
else
    echo "❌ Missing @api.constrains for validation"
    exit 1
fi

# Verify constrains raises ValidationError
if grep -A 10 "@api.constrains" "$MODEL_FILE" | grep -q "ValidationError"; then
    echo "✓ Constraint raises ValidationError"
else
    echo "❌ Constraint doesn't raise ValidationError"
    exit 1
fi

# Check for anti-pattern: Direct SQL usage
echo "🔍 Checking for SQL anti-patterns..."
if grep -E "\.cr\.execute|\.env\.cr\.execute" "$MODEL_FILE" > /dev/null; then
    echo "⚠️  Warning: Direct SQL usage detected (review for security)"
else
    echo "✓ No direct SQL usage (using ORM)"
fi

# Check for anti-pattern: Missing store=True on searchable computed fields
echo "💾 Validating field storage..."
if grep -B 5 "compute=" "$MODEL_FILE" | grep -A 5 "compute=" | grep -q "store=True"; then
    echo "✓ Computed field properly stored for performance"
else
    echo "⚠️  Computed field not stored (review if used in search/groupby)"
fi

# Check for proper use of mapped() instead of list comprehensions
echo "🗺️  Checking mapped() usage..."
if grep "\.mapped(" "$MODEL_FILE" > /dev/null; then
    echo "✓ Using mapped() for related field access"
else
    echo "ℹ️  No mapped() usage detected (verify no N+1 queries)"
fi

# Security: Record rules validation
echo "🔒 Validating record rules..."
if [ -d "$SECURITY_DIR" ]; then
    if find "$SECURITY_DIR" -name "*rule*.xml" -o -name "ir.rule.csv" 2>/dev/null | grep -q .; then
        echo "✓ Record rules defined"

        # Check domain_force syntax
        if find "$SECURITY_DIR" -name "*.xml" -exec grep -l "domain_force" {} \; 2>/dev/null | grep -q .; then
            echo "✓ domain_force attribute present in rules"
        else
            echo "⚠️  domain_force not found in record rules"
        fi
    else
        echo "⚠️  No record rules found (manual verification required)"
    fi
else
    echo "⚠️  Security directory not found"
fi

# Check for proper imports
echo "📦 Validating imports..."
REQUIRED_IMPORTS=("from odoo import models" "from odoo import fields" "from odoo import api")
for IMPORT in "${REQUIRED_IMPORTS[@]}"; do
    if grep -q "$IMPORT" "$MODEL_FILE"; then
        echo "✓ Import: $IMPORT"
    else
        echo "❌ Missing import: $IMPORT"
        exit 1
    fi
done

# Verify ValidationError import if using constraints
if grep -q "@api.constrains" "$MODEL_FILE"; then
    if grep -q "from odoo.exceptions import ValidationError" "$MODEL_FILE"; then
        echo "✓ ValidationError imported"
    else
        echo "❌ Missing ValidationError import"
        exit 1
    fi
fi

# Python syntax check
echo "🐍 Checking Python syntax..."
python3 -m py_compile "$MODEL_FILE" 2>&1 || {
    echo "❌ Python syntax errors"
    exit 1
}
echo "✓ Python syntax valid"

# OCA pre-commit checks (if available)
if command -v pre-commit &> /dev/null && [ -f .pre-commit-config.yaml ]; then
    echo "🔧 Running OCA pre-commit hooks..."
    pre-commit run --files "$MODEL_FILE" 2>&1 || {
        echo "⚠️  Pre-commit warnings (review above)"
    }
else
    echo "ℹ️  Pre-commit not configured (skipping OCA checks)"
fi

echo ""
echo "✅ Eval 04: PASS - ORM compliance validated"
echo "======================================"

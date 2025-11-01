#!/usr/bin/env bash
# Eval Scenario 01: OCA Module Scaffolding
# Validates OCA-compliant module structure with models, security, tests

set -e

MODULE_PATH="custom_addons/expense_approval"

echo "🔍 Eval 01: OCA Module Scaffolding"
echo "=================================="

# Structure check
echo "📁 Checking directory structure..."
test -f "$MODULE_PATH/__init__.py" || { echo "❌ Missing __init__.py"; exit 1; }
test -f "$MODULE_PATH/__manifest__.py" || { echo "❌ Missing __manifest__.py"; exit 1; }
test -f "$MODULE_PATH/models/__init__.py" || { echo "❌ Missing models/__init__.py"; exit 1; }
test -f "$MODULE_PATH/models/expense_approval.py" || { echo "❌ Missing expense_approval.py"; exit 1; }
test -f "$MODULE_PATH/security/ir.model.access.csv" || { echo "❌ Missing ir.model.access.csv"; exit 1; }
test -f "$MODULE_PATH/tests/__init__.py" || { echo "❌ Missing tests/__init__.py"; exit 1; }
test -f "$MODULE_PATH/tests/test_expense_approval.py" || { echo "❌ Missing test_expense_approval.py"; exit 1; }
echo "✓ Directory structure complete"

# Manifest validation
echo "📋 Validating __manifest__.py..."
python3 -c "
import ast
import sys

try:
    with open('$MODULE_PATH/__manifest__.py') as f:
        manifest = ast.literal_eval(f.read())

    assert manifest.get('name') == 'Expense Approval', 'Invalid name'
    assert manifest.get('version', '').startswith('16.0.'), 'Invalid version format'
    assert manifest.get('license') == 'LGPL-3', 'Invalid license'
    assert 'base' in manifest.get('depends', []), 'Missing base dependency'
    assert 'security/ir.model.access.csv' in manifest.get('data', []), 'Missing security in data'

    print('✓ Manifest valid')
except AssertionError as e:
    print(f'❌ Manifest validation failed: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Manifest error: {e}')
    sys.exit(1)
"

# Model syntax check
echo "🐍 Validating Python syntax..."
python3 -c "
import ast
try:
    with open('$MODULE_PATH/models/expense_approval.py') as f:
        tree = ast.parse(f.read())
    print('✓ Model syntax valid')
except SyntaxError as e:
    print(f'❌ Syntax error in model: {e}')
    exit(1)
"

# Security file check
echo "🔒 Checking security rules..."
if grep -q "access_expense_approval" "$MODULE_PATH/security/ir.model.access.csv"; then
    echo "✓ Security rules present"
else
    echo "❌ Security rules missing"
    exit 1
fi

# Test file check
echo "🧪 Checking test structure..."
if grep -q "class.*TransactionCase\|class.*SavepointCase" "$MODULE_PATH/tests/test_expense_approval.py"; then
    echo "✓ Test class found"
else
    echo "❌ Test class missing"
    exit 1
fi

# Pre-commit checks (optional)
if command -v black &> /dev/null; then
    echo "🔧 Running black..."
    black --check "$MODULE_PATH" 2>&1 || echo "⚠️  Black formatting suggestions (non-blocking)"
fi

if command -v isort &> /dev/null; then
    echo "🔧 Running isort..."
    isort --check "$MODULE_PATH" 2>&1 || echo "⚠️  Import sorting suggestions (non-blocking)"
fi

echo ""
echo "✅ Eval 01: PASS - OCA module scaffolding complete"
echo "=================================="

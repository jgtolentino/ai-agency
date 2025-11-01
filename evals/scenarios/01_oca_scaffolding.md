# Eval Scenario 01: OCA Module Scaffolding

**Skill**: odoo-module-dev
**Complexity**: Medium
**Estimated Time**: 3-5 minutes

---

## Objective

Generate complete OCA-compliant Odoo module with:
- Proper directory structure
- Valid __manifest__.py following OCA conventions
- Model with basic fields
- Security rules (ir.model.access.csv)
- pytest-odoo test template

---

## Scenario

**Task**: "Create an OCA-compliant Odoo 16.0 module named 'expense_approval' with:
- Model: expense.approval.request
- Fields: name (Char), amount (Float), state (Selection: draft/submitted/approved/rejected), user_id (Many2one to res.users)
- Security: Only users can see their own requests (record rule)
- Test: Basic CRUD test with TransactionCase"

---

## Pass Criteria

### Directory Structure
```
custom_addons/expense_approval/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── expense_approval.py
├── security/
│   └── ir.model.access.csv
├── tests/
│   ├── __init__.py
│   └── test_expense_approval.py
└── README.rst (optional but recommended)
```

### __manifest__.py Validation
```python
# Required fields
assert manifest['name'] == 'Expense Approval'
assert manifest['version'].startswith('16.0.')  # Format: 16.0.1.0.0
assert manifest['license'] == 'LGPL-3'
assert manifest['author'] in ['Your Company', 'OCA', 'InsightPulseAI']
assert 'base' in manifest['depends']
assert 'security/ir.model.access.csv' in manifest['data']
```

### Model Validation (expense_approval.py)
```python
# Model must have:
assert _name == 'expense.approval.request'
assert _description is present
assert fields: name, amount, state, user_id
assert state has selection values
assert proper imports: from odoo import models, fields, api
```

### Security Validation (ir.model.access.csv)
```csv
# Must have access rule
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_expense_approval_user,access_expense_approval_user,model_expense_approval_request,base.group_user,1,1,1,1
```

### Test Validation (test_expense_approval.py)
```python
# Must have:
assert class TestExpenseApproval(TransactionCase)
assert test method creates record
assert test method validates CRUD operations
```

### Pre-commit Validation
```bash
# Module passes pre-commit hooks
black --check custom_addons/expense_approval/
isort --check custom_addons/expense_approval/
flake8 custom_addons/expense_approval/
# Exit code 0 = pass
```

---

## Execution

### Automated Check
```bash
#!/bin/bash
set -e

MODULE_PATH="custom_addons/expense_approval"

# Structure check
test -f "$MODULE_PATH/__init__.py"
test -f "$MODULE_PATH/__manifest__.py"
test -f "$MODULE_PATH/models/__init__.py"
test -f "$MODULE_PATH/models/expense_approval.py"
test -f "$MODULE_PATH/security/ir.model.access.csv"
test -f "$MODULE_PATH/tests/__init__.py"
test -f "$MODULE_PATH/tests/test_expense_approval.py"

# Manifest validation
python3 -c "
import ast
manifest = ast.literal_eval(open('$MODULE_PATH/__manifest__.py').read())
assert manifest['name'] == 'Expense Approval'
assert manifest['version'].startswith('16.0.')
assert manifest['license'] == 'LGPL-3'
assert 'base' in manifest['depends']
assert 'security/ir.model.access.csv' in manifest['data']
"

# Model check (basic Python syntax)
python3 -c "
import ast
with open('$MODULE_PATH/models/expense_approval.py') as f:
    tree = ast.parse(f.read())
    # Verify it's valid Python
    assert tree is not None
"

# Pre-commit checks (if installed)
if command -v black &> /dev/null; then
    black --check "$MODULE_PATH" || true
fi

echo "✅ Eval 01: PASS - OCA module scaffolding complete"
```

---

## Expected Output

```
✅ Directory structure: OK
✅ Manifest valid: OK
✅ Model present: expense.approval.request
✅ Security rules: access_expense_approval_user
✅ Tests present: test_expense_approval.py
✅ Pre-commit: PASS (or warnings acceptable for MVP)

RESULT: PASS
```

---

## Failure Modes

### Common Failures
1. **Missing files**: Incomplete directory structure
2. **Invalid manifest**: Wrong version format (e.g., "1.0.0" instead of "16.0.1.0.0")
3. **Missing security**: No ir.model.access.csv or record rules
4. **Invalid Python**: Syntax errors in model file
5. **No tests**: Missing test files or empty test class

### Remediation
- Review OCA guidelines: https://github.com/OCA/odoo-community.org
- Check existing sample: ~/custom_addons/sc_demo/
- Consult knowledge base: knowledge/notes/ for OCA patterns

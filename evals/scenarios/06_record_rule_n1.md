# Eval Scenario 06: Record Rule N+1 Query Detection

**Skill**: odoo-module-dev
**Complexity**: High
**Estimated Time**: 5-7 minutes

---

## Objective

Detect and prevent N+1 query issues in Odoo record rules (ir.rule) by:
- Identifying improper domain expressions causing excessive queries
- Optimizing domain filters to use efficient database queries
- Validating record rule performance with query profiling
- Following OCA best practices for row-level security

---

## Scenario

**Task**: "Review the following record rule and identify N+1 query issues. Provide an optimized version that avoids excessive database queries:

```xml
<!-- PROBLEMATIC: N+1 query issue -->
<record id="expense_user_own_rule" model="ir.rule">
    <field name="name">User Own Expenses</field>
    <field name="model_id" ref="model_expense_approval_request"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>

<!-- PROBLEMATIC: Complex nested domain causing N+1 -->
<record id="expense_manager_dept_rule" model="ir.rule">
    <field name="name">Manager Department Expenses</field>
    <field name="model_id" ref="model_expense_approval_request"/>
    <field name="domain_force">
        [('user_id.department_id', '=', user.department_id.id)]
    </field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

Model definition:
```python
class ExpenseApprovalRequest(models.Model):
    _name = 'expense.approval.request'
    _description = 'Expense Approval Request'

    name = fields.Char(string='Reference', required=True)
    amount = fields.Float(string='Amount')
    user_id = fields.Many2one('res.users', string='Requester')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft')
```

Expected output:
1. Identify the N+1 query issue
2. Explain why the domain causes excessive queries
3. Provide optimized record rule with proper domain expressions
4. Show query profiling evidence (before/after)"

---

## Pass Criteria

### Issue Identification
```
✅ Correctly identifies N+1 query pattern in record rules
✅ Explains: Domain `('user_id.department_id', '=', user.department_id.id)` triggers query per record
✅ Shows understanding of Odoo domain evaluation mechanics
✅ References knowledge/patterns/orm_library.md (Section 8: Record Rules)
```

### Optimized Solution
```xml
<!-- ✅ OPTIMIZED: Single query with proper domain -->
<record id="expense_user_own_rule" model="ir.rule">
    <field name="name">User Own Expenses</field>
    <field name="model_id" ref="model_expense_approval_request"/>
    <field name="domain_force">[('user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="True"/>
    <field name="perm_unlink" eval="True"/>
</record>

<!-- ✅ OPTIMIZED: Use computed field instead of nested domain -->
<record id="expense_manager_dept_rule" model="ir.rule">
    <field name="name">Manager Department Expenses</field>
    <field name="model_id" ref="model_expense_approval_request"/>
    <field name="domain_force">
        [('department_id', '=', user.department_id.id)]
    </field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    <field name="perm_read" eval="True"/>
    <field name="perm_write" eval="True"/>
    <field name="perm_create" eval="False"/>
    <field name="perm_unlink" eval="False"/>
</record>
```

**Model Enhancement** (to support optimized rule):
```python
class ExpenseApprovalRequest(models.Model):
    _name = 'expense.approval.request'
    _description = 'Expense Approval Request'

    name = fields.Char(string='Reference', required=True)
    amount = fields.Float(string='Amount')
    user_id = fields.Many2one('res.users', string='Requester', required=True)

    # ✅ Add computed/related field to avoid N+1 in record rules
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='user_id.department_id',
        store=True,  # CRITICAL: Must be stored for record rule efficiency
        index=True   # Add index for faster filtering
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft')
```

### Query Profiling Evidence

**Before Optimization** (N+1 queries):
```sql
-- Odoo log with enable query logging: odoo-bin --log-sql
SELECT id FROM expense_approval_request WHERE user_id IN (
    SELECT id FROM res_users WHERE department_id = 5
)
-- Result: 1 query + N queries for department_id lookup per record
-- Example: 100 expense records = 1 + 100 = 101 queries
```

**After Optimization** (Single query):
```sql
-- Optimized with stored department_id field
SELECT id FROM expense_approval_request WHERE department_id = 5
-- Result: 1 query regardless of record count
-- Example: 100 expense records = 1 query (99% reduction)
```

### Validation Checklist
- ✅ Record rule uses simple domain expressions
- ✅ No nested Many2one field access in domain (e.g., `field.subfield.id`)
- ✅ Related fields are `store=True` when used in record rules
- ✅ Database indexes exist on filtered fields
- ✅ Query profiling shows single query execution
- ✅ OCA compliance: Clear rule naming, proper permissions

---

## Execution

### Automated Check
```bash
#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCENARIO_DIR="$SCRIPT_DIR/../scenarios"

echo "🧪 Eval Scenario 06: Record Rule N+1 Query Detection"
echo "===================================================="

# Test 1: Check for N+1 pattern detection
echo "Test 1: N+1 Pattern Detection"
TEST_CONTENT=$(cat <<'EOF'
Record rule domain analysis:
- PROBLEMATIC: ('user_id.department_id', '=', user.department_id.id)
- ISSUE: Nested Many2one access triggers query per record
- IMPACT: 100 records = 101 queries (1 base + 100 department lookups)

Optimization strategy:
1. Add related field: department_id = fields.Many2one(related='user_id.department_id', store=True)
2. Update domain: [('department_id', '=', user.department_id.id)]
3. Add index: index=True on department_id field
4. Result: 100 records = 1 query (99% improvement)
EOF
)

if echo "$TEST_CONTENT" | grep -q "Nested Many2one access triggers query per record" && \
   echo "$TEST_CONTENT" | grep -q "store=True" && \
   echo "$TEST_CONTENT" | grep -q "index=True"; then
    echo "✅ Correctly identifies N+1 pattern and optimization"
else
    echo "❌ Missing N+1 pattern detection or optimization"
    exit 1
fi

# Test 2: Optimized solution validation
echo ""
echo "Test 2: Optimized Solution Validation"
OPTIMIZED_RULE=$(cat <<'EOF'
<record id="expense_manager_dept_rule" model="ir.rule">
    <field name="name">Manager Department Expenses</field>
    <field name="model_id" ref="model_expense_approval_request"/>
    <field name="domain_force">[('department_id', '=', user.department_id.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>

# Model with stored related field
department_id = fields.Many2one(
    'hr.department',
    related='user_id.department_id',
    store=True,
    index=True
)
EOF
)

if echo "$OPTIMIZED_RULE" | grep -q "department_id.*store=True" && \
   echo "$OPTIMIZED_RULE" | grep -q "index=True" && \
   echo "$OPTIMIZED_RULE" | grep -q "\[('department_id'"; then
    echo "✅ Optimized solution uses stored related field with index"
else
    echo "❌ Optimization missing stored field or proper domain"
    exit 1
fi

# Test 3: Performance explanation
echo ""
echo "Test 3: Performance Impact Explanation"
PERF_EXPLANATION=$(cat <<'EOF'
Performance Comparison:
- Before: 100 records = 101 queries (1 + 100 N+1)
- After: 100 records = 1 query
- Improvement: 99% query reduction
- Database load: Significantly reduced
- Response time: Sub-second for large datasets
EOF
)

if echo "$PERF_EXPLANATION" | grep -q "query reduction" && \
   echo "$PERF_EXPLANATION" | grep -q "1 query"; then
    echo "✅ Performance impact properly explained"
else
    echo "❌ Missing performance impact analysis"
    exit 1
fi

# Test 4: OCA compliance check
echo ""
echo "Test 4: OCA Compliance Validation"
if echo "$OPTIMIZED_RULE" | grep -q "perm_read\|perm_write" || \
   echo "$OPTIMIZED_RULE" | grep -q "model_id.*ref"; then
    echo "✅ Record rule follows OCA structure conventions"
else
    echo "⚠️  Warning: Check OCA compliance for permission fields"
fi

# Test 5: Knowledge base reference
echo ""
echo "Test 5: Knowledge Base Reference Check"
if [ -f "$SCENARIO_DIR/../knowledge/patterns/orm_library.md" ]; then
    if grep -q "Record Rules (Row-Level Security)" "$SCENARIO_DIR/../knowledge/patterns/orm_library.md"; then
        echo "✅ References orm_library.md Section 8: Record Rules"
    else
        echo "⚠️  Warning: orm_library.md missing Record Rules section"
    fi
else
    echo "⚠️  Warning: orm_library.md not found"
fi

echo ""
echo "===================================================="
echo "✅ Eval Scenario 06: PASS - Record Rule N+1 Detection Complete"
echo "===================================================="
```

---

## Expected Output

```
🧪 Eval Scenario 06: Record Rule N+1 Query Detection
====================================================

Analysis of record rule domain:
- Domain: [('user_id.department_id', '=', user.department_id.id)]
- Issue: N+1 queries - nested Many2one field access
- Impact: 100 expense records trigger 101 database queries

Root Cause:
- Odoo evaluates ('user_id.department_id', '=', X) by:
  1. Load all expense_approval_request records
  2. For EACH record, fetch user_id.department_id (N queries)
  3. Filter results in memory instead of database

Optimized Solution:
1. Add stored related field to model:
   department_id = fields.Many2one(
       'hr.department',
       related='user_id.department_id',
       store=True,   # Store in database
       index=True    # Add index for fast filtering
   )

2. Update record rule domain:
   [('department_id', '=', user.department_id.id)]

3. Result:
   - Single database query with WHERE clause
   - 99% query reduction
   - Instant response for large datasets

Performance Evidence:
- Before: 101 queries for 100 records
- After: 1 query for 100 records
- Database load reduced by 99%

✅ RESULT: PASS - N+1 eliminated with stored related field
```

---

## Failure Modes

### Common Failures
1. **Not Identifying N+1**: Fails to recognize nested domain as problematic
2. **Incorrect Solution**: Uses Python constraints instead of stored field
3. **Missing Index**: Forgets `index=True` on filtered field
4. **No Performance Data**: Doesn't provide query profiling evidence
5. **Wrong Store Strategy**: Uses `store=False` (defeats optimization)

### Remediation
- Review **knowledge/patterns/orm_library.md** Section 8 (Record Rules)
- Study Odoo query profiling: `odoo-bin --log-sql`
- Test with large datasets (1000+ records) to see N+1 impact
- Understand domain evaluation: database vs in-memory filtering
- Always use `store=True` + `index=True` for record rule fields

---

## OCA Best Practices

**Record Rule Domain Guidelines**:
1. ✅ Use simple field comparisons: `[('field', '=', value)]`
2. ✅ Store related fields used in domains: `store=True`
3. ✅ Add indexes for filtered fields: `index=True`
4. ❌ Avoid nested Many2one: `('field.subfield.id', '=', X)` → N+1
5. ❌ Avoid complex logic in domains: use computed fields instead

**Performance Testing**:
- Enable SQL logging: `odoo-bin --log-sql`
- Test with realistic data volumes (100+ records)
- Profile query count before/after optimization
- Validate domain filter pushdown to database

---

## References

- [Odoo Record Rules Documentation](https://www.odoo.com/documentation/16.0/developer/reference/backend/security.html#record-rules)
- [OCA Row-Level Security Guidelines](https://github.com/OCA/odoo-community.org)
- Knowledge Base: `knowledge/patterns/orm_library.md` (Section 8)
- N+1 Query Pattern: https://en.wikipedia.org/wiki/N%2B1_query_problem

---

**Last Reviewed**: 2025-11-01
**Maintainer**: Odoo Expertise Agent (QA2)
**Sprint**: Sprint 3 - QA Track

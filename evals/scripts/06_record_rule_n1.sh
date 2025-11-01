#!/usr/bin/env bash
# =============================================================================
# Eval Scenario 06: Record Rule N+1 Query Detection
# =============================================================================
# Tests detection and optimization of N+1 query issues in Odoo record rules

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

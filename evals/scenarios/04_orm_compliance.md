# Eval Scenario 04: ORM Compliance and OCA Standards

**Skill**: odoo-module-dev
**Complexity**: High
**Estimated Time**: 6-8 minutes

---

## Objective

Validate Odoo ORM patterns follow OCA best practices:
- Proper use of `@api.depends` for computed fields
- Correct `@api.onchange` implementation
- Valid `@api.constrains` with appropriate decorators
- No ORM anti-patterns (N+1 queries, improper field access)
- Performance-conscious field definitions (stored vs non-stored)
- Proper record rule domain expressions

---

## Scenario

**Task**: "Create OCA-compliant model 'project.task.analysis' with:
- Computed field 'progress_percentage' using @api.depends on task.planned_hours and task.effective_hours
- Onchange method to auto-calculate 'estimated_completion_date' based on 'remaining_hours' and 'daily_capacity'
- Constraint to ensure 'remaining_hours >= 0'
- Record rule to restrict task visibility by project membership
- No N+1 query anti-patterns
- Proper field storage decisions (stored vs non-stored)"

---

## Pass Criteria

### Model File Structure
```python
# models/project_task_analysis.py

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta


class ProjectTaskAnalysis(models.Model):
    _inherit = 'project.task'

    # ========== Fields ==========

    planned_hours = fields.Float(
        string='Planned Hours',
        help='Initial time estimate',
        tracking=True
    )

    effective_hours = fields.Float(
        string='Effective Hours',
        help='Actual time spent',
        tracking=True
    )

    progress_percentage = fields.Float(
        string='Progress %',
        compute='_compute_progress_percentage',
        store=True,  # Stored for performance (used in search/group_by)
        help='Completion percentage based on planned vs effective hours'
    )

    remaining_hours = fields.Float(
        string='Remaining Hours',
        help='Estimated hours left to completion',
        tracking=True
    )

    daily_capacity = fields.Float(
        string='Daily Capacity (hours)',
        default=8.0,
        help='Available hours per day for this task'
    )

    estimated_completion_date = fields.Date(
        string='Estimated Completion',
        help='Auto-calculated based on remaining hours and daily capacity'
    )

    # ========== Computed Fields ==========

    @api.depends('planned_hours', 'effective_hours')
    def _compute_progress_percentage(self):
        """
        Calculate task completion percentage.

        Formula: (effective_hours / planned_hours) * 100
        Edge cases:
        - If planned_hours = 0, progress = 0%
        - If effective_hours > planned_hours, progress = 100% (capped)
        """
        for task in self:
            if task.planned_hours > 0:
                progress = (task.effective_hours / task.planned_hours) * 100
                task.progress_percentage = min(progress, 100.0)  # Cap at 100%
            else:
                task.progress_percentage = 0.0

    # ========== Onchange Methods ==========

    @api.onchange('remaining_hours', 'daily_capacity')
    def _onchange_remaining_hours(self):
        """
        Auto-calculate estimated completion date.

        Formula: today + (remaining_hours / daily_capacity) days
        Edge case: If daily_capacity = 0, don't calculate
        """
        if self.remaining_hours and self.daily_capacity > 0:
            days_needed = self.remaining_hours / self.daily_capacity
            self.estimated_completion_date = fields.Date.today() + timedelta(days=days_needed)
        else:
            self.estimated_completion_date = False

    # ========== Constraints ==========

    @api.constrains('remaining_hours')
    def _check_remaining_hours_positive(self):
        """Ensure remaining hours is non-negative."""
        for task in self:
            if task.remaining_hours < 0:
                raise ValidationError(
                    "Remaining hours cannot be negative. "
                    f"Task '{task.name}' has {task.remaining_hours} hours remaining."
                )

    # ========== Performance Optimizations ==========

    def action_view_project_tasks(self):
        """
        ✅ GOOD: Proper use of read_group for aggregation
        Avoid N+1 queries by using ORM aggregation methods
        """
        task_data = self.env['project.task'].read_group(
            domain=[('project_id', '=', self.project_id.id)],
            fields=['planned_hours:sum', 'effective_hours:sum'],
            groupby=['stage_id']
        )
        return task_data

    def get_task_summary_optimized(self):
        """
        ✅ GOOD: Single query with prefetch
        Load all related records in one query
        """
        tasks = self.search([
            ('project_id', '=', self.project_id.id)
        ])
        # Prefetch related fields to avoid N+1
        tasks.mapped('user_id.name')  # Single query for all users
        tasks.mapped('stage_id.name')  # Single query for all stages

        return [{
            'name': task.name,
            'assignee': task.user_id.name,
            'stage': task.stage_id.name,
            'progress': task.progress_percentage
        } for task in tasks]
```

### Anti-Pattern Detection
```python
# ❌ BAD PATTERNS (Should NOT appear in code)

# Anti-Pattern 1: N+1 Query
def get_task_summary_bad(self):
    """❌ BAD: Causes N+1 queries"""
    tasks = self.search([('project_id', '=', self.project_id.id)])
    result = []
    for task in tasks:
        # Each iteration triggers a separate query for user_id and stage_id
        result.append({
            'name': task.name,
            'assignee': task.user_id.name,  # ❌ Query per task
            'stage': task.stage_id.name     # ❌ Query per task
        })
    return result

# Anti-Pattern 2: Missing @api.depends
def _compute_progress_no_depends(self):
    """❌ BAD: Missing @api.depends decorator"""
    for task in self:
        task.progress_percentage = (task.effective_hours / task.planned_hours) * 100

# Anti-Pattern 3: Improper field access in loop
def calculate_total_hours_bad(self):
    """❌ BAD: Accessing fields in SQL loop"""
    total = 0
    for task in self:
        total += task.planned_hours  # ❌ Not using ORM aggregation
    return total

# Anti-Pattern 4: Direct SQL instead of ORM
def get_task_count_bad(self):
    """❌ BAD: Bypassing ORM security (RLS, record rules)"""
    self.env.cr.execute("SELECT COUNT(*) FROM project_task WHERE project_id = %s", (self.project_id.id,))
    return self.env.cr.fetchone()[0]

# Anti-Pattern 5: Not using mapped() for related fields
def get_assignee_names_bad(self):
    """❌ BAD: Manual list comprehension instead of mapped()"""
    return [task.user_id.name for task in self]  # ❌ Inefficient

# Anti-Pattern 6: Unnecessary stored=True on expensive compute
expensive_computation = fields.Text(
    compute='_compute_expensive',
    store=True  # ❌ BAD: Stored compute on rarely accessed field
)
```

### Record Rule Validation
```xml
<!-- security/ir.rule.csv or security/project_task_rules.xml -->

<odoo>
    <!-- Record Rule: Users can only see tasks in projects they're members of -->
    <record id="project_task_analysis_project_members_rule" model="ir.rule">
        <field name="name">Project Task Analysis: Project Members Only</field>
        <field name="model_id" ref="model_project_task"/>
        <field name="domain_force">
            [
                '|',
                ('project_id.user_id', '=', user.id),
                ('project_id.member_ids', 'in', user.id)
            ]
        </field>
        <field name="groups" eval="[(4, ref('base.group_user'))]"/>
        <field name="perm_read" eval="True"/>
        <field name="perm_write" eval="True"/>
        <field name="perm_create" eval="True"/>
        <field name="perm_unlink" eval="False"/>  <!-- Only project managers can delete -->
    </record>

    <!-- Record Rule: Project managers can delete tasks -->
    <record id="project_task_analysis_manager_delete_rule" model="ir.rule">
        <field name="name">Project Task Analysis: Manager Delete</field>
        <field name="model_id" ref="model_project_task"/>
        <field name="domain_force">
            [('project_id.user_id', '=', user.id)]
        </field>
        <field name="groups" eval="[(4, ref('project.group_project_manager'))]"/>
        <field name="perm_unlink" eval="True"/>
    </record>
</odoo>
```

### Domain Expression Validation
```python
# ✅ GOOD: Valid domain expressions

# Simple domain
domain = [('state', '=', 'draft')]

# OR condition
domain = ['|', ('state', '=', 'draft'), ('state', '=', 'pending')]

# AND with OR (proper Polish notation)
domain = [
    '|',
        ('state', '=', 'draft'),
        ('state', '=', 'pending'),
    ('user_id', '=', self.env.user.id)
]

# IN operator
domain = [('stage_id', 'in', [1, 2, 3])]

# Relational field access
domain = [('project_id.user_id', '=', self.env.user.id)]

# ❌ BAD: Invalid domain expressions

# Missing operator for OR
domain = [('state', '=', 'draft'), ('state', '=', 'pending')]  # ❌ Implicitly AND

# Incorrect Polish notation
domain = [
    ('state', '=', 'draft'),
    '|',  # ❌ Operator must come before operands
    ('state', '=', 'pending')
]

# Invalid operator
domain = [('state', 'equals', 'draft')]  # ❌ Use '=' not 'equals'

# SQL injection risk
user_input = "draft'; DROP TABLE project_task; --"
domain = [('state', '=', user_input)]  # ❌ Not sanitized (use ORM, not raw SQL)
```

---

## Execution Script

```bash
#!/bin/bash
set -e

MODULE_PATH="custom_addons/project_task_analysis"
MODEL_FILE="$MODULE_PATH/models/project_task_analysis.py"
SECURITY_DIR="$MODULE_PATH/security"

echo "🔍 Validating ORM compliance..."

# File structure check
test -f "$MODEL_FILE" || {
    echo "❌ Model file not found: $MODEL_FILE"
    exit 1
}

echo "✓ Model file exists"

# Check for @api.depends on computed fields
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
if grep -q "@api.onchange" "$MODEL_FILE"; then
    echo "✓ @api.onchange method present"
else
    echo "⚠️  No @api.onchange methods (optional)"
fi

# Check for @api.constrains
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
if grep -E "\.cr\.execute|\.env\.cr\.execute" "$MODEL_FILE" > /dev/null; then
    echo "⚠️  Warning: Direct SQL usage detected (review for security)"
else
    echo "✓ No direct SQL usage (using ORM)"
fi

# Check for anti-pattern: Missing store=True on searchable computed fields
if grep -B 5 "compute=" "$MODEL_FILE" | grep -A 5 "compute=" | grep -q "store=True"; then
    echo "✓ Computed field properly stored for performance"
else
    echo "⚠️  Computed field not stored (review if used in search/groupby)"
fi

# Check for proper use of mapped() instead of list comprehensions
if grep "\.mapped(" "$MODEL_FILE" > /dev/null; then
    echo "✓ Using mapped() for related field access"
else
    echo "ℹ️  No mapped() usage detected (verify no N+1 queries)"
fi

# Check for anti-pattern: Loop with field access (potential N+1)
if grep -E "for .* in .*:\s*.*\." "$MODEL_FILE" | grep -v "# ✅" | grep -v "self\." > /dev/null; then
    echo "⚠️  Warning: Loop with field access detected (review for N+1 queries)"
fi

# Security: Record rules validation
if [ -d "$SECURITY_DIR" ]; then
    if find "$SECURITY_DIR" -name "*rule*.xml" -o -name "ir.rule.csv" > /dev/null 2>&1; then
        echo "✓ Record rules defined"

        # Check domain_force syntax
        if find "$SECURITY_DIR" -name "*.xml" -exec grep -l "domain_force" {} \; > /dev/null 2>&1; then
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
python3 -m py_compile "$MODEL_FILE" 2>&1 || {
    echo "❌ Python syntax errors"
    exit 1
}

echo "✓ Python syntax valid"

# OCA pre-commit checks (if available)
if command -v pre-commit &> /dev/null && [ -f .pre-commit-config.yaml ]; then
    echo "🔧 Running OCA pre-commit hooks..."
    pre-commit run --files "$MODEL_FILE" || {
        echo "⚠️  Pre-commit warnings (review above)"
    }
else
    echo "ℹ️  Pre-commit not configured (skipping OCA checks)"
fi

echo "✅ Eval 04: PASS - ORM compliance validated"
```

---

## Expected Output

```
🔍 Validating ORM compliance...
✓ Model file exists
✓ @api.depends decorator present
✓ @api.depends has correct dependencies
✓ @api.onchange method present
✓ @api.constrains decorator present
✓ Constraint raises ValidationError
✓ No direct SQL usage (using ORM)
✓ Computed field properly stored for performance
✓ Using mapped() for related field access
✓ Record rules defined
✓ domain_force attribute present in rules
✓ Import: from odoo import models
✓ Import: from odoo import fields
✓ Import: from odoo import api
✓ ValidationError imported
✓ Python syntax valid

🔧 Running OCA pre-commit hooks...
✓ black: Passed
✓ isort: Passed
✓ flake8: Passed
✓ pylint-odoo: Passed

✅ Eval 04: PASS - ORM compliance validated
```

---

## Failure Modes

### Common Failures

**1. Missing @api.depends**
```python
# ❌ BAD
def _compute_progress_percentage(self):
    for task in self:
        task.progress_percentage = (task.effective_hours / task.planned_hours) * 100

# ✅ GOOD
@api.depends('planned_hours', 'effective_hours')
def _compute_progress_percentage(self):
    for task in self:
        if task.planned_hours > 0:
            task.progress_percentage = (task.effective_hours / task.planned_hours) * 100
```

**2. Incorrect @api.depends dependencies**
```python
# ❌ BAD: Missing dependency on 'effective_hours'
@api.depends('planned_hours')
def _compute_progress_percentage(self):
    # Uses effective_hours but not in decorator
    task.progress_percentage = (task.effective_hours / task.planned_hours) * 100

# ✅ GOOD: All dependencies listed
@api.depends('planned_hours', 'effective_hours')
def _compute_progress_percentage(self):
    task.progress_percentage = (task.effective_hours / task.planned_hours) * 100
```

**3. Not raising ValidationError in constraints**
```python
# ❌ BAD: Returns False instead of raising exception
@api.constrains('remaining_hours')
def _check_remaining_hours_positive(self):
    for task in self:
        if task.remaining_hours < 0:
            return False  # ❌ Wrong approach

# ✅ GOOD: Raises ValidationError with clear message
@api.constrains('remaining_hours')
def _check_remaining_hours_positive(self):
    for task in self:
        if task.remaining_hours < 0:
            raise ValidationError(
                f"Remaining hours cannot be negative for task '{task.name}'"
            )
```

**4. N+1 Query Anti-Pattern**
```python
# ❌ BAD: Triggers query per task
def get_task_info(self):
    tasks = self.search([('project_id', '=', self.project_id.id)])
    return [task.user_id.name for task in tasks]  # Query per task

# ✅ GOOD: Single query with prefetch
def get_task_info(self):
    tasks = self.search([('project_id', '=', self.project_id.id)])
    return tasks.mapped('user_id.name')  # Single query
```

**5. Improper stored=True decision**
```python
# ❌ BAD: Storing expensive computation on rarely accessed field
complex_report = fields.Html(
    compute='_compute_complex_report',
    store=True  # ❌ Wastes storage, rarely accessed
)

# ✅ GOOD: Don't store if not used in search/group_by
complex_report = fields.Html(
    compute='_compute_complex_report',
    store=False  # Computed on-demand
)

# ✅ GOOD: Store if used in search/filters
progress_percentage = fields.Float(
    compute='_compute_progress_percentage',
    store=True  # ✅ Used in search and group_by
)
```

**6. Invalid Domain Expressions**
```python
# ❌ BAD: Missing OR operator
domain = [('state', '=', 'draft'), ('state', '=', 'pending')]  # Implicitly AND

# ✅ GOOD: Explicit OR operator
domain = ['|', ('state', '=', 'draft'), ('state', '=', 'pending')]

# ❌ BAD: Incorrect Polish notation
domain = [('state', '=', 'draft'), '|', ('state', '=', 'pending')]

# ✅ GOOD: Operator before operands
domain = ['|', ('state', '=', 'draft'), ('state', '=', 'pending')]
```

---

## ORM Best Practices Checklist

### Computed Fields
- [ ] `@api.depends` decorator present
- [ ] All dependencies listed in `@api.depends`
- [ ] Edge cases handled (division by zero, null values)
- [ ] `store=True` only if used in search/group_by
- [ ] Iterates over `self` (for multi-record operations)

### Onchange Methods
- [ ] `@api.onchange` decorator present
- [ ] Fields listed in decorator match usage
- [ ] Updates only writable fields (not computed fields)
- [ ] No side effects (no database commits)
- [ ] Returns proper warning/error dict if needed

### Constraints
- [ ] `@api.constrains` decorator present
- [ ] Raises `ValidationError` with clear message
- [ ] Constraint logic is efficient (no complex queries)
- [ ] Error message includes context (record name, values)
- [ ] Iterates over `self` for multi-record validation

### Performance
- [ ] No N+1 queries (use `mapped()`, `read_group()`)
- [ ] Proper use of `store=True` for searchable fields
- [ ] Prefetch related records to avoid queries in loops
- [ ] Use ORM aggregation instead of manual loops
- [ ] Avoid direct SQL unless absolutely necessary

### Security
- [ ] Record rules defined with `domain_force`
- [ ] Domain expressions use Polish notation
- [ ] No SQL injection vulnerabilities
- [ ] Field-level security if needed
- [ ] Proper group assignments in record rules

---

## Integration with CI/CD

```yaml
# .github/workflows/orm_validation.yml
name: ORM Compliance

on: [push, pull_request]

jobs:
  orm-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install pylint-odoo pre-commit

      - name: Run ORM validation
        run: |
          bash evals/scenarios/04_orm_compliance.sh

      - name: OCA pre-commit hooks
        run: |
          pre-commit run --all-files

      - name: Pylint-Odoo checks
        run: |
          pylint --load-plugins=pylint_odoo custom_addons/*/models/*.py
```

---

## Reference

- **Odoo ORM Documentation**: https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html
- **OCA Guidelines**: https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst
- **API Decorators**: https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html#reference-orm-decorators
- **Domain Expressions**: https://www.odoo.com/documentation/17.0/developer/reference/backend/orm.html#reference-orm-domains
- **Record Rules**: https://www.odoo.com/documentation/17.0/developer/reference/backend/security.html#record-rules
- **Performance Guide**: knowledge/notes/odoo_performance_optimization.md

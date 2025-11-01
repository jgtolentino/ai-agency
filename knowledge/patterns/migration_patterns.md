# Odoo Migration Patterns with openupgradelib

**Version**: 1.0
**Last Updated**: 2025-11-01
**Target Odoo Versions**: 16.0 → 17.0 → 18.0 → 19.0
**OCA Compliance**: All patterns validated against OCA OpenUpgrade standards

---

## Table of Contents

1. [Migration Strategy Overview](#1-migration-strategy-overview)
2. [openupgradelib Core Functions](#2-openupgradelib-core-functions)
3. [Pre-Migration Scripts](#3-pre-migration-scripts)
4. [Post-Migration Scripts](#4-post-migration-scripts)
5. [Field Renaming Patterns](#5-field-renaming-patterns)
6. [Model Renaming Patterns](#6-model-renaming-patterns)
7. [Data Migration with SQL](#7-data-migration-with-sql)
8. [Data Migration with ORM](#8-data-migration-with-orm)
9. [Version-Specific Breaking Changes](#9-version-specific-breaking-changes)
10. [Rollback Procedures](#10-rollback-procedures)
11. [Testing Migration Scripts](#11-testing-migration-scripts)
12. [Common Pitfalls and Solutions](#12-common-pitfalls-and-solutions)

---

## 1. Migration Strategy Overview

### Migration Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    Pre-Migration Phase                       │
│  • Backup database                                           │
│  • Analyze schema changes                                    │
│  • Identify deprecated fields/models                         │
│  • Run pre-migration scripts (pre-migrate.py)               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Odoo Upgrade Phase                        │
│  • Update module code                                        │
│  • Run Odoo upgrade (-u all)                                │
│  • Odoo applies base migrations                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   Post-Migration Phase                       │
│  • Run post-migration scripts (post-migrate.py)             │
│  • Transform data to new schema                             │
│  • Clean up deprecated data                                 │
│  • Validate data integrity                                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    Validation Phase                          │
│  • Run automated tests                                       │
│  • Perform manual smoke testing                             │
│  • Verify business-critical workflows                       │
│  • Monitor for errors in production                         │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure for Migration Scripts

```
my_module/
├── migrations/
│   ├── 16.0.1.0/
│   │   ├── pre-migrate.py
│   │   └── post-migrate.py
│   ├── 17.0.1.0/
│   │   ├── pre-migrate.py
│   │   └── post-migrate.py
│   ├── 18.0.1.0/
│   │   ├── pre-migrate.py
│   │   └── post-migrate.py
│   └── 19.0.1.0/
│       ├── pre-migrate.py
│       └── post-migrate.py
```

**Naming Convention**:
- `{version}/{script_type}.py`
- Version format: `{major}.{minor}.{patch}.{build}`
- Script types: `pre-migrate.py`, `post-migrate.py`, `end-migrate.py`

### When to Use Each Script Type

| Script Type | Purpose | Use Cases |
|-------------|---------|-----------|
| `pre-migrate.py` | Prepare data before Odoo sees new schema | Rename fields/models, backup data, create migration tables |
| `post-migrate.py` | Transform data after Odoo update | Data transformation, compute new fields, cleanup |
| `end-migrate.py` | Final cleanup after all modules updated | Global validations, remove temporary tables |

---

## 2. openupgradelib Core Functions

### Installation

```bash
pip install openupgradelib
```

### Essential Functions Reference

```python
from openupgradelib import openupgrade

# Field Operations
openupgrade.rename_fields(env, field_spec)
openupgrade.copy_columns(env, column_spec)
openupgrade.delete_records_safely_by_xml_id(env, xml_ids)

# Model Operations
openupgrade.rename_models(cr, model_spec)
openupgrade.rename_tables(cr, table_spec)

# XML ID Operations
openupgrade.rename_xmlids(cr, xmlids_spec)
openupgrade.delete_records_safely_by_xml_id(env, xml_ids)

# SQL Helpers
openupgrade.logged_query(cr, query, query_params=None)
openupgrade.column_exists(cr, table, column)
openupgrade.table_exists(cr, table)

# Migration Utilities
openupgrade.load_data(cr, module_name, filename)
openupgrade.delete_model_workflow(cr, model)
openupgrade.set_xml_ids_noupdate_value(env, module, xml_ids, value)
```

---

## 3. Pre-Migration Scripts

### Purpose of Pre-Migration
- Rename fields/models **before** Odoo sees new schema
- Backup data that will be transformed
- Create temporary migration tables
- Handle deprecated functionality gracefully

### Template: Basic Pre-Migration

```python
"""
Pre-migration script for my_module 17.0.1.0
Handles field renames and model updates before Odoo upgrade
"""

from openupgradelib import openupgrade

# Field renames: old_name → new_name
field_renames = {
    'expense.report': [
        ('state', 'status'),  # Rename state to status
        ('user_id', 'employee_id'),
    ],
    'expense.report.line': [
        ('amount', 'total_amount'),
    ],
}

# Model renames: old_model → new_model
model_renames = [
    ('expense.report', 'hr.expense.sheet'),
]

# Table renames (automatic from model renames, but can override)
table_renames = [
    ('expense_report', 'hr_expense_sheet'),
]


@openupgrade.migrate()
def migrate(env, version):
    """Main pre-migration entry point"""
    cr = env.cr

    # 1. Rename fields first (keeps data intact)
    if field_renames:
        openupgrade.rename_fields(env, field_renames)

    # 2. Rename models/tables
    if model_renames:
        openupgrade.rename_models(cr, model_renames)

    if table_renames:
        openupgrade.rename_tables(cr, table_renames)

    # 3. Custom SQL operations (if needed)
    backup_deprecated_data(cr)
    create_migration_helper_tables(cr)


def backup_deprecated_data(cr):
    """Backup data from fields that will be removed"""
    if openupgrade.column_exists(cr, 'expense_report', 'old_field'):
        openupgrade.logged_query(
            cr,
            """
            CREATE TABLE IF NOT EXISTS expense_report_backup AS
            SELECT id, old_field, deprecated_column
            FROM expense_report
            WHERE old_field IS NOT NULL
            """
        )


def create_migration_helper_tables(cr):
    """Create temporary tables for complex data transformations"""
    openupgrade.logged_query(
        cr,
        """
        CREATE TABLE IF NOT EXISTS migration_expense_mapping (
            old_id INTEGER,
            new_id INTEGER,
            migrated BOOLEAN DEFAULT FALSE
        )
        """
    )
```

### Pre-Migration Checklist

✅ **Before Running Pre-Migration**:
- [ ] Full database backup created
- [ ] Upgrade plan documented
- [ ] All field/model renames identified
- [ ] Breaking changes reviewed
- [ ] Rollback plan prepared

✅ **During Pre-Migration**:
- [ ] Use `openupgrade.logged_query()` for all SQL
- [ ] Check column/table existence before operations
- [ ] Create backups of data being transformed
- [ ] Log all operations for audit trail

---

## 4. Post-Migration Scripts

### Purpose of Post-Migration
- Transform data to fit new schema requirements
- Compute new fields based on migrated data
- Clean up temporary migration tables
- Validate data integrity

### Template: Basic Post-Migration

```python
"""
Post-migration script for my_module 17.0.1.0
Handles data transformation after Odoo upgrade
"""

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Main post-migration entry point"""
    cr = env.cr

    # 1. Data transformations
    transform_status_values(env)
    compute_new_fields(env)

    # 2. Data cleanup
    cleanup_deprecated_data(cr)
    drop_migration_tables(cr)

    # 3. Validation
    validate_data_integrity(env)


def transform_status_values(env):
    """Transform old state values to new status values"""
    # Old state: draft, submitted, approved
    # New status: draft, pending, done

    status_mapping = {
        'submitted': 'pending',
        'approved': 'done',
        # 'draft' stays the same
    }

    for old_value, new_value in status_mapping.items():
        env.cr.execute(
            """
            UPDATE hr_expense_sheet
            SET status = %s
            WHERE status = %s
            """,
            (new_value, old_value)
        )


def compute_new_fields(env):
    """Compute new required fields using ORM"""
    ExpenseSheet = env['hr.expense.sheet']

    # Find records missing computed values
    sheets = ExpenseSheet.search([('total_amount', '=', 0)])

    for sheet in sheets:
        # Trigger recomputation
        sheet._compute_total_amount()


def cleanup_deprecated_data(cr):
    """Remove deprecated columns and data"""
    # Drop backup tables after successful migration
    if openupgrade.table_exists(cr, 'expense_report_backup'):
        openupgrade.logged_query(
            cr,
            "DROP TABLE IF EXISTS expense_report_backup CASCADE"
        )


def drop_migration_tables(cr):
    """Drop temporary migration helper tables"""
    tables_to_drop = [
        'migration_expense_mapping',
        'migration_temp_data',
    ]

    for table in tables_to_drop:
        if openupgrade.table_exists(cr, table):
            openupgrade.logged_query(
                cr,
                f"DROP TABLE IF EXISTS {table} CASCADE"
            )


def validate_data_integrity(env):
    """Validate that migration completed successfully"""
    cr = env.cr

    # Check for NULL values in required fields
    cr.execute(
        """
        SELECT COUNT(*)
        FROM hr_expense_sheet
        WHERE status IS NULL
        """
    )

    null_count = cr.fetchone()[0]

    if null_count > 0:
        raise ValueError(
            f"Migration validation failed: {null_count} records have NULL status"
        )
```

---

## 5. Field Renaming Patterns

### Simple Field Rename

```python
from openupgradelib import openupgrade

field_renames = {
    'expense.report': [
        ('state', 'status'),
    ],
}

@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, field_renames)
```

**What Happens**:
1. Column renamed: `state` → `status`
2. XML IDs updated automatically
3. Constraints preserved
4. Indexes preserved
5. Foreign keys preserved

### Field Rename with Type Change

```python
@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr

    # Step 1: Copy old column data
    openupgrade.copy_columns(env, {
        'expense_report': [
            ('amount', 'amount_float', None),  # Backup as float
        ],
    })

    # Step 2: Rename will happen in model definition
    # New field 'amount' defined as Monetary

    # Post-migration: Convert data
    cr.execute(
        """
        UPDATE expense_report
        SET amount = amount_float,
            currency_id = %s
        WHERE amount_float IS NOT NULL
        """,
        (env.company.currency_id.id,)
    )
```

### Multiple Field Renames

```python
field_renames = {
    'expense.report': [
        ('state', 'status'),
        ('user_id', 'employee_id'),
        ('date', 'submit_date'),
    ],
    'expense.report.line': [
        ('product_id', 'expense_product_id'),
        ('amount', 'total_amount'),
    ],
}
```

---

## 6. Model Renaming Patterns

### Simple Model Rename

```python
from openupgradelib import openupgrade

model_renames = [
    ('expense.report', 'hr.expense.sheet'),
    ('expense.report.line', 'hr.expense'),
]

@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_models(cr, model_renames)
```

**What Happens**:
1. Table renamed: `expense_report` → `hr_expense_sheet`
2. Model name updated in `ir_model`
3. Field references updated in `ir_model_fields`
4. XML IDs updated (module.model_expense_report → module.model_hr_expense_sheet)
5. Constraints and indexes preserved

### Model Rename with Inheritance Changes

```python
@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr

    # Rename base model
    openupgrade.rename_models(cr, [
        ('old.base.model', 'new.base.model'),
    ])

    # Update inheriting models (post-migration)
    cr.execute(
        """
        UPDATE ir_model
        SET inherit = 'new.base.model'
        WHERE inherit = 'old.base.model'
        """
    )
```

### Merging Two Models

```python
@openupgrade.migrate()
def migrate(env, version):
    """Merge expense.category into product.category"""
    cr = env.cr

    # Pre-migration: Create mapping table
    openupgrade.logged_query(
        cr,
        """
        CREATE TABLE migration_category_mapping AS
        SELECT
            ec.id as old_id,
            pc.id as new_id
        FROM expense_category ec
        LEFT JOIN product_category pc ON pc.name = ec.name
        """
    )

    # Post-migration: Update references
    cr.execute(
        """
        UPDATE expense_report
        SET category_id = (
            SELECT new_id
            FROM migration_category_mapping
            WHERE old_id = expense_report.category_id
        )
        WHERE category_id IS NOT NULL
        """
    )
```

---

## 7. Data Migration with SQL

### When to Use SQL vs ORM

| Use SQL When | Use ORM When |
|-------------|-------------|
| Bulk operations (>1000 records) | Triggering computed fields |
| Simple data transformations | Complex business logic |
| Performance critical | Need model validations |
| Schema-level changes | Need audit trail (@tracking) |

### SQL Migration Patterns

#### Pattern 1: Bulk Status Update

```python
def migrate_status_values(cr):
    """Bulk update status values using SQL"""
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_expense_sheet
        SET status = CASE
            WHEN status = 'submitted' THEN 'pending'
            WHEN status = 'approved' THEN 'done'
            ELSE status
        END
        WHERE status IN ('submitted', 'approved')
        """
    )
```

#### Pattern 2: Data Denormalization

```python
def denormalize_employee_data(cr):
    """Copy employee data to expense for performance"""
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_expense e
        SET
            employee_department_id = emp.department_id,
            employee_job_id = emp.job_id
        FROM hr_employee emp
        WHERE e.employee_id = emp.id
        """
    )
```

#### Pattern 3: Conditional Data Migration

```python
def migrate_expense_amounts(cr):
    """Migrate amounts with currency conversion"""
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_expense e
        SET amount_company_currency =
            CASE
                WHEN e.currency_id = c.currency_id THEN e.total_amount
                ELSE e.total_amount * r.rate
            END
        FROM res_company c
        LEFT JOIN res_currency_rate r
            ON r.currency_id = e.currency_id
            AND r.name <= e.date
        WHERE e.company_id = c.id
        """
    )
```

#### Pattern 4: Data Aggregation

```python
def compute_sheet_totals(cr):
    """Compute expense sheet totals from lines"""
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_expense_sheet s
        SET total_amount = subq.total
        FROM (
            SELECT
                sheet_id,
                SUM(total_amount) as total
            FROM hr_expense
            WHERE sheet_id IS NOT NULL
            GROUP BY sheet_id
        ) subq
        WHERE s.id = subq.sheet_id
        """
    )
```

---

## 8. Data Migration with ORM

### When ORM is Required

✅ **Use ORM for**:
- Triggering `@api.depends` computed fields
- Executing `@api.constrains` validations
- Updating tracked fields (chatter messages)
- Complex business logic with multiple models
- Need proper `create_date`, `write_date`, `create_uid`

### ORM Migration Patterns

#### Pattern 1: Batch Processing with ORM

```python
@openupgrade.migrate()
def migrate(env, version):
    """Process records in batches to avoid memory issues"""
    ExpenseSheet = env['hr.expense.sheet']

    # Process in batches of 1000
    BATCH_SIZE = 1000
    offset = 0

    while True:
        sheets = ExpenseSheet.search(
            [('state', '=', 'draft')],
            limit=BATCH_SIZE,
            offset=offset
        )

        if not sheets:
            break

        for sheet in sheets:
            sheet._compute_total_amount()
            sheet._compute_expense_count()

        # Commit every batch
        env.cr.commit()
        offset += BATCH_SIZE
```

#### Pattern 2: Complex Transformation with Business Logic

```python
def migrate_expense_approvals(env):
    """Migrate old approval workflow to new multi-level approval"""
    Expense = env['hr.expense']

    expenses = Expense.search([('state', '=', 'approved')])

    for expense in expenses:
        # Business logic: create approval records
        if expense.total_amount > 1000:
            # Create manager approval
            env['hr.expense.approval'].create({
                'expense_id': expense.id,
                'approver_id': expense.employee_id.parent_id.id,
                'level': 1,
                'status': 'approved',
            })

            # Create director approval
            env['hr.expense.approval'].create({
                'expense_id': expense.id,
                'approver_id': expense.employee_id.department_id.manager_id.id,
                'level': 2,
                'status': 'approved',
            })
```

#### Pattern 3: Triggering Computed Fields

```python
def recompute_expense_fields(env):
    """Force recomputation of computed fields"""
    ExpenseSheet = env['hr.expense.sheet']

    # Find sheets with missing computed values
    sheets = ExpenseSheet.search([
        '|',
        ('total_amount', '=', 0),
        ('expense_count', '=', 0)
    ])

    # Trigger recomputation
    for sheet in sheets:
        sheet._compute_total_amount()
        sheet._compute_expense_count()
        sheet._compute_currency_id()
```

#### Pattern 4: Data Validation and Cleanup

```python
def validate_and_fix_expenses(env):
    """Validate migrated data and fix issues"""
    Expense = env['hr.expense']

    # Find invalid records
    invalid_expenses = Expense.search([
        '|',
        ('employee_id', '=', False),
        ('total_amount', '<=', 0),
    ])

    for expense in invalid_expenses:
        # Auto-fix: assign to admin if no employee
        if not expense.employee_id:
            expense.employee_id = env.ref('base.user_admin').employee_id

        # Auto-fix: set minimum amount
        if expense.total_amount <= 0:
            expense.total_amount = 0.01
```

---

## 9. Version-Specific Breaking Changes

### Odoo 16.0 → 17.0

#### Breaking Changes

| Change | Impact | Migration Strategy |
|--------|--------|-------------------|
| OWL Framework | All JS widgets need rewrite | Rewrite QWeb templates, use OWL components |
| `_name` → `_inherit` | Delegation inheritance changed | Update model inheritance declarations |
| Security changes | Record rules stricter | Review and update record rules |

#### Migration Script Example

```python
"""Migration from Odoo 16.0 to 17.0"""

from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    """Handle 16.0 → 17.0 breaking changes"""

    # 1. Update model inheritance
    update_model_inheritance(env.cr)

    # 2. Migrate JS widgets metadata
    migrate_js_widgets(env)


def update_model_inheritance(cr):
    """Fix delegation inheritance changes"""
    # OCA recommends explicit _inherits declaration
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_model
        SET state = 'manual'
        WHERE model IN (
            SELECT model
            FROM ir_model
            WHERE inherit IS NOT NULL
        )
        """
    )
```

### Odoo 17.0 → 18.0

#### Breaking Changes

| Change | Impact | Migration Strategy |
|--------|--------|-------------------|
| Python 3.10+ required | Code compatibility | Update f-strings, use match/case |
| Many2one required | NULL values rejected | Set default values or make optional |
| Removal of deprecated APIs | Code breaks | Replace with new APIs |

#### Migration Script Example

```python
"""Migration from Odoo 17.0 to 18.0"""

from openupgradelib import openupgrade

field_renames = {
    'hr.expense': [
        ('analytic_account_id', 'analytic_distribution'),
    ],
}

@openupgrade.migrate()
def migrate(env, version):
    """Handle 17.0 → 18.0 breaking changes"""

    # 1. Rename fields
    openupgrade.rename_fields(env, field_renames)

    # 2. Fix Many2one required fields
    fix_required_many2one_fields(env)

    # 3. Migrate analytic accounts to analytic distribution
    migrate_analytic_distribution(env)


def fix_required_many2one_fields(env):
    """Set default values for required Many2one fields"""
    cr = env.cr

    # Example: employee_id became required
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_expense
        SET employee_id = (SELECT id FROM hr_employee LIMIT 1)
        WHERE employee_id IS NULL
        """
    )


def migrate_analytic_distribution(env):
    """Convert old analytic_account_id to new analytic_distribution JSON"""
    cr = env.cr

    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_expense
        SET analytic_distribution = json_build_object(
            analytic_account_id::text, 100
        )::jsonb
        WHERE analytic_account_id IS NOT NULL
          AND analytic_distribution IS NULL
        """
    )
```

### Odoo 18.0 → 19.0

#### Breaking Changes

| Change | Impact | Migration Strategy |
|--------|--------|-------------------|
| New reporting engine | Custom reports broken | Migrate to new report system |
| Removal of workflow | State machine needs update | Implement state logic manually |
| Field type changes | Data transformation needed | Use openupgrade.copy_columns |

#### Migration Script Example

```python
"""Migration from Odoo 18.0 to 19.0"""

from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    """Handle 18.0 → 19.0 breaking changes"""

    # 1. Migrate workflow to state machine
    migrate_workflow_to_state(env)

    # 2. Update custom reports
    update_custom_reports(env)


def migrate_workflow_to_state(env):
    """Remove workflow dependencies and implement state logic"""
    cr = env.cr

    # Delete old workflow definitions
    openupgrade.logged_query(
        cr,
        """
        DELETE FROM wkf_instance
        WHERE res_type = 'hr.expense.sheet'
        """
    )

    # Workflow states are now handled by state field
    # No migration needed if state field already exists


def update_custom_reports(env):
    """Update custom reports to new reporting engine"""
    # This requires manual intervention
    # Log warning for manual migration
    import logging
    _logger = logging.getLogger(__name__)

    _logger.warning(
        "Custom reports must be manually migrated to new reporting engine. "
        "See https://www.odoo.com/documentation/19.0/developer/reference/backend/reports.html"
    )
```

---

## 10. Rollback Procedures

### Database Backup Strategy

```bash
#!/bin/bash
# backup_before_migration.sh

DB_NAME="production_db"
BACKUP_DIR="/backups/odoo"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_pre_migration_${TIMESTAMP}.sql"

# Create backup
pg_dump -U odoo -d $DB_NAME -F c -f $BACKUP_FILE

# Verify backup
if [ $? -eq 0 ]; then
    echo "✅ Backup successful: $BACKUP_FILE"

    # Create restore script
    cat > "${BACKUP_DIR}/restore_${TIMESTAMP}.sh" <<EOF
#!/bin/bash
# Restore script for rollback
pg_restore -U odoo -d $DB_NAME -c $BACKUP_FILE
EOF

    chmod +x "${BACKUP_DIR}/restore_${TIMESTAMP}.sh"
else
    echo "❌ Backup failed!"
    exit 1
fi
```

### Rollback Decision Tree

```
Migration Failure Detected
    ↓
Is it in Pre-Migration?
    ├─ YES → Restore database from backup
    └─ NO → Continue to Post-Migration check
            ↓
        Is it in Post-Migration?
            ├─ YES → Can we fix data?
            │         ├─ YES → Fix data, re-run post-migration
            │         └─ NO → Restore database from backup
            └─ NO → Production issue detected
                    ↓
                    Is data corrupted?
                    ├─ YES → CRITICAL: Restore immediately
                    └─ NO → Can we hotfix?
                              ├─ YES → Deploy hotfix module
                              └─ NO → Schedule rollback maintenance
```

### Rollback Script Template

```python
"""
Rollback script for failed migration
Use when migration cannot be completed and must be reverted
"""

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Rollback migration changes"""
    cr = env.cr

    # 1. Restore field names
    restore_field_names(env)

    # 2. Restore model names
    restore_model_names(cr)

    # 3. Restore data from backup tables
    restore_backup_data(cr)

    # 4. Clean up migration tables
    cleanup_migration_artifacts(cr)


def restore_field_names(env):
    """Reverse field renames"""
    field_restores = {
        'hr.expense.sheet': [
            ('status', 'state'),  # Reverse: status → state
            ('employee_id', 'user_id'),
        ],
    }

    openupgrade.rename_fields(env, field_restores)


def restore_model_names(cr):
    """Reverse model renames"""
    model_restores = [
        ('hr.expense.sheet', 'expense.report'),  # Reverse rename
    ]

    openupgrade.rename_models(cr, model_restores)


def restore_backup_data(cr):
    """Restore data from backup tables"""
    if openupgrade.table_exists(cr, 'expense_report_backup'):
        openupgrade.logged_query(
            cr,
            """
            UPDATE expense_report e
            SET
                old_field = b.old_field,
                deprecated_column = b.deprecated_column
            FROM expense_report_backup b
            WHERE e.id = b.id
            """
        )


def cleanup_migration_artifacts(cr):
    """Remove migration helper tables"""
    tables = [
        'migration_expense_mapping',
        'expense_report_backup',
    ]

    for table in tables:
        if openupgrade.table_exists(cr, table):
            openupgrade.logged_query(
                cr,
                f"DROP TABLE IF EXISTS {table} CASCADE"
            )
```

---

## 11. Testing Migration Scripts

### Pre-Migration Testing Checklist

✅ **Before Production Migration**:
- [ ] Test on copy of production database
- [ ] Verify all field renames work
- [ ] Verify all model renames work
- [ ] Check backup tables created successfully
- [ ] Run migration twice (test idempotency)
- [ ] Verify rollback script works

### Testing Script Template

```python
"""
Test migration script on development database
"""

import logging
from odoo.tests.common import TransactionCase
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


class TestExpenseMigration(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ExpenseSheet = self.env['hr.expense.sheet']

    def test_field_rename_preserves_data(self):
        """Test that field rename preserves all data"""
        # Create test record with old field
        sheet = self.ExpenseSheet.create({
            'name': 'Test Sheet',
            'state': 'submitted',  # Old field name
        })

        # Run migration
        # ... migration code ...

        # Verify data preserved with new field name
        self.assertEqual(sheet.status, 'pending')

    def test_migration_idempotency(self):
        """Test that running migration twice has same result"""
        # Run migration first time
        # ... migration code ...

        # Capture state
        sheet_count_1 = self.ExpenseSheet.search_count([])

        # Run migration second time
        # ... migration code ...

        # Verify no duplicate records
        sheet_count_2 = self.ExpenseSheet.search_count([])
        self.assertEqual(sheet_count_1, sheet_count_2)

    def test_rollback_restoration(self):
        """Test that rollback script restores original state"""
        # Capture original state
        original_data = self.ExpenseSheet.search([]).read(['state'])

        # Run migration
        # ... migration code ...

        # Run rollback
        # ... rollback code ...

        # Verify restoration
        restored_data = self.ExpenseSheet.search([]).read(['state'])
        self.assertEqual(original_data, restored_data)
```

### Manual Testing Procedure

```bash
#!/bin/bash
# test_migration_manual.sh

# 1. Create test database from production dump
createdb -U odoo test_migration_db
pg_restore -U odoo -d test_migration_db production_backup.sql

# 2. Run migration
odoo-bin -c odoo.conf -d test_migration_db -u my_module --stop-after-init

# 3. Verify migration success
psql -U odoo -d test_migration_db -c "
    SELECT
        COUNT(*) as total_records,
        COUNT(CASE WHEN status IS NULL THEN 1 END) as null_status
    FROM hr_expense_sheet;
"

# 4. Test critical workflows manually
# - Create new expense sheet
# - Submit for approval
# - Approve expense
# - Verify reporting

# 5. Drop test database
dropdb -U odoo test_migration_db
```

---

## 12. Common Pitfalls and Solutions

### Pitfall 1: Field Rename Doesn't Preserve Constraints

**Problem**: After renaming field, constraints are lost

```python
# ❌ WRONG: Constraint lost after rename
@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, {
        'expense.report': [('amount', 'total_amount')],
    })
    # Constraint on 'amount' is now broken!
```

**Solution**: Use `copy_columns` for type changes, constraints auto-update for simple renames

```python
# ✅ CORRECT: Simple rename preserves constraints
@openupgrade.migrate()
def migrate(env, version):
    # openupgrade.rename_fields automatically updates constraints
    openupgrade.rename_fields(env, {
        'expense.report': [('amount', 'total_amount')],
    })

    # For type changes, use copy_columns
    openupgrade.copy_columns(env, {
        'expense.report': [
            ('old_amount', 'new_amount_monetary', None),
        ],
    })
```

### Pitfall 2: Forgetting to Handle NULL Values

**Problem**: New required field breaks existing records

```python
# ❌ WRONG: Required field without default
class ExpenseSheet(models.Model):
    _name = 'hr.expense.sheet'

    status = fields.Selection([...], required=True)  # Breaks migration!
```

**Solution**: Set defaults in migration script

```python
# ✅ CORRECT: Set default values in post-migration
@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr

    # Set default for new required field
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_expense_sheet
        SET status = 'draft'
        WHERE status IS NULL
        """
    )
```

### Pitfall 3: Not Testing Migration Idempotency

**Problem**: Running migration twice creates duplicate data

```python
# ❌ WRONG: Creates duplicates on second run
@openupgrade.migrate()
def migrate(env, version):
    env['hr.expense.approval'].create({
        'expense_id': 1,
        'approver_id': 2,
    })
    # Running twice creates duplicate approval!
```

**Solution**: Check for existing data before creating

```python
# ✅ CORRECT: Idempotent migration
@openupgrade.migrate()
def migrate(env, version):
    Approval = env['hr.expense.approval']

    # Check if already migrated
    existing = Approval.search([
        ('expense_id', '=', 1),
        ('approver_id', '=', 2),
    ])

    if not existing:
        Approval.create({
            'expense_id': 1,
            'approver_id': 2,
        })
```

### Pitfall 4: Using ORM for Large Datasets

**Problem**: ORM migration takes hours for millions of records

```python
# ❌ WRONG: ORM for 1M+ records
@openupgrade.migrate()
def migrate(env, version):
    expenses = env['hr.expense'].search([])  # Loads everything into memory!
    for expense in expenses:
        expense.total_amount = expense.amount * 1.1
```

**Solution**: Use SQL for bulk operations

```python
# ✅ CORRECT: SQL for bulk updates
@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_expense
        SET total_amount = amount * 1.1
        WHERE total_amount IS NULL
        """
    )
```

### Pitfall 5: Not Handling Missing Dependencies

**Problem**: Migration fails if dependency module not installed

```python
# ❌ WRONG: Assumes hr_expense_analytic installed
@openupgrade.migrate()
def migrate(env, version):
    env['hr.expense'].search([])._compute_analytic_distribution()
    # Breaks if hr_expense_analytic not installed!
```

**Solution**: Check module installation before using

```python
# ✅ CORRECT: Check module before using
@openupgrade.migrate()
def migrate(env, version):
    # Check if dependency module installed
    if openupgrade.is_module_installed(env.cr, 'hr_expense_analytic'):
        env['hr.expense'].search([])._compute_analytic_distribution()
    else:
        _logger.warning(
            "hr_expense_analytic not installed, skipping analytic migration"
        )
```

---

## Additional Resources

### OCA OpenUpgrade Documentation
- **GitHub**: https://github.com/OCA/OpenUpgrade
- **Migration Guide**: https://github.com/OCA/OpenUpgrade/blob/16.0/docsource/migration_guide.rst
- **API Reference**: https://github.com/OCA/openupgradelib

### Odoo Official Documentation
- **Upgrade Documentation**: https://www.odoo.com/documentation/19.0/administration/upgrade.html
- **Migration Scripts**: https://www.odoo.com/documentation/19.0/developer/reference/backend/upgrade.html

### Community Resources
- **OCA Migration Wiki**: https://github.com/OCA/OpenUpgrade/wiki
- **Odoo Community Forums**: https://www.odoo.com/forum/help-1
- **Reddit r/Odoo**: https://www.reddit.com/r/Odoo/

---

**Best Practices Summary**:

✅ **DO**:
- Always backup database before migration
- Test migrations on copy of production data
- Use `openupgrade.logged_query()` for all SQL
- Make migrations idempotent (safe to run multiple times)
- Document breaking changes in migration script comments
- Create rollback scripts for critical migrations

❌ **DON'T**:
- Skip testing on production-like data
- Use ORM for bulk operations (>1000 records)
- Forget to handle NULL values in required fields
- Assume all dependency modules are installed
- Modify data without backup tables
- Deploy migrations without rollback plan

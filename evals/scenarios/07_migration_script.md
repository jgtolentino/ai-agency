# Eval Scenario 07: Migration Script Validation (openupgradelib)

**Skill**: odoo-module-dev
**Complexity**: High
**Estimated Time**: 7-10 minutes

---

## Objective

Validate Odoo migration scripts using openupgradelib framework:
- Create pre-migration and post-migration scripts
- Ensure data preservation during schema changes
- Implement proper rollback mechanisms
- Follow OCA migration best practices and conventions

---

## Scenario

**Task**: "Create migration scripts for upgrading `expense_approval` module from 16.0.1.0.0 to 16.0.2.0.0 with the following changes:

**Schema Changes**:
1. Rename field: `amount` → `total_amount`
2. Add new field: `currency_id` (Many2one to res.currency)
3. Split field: `user_id` → `requester_id` and `approver_id`
4. Add computed field: `approval_date` (Datetime)

**Requirements**:
- Preserve all existing expense data
- Migrate `amount` values to `total_amount`
- Set default currency based on company
- Copy `user_id` to `requester_id` for all records
- Ensure rollback capability if migration fails
- Use openupgradelib for all operations

Expected deliverables:
1. Pre-migration script (`pre-migration.py`)
2. Post-migration script (`post-migration.py`)
3. Migration test plan with rollback procedure
4. Evidence of successful data preservation"

---

## Pass Criteria

### Directory Structure
```
custom_addons/expense_approval/migrations/
└── 16.0.2.0.0/
    ├── pre-migration.py
    ├── post-migration.py
    └── README.md (migration notes)
```

### Pre-Migration Script (`pre-migration.py`)
```python
# -*- coding: utf-8 -*-
"""
Pre-migration script for expense_approval 16.0.1.0.0 -> 16.0.2.0.0

This script prepares data before Odoo loads the new module structure.
Uses openupgradelib for safe, reversible database operations.
"""
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """
    Pre-migration operations executed BEFORE module update

    Args:
        env: Odoo environment
        version: Target version string (16.0.2.0.0)
    """
    cr = env.cr

    # 1. Rename field: amount → total_amount
    # openupgradelib handles column rename safely
    if openupgrade.column_exists(cr, 'expense_approval_request', 'amount'):
        openupgrade.rename_fields(
            env,
            [
                (
                    'expense.approval.request',  # Model name
                    'expense_approval_request',  # Table name
                    'amount',                     # Old field name
                    'total_amount'                # New field name
                )
            ]
        )

    # 2. Create backup column for user_id (will be split into requester_id/approver_id)
    if openupgrade.column_exists(cr, 'expense_approval_request', 'user_id'):
        # Backup user_id data before model changes
        openupgrade.logged_query(
            cr,
            """
            ALTER TABLE expense_approval_request
            ADD COLUMN IF NOT EXISTS user_id_backup INTEGER
            """
        )
        openupgrade.logged_query(
            cr,
            """
            UPDATE expense_approval_request
            SET user_id_backup = user_id
            WHERE user_id IS NOT NULL
            """
        )

    # 3. Create placeholder for currency_id (will be populated in post-migration)
    if not openupgrade.column_exists(cr, 'expense_approval_request', 'currency_id'):
        openupgrade.logged_query(
            cr,
            """
            ALTER TABLE expense_approval_request
            ADD COLUMN IF NOT EXISTS currency_id INTEGER
            """
        )

    # 4. Log migration start
    openupgrade.logged_query(
        cr,
        """
        INSERT INTO ir_logging (name, type, dbname, level, message, path, line, func, create_date)
        VALUES (
            'expense_approval.migration',
            'server',
            current_database(),
            'INFO',
            'Pre-migration 16.0.2.0.0 started',
            'migrations/16.0.2.0.0/pre-migration.py',
            0,
            'migrate',
            NOW()
        )
        """
    )
```

### Post-Migration Script (`post-migration.py`)
```python
# -*- coding: utf-8 -*-
"""
Post-migration script for expense_approval 16.0.1.0.0 -> 16.0.2.0.0

This script populates new fields and validates data after module update.
Ensures data integrity and applies business logic to migrated records.
"""
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """
    Post-migration operations executed AFTER module update

    Args:
        env: Odoo environment
        version: Target version string (16.0.2.0.0)
    """
    cr = env.cr

    # 1. Migrate user_id → requester_id (copy all values)
    if openupgrade.column_exists(cr, 'expense_approval_request', 'user_id_backup'):
        openupgrade.logged_query(
            cr,
            """
            UPDATE expense_approval_request
            SET requester_id = user_id_backup
            WHERE user_id_backup IS NOT NULL
            """
        )

    # 2. Set default currency_id based on company
    # Get default company currency
    openupgrade.logged_query(
        cr,
        """
        UPDATE expense_approval_request ear
        SET currency_id = (
            SELECT currency_id
            FROM res_company
            WHERE id = COALESCE(ear.company_id, 1)
            LIMIT 1
        )
        WHERE currency_id IS NULL
        """
    )

    # 3. Validate data migration
    # Check: All records have total_amount
    cr.execute(
        """
        SELECT COUNT(*)
        FROM expense_approval_request
        WHERE total_amount IS NULL AND state != 'draft'
        """
    )
    missing_amounts = cr.fetchone()[0]
    if missing_amounts > 0:
        raise openupgrade.MigrationError(
            f"Migration failed: {missing_amounts} records missing total_amount"
        )

    # Check: All records have requester_id
    cr.execute(
        """
        SELECT COUNT(*)
        FROM expense_approval_request
        WHERE requester_id IS NULL
        """
    )
    missing_requesters = cr.fetchone()[0]
    if missing_requesters > 0:
        raise openupgrade.MigrationError(
            f"Migration failed: {missing_requesters} records missing requester_id"
        )

    # Check: All records have currency_id
    cr.execute(
        """
        SELECT COUNT(*)
        FROM expense_approval_request
        WHERE currency_id IS NULL
        """
    )
    missing_currency = cr.fetchone()[0]
    if missing_currency > 0:
        raise openupgrade.MigrationError(
            f"Migration failed: {missing_currency} records missing currency_id"
        )

    # 4. Clean up backup columns
    if openupgrade.column_exists(cr, 'expense_approval_request', 'user_id_backup'):
        openupgrade.logged_query(
            cr,
            """
            ALTER TABLE expense_approval_request
            DROP COLUMN IF EXISTS user_id_backup
            """
        )

    # 5. Refresh view definitions (if any view changes)
    openupgrade.load_data(
        cr,
        'expense_approval',
        'views/expense_approval_views.xml'
    )

    # 6. Log migration completion
    openupgrade.logged_query(
        cr,
        """
        INSERT INTO ir_logging (name, type, dbname, level, message, path, line, func, create_date)
        VALUES (
            'expense_approval.migration',
            'server',
            current_database(),
            'INFO',
            'Post-migration 16.0.2.0.0 completed successfully',
            'migrations/16.0.2.0.0/post-migration.py',
            0,
            'migrate',
            NOW()
        )
        """
    )
```

### Migration README (`README.md`)
```markdown
# Migration 16.0.1.0.0 → 16.0.2.0.0

**Date**: 2025-11-01
**Author**: Odoo Expertise Agent
**Type**: Schema and data migration

## Changes

### Field Operations
1. **Renamed**: `amount` → `total_amount`
2. **Added**: `currency_id` (Many2one to res.currency)
3. **Split**: `user_id` → `requester_id` + `approver_id`
4. **Added**: `approval_date` (computed Datetime)

### Data Migration
- All existing `amount` values preserved in `total_amount`
- `currency_id` populated from company default currency
- `user_id` copied to `requester_id` for all records
- Backup columns created and cleaned up post-migration

## Rollback Procedure

If migration fails or needs rollback:

1. **Stop Odoo**: `sudo systemctl stop odoo`
2. **Restore Database**: `psql -U odoo -d production < backup_before_migration.sql`
3. **Downgrade Module**: Change `__manifest__.py` version back to `16.0.1.0.0`
4. **Restart Odoo**: `sudo systemctl start odoo`
5. **Update Module**: `odoo-bin -u expense_approval --stop-after-init`

## Testing Checklist

- [ ] Pre-migration script runs without errors
- [ ] Post-migration script runs without errors
- [ ] All existing expense records preserved
- [ ] `total_amount` values match original `amount`
- [ ] All records have valid `currency_id`
- [ ] All records have valid `requester_id`
- [ ] UI displays updated fields correctly
- [ ] Rollback procedure tested successfully

## Dependencies

- `openupgradelib>=3.0.0`
- Database backup before migration
- Staging environment for testing
```

### Validation Checklist
- ✅ Pre-migration script creates backups before schema changes
- ✅ Post-migration script populates new fields with valid data
- ✅ Data validation checks prevent partial migration
- ✅ Rollback procedure documented and tested
- ✅ openupgradelib functions used (no raw SQL for schema changes)
- ✅ Migration logs track execution progress
- ✅ All existing data preserved (0% data loss)

---

## Execution

### Automated Check
```bash
#!/bin/bash
set -e

MIGRATION_DIR="custom_addons/expense_approval/migrations/16.0.2.0.0"

echo "🧪 Eval Scenario 07: Migration Script Validation"
echo "================================================"

# Test 1: Migration directory structure
echo "Test 1: Migration Directory Structure"
if [ -f "$MIGRATION_DIR/pre-migration.py" ] && \
   [ -f "$MIGRATION_DIR/post-migration.py" ] && \
   [ -f "$MIGRATION_DIR/README.md" ]; then
    echo "✅ Migration files present"
else
    echo "❌ Missing migration files"
    exit 1
fi

# Test 2: Pre-migration script validation
echo ""
echo "Test 2: Pre-migration Script Validation"
if grep -q "openupgradelib" "$MIGRATION_DIR/pre-migration.py" && \
   grep -q "@openupgrade.migrate()" "$MIGRATION_DIR/pre-migration.py" && \
   grep -q "rename_fields\|logged_query" "$MIGRATION_DIR/pre-migration.py"; then
    echo "✅ Pre-migration uses openupgradelib"
else
    echo "❌ Pre-migration missing openupgradelib"
    exit 1
fi

# Test 3: Post-migration script validation
echo ""
echo "Test 3: Post-migration Script Validation"
if grep -q "openupgradelib" "$MIGRATION_DIR/post-migration.py" && \
   grep -q "MigrationError" "$MIGRATION_DIR/post-migration.py" && \
   grep -q "SELECT COUNT" "$MIGRATION_DIR/post-migration.py"; then
    echo "✅ Post-migration has data validation"
else
    echo "❌ Post-migration missing validation checks"
    exit 1
fi

# Test 4: Rollback documentation
echo ""
echo "Test 4: Rollback Procedure Documentation"
if grep -q "Rollback Procedure" "$MIGRATION_DIR/README.md" && \
   grep -q "Restore Database" "$MIGRATION_DIR/README.md"; then
    echo "✅ Rollback procedure documented"
else
    echo "❌ Missing rollback documentation"
    exit 1
fi

# Test 5: Data preservation checks
echo ""
echo "Test 5: Data Preservation Validation"
if grep -q "user_id_backup" "$MIGRATION_DIR/pre-migration.py" && \
   grep -q "DROP COLUMN.*user_id_backup" "$MIGRATION_DIR/post-migration.py"; then
    echo "✅ Backup columns created and cleaned up"
else
    echo "❌ Missing data backup strategy"
    exit 1
fi

echo ""
echo "================================================"
echo "✅ Eval Scenario 07: PASS - Migration Scripts Valid"
echo "================================================"
```

---

## Expected Output

```
🧪 Eval Scenario 07: Migration Script Validation
================================================

Migration Plan: expense_approval 16.0.1.0.0 → 16.0.2.0.0

Schema Changes:
1. ✅ Rename: amount → total_amount (openupgrade.rename_fields)
2. ✅ Add: currency_id (ALTER TABLE with backup)
3. ✅ Split: user_id → requester_id + approver_id (backup strategy)
4. ✅ Add: approval_date (computed field, no migration)

Pre-Migration Operations:
- Rename amount column to total_amount
- Create user_id_backup for safe field splitting
- Create currency_id placeholder column
- Log migration start

Post-Migration Operations:
- Copy user_id_backup → requester_id
- Populate currency_id from company defaults
- Validate: 0 records missing total_amount
- Validate: 0 records missing requester_id
- Validate: 0 records missing currency_id
- Clean up backup columns
- Log migration completion

Rollback Procedure:
1. Stop Odoo service
2. Restore pre-migration database backup
3. Downgrade module version in __manifest__.py
4. Restart and update module

Testing Results:
✅ All 500 existing expense records preserved
✅ Data validation: 0 errors
✅ Rollback tested successfully in staging

RESULT: PASS - Migration scripts complete and validated
```

---

## Failure Modes

### Common Failures
1. **No Backup Strategy**: Directly modifying columns without backup
2. **Missing Validation**: Not checking data integrity post-migration
3. **Raw SQL**: Using raw SQL instead of openupgradelib functions
4. **No Rollback Plan**: Can't undo migration if something fails
5. **Partial Migration**: Some records updated, others not (data inconsistency)

### Remediation
- Always use openupgradelib for schema changes
- Create backup columns before destructive operations
- Validate data after each migration step
- Test rollback procedure in staging before production
- Use `MigrationError` to stop on validation failures

---

## OCA Best Practices

**Migration Script Guidelines**:
1. ✅ Use `openupgradelib` for all schema operations
2. ✅ Separate pre-migration (schema prep) and post-migration (data population)
3. ✅ Create backup columns before splitting/renaming fields
4. ✅ Validate data integrity with SELECT COUNT queries
5. ✅ Log migration progress for debugging
6. ❌ Never use raw `ALTER TABLE` for renames (use `openupgrade.rename_fields`)
7. ❌ Never skip data validation checks

**Testing Requirements**:
- Test in staging environment first
- Create database backup before migration
- Verify rollback procedure works
- Check 100% data preservation
- Validate all new fields populated correctly

---

## References

- [openupgradelib Documentation](https://github.com/OCA/openupgradelib)
- [OCA Migration Guidelines](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-X.0)
- [Odoo Migration Best Practices](https://www.odoo.com/documentation/16.0/developer/howtos/upgrade_scripts.html)
- Knowledge Base: Sprint 3 DEV3 migration patterns (upcoming)

---

**Last Reviewed**: 2025-11-01
**Maintainer**: Odoo Expertise Agent (QA2)
**Sprint**: Sprint 3 - QA Track

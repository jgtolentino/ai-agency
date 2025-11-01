#!/usr/bin/env python3
"""
Odoo Migration Script Template with openupgradelib

This template provides a comprehensive structure for creating migration scripts
for Odoo version upgrades.

**Usage**:
1. Copy this template to your module's migrations directory
2. Rename to match target version (e.g., migrations/17.0.1.0/pre-migrate.py)
3. Implement the migration functions for your specific needs
4. Test on copy of production database before deploying

**Directory Structure**:
my_module/
├── migrations/
│   ├── 16.0.1.0/
│   │   ├── pre-migrate.py
│   │   └── post-migrate.py
│   ├── 17.0.1.0/
│   │   ├── pre-migrate.py
│   │   └── post-migrate.py

**References**:
- OpenUpgrade API: https://github.com/OCA/openupgradelib
- Migration Guide: https://github.com/OCA/OpenUpgrade/blob/16.0/docsource/migration_guide.rst
"""

import logging
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


# ==============================================================================
# CONFIGURATION SECTION
# ==============================================================================

# Module information
MODULE_NAME = 'my_module'
SOURCE_VERSION = '16.0.1.0'
TARGET_VERSION = '17.0.1.0'

# Field renames: {model_name: [(old_field, new_field), ...]}
FIELD_RENAMES = {
    # Example: Rename 'state' to 'status' in expense.report
    # 'expense.report': [
    #     ('state', 'status'),
    #     ('user_id', 'employee_id'),
    # ],
}

# Model renames: [(old_model, new_model), ...]
MODEL_RENAMES = [
    # Example: Rename expense.report to hr.expense.sheet
    # ('expense.report', 'hr.expense.sheet'),
]

# Table renames: [(old_table, new_table), ...]
# Usually auto-derived from MODEL_RENAMES, but can be specified explicitly
TABLE_RENAMES = [
    # Example: Rename expense_report table to hr_expense_sheet
    # ('expense_report', 'hr_expense_sheet'),
]

# XML ID renames: [(old_xml_id, new_xml_id), ...]
XMLID_RENAMES = [
    # Example: Rename view XML IDs
    # ('my_module.expense_report_form_view', 'my_module.hr_expense_sheet_form_view'),
]

# Records to delete: [(module, xml_id), ...]
RECORDS_TO_DELETE = [
    # Example: Delete deprecated views
    # ('my_module', 'deprecated_view'),
]


# ==============================================================================
# PRE-MIGRATION FUNCTIONS
# ==============================================================================

def pre_migration_backup_data(cr):
    """
    Create backup tables for data that will be transformed or deleted.

    This function should:
    - Create backup tables for fields being removed
    - Store original values before transformation
    - Create mapping tables for complex migrations

    Example:
        CREATE TABLE expense_report_backup AS
        SELECT id, old_field, deprecated_column
        FROM expense_report
        WHERE old_field IS NOT NULL
    """
    _logger.info("Creating backup tables...")

    # Example: Backup deprecated fields
    if openupgrade.column_exists(cr, 'expense_report', 'old_field'):
        openupgrade.logged_query(
            cr,
            """
            CREATE TABLE IF NOT EXISTS {}_backup AS
            SELECT id, old_field, deprecated_column
            FROM expense_report
            WHERE old_field IS NOT NULL
            """.format('expense_report')
        )
        _logger.info("✅ Backed up expense_report.old_field")


def pre_migration_create_helper_tables(cr):
    """
    Create temporary tables for migration processing.

    These tables help with:
    - Mapping old IDs to new IDs
    - Tracking migration progress
    - Storing intermediate transformation results

    Example:
        CREATE TABLE migration_expense_mapping (
            old_id INTEGER,
            new_id INTEGER,
            migrated BOOLEAN DEFAULT FALSE
        )
    """
    _logger.info("Creating migration helper tables...")

    # Example: Create ID mapping table
    openupgrade.logged_query(
        cr,
        """
        CREATE TABLE IF NOT EXISTS migration_{}_mapping (
            old_id INTEGER PRIMARY KEY,
            new_id INTEGER,
            migrated BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT NOW()
        )
        """.format(MODULE_NAME)
    )
    _logger.info("✅ Created migration mapping table")


def pre_migration_handle_dependencies(cr):
    """
    Handle module dependencies and check for required modules.

    This function should:
    - Verify required modules are installed
    - Handle optional module dependencies
    - Log warnings for missing optional modules
    """
    _logger.info("Checking module dependencies...")

    # Example: Check if required module is installed
    required_modules = ['hr', 'account']
    for module in required_modules:
        if not openupgrade.is_module_installed(cr, module):
            raise Exception(
                f"Required module '{module}' is not installed. "
                f"Install it before running migration."
            )

    # Example: Check optional modules
    optional_modules = ['hr_expense_analytic', 'project']
    for module in optional_modules:
        if not openupgrade.is_module_installed(cr, module):
            _logger.warning(
                f"Optional module '{module}' not installed. "
                f"Some migration features will be skipped."
            )


def pre_migration_schema_changes(cr):
    """
    Perform schema-level changes before Odoo sees new model definitions.

    This is the critical pre-migration step that handles:
    - Adding new columns with default values
    - Changing column types
    - Adding constraints that are referenced later

    IMPORTANT: Changes here happen BEFORE Odoo's ORM updates the schema
    """
    _logger.info("Applying schema changes...")

    # Example: Add new required column with default
    if not openupgrade.column_exists(cr, 'expense_report', 'status'):
        openupgrade.logged_query(
            cr,
            """
            ALTER TABLE expense_report
            ADD COLUMN status VARCHAR(50) DEFAULT 'draft'
            """
        )
        _logger.info("✅ Added expense_report.status column")

    # Example: Change column type (via copy)
    if openupgrade.column_exists(cr, 'expense_report', 'old_amount'):
        openupgrade.logged_query(
            cr,
            """
            ALTER TABLE expense_report
            ADD COLUMN amount_new NUMERIC(12, 2)
            """
        )
        openupgrade.logged_query(
            cr,
            """
            UPDATE expense_report
            SET amount_new = old_amount::NUMERIC
            WHERE old_amount IS NOT NULL
            """
        )
        _logger.info("✅ Converted expense_report.amount to NUMERIC")


@openupgrade.migrate()
def migrate(env, version):
    """
    Main pre-migration entry point.

    Execution order:
    1. Check dependencies
    2. Backup data
    3. Create helper tables
    4. Schema changes
    5. Rename fields/models/tables
    6. Delete deprecated records

    This runs BEFORE Odoo updates models with new definitions.
    """
    cr = env.cr

    _logger.info("="*80)
    _logger.info(f"Starting PRE-migration: {SOURCE_VERSION} → {TARGET_VERSION}")
    _logger.info("="*80)

    # Step 1: Check dependencies
    pre_migration_handle_dependencies(cr)

    # Step 2: Backup data that will be transformed
    pre_migration_backup_data(cr)

    # Step 3: Create helper tables for migration tracking
    pre_migration_create_helper_tables(cr)

    # Step 4: Schema changes (must happen before renames)
    pre_migration_schema_changes(cr)

    # Step 5: Rename fields (preserves data with new names)
    if FIELD_RENAMES:
        _logger.info("Renaming fields...")
        openupgrade.rename_fields(env, FIELD_RENAMES)
        _logger.info("✅ Field renames completed")

    # Step 6: Rename models
    if MODEL_RENAMES:
        _logger.info("Renaming models...")
        openupgrade.rename_models(cr, MODEL_RENAMES)
        _logger.info("✅ Model renames completed")

    # Step 7: Rename tables (if not auto-derived from model renames)
    if TABLE_RENAMES:
        _logger.info("Renaming tables...")
        openupgrade.rename_tables(cr, TABLE_RENAMES)
        _logger.info("✅ Table renames completed")

    # Step 8: Rename XML IDs
    if XMLID_RENAMES:
        _logger.info("Renaming XML IDs...")
        openupgrade.rename_xmlids(cr, XMLID_RENAMES)
        _logger.info("✅ XML ID renames completed")

    # Step 9: Delete deprecated records
    if RECORDS_TO_DELETE:
        _logger.info("Deleting deprecated records...")
        openupgrade.delete_records_safely_by_xml_id(
            env,
            [f"{module}.{xml_id}" for module, xml_id in RECORDS_TO_DELETE]
        )
        _logger.info("✅ Deprecated records deleted")

    _logger.info("="*80)
    _logger.info("PRE-migration completed successfully")
    _logger.info("="*80)


# ==============================================================================
# POST-MIGRATION FUNCTIONS
# ==============================================================================

def post_migration_transform_data(env):
    """
    Transform data to fit new schema requirements.

    This function handles:
    - Status value transformations
    - Computed field calculations
    - Data normalization
    - Default value population

    Example:
        UPDATE hr_expense_sheet
        SET status = CASE
            WHEN status = 'submitted' THEN 'pending'
            WHEN status = 'approved' THEN 'done'
            ELSE status
        END
    """
    cr = env.cr
    _logger.info("Transforming data...")

    # Example: Transform status values
    status_mapping = {
        'submitted': 'pending',
        'approved': 'done',
        # 'draft' stays the same
    }

    for old_value, new_value in status_mapping.items():
        openupgrade.logged_query(
            cr,
            """
            UPDATE hr_expense_sheet
            SET status = %s
            WHERE status = %s
            """,
            (new_value, old_value)
        )

    _logger.info("✅ Status values transformed")


def post_migration_compute_fields(env):
    """
    Recompute computed fields and trigger business logic.

    This function:
    - Triggers @api.depends computed fields
    - Recalculates aggregated values
    - Ensures data consistency

    Use ORM for this to properly trigger all decorators.
    """
    _logger.info("Computing fields...")

    # Example: Recompute expense sheet totals
    ExpenseSheet = env['hr.expense.sheet']

    # Find sheets with missing computed values
    sheets_to_compute = ExpenseSheet.search([
        '|',
        ('total_amount', '=', 0),
        ('expense_count', '=', 0)
    ])

    _logger.info(f"Found {len(sheets_to_compute)} sheets to recompute")

    # Process in batches
    BATCH_SIZE = 1000
    for i in range(0, len(sheets_to_compute), BATCH_SIZE):
        batch = sheets_to_compute[i:i+BATCH_SIZE]

        for sheet in batch:
            sheet._compute_total_amount()
            sheet._compute_expense_count()

        # Commit each batch
        env.cr.commit()

        _logger.info(
            f"Processed batch {i//BATCH_SIZE + 1} "
            f"({min(i+BATCH_SIZE, len(sheets_to_compute))}/{len(sheets_to_compute)})"
        )

    _logger.info("✅ Field computation completed")


def post_migration_data_validation(env):
    """
    Validate migrated data integrity.

    This function should:
    - Check for NULL values in required fields
    - Verify foreign key references
    - Validate business rules
    - Ensure data consistency

    Raises exception if validation fails.
    """
    cr = env.cr
    _logger.info("Validating migrated data...")

    # Example: Check for NULL values in required fields
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
            f"❌ Migration validation failed: "
            f"{null_count} records have NULL status"
        )

    # Example: Verify totals match line items
    cr.execute(
        """
        SELECT s.id, s.total_amount, SUM(e.total_amount) as computed_total
        FROM hr_expense_sheet s
        LEFT JOIN hr_expense e ON e.sheet_id = s.id
        GROUP BY s.id, s.total_amount
        HAVING ABS(s.total_amount - COALESCE(SUM(e.total_amount), 0)) > 0.01
        """
    )

    mismatched = cr.fetchall()

    if mismatched:
        _logger.warning(
            f"Found {len(mismatched)} sheets with mismatched totals. "
            f"Will recompute..."
        )
        # Auto-fix by recomputing
        for sheet_id, _, _ in mismatched:
            sheet = env['hr.expense.sheet'].browse(sheet_id)
            sheet._compute_total_amount()

    _logger.info("✅ Data validation passed")


def post_migration_cleanup(env):
    """
    Clean up temporary migration data.

    This function:
    - Drops backup tables (after verification)
    - Drops helper tables
    - Removes temporary columns
    - Cleans up migration artifacts
    """
    cr = env.cr
    _logger.info("Cleaning up migration artifacts...")

    # Drop backup tables
    backup_tables = [
        'expense_report_backup',
        f'migration_{MODULE_NAME}_mapping',
    ]

    for table in backup_tables:
        if openupgrade.table_exists(cr, table):
            openupgrade.logged_query(
                cr,
                f"DROP TABLE IF EXISTS {table} CASCADE"
            )
            _logger.info(f"✅ Dropped {table}")

    # Drop temporary columns
    if openupgrade.column_exists(cr, 'hr_expense_sheet', 'old_amount'):
        openupgrade.logged_query(
            cr,
            """
            ALTER TABLE hr_expense_sheet
            DROP COLUMN IF EXISTS old_amount
            """
        )
        _logger.info("✅ Dropped temporary columns")

    _logger.info("✅ Cleanup completed")


def post_migration_update_sequences(env):
    """
    Update database sequences to avoid ID conflicts.

    This is important when:
    - Merging data from multiple tables
    - Importing data with specific IDs
    - Preventing duplicate ID issues
    """
    cr = env.cr
    _logger.info("Updating database sequences...")

    # Example: Update expense sheet sequence
    openupgrade.logged_query(
        cr,
        """
        SELECT setval(
            'hr_expense_sheet_id_seq',
            (SELECT MAX(id) FROM hr_expense_sheet)
        )
        """
    )

    _logger.info("✅ Sequences updated")


# Uncomment for POST-migration script
# @openupgrade.migrate()
# def migrate(env, version):
#     """
#     Main post-migration entry point.
#
#     Execution order:
#     1. Transform data to new schema
#     2. Compute fields with ORM
#     3. Update sequences
#     4. Validate data integrity
#     5. Clean up migration artifacts
#
#     This runs AFTER Odoo has updated models with new definitions.
#     """
#     _logger.info("="*80)
#     _logger.info(f"Starting POST-migration: {SOURCE_VERSION} → {TARGET_VERSION}")
#     _logger.info("="*80)
#
#     # Step 1: Transform data
#     post_migration_transform_data(env)
#
#     # Step 2: Compute fields
#     post_migration_compute_fields(env)
#
#     # Step 3: Update sequences
#     post_migration_update_sequences(env)
#
#     # Step 4: Validate data
#     post_migration_data_validation(env)
#
#     # Step 5: Cleanup
#     post_migration_cleanup(env)
#
#     _logger.info("="*80)
#     _logger.info("POST-migration completed successfully")
#     _logger.info("="*80)


# ==============================================================================
# ROLLBACK FUNCTIONS (Use in emergency rollback script)
# ==============================================================================

def rollback_field_renames(env):
    """Reverse field renames to restore original names"""
    # Reverse the FIELD_RENAMES mapping
    field_rollbacks = {}

    for model, renames in FIELD_RENAMES.items():
        field_rollbacks[model] = [
            (new_field, old_field)  # Swap order
            for old_field, new_field in renames
        ]

    if field_rollbacks:
        openupgrade.rename_fields(env, field_rollbacks)
        _logger.info("✅ Field names restored")


def rollback_model_renames(cr):
    """Reverse model renames to restore original names"""
    # Reverse the MODEL_RENAMES list
    model_rollbacks = [
        (new_model, old_model)  # Swap order
        for old_model, new_model in MODEL_RENAMES
    ]

    if model_rollbacks:
        openupgrade.rename_models(cr, model_rollbacks)
        _logger.info("✅ Model names restored")


def rollback_restore_backup_data(cr):
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
        _logger.info("✅ Backup data restored")


# Uncomment for ROLLBACK script
# @openupgrade.migrate()
# def migrate(env, version):
#     """
#     Emergency rollback script.
#
#     Use this when migration fails and must be reverted.
#     Only use on test database first!
#     """
#     cr = env.cr
#
#     _logger.warning("="*80)
#     _logger.warning("ROLLING BACK MIGRATION - THIS IS DESTRUCTIVE!")
#     _logger.warning("="*80)
#
#     # Restore in reverse order
#     rollback_restore_backup_data(cr)
#     rollback_field_renames(env)
#     rollback_model_renames(cr)
#
#     _logger.warning("="*80)
#     _logger.warning("Rollback completed - verify data integrity!")
#     _logger.warning("="*80)


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def get_migration_stats(cr):
    """
    Get statistics about migration progress.

    Useful for monitoring large migrations.
    """
    stats = {}

    # Example: Count records by status
    cr.execute(
        """
        SELECT status, COUNT(*)
        FROM hr_expense_sheet
        GROUP BY status
        """
    )

    stats['status_counts'] = dict(cr.fetchall())

    # Example: Check migration completion
    if openupgrade.table_exists(cr, f'migration_{MODULE_NAME}_mapping'):
        cr.execute(
            f"""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN migrated THEN 1 END) as completed
            FROM migration_{MODULE_NAME}_mapping
            """
        )

        total, completed = cr.fetchone()
        stats['migration_progress'] = {
            'total': total,
            'completed': completed,
            'percentage': (completed / total * 100) if total > 0 else 0
        }

    return stats


if __name__ == '__main__':
    """
    This script is meant to be run by Odoo's migration framework.

    For testing purposes, you can run it standalone:
        python migration_template.py

    But normally it's invoked automatically during Odoo upgrade.
    """
    print(__doc__)
    print("\n⚠️  This script should be run by Odoo migration framework, not directly.")
    print("Copy to migrations/{version}/pre-migrate.py or post-migrate.py")

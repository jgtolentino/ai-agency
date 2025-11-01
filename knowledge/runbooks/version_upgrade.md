# Odoo Version Upgrade Runbook

**Version**: 1.0
**Last Updated**: 2025-11-01
**Target Audience**: Odoo developers, DevOps engineers, system administrators
**Applicable Versions**: Odoo 16.0 → 17.0 → 18.0 → 19.0

---

## Table of Contents

1. [Pre-Upgrade Planning](#1-pre-upgrade-planning)
2. [Version 16.0 → 17.0 Upgrade](#2-version-160--170-upgrade)
3. [Version 17.0 → 18.0 Upgrade](#3-version-170--180-upgrade)
4. [Version 18.0 → 19.0 Upgrade](#4-version-180--190-upgrade)
5. [Module Compatibility Matrix](#5-module-compatibility-matrix)
6. [Testing Procedures](#6-testing-procedures)
7. [Common Pitfalls and Solutions](#7-common-pitfalls-and-solutions)
8. [Emergency Rollback Procedures](#8-emergency-rollback-procedures)

---

## 1. Pre-Upgrade Planning

### 1.1 Upgrade Readiness Checklist

**⏰ Timeline**: Start planning 4-6 weeks before upgrade

✅ **Business Requirements**:
- [ ] Business justification documented
- [ ] Stakeholder approval obtained
- [ ] Maintenance window scheduled
- [ ] User communication plan created
- [ ] Rollback criteria defined

✅ **Technical Assessment**:
- [ ] Current version documented (exact commit hash)
- [ ] All custom modules inventoried
- [ ] OCA module versions identified
- [ ] Third-party integrations catalogued
- [ ] Database size and performance metrics captured

✅ **Environment Preparation**:
- [ ] Test environment created (copy of production)
- [ ] Staging environment ready
- [ ] Backup strategy validated
- [ ] Restore procedure tested
- [ ] Downtime estimate calculated

✅ **Code Preparation**:
- [ ] Custom modules updated for target version
- [ ] Deprecated API usage identified
- [ ] Migration scripts prepared
- [ ] Tests updated for new version
- [ ] Documentation updated

### 1.2 Environment Setup

```bash
#!/bin/bash
# prepare_upgrade_environment.sh

# Configuration
SOURCE_VERSION="16.0"
TARGET_VERSION="17.0"
PRODUCTION_DB="production_db"
TEST_DB="test_upgrade_${TARGET_VERSION}"
BACKUP_DIR="/backups/odoo"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Step 1: Create full backup
echo "📦 Creating production backup..."
pg_dump -U odoo -Fc -d ${PRODUCTION_DB} \
    -f "${BACKUP_DIR}/${PRODUCTION_DB}_${TIMESTAMP}.backup"

# Step 2: Create test database
echo "🔧 Creating test environment..."
createdb -U odoo ${TEST_DB}
pg_restore -U odoo -d ${TEST_DB} \
    "${BACKUP_DIR}/${PRODUCTION_DB}_${TIMESTAMP}.backup"

# Step 3: Install target version in virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv ~/odoo-${TARGET_VERSION}-venv
source ~/odoo-${TARGET_VERSION}-venv/bin/activate

# Install Odoo target version
pip install --upgrade pip
pip install wheel
git clone --depth 1 --branch ${TARGET_VERSION} \
    https://github.com/odoo/odoo.git ~/odoo-${TARGET_VERSION}
pip install -r ~/odoo-${TARGET_VERSION}/requirements.txt

# Step 4: Clone OCA modules for target version
echo "📚 Cloning OCA modules..."
mkdir -p ~/oca-modules-${TARGET_VERSION}
# Example for account-financial-tools
git clone --depth 1 --branch ${TARGET_VERSION} \
    https://github.com/OCA/account-financial-tools.git \
    ~/oca-modules-${TARGET_VERSION}/account-financial-tools

echo "✅ Environment ready for upgrade testing"
```

### 1.3 Database Analysis Script

```python
#!/usr/bin/env python3
"""
Analyze database before upgrade
Identifies potential issues and estimates migration complexity
"""

import psycopg2
import json
from collections import defaultdict

DB_CONFIG = {
    'host': 'localhost',
    'database': 'production_db',
    'user': 'odoo',
    'password': 'your_password'
}

def analyze_database():
    """Analyze database and generate upgrade report"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    report = {
        'database_size': get_database_size(cur),
        'table_sizes': get_table_sizes(cur),
        'custom_modules': get_custom_modules(cur),
        'deprecated_fields': find_deprecated_fields(cur),
        'record_counts': get_record_counts(cur),
    }

    # Generate JSON report
    with open('upgrade_analysis.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("📊 Database Analysis Report")
    print("="*80)
    print(f"Database Size: {report['database_size']}")
    print(f"Custom Modules: {len(report['custom_modules'])}")
    print(f"Largest Tables: {', '.join(list(report['table_sizes'].keys())[:5])}")
    print("="*80)

    cur.close()
    conn.close()

def get_database_size(cur):
    """Get total database size"""
    cur.execute("""
        SELECT pg_size_pretty(pg_database_size(current_database()))
    """)
    return cur.fetchone()[0]

def get_table_sizes(cur):
    """Get sizes of top 20 tables"""
    cur.execute("""
        SELECT
            schemaname || '.' || tablename as table_name,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
        FROM pg_tables
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        LIMIT 20
    """)
    return dict(cur.fetchall())

def get_custom_modules(cur):
    """Get list of installed custom modules"""
    cur.execute("""
        SELECT name, latest_version, state
        FROM ir_module_module
        WHERE state = 'installed'
          AND name NOT LIKE 'base%'
          AND author NOT LIKE '%Odoo%'
        ORDER BY name
    """)
    return [
        {'name': row[0], 'version': row[1], 'state': row[2]}
        for row in cur.fetchall()
    ]

def find_deprecated_fields(cur):
    """Find fields that may be deprecated in target version"""
    # This would need version-specific logic
    # Example for common deprecated fields
    deprecated_patterns = ['workflow', 'osv_']

    cur.execute("""
        SELECT DISTINCT model, name
        FROM ir_model_fields
        WHERE name LIKE ANY(%s)
        ORDER BY model, name
    """, ([f"%{p}%" for p in deprecated_patterns],))

    return [
        {'model': row[0], 'field': row[1]}
        for row in cur.fetchall()
    ]

def get_record_counts(cur):
    """Get record counts for major models"""
    models = [
        'res.partner',
        'account.move',
        'account.move.line',
        'sale.order',
        'purchase.order',
        'stock.picking',
        'product.product',
    ]

    counts = {}
    for model in models:
        table = model.replace('.', '_')
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            counts[model] = cur.fetchone()[0]
        except:
            counts[model] = 'N/A'

    return counts

if __name__ == '__main__':
    analyze_database()
```

---

## 2. Version 16.0 → 17.0 Upgrade

### 2.1 Breaking Changes Summary

| Area | Change | Impact | Migration Required |
|------|--------|--------|-------------------|
| **Frontend** | OWL framework mandatory | All JS widgets need rewrite | ✅ High |
| **Python** | Python 3.8+ required | Legacy code may break | ✅ Medium |
| **ORM** | `_name` vs `_inherit` stricter | Delegation inheritance changes | ✅ Medium |
| **Security** | Stricter record rules | Access denied errors | ✅ High |
| **API** | Deprecated RPC endpoints removed | External integrations break | ✅ High |
| **Views** | QWeb changes | Template rendering issues | ✅ Medium |

### 2.2 Detailed Breaking Changes

#### 2.2.1 OWL Framework (JavaScript)

**Change**: All JavaScript widgets must use OWL framework

**Before (16.0)**:
```javascript
odoo.define('my_module.MyWidget', function (require) {
    var Widget = require('web.Widget');

    var MyWidget = Widget.extend({
        template: 'my_module.MyTemplate',
        events: {
            'click .my-button': '_onClickButton',
        },
        _onClickButton: function() {
            // Handle click
        }
    });

    return MyWidget;
});
```

**After (17.0)**:
```javascript
/** @odoo-module **/
import { Component } from "@odoo/owl";

export class MyWidget extends Component {
    static template = "my_module.MyTemplate";

    onClickButton() {
        // Handle click
    }
}
```

**Migration Steps**:
1. Convert all Widget extensions to OWL Components
2. Update QWeb templates to OWL syntax (t-on-click instead of events)
3. Replace jQuery with OWL refs and state management
4. Test all interactive widgets thoroughly

#### 2.2.2 Model Inheritance Changes

**Change**: Stricter validation of `_name` vs `_inherit`

**Problem Code**:
```python
# ❌ WRONG in 17.0
class ExpenseReport(models.Model):
    _name = 'hr.expense.sheet'
    _inherit = 'hr.expense.sheet'  # Creates conflict
```

**Fixed Code**:
```python
# ✅ CORRECT in 17.0
class ExpenseReport(models.Model):
    _inherit = 'hr.expense.sheet'  # Extension only, no _name
```

**Migration Script**:
```python
# migrations/17.0.1.0/pre-migrate.py
def fix_model_inheritance(cr):
    """Remove duplicate _name/_inherit conflicts"""
    # Check Python code, not database
    # This requires code review and manual fixes
    pass
```

#### 2.2.3 Security: Record Rules Stricter Evaluation

**Change**: Record rules now strictly enforce domain evaluation

**Before (16.0)**: Lenient evaluation, some invalid domains worked
**After (17.0)**: Strict evaluation, invalid domains cause errors

**Example Fix**:
```xml
<!-- Before: Could have None in domain (worked by accident) -->
<record id="expense_user_rule" model="ir.rule">
    <field name="domain_force">
        [('employee_id.user_id', '=', user.id)]
    </field>
</record>

<!-- After: Must handle None explicitly -->
<record id="expense_user_rule" model="ir.rule">
    <field name="domain_force">
        ['|',
            ('employee_id', '=', False),
            ('employee_id.user_id', '=', user.id)
        ]
    </field>
</record>
```

### 2.3 Step-by-Step Upgrade Process

#### Phase 1: Code Preparation (Week 1-2)

```bash
# 1. Create feature branch for 17.0 upgrade
git checkout -b upgrade/17.0
git push -u origin upgrade/17.0

# 2. Update manifest files
# For each module: __manifest__.py
{
    'version': '17.0.1.0.0',  # Update version
    'depends': ['base', 'hr'],  # Verify dependencies exist in 17.0
}

# 3. Update Python code
# - Fix model inheritance
# - Update deprecated API calls
# - Add migration scripts

# 4. Rewrite JavaScript widgets to OWL
# - See section 2.2.1 above

# 5. Run static analysis
flake8 --config=.flake8
pylint --rcfile=.pylintrc addons/
```

#### Phase 2: Database Migration (Week 3)

```bash
#!/bin/bash
# upgrade_to_17.sh

# Configuration
SOURCE_DB="production_db"
TARGET_DB="test_17_upgrade"
ODOO_17_PATH=~/odoo-17.0
ADDONS_PATH="${ODOO_17_PATH}/addons,~/custom_addons,~/oca-modules-17.0"

# Step 1: Backup and restore
echo "📦 Creating test database..."
pg_dump -U odoo -Fc ${SOURCE_DB} > /tmp/${SOURCE_DB}.backup
createdb -U odoo ${TARGET_DB}
pg_restore -U odoo -d ${TARGET_DB} /tmp/${SOURCE_DB}.backup

# Step 2: Update Odoo to 17.0
echo "⬆️  Running Odoo upgrade..."
${ODOO_17_PATH}/odoo-bin \
    -c odoo.conf \
    -d ${TARGET_DB} \
    --addons-path="${ADDONS_PATH}" \
    -u all \
    --stop-after-init \
    --log-level=info \
    2>&1 | tee upgrade_17.log

# Step 3: Verify upgrade
echo "✅ Checking for errors..."
grep -i "error\|exception\|traceback" upgrade_17.log > errors.log

if [ -s errors.log ]; then
    echo "❌ Errors found during upgrade!"
    cat errors.log
    exit 1
else
    echo "✅ Upgrade completed successfully"
fi
```

#### Phase 3: Testing (Week 4)

See [Section 6: Testing Procedures](#6-testing-procedures)

### 2.4 Post-Upgrade Validation

```bash
#!/bin/bash
# validate_17_upgrade.sh

DB="test_17_upgrade"

echo "🔍 Running post-upgrade validations..."

# Check module states
psql -U odoo -d ${DB} -c "
    SELECT name, state
    FROM ir_module_module
    WHERE state NOT IN ('installed', 'uninstalled')
" > module_issues.txt

# Check for broken views
psql -U odoo -d ${DB} -c "
    SELECT name, model, type
    FROM ir_ui_view
    WHERE arch_db LIKE '%error%'
       OR arch_db LIKE '%undefined%'
" > view_errors.txt

# Check for NULL required fields
psql -U odoo -d ${DB} -c "
    SELECT table_name, column_name
    FROM information_schema.columns
    WHERE is_nullable = 'NO'
      AND table_schema = 'public'
      AND table_name IN (
          SELECT table_name
          FROM information_schema.tables
          WHERE table_schema = 'public'
      )
" > required_fields.txt

# Report results
if [ -s module_issues.txt ] || [ -s view_errors.txt ]; then
    echo "❌ Validation issues found!"
    echo "Module issues: $(wc -l < module_issues.txt) lines"
    echo "View errors: $(wc -l < view_errors.txt) lines"
else
    echo "✅ All validations passed"
fi
```

---

## 3. Version 17.0 → 18.0 Upgrade

### 3.1 Breaking Changes Summary

| Area | Change | Impact | Migration Required |
|------|--------|--------|-------------------|
| **Python** | Python 3.10+ required | Match/case syntax available | ✅ Low |
| **ORM** | Many2one fields stricter | NULL values rejected | ✅ High |
| **Accounting** | Analytic accounts → distribution | Complete rewrite needed | ✅ Critical |
| **API** | XML-RPC changes | External API breaks | ✅ High |
| **Reports** | New reporting engine | Custom reports need rewrite | ✅ High |

### 3.2 Detailed Breaking Changes

#### 3.2.1 Many2one Required Fields

**Change**: Many2one fields marked `required=True` no longer accept NULL

**Problem**:
```python
# Old data has NULL values
SELECT COUNT(*) FROM hr_expense WHERE employee_id IS NULL;
# Returns: 150 records
```

**Migration Script**:
```python
# migrations/18.0.1.0/pre-migrate.py
from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    """Fix NULL values in required Many2one fields"""
    cr = env.cr

    # Find default employee (or create dummy)
    cr.execute("""
        SELECT id FROM hr_employee
        WHERE active = true
        LIMIT 1
    """)
    default_employee = cr.fetchone()

    if not default_employee:
        # Create system employee for orphaned records
        env['hr.employee'].create({
            'name': 'System (Migrated Records)',
            'user_id': env.ref('base.user_admin').id,
        })
        default_employee = cr.fetchone()

    # Update NULL values
    openupgrade.logged_query(
        cr,
        """
        UPDATE hr_expense
        SET employee_id = %s
        WHERE employee_id IS NULL
        """,
        (default_employee[0],)
    )
```

#### 3.2.2 Analytic Accounts → Analytic Distribution

**Change**: `analytic_account_id` replaced with `analytic_distribution` (JSONB)

**Old Structure**:
```python
analytic_account_id = fields.Many2one('account.analytic.account')
```

**New Structure**:
```python
analytic_distribution = fields.Json()
# Format: {account_id: percentage, ...}
# Example: {"1": 50, "2": 50} = 50% to account 1, 50% to account 2
```

**Migration Script**:
```python
# migrations/18.0.1.0/post-migrate.py
from openupgradelib import openupgrade
import json

@openupgrade.migrate()
def migrate(env, version):
    """Migrate analytic_account_id to analytic_distribution"""
    cr = env.cr

    # Convert single account to 100% distribution
    openupgrade.logged_query(
        cr,
        """
        UPDATE account_move_line
        SET analytic_distribution = json_build_object(
            analytic_account_id::text, 100
        )::jsonb
        WHERE analytic_account_id IS NOT NULL
          AND analytic_distribution IS NULL
        """
    )

    # Drop old column after migration
    if openupgrade.column_exists(cr, 'account_move_line', 'analytic_account_id'):
        openupgrade.logged_query(
            cr,
            """
            ALTER TABLE account_move_line
            DROP COLUMN analytic_account_id
            """
        )
```

### 3.3 Step-by-Step Upgrade Process

#### Phase 1: Code Preparation

```bash
# 1. Update Python version requirement
# In .python-version or venv
python3.10 -m venv ~/odoo-18.0-venv

# 2. Update manifest files
{
    'version': '18.0.1.0.0',
    'depends': [...],  # Check OCA compatibility matrix
}

# 3. Fix Many2one required fields
# Add defaults or migration scripts

# 4. Migrate analytic accounts
# See section 3.2.2 above
```

#### Phase 2: Database Migration

```bash
#!/bin/bash
# upgrade_to_18.sh

ODOO_18_PATH=~/odoo-18.0

# Run upgrade
${ODOO_18_PATH}/odoo-bin \
    -c odoo.conf \
    -d test_18_upgrade \
    -u all \
    --stop-after-init \
    --log-level=info
```

---

## 4. Version 18.0 → 19.0 Upgrade

### 4.1 Breaking Changes Summary

| Area | Change | Impact | Migration Required |
|------|--------|--------|-------------------|
| **Workflow** | Workflow engine removed | State machine manual | ✅ Critical |
| **Reporting** | Complete rewrite | All custom reports | ✅ Critical |
| **ORM** | Field type changes | Data migration | ✅ Medium |
| **Security** | New RLS engine | Performance impact | ✅ Medium |

### 4.2 Detailed Breaking Changes

#### 4.2.1 Workflow Engine Removal

**Change**: Complete removal of `wkf_*` tables and workflow system

**Migration Strategy**:
```python
# migrations/19.0.1.0/pre-migrate.py
from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    """Remove workflow dependencies"""
    cr = env.cr

    # Delete all workflow data
    tables_to_drop = [
        'wkf',
        'wkf_activity',
        'wkf_instance',
        'wkf_transition',
        'wkf_triggers',
        'wkf_workitem',
    ]

    for table in tables_to_drop:
        if openupgrade.table_exists(cr, table):
            openupgrade.logged_query(
                cr,
                f"DROP TABLE IF EXISTS {table} CASCADE"
            )

    # State transitions now handled in code
    # Ensure state field exists and has proper values
```

**Replace Workflow with State Machine**:
```python
# Before (16.0-18.0): Used workflow
# After (19.0): Manual state machine

class ExpenseSheet(models.Model):
    _name = 'hr.expense.sheet'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('cancel', 'Refused'),
    ], default='draft', required=True)

    def action_submit(self):
        """Submit expense sheet for approval"""
        self.write({'state': 'submit'})

    def action_approve(self):
        """Approve expense sheet"""
        self.write({'state': 'approve'})

    def action_refuse(self):
        """Refuse expense sheet"""
        self.write({'state': 'cancel'})
```

### 4.3 Step-by-Step Upgrade Process

```bash
#!/bin/bash
# upgrade_to_19.sh

# Important: Remove workflow first
psql -U odoo -d test_19_upgrade << EOF
DROP TABLE IF EXISTS wkf CASCADE;
DROP TABLE IF EXISTS wkf_activity CASCADE;
DROP TABLE IF EXISTS wkf_instance CASCADE;
DROP TABLE IF EXISTS wkf_transition CASCADE;
DROP TABLE IF EXISTS wkf_triggers CASCADE;
DROP TABLE IF EXISTS wkf_workitem CASCADE;
EOF

# Run upgrade
~/odoo-19.0/odoo-bin -c odoo.conf -d test_19_upgrade -u all --stop-after-init
```

---

## 5. Module Compatibility Matrix

### 5.1 OCA Module Compatibility

| Module | 16.0 | 17.0 | 18.0 | 19.0 | Notes |
|--------|------|------|------|------|-------|
| account-financial-reporting | ✅ | ✅ | ✅ | ✅ | Stable |
| account-financial-tools | ✅ | ✅ | ✅ | ⚠️ | In progress |
| hr-expense | ✅ | ✅ | ✅ | ✅ | Stable |
| mis-builder | ✅ | ✅ | ✅ | ❌ | Not migrated |
| web-responsive | ✅ | ✅ | ✅ | ✅ | Stable |
| queue-job | ✅ | ✅ | ✅ | ✅ | Stable |
| report-xlsx | ✅ | ✅ | ✅ | ✅ | Stable |
| server-tools | ✅ | ✅ | ✅ | ✅ | Stable |

**Legend**:
- ✅ Fully compatible and tested
- ⚠️ Compatible with limitations
- ❌ Not available or broken

### 5.2 Custom Module Upgrade Checklist

For each custom module, verify:

✅ **Code Compatibility**:
- [ ] Python syntax compatible with target version
- [ ] No use of deprecated APIs
- [ ] ORM patterns follow new conventions
- [ ] JavaScript rewritten for OWL (if 16→17)

✅ **Dependencies**:
- [ ] All `depends` modules available in target version
- [ ] OCA modules migrated to target version
- [ ] Third-party modules compatible

✅ **Database Schema**:
- [ ] Migration scripts created
- [ ] Field renames handled
- [ ] Model renames handled
- [ ] Data transformations planned

✅ **Testing**:
- [ ] Unit tests updated
- [ ] Integration tests pass
- [ ] Manual testing completed

---

## 6. Testing Procedures

### 6.1 Pre-Upgrade Testing

#### Test Plan Template

```markdown
# Upgrade Test Plan: 16.0 → 17.0

## Environment
- Test Database: copy of production (2025-11-01)
- Odoo Version: 17.0 (commit: abc123)
- Python Version: 3.10.12
- Custom Modules: hr_expense_custom, accounting_custom

## Test Scenarios

### 1. Module Installation
- [ ] All modules install without errors
- [ ] No module state = 'to upgrade' stuck
- [ ] No missing dependencies

### 2. Data Integrity
- [ ] All records accessible
- [ ] No NULL in required fields
- [ ] Foreign key constraints valid
- [ ] Computed fields correct

### 3. Business Workflows
- [ ] Create new expense report
- [ ] Submit for approval
- [ ] Approve/reject
- [ ] Post to accounting
- [ ] Generate reports

### 4. Performance
- [ ] List view load time < 2s
- [ ] Form view load time < 1s
- [ ] Search performance acceptable
- [ ] Report generation < 30s

### 5. Security
- [ ] Record rules working
- [ ] Access rights correct
- [ ] Multi-company isolation
- [ ] User permissions valid

## Test Results

| Scenario | Status | Notes |
|----------|--------|-------|
| Module Installation | ✅ | All passed |
| Data Integrity | ⚠️ | 5 NULL employee_id fixed |
| Business Workflows | ✅ | All passed |
| Performance | ✅ | Within targets |
| Security | ✅ | All passed |

## Issues Found

1. **NULL employee_id in hr_expense**: Fixed with migration script
2. **Slow report generation**: Added index on date field

## Sign-Off
- Developer: [Name] - [Date]
- QA: [Name] - [Date]
- Business Owner: [Name] - [Date]
```

### 6.2 Automated Testing Script

```bash
#!/bin/bash
# automated_upgrade_test.sh

DB="test_upgrade"
ODOO_BIN=~/odoo-17.0/odoo-bin
LOG_FILE="upgrade_test_$(date +%Y%m%d_%H%M%S).log"

echo "🧪 Starting automated upgrade tests..." | tee -a $LOG_FILE

# Test 1: Module installation
echo "Test 1: Module installation" | tee -a $LOG_FILE
${ODOO_BIN} -c odoo.conf -d ${DB} --test-enable --stop-after-init \
    2>&1 | tee -a $LOG_FILE

# Test 2: Database integrity
echo "Test 2: Database integrity" | tee -a $LOG_FILE
psql -U odoo -d ${DB} -f tests/integrity_checks.sql >> $LOG_FILE 2>&1

# Test 3: Python unit tests
echo "Test 3: Unit tests" | tee -a $LOG_FILE
${ODOO_BIN} -c odoo.conf -d ${DB} --test-enable --stop-after-init \
    --test-tags="/my_module" >> $LOG_FILE 2>&1

# Test 4: Performance benchmarks
echo "Test 4: Performance" | tee -a $LOG_FILE
python3 tests/performance_benchmarks.py >> $LOG_FILE 2>&1

# Generate report
echo "📊 Test Summary:" | tee -a $LOG_FILE
grep -c "PASSED" $LOG_FILE | xargs echo "Passed:" | tee -a $LOG_FILE
grep -c "FAILED" $LOG_FILE | xargs echo "Failed:" | tee -a $LOG_FILE
grep -c "ERROR" $LOG_FILE | xargs echo "Errors:" | tee -a $LOG_FILE
```

---

## 7. Common Pitfalls and Solutions

### 7.1 Pitfall: Upgrade Stuck at Module State

**Symptom**: Module stuck in "To Upgrade" state

```sql
SELECT name, state FROM ir_module_module WHERE state = 'to upgrade';
```

**Solution**:
```bash
# Force module state to installed
psql -U odoo -d production_db << EOF
UPDATE ir_module_module
SET state = 'installed'
WHERE name = 'my_stuck_module';
EOF

# Then update module
odoo-bin -c odoo.conf -d production_db -u my_stuck_module --stop-after-init
```

### 7.2 Pitfall: Views Break After Upgrade

**Symptom**: `ParseError: Invalid view definition`

**Solution**:
```bash
# Reset all views to default
psql -U odoo -d production_db << EOF
DELETE FROM ir_ui_view
WHERE model = 'my.model'
  AND (arch_db LIKE '%error%' OR arch_db LIKE '%undefined%');
EOF

# Update module to restore views
odoo-bin -c odoo.conf -d production_db -u my_module --stop-after-init
```

### 7.3 Pitfall: Performance Degradation

**Symptom**: System slow after upgrade

**Solution**:
```sql
-- Rebuild PostgreSQL statistics
VACUUM ANALYZE;

-- Reindex database
REINDEX DATABASE production_db;

-- Update PostgreSQL config for better performance
-- In postgresql.conf:
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
```

---

## 8. Emergency Rollback Procedures

### 8.1 Decision Criteria for Rollback

**ROLLBACK IMMEDIATELY if**:
- ❌ Data corruption detected
- ❌ Critical business process broken
- ❌ Security vulnerability introduced
- ❌ Performance degradation >50%

**CONSIDER FIXING if**:
- ⚠️ Minor UI issues
- ⚠️ Non-critical reports broken
- ⚠️ Performance degradation <20%

### 8.2 Rollback Procedure

```bash
#!/bin/bash
# emergency_rollback.sh

BACKUP_FILE="/backups/odoo/production_db_20251101_020000.backup"
PRODUCTION_DB="production_db"
OLD_VERSION_BIN=~/odoo-16.0/odoo-bin

echo "🚨 EMERGENCY ROLLBACK INITIATED"
echo "This will restore database to pre-upgrade state"
read -p "Are you sure? (type 'ROLLBACK' to continue): " confirm

if [ "$confirm" != "ROLLBACK" ]; then
    echo "Rollback cancelled"
    exit 1
fi

# Step 1: Stop Odoo service
echo "🛑 Stopping Odoo..."
systemctl stop odoo

# Step 2: Drop current database
echo "🗑️  Dropping current database..."
dropdb -U odoo ${PRODUCTION_DB}

# Step 3: Restore backup
echo "📦 Restoring backup..."
createdb -U odoo ${PRODUCTION_DB}
pg_restore -U odoo -d ${PRODUCTION_DB} ${BACKUP_FILE}

# Step 4: Start Odoo with old version
echo "🔄 Starting Odoo with old version..."
systemctl start odoo

# Step 5: Verify
echo "✅ Verifying rollback..."
curl -s http://localhost:8069/web/database/selector | grep -q "db_list"

if [ $? -eq 0 ]; then
    echo "✅ Rollback successful"
else
    echo "❌ Rollback verification failed"
    exit 1
fi
```

### 8.3 Post-Rollback Actions

After successful rollback:

1. **Document Failure**:
   ```markdown
   # Upgrade Failure Report

   **Date**: 2025-11-01
   **Version**: 16.0 → 17.0
   **Reason**: Data corruption in analytic accounts

   ## Root Cause
   - Migration script failed to handle NULL values
   - 500+ records with invalid analytic_distribution

   ## Resolution
   - Rolled back to 16.0
   - Fixed migration script
   - Re-testing scheduled for 2025-11-08
   ```

2. **Fix Issues**: Update migration scripts based on failure analysis

3. **Re-Test**: Test fixed migration on copy of production

4. **Reschedule**: Plan new upgrade date after successful testing

---

## Appendix A: Useful SQL Queries

```sql
-- Find modules in bad state
SELECT name, state, latest_version
FROM ir_module_module
WHERE state NOT IN ('installed', 'uninstalled')
ORDER BY name;

-- Find views with errors
SELECT id, name, model, type, arch_db
FROM ir_ui_view
WHERE arch_db LIKE '%error%'
   OR arch_db LIKE '%undefined%';

-- Check for NULL in required fields
SELECT
    c.table_name,
    c.column_name,
    (SELECT COUNT(*) FROM information_schema.tables t
     WHERE t.table_name = c.table_name) as null_count
FROM information_schema.columns c
WHERE c.is_nullable = 'NO'
  AND c.table_schema = 'public'
  AND c.table_name NOT LIKE 'pg_%';

-- Get database statistics
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;
```

---

## Appendix B: Additional Resources

### Official Documentation
- **Odoo Upgrade Guide**: https://www.odoo.com/documentation/19.0/administration/upgrade.html
- **OCA OpenUpgrade**: https://github.com/OCA/OpenUpgrade
- **Odoo Migration Scripts**: https://github.com/odoo/odoo/tree/master/odoo/addons/base/migrations

### Community Resources
- **Odoo Forums**: https://www.odoo.com/forum/help-1
- **Reddit r/Odoo**: https://www.reddit.com/r/Odoo/
- **OCA Migration Guide**: https://github.com/OCA/OpenUpgrade/wiki

### Tools
- **openupgradelib**: https://github.com/OCA/openupgradelib
- **Odoo Analyze Tool**: https://github.com/OCA/odoo-analyze
- **Pre-commit hooks**: https://github.com/OCA/pylint-odoo

---

**Document Control**:
- **Version**: 1.0
- **Last Updated**: 2025-11-01
- **Next Review**: 2025-12-01
- **Owner**: DevOps Team
- **Approvers**: CTO, Lead Developer

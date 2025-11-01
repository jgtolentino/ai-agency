# Module Patterns Comparison

**Purpose**: Compare `~/custom_addons/sc_demo/` with production OCA patterns from `skills/odoo-module-dev/`

**Decision Guide**: When to use simple scaffolding vs full OCA compliance

---

## Side-by-Side Structure Comparison

### Existing: `sc_demo/` (Minimal Reference)

```
sc_demo/
├── __init__.py              # Module imports
├── __manifest__.py          # Minimal metadata
├── models/
│   ├── __init__.py
│   └── sc_demo.py          # Simple model with 2 fields
├── security/
│   └── ir.model.access.csv # Basic CRUD permissions
└── data/
    └── (empty)             # Placeholder for demo data
```

**Total Files**: 6
**Lines of Code**: ~30
**Use Case**: Quick prototyping, learning, simple modules

---

### Enhanced: Production OCA Module (From `odoo-module-dev` skill)

```
hr_expense_approval/  # Example generated module
├── __init__.py
├── __manifest__.py          # Full OCA metadata + dependencies
├── models/
│   ├── __init__.py
│   ├── hr_expense.py       # Extended model with computed fields
│   └── approval_workflow.py
├── views/
│   ├── hr_expense_views.xml
│   └── approval_workflow_views.xml
├── security/
│   ├── ir.model.access.csv
│   └── ir.rule.xml         # Record-level security (RLS)
├── data/
│   ├── approval_stages.xml
│   └── email_templates.xml
├── tests/
│   ├── __init__.py
│   ├── test_expense_approval.py  # Business logic tests
│   └── test_security.py          # Access control tests
├── migrations/
│   └── 16.0.1.0.1/
│       ├── pre-migration.py
│       └── post-migration.py
├── static/
│   └── description/
│       ├── icon.png
│       └── index.html
├── i18n/
│   ├── es.po
│   └── fr.po
├── README.rst              # OCA-generated documentation
├── .pre-commit-config.yaml # Code quality hooks
└── pyproject.toml          # Python project metadata
```

**Total Files**: ~25
**Lines of Code**: ~500-1000
**Use Case**: Production deployments, OCA compliance, CI/CD

---

## Feature-by-Feature Comparison

### 1. Manifest (`__manifest__.py`)

#### sc_demo (Minimal)
```python
{
  "name": "SC Demo",
  "version": "16.0.1.0.0",
  "license": "LGPL-3",
  "summary": "Minimal OCA-style demo module",
  "author": "InsightPulseAI",
  "website": "https://insightpulseai.com",
  "depends": ["base"],
  "data": ["security/ir.model.access.csv"],
}
```

**Coverage**: Bare minimum for module installation

---

#### Production OCA Module (Full)
```python
{
    "name": "HR Expense Approval",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "category": "Human Resources/Expenses",
    "summary": "Multi-level expense approval workflow with budget validation",
    "author": "InsightPulseAI, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr-expense",
    "maintainers": ["your_github_handle"],
    "depends": ["hr_expense", "mail", "approvals"],
    "data": [
        "security/ir.model.access.csv",
        "security/ir.rule.xml",
        "data/approval_stages.xml",
        "views/hr_expense_views.xml",
        "views/approval_workflow_views.xml",
    ],
    "demo": ["demo/demo_data.xml"],
    "installable": True,
    "auto_install": False,
    "application": False,
    "external_dependencies": {
        "python": ["anthropic>=0.36.0"],
    },
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
}
```

**Coverage**: OCA-compliant metadata, hooks, dependencies, maintainers

**Enhancements**:
- ✅ Category classification
- ✅ Maintainer tracking
- ✅ External dependencies
- ✅ Init/uninstall hooks
- ✅ Demo data separation

---

### 2. Models

#### sc_demo (Simple)
```python
from odoo import models, fields

class ScDemoItem(models.Model):
    _name = "sc.demo.item"
    _description = "SC Demo Item"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
```

**Coverage**: Basic model with 2 fields
**ORM Patterns**: None (basic field definitions only)

---

#### Production OCA Module (Advanced)
```python
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class HrExpense(models.Model):
    _inherit = "hr.expense"

    approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='draft', tracking=True)

    approver_ids = fields.Many2many(
        'res.users',
        string='Approvers',
        compute='_compute_approver_ids',
        store=True,
    )

    total_with_tax = fields.Monetary(
        compute='_compute_total_with_tax',
        store=True,
        currency_field='currency_id',
    )

    @api.depends('amount', 'tax_ids')
    def _compute_total_with_tax(self):
        """Calculate total including taxes"""
        for expense in self:
            tax_amount = sum(expense.tax_ids.mapped('amount'))
            expense.total_with_tax = expense.amount * (1 + tax_amount / 100)

    @api.depends('employee_id', 'total_with_tax')
    def _compute_approver_ids(self):
        """Determine approvers based on amount thresholds"""
        for expense in self:
            if expense.total_with_tax > 1000:
                expense.approver_ids = self.env.ref('hr.group_hr_manager').users
            else:
                expense.approver_ids = expense.employee_id.parent_id.user_id

    @api.constrains('amount')
    def _check_amount_positive(self):
        """Ensure expense amounts are positive"""
        for expense in self:
            if expense.amount <= 0:
                raise ValidationError(_("Expense amount must be positive"))

    def action_submit_approval(self):
        """Submit expense for approval"""
        self.ensure_one()
        if not self.approver_ids:
            raise UserError(_("No approvers found. Please contact HR."))
        self.write({'approval_state': 'pending'})
        self._send_approval_notification()

    def _send_approval_notification(self):
        """Send email notification to approvers"""
        template = self.env.ref('hr_expense_approval.email_template_approval_request')
        for approver in self.approver_ids:
            template.send_mail(self.id, force_send=True, email_values={
                'email_to': approver.email
            })
```

**Coverage**: Full ORM patterns, business logic, validations

**Enhancements**:
- ✅ `@api.depends` for computed fields
- ✅ `@api.constrains` for validations
- ✅ Stored computed fields for performance
- ✅ Many2many relationships
- ✅ Field tracking (audit trail)
- ✅ Exception handling with UserError/ValidationError
- ✅ Email template integration
- ✅ Translatable strings with `_()`

---

### 3. Security

#### sc_demo (Basic CRUD)
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sc_demo_item,access_sc_demo_item,model_sc_demo_item,base.group_user,1,1,1,1
```

**Coverage**: Single access rule for all users

---

#### Production OCA Module (Granular Access)

**ir.model.access.csv**:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_expense_user,access_expense_user,model_hr_expense,hr.group_hr_user,1,1,1,0
access_expense_manager,access_expense_manager,model_hr_expense,hr.group_hr_manager,1,1,1,1
access_approval_user,access_approval_user,model_approval_workflow,base.group_user,1,0,0,0
access_approval_manager,access_approval_manager,model_approval_workflow,hr.group_hr_manager,1,1,1,1
```

**ir.rule.xml** (Record-Level Security):
```xml
<odoo>
    <record id="expense_rule_employee" model="ir.rule">
        <field name="name">Expense: Employee can see own expenses</field>
        <field name="model_id" ref="hr_expense.model_hr_expense"/>
        <field name="domain_force">[('employee_id.user_id', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('hr.group_hr_user'))]"/>
    </record>

    <record id="expense_rule_manager" model="ir.rule">
        <field name="name">Expense: Manager can see all</field>
        <field name="model_id" ref="hr_expense.model_hr_expense"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('hr.group_hr_manager'))]"/>
    </record>

    <record id="expense_rule_approver" model="ir.rule">
        <field name="name">Expense: Approver can see assigned expenses</field>
        <field name="model_id" ref="hr_expense.model_hr_expense"/>
        <field name="domain_force">[('approver_ids', 'in', [user.id])]</field>
        <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    </record>
</odoo>
```

**Enhancements**:
- ✅ Role-based access (User vs Manager)
- ✅ Record rules (Row-Level Security)
- ✅ Domain-based filtering (users see only their expenses)
- ✅ Multi-company support ready

---

### 4. Testing

#### sc_demo (None)
```
# No tests directory
```

**Coverage**: 0%

---

#### Production OCA Module (Comprehensive)

**tests/test_expense_approval.py**:
```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestExpenseApproval(TransactionCase):

    def setUp(self):
        super().setUp()
        self.expense_model = self.env['hr.expense']
        self.employee = self.env['hr.employee'].create({
            'name': 'Test Employee',
        })

    def test_computed_total_with_tax(self):
        """Test tax calculation in computed field"""
        tax = self.env['account.tax'].create({
            'name': 'VAT 20%',
            'amount': 20,
        })
        expense = self.expense_model.create({
            'name': 'Flight Ticket',
            'employee_id': self.employee.id,
            'amount': 100,
            'tax_ids': [(6, 0, [tax.id])],
        })
        self.assertEqual(expense.total_with_tax, 120)

    def test_amount_constraint(self):
        """Test validation prevents negative amounts"""
        with self.assertRaises(ValidationError):
            self.expense_model.create({
                'name': 'Invalid Expense',
                'employee_id': self.employee.id,
                'amount': -50,
            })

    def test_approver_assignment(self):
        """Test approver assignment based on amount threshold"""
        # Low amount expense
        expense_low = self.expense_model.create({
            'name': 'Coffee',
            'employee_id': self.employee.id,
            'amount': 10,
        })
        self.assertEqual(len(expense_low.approver_ids), 1)

        # High amount expense
        expense_high = self.expense_model.create({
            'name': 'Conference',
            'employee_id': self.employee.id,
            'amount': 2000,
        })
        self.assertGreater(len(expense_high.approver_ids), 1)
```

**Coverage**: Business logic, validations, computed fields, workflows

**Enhancements**:
- ✅ Unit tests for all critical methods
- ✅ Constraint validation tests
- ✅ Computed field tests
- ✅ Exception handling tests
- ✅ Test data isolation with TransactionCase

---

### 5. Views (Not in sc_demo)

**Production OCA Module**:

**views/hr_expense_views.xml**:
```xml
<odoo>
    <record id="view_hr_expense_form_inherit" model="ir.ui.view">
        <field name="name">hr.expense.form.inherit</field>
        <field name="model">hr.expense</field>
        <field name="inherit_id" ref="hr_expense.hr_expense_view_form"/>
        <field name="arch" type="xml">
            <xpath expr="//sheet" position="before">
                <header>
                    <field name="approval_state" widget="statusbar"/>
                    <button name="action_submit_approval"
                            string="Submit for Approval"
                            type="object"
                            states="draft"
                            class="btn-primary"/>
                </header>
            </xpath>
            <xpath expr="//field[@name='employee_id']" position="after">
                <field name="approver_ids" widget="many2many_tags"/>
                <field name="total_with_tax"/>
            </xpath>
        </field>
    </record>
</odoo>
```

**Enhancements**:
- ✅ Form views with statusbar
- ✅ Action buttons with states
- ✅ Widget customization (many2many_tags)
- ✅ Tree/kanban/pivot/graph views

---

### 6. Migrations (Not in sc_demo)

**Production OCA Module**:

**migrations/16.0.1.0.1/pre-migration.py**:
```python
from openupgradelib import openupgrade

@openupgrade.migrate()
def migrate(env, version):
    """Add approval_state field with default value"""
    if not openupgrade.column_exists(env.cr, 'hr_expense', 'approval_state'):
        openupgrade.add_fields(
            env,
            [
                ('approval_state', 'hr.expense', 'hr_expense',
                 'selection', False, 'hr_expense_approval'),
            ]
        )
        # Set default value for existing records
        env.cr.execute("""
            UPDATE hr_expense
            SET approval_state = 'draft'
            WHERE approval_state IS NULL
        """)
```

**Enhancements**:
- ✅ Version-based migration scripts
- ✅ Pre/post migration separation
- ✅ Database schema changes
- ✅ Data migration for existing records

---

### 7. Documentation

#### sc_demo (None)
```
# No README.rst
```

---

#### Production OCA Module (Auto-Generated)

**README.rst** (generated by `oca-gen-addon-readme`):
```rst
=======================
HR Expense Approval
=======================

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
.. |badge2| image:: https://img.shields.io/badge/licence-LGPL--3-blue.png

|badge1| |badge2|

This module extends the standard HR Expense module with multi-level approval workflows.

**Features**:

* Configurable approval stages (Draft → Pending → Approved/Rejected)
* Automatic approver assignment based on expense amount
* Email notifications to approvers
* Audit trail with field tracking
* Budget validation integration

**Table of contents**

.. contents::
   :local:

Installation
============

Install dependencies:

* hr_expense
* mail
* approvals

Configuration
=============

1. Go to Settings → Technical → Approval Workflows
2. Configure approval amount thresholds
3. Assign approvers to employee departments

Usage
=====

1. Create a new expense
2. Click "Submit for Approval"
3. Approvers receive email notification
4. Approver reviews and approves/rejects
5. Employee receives notification of decision

Known issues / Roadmap
======================

* Add mobile app support for approvals
* Integrate with budget module for real-time validation

Bug Tracker
===========

Bugs are tracked on GitHub Issues. In case of trouble, please check there.

Credits
=======

Authors
~~~~~~~

* InsightPulseAI

Contributors
~~~~~~~~~~~~

* Your Name <your.email@example.com>

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.
```

**Enhancements**:
- ✅ Auto-generated from manifest and docstrings
- ✅ Badges for maturity and license
- ✅ Installation/configuration/usage sections
- ✅ Contributor and maintainer tracking

---

## Migration Path from sc_demo to Production

### Phase 1: Add Views (Low Complexity)

**Goal**: Add UI for sc_demo model

**Steps**:
1. Create `views/` directory
2. Add form/tree views XML for `sc.demo.item`
3. Reference views in `__manifest__.py` data section
4. Test: Install module and verify views appear

**Expected Result**: Basic UI with list and form views

---

### Phase 2: Add Tests (Medium Complexity)

**Goal**: Test coverage for sc_demo model

**Steps**:
1. Create `tests/` directory with `__init__.py`
2. Add `test_sc_demo.py` with TransactionCase
3. Write tests for: create, read, update, delete operations
4. Run tests: `pytest -v tests/test_sc_demo.py`

**Expected Result**: Test coverage >80%

---

### Phase 3: Add ORM Patterns (Medium Complexity)

**Goal**: Demonstrate computed fields and constraints

**Steps**:
1. Add computed field `display_name` with `@api.depends('name')`
2. Add constraint `@api.constrains('name')` to validate non-empty
3. Update tests to cover new patterns
4. Document patterns in docstrings

**Expected Result**: Full ORM pattern demonstration

---

### Phase 4: Add Record Rules (High Complexity)

**Goal**: Implement row-level security

**Steps**:
1. Create `security/ir.rule.xml`
2. Add record rule: users see only their own items
3. Add `user_id` field to sc.demo.item
4. Update access CSV with role-based permissions
5. Test with different users

**Expected Result**: Multi-user access control

---

### Phase 5: Add Pre-commit Hooks (Low Complexity)

**Goal**: Code quality automation

**Steps**:
1. Copy `.pre-commit-config.yaml` from OCA template
2. Install pre-commit: `pip install pre-commit`
3. Run: `pre-commit install`
4. Test: `pre-commit run --all-files`
5. Fix any issues (black, isort, flake8, pylint-odoo)

**Expected Result**: OCA code quality compliance

---

### Phase 6: Generate README (Low Complexity)

**Goal**: Auto-generated documentation

**Steps**:
1. Install `oca-gen-addon-readme`
2. Add docstrings to model and methods
3. Run: `oca-gen-addon-readme --addon-dir=. --org-name=InsightPulseAI`
4. Review generated README.rst

**Expected Result**: Professional module documentation

---

## When to Use Which

### Use `sc_demo/` When:

✅ **Learning Odoo Development**
- Understanding module structure
- First time creating custom modules
- Exploring ORM basics

✅ **Quick Prototyping**
- Proof-of-concept implementations
- Testing module ideas
- Simple CRUD models

✅ **Teaching/Training**
- Demonstrating minimal viable module
- Explaining Odoo architecture
- Workshop exercises

---

### Use Production Patterns When:

✅ **OCA Compliance Required**
- Contributing to OCA repositories
- Enterprise module marketplace
- Community module distribution

✅ **Production Deployment**
- Customer-facing modules
- CI/CD integration
- Multi-environment deployment

✅ **Complex Business Logic**
- Computed fields with dependencies
- Multi-level approval workflows
- Integration with external systems

✅ **Testing & Quality Requirements**
- Test coverage mandates
- Security audits
- Performance optimization

---

## Pattern Adoption Checklist

Before migrating from sc_demo to production patterns:

- [ ] Review OCA guidelines: https://github.com/OCA/odoo-community.org
- [ ] Install pre-commit hooks: `pre-commit install`
- [ ] Add tests for all models and methods
- [ ] Configure CI/CD: GitHub Actions or GitLab CI
- [ ] Generate README: `oca-gen-addon-readme`
- [ ] Add record rules for multi-user scenarios
- [ ] Document API with docstrings
- [ ] Add migration scripts if database changes required
- [ ] Test with real Odoo instance (not just unit tests)
- [ ] Validate with `pylint-odoo` and `flake8`

---

## Code Quality Comparison

### sc_demo
- **Pylint Score**: N/A (no linting configured)
- **Test Coverage**: 0%
- **Documentation**: Minimal (inline comments only)
- **OCA Compliance**: Basic structure only

### Production Module
- **Pylint Score**: 9.5+/10 (OCA pre-commit hooks enforce)
- **Test Coverage**: 85%+ (pytest-odoo)
- **Documentation**: Auto-generated README.rst with usage examples
- **OCA Compliance**: Full (pre-commit, manifest, licensing, tests)

---

## Conclusion

**Recommendation**:
- **Keep sc_demo** as reference for simple module structure
- **Use production patterns** for customer-facing modules
- **Follow migration path** to incrementally add features
- **Reference this document** when deciding complexity level

**Next Steps**:
1. Identify module complexity requirements
2. Choose appropriate starting point (sc_demo vs full patterns)
3. Apply migration path phases as needed
4. Validate with OCA pre-commit hooks
5. Test thoroughly before production deployment

**Questions**: See `skills/odoo-module-dev/skill.yaml` for detailed patterns and examples

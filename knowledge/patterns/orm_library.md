# Odoo ORM Pattern Library

**Version**: 1.0
**Last Updated**: 2025-11-01
**Target Odoo Versions**: 16.0, 17.0, 18.0, 19.0
**OCA Compliance**: All patterns validated against OCA guidelines

---

## Table of Contents

1. [Computed Fields with @api.depends](#1-computed-fields-with-apidepends)
2. [Onchange Methods with @api.onchange](#2-onchange-methods-with-apionchange)
3. [Constraints with @api.constrains](#3-constraints-with-apiconstrains)
4. [Inverse Functions for Computed Fields](#4-inverse-functions-for-computed-fields)
5. [Custom Search Methods](#5-custom-search-methods)
6. [name_get Override for Display Names](#6-name_get-override-for-display-names)
7. [SQL Constraints with _sql_constraints](#7-sql-constraints-with-_sql_constraints)
8. [Record Rules (Row-Level Security)](#8-record-rules-row-level-security)
9. [Many2one Relationships](#9-many2one-relationships)
10. [One2many Relationships](#10-one2many-relationships)
11. [Many2many Relationships](#11-many2many-relationships)
12. [Related Fields](#12-related-fields)

---

## 1. Computed Fields with @api.depends

**Purpose**: Automatically calculate field values based on other fields. Updates trigger when dependencies change.

### Code Example

```python
from odoo import models, fields, api

class ExpenseReport(models.Model):
    _name = 'expense.report'
    _description = 'Expense Report'

    line_ids = fields.One2many('expense.report.line', 'report_id', string='Lines')
    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True,  # Store in database for performance
        readonly=True
    )

    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))
```

### Common Pitfalls

1. **Missing Dependencies**: Not declaring all fields that affect computation
   ```python
   # ❌ WRONG - missing 'line_ids.quantity' dependency
   @api.depends('line_ids.price')
   def _compute_total(self):
       for rec in self:
           rec.total = sum(line.price * line.quantity for line in rec.line_ids)

   # ✅ CORRECT
   @api.depends('line_ids.price', 'line_ids.quantity')
   def _compute_total(self):
       for rec in self:
           rec.total = sum(line.price * line.quantity for line in rec.line_ids)
   ```

2. **Not Iterating Through Recordset**: Computed methods receive recordsets, not single records
   ```python
   # ❌ WRONG
   @api.depends('amount')
   def _compute_total(self):
       self.total = self.amount * 1.1  # Only works for single record

   # ✅ CORRECT
   @api.depends('amount')
   def _compute_total(self):
       for record in self:
           record.total = record.amount * 1.1
   ```

3. **Performance Issues with Non-Stored Fields**: Use `store=True` for frequently accessed computed fields
   ```python
   # For reports/searches - always store
   total = fields.Float(compute='_compute_total', store=True)

   # For real-time UI display only - can be non-stored
   is_overdue = fields.Boolean(compute='_compute_overdue', store=False)
   ```

### OCA Compliance Notes

- Always use `store=True` for computed fields used in searches, reports, or domain filters
- Set `readonly=True` unless you implement an `inverse` method
- Use meaningful method names: `_compute_<field_name>`
- Document complex computation logic in docstrings

---

## 2. Onchange Methods with @api.onchange

**Purpose**: Update field values in UI when user changes a field. Client-side only, not triggered by ORM operations.

### Code Example

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_id = fields.Many2one('res.partner', string='Customer')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Auto-fill payment terms when customer is selected"""
        if self.partner_id:
            self.payment_term_id = self.partner_id.property_payment_term_id
            # Return warning if needed
            if not self.partner_id.property_payment_term_id:
                return {
                    'warning': {
                        'title': 'No Payment Terms',
                        'message': 'Customer has no default payment terms configured.'
                    }
                }
```

### Common Pitfalls

1. **Using onchange for Business Logic**: Onchange is UI-only, use constraints or compute for validation
   ```python
   # ❌ WRONG - business logic in onchange
   @api.onchange('amount')
   def _onchange_amount(self):
       if self.amount > 1000:
           raise ValidationError("Amount too high")

   # ✅ CORRECT - use constrains for validation
   @api.constrains('amount')
   def _check_amount(self):
       for rec in self:
           if rec.amount > 1000:
               raise ValidationError("Amount too high")
   ```

2. **Modifying Database in Onchange**: Onchange is client-side preview only
   ```python
   # ❌ WRONG - don't create/write records
   @api.onchange('partner_id')
   def _onchange_partner(self):
       self.env['crm.lead'].create({'partner_id': self.partner_id.id})

   # ✅ CORRECT - use create/write methods or compute fields
   ```

3. **Complex Calculations**: Move heavy logic to computed fields with proper dependencies
   ```python
   # ❌ WRONG - heavy computation in onchange
   @api.onchange('product_id')
   def _onchange_product(self):
       # 500 lines of complex calculation

   # ✅ CORRECT - use computed field
   price = fields.Float(compute='_compute_price', store=True)

   @api.depends('product_id', 'quantity')
   def _compute_price(self):
       # Complex calculation here
   ```

### OCA Compliance Notes

- Use onchange only for UI convenience, not business logic
- Return warnings/errors as dictionaries with `title` and `message`
- Avoid database operations (create, write, unlink) in onchange
- Use `_onchange_<field_name>` naming convention

---

## 3. Constraints with @api.constrains

**Purpose**: Validate field values before saving to database. Raises errors to prevent invalid data.

### Code Example

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ExpenseApprovalRequest(models.Model):
    _name = 'expense.approval.request'
    _description = 'Expense Approval Request'

    amount = fields.Float(string='Amount', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft')

    @api.constrains('amount')
    def _check_amount_positive(self):
        """Ensure amount is positive"""
        for record in self:
            if record.amount <= 0:
                raise ValidationError(
                    "Amount must be greater than zero. Got: %.2f" % record.amount
                )

    @api.constrains('amount', 'state')
    def _check_approved_amount_limit(self):
        """Ensure approved expenses don't exceed limit"""
        for record in self:
            if record.state == 'approved' and record.amount > 10000:
                raise ValidationError(
                    "Cannot approve expenses over $10,000. "
                    "Current amount: $%.2f" % record.amount
                )
```

### Common Pitfalls

1. **Not Iterating Through Recordset**: Constraints receive recordsets
   ```python
   # ❌ WRONG
   @api.constrains('email')
   def _check_email(self):
       if '@' not in self.email:  # Only works for single record
           raise ValidationError("Invalid email")

   # ✅ CORRECT
   @api.constrains('email')
   def _check_email(self):
       for record in self:
           if record.email and '@' not in record.email:
               raise ValidationError("Invalid email for %s" % record.name)
   ```

2. **Database Queries in Constraints**: Avoid expensive operations
   ```python
   # ❌ WRONG - expensive search
   @api.constrains('code')
   def _check_code_unique(self):
       for rec in self:
           if self.search_count([('code', '=', rec.code), ('id', '!=', rec.id)]) > 0:
               raise ValidationError("Code must be unique")

   # ✅ CORRECT - use SQL constraint for uniqueness
   _sql_constraints = [
       ('code_unique', 'UNIQUE(code)', 'Code must be unique')
   ]
   ```

3. **Validating Related Fields Without Dependency**: Declare all checked fields
   ```python
   # ❌ WRONG - missing 'partner_id' in decorator
   @api.constrains('amount')
   def _check_partner_credit(self):
       for rec in self:
           if rec.partner_id.credit_limit < rec.amount:
               raise ValidationError("Exceeds credit limit")

   # ✅ CORRECT
   @api.constrains('amount', 'partner_id')
   def _check_partner_credit(self):
       for rec in self:
           if rec.partner_id.credit_limit < rec.amount:
               raise ValidationError("Exceeds credit limit")
   ```

### OCA Compliance Notes

- Use `_check_<validation_name>` naming convention
- Provide clear error messages with context
- Use SQL constraints for simple uniqueness/not-null checks
- Iterate through recordsets properly

---

## 4. Inverse Functions for Computed Fields

**Purpose**: Make computed fields writable by defining how to reverse the computation.

### Code Example

```python
from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _description = 'Sale Order Line'

    price_unit = fields.Float(string='Unit Price')
    tax_rate = fields.Float(string='Tax Rate (%)', default=10.0)
    price_total = fields.Float(
        string='Total Price',
        compute='_compute_price_total',
        inverse='_inverse_price_total',
        store=True
    )

    @api.depends('price_unit', 'tax_rate')
    def _compute_price_total(self):
        for record in self:
            record.price_total = record.price_unit * (1 + record.tax_rate / 100)

    def _inverse_price_total(self):
        """Allow setting total price, compute unit price from it"""
        for record in self:
            if record.tax_rate:
                record.price_unit = record.price_total / (1 + record.tax_rate / 100)
            else:
                record.price_unit = record.price_total
```

### Common Pitfalls

1. **Not Handling All Cases**: Inverse must handle edge cases
   ```python
   # ❌ WRONG - division by zero if quantity is 0
   def _inverse_price_total(self):
       for rec in self:
           rec.price_unit = rec.price_total / rec.quantity

   # ✅ CORRECT
   def _inverse_price_total(self):
       for rec in self:
           if rec.quantity:
               rec.price_unit = rec.price_total / rec.quantity
           else:
               rec.price_unit = 0.0
   ```

2. **Circular Dependencies**: Inverse writes to dependency fields
   ```python
   # ❌ WRONG - circular computation
   @api.depends('total')
   def _compute_subtotal(self):
       for rec in self:
           rec.subtotal = rec.total * 0.9

   def _inverse_subtotal(self):
       for rec in self:
           rec.total = rec.subtotal / 0.9  # Triggers _compute_subtotal again
   ```

3. **Complex Multi-Field Inverse**: Keep inverse logic simple
   ```python
   # ❌ WRONG - too complex, better as separate fields
   def _inverse_full_address(self):
       # Parsing "123 Main St, City, State, ZIP" into 4 fields

   # ✅ CORRECT - use separate street, city, state, zip fields
   ```

### OCA Compliance Notes

- Only use inverse when computation is truly reversible
- Handle edge cases (division by zero, None values)
- Keep inverse logic simple and predictable
- Test inverse operations thoroughly

---

## 5. Custom Search Methods

**Purpose**: Override default search behavior for complex domain logic.

### Code Example

```python
from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_available = fields.Boolean(
        string='Available',
        compute='_compute_is_available',
        search='_search_is_available'
    )

    @api.depends('qty_available', 'outgoing_qty')
    def _compute_is_available(self):
        for record in self:
            record.is_available = (record.qty_available - record.outgoing_qty) > 0

    def _search_is_available(self, operator, value):
        """
        Custom search for available products
        Returns domain based on stock quantities
        """
        if operator not in ('=', '!='):
            raise ValueError("Unsupported operator for is_available search")

        if (operator == '=' and value) or (operator == '!=' and not value):
            # Search for available products (qty_available > outgoing_qty)
            products = self.search([])
            available_ids = [p.id for p in products if p.qty_available > p.outgoing_qty]
            return [('id', 'in', available_ids)]
        else:
            # Search for unavailable products
            products = self.search([])
            unavailable_ids = [p.id for p in products if p.qty_available <= p.outgoing_qty]
            return [('id', 'in', unavailable_ids)]
```

### Common Pitfalls

1. **Inefficient Queries**: Avoid loading all records
   ```python
   # ❌ WRONG - loads all records into memory
   def _search_is_available(self, operator, value):
       products = self.search([])  # Loads everything
       available = [p.id for p in products if p.qty_available > 0]
       return [('id', 'in', available)]

   # ✅ CORRECT - use database query
   def _search_is_available(self, operator, value):
       if operator == '=' and value:
           return [('qty_available', '>', 0)]
       else:
           return [('qty_available', '<=', 0)]
   ```

2. **Not Handling Operators**: Support all relevant operators
   ```python
   # ❌ WRONG - only handles '='
   def _search_field(self, operator, value):
       return [('other_field', '>', value)]

   # ✅ CORRECT - handle =, !=, in, not in
   def _search_field(self, operator, value):
       if operator == '=':
           return [('other_field', '=', value)]
       elif operator == '!=':
           return [('other_field', '!=', value)]
       elif operator in ('in', 'not in'):
           return [('other_field', operator, value)]
       else:
           raise ValueError(f"Unsupported operator: {operator}")
   ```

3. **Returning Wrong Domain Format**: Must return proper domain list
   ```python
   # ❌ WRONG - returns IDs instead of domain
   def _search_field(self, operator, value):
       return [1, 2, 3]

   # ✅ CORRECT
   def _search_field(self, operator, value):
       return [('id', 'in', [1, 2, 3])]
   ```

### OCA Compliance Notes

- Return Odoo domain format: `[('field', 'operator', value)]`
- Handle standard operators: `=`, `!=`, `in`, `not in`, `<`, `>`, `<=`, `>=`
- Use database queries, avoid loading all records
- Test with various search scenarios

---

## 6. name_get Override for Display Names

**Purpose**: Customize how records appear in Many2one fields, breadcrumbs, and searches.

### Code Example

```python
from odoo import models, fields, api

class ExpenseApprovalRequest(models.Model):
    _name = 'expense.approval.request'
    _description = 'Expense Approval Request'

    name = fields.Char(string='Reference', required=True)
    amount = fields.Float(string='Amount')
    partner_id = fields.Many2one('res.partner', string='Vendor')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved')
    ], default='draft')

    def name_get(self):
        """
        Custom display name: "REF001 - Vendor Name ($1,234.56) [Approved]"
        """
        result = []
        for record in self:
            name_parts = [record.name]

            if record.partner_id:
                name_parts.append(record.partner_id.name)

            if record.amount:
                name_parts.append('($%.2f)' % record.amount)

            if record.state:
                state_label = dict(record._fields['state'].selection).get(record.state)
                name_parts.append('[%s]' % state_label)

            display_name = ' - '.join(name_parts)
            result.append((record.id, display_name))

        return result
```

### Common Pitfalls

1. **Not Returning List of Tuples**: Must return `[(id, name), ...]`
   ```python
   # ❌ WRONG - returns string
   def name_get(self):
       return self.name

   # ✅ CORRECT
   def name_get(self):
       return [(record.id, record.name) for record in self]
   ```

2. **Not Iterating Through Recordset**: name_get receives recordsets
   ```python
   # ❌ WRONG - only works for single record
   def name_get(self):
       return [(self.id, self.name)]

   # ✅ CORRECT
   def name_get(self):
       result = []
       for record in self:
           result.append((record.id, record.name))
       return result
   ```

3. **Performance Issues with Related Fields**: Avoid excessive database queries
   ```python
   # ❌ WRONG - N+1 queries
   def name_get(self):
       result = []
       for record in self:
           # Each iteration triggers query for partner_id
           name = f"{record.name} - {record.partner_id.name}"
           result.append((record.id, name))
       return result

   # ✅ CORRECT - prefetch with read()
   def name_get(self):
       self.read(['name', 'partner_id'])  # Batch load
       result = []
       for record in self:
           name = f"{record.name} - {record.partner_id.name}"
           result.append((record.id, name))
       return result
   ```

### OCA Compliance Notes

- Always return list of tuples: `[(id, display_name), ...]`
- Keep display names concise (<100 chars recommended)
- Use `dict(field._fields['selection'].selection)` for selection field labels
- Consider performance for large recordsets

---

## 7. SQL Constraints with _sql_constraints

**Purpose**: Database-level constraints for uniqueness, not-null, and check conditions.

### Code Example

```python
from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    internal_code = fields.Char(string='Internal Code')
    minimum_price = fields.Float(string='Minimum Price')
    maximum_price = fields.Float(string='Maximum Price')

    _sql_constraints = [
        (
            'internal_code_unique',
            'UNIQUE(internal_code)',
            'Internal code must be unique!'
        ),
        (
            'minimum_price_positive',
            'CHECK(minimum_price >= 0)',
            'Minimum price must be positive!'
        ),
        (
            'price_range_valid',
            'CHECK(maximum_price >= minimum_price)',
            'Maximum price must be greater than or equal to minimum price!'
        ),
    ]
```

### Common Pitfalls

1. **Using Python Constraints for Simple Checks**: Use SQL for better performance
   ```python
   # ❌ WRONG - Python constraint for simple uniqueness
   @api.constrains('code')
   def _check_code_unique(self):
       for rec in self:
           if self.search_count([('code', '=', rec.code), ('id', '!=', rec.id)]) > 0:
               raise ValidationError("Code must be unique")

   # ✅ CORRECT - SQL constraint
   _sql_constraints = [
       ('code_unique', 'UNIQUE(code)', 'Code must be unique')
   ]
   ```

2. **Complex Logic in SQL Constraints**: Keep SQL constraints simple
   ```python
   # ❌ WRONG - too complex for SQL
   _sql_constraints = [
       (
           'complex_check',
           'CHECK((state = "approved" AND amount < 1000) OR (state != "approved"))',
           'Complex validation message'
       )
   ]

   # ✅ CORRECT - use Python constrains for complex logic
   @api.constrains('state', 'amount')
   def _check_approval_rules(self):
       # Complex validation here
   ```

3. **Poor Error Messages**: Make messages user-friendly
   ```python
   # ❌ WRONG - technical message
   _sql_constraints = [
       ('check_val', 'CHECK(val > 0)', 'Constraint violation')
   ]

   # ✅ CORRECT - clear message
   _sql_constraints = [
       ('amount_positive', 'CHECK(amount > 0)', 'Amount must be greater than zero')
   ]
   ```

### OCA Compliance Notes

- Use SQL constraints for uniqueness, not-null, and simple checks
- Format: `[(name, sql_condition, error_message)]`
- Use descriptive constraint names: `field_condition` (e.g., `code_unique`)
- Provide user-friendly error messages

---

## 8. Record Rules (Row-Level Security)

**Purpose**: Control which records users can see, create, update, or delete based on domain filters.

### Code Example (XML)

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Users can only see their own expense requests -->
    <record id="expense_approval_request_user_rule" model="ir.rule">
        <field name="name">User Own Expenses</field>
        <field name="model_id" ref="model_expense_approval_request"/>
        <field name="domain_force">[('user_id', '=', user.id)]</field>
        <field name="groups" eval="[(4, ref('base.group_user'))]"/>
        <field name="perm_read" eval="True"/>
        <field name="perm_write" eval="True"/>
        <field name="perm_create" eval="True"/>
        <field name="perm_unlink" eval="True"/>
    </record>

    <!-- Managers can see all expenses in their department -->
    <record id="expense_approval_request_manager_rule" model="ir.rule">
        <field name="name">Manager Department Expenses</field>
        <field name="model_id" ref="model_expense_approval_request"/>
        <field name="domain_force">
            [('user_id.department_id', '=', user.department_id.id)]
        </field>
        <field name="groups" eval="[(4, ref('base.group_user'))]"/>
        <field name="perm_read" eval="True"/>
        <field name="perm_write" eval="True"/>
        <field name="perm_create" eval="False"/>
        <field name="perm_unlink" eval="False"/>
    </record>

    <!-- System admins can see everything (no domain filter) -->
    <record id="expense_approval_request_admin_rule" model="ir.rule">
        <field name="name">Admin All Expenses</field>
        <field name="model_id" ref="model_expense_approval_request"/>
        <field name="domain_force">[(1, '=', 1)]</field>
        <field name="groups" eval="[(4, ref('base.group_system'))]"/>
        <field name="perm_read" eval="True"/>
        <field name="perm_write" eval="True"/>
        <field name="perm_create" eval="True"/>
        <field name="perm_unlink" eval="True"/>
    </record>
</odoo>
```

### Common Pitfalls

1. **Overlapping Rules**: Rules for same group are OR'ed, different groups are AND'ed
   ```xml
   <!-- ❌ WRONG - conflicting rules for same group -->
   <record id="rule1" model="ir.rule">
       <field name="domain_force">[('user_id', '=', user.id)]</field>
       <field name="groups" eval="[(4, ref('base.group_user'))]"/>
   </record>
   <record id="rule2" model="ir.rule">
       <field name="domain_force">[('state', '=', 'approved')]</field>
       <field name="groups" eval="[(4, ref('base.group_user'))]"/>
   </record>
   <!-- Result: Users see (own records) OR (approved records) -->

   <!-- ✅ CORRECT - combine conditions in single rule -->
   <record id="rule1" model="ir.rule">
       <field name="domain_force">
           ['|', ('user_id', '=', user.id), ('state', '=', 'approved')]
       </field>
       <field name="groups" eval="[(4, ref('base.group_user'))]"/>
   </record>
   ```

2. **Not Testing Permission Combinations**: Test all CRUD operations
   ```python
   # Test read, write, create, unlink separately
   # Some users may have read-only access
   ```

3. **Performance Issues with Complex Domains**: Keep domains simple
   ```xml
   <!-- ❌ WRONG - too complex, slow queries -->
   <field name="domain_force">
       [('related_id.partner_id.parent_id.country_id.code', '=', 'US')]
   </field>

   <!-- ✅ CORRECT - use computed field -->
   <field name="domain_force">[('is_us_related', '=', True)]</field>
   ```

### OCA Compliance Notes

- Use `[(1, '=', 1)]` for "all records" domain (admin access)
- Test record rules with different user groups
- Document business logic for each rule
- Use prefix notation for complex OR/AND logic

---

## 9. Many2one Relationships

**Purpose**: Reference to a single record in another model (foreign key).

### Code Example

```python
from odoo import models, fields

class ExpenseApprovalRequest(models.Model):
    _name = 'expense.approval.request'
    _description = 'Expense Approval Request'

    # Basic Many2one
    user_id = fields.Many2one(
        'res.users',
        string='Requester',
        required=True,
        default=lambda self: self.env.user,
        ondelete='restrict'  # Prevent deletion of referenced user
    )

    # Many2one with domain filter
    approver_id = fields.Many2one(
        'res.users',
        string='Approver',
        domain="[('groups_id', 'in', [ref('expense_approval.group_approver')])]",
        ondelete='set null'  # Set to NULL if approver is deleted
    )

    # Many2one with context for default values
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        context={'show_address': 1}
    )
```

### Common Pitfalls

1. **Wrong ondelete Behavior**: Choose appropriate cascade action
   ```python
   # ondelete options:
   # - 'restrict': Block deletion if referenced (default)
   # - 'cascade': Delete this record if parent deleted
   # - 'set null': Set field to NULL if parent deleted

   # ❌ WRONG - cascade deletes expense when user deleted
   user_id = fields.Many2one('res.users', ondelete='cascade')

   # ✅ CORRECT - prevent user deletion
   user_id = fields.Many2one('res.users', ondelete='restrict')
   ```

2. **Performance Issues with Domain**: Avoid complex domain expressions
   ```python
   # ❌ WRONG - evaluates for every record
   partner_id = fields.Many2one(
       'res.partner',
       domain=lambda self: [('id', 'in', self._get_allowed_partners())]
   )

   # ✅ CORRECT - use static or simple dynamic domain
   partner_id = fields.Many2one(
       'res.partner',
       domain="[('customer_rank', '>', 0)]"
   )
   ```

3. **Not Handling NULL Values**: Many2one can be False/None
   ```python
   # ❌ WRONG - assumes partner_id exists
   @api.depends('partner_id')
   def _compute_credit(self):
       for rec in self:
           rec.credit_limit = rec.partner_id.credit  # Error if no partner

   # ✅ CORRECT - handle None case
   @api.depends('partner_id')
   def _compute_credit(self):
       for rec in self:
           rec.credit_limit = rec.partner_id.credit if rec.partner_id else 0.0
   ```

### OCA Compliance Notes

- Use `ondelete='restrict'` for critical references
- Use `ondelete='cascade'` for true parent-child relationships
- Use `ondelete='set null'` for optional references
- Document domain logic in comments

---

## 10. One2many Relationships

**Purpose**: Inverse of Many2one - access all records that reference current record.

### Code Example

```python
from odoo import models, fields, api

class ExpenseReport(models.Model):
    _name = 'expense.report'
    _description = 'Expense Report'

    name = fields.Char(string='Report Name', required=True)
    line_ids = fields.One2many(
        'expense.report.line',
        'report_id',
        string='Expense Lines',
        copy=True  # Copy lines when duplicating report
    )
    total_amount = fields.Float(
        string='Total',
        compute='_compute_total_amount',
        store=True
    )

    @api.depends('line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(record.line_ids.mapped('amount'))


class ExpenseReportLine(models.Model):
    _name = 'expense.report.line'
    _description = 'Expense Report Line'

    report_id = fields.Many2one(
        'expense.report',
        string='Report',
        required=True,
        ondelete='cascade'  # Delete line if report deleted
    )
    description = fields.Char(string='Description')
    amount = fields.Float(string='Amount')
```

### Common Pitfalls

1. **Missing Inverse Many2one**: One2many requires corresponding Many2one
   ```python
   # ❌ WRONG - no corresponding Many2one in expense.line
   line_ids = fields.One2many('expense.line', 'report_id')

   # ✅ CORRECT - expense.line must have Many2one field
   # In expense.report:
   line_ids = fields.One2many('expense.line', 'report_id')

   # In expense.line:
   report_id = fields.Many2one('expense.report', ondelete='cascade')
   ```

2. **Wrong Copy Behavior**: Set copy=False for non-duplicable data
   ```python
   # For audit logs, payments - don't copy
   payment_ids = fields.One2many('payment', 'invoice_id', copy=False)

   # For order lines, attributes - do copy
   line_ids = fields.One2many('order.line', 'order_id', copy=True)
   ```

3. **N+1 Query Performance**: Use mapped() for aggregations
   ```python
   # ❌ WRONG - N+1 queries
   @api.depends('line_ids')
   def _compute_total(self):
       for rec in self:
           total = 0
           for line in rec.line_ids:  # Query per line
               total += line.amount
           rec.total = total

   # ✅ CORRECT - single query with mapped
   @api.depends('line_ids.amount')
   def _compute_total(self):
       for rec in self:
           rec.total = sum(rec.line_ids.mapped('amount'))
   ```

### OCA Compliance Notes

- Always use `ondelete='cascade'` on inverse Many2one
- Use `copy=True` for duplicable data, `copy=False` for unique data
- Use `mapped()` for field aggregations to avoid N+1 queries
- Document relationship purpose in docstring

---

## 11. Many2many Relationships

**Purpose**: Link multiple records from both models (many-to-many relationship via junction table).

### Code Example

```python
from odoo import models, fields

class ExpenseCategory(models.Model):
    _name = 'expense.category'
    _description = 'Expense Category'

    name = fields.Char(string='Category Name', required=True)
    tag_ids = fields.Many2many(
        'expense.tag',
        'expense_category_tag_rel',  # Junction table name
        'category_id',                # Column for this model
        'tag_id',                     # Column for related model
        string='Tags'
    )


class ExpenseTag(models.Model):
    _name = 'expense.tag'
    _description = 'Expense Tag'

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color Index')
    category_ids = fields.Many2many(
        'expense.category',
        'expense_category_tag_rel',  # Same junction table
        'tag_id',                     # Reversed column
        'category_id',                # Reversed column
        string='Categories'
    )
```

### Common Pitfalls

1. **Junction Table Name Conflicts**: Use unique, descriptive table names
   ```python
   # ❌ WRONG - generic name, may conflict
   tag_ids = fields.Many2many('expense.tag', 'rel', 'id1', 'id2')

   # ✅ CORRECT - specific, unique name
   tag_ids = fields.Many2many(
       'expense.tag',
       'expense_category_tag_rel',
       'category_id',
       'tag_id'
   )
   ```

2. **Reversed Column Names**: Inverse relation must reverse column names
   ```python
   # In expense.category:
   tag_ids = fields.Many2many(
       'expense.tag',
       'expense_category_tag_rel',
       'category_id',  # This model
       'tag_id'        # Related model
   )

   # In expense.tag:
   category_ids = fields.Many2many(
       'expense.category',
       'expense_category_tag_rel',
       'tag_id',       # This model (reversed)
       'category_id'   # Related model (reversed)
   )
   ```

3. **Performance with Large Sets**: Use SQL for bulk operations
   ```python
   # ❌ WRONG - multiple ORM writes
   for tag in tags:
       category.tag_ids = [(4, tag.id)]

   # ✅ CORRECT - single operation
   category.tag_ids = [(6, 0, tag_ids)]
   ```

### Many2many Command Syntax

```python
# Replace all: (6, 0, [id1, id2, id3])
record.tag_ids = [(6, 0, [1, 2, 3])]

# Add one: (4, id)
record.tag_ids = [(4, new_tag.id)]

# Remove one: (3, id)
record.tag_ids = [(3, old_tag.id)]

# Clear all: (5, 0, 0)
record.tag_ids = [(5, 0, 0)]
```

### OCA Compliance Notes

- Use descriptive junction table names: `model1_model2_rel`
- Always specify all 4 parameters for clarity
- Use command syntax for bulk operations: `[(6, 0, ids)]`
- Document relationship purpose

---

## 12. Related Fields

**Purpose**: Access fields from related records without writing custom compute methods.

### Code Example

```python
from odoo import models, fields

class SaleOrderLine(models.Model):
    _name = 'sale.order.line'
    _description = 'Sale Order Line'

    order_id = fields.Many2one('sale.order', string='Order', required=True)
    product_id = fields.Many2one('product.product', string='Product')

    # Related field - automatic delegation
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='order_id.partner_id',
        store=True,  # Store for searching/filtering
        readonly=True
    )

    # Related field through multiple levels
    partner_country_id = fields.Many2one(
        'res.country',
        string='Customer Country',
        related='order_id.partner_id.country_id',
        store=False  # Don't store, always real-time
    )

    # Related field for simple fields
    product_type = fields.Selection(
        related='product_id.type',
        string='Product Type',
        store=True
    )
```

### Common Pitfalls

1. **Over-Storing Related Fields**: Only store if needed for search/reports
   ```python
   # ❌ WRONG - storing rarely-used field
   partner_phone = fields.Char(related='partner_id.phone', store=True)

   # ✅ CORRECT - don't store, access directly when needed
   partner_phone = fields.Char(related='partner_id.phone', store=False)
   ```

2. **Making Related Fields Writable**: Keep readonly unless intentional
   ```python
   # ❌ WRONG - writable related field without inverse
   partner_name = fields.Char(related='partner_id.name', readonly=False)

   # ✅ CORRECT - readonly by default
   partner_name = fields.Char(related='partner_id.name', readonly=True)
   ```

3. **Deep Chains**: Avoid too many levels
   ```python
   # ❌ WRONG - 5 levels deep, fragile
   country = fields.Char(
       related='order_id.partner_id.parent_id.country_id.name'
   )

   # ✅ CORRECT - maximum 2-3 levels
   country_id = fields.Many2one(
       related='partner_id.country_id',
       store=True
   )
   ```

### OCA Compliance Notes

- Use `store=True` only for searchable/reportable fields
- Keep `readonly=True` unless you need write-through
- Limit to 2-3 relation levels maximum
- Document business reason for storing

---

## Performance Best Practices

### General ORM Optimization

1. **Use Batch Operations**
   ```python
   # ❌ WRONG - N writes
   for line in lines:
       line.write({'state': 'done'})

   # ✅ CORRECT - single write
   lines.write({'state': 'done'})
   ```

2. **Avoid N+1 Queries**
   ```python
   # ❌ WRONG - query per record
   for order in orders:
       total = sum(line.amount for line in order.line_ids)

   # ✅ CORRECT - prefetch with read
   orders.read(['line_ids'])
   for order in orders:
       total = sum(order.line_ids.mapped('amount'))
   ```

3. **Use SQL for Mass Updates**
   ```python
   # ❌ WRONG - ORM for 10,000 records
   records.write({'field': 'value'})

   # ✅ CORRECT - direct SQL
   self.env.cr.execute(
       "UPDATE table SET field = %s WHERE id IN %s",
       ('value', tuple(records.ids))
   )
   records.invalidate_cache()
   ```

---

## Testing Patterns

### Basic Test Structure

```python
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestExpenseApproval(TransactionCase):

    def setUp(self):
        super().setUp()
        self.ExpenseModel = self.env['expense.approval.request']
        self.user = self.env.ref('base.user_demo')

    def test_compute_total_amount(self):
        """Test computed field calculates correctly"""
        expense = self.ExpenseModel.create({
            'name': 'Test Expense',
            'amount': 100.0,
            'user_id': self.user.id
        })
        self.assertEqual(expense.total_amount, 100.0)

    def test_amount_constraint(self):
        """Test amount must be positive"""
        with self.assertRaises(ValidationError):
            self.ExpenseModel.create({
                'name': 'Invalid Expense',
                'amount': -50.0,
                'user_id': self.user.id
            })
```

---

## References

- [Odoo ORM Documentation](https://www.odoo.com/documentation/16.0/developer/reference/backend/orm.html)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
- [Odoo API Decorators](https://www.odoo.com/documentation/16.0/developer/reference/backend/orm.html#api-decorators)

---

**Last Reviewed**: 2025-11-01
**Maintainer**: Odoo Expertise Agent
**License**: Apache-2.0

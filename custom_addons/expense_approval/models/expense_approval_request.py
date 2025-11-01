# Copyright 2025 InsightPulseAI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ExpenseApprovalRequest(models.Model):
    """Model for expense.approval.request"""

    _name = "expense.approval.request"
    _description = "Expense Approval Request"
    _order = "create_date desc"

    # Basic fields
    name = fields.Char(
        string="Name",
        required=True,
        index=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        default=lambda self: self.env.user,
        required=True,
    )
    amount = fields.Float(
        string="Amount",
        required=True,
        default=0.0,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        default="draft",
        required=True,
    )
    notes = fields.Text(string="Notes")

    # Computed fields example
    display_name_custom = fields.Char(
        string="Display Name",
        compute="_compute_display_name_custom",
        store=True,
    )

    @api.depends("name", "state")
    def _compute_display_name_custom(self):
        """Compute custom display name with status"""
        for record in self:
            state_label = dict(
                record._fields["state"].selection
            ).get(record.state, "")
            record.display_name_custom = f"{record.name} [{state_label}]"

    # Constraints
    @api.constrains("name")
    def _check_name_not_empty(self):
        """Ensure name is not empty or whitespace only"""
        for record in self:
            if not record.name or not record.name.strip():
                raise ValidationError("Name cannot be empty")

    # Actions
    def action_submit(self):
        """Submit for approval"""
        self.ensure_one()
        self.write({"state": "submitted"})

    def action_approve(self):
        """Approve request"""
        self.ensure_one()
        self.write({"state": "approved"})

    def action_reject(self):
        """Reject request"""
        self.ensure_one()
        self.write({"state": "rejected"})

    def action_reset_to_draft(self):
        """Reset to draft"""
        self.ensure_one()
        self.write({"state": "draft"})

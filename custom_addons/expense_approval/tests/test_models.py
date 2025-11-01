# Copyright 2025 InsightPulseAI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestModels(TransactionCase):
    """Test cases for expense_approval models"""

    def setUp(self):
        super().setUp()
        self.user = self.env.ref("base.user_demo")

        self.ExpenseApprovalRequestModel = self.env["expense.approval.request"]


    def test_create_expense_approval_request(self):
        """Test creating expense.approval.request record"""
        record = self.ExpenseApprovalRequestModel.create({
            "name": "Test Expense Approval Request",
            "user_id": self.user.id,
        })
        self.assertTrue(record)
        self.assertEqual(record.name, "Test Expense Approval Request")
        self.assertEqual(record.state, "draft")

    def test_expense_approval_request_workflow(self):
        """Test expense.approval.request state workflow"""
        record = self.ExpenseApprovalRequestModel.create({
            "name": "Test Workflow",
            "user_id": self.user.id,
        })

        # Test submit
        record.action_submit()
        self.assertEqual(record.state, "submitted")

        # Test approve
        record.action_approve()
        self.assertEqual(record.state, "approved")

        # Test reset
        record.action_reset_to_draft()
        self.assertEqual(record.state, "draft")

    def test_expense_approval_request_name_constraint(self):
        """Test name cannot be empty"""
        with self.assertRaises(ValidationError):
            self.ExpenseApprovalRequestModel.create({
                "name": "   ",  # Empty/whitespace
                "user_id": self.user.id,
            })

    def test_expense_approval_request_computed_fields(self):
        """Test computed field: display_name_custom"""
        record = self.ExpenseApprovalRequestModel.create({
            "name": "Test Compute",
            "user_id": self.user.id,
        })
        self.assertIn("Test Compute", record.display_name_custom)
        self.assertIn("[Draft]", record.display_name_custom)

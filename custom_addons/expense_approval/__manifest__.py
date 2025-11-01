# Copyright 2025 InsightPulseAI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Expense Approval",
    "version": "16.0.1.0.0",
    "category": "Accounting",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "website": "https://github.com/tbwa/odoo-expertise",
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/record_rules.xml",
        "views/expense_approval_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}

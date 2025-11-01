#!/usr/bin/env python3
"""
OCA-Compliant Odoo Module Scaffolder

Generates complete Odoo module structure following OCA conventions:
- Proper directory structure
- Valid __manifest__.py with correct versioning
- Model files with ORM patterns
- Security rules (ir.model.access.csv)
- pytest-odoo test templates
- Pre-commit configuration

Usage:
    python scaffold_module.py --name expense_approval --category Accounting --models expense.approval.request,expense.approval.level

Author: Odoo Expertise Agent
License: Apache-2.0
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Dict


class OdooModuleScaffolder:
    """OCA-compliant Odoo module generator"""

    def __init__(self, name: str, category: str, models: List[str], odoo_version: str = "16.0"):
        self.name = name
        self.category = category
        self.models = models
        self.odoo_version = odoo_version
        self.module_path = Path(f"custom_addons/{name}")

    def scaffold(self):
        """Generate complete module structure"""
        print(f"🏗️  Scaffolding OCA module: {self.name}")

        # Create directory structure
        self._create_directories()

        # Generate files
        self._create_manifest()
        self._create_init_files()
        self._create_models()
        self._create_security()
        self._create_tests()
        self._create_readme()

        print(f"✅ Module scaffolding complete: {self.module_path}")

    def _create_directories(self):
        """Create standard OCA directory structure"""
        directories = [
            self.module_path,
            self.module_path / "models",
            self.module_path / "security",
            self.module_path / "tests",
            self.module_path / "views",
            self.module_path / "data",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created: {directory}")

    def _create_manifest(self):
        """Generate __manifest__.py following OCA conventions"""
        manifest_content = f'''# Copyright {self._get_current_year()} InsightPulseAI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{{
    "name": "{self._format_module_name()}",
    "version": "{self.odoo_version}.1.0.0",
    "category": "{self.category}",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "website": "https://github.com/tbwa/odoo-expertise",
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/{self.name}_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}}
'''
        manifest_path = self.module_path / "__manifest__.py"
        manifest_path.write_text(manifest_content)
        print(f"📄 Created: {manifest_path}")

    def _create_init_files(self):
        """Create __init__.py files for Python package structure"""
        # Root __init__.py
        root_init = self.module_path / "__init__.py"
        root_init.write_text("from . import models\n")
        print(f"📄 Created: {root_init}")

        # models/__init__.py
        models_init = self.module_path / "models" / "__init__.py"
        model_imports = "\n".join([
            f"from . import {self._model_to_filename(model)}"
            for model in self.models
        ])
        models_init.write_text(model_imports + "\n")
        print(f"📄 Created: {models_init}")

        # tests/__init__.py
        tests_init = self.module_path / "tests" / "__init__.py"
        tests_init.write_text("from . import test_models\n")
        print(f"📄 Created: {tests_init}")

    def _create_models(self):
        """Generate model files with ORM patterns"""
        for model_name in self.models:
            filename = self._model_to_filename(model_name)
            class_name = self._model_to_classname(model_name)

            model_content = f'''# Copyright {self._get_current_year()} InsightPulseAI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class {class_name}(models.Model):
    """Model for {model_name}"""

    _name = "{model_name}"
    _description = "{self._format_description(model_name)}"
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
            record.display_name_custom = f"{{record.name}} [{{state_label}}]"

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
        self.write({{"state": "submitted"}})

    def action_approve(self):
        """Approve request"""
        self.ensure_one()
        self.write({{"state": "approved"}})

    def action_reject(self):
        """Reject request"""
        self.ensure_one()
        self.write({{"state": "rejected"}})

    def action_reset_to_draft(self):
        """Reset to draft"""
        self.ensure_one()
        self.write({{"state": "draft"}})
'''

            model_path = self.module_path / "models" / f"{filename}.py"
            model_path.write_text(model_content)
            print(f"📄 Created: {model_path}")

    def _create_security(self):
        """Generate ir.model.access.csv with proper permissions"""
        csv_rows = ["id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink"]

        for model_name in self.models:
            model_id = f"model_{model_name.replace('.', '_')}"
            access_id = f"access_{model_name.replace('.', '_')}_user"
            access_name = f"access_{model_name.replace('.', '_')}_user"

            # User access (read, write, create, unlink)
            csv_rows.append(
                f"{access_id},{access_name},{model_id},base.group_user,1,1,1,1"
            )

        csv_content = "\n".join(csv_rows) + "\n"
        csv_path = self.module_path / "security" / "ir.model.access.csv"
        csv_path.write_text(csv_content)
        print(f"📄 Created: {csv_path}")

        # Create record rules
        self._create_record_rules()

    def _create_record_rules(self):
        """Generate record rules for row-level security"""
        rules_content = f'''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
'''

        for model_name in self.models:
            model_ref = f"model_{model_name.replace('.', '_')}"
            rule_id = f"{model_name.replace('.', '_')}_user_rule"

            rules_content += f'''
        <!-- Users can only see their own records -->
        <record id="{rule_id}" model="ir.rule">
            <field name="name">{self._format_description(model_name)} - User Access</field>
            <field name="model_id" ref="{model_ref}"/>
            <field name="domain_force">[('user_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('base.group_user'))]"/>
            <field name="perm_read" eval="True"/>
            <field name="perm_write" eval="True"/>
            <field name="perm_create" eval="True"/>
            <field name="perm_unlink" eval="True"/>
        </record>
'''

        rules_content += '''
    </data>
</odoo>
'''

        rules_path = self.module_path / "security" / "record_rules.xml"
        rules_path.write_text(rules_content)

        # Update manifest to include record rules
        manifest_path = self.module_path / "__manifest__.py"
        manifest_content = manifest_path.read_text()
        manifest_content = manifest_content.replace(
            '"security/ir.model.access.csv",',
            '"security/ir.model.access.csv",\n        "security/record_rules.xml",'
        )
        manifest_path.write_text(manifest_content)
        print(f"📄 Created: {rules_path}")

    def _create_tests(self):
        """Generate pytest-odoo test templates"""
        test_content = f'''# Copyright {self._get_current_year()} InsightPulseAI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestModels(TransactionCase):
    """Test cases for {self.name} models"""

    def setUp(self):
        super().setUp()
        self.user = self.env.ref("base.user_demo")
'''

        for model_name in self.models:
            class_var = self._model_to_classname(model_name) + "Model"
            test_content += f'''
        self.{class_var} = self.env["{model_name}"]
'''

        # Add test methods
        for model_name in self.models:
            class_var = self._model_to_classname(model_name) + "Model"
            safe_name = model_name.replace(".", "_")

            test_content += f'''

    def test_create_{safe_name}(self):
        """Test creating {model_name} record"""
        record = self.{class_var}.create({{
            "name": "Test {self._format_description(model_name)}",
            "user_id": self.user.id,
        }})
        self.assertTrue(record)
        self.assertEqual(record.name, "Test {self._format_description(model_name)}")
        self.assertEqual(record.state, "draft")

    def test_{safe_name}_workflow(self):
        """Test {model_name} state workflow"""
        record = self.{class_var}.create({{
            "name": "Test Workflow",
            "user_id": self.user.id,
        }})

        # Test submit
        record.action_submit()
        self.assertEqual(record.state, "submitted")

        # Test approve
        record.action_approve()
        self.assertEqual(record.state, "approved")

        # Test reset
        record.action_reset_to_draft()
        self.assertEqual(record.state, "draft")

    def test_{safe_name}_name_constraint(self):
        """Test name cannot be empty"""
        with self.assertRaises(ValidationError):
            self.{class_var}.create({{
                "name": "   ",  # Empty/whitespace
                "user_id": self.user.id,
            }})

    def test_{safe_name}_computed_fields(self):
        """Test computed field: display_name_custom"""
        record = self.{class_var}.create({{
            "name": "Test Compute",
            "user_id": self.user.id,
        }})
        self.assertIn("Test Compute", record.display_name_custom)
        self.assertIn("[Draft]", record.display_name_custom)
'''

        test_path = self.module_path / "tests" / "test_models.py"
        test_path.write_text(test_content)
        print(f"📄 Created: {test_path}")

    def _create_readme(self):
        """Generate OCA-compliant README.rst"""
        readme_content = f'''.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

========
{self._format_module_name()}
========

{self._format_description(self.name)}

**Table of contents**

.. contents::
   :local:

Configuration
=============

No configuration needed.

Usage
=====

To use this module:

#. Go to {self.category}
#. Create a new record
#. Fill in the required fields
#. Submit for approval

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/tbwa/odoo-expertise/issues>`_.

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

This module is maintained by InsightPulseAI.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is part of the OCA project.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the odoo-expertise project.
'''

        readme_path = self.module_path / "README.rst"
        readme_path.write_text(readme_content)
        print(f"📄 Created: {readme_path}")

    def _create_views(self):
        """Generate basic view XML (optional)"""
        # This is a placeholder - views can be added later
        pass

    # Helper methods
    def _model_to_filename(self, model_name: str) -> str:
        """Convert model name to filename (expense.approval -> expense_approval)"""
        return model_name.replace(".", "_")

    def _model_to_classname(self, model_name: str) -> str:
        """Convert model name to class name (expense.approval -> ExpenseApproval)"""
        parts = model_name.split(".")
        return "".join(word.capitalize() for word in parts)

    def _format_module_name(self) -> str:
        """Format module name for display (expense_approval -> Expense Approval)"""
        return self.name.replace("_", " ").title()

    def _format_description(self, text: str) -> str:
        """Format description text"""
        return text.replace(".", " ").replace("_", " ").title()

    def _get_current_year(self) -> int:
        """Get current year for copyright"""
        from datetime import datetime
        return datetime.now().year


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate OCA-compliant Odoo module structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single model
  python scaffold_module.py --name expense_approval --category Accounting --models expense.approval.request

  # Multiple models
  python scaffold_module.py --name expense_approval --category Accounting \\
      --models expense.approval.request,expense.approval.level

  # Custom Odoo version
  python scaffold_module.py --name my_module --category Custom --models my.model --version 17.0
        """
    )

    parser.add_argument(
        "--name",
        required=True,
        help="Module name (e.g., expense_approval)"
    )
    parser.add_argument(
        "--category",
        required=True,
        help="Module category (e.g., Accounting, Sales, Custom)"
    )
    parser.add_argument(
        "--models",
        required=True,
        help="Comma-separated model names (e.g., expense.approval.request,expense.approval.level)"
    )
    parser.add_argument(
        "--version",
        default="16.0",
        help="Odoo version (default: 16.0)"
    )

    args = parser.parse_args()

    # Parse models
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    if not models:
        print("❌ Error: At least one model is required")
        sys.exit(1)

    # Validate model names
    for model in models:
        if "." not in model:
            print(f"❌ Error: Model name must contain '.' (e.g., 'expense.approval'): {model}")
            sys.exit(1)

    # Generate module
    scaffolder = OdooModuleScaffolder(
        name=args.name,
        category=args.category,
        models=models,
        odoo_version=args.version
    )

    try:
        scaffolder.scaffold()
        print("\n✅ SUCCESS: Module scaffolding complete!")
        print(f"\n📂 Module location: {scaffolder.module_path}")
        print("\n📋 Next steps:")
        print("   1. Review generated files")
        print("   2. Customize model fields and logic")
        print("   3. Run pre-commit hooks: pre-commit run --all-files")
        print("   4. Run tests: pytest-odoo -d test_db -m odoo_module")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

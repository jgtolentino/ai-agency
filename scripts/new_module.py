#!/usr/bin/env python3
"""
Odoo Module Generator

Generates OCA-compliant Odoo modules using Jinja2 templates.

Usage:
    python scripts/new_module.py \\
        --name expense_approval \\
        --description "Expense approval workflow" \\
        --models "expense.approval:name,amount,state" \\
        --depends "base,account,project"

Features:
    - OCA-compliant module structure
    - Pre-commit hook validation
    - Automatic README generation
    - Security rules scaffolding
    - Test structure creation
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path
from typing import Dict, List

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except ImportError:
    print("ERROR: jinja2 not installed. Run: pip install jinja2")
    sys.exit(1)


class OdooModuleGenerator:
    """Generate OCA-compliant Odoo modules"""

    def __init__(self, template_dir: str = None, output_dir: str = None):
        self.template_dir = template_dir or self._get_template_dir()
        self.output_dir = output_dir or os.path.join(os.getcwd(), "custom_addons")

        # Setup Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _get_template_dir(self) -> str:
        """Find templates directory relative to script location"""
        script_dir = Path(__file__).parent.parent
        template_dir = script_dir / "templates"

        if not template_dir.exists():
            raise FileNotFoundError(
                f"Templates directory not found: {template_dir}\n"
                f"Expected location: {template_dir.absolute()}"
            )

        return str(template_dir)

    def generate_module(
        self,
        name: str,
        description: str,
        models: List[str] = None,
        depends: List[str] = None,
        author: str = "Odoo Community Association (OCA)",
        website: str = "https://github.com/OCA",
        category: str = "Uncategorized",
        version: str = "16.0.1.0.0",
        application: bool = False,
    ):
        """Generate complete module structure"""

        # Validate module name
        if not re.match(r'^[a-z][a-z0-9_]*$', name):
            raise ValueError(
                f"Invalid module name: {name}\n"
                f"Must start with lowercase letter and contain only lowercase letters, digits, and underscores"
            )

        # Parse models
        parsed_models = self._parse_models(models or [])

        # Prepare template context
        context = {
            'module_name': name,
            'display_name': self._to_display_name(name),
            'description': description,
            'author': author,
            'website': website,
            'category': category,
            'version': version,
            'year': datetime.datetime.now().year,
            'application': application,
            'depends': depends or ['base'],
            'models': parsed_models,
            'summary': description.split('.')[0] if '.' in description else description,
        }

        # Create module directory
        module_dir = Path(self.output_dir) / name
        self._create_directory_structure(module_dir, parsed_models)

        # Generate files
        self._generate_manifest(module_dir, context)
        self._generate_init_files(module_dir, parsed_models)
        self._generate_models(module_dir, context)
        self._generate_views(module_dir, context)
        self._generate_security(module_dir, context)
        self._generate_tests(module_dir, context)
        self._generate_readme(module_dir, context)

        print(f"✅ Module '{name}' generated successfully at: {module_dir}")
        print(f"\nNext steps:")
        print(f"  1. Review generated files in {module_dir}")
        print(f"  2. Install module: odoo-bin -d <database> -i {name}")
        print(f"  3. Run tests: pytest {module_dir}/tests/")
        print(f"  4. Run pre-commit: pre-commit run --all-files")

        return module_dir

    def _parse_models(self, models: List[str]) -> List[Dict]:
        """Parse model specifications

        Format: "model.name:field1,field2,field3"
        Example: "expense.approval:name,amount,state"
        """
        parsed = []

        for model_spec in models:
            if ':' not in model_spec:
                raise ValueError(
                    f"Invalid model specification: {model_spec}\n"
                    f"Expected format: model.name:field1,field2,field3"
                )

            model_name, fields_str = model_spec.split(':', 1)
            field_names = [f.strip() for f in fields_str.split(',') if f.strip()]

            # Convert model name to class name
            class_name = ''.join(word.capitalize() for word in model_name.split('.'))

            # Generate field definitions
            fields = []
            for field_name in field_names:
                field_type = self._infer_field_type(field_name)
                fields.append({
                    'name': field_name,
                    'type': field_type,
                    'string': field_name.replace('_', ' ').title(),
                    'required': field_name in ['name'],
                })

            parsed.append({
                'model_name': model_name,
                'class_name': class_name,
                'model_safe': model_name.replace('.', '_'),
                'description': f'{class_name} model',
                'fields': fields,
                'file_name': f'{model_name.replace(".", "_")}.py',
            })

        return parsed

    def _infer_field_type(self, field_name: str) -> str:
        """Infer Odoo field type from field name"""
        field_name_lower = field_name.lower()

        # Common patterns
        type_patterns = {
            'Char': ['name', 'code', 'reference', 'email', 'phone', 'url'],
            'Text': ['description', 'notes', 'comment', 'remarks'],
            'Integer': ['sequence', 'count', 'qty', 'quantity'],
            'Float': ['amount', 'price', 'rate', 'percentage', 'total'],
            'Boolean': ['active', 'is_', 'has_', 'can_'],
            'Date': ['date', '_date'],
            'Datetime': ['datetime', '_datetime', 'timestamp'],
            'Selection': ['state', 'status', 'type', 'stage'],
            'Many2one': ['_id'],
        }

        for field_type, patterns in type_patterns.items():
            if any(pattern in field_name_lower for pattern in patterns):
                return field_type

        # Default to Char
        return 'Char'

    def _to_display_name(self, name: str) -> str:
        """Convert module name to display name"""
        return ' '.join(word.capitalize() for word in name.split('_'))

    def _create_directory_structure(self, module_dir: Path, models: List[Dict]):
        """Create module directory structure"""
        directories = [
            module_dir,
            module_dir / 'models',
            module_dir / 'views',
            module_dir / 'security',
            module_dir / 'data',
            module_dir / 'tests',
            module_dir / 'static',
            module_dir / 'static' / 'description',
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _generate_manifest(self, module_dir: Path, context: Dict):
        """Generate __manifest__.py"""
        template = self.env.get_template('manifest.py.j2')

        # Prepare view files
        view_files = []
        for model in context.get('models', []):
            view_files.append(f"views/{model['model_safe']}_views.xml")

        context.update({
            'has_security': True,
            'view_files': view_files,
            'data_files': [],
            'demo_files': [],
        })

        content = template.render(**context)
        (module_dir / '__manifest__.py').write_text(content)

    def _generate_init_files(self, module_dir: Path, models: List[Dict]):
        """Generate __init__.py files"""
        # Root __init__.py
        model_imports = ', '.join(f'models' for _ in models) if models else ''
        root_init = f"# -*- coding: utf-8 -*-\n\nfrom . import {model_imports}\n" if models else "# -*- coding: utf-8 -*-\n"
        (module_dir / '__init__.py').write_text(root_init)

        # Models __init__.py
        if models:
            model_imports = '\n'.join(
                f"from . import {model['model_safe']}"
                for model in models
            )
            models_init = f"# -*- coding: utf-8 -*-\n\n{model_imports}\n"
            (module_dir / 'models' / '__init__.py').write_text(models_init)

        # Tests __init__.py
        (module_dir / 'tests' / '__init__.py').write_text(
            "# -*- coding: utf-8 -*-\n\nfrom . import test_common\n"
        )

    def _generate_models(self, module_dir: Path, context: Dict):
        """Generate model files"""
        template = self.env.get_template('model.py.j2')

        for model in context.get('models', []):
            model_context = {
                **context,
                **model,
                'model_description': model['description'],
                'order': 'id desc',
            }

            content = template.render(**model_context)
            file_path = module_dir / 'models' / model['file_name']
            file_path.write_text(content)

    def _generate_views(self, module_dir: Path, context: Dict):
        """Generate view XML files"""
        template = self.env.get_template('view.xml.j2')

        for model in context.get('models', []):
            view_context = {
                **context,
                'model_name': model['model_name'],
                'model_safe': model['model_safe'],
                'model_title': model['class_name'],
                'tree_view': True,
                'form_view': True,
                'search_view': True,
                'tree_fields': [{'name': f['name'], 'optional': False} for f in model['fields'][:5]],
                'form_fields': model['fields'],
                'search_fields': [{'name': f['name']} for f in model['fields'][:3]],
                'view_modes': ['tree', 'form'],
                'menu_items': [
                    {
                        'id': f"{model['model_safe']}_root",
                        'name': model['class_name'],
                        'action': f"action_{model['model_safe']}",
                        'sequence': 10,
                    }
                ],
            }

            content = template.render(**view_context)
            file_path = module_dir / 'views' / f"{model['model_safe']}_views.xml"
            file_path.write_text(content)

    def _generate_security(self, module_dir: Path, context: Dict):
        """Generate security files"""
        template = self.env.get_template('security.csv.j2')

        access_rules = []
        for model in context.get('models', []):
            # Add basic access rule for all users
            access_rules.append({
                'model_safe': model['model_safe'],
                'group_safe': 'user',
                'name': f"{model['model_name']} user access",
                'group_ref': 'base.group_user',
                'perm_read': '1',
                'perm_write': '1',
                'perm_create': '1',
                'perm_unlink': '1',
            })

        content = template.render(access_rules=access_rules)
        (module_dir / 'security' / 'ir.model.access.csv').write_text(content)

    def _generate_tests(self, module_dir: Path, context: Dict):
        """Generate test files"""
        # Generate test_common.py
        test_common = f"""# -*- coding: utf-8 -*-
# Copyright {context['year']} {context['author']}
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests.common import TransactionCase


class TestCommon(TransactionCase):
    \"\"\"Common test setup for {context['module_name']}\"\"\"

    def setUp(self):
        super().setUp()
        # TODO: Add common test setup
        pass
"""
        (module_dir / 'tests' / 'test_common.py').write_text(test_common)

        # Generate test file for each model
        for model in context.get('models', []):
            test_file = f"""# -*- coding: utf-8 -*-
# Copyright {context['year']} {context['author']}
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests import tagged
from .test_common import TestCommon


@tagged('post_install', '-at_install')
class Test{model['class_name']}(TestCommon):
    \"\"\"Tests for {model['model_name']} model\"\"\"

    def test_create_{model['model_safe']}(self):
        \"\"\"Test {model['model_name']} creation\"\"\"
        record = self.env['{model['model_name']}'].create({{
            'name': 'Test {model['class_name']}',
        }})
        self.assertTrue(record)
        self.assertEqual(record.name, 'Test {model['class_name']}')

    def test_{model['model_safe']}_constraints(self):
        \"\"\"Test {model['model_name']} constraints\"\"\"
        # TODO: Add constraint tests
        pass
"""
            (module_dir / 'tests' / f"test_{model['model_safe']}.py").write_text(test_file)

    def _generate_readme(self, module_dir: Path, context: Dict):
        """Generate README.rst"""
        readme = f"""===========================
{context['display_name']}
===========================

.. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

{context['description']}

**Table of contents**

.. contents::
   :local:

Usage
=====

To use this module, you need to:

#. Go to ...
#. ...

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/project/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Authors
~~~~~~~

* {context['author']}

Contributors
~~~~~~~~~~~~

* Your Name <your.email@example.com>

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/project <https://github.com/OCA/project/tree/{context['version'].split('.')[0]}.0/{context['module_name']}>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
"""
        (module_dir / 'README.rst').write_text(readme)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate OCA-compliant Odoo module',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic module with single model
  python scripts/new_module.py \\
    --name expense_approval \\
    --description "Expense approval workflow" \\
    --models "expense.approval:name,amount,state"

  # Module with dependencies
  python scripts/new_module.py \\
    --name hr_expense_custom \\
    --description "Custom expense management" \\
    --models "hr.expense.custom:name,employee_id,amount,state" \\
    --depends "base,hr,hr_expense"

  # Application module with multiple models
  python scripts/new_module.py \\
    --name project_management \\
    --description "Project management system" \\
    --models "project.task:name,description,deadline,status" \\
             "project.milestone:name,project_id,date" \\
    --application
        """
    )

    parser.add_argument('--name', required=True,
                        help='Module technical name (lowercase, underscores only)')
    parser.add_argument('--description', required=True,
                        help='Module description')
    parser.add_argument('--models', nargs='+',
                        help='Models to generate (format: model.name:field1,field2)')
    parser.add_argument('--depends', nargs='+', default=['base'],
                        help='Module dependencies (default: base)')
    parser.add_argument('--author', default='Odoo Community Association (OCA)',
                        help='Module author')
    parser.add_argument('--website', default='https://github.com/OCA',
                        help='Author website')
    parser.add_argument('--category', default='Uncategorized',
                        help='Module category')
    parser.add_argument('--version', default='16.0.1.0.0',
                        help='Module version (default: 16.0.1.0.0)')
    parser.add_argument('--application', action='store_true',
                        help='Mark as application module')
    parser.add_argument('--output-dir', default=None,
                        help='Output directory (default: ./custom_addons)')
    parser.add_argument('--template-dir', default=None,
                        help='Templates directory (default: ../templates)')

    args = parser.parse_args()

    try:
        generator = OdooModuleGenerator(
            template_dir=args.template_dir,
            output_dir=args.output_dir
        )

        module_dir = generator.generate_module(
            name=args.name,
            description=args.description,
            models=args.models,
            depends=args.depends,
            author=args.author,
            website=args.website,
            category=args.category,
            version=args.version,
            application=args.application,
        )

        sys.exit(0)

    except Exception as e:
        print(f"❌ Error generating module: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

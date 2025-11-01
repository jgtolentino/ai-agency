# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    'name': 'Pulser Webhook',
    'version': '16.0.1.0.0',
    'summary': 'Git-Ops dispatch from Odoo UI (webhook to GitHub)',
    'category': 'Tools',
    'author': 'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'views/pulser_gitops_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    'name': 'QMS SOP',
    'version': '16.0.1.0.0',
    'summary': 'QMS Standard Operating Procedures with error tracking',
    'category': 'Quality Management',
    'author': 'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sop_seeds.xml',
        'views/qms_sop_document_views.xml',
        'views/qms_sop_run_views.xml',
        'views/qms_error_code_views.xml',
        'views/menu_items.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

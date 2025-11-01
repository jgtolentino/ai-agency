# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    'name': 'Studio Automations',
    'version': '16.0.1.0.0',
    'summary': 'Automated actions for deployment workflows',
    'category': 'Tools',
    'author': 'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'project',
        'pulser_webhook',
        'qms_sop',
        'mail',
    ],
    'data': [
        'data/studio_automations.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

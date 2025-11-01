# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class QmsErrorCode(models.Model):
    """QMS Error Code Registry"""

    _name = 'qms.error.code'
    _description = 'QMS Error Code'
    _order = 'code'

    code = fields.Char(
        string='Code',
        required=True,
        copy=False,
        help='Unique error code identifier',
    )
    title = fields.Char(
        string='Title',
        required=True,
        help='Error description',
    )
    severity = fields.Selection(
        selection=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        string='Severity',
        required=True,
        default='medium',
        help='Error severity level',
    )
    sop_id = fields.Many2one(
        comodel_name='qms.sop.document',
        string='SOP',
        ondelete='set null',
        help='Related SOP for error resolution',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Error code must be unique!'),
    ]

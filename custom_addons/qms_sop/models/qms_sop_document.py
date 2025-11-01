# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class QmsSopDocument(models.Model):
    """QMS Standard Operating Procedure Document"""

    _name = 'qms.sop.document'
    _description = 'QMS SOP Document'
    _order = 'code, name'

    name = fields.Char(
        string='Name',
        required=True,
        help='SOP document title',
    )
    code = fields.Char(
        string='Code',
        required=True,
        copy=False,
        help='Unique SOP identifier (e.g., SOP-BUILD-001)',
    )
    category = fields.Selection(
        selection=[
            ('build', 'Build'),
            ('deploy', 'Deploy'),
            ('rollback', 'Rollback'),
            ('error_triage', 'Error Triage'),
        ],
        string='Category',
        required=True,
        default='build',
        help='SOP category classification',
    )
    content = fields.Html(
        string='Content',
        help='Detailed SOP documentation',
    )
    step_ids = fields.One2many(
        comodel_name='qms.sop.step',
        inverse_name='sop_id',
        string='Steps',
        help='Ordered SOP execution steps',
    )
    error_code_ids = fields.One2many(
        comodel_name='qms.error.code',
        inverse_name='sop_id',
        string='Error Codes',
        help='Associated error codes for this SOP',
    )
    run_ids = fields.One2many(
        comodel_name='qms.sop.run',
        inverse_name='sop_id',
        string='Runs',
        help='Execution history of this SOP',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'SOP code must be unique!'),
    ]

    @api.constrains('code')
    def _check_code_format(self):
        """Validate SOP code format"""
        for record in self:
            if not record.code.startswith('SOP-'):
                raise ValidationError(_(
                    'SOP code must start with "SOP-" prefix.\n'
                    'Example: SOP-BUILD-001'
                ))

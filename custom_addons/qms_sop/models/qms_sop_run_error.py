# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class QmsSopRunError(models.Model):
    """QMS SOP Run Error Tracking"""

    _name = 'qms.sop.run.error'
    _description = 'QMS SOP Run Error'
    _order = 'create_date desc'

    run_id = fields.Many2one(
        comodel_name='qms.sop.run',
        string='Run',
        required=True,
        ondelete='cascade',
        help='Parent SOP run',
    )
    error_code_id = fields.Many2one(
        comodel_name='qms.error.code',
        string='Error Code',
        help='Predefined error code',
    )
    description = fields.Text(
        string='Description',
        required=True,
        help='Error description and context',
    )
    created_at = fields.Datetime(
        string='Created At',
        default=fields.Datetime.now,
    )

    # Related fields for convenience
    error_code = fields.Char(
        related='error_code_id.code',
        string='Code',
        store=True,
    )
    error_severity = fields.Selection(
        related='error_code_id.severity',
        string='Severity',
        store=True,
    )

# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class QmsSopStep(models.Model):
    """QMS SOP Execution Step"""

    _name = 'qms.sop.step'
    _description = 'QMS SOP Step'
    _order = 'sop_id, sequence, id'

    sop_id = fields.Many2one(
        comodel_name='qms.sop.document',
        string='SOP',
        required=True,
        ondelete='cascade',
        help='Parent SOP document',
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Step execution order',
    )
    title = fields.Char(
        string='Title',
        required=True,
        help='Step title',
    )
    description = fields.Html(
        string='Description',
        help='Detailed step instructions',
    )

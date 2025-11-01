# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class QmsSopRunStep(models.Model):
    """QMS SOP Run Step Tracking"""

    _name = 'qms.sop.run.step'
    _description = 'QMS SOP Run Step'
    _order = 'run_id, step_id'

    run_id = fields.Many2one(
        comodel_name='qms.sop.run',
        string='Run',
        required=True,
        ondelete='cascade',
        help='Parent SOP run',
    )
    step_id = fields.Many2one(
        comodel_name='qms.sop.step',
        string='Step',
        required=True,
        ondelete='restrict',
        help='SOP step being executed',
    )
    state = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('skipped', 'Skipped'),
        ],
        string='State',
        default='pending',
        required=True,
        help='Step execution state',
    )
    notes = fields.Text(
        string='Notes',
        help='Execution notes and observations',
    )
    started_at = fields.Datetime(
        string='Started At',
    )
    completed_at = fields.Datetime(
        string='Completed At',
    )

    # Related fields for convenience
    step_sequence = fields.Integer(
        related='step_id.sequence',
        string='Sequence',
        store=True,
    )
    step_title = fields.Char(
        related='step_id.title',
        string='Title',
        store=True,
    )

    def action_start(self):
        """Mark step as in progress"""
        self.ensure_one()
        self.write({
            'state': 'in_progress',
            'started_at': fields.Datetime.now(),
        })

    def action_complete(self):
        """Mark step as completed"""
        self.ensure_one()
        self.write({
            'state': 'completed',
            'completed_at': fields.Datetime.now(),
        })

    def action_fail(self):
        """Mark step as failed"""
        self.ensure_one()
        self.write({
            'state': 'failed',
            'completed_at': fields.Datetime.now(),
        })

    def action_skip(self):
        """Mark step as skipped"""
        self.ensure_one()
        self.write({
            'state': 'skipped',
            'completed_at': fields.Datetime.now(),
        })

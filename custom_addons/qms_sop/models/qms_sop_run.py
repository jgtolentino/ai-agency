# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models


class QmsSopRun(models.Model):
    """QMS SOP Execution Run"""

    _name = 'qms.sop.run'
    _description = 'QMS SOP Run'
    _order = 'create_date desc, id desc'

    sop_id = fields.Many2one(
        comodel_name='qms.sop.document',
        string='SOP',
        required=True,
        ondelete='restrict',
        help='SOP being executed',
    )
    started_by = fields.Many2one(
        comodel_name='res.users',
        string='Started By',
        default=lambda self: self.env.user,
        help='User who initiated this run',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        string='State',
        default='draft',
        required=True,
        help='Execution state',
    )
    result = fields.Text(
        string='Result',
        help='Execution outcome and notes',
    )
    step_run_ids = fields.One2many(
        comodel_name='qms.sop.run.step',
        inverse_name='run_id',
        string='Step Runs',
        help='Individual step execution records',
    )
    error_ids = fields.One2many(
        comodel_name='qms.sop.run.error',
        inverse_name='run_id',
        string='Errors',
        help='Errors encountered during execution',
    )
    start_date = fields.Datetime(
        string='Start Date',
        default=fields.Datetime.now,
    )
    end_date = fields.Datetime(
        string='End Date',
    )

    @api.model
    def create(self, vals):
        """Auto-create step runs when SOP run is created"""
        run = super().create(vals)

        if run.sop_id and run.sop_id.step_ids:
            StepRun = self.env['qms.sop.run.step']
            for step in run.sop_id.step_ids:
                StepRun.create({
                    'run_id': run.id,
                    'step_id': step.id,
                    'state': 'pending',
                })

        return run

    def action_start(self):
        """Start SOP execution"""
        self.ensure_one()
        self.write({
            'state': 'in_progress',
            'start_date': fields.Datetime.now(),
        })

    def action_complete(self):
        """Mark SOP execution as completed"""
        self.ensure_one()
        self.write({
            'state': 'completed',
            'end_date': fields.Datetime.now(),
        })

    def action_fail(self):
        """Mark SOP execution as failed"""
        self.ensure_one()
        self.write({
            'state': 'failed',
            'end_date': fields.Datetime.now(),
        })

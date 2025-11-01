# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests.common import TransactionCase


class TestQmsSopRun(TransactionCase):
    """Test QMS SOP Run model and workflow"""

    def setUp(self):
        super().setUp()
        self.SopDocument = self.env['qms.sop.document']
        self.SopStep = self.env['qms.sop.step']
        self.SopRun = self.env['qms.sop.run']
        self.SopRunStep = self.env['qms.sop.run.step']
        self.SopRunError = self.env['qms.sop.run.error']
        self.ErrorCode = self.env['qms.error.code']

        # Create test SOP with steps
        self.sop = self.SopDocument.create({
            'name': 'Test Deployment',
            'code': 'SOP-RUN-001',
            'category': 'deploy',
        })

        self.step1 = self.SopStep.create({
            'sop_id': self.sop.id,
            'sequence': 10,
            'title': 'Prepare environment',
        })

        self.step2 = self.SopStep.create({
            'sop_id': self.sop.id,
            'sequence': 20,
            'title': 'Execute deployment',
        })

        self.step3 = self.SopStep.create({
            'sop_id': self.sop.id,
            'sequence': 30,
            'title': 'Verify deployment',
        })

    def test_sop_run_creation(self):
        """Test SOP run creation with auto-generated step runs"""
        run = self.SopRun.create({
            'sop_id': self.sop.id,
        })

        self.assertEqual(run.state, 'draft')
        self.assertEqual(run.started_by, self.env.user)
        self.assertEqual(len(run.step_run_ids), 3)
        self.assertTrue(all(s.state == 'pending' for s in run.step_run_ids))

    def test_sop_run_workflow(self):
        """Test complete SOP run workflow"""
        run = self.SopRun.create({
            'sop_id': self.sop.id,
        })

        # Start run
        run.action_start()
        self.assertEqual(run.state, 'in_progress')
        self.assertTrue(run.start_date)

        # Complete run
        run.action_complete()
        self.assertEqual(run.state, 'completed')
        self.assertTrue(run.end_date)

    def test_sop_run_failure(self):
        """Test SOP run failure state"""
        run = self.SopRun.create({
            'sop_id': self.sop.id,
        })

        run.action_start()
        run.action_fail()

        self.assertEqual(run.state, 'failed')
        self.assertTrue(run.end_date)

    def test_step_run_workflow(self):
        """Test individual step run workflow"""
        run = self.SopRun.create({
            'sop_id': self.sop.id,
        })

        step_run = run.step_run_ids[0]

        # Start step
        step_run.action_start()
        self.assertEqual(step_run.state, 'in_progress')
        self.assertTrue(step_run.started_at)

        # Complete step
        step_run.action_complete()
        self.assertEqual(step_run.state, 'completed')
        self.assertTrue(step_run.completed_at)

    def test_step_run_failure(self):
        """Test step run failure"""
        run = self.SopRun.create({
            'sop_id': self.sop.id,
        })

        step_run = run.step_run_ids[0]

        step_run.action_start()
        step_run.action_fail()

        self.assertEqual(step_run.state, 'failed')
        self.assertTrue(step_run.completed_at)

    def test_step_run_skip(self):
        """Test step run skip"""
        run = self.SopRun.create({
            'sop_id': self.sop.id,
        })

        step_run = run.step_run_ids[1]

        step_run.action_skip()

        self.assertEqual(step_run.state, 'skipped')
        self.assertTrue(step_run.completed_at)

    def test_error_tracking(self):
        """Test error tracking during SOP run"""
        run = self.SopRun.create({
            'sop_id': self.sop.id,
        })

        # Create error code
        error_code = self.ErrorCode.create({
            'code': 'DEPLOY_FAIL',
            'title': 'Deployment Failed',
            'severity': 'critical',
            'sop_id': self.sop.id,
        })

        # Log error during run
        error = self.SopRunError.create({
            'run_id': run.id,
            'error_code_id': error_code.id,
            'description': 'Health check failed after deployment',
        })

        self.assertEqual(len(run.error_ids), 1)
        self.assertEqual(error.error_code, 'DEPLOY_FAIL')
        self.assertEqual(error.error_severity, 'critical')

    def test_multiple_runs_same_sop(self):
        """Test multiple runs of the same SOP"""
        run1 = self.SopRun.create({
            'sop_id': self.sop.id,
        })

        run2 = self.SopRun.create({
            'sop_id': self.sop.id,
        })

        self.assertEqual(len(self.sop.run_ids), 2)
        self.assertIn(run1, self.sop.run_ids)
        self.assertIn(run2, self.sop.run_ids)

        # Verify runs are independent
        run1.action_start()
        self.assertEqual(run1.state, 'in_progress')
        self.assertEqual(run2.state, 'draft')

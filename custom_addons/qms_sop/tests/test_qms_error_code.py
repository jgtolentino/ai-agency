# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests.common import TransactionCase


class TestQmsErrorCode(TransactionCase):
    """Test QMS Error Code model"""

    def setUp(self):
        super().setUp()
        self.ErrorCode = self.env['qms.error.code']
        self.SopDocument = self.env['qms.sop.document']

    def test_error_code_creation(self):
        """Test error code can be created"""
        error = self.ErrorCode.create({
            'code': 'TEST_ERROR',
            'title': 'Test Error',
            'severity': 'medium',
        })

        self.assertEqual(error.code, 'TEST_ERROR')
        self.assertEqual(error.title, 'Test Error')
        self.assertEqual(error.severity, 'medium')
        self.assertTrue(error.active)

    def test_error_code_unique_constraint(self):
        """Test error code must be unique"""
        self.ErrorCode.create({
            'code': 'DUP_ERROR',
            'title': 'First Error',
            'severity': 'low',
        })

        with self.assertRaises(Exception):
            self.ErrorCode.create({
                'code': 'DUP_ERROR',
                'title': 'Second Error',
                'severity': 'high',
            })

    def test_error_code_with_sop(self):
        """Test error code linked to SOP"""
        sop = self.SopDocument.create({
            'name': 'Test SOP',
            'code': 'SOP-ERR-001',
            'category': 'build',
        })

        error = self.ErrorCode.create({
            'code': 'BUILD_FAIL',
            'title': 'Build Failed',
            'severity': 'critical',
            'sop_id': sop.id,
        })

        self.assertEqual(error.sop_id, sop)
        self.assertIn(error, sop.error_code_ids)

    def test_error_code_severity_levels(self):
        """Test all severity levels"""
        severities = ['low', 'medium', 'high', 'critical']

        for sev in severities:
            error = self.ErrorCode.create({
                'code': 'ERROR_%s' % sev.upper(),
                'title': '%s Severity Error' % sev.capitalize(),
                'severity': sev,
            })

            self.assertEqual(error.severity, sev)

    def test_error_code_without_sop(self):
        """Test error code can exist without SOP"""
        error = self.ErrorCode.create({
            'code': 'ORPHAN_ERROR',
            'title': 'Orphan Error',
            'severity': 'medium',
        })

        self.assertFalse(error.sop_id)

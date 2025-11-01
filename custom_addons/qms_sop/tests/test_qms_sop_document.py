# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestQmsSopDocument(TransactionCase):
    """Test QMS SOP Document model"""

    def setUp(self):
        super().setUp()
        self.SopDocument = self.env['qms.sop.document']
        self.SopStep = self.env['qms.sop.step']
        self.ErrorCode = self.env['qms.error.code']

    def test_sop_document_creation(self):
        """Test SOP document can be created"""
        sop = self.SopDocument.create({
            'name': 'Test Build Process',
            'code': 'SOP-TEST-001',
            'category': 'build',
            'content': '<p>Test content</p>',
        })

        self.assertEqual(sop.name, 'Test Build Process')
        self.assertEqual(sop.code, 'SOP-TEST-001')
        self.assertEqual(sop.category, 'build')
        self.assertTrue(sop.active)

    def test_sop_code_unique_constraint(self):
        """Test SOP code must be unique"""
        self.SopDocument.create({
            'name': 'First SOP',
            'code': 'SOP-DUP-001',
            'category': 'build',
        })

        with self.assertRaises(Exception):
            self.SopDocument.create({
                'name': 'Second SOP',
                'code': 'SOP-DUP-001',
                'category': 'deploy',
            })

    def test_sop_code_validation(self):
        """Test SOP code format validation"""
        with self.assertRaises(ValidationError):
            self.SopDocument.create({
                'name': 'Invalid Code SOP',
                'code': 'INVALID-001',
                'category': 'build',
            })

    def test_sop_with_steps(self):
        """Test SOP with execution steps"""
        sop = self.SopDocument.create({
            'name': 'Multi-Step SOP',
            'code': 'SOP-STEPS-001',
            'category': 'deploy',
        })

        step1 = self.SopStep.create({
            'sop_id': sop.id,
            'sequence': 10,
            'title': 'First Step',
            'description': '<p>Do something</p>',
        })

        step2 = self.SopStep.create({
            'sop_id': sop.id,
            'sequence': 20,
            'title': 'Second Step',
            'description': '<p>Do something else</p>',
        })

        self.assertEqual(len(sop.step_ids), 2)
        self.assertEqual(sop.step_ids[0].sequence, 10)
        self.assertEqual(sop.step_ids[1].sequence, 20)

    def test_sop_with_error_codes(self):
        """Test SOP with associated error codes"""
        sop = self.SopDocument.create({
            'name': 'Error-Prone SOP',
            'code': 'SOP-ERROR-001',
            'category': 'build',
        })

        error1 = self.ErrorCode.create({
            'code': 'TEST_ERROR_1',
            'title': 'Test Error 1',
            'severity': 'high',
            'sop_id': sop.id,
        })

        error2 = self.ErrorCode.create({
            'code': 'TEST_ERROR_2',
            'title': 'Test Error 2',
            'severity': 'critical',
            'sop_id': sop.id,
        })

        self.assertEqual(len(sop.error_code_ids), 2)
        self.assertIn(error1, sop.error_code_ids)
        self.assertIn(error2, sop.error_code_ids)

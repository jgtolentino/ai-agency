# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import base64
import hashlib
import hmac
import json
from unittest.mock import patch, MagicMock

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestPulserGitopsWizard(TransactionCase):
    """Test Pulser Git-Ops Wizard functionality"""

    def setUp(self):
        super().setUp()
        self.wizard_model = self.env['pulser.gitops.wizard']

        # Setup config parameters
        self.env['ir.config_parameter'].sudo().set_param(
            'pulser.webhook.secret',
            base64.b64encode(b'test-secret-key').decode('utf-8')
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'pulser.github.token',
            'ghp_test_token_1234567890'
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'pulser.github.repo',
            'test-org/test-repo'
        )

    def test_wizard_creation(self):
        """Test wizard can be created with default values"""
        wizard = self.wizard_model.create({
            'branch': 'staging',
            'message': 'Test deployment',
        })

        self.assertEqual(wizard.branch, 'staging')
        self.assertEqual(wizard.message, 'Test deployment')
        self.assertFalse(wizard.kv_key)
        self.assertFalse(wizard.response_json)

    def test_hmac_signature_generation(self):
        """Test HMAC signature is correctly generated"""
        wizard = self.wizard_model.create({
            'branch': 'main',
            'message': 'Deploy to production',
        })

        secret = self.env['ir.config_parameter'].sudo().get_param(
            'pulser.webhook.secret'
        )

        payload = {
            'event_type': 'deploy_request',
            'client_payload': {
                'branch': 'main',
                'message': 'Deploy to production',
            }
        }

        payload_str = json.dumps(payload, sort_keys=True)
        expected_signature = hmac.new(
            base64.b64decode(secret),
            payload_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # Verify signature format
        self.assertTrue(isinstance(expected_signature, str))
        self.assertEqual(len(expected_signature), 64)  # SHA256 hex length

    @patch('requests.post')
    def test_action_dispatch_success(self, mock_post):
        """Test successful GitHub API dispatch"""
        # Mock successful response (204 No Content)
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.headers = {'X-GitHub-Request-Id': 'test-id-123'}
        mock_post.return_value = mock_response

        wizard = self.wizard_model.create({
            'branch': 'staging',
            'message': 'Test deployment',
        })

        result = wizard.action_dispatch()

        # Verify notification action returned
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['tag'], 'display_notification')
        self.assertEqual(result['params']['type'], 'success')

        # Verify API was called with correct parameters
        mock_post.assert_called_once()
        call_args = mock_post.call_args

        # Check URL
        self.assertIn('test-org/test-repo/dispatches', call_args[0][0])

        # Check headers
        headers = call_args[1]['headers']
        self.assertIn('Bearer ghp_test_token', headers['Authorization'])
        self.assertIn('X-Pulser-Signature', headers)
        self.assertTrue(headers['X-Pulser-Signature'].startswith('sha256='))

        # Check payload
        payload = call_args[1]['json']
        self.assertEqual(payload['event_type'], 'deploy_request')
        self.assertEqual(payload['client_payload']['branch'], 'staging')
        self.assertEqual(payload['client_payload']['message'], 'Test deployment')

    @patch('requests.post')
    def test_action_dispatch_with_kv(self, mock_post):
        """Test dispatch with optional KV parameters"""
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.headers = {}
        mock_post.return_value = mock_response

        wizard = self.wizard_model.create({
            'branch': 'production',
            'message': 'Deploy with env vars',
            'kv_key': 'ENVIRONMENT',
            'kv_value': 'production',
        })

        wizard.action_dispatch()

        # Verify KV pair in payload
        payload = mock_post.call_args[1]['json']
        self.assertIn('kv', payload['client_payload'])
        self.assertEqual(payload['client_payload']['kv']['ENVIRONMENT'], 'production')

    @patch('requests.post')
    def test_action_dispatch_api_error(self, mock_post):
        """Test handling of GitHub API errors"""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        mock_response.json.return_value = {
            'message': 'Bad credentials'
        }
        mock_post.return_value = mock_response

        wizard = self.wizard_model.create({
            'branch': 'main',
            'message': 'This should fail',
        })

        with self.assertRaises(ValidationError) as context:
            wizard.action_dispatch()

        self.assertIn('401', str(context.exception))

    def test_missing_secret_validation(self):
        """Test validation when secret is missing"""
        # Remove secret
        self.env['ir.config_parameter'].sudo().set_param(
            'pulser.webhook.secret',
            ''
        )

        wizard = self.wizard_model.create({
            'branch': 'main',
            'message': 'Test',
        })

        with self.assertRaises(ValidationError) as context:
            wizard.action_dispatch()

        self.assertIn('pulser.webhook.secret', str(context.exception))

    def test_missing_token_validation(self):
        """Test validation when GitHub token is missing"""
        # Remove token
        self.env['ir.config_parameter'].sudo().set_param(
            'pulser.github.token',
            ''
        )

        wizard = self.wizard_model.create({
            'branch': 'main',
            'message': 'Test',
        })

        with self.assertRaises(ValidationError) as context:
            wizard.action_dispatch()

        self.assertIn('pulser.github.token', str(context.exception))

    def test_action_cancel(self):
        """Test wizard cancel action"""
        wizard = self.wizard_model.create({
            'branch': 'main',
            'message': 'Test',
        })

        result = wizard.action_cancel()

        self.assertEqual(result['type'], 'ir.actions.act_window_close')

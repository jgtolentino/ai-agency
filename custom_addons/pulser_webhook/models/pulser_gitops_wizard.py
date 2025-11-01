# -*- coding: utf-8 -*-
# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import base64
import hashlib
import hmac
import json
import logging

import requests

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PulserGitopsWizard(models.TransientModel):
    """Git-Ops Dispatch Wizard

    Sends repository_dispatch webhook to GitHub with HMAC signature
    for secure Git-Ops workflows triggered from Odoo UI.
    """

    _name = 'pulser.gitops.wizard'
    _description = 'Git-Ops Dispatch Wizard'

    # Fields
    branch = fields.Char(
        string='Branch',
        required=True,
        default='main',
        help='Target branch for deployment',
    )
    message = fields.Text(
        string='Commit Message',
        required=True,
        help='Description of the deployment or operation',
    )
    kv_key = fields.Char(
        string='KV Key',
        help='Optional key-value parameter key (e.g., environment variable name)',
    )
    kv_value = fields.Char(
        string='KV Value',
        help='Optional key-value parameter value',
    )
    response_json = fields.Text(
        string='Response',
        readonly=True,
        help='GitHub API response details',
    )

    def action_dispatch(self):
        """Send repository_dispatch to GitHub API with HMAC signature

        Workflow:
        1. Build payload with event_type and client_payload
        2. Generate HMAC-SHA256 signature from secret
        3. Send POST to GitHub API with signature header
        4. Handle response and display notification

        Returns:
            dict: Notification action or error
        """
        self.ensure_one()

        # Build payload
        payload = {
            'event_type': 'deploy_request',
            'client_payload': {
                'branch': self.branch,
                'message': self.message,
            }
        }

        # Add optional KV pair
        if self.kv_key:
            payload['client_payload']['kv'] = {
                self.kv_key: self.kv_value or ''
            }

        # Get configuration from system parameters
        IrConfigParameter = self.env['ir.config_parameter'].sudo()

        secret = IrConfigParameter.get_param('pulser.webhook.secret')
        if not secret:
            raise ValidationError(_(
                'Missing pulser.webhook.secret in System Parameters.\n'
                'Configure in Settings > Technical > Parameters > System Parameters'
            ))

        github_token = IrConfigParameter.get_param('pulser.github.token')
        if not github_token:
            raise ValidationError(_(
                'Missing pulser.github.token in System Parameters.\n'
                'Configure in Settings > Technical > Parameters > System Parameters'
            ))

        repo = IrConfigParameter.get_param('pulser.github.repo')
        if not repo:
            raise ValidationError(_(
                'Missing pulser.github.repo in System Parameters.\n'
                'Configure in Settings > Technical > Parameters > System Parameters'
            ))

        # Generate HMAC signature
        try:
            payload_str = json.dumps(payload, sort_keys=True)
            signature = hmac.new(
                base64.b64decode(secret),
                payload_str.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
        except Exception as e:
            _logger.error('Failed to generate HMAC signature: %s', str(e))
            raise ValidationError(_(
                'Failed to generate HMAC signature.\n'
                'Ensure pulser.webhook.secret is a valid base64-encoded string.\n'
                'Error: %s'
            ) % str(e))

        # GitHub API call
        url = f'https://api.github.com/repos/{repo}/dispatches'
        headers = {
            'Authorization': f'Bearer {github_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
            'X-Pulser-Signature': f'sha256={signature}',
        }

        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=10
            )

            # Store response
            response_data = {
                'status_code': response.status_code,
                'headers': dict(response.headers),
            }

            # GitHub repository_dispatch returns 204 No Content on success
            if response.status_code == 204:
                response_data['message'] = 'Dispatch successful'
            else:
                try:
                    response_data['body'] = response.json()
                except ValueError:
                    response_data['body'] = response.text

            self.response_json = json.dumps(response_data, indent=2)

            if response.status_code == 204:
                _logger.info(
                    'Dispatched Git-Ops event to %s:%s - %s',
                    repo, self.branch, self.message
                )
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Success'),
                        'message': _(
                            'Dispatched to %s:%s\n%s'
                        ) % (repo, self.branch, self.message),
                        'sticky': False,
                        'type': 'success',
                    }
                }
            else:
                error_msg = response_data.get('body', {}).get(
                    'message',
                    response.text
                )
                raise ValidationError(_(
                    'GitHub API error: %s\n%s'
                ) % (response.status_code, error_msg))

        except requests.exceptions.Timeout:
            raise UserError(_(
                'GitHub API request timeout.\n'
                'Please check network connectivity and try again.'
            ))
        except requests.exceptions.ConnectionError as e:
            raise UserError(_(
                'Failed to connect to GitHub API.\n'
                'Error: %s'
            ) % str(e))
        except requests.exceptions.RequestException as e:
            _logger.error('GitHub API request failed: %s', str(e))
            raise UserError(_(
                'GitHub API request failed.\n'
                'Error: %s'
            ) % str(e))

    def action_cancel(self):
        """Cancel wizard"""
        return {
            'type': 'ir.actions.act_window_close'
        }

# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import logging
import os
import time

import requests
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PulserPulseHubWizard(models.TransientModel):
    """
    Wizard for triggering pulse-hub deployment via GitHub repository_dispatch.

    Opens from Settings > Technical > Pulser > Deploy Pulse-Hub menu.

    Workflow:
        1. User selects environment (staging/production)
        2. User specifies image tag and service to deploy
        3. Wizard generates HMAC-signed payload
        4. POST to GitHub API /repos/{owner}/{repo}/dispatches
        5. Event type: 'deploy_pulse_hub'
        6. GitHub Actions workflow (deploy-pulse-hub.yml) runs
        7. DigitalOcean App Platform deployment triggered

    Requirements:
        - GITHUB_REPO_OWNER: Repository owner (e.g., jgtolentino)
        - GITHUB_REPO_NAME: Repository name (e.g., insightpulse-odoo)
        - GITHUB_APP_ID: GitHub App ID or Client ID
        - GITHUB_INSTALLATION_ID: Installation ID for the repository
        - GITHUB_APP_PRIVATE_KEY_BASE64: Base64-encoded private key
        - PULSER_WEBHOOK_SECRET: Shared secret for HMAC signature
    """
    _name = "pulser.pulse.hub.wizard"
    _description = "Pulser Pulse-Hub Deployment"

    environment = fields.Selection(
        [
            ("staging", "Staging"),
            ("production", "Production"),
        ],
        string="Environment",
        required=True,
        default="staging",
        help="Target deployment environment",
    )
    image_tag = fields.Char(
        string="Image Tag",
        required=True,
        default="latest",
        help="Docker image tag to deploy (e.g., latest, v1.0.0, commit-sha)",
    )
    service = fields.Selection(
        [
            ("web", "Web"),
            ("mcp", "MCP"),
            ("superset", "Superset"),
            ("all", "All Services"),
        ],
        string="Service",
        required=True,
        default="all",
        help="Service to deploy (or all services)",
    )
    response_json = fields.Text(
        string="Response",
        readonly=True,
        help="GitHub API response (JSON format)",
    )

    @api.constrains("image_tag")
    def _check_image_tag(self):
        """Validate image tag format."""
        for record in self:
            if not record.image_tag:
                raise ValidationError(_("Image tag cannot be empty."))

            # Basic validation: alphanumeric, dash, dot, underscore
            if not all(c.isalnum() or c in "-._" for c in record.image_tag):
                raise ValidationError(
                    _("Image tag contains invalid characters. "
                      "Use only alphanumeric, dash, dot, or underscore.")
                )

    def _get_github_installation_token(self):
        """
        Generate GitHub App Installation Access Token.

        Process:
            1. Load GitHub App private key from base64-encoded env var
            2. Generate JWT with App ID and expiration
            3. Exchange JWT for Installation Access Token
            4. Return token for API authentication

        Returns:
            str: GitHub Installation Access Token

        Raises:
            UserError: If any required environment variable is missing or token exchange fails
        """
        import jwt  # PyJWT dependency

        # Get required environment variables
        app_id = os.getenv("GITHUB_APP_ID", "")
        installation_id = os.getenv("GITHUB_INSTALLATION_ID", "")
        private_key_b64 = os.getenv("GITHUB_APP_PRIVATE_KEY_BASE64", "")

        if not app_id:
            raise UserError(_("Missing GITHUB_APP_ID in environment."))
        if not installation_id:
            raise UserError(_("Missing GITHUB_INSTALLATION_ID in environment."))
        if not private_key_b64:
            raise UserError(_("Missing GITHUB_APP_PRIVATE_KEY_BASE64 in environment."))

        try:
            # Decode private key from base64
            private_key = base64.b64decode(private_key_b64).decode("utf-8")
        except Exception as e:
            _logger.exception("Failed to decode GitHub App private key: %s", e)
            raise UserError(_("Invalid GITHUB_APP_PRIVATE_KEY_BASE64 encoding: %s") % str(e))

        # Generate JWT
        now = int(time.time())
        payload = {
            "iat": now - 60,  # Issued 60 seconds in the past to account for clock drift
            "exp": now + 600,  # Expires in 10 minutes
            "iss": app_id,
        }

        try:
            jwt_token = jwt.encode(payload, private_key, algorithm="RS256")
        except Exception as e:
            _logger.exception("Failed to generate GitHub App JWT: %s", e)
            raise UserError(_("JWT generation failed: %s") % str(e))

        # Exchange JWT for Installation Access Token
        url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        try:
            response = requests.post(url, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            token = data.get("token")

            if not token:
                raise UserError(_("GitHub API did not return access token."))

            _logger.info("Successfully obtained GitHub Installation Access Token")
            return token

        except requests.RequestException as e:
            _logger.exception("GitHub token exchange failed: %s", e)
            raise UserError(_("Failed to obtain GitHub token: %s") % str(e))

    def _generate_hmac_signature(self, payload_str):
        """
        Generate HMAC-SHA256 signature for payload.

        Args:
            payload_str (str): JSON payload string

        Returns:
            str: HMAC signature in format "sha256=<hexdigest>"

        Raises:
            UserError: If PULSER_WEBHOOK_SECRET is missing
        """
        secret = os.getenv("PULSER_WEBHOOK_SECRET", "")
        if not secret:
            raise UserError(_("Missing PULSER_WEBHOOK_SECRET in environment."))

        body = payload_str.encode("utf-8")
        signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

        return f"sha256={signature}"

    def action_dispatch_pulse_hub(self):
        """
        Dispatch pulse-hub deployment event to GitHub Actions.

        Process:
            1. Validate environment variables (GitHub App credentials)
            2. Build deployment payload (environment, image_tag, service)
            3. Generate HMAC signature for security
            4. Get GitHub Installation Access Token
            5. POST to /repos/{owner}/{repo}/dispatches
            6. Display response in wizard

        GitHub API Reference:
            https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event

        Returns:
            dict: Notification action for user feedback

        Raises:
            UserError: If GitHub API call fails or validation errors occur
        """
        self.ensure_one()

        # Get repository information
        repo_owner = os.getenv("GITHUB_REPO_OWNER", "")
        repo_name = os.getenv("GITHUB_REPO_NAME", "")

        if not repo_owner:
            raise UserError(_("Missing GITHUB_REPO_OWNER in environment."))
        if not repo_name:
            raise UserError(_("Missing GITHUB_REPO_NAME in environment."))

        # Build deployment payload
        client_payload = {
            "environment": self.environment,
            "image_tag": self.image_tag,
            "service": self.service,
            "timestamp": int(time.time()),
            "triggered_by": "odoo_wizard",
            "odoo_user": self.env.user.name,
        }

        payload = {
            "event_type": "deploy_pulse_hub",
            "client_payload": client_payload,
        }

        # Generate HMAC signature
        payload_str = json.dumps(payload, separators=(",", ":"))
        signature = self._generate_hmac_signature(payload_str)

        # Get GitHub Installation Access Token
        try:
            github_token = self._get_github_installation_token()
        except UserError:
            raise
        except Exception as e:
            _logger.exception("Unexpected error getting GitHub token: %s", e)
            raise UserError(_("Unexpected error: %s") % str(e))

        # Prepare GitHub API request
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/dispatches"
        headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
            "X-Pulser-Signature": signature,
        }

        # POST to GitHub API
        try:
            _logger.info(
                "Dispatching pulse-hub deployment: env=%s, tag=%s, service=%s",
                self.environment,
                self.image_tag,
                self.service,
            )

            response = requests.post(
                url,
                headers=headers,
                data=payload_str,
                timeout=20,
            )

            # GitHub API returns 204 No Content on success
            if response.status_code == 204:
                self.response_json = json.dumps(
                    {
                        "status": "success",
                        "message": "Deployment dispatched successfully",
                        "environment": self.environment,
                        "image_tag": self.image_tag,
                        "service": self.service,
                        "repository": f"{repo_owner}/{repo_name}",
                    },
                    indent=2,
                )

                _logger.info(
                    "Pulse-hub deployment dispatched successfully: %s @ %s (%s)",
                    self.service,
                    self.image_tag,
                    self.environment,
                )

                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Deployment Dispatched"),
                        "message": _(
                            "Pulse-hub deployment triggered: %(service)s @ %(tag)s (%(env)s)"
                        ) % {
                            "service": self.service,
                            "tag": self.image_tag,
                            "env": self.environment,
                        },
                        "type": "success",
                        "sticky": False,
                    },
                }
            else:
                # API error - capture response for debugging
                try:
                    error_data = response.json()
                except ValueError:
                    error_data = {"raw_response": response.text}

                self.response_json = json.dumps(
                    {
                        "status": "error",
                        "http_status": response.status_code,
                        "error": error_data,
                    },
                    indent=2,
                )

                _logger.error(
                    "GitHub API dispatch failed: HTTP %s - %s",
                    response.status_code,
                    response.text,
                )

                raise UserError(
                    _("GitHub API dispatch failed (HTTP %(status)s). "
                      "See response field for details.") % {"status": response.status_code}
                )

        except requests.RequestException as e:
            _logger.exception("HTTP error dispatching pulse-hub deployment: %s", e)

            self.response_json = json.dumps(
                {
                    "status": "error",
                    "message": str(e),
                },
                indent=2,
            )

            raise UserError(_("HTTP request failed: %s") % str(e))

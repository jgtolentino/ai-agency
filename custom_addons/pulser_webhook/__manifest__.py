# -*- coding: utf-8 -*-
{
    "name": "Pulser Webhook",
    "summary": "Triggers GitHub repository_dispatch (git-ops) from Odoo",
    "description": """
        GitHub App Integration for Git Operations
        ==========================================

        * Triggers repository_dispatch events to GitHub Actions
        * Uses GitHub App authentication (Installation Access Token)
        * Server Action for one-click Git-Ops from any record
        * Webhook endpoint with HMAC signature validation
        * Targeted bindings: Project Task, Sale Order, Invoice/Bill, Expense, Purchase Order
        * Pulse-Hub deployment wizard for DigitalOcean App Platform

        Environment Variables Required:
        * PULSER_WEBHOOK_SECRET: Shared secret for webhook auth
        * GITHUB_APP_ID: GitHub App ID (2191216) or Client ID
        * GITHUB_INSTALLATION_ID: Installation ID for your org/repo
        * GITHUB_REPO_OWNER: Repository owner (e.g., jgtolentino)
        * GITHUB_REPO_NAME: Repository name (e.g., insightpulse-odoo)
        * GITHUB_APP_PRIVATE_KEY_BASE64: Base64-encoded .pem private key
    """,
    "version": "16.0.1.1.0",
    "license": "LGPL-3",
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/insightpulse-odoo",
    "category": "Tools",
    "depends": [
        "base",
        "project",
        "sale_management",
        "account",
        "hr_expense",
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/gitops_wizard_views.xml",
        "views/gitops_bindings.xml",
        "views/pulse_hub_wizard_views.xml",
    ],
    "external_dependencies": {
        "python": ["PyJWT"],  # For GitHub App JWT generation
    },
    "application": False,
    "installable": True,
    "auto_install": False,
}

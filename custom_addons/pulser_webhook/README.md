# Pulser Webhook - GitHub App Integration

GitHub App integration for triggering repository_dispatch events from Odoo.

## Features

- ✅ **GitHub App Authentication**: Uses Installation Access Tokens via JWT
- ✅ **Webhook Endpoint**: `/pulser/git-ops` with HMAC signature validation
- ✅ **Server Actions**: One-click Git-Ops from any Odoo record
- ✅ **Targeted Bindings**: Project Task, Sale Order, Invoice/Bill, Expense, Purchase Order
- ✅ **GitHub Actions Integration**: Triggers `git-ops` workflow via repository_dispatch
- ✅ **Pulse-Hub Deployment**: DigitalOcean App Platform deployment wizard

## Installation

### 1) GitHub App Setup

1. Create GitHub App at: https://github.com/settings/apps/new
   - **Name**: pulser-hub (or your choice)
   - **Permissions**:
     - Contents: Read & Write
     - Pull Requests: Read & Write
     - Metadata: Read-only
   - **Events**: None (we use repository_dispatch)

2. Install the app on your repository

3. Note these values:
   - **App ID**: 2191216 (or your Client ID: Iv23liwGL7fnYySPPAjS)
   - **Installation ID**: Get from installation URL
   - **Private Key**: Generate and download .pem file

### 2) Environment Variables

Add to your Odoo container environment (`.env`, `odoo.conf`, or DigitalOcean App Platform):

```bash
# GitHub App credentials
GITHUB_APP_ID=2191216
GITHUB_INSTALLATION_ID=your_installation_id
GITHUB_REPO_OWNER=jgtolentino
GITHUB_REPO_NAME=insightpulse-odoo

# GitHub App private key (base64-encoded)
GITHUB_APP_PRIVATE_KEY_BASE64=LS0tLS1CRUdJTi...  # base64 -w0 your-app.pem

# Webhook secret for HMAC validation
PULSER_WEBHOOK_SECRET=change_me_to_random_string
```

### 3) GitHub Actions Secrets & Variables

In your repository Settings → Secrets and variables → Actions:

**Variables**:
- `APP_ID` = `2191216` (or Client ID)

**Secrets**:
- `PRIVATE_KEY` = paste your `.pem` file contents (multiline OK)

### 4) Install Odoo Addon

```bash
# Update apps list
docker compose -f deploy/odoo.bundle.yml exec odoo odoo shell -c "self.env['ir.module.module'].update_list()"

# Install via UI: Apps → Update Apps List → Search "Pulser Webhook" → Install
# Or via CLI:
docker compose -f deploy/odoo.bundle.yml exec odoo odoo -d postgres -i pulser_webhook --stop-after-init
```

## Usage

### From Odoo (Server Action)

1. Open any supported record (Project Task, Sale Order, Invoice, Expense, Purchase Order)
2. Click **Action** → **Pulser: Dispatch Git-Ops…**
3. Configure:
   - **Branch**: Target branch (default: `gitops/push`)
   - **Message**: Git commit message
   - **KV Key/Value** (optional): Write key-value pair to `ops/kv/<key>.txt`
4. Click **Dispatch**
5. Check GitHub Actions → `git-ops` workflow

### Via Webhook (External)

```bash
BODY='{"branch":"gitops/push","message":"chore: webhook dispatch","kv_key":"env","kv_value":"staging"}'
SIG="sha256=$(printf '%s' "$BODY" | openssl dgst -sha256 -hmac "$PULSER_WEBHOOK_SECRET" -r | awk '{print $1}')"

curl -s http://your-odoo-host/pulser/git-ops \
  -H "Content-Type: application/json" \
  -H "X-Pulser-Secret: $PULSER_WEBHOOK_SECRET" \
  -H "X-Pulser-Signature: $SIG" \
  -d "$BODY"
```

### Manual GitHub Actions Trigger

1. Go to: https://github.com/jgtolentino/insightpulse-odoo/actions/workflows/git-ops.yml
2. Click **Run workflow**
3. Enter branch, message, and optional KV pairs
4. Workflow creates branch, commits changes, opens PR to main

### Pulse-Hub Deployment (DigitalOcean App Platform)

**New Feature**: Deploy pulse-hub services directly from Odoo using GitHub repository_dispatch.

**Access**: Settings → Technical → Pulser → Deploy Pulse-Hub

**Configuration**:
1. **Environment**: Staging or Production
2. **Image Tag**: Docker image tag (e.g., `latest`, `v1.0.0`, commit SHA)
3. **Service**: Web, MCP, Superset, or All Services
4. Click **Deploy Pulse-Hub**

**Workflow**:
```
Odoo Wizard
    ↓
pulser.pulse.hub.wizard
    ↓
Generate HMAC-signed payload
    ↓
GitHub App JWT → Installation Token
    ↓
POST /repos/{owner}/{repo}/dispatches
    ↓
Event type: deploy_pulse_hub
    ↓
GitHub Actions: deploy-pulse-hub.yml
    ↓
DigitalOcean App Platform deployment
```

**Payload Example**:
```json
{
  "event_type": "deploy_pulse_hub",
  "client_payload": {
    "environment": "staging",
    "image_tag": "latest",
    "service": "all",
    "timestamp": 1699012345,
    "triggered_by": "odoo_wizard",
    "odoo_user": "Administrator"
  }
}
```

**GitHub Actions Workflow**:
Create `.github/workflows/deploy-pulse-hub.yml`:
```yaml
name: Deploy Pulse-Hub

on:
  repository_dispatch:
    types: [deploy_pulse_hub]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Deploy to DigitalOcean App Platform
        run: |
          ENV="${{ github.event.client_payload.environment }}"
          TAG="${{ github.event.client_payload.image_tag }}"
          SERVICE="${{ github.event.client_payload.service }}"

          echo "Deploying $SERVICE @ $TAG to $ENV"

          # Update app spec and trigger deployment
          doctl apps update <app-id> --spec infra/do/pulse-hub-$ENV.yaml
          doctl apps create-deployment <app-id> --force-rebuild
```

**Security**:
- ✅ HMAC-SHA256 signature on all requests
- ✅ GitHub App Installation Tokens (auto-expire)
- ✅ Access restricted to base.group_system (Technical Features)
- ✅ Deployment triggered via secure GitHub Actions

## Workflow

```
Odoo Record
    ↓
Server Action Button
    ↓
pulser.gitops.wizard
    ↓
POST /pulser/git-ops (HMAC signed)
    ↓
Webhook Controller
    ↓
GitHub App JWT → Installation Token
    ↓
repository_dispatch event
    ↓
GitHub Actions: git-ops workflow
    ↓
Git operations: branch/commit/push/PR
```

## Dependencies

- **Python**: PyJWT (for GitHub App authentication)
- **Odoo**: base, project, sale_management, account, hr_expense, purchase

## Security

- ✅ HMAC-SHA256 signature validation on webhook endpoint
- ✅ GitHub App Installation Tokens (auto-expire)
- ✅ Secrets stored in environment variables (never in code)
- ✅ HTTPS-only webhook endpoint
- ✅ Base64-encoded private key storage

## Troubleshooting

### "Missing PULSER_WEBHOOK_SECRET"
- Check environment variable is set in Odoo container
- Restart container after adding: `docker compose restart odoo`

### "token_exchange_failed"
- Verify GITHUB_APP_ID and GITHUB_INSTALLATION_ID are correct
- Check GITHUB_APP_PRIVATE_KEY_BASE64 is valid base64 encoding
- Test JWT generation: `python3 -c "import jwt; print('OK')"`

### "unauthorized" from webhook
- Verify X-Pulser-Secret matches PULSER_WEBHOOK_SECRET
- Check HMAC signature calculation
- Ensure Content-Type is application/json

### GitHub Actions workflow not triggering
- Verify repository_dispatch event type is "git-ops"
- Check workflow file: `.github/workflows/git-ops.yml` exists
- Ensure APP_ID variable and PRIVATE_KEY secret are set in GitHub

## License

LGPL-3

## Author

InsightPulse AI - https://github.com/jgtolentino/insightpulse-odoo

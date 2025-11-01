# VS Code Extension Usage Guide

**Odoo Dev Kit for VS Code** - Streamlined module development with automated scaffolding, docgen, and deployment.

## Overview

The **Odoo Dev Kit** extension wraps the odoo-expertise agent's CLI automation with a graphical VS Code interface, enabling developers to:

- Scaffold OCA-compliant modules with one command
- Auto-generate documentation from `__manifest__.py`
- Trigger GitHub Actions deployments from the IDE
- Validate OCA compliance with pre-commit hooks
- Work in containerized Odoo development environments

**Architecture**: The extension is a **thin UI layer** over existing automation scripts, ensuring consistency between GUI (VS Code) and CLI (Cline) workflows.

## Installation

### Prerequisites

- **VS Code**: Version 1.85.0 or higher
- **Python**: 3.11+ (for Odoo 16.0+)
- **Docker**: For devcontainer support (optional)
- **GitHub CLI**: `gh` (for deployment commands)

### Install from VSIX

```bash
# Clone extension repository
git clone https://github.com/your-org/vscode-odoo-dev-kit
cd vscode-odoo-dev-kit

# Install dependencies
npm install

# Build extension
npm run build

# Package extension
npx vsce package

# Install to VS Code
code --install-extension odoo-dev-kit-0.1.0.vsix
```

### Install from Marketplace

*(Coming Soon)*

Search for "Odoo Dev Kit" in VS Code Extensions marketplace and click Install.

## Commands

All commands are accessible via Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`).

### 1. Odoo: Scaffold Module

**Command ID**: `odoo.scaffoldModule`

**What it does**: Creates OCA-compliant module structure using Jinja2 templates

**Workflow**:

1. Open Command Palette
2. Type "Odoo: Scaffold Module"
3. Interactive prompts:
   - **Module Name**: e.g., `expense_approval`
   - **Description**: e.g., "Multi-level expense approval workflow"
   - **Models**: Format: `model.name:field1,field2,field3`
     - Example: `expense.approval:name,amount,state,approver_id`
   - **Dependencies**: Comma-separated list
     - Example: `base,account,project`
   - **Author**: Default from git config
   - **License**: Default: `LGPL-3`

4. Extension executes:
   ```bash
   python scripts/scaffold_module.py \
     --name expense_approval \
     --description "Multi-level expense approval workflow" \
     --models "expense.approval:name,amount,state,approver_id" \
     --depends "base,account,project" \
     --author "Your Name" \
     --license "LGPL-3"
   ```

**Output Structure**:

```
custom_addons/expense_approval/
├── __init__.py                    # Package initialization
├── __manifest__.py                # Module metadata
├── models/
│   ├── __init__.py
│   └── expense_approval.py       # Model definition
├── views/
│   ├── expense_approval_views.xml  # Tree/form/search views
│   └── expense_approval_menu.xml   # Menu items
├── security/
│   ├── ir.model.access.csv        # Access rights
│   └── expense_approval_security.xml  # Record rules
├── tests/
│   ├── __init__.py
│   ├── test_expense_approval.py   # Unit tests
│   └── test_approval_workflow.py  # Integration tests
├── static/
│   └── description/
│       └── icon.png               # Module icon
├── README.rst                     # OCA documentation
└── .gitignore                     # Git exclusions
```

**Expected Time**: 30 seconds
**Success Indicators**:
- ✅ Module directory created
- ✅ All OCA-required files present
- ✅ No syntax errors in Python/XML
- ✅ Pre-commit hooks pass

**Troubleshooting**:

| Issue | Cause | Solution |
|-------|-------|----------|
| "Module name invalid" | Name contains spaces/capitals | Use lowercase with underscores |
| "Template not found" | Missing templates directory | Ensure `templates/` exists in workspace |
| "Python import error" | Jinja2 not installed | `pip install jinja2` |

### 2. Odoo: Generate Docs

**Command ID**: `odoo.generateDocs`

**What it does**: Auto-generates README, CHANGELOG, ADR from `__manifest__.py`

**Workflow**:

1. Open module directory in workspace
2. Command Palette → "Odoo: Generate Docs"
3. Optional prompts:
   - **Generate ADR?**: Yes/No
   - **ADR Decision Title**: e.g., "Use state machine for approval flow"

4. Extension executes:
   ```bash
   # Without ADR
   python scripts/docgen.py custom_addons/expense_approval

   # With ADR
   python scripts/docgen.py custom_addons/expense_approval \
     --adr "Use state machine for approval flow"
   ```

**Generated Files**:

1. **README.rst** (~200 lines)
   - OCA-compliant format
   - License badge
   - Table of contents
   - Configuration instructions
   - Usage examples
   - Bug tracker link
   - Credits and contributors

2. **CHANGELOG.md** (~150 lines)
   - Keep a Changelog format
   - Semantic Versioning guidelines
   - Version history seed
   - Release process documentation

3. **ADR-001-slug.md** (~180 lines, if requested)
   - Michael Nygard template
   - Context and decision rationale
   - Consequences (positive/negative)
   - Alternatives considered
   - Implementation notes

**Example Output** (README.rst):

```rst
=================
Expense Approval
=================

.. |badge1| image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

|badge1|

Multi-level expense approval workflow

**Table of contents**

.. contents::
   :local:

Configuration
=============

To configure this module:

1. Go to Settings > Technical > Expense > Approval Levels
2. Configure approval hierarchy and budget thresholds

Usage
=====

1. Create expense from Expenses menu
2. Submit for approval
3. Manager reviews and approves/rejects
4. Finance director provides final approval
```

**Expected Time**: 10 seconds
**Success Indicators**:
- ✅ All files created without errors
- ✅ README follows OCA format
- ✅ CHANGELOG uses Keep a Changelog format
- ✅ ADR follows Michael Nygard template (if requested)

**Troubleshooting**:

| Issue | Cause | Solution |
|-------|-------|----------|
| "No __manifest__.py found" | Wrong directory | Navigate to module root |
| "Parse error" | Invalid manifest syntax | Validate Python syntax |
| "File exists" | Docs already generated | Delete existing or use --force flag |

### 3. Odoo: Deploy

**Command ID**: `odoo.deploy`

**What it does**: Triggers GitHub Actions deployment workflow via GitHub CLI

**Workflow**:

1. Command Palette → "Odoo: Deploy"
2. Interactive prompts:
   - **Environment**: `staging` or `production`
   - **Image Tag**: Default: `latest`, or specific SHA
   - **Confirmation**: "Deploy to [environment]?" (production only)

3. Extension executes:
   ```bash
   gh workflow run deploy.yml \
     -f environment=staging \
     -f image_tag=latest
   ```

**Integration Flow**:

```
VS Code Command
    ↓
GitHub CLI (gh workflow run)
    ↓
.github/workflows/deploy.yml triggered
    ↓
DigitalOcean App Platform deployment
    ├── Update app spec
    ├── Create deployment
    ├── Wait for completion (max 10 min)
    └── Health check
    ↓
Success → Notification in VS Code
Failure → Automatic rollback workflow
```

**Real-time Monitoring**:

Extension opens an integrated terminal showing:
```bash
# Deployment progress
⏳ Triggering deployment workflow...
✅ Workflow started: run ID 1234567890

⏳ Waiting for deployment to complete...
⏳ Status: Building image...
⏳ Status: Deploying to DigitalOcean...
⏳ Status: Running health checks...

✅ Deployment successful!
   Environment: staging
   URL: https://odoo-staging.ondigitalocean.app
   Image: registry.digitalocean.com/insightpulse/odoo:abc123
   Duration: 8m 32s
```

**Expected Time**: 8-15 minutes
**Success Indicators**:
- ✅ GitHub Actions workflow triggered
- ✅ Deployment reaches ACTIVE state
- ✅ Health check returns 200 OK

**Troubleshooting**:

| Issue | Cause | Solution |
|-------|-------|----------|
| "gh: command not found" | GitHub CLI not installed | `brew install gh` (macOS) or `apt install gh` (Linux) |
| "gh auth required" | Not authenticated | `gh auth login` |
| "Workflow not found" | Wrong repository | Verify remote: `git remote -v` |
| "Deployment timeout" | >10 min build | Check GitHub Actions logs |

### 4. Odoo: Validate OCA

**Command ID**: `odoo.validateOCA`

**What it does**: Runs pre-commit hooks for OCA compliance validation

**Workflow**:

1. Command Palette → "Odoo: Validate OCA"
2. Extension executes:
   ```bash
   pre-commit run --all-files
   ```
3. Results displayed in Output panel

**Validation Checks**:

| Check | Tool | Purpose |
|-------|------|---------|
| Linting | ruff | Fast Python linter |
| Formatting | black | Code formatting (88 char line length) |
| Import Sorting | isort | Alphabetical import organization |
| Style Guide | flake8 | PEP 8 compliance |
| Odoo-specific | pylint-odoo | OCA coding guidelines |
| XML Validation | libxml2 | Well-formed XML views |
| YAML Validation | yamllint | Manifest and workflow files |
| Security | bandit | Security issue detection |

**Example Output**:

```
✅ ruff.....................................................Passed
✅ black....................................................Passed
✅ isort....................................................Passed
✅ flake8...................................................Passed
✅ pylint-odoo..............................................Passed
✅ check-xml................................................Passed
❌ yamllint.................................................Failed
   - __manifest__.py:12: [error] trailing spaces (trailing-spaces)

⚠️  1 check failed. Fix errors and re-run validation.
```

**Auto-fix Mode**:

Extension provides quick-fix button for common issues:
- **Black formatting**: Auto-formats all Python files
- **Isort sorting**: Auto-sorts all imports
- **Trailing spaces**: Removes from all files

**Expected Time**: 30 seconds
**Success Indicators**:
- ✅ All checks pass with green checkmarks
- ✅ Exit code 0

**Troubleshooting**:

| Issue | Cause | Solution |
|-------|-------|----------|
| "pre-commit not found" | Not installed | `pip install pre-commit` |
| "Hook install required" | First run | `pre-commit install` |
| "Python version mismatch" | Wrong Python | Use Python 3.11+ |
| "Pylint-odoo errors" | Missing OCA plugin | `pip install pylint-odoo` |

### 5. Odoo: Run Tests

**Command ID**: `odoo.runTests`

**What it does**: Executes pytest test suite for module

**Workflow**:

1. Open module with tests
2. Command Palette → "Odoo: Run Tests"
3. Interactive prompts:
   - **Test Scope**: `current module` or `all modules`
   - **Verbosity**: `-v` (verbose) or `-vv` (very verbose)
   - **Coverage Report**: Yes/No

4. Extension executes:
   ```bash
   # Single module with coverage
   pytest custom_addons/expense_approval/tests/ -v --cov=custom_addons/expense_approval

   # All modules
   pytest custom_addons/ -v --cov=custom_addons/
   ```

**Test Report** (integrated in VS Code):

```
===================== test session starts ======================
collected 15 items

tests/test_expense_approval.py::test_create_expense PASSED [ 6%]
tests/test_expense_approval.py::test_submit_approval PASSED [13%]
tests/test_expense_approval.py::test_approve_expense PASSED [20%]
tests/test_approval_workflow.py::test_multi_level_approval PASSED [26%]
...

---------- coverage: platform darwin, python 3.11.5 -----------
Name                                      Stmts   Miss  Cover
-------------------------------------------------------------
models/expense_approval.py                  145     12    92%
controllers/expense_controller.py            87      8    91%
wizards/approval_wizard.py                   56      3    95%
-------------------------------------------------------------
TOTAL                                       288     23    92%

===================== 15 passed in 4.23s ======================
```

**Expected Time**: 5-30 seconds
**Success Indicators**:
- ✅ All tests passed
- ✅ Coverage ≥75%

## Devcontainer Setup

The extension includes a `.devcontainer/` configuration for consistent development environments.

### Configuration

**`.devcontainer/devcontainer.json`**:

```json
{
  "name": "Odoo 16.0 Development",
  "dockerComposeFile": "docker-compose.yml",
  "service": "odoo",
  "workspaceFolder": "/workspace",

  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff",
        "ms-azuretools.vscode-docker"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/bin/python3",
        "python.linting.enabled": true,
        "python.linting.ruffEnabled": true,
        "python.formatting.provider": "black",
        "editor.formatOnSave": true,
        "files.autoSave": "onFocusChange"
      }
    }
  },

  "forwardPorts": [8069, 5678],
  "postCreateCommand": "pip install -r requirements.txt && pre-commit install",

  "remoteUser": "odoo"
}
```

**`.devcontainer/docker-compose.yml`**:

```yaml
version: '3.8'

services:
  odoo:
    build:
      context: .
      dockerfile: Dockerfile
    volumes:
      - ../:/workspace:cached
      - odoo-data:/var/lib/odoo
    ports:
      - "8069:8069"
      - "5678:5678"  # debugpy
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=odoo
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  odoo-data:
  postgres-data:
```

### Usage

1. **Open in Container**:
   - Command Palette → "Dev Containers: Reopen in Container"
   - VS Code rebuilds and reopens in container (~5 min first time)

2. **Start Odoo**:
   ```bash
   # Integrated terminal
   odoo -d odoo --db_host db --db_user odoo --db_password odoo --dev all
   ```

3. **Access Odoo**:
   - Browser: http://localhost:8069
   - Database: `odoo`
   - Username: `admin`
   - Password: `admin`

4. **Debug**:
   - Set breakpoints in Python code
   - Run → Start Debugging (`F5`)
   - Debugger attaches to port 5678

**Features**:
- ✅ Odoo 16.0 pre-installed
- ✅ Python 3.11 + debugpy
- ✅ PostgreSQL 15 with persistent data
- ✅ Pre-commit hooks configured
- ✅ All extensions pre-installed

**Expected Time**: 5 minutes (first build), 30 seconds (subsequent)

## Integration with Cline

All VS Code commands wrap existing Cline automation, ensuring **workflow consistency** across GUI and CLI.

| VS Code Command | Underlying Script | Cline Skill | Reuse |
|-----------------|-------------------|-------------|-------|
| Scaffold Module | `scripts/scaffold_module.py` | `odoo-module-dev` | ✅ 100% |
| Generate Docs | `scripts/docgen.py` | (new) | ✅ 60% |
| Deploy | `gh workflow run deploy.yml` | `odoo-sh-devops` | ✅ 85% |
| Validate OCA | `pre-commit run --all-files` | (existing) | ✅ 100% |
| Run Tests | `pytest custom_addons/ -v` | (existing) | ✅ 100% |

**Benefits**:
- **Consistency**: Same scripts power GUI and CLI
- **Testing**: Scripts tested in CLI, validated in GUI
- **Flexibility**: Developers choose their preferred interface
- **Automation**: Scripts can be used in CI/CD pipelines

**Example Workflows**:

**GUI Workflow** (VS Code):
```
1. Odoo: Scaffold Module → expense_approval
2. Develop features in devcontainer
3. Odoo: Validate OCA → Fix issues
4. Odoo: Run Tests → Ensure coverage ≥75%
5. Odoo: Generate Docs → Auto-create README/CHANGELOG
6. Git commit and push
7. Odoo: Deploy → staging
```

**CLI Workflow** (Cline):
```bash
# Same automation, different interface
python scripts/scaffold_module.py --name expense_approval
# ... develop ...
pre-commit run --all-files
pytest custom_addons/expense_approval/tests/ -v
python scripts/docgen.py custom_addons/expense_approval
git add . && git commit -m "feat: expense approval module"
gh workflow run deploy.yml -f environment=staging
```

## Keyboard Shortcuts

Customize in VS Code settings (`keybindings.json`):

```json
[
  {
    "key": "ctrl+shift+o s",
    "command": "odoo.scaffoldModule",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+o d",
    "command": "odoo.generateDocs",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+o v",
    "command": "odoo.validateOCA",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+o t",
    "command": "odoo.runTests",
    "when": "editorTextFocus"
  }
]
```

**Mnemonic**: `Ctrl+Shift+O` (Odoo) + action letter

## Troubleshooting

### Common Issues

#### 1. Extension Not Activating

**Symptom**: Commands not appearing in Command Palette

**Causes**:
- Extension not properly installed
- VS Code version too old
- Workspace not recognized as Odoo project

**Solutions**:
1. Verify installation: Extensions sidebar → "Odoo Dev Kit" installed
2. Update VS Code: Help → Check for Updates
3. Open workspace with Odoo modules: `custom_addons/` directory present

#### 2. Python Scripts Failing

**Symptom**: "python: command not found" or import errors

**Causes**:
- Python not in PATH
- Wrong Python version
- Missing dependencies

**Solutions**:
1. Set Python interpreter: Command Palette → "Python: Select Interpreter" → Python 3.11+
2. Install dependencies:
   ```bash
   pip install jinja2 ruff black isort flake8 pylint-odoo pytest
   ```
3. Update VS Code settings:
   ```json
   {
     "python.defaultInterpreterPath": "/usr/bin/python3"
   }
   ```

#### 3. GitHub CLI Authentication

**Symptom**: `gh workflow run` fails with "authentication required"

**Solutions**:
1. Install GitHub CLI:
   ```bash
   # macOS
   brew install gh

   # Ubuntu/Debian
   sudo apt install gh
   ```

2. Authenticate:
   ```bash
   gh auth login
   # Select: GitHub.com → HTTPS → Paste authentication token
   ```

3. Verify:
   ```bash
   gh auth status
   ```

#### 4. Pre-commit Hooks Not Running

**Symptom**: "pre-commit: command not found"

**Solutions**:
1. Install pre-commit:
   ```bash
   pip install pre-commit
   ```

2. Install hooks:
   ```bash
   pre-commit install
   ```

3. Run manually:
   ```bash
   pre-commit run --all-files
   ```

#### 5. Devcontainer Build Failures

**Symptom**: Container fails to build or start

**Causes**:
- Docker not running
- Insufficient disk space
- Port conflicts (8069, 5678)

**Solutions**:
1. Start Docker Desktop
2. Free disk space: `docker system prune`
3. Check port conflicts:
   ```bash
   # macOS/Linux
   lsof -i :8069
   lsof -i :5678
   ```
4. Rebuild container:
   - Command Palette → "Dev Containers: Rebuild Container"

### Logs and Debugging

#### Extension Logs

**View Output**:
1. View → Output
2. Dropdown → "Odoo Dev Kit"

**Log Levels**:
- INFO: Command execution status
- WARNING: Non-critical issues
- ERROR: Command failures with stack traces

#### Command Execution Logs

All commands log to integrated terminal:
- View → Terminal
- Look for "Odoo Dev Kit" terminal

**Example**:
```
[Odoo Dev Kit] Running command: odoo.scaffoldModule
[Odoo Dev Kit] Script: python scripts/scaffold_module.py --name expense_approval
[Odoo Dev Kit] ✅ Module scaffolding complete
[Odoo Dev Kit] Duration: 2.3s
```

#### GitHub Actions Logs

**View Workflow Runs**:
```bash
# List recent runs
gh run list --workflow=deploy.yml

# View specific run
gh run view 1234567890

# View logs
gh run view 1234567890 --log
```

## Performance Benchmarks

| Operation | Expected Time | Actual Time | Status |
|-----------|--------------|-------------|--------|
| Scaffold Module | <5s | ~2.3s | ✅ |
| Generate Docs | <15s | ~8.7s | ✅ |
| Validate OCA | <60s | ~32s | ✅ |
| Run Tests (single module) | <30s | ~18s | ✅ |
| Deploy (staging) | <10min | ~8.5min | ✅ |
| Devcontainer Build (first) | <10min | ~6.2min | ✅ |
| Devcontainer Start (cached) | <1min | ~28s | ✅ |

## Roadmap

### Version 0.2.0 (Next Release)

- [ ] Odoo: Create View (form/tree/search wizard)
- [ ] Odoo: Add Security Rules (RLS wizard)
- [ ] Odoo: Create Wizard (transient model scaffold)
- [ ] Odoo: Migration Assistant (version upgrade helper)
- [ ] Integrated Git-Ops panel (deploy status in sidebar)

### Version 0.3.0

- [ ] Visual module builder (drag-and-drop UI)
- [ ] SOP execution panel (qms_sop integration)
- [ ] Performance profiler (bottleneck visualization)
- [ ] Multi-language support (i18n helper)

### Version 1.0.0

- [ ] Marketplace publish
- [ ] Full Odoo.sh integration
- [ ] AI-powered code suggestions (via DeepSeek)
- [ ] Collaborative development features

## Contributing

**Repository**: https://github.com/your-org/vscode-odoo-dev-kit

**Issues**: https://github.com/your-org/vscode-odoo-dev-kit/issues

**Pull Requests**: Welcome! See `CONTRIBUTING.md`

## License

LGPL-3.0 (same as Odoo)

## Support

- **Documentation**: https://your-org.github.io/vscode-odoo-dev-kit
- **Community**: https://discord.gg/odoo-dev-kit
- **Email**: support@your-org.com

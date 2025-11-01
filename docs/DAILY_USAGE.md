# Daily Usage Guide – Odoo Agent Expertise

**Purpose**: Practical workflows for daily Odoo development using Cline + DeepSeek + Claude Code

**Last Updated**: 2025-11-01

---

## Morning Startup Routine

### 1. Environment Check (2 minutes)

```bash
# Verify API keys and services
echo "DeepSeek: ${DEEPSEEK_API_KEY:+✅}" || echo "❌ DEEPSEEK_API_KEY missing"
echo "GitHub: ${GITHUB_TOKEN:+✅}" || echo "❌ GITHUB_TOKEN missing"
echo "DO: ${DO_ACCESS_TOKEN:+✅}" || echo "❌ DO_ACCESS_TOKEN missing"

# Check Cline config
cat ~/.cline/config.yaml | grep -A 5 "odoo_expertise"

# Verify skill symlinks
ls -la ~/.cline/skills/odoo-expertise/ | grep -E "(odoo-module-dev|odoo-studio-ops|odoo-sh-devops|odoo-docker-claude)"

# Quick health check
which python3 pre-commit docker doctl psql
```

**Expected Output**: All ✅ checkmarks, 4 skills visible, all CLIs present

### 2. Update Knowledge Base (5 minutes)

```bash
# Pull latest OCA patterns
cd ~/ai-agency/agents/odoo-expertise/knowledge/scripts
python3 auto_research.py --domain oca --query "latest patterns" --limit 5

# Check for updates in key repos
python3 auto_research.py --domain oca --repo "OCA/maintainer-tools" --since 7days

# Review yesterday's citations
cd ../notes
cat $(date -v-1d +%Y-%m-%d).md 2>/dev/null || echo "No citations from yesterday"
```

**When to skip**: If you're repeating a known workflow (e.g., generating similar modules)

### 3. Review Active Tasks (3 minutes)

```bash
# Check sprint tasks
cd ~/ai-agency/agents/odoo-expertise
cat spec/tasks/TASKS.yaml | grep -A 3 "status: in_progress"

# Review eval status
cd evals
cat RESULTS.md | grep "Sprint 3" -A 10

# Check for stuck tasks
psql "$POSTGRES_URL" -c "SELECT * FROM task_queue WHERE status='processing' AND created_at < now() - interval '5 minutes';"
```

---

## Common Workflows

### Workflow 1: Create New OCA Module (10 minutes)

**Scenario**: Generate a new OCA-compliant module from scratch

```bash
# Step 1: Research existing patterns
cline-odoo "Research OCA patterns for task priority management with color fields"

# Expected: 3-5 citations from OCA repos, Stack Overflow, Reddit
# Review output and note key patterns

# Step 2: Generate module scaffolding
cline-odoo "Create OCA module named 'task_priority' with:
- Model: task.priority
- Fields: name (Char, required), level (Integer), color (Char)
- Security: Manager can create/write, User can read
- Tests: TestTaskPriority with CRUD assertions
- README with usage examples"

# Expected: Complete module in custom_addons/task_priority/
# - __manifest__.py with proper version (16.0.1.0.0)
# - models/task_priority.py with ORM patterns
# - security/ir.model.access.csv
# - tests/test_task_priority.py
# - README.rst

# Step 3: Validate OCA compliance
cd custom_addons/task_priority
pre-commit run --all-files

# Step 4: Run tests
pytest tests/test_task_priority.py -v

# Step 5: Document in knowledge base
echo "## Task Priority Module
- Pattern: Simple color-coded priority system
- Takeaway: Use Integer for sorting, Char for color hex codes
- Application: odoo-module-dev
- Date: $(date +%Y-%m-%d)
" >> ~/ai-agency/agents/odoo-expertise/knowledge/notes/$(date +%Y-%m-%d).md
```

**Model Used**: DeepSeek v3.1 (auto-detects from "Create module")

**Cost**: ~$0.0001 per generation

### Workflow 2: Add Computed Field to Existing Module (15 minutes)

**Scenario**: Add a computed field with proper @api.depends and store=True

```bash
# Step 1: Review ORM library patterns
cd ~/ai-agency/agents/odoo-expertise
cat knowledge/patterns/orm_library.md | grep -A 30 "@api.depends"

# Step 2: Implement computed field
cline-odoo "Add computed field to custom_addons/expense_approval/models/expense_approval_request.py:
- Field name: total_with_tax
- Type: Float
- Compute method: _compute_total_with_tax
- Dependencies: amount, tax_rate
- Store: True for performance
- Include inverse function for editable field
- Add test in tests/test_expense_approval.py"

# Expected: Updated model with:
# - @api.depends('amount', 'tax_rate')
# - def _compute_total_with_tax(self)
# - Proper store=True and inverse function
# - New test method test_total_with_tax_computation

# Step 3: Test locally
cd custom_addons/expense_approval
pytest tests/test_expense_approval.py::TestExpenseApproval::test_total_with_tax_computation -v

# Step 4: Check for N+1 queries
cline-odoo "Review expense_approval_request.py for potential N+1 query issues in computed fields"

# Step 5: Update changelog
echo "- Added total_with_tax computed field with @api.depends pattern" >> __manifest__.py
```

**Model Used**: DeepSeek v3.1 (standard ORM operations)

**Cost**: ~$0.00005

### Workflow 3: Deploy to Odoo.sh (20 minutes)

**Scenario**: Push module to Odoo.sh staging, validate, promote to production

```bash
# Step 1: Create deployment plan
cline-odoo "Using DeepSeek R1 reasoning, create comprehensive Odoo.sh deployment plan for task_priority module:
- Pre-deployment checklist
- Staging validation gates (5 required)
- Production deployment steps
- Rollback procedures"

# Expected: Detailed runbook with:
# - Branch strategy (dev → staging → production)
# - Database migration checks
# - Dependency validation
# - Smoke test procedures
# - Zero-downtime deployment steps

# Step 2: Push to staging branch
git checkout -b staging/task-priority
git add custom_addons/task_priority
git commit -m "feat(task_priority): Add priority management module

- OCA-compliant scaffolding
- Color-coded priority levels
- Tests with ≥80% coverage

🤖 Generated with Cline + DeepSeek v3.1"
git push origin staging/task-priority

# Step 3: Monitor Odoo.sh build
# (Open Odoo.sh web interface or use CLI if available)
# Wait for build completion (~3-5 minutes)

# Step 4: Validate on staging
cline-odoo "Generate validation checklist for task_priority module on staging:
- UI smoke tests
- Database integrity checks
- Permission validation
- Performance checks"

# Step 5: Promote to production (if staging passes)
git checkout production
git merge staging/task-priority
git push origin production

# Step 6: Monitor production deployment
# Watch logs for 10 minutes post-deployment
# Check error rates, performance metrics
```

**Model Used**: DeepSeek R1 (deployment planning requires reasoning)

**Cost**: ~$0.001 (reasoning tokens)

### Workflow 4: Run Eval Scenarios Locally (10 minutes)

**Scenario**: Validate changes against eval suite before pushing

```bash
# Step 1: Run specific scenario
cd ~/ai-agency/agents/odoo-expertise/evals
bash scripts/01_oca_scaffolding.sh

# Expected output:
# ✅ Module scaffold generated
# ✅ Manifest version format correct (16.0.1.0.0)
# ✅ Security rules present
# ✅ Tests executable
# ✅ Pre-commit hooks pass

# Step 2: Run all Sprint 2 scenarios
bash scripts/run_all_scenarios.sh

# Expected: ≥90% pass rate (8/10 scenarios)

# Step 3: If failures occur, analyze
cline-odoo "Analyze eval failure in scenario 04_orm_compliance:
- Show failed test output
- Identify root cause
- Suggest fix following OCA patterns"

# Step 4: Fix and re-run
# (Apply suggested fix)
bash scripts/04_orm_compliance.sh

# Step 5: Update knowledge base if new pattern discovered
echo "## Eval Failure Resolution
- Scenario: 04_orm_compliance
- Issue: N+1 query in computed field
- Fix: Added read_group with limit parameter
- Date: $(date +%Y-%m-%d)
" >> ~/ai-agency/agents/odoo-expertise/knowledge/notes/$(date +%Y-%m-%d).md
```

**Model Used**: DeepSeek v3.1 (analysis) + Claude Code (if complex refactor needed)

**Cost**: ~$0.0002

---

## Note-Taking Workflow

### Daily Citation Capture (10 minutes per day)

**Purpose**: Build knowledge base organically from daily discoveries

```bash
# Create today's note file
cd ~/ai-agency/agents/odoo-expertise/knowledge/notes
touch $(date +%Y-%m-%d).md

# Template structure
cat > $(date +%Y-%m-%d).md <<'EOF'
# Daily Citations – $(date +%Y-%m-%d)

## OCA Guidelines
<!-- Patterns from OCA repos, maintainer notes -->

## Odoo Official Docs
<!-- API changes, new features, best practices -->

## Community Wisdom
<!-- Reddit r/odoo, Stack Overflow, forums -->

## Docker/Infrastructure
<!-- Deployment patterns, Docker optimization -->

## ORM Patterns
<!-- Field types, decorators, performance -->

EOF
```

**When to Add Citations**:
1. **After Research**: Immediately after `cline-odoo "Research..."`
2. **After Problem Solving**: Document solution for future reference
3. **After Eval Failure**: Capture lesson learned
4. **During Code Review**: Note interesting patterns in OCA modules

**Citation Format** (from `knowledge/notes/citation_template.md`):
```markdown
## [Pattern/Issue Name]
- **Link**: [URL to source]
- **Takeaway**: One-line actionable summary
- **Application**: [Which skill: odoo-module-dev, odoo-studio-ops, etc.]
- **Quality Score**: [60-100, optional]
- **Date Added**: YYYY-MM-DD
```

**Example Daily Citation**:
```markdown
## @api.depends with Related Fields
- **Link**: https://github.com/OCA/account-financial-tools/blob/16.0/account_move_line_tax_editable/models/account_move_line.py#L45
- **Takeaway**: When depending on related fields, use 'field_id.related_field' format, not just 'field_id'
- **Application**: odoo-module-dev
- **Quality Score**: 90
- **Date Added**: 2025-11-01
```

### Weekly Knowledge Base Review (30 minutes, Fridays)

```bash
# Step 1: Review week's citations
cd ~/ai-agency/agents/odoo-expertise/knowledge/notes
cat $(date -v-7d +%Y-%m-%d).md $(date -v-6d +%Y-%m-%d).md ... $(date +%Y-%m-%d).md

# Step 2: Identify high-impact patterns
grep -h "Quality Score: [89][0-9]" *.md

# Step 3: Promote to ORM library if applicable
cline-odoo "Review this week's citations and identify patterns that should be added to knowledge/patterns/orm_library.md"

# Step 4: Update sources catalog
# Edit knowledge/refs/sources.yaml with new high-quality sources

# Step 5: Run automated research for gap-filling
python3 ~/ai-agency/agents/odoo-expertise/knowledge/scripts/auto_research.py --domain all --weekly-summary
```

---

## Model Routing Decisions

### Decision Matrix

| Task Characteristics | Recommended Model | Reasoning |
|---------------------|-------------------|-----------|
| Single module generation | DeepSeek v3.1 | Tool calls, JSON, straightforward |
| Multiple related modules | DeepSeek v3.1 | Batch operations, context reuse |
| Deployment strategy planning | DeepSeek R1 | Requires reasoning, risk assessment |
| Complex git operations (>5 files) | Claude Code | Repo-wide awareness, git tooling |
| Architecture redesign | DeepSeek R1 → Claude Code | Start with R1 planning, escalate if needed |
| Debugging N+1 queries | DeepSeek v3.1 | Pattern matching, known solutions |
| Creating deployment runbooks | DeepSeek R1 | Systematic thinking, edge cases |
| Refactoring across modules | Claude Code | Multi-file coordination |

### Manual Model Selection

**Force DeepSeek R1**:
```bash
cline-odoo "Using DeepSeek R1 reasoning, analyze trade-offs between..."
```

**Switch to Claude Code**:
1. Open Cline UI
2. Click provider dropdown (top right)
3. Select "Claude Code"
4. Continue conversation

**When to Escalate**:
- DeepSeek v3.1 fails after 2 attempts
- Need to refactor >10 files simultaneously
- Complex shell scripting or git operations
- Infrastructure as code (Terraform, Ansible)

### Cost Monitoring Per Model

```bash
# Check DeepSeek usage (daily)
curl https://api.deepseek.com/v1/usage \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" \
  | jq '.data.total_usage'

# Expected output:
# {
#   "total_tokens": 150000,  # ~$0.15 at $1/1M tokens
#   "total_cost": 0.15,
#   "period": "2025-11-01"
# }

# Set spending alert (add to crontab)
echo "0 8 * * * ~/ai-agency/agents/odoo-expertise/scripts/check_api_costs.sh" | crontab -
```

---

## Troubleshooting Common Errors

### Error 1: "Module not found" after generation

**Symptom**: Cline generated module but Odoo can't find it

**Solution**:
```bash
# Check module path
ls -la custom_addons/your_module/__manifest__.py

# Verify Odoo addons path
grep addons_path ~/infra/odoo/odoo.conf

# Restart Odoo
docker-compose restart odoo

# Update app list in Odoo UI
# Settings → Apps → Update Apps List
```

### Error 2: "@api.depends not triggering recomputation"

**Symptom**: Computed field not updating when dependency changes

**Solution**:
```bash
# Check dependency field names match exactly
cline-odoo "Review dependencies in _compute_method and verify field name spelling matches model definition"

# Common mistakes:
# ❌ @api.depends('related_field')  # If field is 'related_field_id'
# ✅ @api.depends('related_field_id')

# ❌ @api.depends('line_ids')  # If you need line field values
# ✅ @api.depends('line_ids.amount')  # Specific field in related model
```

### Error 3: "Pre-commit hooks failing"

**Symptom**: `pre-commit run` exits with errors

**Solution**:
```bash
# Install missing tools
pip install black isort flake8 pylint-odoo

# Run auto-fix
pre-commit run --all-files

# Manual fixes for pylint-odoo
pylint --load-plugins=pylint_odoo -d all -e odoolint custom_addons/your_module/ | grep "E[0-9]"

# Common issues:
# - Missing docstrings: Add """ """ to classes/methods
# - Import order: Run `isort .`
# - Line length: Run `black .`
```

### Error 4: "Research automation returning no results"

**Symptom**: `auto_research.py` finds 0 citations

**Solution**:
```bash
# Test API connectivity
python3 -c "import requests; print(requests.get('https://api.github.com').status_code)"
# Should print: 200

# Check API keys
echo "GitHub token: ${GITHUB_TOKEN:0:10}..."
echo "Reddit client: ${REDDIT_CLIENT_ID:+SET}"

# Run with verbose logging
python3 auto_research.py --domain oca --query "test query" --verbose --debug

# If still failing, check rate limits
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit
```

### Error 5: "Eval scenario timeout"

**Symptom**: Scenario script hangs or times out

**Solution**:
```bash
# Increase timeout in script
export EVAL_TIMEOUT=300  # 5 minutes

# Run with debug mode
bash -x evals/scripts/01_oca_scaffolding.sh

# Check for blocking operations
ps aux | grep -E "(python|odoo|docker)"

# Kill stuck processes
pkill -f "pytest.*test_module"

# Clean and retry
rm -rf custom_addons/test_module_*
bash evals/scripts/01_oca_scaffolding.sh
```

---

## PRD Integration Workflows

### Workflow 5: Create Module with VS Code (5 minutes)

**Scenario**: Generate OCA module using VS Code extension with automated documentation

```bash
# Step 1: Open Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
# Type: "Odoo: Scaffold Module"

# Interactive prompts:
Module Name: expense_approval
Description: "Multi-level expense approval workflow"
Models: "expense.approval:name,amount,state,approver_id,notes"
Dependencies: "base,account,project"
Author: (auto-filled from git config)
License: LGPL-3

# Expected: Module created in custom_addons/expense_approval/
# - Complete OCA-compliant structure
# - All models, views, security files
# - Unit tests scaffolded
# - README.rst auto-generated

# Step 2: Validate OCA Compliance
# Command Palette → "Odoo: Validate OCA"
# Expected: Pre-commit runs all checks
# - ruff (linting) ✅
# - black (formatting) ✅
# - isort (import sorting) ✅
# - flake8 (style guide) ✅
# - pylint-odoo (OCA-specific) ✅

# Step 3: Generate Documentation
# Command Palette → "Odoo: Generate Docs"
# Optional: Enter ADR decision title (e.g., "Use state machine for approval flow")
# Expected: Documentation created
# - README.rst (OCA format, ~200 lines)
# - CHANGELOG.md (Keep a Changelog format, ~150 lines)
# - ADR-001-state-machine.md (if ADR requested, ~180 lines)

# Step 4: Develop Features
# Use devcontainer for consistent environment
# Command Palette → "Dev Containers: Reopen in Container"
# Expected: Container starts with Odoo 16.0 pre-installed (~30s after first build)

# Access Odoo:
# - Browser: http://localhost:8069
# - Database: odoo
# - Username: admin
# - Password: admin

# Step 5: Deploy to Staging
# Command Palette → "Odoo: Deploy"
# Select environment: staging
# Image tag: latest (or specific SHA)
# Expected: GitHub Actions triggered
# - CI workflow runs (~8 min)
# - Deployment to DigitalOcean (~8 min)
# - Health checks pass ✅
# - Total time: ~16 min
```

**Model Used**: DeepSeek v3.1 (scaffolding), GitHub Actions (deployment automation)
**Cost**: ~$0.0001 (scaffolding only, deployment is free via CI)
**Time Saved**: ~15 minutes vs manual module creation

### Workflow 6: Git-Ops Deployment via Odoo UI (10 minutes)

**Scenario**: Deploy module to production from Odoo Project task (non-technical user workflow)

```bash
# Step 1: Create Deployment Task in Odoo UI
# Navigate to: Project → Tasks → Create
Task fields:
  - Name: "Deploy expense_approval v1.0.0 to production"
  - Type: Deploy (custom task type)
  - Branch: main
  - Commit Message: "feat(expense): Add multi-level approval workflow"
  - Environment: production
  - Image Tag: 1.0.0
  - State: Ready for Review

# Step 2: Code Review Process
# Assign to technical lead for review
# Lead reviews:
  - Code changes in PR
  - Test coverage report (must be ≥75%)
  - OCA validation status (must be green)
  - Security scan results (no HIGH/CRITICAL vulnerabilities)

# Step 3: Approval
# Technical lead or project manager sets:
  - State: Approved

# Expected: Studio automation triggers immediately
# Studio Automated Action:
#   Model: project.task
#   Trigger: State changes to "Approved"
#   Condition: Type = "Deploy"
#   Action: Execute pulser_webhook.action_dispatch()

# Step 4: Git-Ops Dispatch
# pulser_webhook module:
  - Generates HMAC signature for security
  - Calls GitHub API: repository_dispatch
  - Event type: deploy
  - Client payload:
      branch: main
      commit_message: "feat(expense): Add multi-level approval workflow"
      task_id: 1234
      environment: production
      image_tag: 1.0.0
      initiated_by: "Project Manager Name"

# Step 5: GitHub Actions Execution
# .github/workflows/deploy.yml triggered by repository_dispatch
# Workflow steps:
  1. Checkout code ✅
  2. Update app spec with image tag ✅
  3. Apply app spec to DigitalOcean ✅
  4. Create deployment with force rebuild ✅
  5. Monitor deployment progress (max 10 min) ✅
  6. Run health check validation ✅
  7. Decision:
     - ✅ Health Check Pass → Update task state to "Deployed" → Notify stakeholders
     - ❌ Health Check Fail → Trigger rollback.yml → Update task to "Rolled Back" → Create incident issue

# Step 6: Post-Deployment Verification
# If successful:
  - Task state updated to: Deployed ✅
  - Deployment ID recorded in task
  - Deployed at timestamp: 2025-11-01T10:30:00Z
  - Notification sent to: Slack #deployments channel
  - Email notification: project-team@your-org.com

# If failed (automatic rollback):
  - Task state updated to: Rolled Back ⚠️
  - Previous deployment ID activated
  - Incident issue created: "[INCIDENT] Production deployment failed"
  - Notification sent to: Slack #incidents channel (urgent)
  - PagerDuty alert: On-call engineer notified
  - Health check confirms: Previous version is healthy ✅

# Step 7: Verify Production
# Manual verification by non-technical user:
  - Open production URL: https://odoo-prod.your-domain.com
  - Navigate to Expenses menu
  - Create test expense
  - Submit for approval
  - Verify approval workflow works as expected
  - Mark task as "Verified" in Odoo

# Rollback scenario example:
# If health check fails (e.g., database migration error):
  1. Health check endpoint returns 500 error ❌
  2. deploy.yml detects failure
  3. Triggers rollback.yml workflow automatically
  4. Gets previous deployment ID from DigitalOcean
  5. Creates deployment with previous ID
  6. Waits for rollback completion (~1.5 min)
  7. Verifies rollback health check ✅
  8. Updates task state to "Rolled Back"
  9. Creates GitHub issue with incident details
  10. Notifies on-call engineer via PagerDuty
```

**Model Used**: N/A (fully automated workflow, no LLM needed)
**Cost**: $0 (GitHub Actions free tier, DigitalOcean costs same regardless)
**Time Saved**: ~20 minutes vs manual deployment process
**Non-Technical Friendly**: ✅ Project managers can deploy without CLI access

**Benefits**:
- **Audit Trail**: Every deployment tracked in Odoo Project tasks
- **Access Control**: Only approved tasks trigger deployments
- **Automatic Rollback**: Health check failures trigger instant rollback
- **Incident Management**: Failed deployments auto-create GitHub issues
- **Notification**: Stakeholders informed via Slack/Email
- **Zero CLI Knowledge**: Non-technical users can deploy via Odoo UI

### Workflow 7: SOP-Guided Error Investigation (15 minutes)

**Scenario**: Production deployment failed, use qms_sop module to investigate

```bash
# Step 1: SOP Selection in Odoo
# Navigate to: Quality Management → SOPs → SOP Runs → Create
# Select SOP: SOP-TRIAGE-001 (Error Investigation Workflow)
# Click: "Start Execution"

# Expected: SOP run created with 6 steps

# Step 2: Execute Step 1 - Error Classification
# SOP Step 1 Instructions:
#   "Categorize error by type and assign severity"
#
# Action in terminal:
doctl apps logs $DO_APP_ID --type DEPLOY --tail 100 | grep -i "error"

# Example output:
# ERROR: Database connection timeout
# ERROR: Health check failed with status 500

# Classification:
#   - Category: DATABASE
#   - Severity: CRITICAL (production down)

# Mark step complete in Odoo:
#   - Actual Result: "Database connection timeout, severity: CRITICAL"
#   - State: Completed ✅

# Step 3: Execute Step 2 - Gather Evidence
# SOP Step 2 Instructions:
#   "Collect all relevant logs and metrics"
#
# Actions:
# a) Get deployment logs
doctl apps logs $DO_APP_ID --type DEPLOY --tail 500 > /tmp/deployment.log

# b) Get application logs
doctl apps logs $DO_APP_ID --type RUN --tail 1000 > /tmp/application.log

# c) Get database connection stats
psql "$POSTGRES_URL" -c "
  SELECT datname, numbackends, deadlocks
  FROM pg_stat_database
  WHERE datname = 'odoo';
" > /tmp/db-stats.txt

# d) Extract error patterns
grep -E "(ERROR|FATAL|Exception)" /tmp/application.log > /tmp/errors.txt

# Mark step complete in Odoo:
#   - Actual Result: "Logs collected: deployment.log (15KB), application.log (50KB), db-stats.txt (1KB)"
#   - Attach files to SOP run
#   - State: Completed ✅

# Step 4: Execute Step 3 - Root Cause Analysis (5 Whys)
# SOP Step 3 Instructions:
#   "Identify underlying cause using 5 Whys methodology"
#
# Analysis:
# Why 1: Why did deployment fail?
#   → Health check returned 500 error
#
# Why 2: Why did health check return 500?
#   → Database connection timed out
#
# Why 3: Why did connection timeout?
#   → Connection pool exhausted (20/20 connections in use)
#
# Why 4: Why was pool exhausted?
#   → Long-running queries not releasing connections
#
# Why 5: Why are queries not releasing connections?
#   → Missing connection cleanup in exception handlers

# ROOT CAUSE: Exception handling code doesn't close database connections

# Record in Odoo:
#   - Create qms.sop.run.error record:
#       Error Code: DB_CONNECTION_LEAK
#       Description: "Missing finally blocks in DB exception handlers"
#       Severity: HIGH
#   - Mark step complete:
#       Actual Result: "Root cause identified: DB_CONNECTION_LEAK"
#       State: Completed ✅

# Step 5: Execute Step 4 - Implement Fix
# SOP Step 4 Instructions:
#   "Apply corrective action to resolve error"
#
# Fix implementation:
# a) Create fix branch
git checkout -b fix/db-connection-leak

# b) Update code with connection cleanup
# Edit: custom_addons/expense_approval/models/expense_approval.py
# Add try/finally blocks to ensure connection cleanup

# c) Add regression test
# Edit: custom_addons/expense_approval/tests/test_connection_cleanup.py
def test_connection_cleanup_on_exception():
    """Ensure connections closed even when exceptions occur."""
    initial_count = get_connection_count()
    try:
        fetch_data_that_raises_exception()
    except Exception:
        pass
    time.sleep(1)  # Wait for cleanup
    assert get_connection_count() == initial_count

# d) Validate fix locally
pytest custom_addons/expense_approval/tests/test_connection_cleanup.py -v
# Expected: PASSED ✅

# e) Create PR
git add .
git commit -m "fix(expense): Add connection cleanup in exception handlers"
git push origin fix/db-connection-leak
gh pr create --title "Fix DB connection leak" --body "Closes incident #1234"

# f) Deploy fix to staging
gh workflow run deploy.yml -f environment=staging -f branch=fix/db-connection-leak

# g) Verify fix in staging
python scripts/health_check.py --url https://odoo-staging.your-domain.com
# Expected: ✅ Health check passed

# Mark step complete in Odoo:
#   - Actual Result: "Fix implemented in PR #456, verified in staging"
#   - State: Completed ✅

# Step 6: Execute Step 5 - Document Resolution
# SOP Step 5 Instructions:
#   "Record resolution for future reference"
#
# Documentation tasks:
# a) Update error code catalog
# Navigate in Odoo: Quality Management → Error Codes → Create
#   - Code: DB_CONNECTION_LEAK
#   - Severity: High
#   - Description: "Database connections not released in exception handlers"
#   - Resolution: "Ensure all DB operations use try/finally blocks"
#   - Related SOPs: SOP-TRIAGE-001

# b) Create post-mortem document
python scripts/create_postmortem.py \
  --title "Production deployment failure - DB connection leak" \
  --root-cause "Missing connection cleanup in exception handlers" \
  --fix "Added finally blocks to ensure cleanup" \
  --preventive "Add linting rule, connection pool monitoring"

# c) Update knowledge base
# Add to: knowledge/patterns/database_patterns.md
# Section: "Connection Management Best Practices"
# Content: "Always use try/finally for database operations..."

# d) Create GitHub issue for preventive measures
gh issue create \
  --title "[TECH-DEBT] Audit all DB operations for connection cleanup" \
  --body "Add linting rule to enforce try/finally blocks" \
  --label tech-debt,database,high-priority

# Mark step complete in Odoo:
#   - Actual Result: "Documentation complete: error code added, post-mortem created, knowledge base updated"
#   - State: Completed ✅

# Step 7: Execute Step 6 - Preventive Measures
# SOP Step 6 Instructions:
#   "Prevent recurrence through systemic improvements"
#
# Preventive actions:
# a) Add regression test (already done in Step 4)
# b) Add CI validation for connection cleanup
# Edit: .github/workflows/odoo-ci.yml
- name: Check DB connection cleanup
  run: |
    # Ensure all DB cursors have try/finally
    grep -r "cursor\(\)" custom_addons/ | while read line; do
      if ! grep -A 10 "$line" | grep -q "finally"; then
        echo "Missing finally block: $line"
        exit 1
      fi
    done

# c) Add monitoring alert for connection pool usage
# (Example: configure alert when connections > 80%)

# d) Enable Dependabot for automated dependency updates
# Create: .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"

# Mark step complete in Odoo:
#   - Actual Result: "Preventive measures implemented: CI validation, monitoring, Dependabot"
#   - State: Completed ✅

# Step 8: Complete SOP Run
# All steps completed → SOP run state: Completed ✅
# Total time: ~15 minutes (CRITICAL severity met <15 min SLA)
# Resolution time: 15 minutes to mitigation, 2 hours to root cause fix (including PR review)

# SOP run summary in Odoo:
#   - Start time: 2025-11-01T10:45:00Z
#   - End time: 2025-11-01T11:00:00Z
#   - Duration: 15 minutes
#   - Error code: DB_CONNECTION_LEAK
#   - Root cause: Missing connection cleanup
#   - Resolution: Try/finally blocks added
#   - Preventive measures: 3 actions completed
#   - All steps: 6/6 completed ✅
```

**Model Used**: N/A (SOP-guided manual investigation, no LLM needed)
**Cost**: $0 (uses existing tools and logs)
**Time Saved**: ~30 minutes vs unstructured debugging
**SLA Compliance**: ✅ CRITICAL severity resolved in <15 minutes

**Benefits**:
- **Structured Approach**: SOP ensures no steps are missed
- **Knowledge Capture**: All investigations tracked in qms_sop module
- **Error Catalog**: Build library of known issues and resolutions
- **Compliance**: Audit trail for incident response
- **Training**: New team members follow proven procedures
- **Continuous Improvement**: Preventive measures prevent recurrence

---

## Performance Tips

### Speed Up Module Generation

1. **Use cached patterns**: Reference `knowledge/patterns/orm_library.md` in prompts
2. **Batch requests**: Generate multiple related modules in one request
3. **Skip research**: If pattern is known, skip research step

### Optimize Knowledge Base Updates

1. **Schedule automation**: Run `auto_research.py` nightly via cron
2. **Focus queries**: Use specific domains and queries, not broad searches
3. **Cache results**: Script already caches for 24 hours

### Reduce API Costs

1. **Use v3.1 by default**: Only escalate to R1 when planning needed
2. **Reuse context**: Continue conversations instead of starting new ones
3. **Local validation**: Run pre-commit and pytest locally before asking for fixes

---

## Next Steps

- **New to system?** Start with "Workflow 1: Create New OCA Module"
- **Experienced user?** Jump to specific workflow or check troubleshooting
- **Contributing?** See `docs/IMPROVEMENT_WORKFLOW.md` for knowledge loop
- **Cost-conscious?** Review `docs/COST_ANALYSIS.md` for optimization strategies
- **Performance issues?** See `docs/PERFORMANCE_BENCHMARKS.md` for targets

**Daily Checklist**:
- [ ] Morning startup routine (10 minutes)
- [ ] Update knowledge base (5 minutes)
- [ ] Document discoveries (10 minutes)
- [ ] Run local evals before pushing (10 minutes)
- [ ] Review API costs (2 minutes)

**Weekly Checklist**:
- [ ] Knowledge base review (30 minutes)
- [ ] Update ORM library with new patterns (20 minutes)
- [ ] Review eval pass rates (10 minutes)
- [ ] Check API spending vs budget (5 minutes)

---

**Generated**: 2025-11-01
**Framework**: Cline CLI + DeepSeek API + Claude Code
**Target Audience**: Intermediate Odoo developers using agent-assisted workflows

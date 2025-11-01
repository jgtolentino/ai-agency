# Evaluation Scenarios for Odoo Agent Expertise

**Purpose**: Production-grade validation suite for agent capabilities

**Target Pass Rate**: ≥95% (all scenarios must pass before production release)

---

## Scenario Categories

### Module Development (Scenarios 1-3)
- OCA module scaffolding with security and tests
- ORM patterns (computed fields, record rules)
- Migration scripts with openupgradelib

### Studio Operations (Scenario 4)
- Studio change plans with safe rollback procedures

### Infrastructure (Scenarios 5-6)
- Docker image validation (wkhtmltopdf, SDK, security)
- Docker Compose environment setup

### DevOps (Scenarios 7-8)
- Odoo.sh deployment planning
- Visual parity gates validation

### Integration (Scenario 9)
- Task bus integration for deployment notifications

### Security (Scenario 10)
- Secrets policy compliance

---

## Execution

### Manual Execution
```bash
# Run individual scenario
bash evals/scenarios/01_oca_scaffolding.sh

# Run all scenarios
bash evals/scripts/run_all_evals.sh
```

### CI Integration
GitHub Actions workflow runs all scenarios on PR

### Pass Criteria
- **Individual**: Each scenario exits with code 0 (success)
- **Suite**: ≥95% pass rate (at least 9/10 passing)
- **Regression**: No previously passing scenarios may fail

---

## Scenarios

### 1. OCA Module Scaffolding
**File**: `01_oca_scaffolding.md`
**Skill**: odoo-module-dev
**Objective**: Generate OCA-compliant module with models, security, tests

### 2. Computed Field & Record Rule
**File**: `02_computed_record_rule.md`
**Skill**: odoo-module-dev
**Objective**: Implement @api.depends computed field and domain-based record rule

### 3. Migration Script
**File**: `03_migration_script.md`
**Skill**: odoo-module-dev
**Objective**: Create pre/post-migration scripts using openupgradelib

### 4. Studio Change Plan
**File**: `04_studio_change_plan.md`
**Skill**: odoo-studio-ops
**Objective**: Document Studio changes with XML export and rollback steps

### 5. Docker Image Validation
**File**: `05_docker_validation.md`
**Skill**: odoo-docker-claude
**Objective**: Build Docker image, validate wkhtmltopdf, SDK, non-root user

### 6. Docker Compose Environment
**File**: `06_docker_compose_env.md`
**Skill**: odoo-docker-claude
**Objective**: Set up functional Odoo + PostgreSQL environment

### 7. Odoo.sh Deployment Plan
**File**: `07_odoo_sh_deployment.md`
**Skill**: odoo-sh-devops
**Objective**: Create deployment runbook with staging validation gates

### 8. Visual Parity Validation
**File**: `08_visual_parity.md`
**Skill**: odoo-sh-devops
**Objective**: Validate SSIM thresholds for UI changes

### 9. Task Bus Integration
**File**: `09_task_bus_integration.md`
**Skill**: odoo-sh-devops
**Objective**: Implement deployment notifications via task_queue

### 10. Secrets Compliance
**File**: `10_secrets_compliance.md`
**Skill**: All
**Objective**: Verify no hardcoded secrets in any generated files

---

## Success Metrics

### Individual Scenario Metrics
- **Execution Time**: <5 minutes per scenario
- **Pass/Fail**: Binary (no partial credit)
- **Evidence**: Concrete output artifacts (files, logs, screenshots)

### Suite Metrics
- **Total Pass Rate**: ≥95% (9+/10 passing)
- **Regression Rate**: 0% (no previously passing scenarios may fail)
- **Execution Time**: <30 minutes for full suite
- **CI Integration**: All PRs gated on eval pass

---

## Improvement Loop

```
Eval Failure → Root Cause Analysis → Knowledge Base Update → Skill Refinement → Retest
```

**Process**:
1. Scenario fails with specific error
2. Investigate why skill didn't handle case
3. Research correct pattern (deep-research-oca)
4. Add citation to knowledge base
5. Update skill manifest with new capability
6. Rerun scenario → verify pass
7. Add regression test to prevent future failures

# Eval Scenario 12: QMS SOP Workflow

**Purpose**: Validate `qms_sop` module SOP execution tracking from creation through completion with error handling.

**Category**: PRD Implementation Validation
**Priority**: High (Production Critical)
**Estimated Execution Time**: 10-15 seconds

---

## Objective

Validate that the `qms_sop` module correctly implements Standard Operating Procedure (SOP) tracking with:
- SOP document creation with steps
- SOP run workflow (draft → in_progress → completed)
- Step-level execution tracking
- Error code linkage and resolution tracking
- State machine validation

---

## Prerequisites

### Module Installation
```bash
# Module must be installed in Odoo instance
# Path: custom_addons/qms_sop/
```

### Seed Data
```python
# Load seed SOPs via Odoo shell or data files
env['qms.sop.document'].create({
    'name': 'Build Docker Image',
    'code': 'SOP-BUILD-001',
    'category': 'build',
    'description': 'Standard procedure for building Odoo Docker images',
})

env['qms.sop.document'].create({
    'name': 'Deploy to DigitalOcean',
    'code': 'SOP-DEPLOY-001',
    'category': 'deployment',
    'description': 'Standard procedure for deploying to DO App Platform',
})

env['qms.sop.document'].create({
    'name': 'Error Triage Procedure',
    'code': 'SOP-ERROR-001',
    'category': 'operations',
    'description': 'Standard procedure for triaging production errors',
})
```

### Dependencies
```python
# Python libraries (standard Odoo)
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
```

---

## Test Cases

### TC01: SOP Document Creation
**Objective**: Verify SOP document creation with steps

**Input**:
```python
sop = env['qms.sop.document'].create({
    'name': 'Test Build Procedure',
    'code': 'SOP-TEST-001',
    'category': 'build',
    'description': 'Test SOP for evaluation',
})

# Add steps
step1 = env['qms.sop.step'].create({
    'sop_id': sop.id,
    'sequence': 10,
    'title': 'Pull base image',
    'description': 'Pull Odoo 19.0 base image from Docker Hub',
})

step2 = env['qms.sop.step'].create({
    'sop_id': sop.id,
    'sequence': 20,
    'title': 'Copy custom addons',
    'description': 'Copy custom modules to /opt/odoo/custom_addons',
})
```

**Expected Output**:
```python
assert sop.code == 'SOP-TEST-001'
assert sop.category == 'build'
assert len(sop.step_ids) == 2
assert sop.step_ids[0].title == 'Pull base image'
assert sop.step_ids[1].title == 'Copy custom addons'
```

**Pass Criteria**:
- ✅ SOP document created successfully
- ✅ Steps linked to SOP via step_ids
- ✅ Sequence ordering maintained
- ✅ No ValidationError raised

---

### TC02: SOP Run Workflow (Draft → In Progress → Completed)
**Objective**: Verify state transitions in SOP run lifecycle

**Input**:
```python
sop = env['qms.sop.document'].search([('code', '=', 'SOP-TEST-001')], limit=1)

run = env['qms.sop.run'].create({
    'sop_id': sop.id,
    'started_by': env.user.id,
    'state': 'draft',
})
```

**State Transitions**:
```python
# Initial state
assert run.state == 'draft'
assert run.start_time is False

# Start execution
run.action_start()
assert run.state == 'in_progress'
assert run.start_time is not False

# Complete execution
run.action_complete()
assert run.state == 'completed'
assert run.end_time is not False
assert run.duration > 0  # Computed field
```

**Pass Criteria**:
- ✅ Draft state allows transition to in_progress
- ✅ In_progress state allows transition to completed
- ✅ Timestamps recorded correctly (start_time, end_time)
- ✅ Duration computed from timestamps
- ✅ No invalid state transitions allowed

---

### TC03: Step Tracking
**Objective**: Verify step-level execution tracking within SOP run

**Input**:
```python
sop = env['qms.sop.document'].search([('code', '=', 'SOP-TEST-001')], limit=1)

run = env['qms.sop.run'].create({
    'sop_id': sop.id,
    'started_by': env.user.id,
    'state': 'draft',
})

run.action_start()

# Create step runs for each SOP step
for step in sop.step_ids:
    step_run = env['qms.sop.run.step'].create({
        'run_id': run.id,
        'step_id': step.id,
        'state': 'pending',
    })
```

**Step Execution**:
```python
# Get first step
step_run = run.step_run_ids[0]

# Start step
step_run.state = 'in_progress'
assert step_run.state == 'in_progress'

# Complete step with notes
step_run.state = 'completed'
step_run.notes = 'Base image pulled successfully: odoo:19.0'

assert step_run.state == 'completed'
assert 'successfully' in step_run.notes
```

**Pass Criteria**:
- ✅ Step runs created for each SOP step
- ✅ Step state transitions (pending → in_progress → completed)
- ✅ Notes captured for each step
- ✅ Computed field: run completion % based on step states

---

### TC04: Error Code Linkage
**Objective**: Verify error tracking and linkage to SOP runs

**Input**:
```python
# Create error code
error_code = env['qms.error.code'].create({
    'code': 'DOCKER-BUILD-001',
    'title': 'Docker build failed',
    'severity': 'high',
    'category': 'build',
    'description': 'Docker build command exited with non-zero status',
    'sop_id': sop.id,  # Link to resolution SOP
})

# Link error to run
error = env['qms.sop.run.error'].create({
    'run_id': run.id,
    'error_code_id': error_code.id,
    'description': 'Docker build failed at step 2: Copy custom addons',
    'resolved': False,
})
```

**Expected Output**:
```python
assert error.error_code_id.code == 'DOCKER-BUILD-001'
assert 'step 2' in error.description
assert error.resolved is False

# Resolve error
error.resolved = True
error.resolution_notes = 'Fixed permission issue on custom_addons directory'

assert error.resolved is True
assert 'Fixed' in error.resolution_notes
```

**Pass Criteria**:
- ✅ Error code created and linked to SOP
- ✅ Error instance linked to run
- ✅ Resolved flag toggles correctly
- ✅ Resolution notes captured

---

### TC05: Computed Field - Run Progress
**Objective**: Verify computed field calculates run completion percentage

**Input**:
```python
run = env['qms.sop.run'].search([('sop_id.code', '=', 'SOP-TEST-001')], limit=1)

# Initially no steps completed
assert run.progress_percentage == 0

# Complete first step
run.step_run_ids[0].state = 'completed'

# Progress should be 50% (1 of 2 steps)
assert run.progress_percentage == 50

# Complete second step
run.step_run_ids[1].state = 'completed'

# Progress should be 100%
assert run.progress_percentage == 100
```

**Pass Criteria**:
- ✅ Progress computed correctly based on completed steps
- ✅ Progress updates when step state changes
- ✅ Progress = 100 when all steps completed

---

### TC06: State Machine Validation
**Objective**: Verify invalid state transitions are blocked

**Input**:
```python
run = env['qms.sop.run'].create({
    'sop_id': sop.id,
    'started_by': env.user.id,
    'state': 'draft',
})
```

**Invalid Transitions**:
```python
from odoo.exceptions import ValidationError

# Cannot go from draft directly to completed
with pytest.raises(ValidationError):
    run.state = 'completed'

# Cannot go from completed back to in_progress
run.action_start()
run.action_complete()

with pytest.raises(ValidationError):
    run.state = 'in_progress'
```

**Pass Criteria**:
- ✅ Draft → Completed blocked (must go through in_progress)
- ✅ Completed → In Progress blocked (no backwards)
- ✅ ValidationError raised with clear message

---

## Acceptance Criteria

### Functional Requirements
- ✅ All 6 test cases pass (TC01-TC06)
- ✅ Execution time < 15 seconds
- ✅ State machine validated
- ✅ Error tracking functional
- ✅ Computed fields working correctly

### Data Integrity
- ✅ No orphan step_run records
- ✅ Timestamps consistent (start < end)
- ✅ Error codes reusable across runs
- ✅ SOP steps reusable across runs

### Code Quality
- ✅ Follows OCA guidelines
- ✅ Proper @api.depends on computed fields
- ✅ Constraints enforce state machine
- ✅ Documentation clear and complete

---

## Pass Criteria

**Overall Pass**: 100% of test cases must pass (6/6)

**Critical Test Cases** (must all pass):
- TC02: SOP Run Workflow
- TC03: Step Tracking
- TC06: State Machine Validation

**Non-Critical** (≥80% pass allowed):
- TC01: SOP Document Creation
- TC04: Error Code Linkage
- TC05: Computed Field - Run Progress

**Execution Requirements**:
- Total execution time < 15 seconds
- No manual intervention required
- Idempotent (can be run multiple times)

---

## Expected Output Format

### Successful Execution
```
=== Eval Scenario 12: QMS SOP Workflow ===

✅ TC01: SOP Document Creation - PASS (0.5s)
✅ TC02: SOP Run Workflow (Draft → Completed) - PASS (1.2s)
✅ TC03: Step Tracking - PASS (1.5s)
✅ TC04: Error Code Linkage - PASS (0.8s)
✅ TC05: Computed Field - Run Progress - PASS (0.6s)
✅ TC06: State Machine Validation - PASS (0.4s)

=== Summary ===
Passed: 6/6 (100%)
Total Time: 5.0s

✅ Scenario 12: PASS
```

### Failed Execution
```
=== Eval Scenario 12: QMS SOP Workflow ===

✅ TC01: SOP Document Creation - PASS (0.5s)
❌ TC02: SOP Run Workflow - FAIL (0.8s)
   Error: State transition draft → completed not blocked

⚠️  TC03: Step Tracking - SKIP (dependency failed)
✅ TC04: Error Code Linkage - PASS (0.8s)
❌ TC05: Computed Field - Run Progress - FAIL (0.6s)
   Error: Expected 50%, got 0%

✅ TC06: State Machine Validation - PASS (0.4s)

=== Summary ===
Passed: 3/6 (50%)
Failed: 2/6
Skipped: 1/6
Total Time: 3.1s

❌ Scenario 12: FAIL
```

---

## Common Failure Modes

### Failure Mode 1: Missing @api.depends on Computed Fields
**Symptom**: progress_percentage always returns 0

**Root Cause**:
- Missing @api.depends decorator on computed field
- Incorrect dependency specification

**Remediation**:
```python
# models/qms_sop_run.py
from odoo import models, fields, api

class QmsSopRun(models.Model):
    _name = 'qms.sop.run'

    # Correct implementation
    @api.depends('step_run_ids.state')
    def _compute_progress_percentage(self):
        for rec in self:
            total = len(rec.step_run_ids)
            if total == 0:
                rec.progress_percentage = 0
            else:
                completed = len(rec.step_run_ids.filtered(lambda s: s.state == 'completed'))
                rec.progress_percentage = (completed / total) * 100
```

---

### Failure Mode 2: State Machine Not Enforced
**Symptom**: Invalid state transitions allowed (e.g., draft → completed)

**Root Cause**:
- Missing @api.constrains decorator
- No validation logic on state field

**Remediation**:
```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class QmsSopRun(models.Model):
    _name = 'qms.sop.run'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', required=True)

    @api.constrains('state')
    def _check_state_transition(self):
        for rec in self:
            # Get previous state from cache or database
            old_state = rec._origin.state if rec._origin else 'draft'

            # Define valid transitions
            valid_transitions = {
                'draft': ['in_progress', 'cancelled'],
                'in_progress': ['completed', 'cancelled'],
                'completed': [],  # Terminal state
                'cancelled': [],  # Terminal state
            }

            if old_state and rec.state not in valid_transitions.get(old_state, []):
                raise ValidationError(
                    f"Invalid state transition: {old_state} → {rec.state}"
                )
```

---

### Failure Mode 3: Orphan Step Runs
**Symptom**: step_run_ids not linked to run after creation

**Root Cause**:
- Missing run_id in create() call
- Incorrect One2many field definition

**Remediation**:
```python
# models/qms_sop_run.py
class QmsSopRun(models.Model):
    _name = 'qms.sop.run'

    step_run_ids = fields.One2many(
        'qms.sop.run.step',
        'run_id',
        string='Step Runs',
        copy=False,
    )

# models/qms_sop_run_step.py
class QmsSopRunStep(models.Model):
    _name = 'qms.sop.run.step'

    run_id = fields.Many2one(
        'qms.sop.run',
        string='SOP Run',
        required=True,
        ondelete='cascade',  # Delete step runs when run is deleted
    )
```

---

## Integration with Knowledge Base

### Related Documentation
- `knowledge/patterns/odoo_state_machine.md` - State machine implementation
- `knowledge/patterns/odoo_workflow.md` - Workflow and approval patterns
- `knowledge/patterns/odoo_computed_fields.md` - Computed field best practices

### Pattern Extraction
If scenario fails, check for missing patterns:
- State machine constraints in Odoo
- Computed field dependencies
- One2many/Many2one relationship best practices

---

## References

- [Odoo 19.0 ORM Documentation](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [State Machine Pattern in Odoo](https://www.odoo.com/documentation/19.0/developer/tutorials/backend/11_states.html)
- [Computed Fields](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html#computed-fields)
- [OCA Guidelines: Workflow Models](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#workflow)

---

## Automation Notes

This scenario is fully automatable with:
- Pytest fixtures for Odoo environment setup
- TransactionCase for database rollback after tests
- setUp/tearDown methods for SOP seed data
- Isolated test database to prevent pollution

**CI/CD Integration**: Safe to run in CI (no external dependencies, pure Odoo ORM)

---

## Seed Data Files

**File**: `custom_addons/qms_sop/data/qms_sop_seeds.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Build Image SOP -->
        <record id="sop_build_image" model="qms.sop.document">
            <field name="name">Build Docker Image</field>
            <field name="code">SOP-BUILD-001</field>
            <field name="category">build</field>
            <field name="description">Standard procedure for building Odoo Docker images</field>
        </record>

        <record id="sop_build_step_1" model="qms.sop.step">
            <field name="sop_id" ref="sop_build_image"/>
            <field name="sequence">10</field>
            <field name="title">Pull base image</field>
            <field name="description">Pull Odoo 19.0 base image from Docker Hub</field>
        </record>

        <record id="sop_build_step_2" model="qms.sop.step">
            <field name="sop_id" ref="sop_build_image"/>
            <field name="sequence">20</field>
            <field name="title">Copy custom addons</field>
            <field name="description">Copy custom modules to /opt/odoo/custom_addons</field>
        </record>

        <!-- Deploy to DigitalOcean SOP -->
        <record id="sop_deploy_do" model="qms.sop.document">
            <field name="name">Deploy to DigitalOcean</field>
            <field name="code">SOP-DEPLOY-001</field>
            <field name="category">deployment</field>
            <field name="description">Standard procedure for deploying to DO App Platform</field>
        </record>

        <!-- Error Triage SOP -->
        <record id="sop_error_triage" model="qms.sop.document">
            <field name="name">Error Triage Procedure</field>
            <field name="code">SOP-ERROR-001</field>
            <field name="category">operations</field>
            <field name="description">Standard procedure for triaging production errors</field>
        </record>

        <!-- Common Error Codes -->
        <record id="error_docker_build" model="qms.error.code">
            <field name="code">DOCKER-BUILD-001</field>
            <field name="title">Docker build failed</field>
            <field name="severity">high</field>
            <field name="category">build</field>
            <field name="description">Docker build command exited with non-zero status</field>
            <field name="sop_id" ref="sop_build_image"/>
        </record>

        <record id="error_deploy_timeout" model="qms.error.code">
            <field name="code">DEPLOY-TIMEOUT-001</field>
            <field name="title">Deployment timeout</field>
            <field name="severity">high</field>
            <field name="category">deployment</field>
            <field name="description">Deployment exceeded 10-minute timeout</field>
            <field name="sop_id" ref="sop_deploy_do"/>
        </record>
    </data>
</odoo>
```

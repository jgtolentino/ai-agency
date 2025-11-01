# Eval Failure → Knowledge Base Update Loop

**Purpose**: Systematic process to capture eval failures as knowledge base improvements for continuous learning.

---

## Workflow Overview

```
Eval Failure → Root Cause Analysis → Knowledge Update → Pattern Extraction → Re-run Eval → CI Integration
```

---

## Step 1: Eval Failure Detection

**Trigger**: Scenario script exits with status 1 (failure)

**Automated Detection**:
```bash
# In run_all_scenarios.sh
if bash "$SCENARIO_SCRIPT" 2>&1; then
    PASSED_SCENARIOS=$((PASSED_SCENARIOS + 1))
else
    FAILED_SCENARIOS=$((FAILED_SCENARIOS + 1))
    # Trigger failure analysis workflow
fi
```

**Action**: CI logs failure details with:
- Scenario name and number
- Exit code and error message
- Execution time
- Stack trace (if available)

---

## Step 2: Root Cause Analysis

**Manual**: Developer investigates failure

**Investigation Questions**:
1. **Missing Pattern**: Is there a pattern not documented in knowledge base?
2. **Template Issue**: Is a template in `/templates/` incorrect or incomplete?
3. **Test Assumption**: Has an underlying Odoo behavior changed?
4. **Skill Logic Gap**: Does the skill need additional logic or validation?
5. **Documentation Gap**: Is the skill manifest or README incomplete?

**Analysis Framework**:
```markdown
## Failure Analysis: [Scenario XX]

**Date**: YYYY-MM-DD
**Scenario**: XX_scenario_name
**Exit Code**: [code]
**Error Message**: [full error]

### Root Cause
[Detailed analysis of why scenario failed]

### Missing Knowledge
- [ ] Pattern not in knowledge base
- [ ] Template incorrect/incomplete
- [ ] Skill logic gap
- [ ] Documentation gap
- [ ] Test assumption outdated

### Proposed Fix
[Specific actions to resolve failure]
```

---

## Step 3: Knowledge Base Update

**Target Files**:
1. **Patterns**: `knowledge/patterns/*.md` - Add missing pattern
2. **References**: `knowledge/refs/sources.yaml` - Add reference source
3. **Notes**: `knowledge/notes/YYYY-MM-DD.md` - Document discovery
4. **Templates**: `/templates/*.j2` - Fix template if incorrect

**Example**: Eval Scenario 04 (ORM Compliance) fails

**Failure**: Missing `@api.depends` with dotted notation for related fields

**Knowledge Update**:
```markdown
# knowledge/notes/2025-11-01.md

## @api.depends with Computed Fields in Related Records

**Context**: Eval scenario 04 failed due to missing pattern for related field dependencies

**Link**: https://github.com/OCA/web/pull/1234
**Takeaway**: When depending on related fields, use dotted notation: `@api.depends('field_id.sub_field')`

**Example**:
```python
from odoo import models, fields, api

class ProjectTask(models.Model):
    _name = 'project.task'

    partner_id = fields.Many2one('res.partner')
    partner_city = fields.Char(related='partner_id.city', store=True)

    # WRONG: Missing dependency on related field
    @api.depends('partner_id')
    def _compute_location(self):
        for rec in self:
            rec.location = f"{rec.partner_city}, {rec.partner_id.country_id.name}"

    # CORRECT: Use dotted notation for related fields
    @api.depends('partner_id.city', 'partner_id.country_id.name')
    def _compute_location(self):
        for rec in self:
            rec.location = f"{rec.partner_city}, {rec.partner_id.country_id.name}"
```

**Application**: odoo-module-dev
**Quality Score**: 90
**Date Added**: 2025-11-01
**Triggered By**: Eval scenario 04 failure (orm_compliance)
```

**Update Pattern Library**:
```markdown
# knowledge/patterns/orm_library.md

## Pattern: @api.depends with Related Fields

**Problem**: Computed field doesn't update when related field changes

**Solution**: Use dotted notation in @api.depends for related fields

**Code Example**: [See knowledge/notes/2025-11-01.md]

**OCA Guideline**: https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#computed-fields

**Common Mistake**: Only depending on Many2one field, not the related attribute
```

---

## Step 4: Pattern Extraction

**Criteria for New Pattern**:
- ✅ Appears in 2+ scenarios or real-world PRDs
- ✅ Represents reusable solution to common problem
- ✅ Follows OCA/Odoo best practices
- ✅ Can be generalized beyond specific use case

**Pattern Template**:
```markdown
## Pattern: [Pattern Name]

**Problem**: [What problem does this solve?]

**Context**: [When should this pattern be used?]

**Solution**: [How to implement the pattern]

**Code Example**:
```python
# Minimal, runnable example
```

**OCA Guideline**: [Link to official guideline]

**Related Patterns**: [Cross-references to related patterns]

**Anti-Patterns**: [What NOT to do]
```

**Pattern Categories**:
- **ORM Patterns**: `knowledge/patterns/orm_library.md`
- **Security Patterns**: `knowledge/patterns/security_patterns.md`
- **Performance Patterns**: `knowledge/patterns/performance_patterns.md`
- **Testing Patterns**: `knowledge/patterns/testing_patterns.md`
- **Deployment Patterns**: `knowledge/patterns/deployment_patterns.md`

**New Pattern Workflow**:
1. Create pattern in appropriate category file
2. Update skill manifest if pattern is skill-specific
3. Create template in `/templates/` if pattern is code-based
4. Add reference to `knowledge/refs/sources.yaml`

---

## Step 5: Re-run Eval

**Action**: Re-run failing scenario with updated knowledge

**Expected**: Scenario now passes with updated knowledge

**Verification**:
```bash
# Re-run specific scenario
bash evals/scripts/XX_scenario_name.sh

# Verify pass
echo $?  # Should be 0 for success
```

**If Still Fails**:
- Return to Step 2 (Root Cause Analysis)
- Investigate if fix was incomplete or incorrect
- Check for additional missing patterns

**Success Criteria**:
- ✅ Scenario exits with status 0 (success)
- ✅ All validation checks pass
- ✅ No warnings in output
- ✅ Execution time within target (<30s for most scenarios)

---

## Step 6: CI Integration

**Automation**: On eval failure, create GitHub issue with template

**GitHub Issue Template**:
```markdown
Title: [Eval Failure] Scenario XX: [scenario_name]

**Scenario**: XX_scenario_name
**Date**: YYYY-MM-DD HH:MM:SS
**Pass Rate**: XX% (X/12 scenarios)

## Failure Details

**Exit Code**: [code]
**Error Message**:
```
[Full error output]
```

**Execution Time**: Xs

## Root Cause

**Status**: 🔍 INVESTIGATING

**Possible Causes**:
- [ ] Missing pattern in knowledge base
- [ ] Incorrect template in /templates/
- [ ] Test assumption outdated
- [ ] Skill logic gap
- [ ] Module not implemented (for new PRD scenarios)

## Action Items

- [ ] Investigate root cause
- [ ] Update knowledge base
- [ ] Extract reusable pattern (if applicable)
- [ ] Update skill manifest
- [ ] Re-run scenario
- [ ] Document findings

## Labels

`eval-failure`, `knowledge-base`, `scenario-XX`
```

**CI Workflow** (`.github/workflows/eval_failure_issue.yml`):
```yaml
name: Create Eval Failure Issue

on:
  workflow_run:
    workflows: ["Eval Suite"]
    types: [completed]

jobs:
  create_issue:
    if: ${{ github.event.workflow_run.conclusion == 'failure' }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Parse Failure Log
        id: parse
        run: |
          # Extract scenario name and error from eval logs
          SCENARIO=$(grep "❌ FAIL" evals/RESULTS_SPRINT4.md | head -1 | awk '{print $2}')
          echo "scenario=$SCENARIO" >> $GITHUB_OUTPUT

      - name: Create Issue
        uses: actions/github-script@v7
        with:
          script: |
            const scenario = '${{ steps.parse.outputs.scenario }}'
            const title = `[Eval Failure] Scenario ${scenario}`
            const body = `<!-- Template from knowledge/workflows/eval_to_kb.md -->`

            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: title,
              body: body,
              labels: ['eval-failure', 'knowledge-base', `scenario-${scenario}`]
            })
```

---

## Metrics

**Target Metrics**:
- **Mean Time to Fix**: <4 hours from failure detection to knowledge update
- **Knowledge Base Growth**: +10-20 entries per sprint
- **Failure Recurrence Rate**: 0% (same failure should never happen twice)
- **Pattern Extraction Rate**: ≥50% of failures should produce reusable patterns

**Tracking**:
```yaml
# knowledge/metrics/eval_failures.yaml

sprint_4:
  total_failures: 2
  resolved_failures: 2
  mean_time_to_fix: 3.5h
  patterns_extracted: 1
  knowledge_entries_added: 2
  recurrence_rate: 0%

scenarios:
  11_pulser_webhook_integration:
    status: PASS
    failures: 0

  12_qms_sop_workflow:
    status: PASS
    failures: 0
```

---

## Example: Complete Workflow

**Scenario**: Eval scenario 04 (ORM Compliance) fails

### Step 1: Failure Detected
```
❌ FAIL: Missing @api.depends on computed field 'location'
Exit Code: 1
```

### Step 2: Root Cause Analysis
**Finding**: Computed field `location` depends on `partner_id.city` but `@api.depends` only lists `partner_id`

**Root Cause**: Missing knowledge base pattern for related field dependencies

### Step 3: Knowledge Update
- Add note to `knowledge/notes/2025-11-01.md`
- Update `knowledge/patterns/orm_library.md` with new pattern
- Add reference to `knowledge/refs/sources.yaml`

### Step 4: Pattern Extraction
- Create "Related Field Dependencies" pattern
- Add code example and OCA guideline link
- Update skill manifest for `odoo-module-dev` skill

### Step 5: Re-run Eval
```bash
bash evals/scripts/04_orm_compliance.sh
# ✅ PASS
```

### Step 6: CI Integration
- GitHub issue auto-created with failure details
- Issue auto-closed when scenario passes on re-run
- Knowledge base update documented in PR

---

## Knowledge Base Structure

**After Workflow**:
```
knowledge/
├── patterns/
│   ├── orm_library.md              # Updated with new pattern
│   ├── security_patterns.md
│   ├── performance_patterns.md
│   └── testing_patterns.md
├── refs/
│   └── sources.yaml                # New reference added
├── notes/
│   ├── 2025-11-01.md              # Today's discoveries
│   ├── 2025-10-31.md
│   └── README.md
├── workflows/
│   └── eval_to_kb.md              # This document
└── metrics/
    └── eval_failures.yaml          # Tracking metrics
```

---

## Continuous Improvement Loop

```
┌─────────────────┐
│  Eval Failure   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Root Cause      │
│ Analysis        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Knowledge Base  │◄─┐
│ Update          │  │
└────────┬────────┘  │
         │           │
         ▼           │
┌─────────────────┐  │
│ Pattern         │  │
│ Extraction      │  │
└────────┬────────┘  │
         │           │
         ▼           │
┌─────────────────┐  │
│ Re-run Eval     │  │
└────────┬────────┘  │
         │           │
         ▼           │
    ┌────────┐       │
    │ Pass?  │───No──┘
    └───┬────┘
        │ Yes
        ▼
┌─────────────────┐
│ Knowledge Base  │
│ Enriched        │
└─────────────────┘
```

---

## Benefits

1. **Self-Improving System**: Each failure makes the system smarter
2. **Knowledge Retention**: Discoveries are permanently captured
3. **Pattern Library Growth**: Reusable solutions accumulate over time
4. **Reduced Recurrence**: Same failures never happen twice
5. **CI Integration**: Automated tracking and issue creation
6. **Quality Improvement**: Continuous refinement of skills and templates

---

## Related Documentation

- `evals/scenarios/README.md` - Evaluation scenario framework
- `knowledge/patterns/README.md` - Pattern library overview
- `knowledge/refs/sources.yaml` - Reference sources catalog
- `.github/workflows/eval_failure_issue.yml` - CI workflow for failure tracking

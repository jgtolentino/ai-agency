# Improvement Workflow – Eval Failure Analysis & Knowledge Loop

**Purpose**: Systematic process for learning from failures and improving agent capabilities

**Last Updated**: 2025-11-01

---

## Overview

The improvement workflow is a closed-loop system that converts eval failures, production issues, and community discoveries into actionable knowledge that enhances agent capabilities.

```
Eval Failure / Production Issue
    ↓
Root Cause Analysis
    ↓
Pattern Extraction
    ↓
Knowledge Base Update
    ↓
Skill Enhancement (if needed)
    ↓
New Eval Scenario
    ↓
Validation & Deployment
```

---

## Phase 1: Eval Failure Analysis (30 minutes)

### Step 1: Identify Failure

```bash
# Run specific failed scenario
cd ~/ai-agency/agents/odoo-expertise/evals
bash scripts/04_orm_compliance.sh -v

# Example failure output:
# ❌ FAIL: N+1 query detected in _compute_total_lines
# Expected: 1 query
# Actual: 51 queries (1 + 50 line reads)
```

### Step 2: Reproduce Locally

```bash
# Extract failing code to test file
cd ~/ai-agency/agents/odoo-expertise
mkdir -p debug/eval_failures/$(date +%Y-%m-%d)
cd debug/eval_failures/$(date +%Y-%m-%d)

# Create reproduction script
cat > reproduce_n1_query.py <<'EOF'
from odoo.tests.common import TransactionCase

class TestN1Query(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Model = self.env['your.model']

    def test_compute_no_n1(self):
        # Create 50 records with related data
        records = self.Model.create([...])

        # Trigger computation
        with self.assertQueryCount(1):  # Should be 1 query, not 51
            records._compute_total_lines()
EOF

# Run reproduction
pytest reproduce_n1_query.py -v -s
```

### Step 3: Analyze with AI

```bash
# Use DeepSeek v3.1 for analysis
cline-odoo "Analyze this eval failure:
Scenario: 04_orm_compliance
Symptom: N+1 query in _compute_total_lines method
Code: [paste failing code]
Expected: 1 query
Actual: 51 queries

Provide:
1. Root cause explanation
2. OCA-compliant fix
3. Prevention strategy for future modules
4. Citation to OCA example implementing this correctly"
```

**Expected Output**:
```markdown
## Root Cause
The _compute_total_lines method iterates over self and accesses
self.line_ids for each record individually, triggering database
queries in a loop.

## OCA-Compliant Fix
Use read_group to fetch all line counts in a single query:

```python
@api.depends('line_ids')
def _compute_total_lines(self):
    if not self:
        return

    # Single query for all records
    line_data = self.env['your.model.line'].read_group(
        domain=[('model_id', 'in', self.ids)],
        fields=['model_id'],
        groupby=['model_id']
    )

    # Create mapping
    line_counts = {
        data['model_id'][0]: data['model_id_count']
        for data in line_data
    }

    # Assign in memory (no queries)
    for record in self:
        record.total_lines = line_counts.get(record.id, 0)
```

## Prevention Strategy
- Always use read_group for aggregations
- Test with assertQueryCount in setUp
- Review OCA modules before implementing patterns

## OCA Citation
- Link: https://github.com/OCA/sale-workflow/blob/16.0/sale_order_line_sequence/models/sale_order.py#L67
- Pattern: read_group with domain and groupby
```

### Step 4: Validate Fix

```bash
# Apply fix
# (Edit the failing code with suggested fix)

# Re-run eval
bash scripts/04_orm_compliance.sh

# Expected:
# ✅ PASS: N+1 query resolved
# ✅ PASS: 1 query as expected
```

---

## Phase 2: Pattern Extraction (20 minutes)

### Step 1: Generalize the Pattern

```bash
# Use DeepSeek R1 for pattern abstraction
cline-odoo "Using DeepSeek R1 reasoning, extract a general pattern from this fix:

Specific Case: N+1 in _compute_total_lines
Fix: Used read_group with domain and groupby

Generalize to:
- Pattern name
- When to apply
- Code template
- Test template
- Common pitfalls"
```

**Expected Output**:
```markdown
## Pattern: Aggregation Without N+1

### When to Apply
- Computing counts, sums, averages from related records
- Working with One2many or Many2many fields
- Need to process multiple parent records at once

### Code Template
```python
@api.depends('related_field_ids', 'related_field_ids.field_to_aggregate')
def _compute_aggregated_value(self):
    if not self:
        return

    # Single query for all records
    aggregate_data = self.env['related.model'].read_group(
        domain=[('parent_id', 'in', self.ids)],
        fields=['parent_id', 'field_to_aggregate:sum'],  # or avg, count
        groupby=['parent_id']
    )

    # Create mapping {parent_id: aggregated_value}
    mapping = {
        data['parent_id'][0]: data['field_to_aggregate']
        for data in aggregate_data
    }

    # Assign in memory
    for record in self:
        record.aggregated_value = mapping.get(record.id, 0.0)
```

### Test Template
```python
def test_no_n1_in_aggregation(self):
    """Ensure aggregation uses single query"""
    parent_records = self.env['parent.model'].create([
        {'name': f'Parent {i}'} for i in range(50)
    ])

    # Create related records
    for parent in parent_records:
        self.env['related.model'].create([
            {'parent_id': parent.id, 'value': i} for i in range(10)
        ])

    # Trigger computation with query count assertion
    with self.assertQueryCount(1):  # Expect 1 read_group query
        parent_records._compute_aggregated_value()
```

### Common Pitfalls
❌ Accessing related fields in loop: `for rec in self: total = sum(rec.line_ids.mapped('amount'))`
❌ Using search() in compute: `for rec in self: rec.total = self.env['model'].search_count([('parent_id', '=', rec.id)])`
❌ Forgetting to handle empty self: Not checking `if not self: return`

✅ Use read_group for aggregations
✅ Use search_read for filtered data
✅ Always check `if not self` at start of compute methods
```

### Step 2: Add to ORM Library

```bash
# Add pattern to knowledge base
cd ~/ai-agency/agents/odoo-expertise/knowledge/patterns

# Append to orm_library.md
cat >> orm_library.md <<'EOF'

---

## 13. Aggregation Without N+1 Queries

**Purpose**: Compute aggregated values (count, sum, avg) from related records without N+1 queries

**Pattern**: read_group with domain and groupby

### Example: Computing Total Line Count

```python
from odoo import api, fields, models

class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sale Order'

    line_ids = fields.One2many('sale.order.line', 'order_id', string='Order Lines')
    total_lines = fields.Integer(compute='_compute_total_lines', store=True)

    @api.depends('line_ids')
    def _compute_total_lines(self):
        if not self:
            return

        # Single query for all records
        line_data = self.env['sale.order.line'].read_group(
            domain=[('order_id', 'in', self.ids)],
            fields=['order_id'],
            groupby=['order_id']
        )

        # Create mapping
        line_counts = {
            data['order_id'][0]: data['order_id_count']
            for data in line_data
        }

        # Assign in memory
        for record in self:
            record.total_lines = line_counts.get(record.id, 0)
```

### Example: Computing Sum of Line Amounts

```python
@api.depends('line_ids', 'line_ids.amount')
def _compute_total_amount(self):
    if not self:
        return

    amount_data = self.env['sale.order.line'].read_group(
        domain=[('order_id', 'in', self.ids)],
        fields=['order_id', 'amount:sum'],
        groupby=['order_id']
    )

    amount_mapping = {
        data['order_id'][0]: data['amount']
        for data in amount_data
    }

    for record in self:
        record.total_amount = amount_mapping.get(record.id, 0.0)
```

### Pitfalls to Avoid

❌ **N+1 Query Pattern**:
```python
# This triggers 1 + N queries
for record in self:
    record.total_lines = len(record.line_ids)  # Query per record
```

❌ **search_count in Loop**:
```python
# This triggers N queries
for record in self:
    record.total_lines = self.env['sale.order.line'].search_count([
        ('order_id', '=', record.id)
    ])
```

✅ **Correct Pattern**:
- Use `read_group` for aggregations
- Always check `if not self: return` first
- Create mapping dictionary before loop
- Assign values in memory without queries

### Test Template

```python
def test_aggregation_no_n1(self):
    """Ensure aggregation computed without N+1 queries"""
    # Create 50 parent records
    parents = self.env['sale.order'].create([
        {'name': f'SO{i:03d}'} for i in range(50)
    ])

    # Create 10 lines per parent
    for parent in parents:
        self.env['sale.order.line'].create([
            {'order_id': parent.id, 'amount': i * 10}
            for i in range(10)
        ])

    # Trigger computation with query count assertion
    with self.assertQueryCount(1):
        parents._compute_total_lines()

    # Verify results
    for parent in parents:
        self.assertEqual(parent.total_lines, 10)
```

### OCA References
- [sale-workflow: read_group pattern](https://github.com/OCA/sale-workflow/blob/16.0/sale_order_line_sequence/models/sale_order.py#L67)
- [account-financial-tools: aggregation](https://github.com/OCA/account-financial-tools/blob/16.0/account_move_budget/models/account_move.py#L89)

EOF
```

---

## Phase 3: Knowledge Base Update (15 minutes)

### Step 1: Create Citation

```bash
# Add to daily notes
cd ~/ai-agency/agents/odoo-expertise/knowledge/notes
cat >> $(date +%Y-%m-%d).md <<'EOF'

## Aggregation Without N+1 Pattern
- **Link**: https://github.com/OCA/sale-workflow/blob/16.0/sale_order_line_sequence/models/sale_order.py#L67
- **Takeaway**: Use read_group with domain and groupby to compute aggregations in single query
- **Application**: odoo-module-dev
- **Trigger**: Eval 04_orm_compliance failure analysis
- **Quality Score**: 95 (OCA maintainer code)
- **Date Added**: 2025-11-01

### Context
Discovered during eval failure analysis. N+1 query in _compute_total_lines
was triggering 51 queries instead of 1. Fix: read_group with domain filter.

### Impact
- Prevents N+1 queries in computed fields
- Reduces database load for large recordsets
- Improves UI responsiveness
- Follows OCA performance best practices
EOF
```

### Step 2: Update Sources Catalog

```bash
# Edit knowledge/refs/sources.yaml
cat >> knowledge/refs/sources.yaml <<'EOF'

- name: "OCA sale-workflow: read_group aggregation"
  url: "https://github.com/OCA/sale-workflow/blob/16.0/sale_order_line_sequence/models/sale_order.py"
  type: oca
  quality_score: 95
  date_added: "2025-11-01"
  categories:
    - orm_patterns
    - performance
  tags:
    - read_group
    - n+1_prevention
    - computed_fields
  notes: |
    Reference implementation of read_group for aggregations without N+1 queries.
    Used in eval failure resolution for 04_orm_compliance.
EOF
```

### Step 3: Update Playbooks (if applicable)

```bash
# If pattern affects deep research queries
cd ~/ai-agency/agents/odoo-expertise/knowledge/playbooks

# Add to deep_research_odoo.md query sets
cat >> deep_research_odoo.md <<'EOF'

### Query Set: Performance Patterns

**Objective**: Find OCA-validated performance optimization patterns

**GitHub Queries**:
- `org:OCA read_group language:Python`
- `org:OCA assertQueryCount language:Python`
- `org:OCA "computed field" performance language:Python`

**Reddit Queries**:
- `subreddit:odoo N+1 query`
- `subreddit:odoo "computed field" performance`
- `subreddit:odoo read_group optimization`

**Stack Overflow Queries**:
- `[odoo] N+1 query computed field`
- `[odoo] read_group performance`
- `[odoo] optimize computed field`

**Expected Outcomes**: 5-10 high-quality patterns for N+1 prevention

EOF
```

---

## Phase 4: Skill Enhancement (Optional, 30 minutes)

### When to Update Skills

Update skill YAML if:
- Pattern is broadly applicable (not edge case)
- Multiple evals failed on similar issues
- Community frequently asks about this
- Current skill instructions are incomplete

### Skill Update Process

```bash
# Edit skill manifest
cd ~/ai-agency/agents/odoo-expertise/skills/odoo-module-dev

# Update skill.yaml
```

**Example Addition**:
```yaml
guidelines:
  orm_patterns:
    - "Use read_group for aggregations to avoid N+1 queries"
    - "Always include 'if not self: return' at start of compute methods"
    - "Test with assertQueryCount to validate query efficiency"

  computed_fields:
    - "For aggregations: use read_group with domain [('parent_id', 'in', self.ids)]"
    - "For filtering: use search_read with domain and fields parameter"
    - "For counts: prefer read_group over search_count in loops"

examples:
  - name: "Aggregation Without N+1"
    code: |
      @api.depends('line_ids', 'line_ids.amount')
      def _compute_total_amount(self):
          if not self:
              return

          amount_data = self.env['related.model'].read_group(
              domain=[('parent_id', 'in', self.ids)],
              fields=['parent_id', 'amount:sum'],
              groupby=['parent_id']
          )

          mapping = {d['parent_id'][0]: d['amount'] for d in amount_data}

          for record in self:
              record.total_amount = mapping.get(record.id, 0.0)
```

### Validate Skill Update

```bash
# Test skill with new pattern
cline-odoo "Create module with computed field using read_group aggregation pattern"

# Verify it generates correct code
cat custom_addons/test_aggregation/models/*.py | grep read_group

# Run eval to confirm
cd evals
bash scripts/04_orm_compliance.sh
```

---

## Phase 5: New Eval Scenario Creation (45 minutes)

### Step 1: Define Scenario

```bash
# Create new scenario file
cd ~/ai-agency/agents/odoo-expertise/evals/scenarios
cat > 11_aggregation_patterns.md <<'EOF'
# Eval Scenario 11: Aggregation Patterns Without N+1

**Objective**: Validate agent generates efficient aggregation patterns using read_group

**Difficulty**: Intermediate
**Duration**: 10 minutes
**Prerequisites**: Python 3.11+, pytest-odoo

---

## Scenario Description

Generate an Odoo module with multiple aggregation computed fields and verify
no N+1 queries are triggered when computing values for large recordsets.

## Test Module Specification

**Module Name**: `test_aggregation_patterns`
**Model**: `test.parent`

**Fields**:
- `name` (Char, required)
- `line_ids` (One2many → test.parent.line)
- `total_lines` (Integer, computed, stored) - Count of lines
- `total_amount` (Float, computed, stored) - Sum of line amounts
- `average_amount` (Float, computed) - Average of line amounts

**Related Model**: `test.parent.line`
**Fields**:
- `parent_id` (Many2one → test.parent, required)
- `amount` (Float, required)

## Pass Criteria

✅ Module generated with OCA structure
✅ All computed fields use read_group (no N+1 queries)
✅ Includes `if not self: return` guards
✅ Test file with assertQueryCount validations
✅ All tests pass with query count = 1 per computation
✅ Pre-commit hooks pass

## Automated Validation

```bash
#!/bin/bash
# evals/scripts/11_aggregation_patterns.sh

set -e

echo "=== Eval Scenario 11: Aggregation Patterns ==="

# Generate module
cline-odoo "Create OCA module 'test_aggregation_patterns' with:
- Model test.parent with name, line_ids, total_lines, total_amount, average_amount
- Model test.parent.line with parent_id, amount
- All aggregations using read_group pattern
- Tests with assertQueryCount(1) for each computed field"

# Validate structure
test -f custom_addons/test_aggregation_patterns/__manifest__.py || exit 1
test -f custom_addons/test_aggregation_patterns/models/test_parent.py || exit 1
test -f custom_addons/test_aggregation_patterns/tests/test_aggregation.py || exit 1

# Check for read_group usage
grep -q "read_group" custom_addons/test_aggregation_patterns/models/test_parent.py || {
    echo "❌ FAIL: read_group not found in model"
    exit 1
}

# Check for query count assertions
grep -q "assertQueryCount" custom_addons/test_aggregation_patterns/tests/test_aggregation.py || {
    echo "❌ FAIL: assertQueryCount not found in tests"
    exit 1
}

# Run tests
pytest custom_addons/test_aggregation_patterns/tests/test_aggregation.py -v

echo "✅ PASS: Aggregation patterns eval complete"
```
EOF
```

### Step 2: Create Executable Script

```bash
# Create test runner
cd ~/ai-agency/agents/odoo-expertise/evals/scripts
cat > 11_aggregation_patterns.sh <<'EOF'
#!/bin/bash
# Eval Scenario 11: Aggregation Patterns Without N+1

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVAL_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(dirname "$EVAL_DIR")"

echo "=== Eval Scenario 11: Aggregation Patterns ==="
echo "Working directory: $REPO_ROOT"

cd "$REPO_ROOT"

# Clean previous run
rm -rf custom_addons/test_aggregation_patterns

# Generate module (using Cline automation)
echo "Generating test module..."
cline-odoo "Create OCA module 'test_aggregation_patterns' with:
- Model: test.parent (name, line_ids, total_lines, total_amount, average_amount)
- Model: test.parent.line (parent_id, amount)
- All computed fields use read_group pattern
- Include assertQueryCount tests
- OCA-compliant structure"

# Validate generated structure
echo "Validating structure..."
test -f custom_addons/test_aggregation_patterns/__manifest__.py || {
    echo "❌ FAIL: __manifest__.py not found"
    exit 1
}

test -f custom_addons/test_aggregation_patterns/models/test_parent.py || {
    echo "❌ FAIL: models/test_parent.py not found"
    exit 1
}

# Check for read_group pattern
echo "Checking for read_group usage..."
if ! grep -q "read_group" custom_addons/test_aggregation_patterns/models/test_parent.py; then
    echo "❌ FAIL: read_group not found (likely N+1 pattern)"
    exit 1
fi

# Check for assertQueryCount
echo "Checking for query count assertions..."
if ! grep -q "assertQueryCount" custom_addons/test_aggregation_patterns/tests/test_aggregation.py; then
    echo "❌ FAIL: assertQueryCount not found in tests"
    exit 1
fi

# Run pre-commit hooks
echo "Running pre-commit hooks..."
cd custom_addons/test_aggregation_patterns
pre-commit run --all-files || {
    echo "❌ FAIL: Pre-commit hooks failed"
    exit 1
}

# Run tests
echo "Running pytest..."
pytest tests/test_aggregation.py -v || {
    echo "❌ FAIL: Tests failed"
    exit 1
}

echo ""
echo "✅ PASS: All aggregation patterns validated"
echo "✅ PASS: No N+1 queries detected"
echo "✅ PASS: Pre-commit hooks passed"
echo "✅ PASS: Tests passed"
echo ""
echo "Eval Scenario 11: COMPLETE"
EOF

chmod +x 11_aggregation_patterns.sh
```

### Step 3: Add to CI Pipeline

```bash
# Update .github/workflows/ci.yaml
```

**Add to scenario list**:
```yaml
- name: Run Eval Scenario 11 - Aggregation Patterns
  run: bash evals/scripts/11_aggregation_patterns.sh
```

### Step 4: Update Eval Results Tracking

```bash
# Add to evals/RESULTS.md
cat >> evals/RESULTS.md <<'EOF'

### Scenario 11: Aggregation Patterns Without N+1

**Added**: 2025-11-01 (Sprint 3)
**Status**: ⏳ Pending first run
**Trigger**: Eval 04 failure analysis (N+1 queries in computed fields)

**Acceptance**:
- Module generates with read_group patterns
- No N+1 queries in computed fields
- assertQueryCount tests validate efficiency
- All tests pass

**History**:
- 2025-11-01: Created scenario after pattern extraction from eval 04 failure

EOF
```

---

## Phase 6: Validation & Deployment (20 minutes)

### Step 1: Run New Eval Locally

```bash
cd ~/ai-agency/agents/odoo-expertise/evals
bash scripts/11_aggregation_patterns.sh

# Expected:
# ✅ PASS: All aggregation patterns validated
# ✅ PASS: No N+1 queries detected
# ✅ PASS: Eval Scenario 11: COMPLETE
```

### Step 2: Commit Changes

```bash
cd ~/ai-agency/agents/odoo-expertise

git add knowledge/patterns/orm_library.md
git add knowledge/notes/$(date +%Y-%m-%d).md
git add knowledge/refs/sources.yaml
git add evals/scenarios/11_aggregation_patterns.md
git add evals/scripts/11_aggregation_patterns.sh
git add skills/odoo-module-dev/skill.yaml

git commit -m "feat(knowledge): Add aggregation pattern from eval 04 failure

- Pattern: read_group for aggregations without N+1
- Source: OCA sale-workflow reference implementation
- New eval scenario 11 for pattern validation
- Updated odoo-module-dev skill with guidelines
- Added citation and sources entry

Resolves: Eval 04 N+1 query failures
Impact: Prevents N+1 queries in future module generations

🤖 Generated with improvement workflow loop"
```

### Step 3: Push and Monitor CI

```bash
git push origin sprint3/docs

# Monitor GitHub Actions
# Should see new eval scenario 11 run and pass
```

---

## Continuous Improvement Metrics

### Weekly Review (Fridays, 30 minutes)

```bash
# Generate weekly report
cd ~/ai-agency/agents/odoo-expertise

echo "=== Weekly Improvement Report ==="
echo "Week of: $(date -v-7d +%Y-%m-%d) to $(date +%Y-%m-%d)"
echo ""

# Count new patterns added
echo "New Patterns:"
git log --since="7 days ago" --grep="feat(knowledge)" --oneline | wc -l

# Count eval scenarios added
echo "New Eval Scenarios:"
ls evals/scenarios/*.md | wc -l

# Current pass rate
echo "Current Eval Pass Rate:"
bash evals/scripts/run_all_scenarios.sh 2>&1 | grep "Pass Rate" | tail -1

# Knowledge base growth
echo "Citations Added This Week:"
find knowledge/notes -name "*.md" -mtime -7 | wc -l

# Skill updates
echo "Skill Updates:"
git log --since="7 days ago" --name-only -- skills/*.yaml | grep skill.yaml | sort -u

echo ""
echo "=== Action Items ==="
echo "- [ ] Review failing evals and create improvement tickets"
echo "- [ ] Update ORM library with new high-quality patterns"
echo "- [ ] Schedule deep research for gap areas"
```

### Monthly Metrics

Track these KPIs monthly:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Eval Pass Rate | ≥95% | `bash run_all_scenarios.sh` output |
| Knowledge Base Citations | +20/month | Count in `knowledge/notes/` |
| Pattern Library Entries | +3/month | Count in `orm_library.md` |
| Skills Updated | ≥1/month | Git history of `skills/` |
| Community Contributions | ≥2/month | GitHub PRs from external contributors |

---

## Community Contribution Workflow

### Accept External Pattern

```bash
# Review submitted pattern (e.g., via GitHub PR)
gh pr checkout 42

# Validate pattern quality
cline-odoo "Review this pattern for OCA compliance and quality:
[paste pattern code]

Evaluate:
1. OCA alignment (✅/❌)
2. Quality score (60-100)
3. Completeness (has example, test, documentation)
4. Conflicts with existing patterns"

# If approved, merge with attribution
git commit -m "feat(knowledge): Add [pattern name] (contributed by @username)"
```

### Share Pattern with OCA

```bash
# If pattern is novel and high-quality, share with OCA
gh repo clone OCA/odoo-community.org
cd odoo-community.org

# Create discussion or RFC
gh issue create --title "Pattern Proposal: [name]" --body "$(cat pattern_description.md)"
```

---

## Next Steps

- **Eval Failed?** Start with Phase 1: Eval Failure Analysis
- **Found New Pattern?** Jump to Phase 2: Pattern Extraction
- **Want to Contribute?** See Community Contribution Workflow
- **Track Progress?** Review Continuous Improvement Metrics

**Improvement Cycle Frequency**:
- **Daily**: Add citations as you discover patterns
- **Weekly**: Extract patterns from week's citations, update ORM library
- **Monthly**: Review metrics, create new eval scenarios, update skills

**Success Criteria**:
- Eval pass rate trending toward ≥95%
- Knowledge base growing organically (≥20 citations/month)
- Agent capabilities improving measurably (fewer manual interventions)
- Community engagement increasing (external contributions)

---

**Generated**: 2025-11-01
**Framework**: Cline CLI + DeepSeek API + Claude Code
**Loop Duration**: ~2 hours per significant pattern (analysis → extraction → deployment)

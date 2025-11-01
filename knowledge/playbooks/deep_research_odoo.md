# Deep Research Odoo - Automated Knowledge Gathering Playbook

**Purpose**: Systematic research automation for Odoo agent expertise using coordinated query strategies

**Integration**: Works with existing `~/.cline/skills/odoo/deep-research-oca/SKILL.md`

**Last Updated**: 2025-11-01

---

## Mandate

Pull practical, OCA-aligned guidance on:
- **Odoo Module Development** (versions 16, 17, 19)
- **Odoo Studio Operations** (safe patterns, export mechanisms)
- **Odoo.sh Lifecycle** (deployment, monitoring, backups)
- **Docker Images** (wkhtmltopdf, Anthropic SDK, production security)

---

## Research Strategy

### Phase 1: Discovery (2-5 minutes)
Parallel execution of targeted queries across multiple sources

### Phase 2: Analysis (5-10 minutes)
Pattern extraction, quality filtering, relevance scoring

### Phase 3: Synthesis (3-5 minutes)
Citation generation, knowledge base updates, playbook additions

**Total Time Budget**: <15 minutes per research session

---

## Query Sets

### Module Development Queries

#### OCA GitHub Searches
```bash
# Pre-commit and code quality
site:github.com/OCA pre-commit odoo 16.0
site:github.com/OCA "pytest-odoo" TransactionCase
site:github.com/OCA "@api.depends" computed field

# ORM patterns
site:github.com/OCA "record rule" domain multi-company
site:github.com/OCA "@api.constrains" validation
site:github.com/OCA "openupgradelib" migration

# Security patterns
site:github.com/OCA "ir.model.access" security
site:github.com/OCA record rules RLS performance
```

#### Stack Overflow Queries
```bash
# Odoo-specific searches (prefer 2023+)
site:stackoverflow.com [odoo] @api.depends computed field after:2023-01-01
site:stackoverflow.com [odoo] record rule N+1 performance after:2023-01-01
site:stackoverflow.com [odoo] pytest-odoo test coverage after:2023-01-01
```

#### Reddit r/odoo Queries
```bash
site:reddit.com/r/odoo OCA module best practices
site:reddit.com/r/odoo computed field cache
site:reddit.com/r/odoo record rule optimization
```

---

### Studio Operations Queries

#### Official Documentation
```bash
site:odoo.com "Studio" export XML JSON
site:odoo.com "Studio" server actions automations
site:odoo.com "Studio" field types constraints
```

#### Community Forums
```bash
site:odoo.com/forum "Studio" export rollback
site:odoo.com/forum "Studio" automated action
site:reddit.com/r/odoo Studio customization limits
```

---

### Odoo.sh DevOps Queries

#### Official Platform Documentation
```bash
site:odoo.sh features branch management
site:odoo.sh features staging deployment
site:odoo.sh features logs monitoring
site:odoo.sh features backups restore
```

#### Self-Hosted Parity
```bash
site:reddit.com/r/odoo self-hosted vs odoo.sh
site:reddit.com/r/odoo docker compose odoo production
site:reddit.com/r/odoo blue-green deployment odoo
```

---

### Docker + Claude SDK Queries

#### Docker Best Practices
```bash
site:reddit.com/r/odoo docker wkhtmltopdf fonts
site:reddit.com/r/odoo docker compose odoo postgres
site:stackoverflow.com [docker] [odoo] wkhtmltopdf rendering after:2023-01-01
site:stackoverflow.com [docker] [odoo] non-root user after:2023-01-01
```

#### Anthropic SDK Integration
```bash
"Anthropic Python SDK" docker non-root
"Anthropic Python SDK" environment variables secrets
site:docs.anthropic.com python sdk best practices
```

#### Production Security
```bash
site:reddit.com/r/docker multi-stage build python
site:stackoverflow.com [docker] secrets environment variables production
site:github.com docker security best practices
```

---

## Source Quality Scoring

### Scoring Matrix
```yaml
quality_score:
  official_odoo_docs: 100
  oca_maintainer_response: 95
  oca_repository_code: 90
  stackoverflow_accepted_20plus: 85
  reddit_10plus_upvotes_solved: 75
  stackoverflow_accepted_10_19: 70
  forum_official_response: 70
  reddit_5_9_upvotes: 60
  stackoverflow_no_accept_10plus: 50

recency_bonus:
  2025: +20
  2024: +15
  2023: +10
  2022: 0
  2021_older: -20

alignment_bonus:
  oca_compliant: +15
  self_hosted_focus: +10
  version_16_17_19: +10
  proprietary_only: -30
```

### Minimum Acceptance Thresholds
- **Total Score**: ≥60 (base + recency + alignment)
- **Recency**: Prefer 2023+ (exceptions: foundational patterns, migration guides)
- **OCA Alignment**: Must not contradict OCA guidelines
- **Completeness**: Must include working example or clear implementation path

---

## Citation Workflow

### Automated Citation Generation

For each qualifying source:

1. **Extract Information**:
   ```yaml
   title: [Brief descriptive title]
   link: [Full URL]
   date: [YYYY-MM-DD or Odoo version]
   source_type: [OCA/Reddit/Forum/StackOverflow/Official]
   quality_score: [Calculated score]
   takeaway: [1-2 line key insight]
   snippet: [≤2 lines code/quote]
   application: [skill1, skill2, ...]
   tags: [keyword1, keyword2, ...]
   ```

2. **Format as Markdown**:
   Use template from `knowledge/notes/citation_template.md`

3. **Add to Daily Note**:
   Append to `knowledge/notes/$(date +%Y-%m-%d).md`

4. **Update Playbook** (if pattern warrants):
   Add to relevant playbook in `knowledge/playbooks/`

---

## Example Research Session

### Session Goal
Research ORM computed field best practices for expense approval module

### Queries Executed (Parallel)
```bash
# GitHub
site:github.com/OCA "@api.depends" expense approval
site:github.com/OCA computed field performance cache

# Stack Overflow
site:stackoverflow.com [odoo] @api.depends stored computed after:2023-01-01

# Reddit
site:reddit.com/r/odoo computed field optimization
```

### Results Found
1. **OCA/account-financial-tools** - Invoice computed total with taxes
2. **Stack Overflow** - Stored vs non-stored performance comparison (25 upvotes)
3. **Reddit r/odoo** - Cache invalidation troubleshooting (12 upvotes)

### Citations Generated
```markdown
## OCA Pattern: Computed Field for Invoice Total

- **Link**: https://github.com/OCA/account-financial-tools/blob/16.0/account_invoice_total/models/invoice.py#L34-L42
- **Date/Version**: 2024-02-15, Odoo 16.0
- **Source Type**: OCA Repository
- **Quality Score**: 100 (official OCA + recent + aligned)
- **Takeaway**: Use @api.depends with full path for line items; store=True for frequently accessed totals
- **Snippet**: `@api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount')`
- **Application**: odoo-module-dev (ORM patterns)
- **Tags**: computed-field, api-depends, performance, invoicing

## Stack Overflow: Stored vs Non-Stored Performance

- **Link**: https://stackoverflow.com/questions/78345678/odoo-computed-field-performance
- **Date/Version**: 2024-03-20, Odoo 17.0
- **Source Type**: Stack Overflow (25 upvotes, accepted answer)
- **Quality Score**: 85 (high upvotes + accepted + recent)
- **Takeaway**: Use store=True for computed fields in list views or search domains; non-stored for rarely accessed calculations
- **Snippet**: Stored fields add DB overhead but save computation; benchmark with 1000+ records to decide
- **Application**: odoo-module-dev (performance optimization)
- **Tags**: computed-field, performance, stored, database

## Reddit: Computed Field Cache Invalidation

- **Link**: https://www.reddit.com/r/odoo/comments/xyz789/computed_field_not_updating/
- **Date/Version**: 2024-01-10
- **Source Type**: Reddit r/odoo (12 upvotes, solved)
- **Quality Score**: 75 (medium upvotes + solved + recent)
- **Takeaway**: Missing dependency in @api.depends causes cache not to invalidate; use self.env.cache.invalidate() for debugging
- **Snippet**: Add all related fields to @api.depends, including inverse relations like 'line_ids.field_name'
- **Application**: odoo-module-dev (debugging, cache)
- **Tags**: computed-field, cache, debugging, api-depends
```

### Playbook Updated
Added patterns to `knowledge/playbooks/orm_patterns.md`:
- Computed field dependency patterns
- Stored vs non-stored decision matrix
- Cache invalidation troubleshooting

---

## Integration with Existing Deep Research Skill

### Coordination Strategy

**Existing Skill** (`~/.cline/skills/odoo/deep-research-oca/SKILL.md`):
- Auto-crawls OCA GitHub, Reddit r/odoo, Odoo forums
- Provides research workflow and source access

**This Playbook** (`knowledge/playbooks/deep_research_odoo.md`):
- Defines specific query sets for each skill domain
- Provides quality scoring and citation workflows
- Feeds findings into structured knowledge base

**Workflow**:
1. Existing skill **executes** queries (WebSearch, WebFetch tools)
2. This playbook **guides** what to query and how to score results
3. Both **output** citations to `knowledge/notes/` in standard format

---

## Automation Scripts

### Daily Research Cron (Optional)

```bash
#!/bin/bash
# ~/ai-agency/agents/odoo-expertise/evals/scripts/daily_research.sh

DATE=$(date +%Y-%m-%d)
NOTE_FILE="$HOME/ai-agency/agents/odoo-expertise/knowledge/notes/${DATE}.md"

# Create daily note with header
cat > "$NOTE_FILE" <<EOF
# Daily Research Notes - ${DATE}

**Auto-generated research findings**

---

EOF

# Trigger deep research skill with today's focus
# (This would invoke Cline with deep-research-oca skill)

echo "Daily research complete. Results in: $NOTE_FILE"
```

---

## Quality Assurance

### Validation Checklist

After each research session:
- [ ] All citations follow template format
- [ ] Quality scores calculated correctly
- [ ] Sources are recent (prefer 2023+)
- [ ] OCA alignment verified (no contradictions)
- [ ] Takeaways are actionable (not just descriptions)
- [ ] Snippets provide concrete examples
- [ ] Applications tagged to correct skills
- [ ] Daily note updated with new citations

### Coverage Targets

By Sprint 4 completion:
- **Total Citations**: ≥20 high-quality sources
- **Per-Skill Coverage**: ≥5 citations each for odoo-module-dev, odoo-studio-ops, odoo-sh-devops, odoo-docker-claude
- **OCA Repository Citations**: ≥8 (primary source for module dev)
- **Community Citations**: ≥6 (Reddit/Forums for real-world patterns)
- **Official Docs Citations**: ≥6 (Studio, Odoo.sh, API reference)

---

## Troubleshooting

### Common Issues

**Issue**: Too many low-quality results
**Solution**: Increase quality score threshold, add more specific keywords, use date filters

**Issue**: Contradictory advice from different sources
**Solution**: Prioritize OCA guidelines > official docs > high-upvote community, document trade-offs

**Issue**: Outdated information (pre-2023)
**Solution**: Use as historical context only, search for version-specific updates, mark as deprecated if superseded

**Issue**: No results for specific query
**Solution**: Broaden keywords, search adjacent topics, check if feature is version-specific

---

## Next Steps

1. **Execute First Research Session**: Focus on ORM patterns for module development
2. **Generate 5 Initial Citations**: Seed knowledge base with high-quality sources
3. **Update Playbooks**: Add validated patterns to `orm_patterns.md`
4. **Automate Daily Research**: Set up cron or manual daily workflow
5. **Iterate on Quality**: Refine scoring matrix based on practical usefulness

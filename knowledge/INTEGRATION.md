# Deep-Research Playbook Integration

Integration documentation for automated research with existing `deep-research-oca` skill.

## Overview

The deep-research playbook automation system consists of two components that work together:

1. **Existing Skill**: `~/.cline/skills/odoo/deep-research-oca/SKILL.md`
   - Provides research workflow framework
   - Defines source access patterns
   - Auto-activates on research keywords

2. **New Automation**: `knowledge/scripts/` (this implementation)
   - Executable Python/Bash scripts
   - Automated query execution
   - Citation generation and quality scoring
   - Daily scheduling capability

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Cline User Request                                          │
│ "Research OCA computed field patterns"                      │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│ Deep-Research-OCA Skill (Auto-Activation)                   │
│ ~/.cline/skills/odoo/deep-research-oca/SKILL.md             │
│                                                              │
│ - Detects research intent                                   │
│ - Provides research workflow guidance                       │
│ - Uses WebSearch/WebFetch tools                             │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│ Automation Scripts (Execution)                              │
│ knowledge/scripts/auto_research.py                          │
│                                                              │
│ - GitHub API: OCA code patterns                             │
│ - Reddit API: Community solutions                           │
│ - Stack Overflow API: Q&A search                            │
│ - Quality scoring (0-120 scale)                             │
│ - Citation formatting                                       │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│ Knowledge Base Updates                                      │
│ knowledge/notes/YYYY-MM-DD.md                               │
│                                                              │
│ - Daily research notes                                      │
│ - Structured citations                                      │
│ - Quality scores                                            │
│ - Searchable tags                                           │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│ Future Research Sessions                                    │
│                                                              │
│ - Skill references cached citations                         │
│ - Avoids duplicate queries                                  │
│ - Builds on prior knowledge                                 │
└─────────────────────────────────────────────────────────────┘
```

## Integration Points

### 1. Skill-Triggered Research

**Scenario**: User asks Cline for OCA guidance

```
User: "What's the best pattern for computed fields in Odoo?"

Cline: [Auto-activates deep-research-oca skill]
       [Executes automation scripts]
       [Returns citations + summary]
```

**Workflow**:
1. Skill detects research keywords
2. Skill invokes `auto_research.py` via Bash tool
3. Script queries OCA GitHub, Reddit, Stack Overflow
4. Citations saved to `knowledge/notes/YYYY-MM-DD.md`
5. Skill presents findings to user

### 2. Scheduled Research

**Scenario**: Daily automated knowledge gathering

```bash
# Cron job (daily at 2 AM UTC)
0 2 * * * /path/to/research_scheduler.sh
```

**Workflow**:
1. Scheduler determines daily domain (rotating schedule)
2. Executes `auto_research.py` for domain
3. Citations saved to daily note
4. Weekly summary generated on Sundays
5. Knowledge base grows organically

### 3. Manual Research

**Scenario**: Developer runs ad-hoc research

```bash
# Specific domain focus
python3 knowledge/scripts/auto_research.py --domain docker --max-results 10

# Test mode (no SO to avoid rate limits)
python3 knowledge/scripts/auto_research.py --test-mode
```

**Workflow**:
1. Direct script execution
2. Citations generated immediately
3. Knowledge base updated
4. Available for next Cline session

## Query Coordination

### Skill Queries (WebSearch/WebFetch)

From `~/.cline/skills/odoo/deep-research-oca/SKILL.md`:

```bash
# Example: User asks about ORM performance
WebSearch: "site:github.com/OCA search_count optimization"
WebFetch: https://github.com/OCA/server-tools/path/to/file.py
```

**Characteristics**:
- Real-time queries during Cline session
- Uses Cline's WebSearch/WebFetch tools
- Interactive result presentation
- Immediate user feedback

### Automation Queries (API Calls)

From `knowledge/scripts/auto_research.py`:

```python
# GitHub API
GET /search/code?q=org:OCA+computed+field

# Reddit JSON API
GET /r/odoo/search.json?q=ORM+performance

# Stack Overflow API
GET /search/advanced?tagged=odoo&q=computed+field
```

**Characteristics**:
- Batch queries (parallel execution)
- API-based (structured responses)
- Quality scoring and filtering
- Persistent storage

### Query Deduplication

**Strategy**: Both systems write to same daily note

```markdown
# knowledge/notes/2025-11-01.md

## [Skill-generated citation at 09:00]
...

## [Automation-generated citation at 02:00]
...
```

**Benefits**:
- Single source of truth
- No duplicate citations (URLs checked)
- Chronological research log
- Skill can reference automation findings

## Quality Scoring Integration

### Automation Scoring

From `auto_research.py`:

```python
quality_score = base_score + recency_bonus + alignment_bonus

# Example: OCA repository code from 2024
base_score = 90         # OCA repository
recency = +15           # 2024
alignment = +15         # OCA compliant
total = 120             # Excellent quality
```

**Threshold**: ≥60 for inclusion in citations

### Skill Consumption

When skill references citations:

```markdown
## High-Quality Sources (Score ≥100)
- [OCA Pattern: computed field] (Score: 120)
- [Official Docs: API Reference] (Score: 100)

## Community Solutions (Score 70-99)
- [Reddit: Cache invalidation] (Score: 75)
- [Stack Overflow: N+1 queries] (Score: 85)
```

**Benefit**: Skill prioritizes highest-quality sources

## Citation Format Compliance

Both systems follow `knowledge/notes/citation_template.md`:

### Automation Output

```markdown
## OCA Pattern: Computed Field with @api.depends

- **Link**: https://github.com/OCA/server-tools/blob/...
- **Date/Version**: 2024-03-12, Odoo 16.0
- **Source Type**: OCA Repository
- **Quality Score**: 120
- **Takeaway**: Use @api.depends with full path for cache invalidation
- **Snippet**: `@api.depends('line_ids.product_id', 'line_ids.quantity')`
- **Application**: odoo-module-dev
- **Tags**: computed-field, api-depends, cache-invalidation, oca
```

### Skill Output

Same format, ensuring:
- Consistent citation structure
- Searchable metadata
- Quality scores visible
- Applications tagged correctly

## Search and Discovery

### Finding Citations by Skill

```bash
# Find all odoo-module-dev citations
grep -r "Application: odoo-module-dev" knowledge/notes/

# Find computed field patterns
grep -r "Tags:.*computed-field" knowledge/notes/

# Find high-quality sources (score ≥100)
grep -r "Quality Score: 1[0-2][0-9]" knowledge/notes/
```

### Skill Consumption

Skill can search citations during research:

```bash
# Within Cline session
Read: knowledge/notes/2025-11-01.md
Grep: "Application: odoo-docker-claude" in knowledge/notes/*.md
```

**Benefit**: Build on prior research, avoid duplication

## Daily Workflow Example

### Morning Research (Automated)

```
02:00 UTC - Cron triggers research_scheduler.sh
02:01 UTC - Domain: module_dev (Monday)
02:02 UTC - Query: OCA @api.depends patterns
02:03 UTC - Query: Reddit computed field cache
02:04 UTC - Query: Stack Overflow ORM performance
02:05 UTC - Quality filtering (≥60 score)
02:06 UTC - Generate 8 citations
02:07 UTC - Save to knowledge/notes/2025-11-01.md
```

**Result**: 8 fresh citations ready for Cline sessions

### User Session (Interactive)

```
10:00 UTC - User asks: "Best practice for computed fields?"
10:00 UTC - Cline activates deep-research-oca skill
10:01 UTC - Skill reads knowledge/notes/2025-11-01.md
10:01 UTC - Skill finds 3 relevant citations (automation-generated)
10:02 UTC - Skill executes supplementary WebSearch (real-time)
10:03 UTC - Skill presents combined findings
10:04 UTC - User gets comprehensive answer (automation + real-time)
```

**Result**: Fast response with depth (cached + fresh)

## Weekly Summary Integration

### Sunday Automation

From `research_scheduler.sh`:

```bash
# Generate weekly summary
knowledge/notes/weekly-summary-2025-11-01.md

## This Week's Research

### 2025-10-26
- **Citations**: 6
- **File**: knowledge/notes/2025-10-26.md

### 2025-10-27
- **Citations**: 8
- **File**: knowledge/notes/2025-10-27.md

...

## Next Week's Focus
- [ ] OCA repository patterns (target: ≥8 citations)
- [ ] Community solutions (target: ≥6 citations)
```

### Skill Consumption

Skill references weekly summary for:
- Coverage gap analysis
- Research focus planning
- Citation quality trends

## Performance Characteristics

### Automation Performance

**Research Session**:
- Discovery: 2-5 minutes (parallel queries)
- Analysis: 1-2 minutes (quality scoring)
- Citation generation: <1 minute
- **Total**: <10 minutes per session

**API Rate Limits**:
- GitHub (authenticated): 5000/hour (GITHUB_TOKEN required)
- Reddit: 60/minute
- Stack Overflow: 300/day

### Skill Performance

**Interactive Research**:
- Query: <5 seconds (WebSearch/WebFetch)
- Citation read: <1 second (Read tool)
- Presentation: Real-time

**Cache Hit Benefits**:
- Cached citation: <1 second
- Fresh research: 10-30 seconds
- **Speedup**: 10-30x faster with cache

## Error Handling

### Automation Errors

**GitHub API Rate Limit**:
```python
# Fallback: Use cached results
logger.warning("GitHub rate limit - using cached citations")
```

**Reddit Timeout**:
```python
# Continue with partial results
logger.error("Reddit timeout - skipping Reddit sources")
```

**Minimum Citation Threshold**:
```python
if len(citations) < 5:
    logger.warning("Below 5 citations - consider broadening search")
    return 1  # Non-zero exit code
```

### Skill Error Recovery

**No Cached Citations**:
```
Skill: No cached citations found
Action: Execute real-time WebSearch
Fallback: Manual research guidance
```

**Invalid Citation Format**:
```
Skill: Citation parsing failed
Action: Skip malformed citation
Continue: Process remaining citations
```

## Configuration

### Environment Variables

Both systems use same configuration:

```bash
# Required for authenticated GitHub API
export GITHUB_TOKEN=ghp_your_token_here

# Optional: Custom output directory
export RESEARCH_OUTPUT_DIR=/path/to/custom/notes/

# Optional: Custom quality threshold
export MIN_QUALITY_SCORE=60
```

### Skill Configuration

In `~/.cline/skills/odoo/deep-research-oca/SKILL.md`:

```yaml
allowed-tools: [WebFetch, WebSearch, Bash, Read, Write, Grep]
```

**Integration**: Skill can invoke automation scripts via Bash tool

### Automation Configuration

In `knowledge/scripts/auto_research.py`:

```python
# Customizable queries
QUERIES = {
    'module_dev': {
        'oca': [...],
        'reddit': [...],
        'stackoverflow': [...]
    }
}

# Customizable scoring
MIN_ACCEPTABLE_SCORE = 60
```

## Testing Integration

### Test Automation

```bash
# Test citation generation
python3 knowledge/scripts/auto_research.py --test-mode

# Expected: ≥5 citations, exact template format
```

### Test Skill

```
User: "Use deep-research-oca skill to find ORM patterns"

Expected:
1. Skill activates
2. Reads cached citations from knowledge/notes/
3. Executes supplementary searches if needed
4. Presents combined findings
```

### Test End-to-End

```bash
# 1. Run automation
./knowledge/scripts/research_scheduler.sh --test

# 2. Verify citations
ls -la knowledge/notes/2025-11-01.md

# 3. Invoke Cline with skill
cline --skill deep-research-oca "Find computed field patterns"

# 4. Verify skill reads automation citations
# Should see: "Found 6 cached citations from 2025-11-01"
```

## Troubleshooting

### Issue: Skill Not Finding Automation Citations

**Symptom**: Skill executes fresh research instead of using cached

**Solution**:
1. Verify citations in `knowledge/notes/YYYY-MM-DD.md`
2. Check citation format matches template exactly
3. Ensure skill has Read tool access
4. Verify file permissions (readable)

### Issue: Duplicate Citations

**Symptom**: Same source appears multiple times

**Solution**:
1. Automation checks URLs before adding
2. Skill should deduplicate on URL match
3. Manual cleanup: grep for duplicate URLs

### Issue: Automation Generates <5 Citations

**Symptom**: Quality filtering too aggressive

**Solution**:
1. Lower `MIN_QUALITY_SCORE` threshold
2. Increase `--max-results` parameter
3. Broaden search queries
4. Check GitHub token (rate limits)

## Best Practices

### For Automation

1. **Run daily**: Consistent knowledge growth
2. **Rotate domains**: Balanced coverage
3. **Monitor quality**: Review weekly summaries
4. **Tune queries**: Add domain-specific searches

### For Skill Usage

1. **Check cache first**: Read daily notes before fresh research
2. **Supplement gaps**: Execute WebSearch for missing areas
3. **Update automation**: Add new query patterns discovered
4. **Maintain quality**: Report low-quality citations

### For Knowledge Base

1. **Review citations**: Monthly quality audit
2. **Update outdated**: Mark deprecated patterns
3. **Cross-reference**: Link related citations
4. **Organize**: Create playbook sections from patterns

## Future Enhancements

### Planned Improvements

1. **ML Ranking**: Train model on successful patterns
2. **Auto-Tagging**: NLP-based tag generation
3. **Conflict Detection**: Identify contradictory advice
4. **Pattern Library**: Curated collection of verified patterns
5. **Runbot Integration**: Monitor OCA module compatibility
6. **Video Indexing**: Search Odoo YouTube tutorials

### Integration Roadmap

**Sprint 3**: ML-based quality prediction
**Sprint 4**: Conflict detection and resolution
**Sprint 5**: Pattern library with code examples
**Sprint 6**: Runbot and video integration

## Metrics and KPIs

### Coverage Targets (Sprint 4)

- **Total Citations**: ≥20 high-quality
- **Per-Skill Coverage**: ≥5 each (module-dev, studio, sh, docker)
- **OCA Citations**: ≥8 (primary source)
- **Community Citations**: ≥6 (real-world patterns)
- **Official Docs**: ≥6 (Studio, Odoo.sh, API)

### Quality Metrics

- **Average Score**: ≥80 (high-quality sources)
- **OCA Alignment**: ≥70% (OCA-compliant patterns)
- **Recency**: ≥60% from 2023+ (current practices)
- **Completeness**: ≥90% with working snippets

### Performance Metrics

- **Research Time**: <10 min per session
- **Cache Hit Rate**: ≥60% for common queries
- **API Success Rate**: ≥95% (robust error handling)
- **Citation Accuracy**: ≥90% (manual audit)

## Support and Documentation

**Primary Documentation**:
- `knowledge/playbooks/deep_research_odoo.md` - Query sets, quality scoring
- `knowledge/notes/citation_template.md` - Citation format
- `knowledge/scripts/README.md` - Script usage
- `~/.cline/skills/odoo/deep-research-oca/SKILL.md` - Skill reference

**Issue Reporting**: Sprint branch (sprint2/skills)

**Questions**: See troubleshooting section or consult playbook

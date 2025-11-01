# Research Coordination

**Purpose**: Coordinate `knowledge/scripts/auto_research.py` with existing `~/.cline/skills/odoo/deep-research-oca/`

**Goal**: Complementary automation, not duplication

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  ~/.cline/skills/odoo/deep-research-oca/SKILL.md          │
│  ────────────────────────────────────────────────────────  │
│  Purpose: Interactive research workflow specification       │
│  Output: Research summaries, code patterns, solutions       │
│  Cache: ~/.cline/research/*.md                             │
│  Activation: Manual deep-dive, complex investigations      │
└─────────────────────────────────────────────────────────────┘
                              ↓ Implements
┌─────────────────────────────────────────────────────────────┐
│  knowledge/scripts/auto_research.py                         │
│  ────────────────────────────────────────────────────────  │
│  Purpose: Automated daily research implementation           │
│  Output: Structured citations in knowledge/notes/*.md       │
│  Quality: Scoring algorithm + citation template validation │
│  Activation: Cron jobs, CI/CD, pre-development research    │
└─────────────────────────────────────────────────────────────┘
```

---

## Relationship Specification

### Deep Research Skill (Specification)

**Role**: Defines what to research and how to structure findings

**Key Elements**:
- **Sources**: OCA GitHub, Reddit r/odoo, Odoo Forums, Official Docs, Stack Overflow
- **Workflow**: 3-phase process (Discovery → Analysis → Synthesis)
- **Output Format**: YAML research results with patterns, solutions, recommendations
- **Performance Targets**: <10 minutes total research time

**Example Output Structure** (from SKILL.md):
```yaml
research_results:
  query: "Original user question"
  oca_patterns:
    - module: "OCA/module-name"
      pattern: "Code pattern description"
      code_sample: |
        Working example code
      url: "https://github.com/OCA/..."
  community_solutions:
    - source: "Reddit r/odoo"
      solution: "Description"
  official_docs:
    - topic: "API Reference"
      content: "Documentation excerpt"
  recommendations:
    primary: "Use OCA module X"
    warnings: ["Gotcha 1", "Gotcha 2"]
  confidence_score: 0.92
```

---

### Auto Research Script (Implementation)

**Role**: Automates skill workflow with quality scoring and citation formatting

**Key Enhancements**:
- **Quality Scoring**: 0-100 scale with recency/alignment bonuses (lines 32-108)
- **Citation Formatting**: Structured markdown following `citation_template.md` (lines 301-338)
- **Daily Automation**: Auto-save to `knowledge/notes/YYYY-MM-DD.md` (lines 514-542)
- **Filtering**: Only citations with score ≥60 included (line 64)

**Example Output** (formatted citation):
```markdown
## OCA Pattern: hr_expense.py

- **Link**: https://github.com/OCA/hr-expense/blob/16.0/hr_expense/models/hr_expense.py
- **Date/Version**: 2024-11-15
- **Source Type**: OCA Repository Code
- **Quality Score**: 95
- **Takeaway**: OCA pattern from OCA/hr-expense - review code for implementation details
- **Snippet**:
  @api.depends('amount', 'tax_ids')
  def _compute_total_with_tax(self):
- **Application**: odoo-module-dev
- **Tags**: computed-field, api-depends, oca
```

---

## Query Set Coordination

### Complementary, Not Duplicative

**Strategy**: auto_research.py queries are **subsets** of deep-research-oca sources

**Query Mapping**:

| Deep Research Source | Auto Research Implementation | Relationship |
|---------------------|------------------------------|--------------|
| OCA GitHub (search repos, code, PRs) | `OCAGitHubCrawler.search_code()` | Implements code search only |
| Reddit r/odoo | `RedditCrawler.search()` | Implements JSON API queries |
| Stack Overflow [odoo] tag | `StackOverflowCrawler.search()` | Implements API v2.3 queries |
| Odoo Forums | ❌ Not implemented yet | Future enhancement |
| Odoo Documentation | ❌ Not implemented yet | Future enhancement |

**Why Not 100% Coverage?**
- Forums and official docs require HTML scraping (complex)
- Focus on high-ROI sources first (OCA, Reddit, SO provide 80% of value)
- Deep-research-oca workflow used for manual forum/doc exploration

---

### Query Set Details

#### Module Development Queries

**Deep Research Skill Defines**:
```bash
# OCA GitHub queries (from SKILL.md lines 68-69)
gh search code --repo OCA/account-financial-tools "def _compute" --limit 50

# Reddit queries
site:reddit.com/r/odoo ORM performance
site:reddit.com/r/odoo custom module tutorial
```

**Auto Research Implements**:
```python
# queries from auto_research.py lines 358-372
'module_dev': {
    'oca': [
        '@api.depends computed field',
        'record rule domain multi-company',
        'pytest-odoo TransactionCase',
    ],
    'reddit': [
        'OCA module best practices',
        'computed field cache',
    ],
    'stackoverflow': [
        '@api.depends computed field',
        'record rule performance',
    ],
}
```

**Coordination**:
- ✅ Query topics match (computed fields, record rules, testing)
- ✅ Auto research uses simpler query syntax (no bash commands)
- ✅ Auto research adds quality filtering (min upvotes, score ≥60)

---

#### Docker Queries

**Deep Research Skill Defines**:
```bash
# Reddit queries for Docker issues
site:reddit.com/r/odoo docker wkhtmltopdf fonts
site:reddit.com/r/odoo docker compose odoo postgres
```

**Auto Research Implements**:
```python
# queries from auto_research.py lines 373-383
'docker': {
    'reddit': [
        'docker wkhtmltopdf fonts',
        'docker compose odoo postgres',
    ],
    'stackoverflow': [
        'docker odoo wkhtmltopdf',
        'docker odoo non-root',
    ],
}
```

**Coordination**:
- ✅ Query topics match (wkhtmltopdf, docker-compose)
- ✅ Auto research adds Stack Overflow for additional coverage
- ✅ Queries complementary (Reddit for community, SO for technical solutions)

---

## Citation Format Validation

### Shared Format Requirements

**Deep Research Skill Specifies** (SKILL.md lines 220-250):
```yaml
research_results:
  oca_patterns:
    - module: "OCA/module-name"
      pattern: "Code pattern description"
      code_sample: |
        Working code
      url: "https://github.com/OCA/..."
  community_solutions:
    - source: "Reddit r/odoo"
      author: "u/username"
      solution: "Description"
      upvotes: 42
      url: "https://reddit.com/..."
```

**Auto Research Implements** (auto_research.py lines 305-338):
```markdown
## {title}

- **Link**: {url}
- **Date/Version**: {date}
- **Source Type**: {source_type}
- **Quality Score**: {score}
- **Takeaway**: {takeaway}
- **Snippet**: {snippet}
- **Application**: {application}
- **Tags**: {tags}
```

**Validation**:
- ✅ Both require URL reference
- ✅ Both include source type identification
- ✅ Both capture code snippets/patterns
- ⚠️ Different output formats (YAML vs Markdown)
  - **Resolution**: Markdown better for knowledge base notes
  - **Justification**: Human-readable, integrates with Obsidian/Notion

---

### Citation Quality Scoring

**Auto Research Enhancement** (not in deep-research-oca):

**Quality Scores** (lines 36-46):
```python
QUALITY_SCORES = {
    'official_odoo_docs': 100,
    'oca_maintainer_response': 95,
    'oca_repository_code': 90,
    'stackoverflow_accepted_20plus': 85,
    'reddit_10plus_upvotes_solved': 75,
    'stackoverflow_accepted_10_19': 70,
    'forum_official_response': 70,
    'reddit_5_9_upvotes': 60,
    'stackoverflow_no_accept_10plus': 50,
}
```

**Recency Bonus** (lines 49-54):
```python
RECENCY_BONUS = {
    2025: 20,
    2024: 15,
    2023: 10,
    2022: 0,
}
```

**Alignment Bonus** (lines 57-62):
```python
ALIGNMENT_BONUS = {
    'oca_compliant': 15,
    'self_hosted_focus': 10,
    'version_16_17_19': 10,
    'proprietary_only': -30,
}
```

**Filtering** (line 64):
```python
MIN_ACCEPTABLE_SCORE = 60  # Only citations ≥60 included in daily notes
```

**Why This Matters**:
- Prevents low-quality sources from polluting knowledge base
- Prioritizes OCA-aligned, recent, well-validated solutions
- Systematic vs subjective quality assessment

---

## When to Use Which

### Use Deep-Research-Oca Skill (Manual) When:

✅ **Interactive Exploration**
- User asks "How do I implement X in Odoo?"
- Need to explore multiple approaches
- Uncertain about best pattern
- Learning/understanding phase

✅ **Complex Problem Solving**
- Multi-component architectural decisions
- Integration pattern selection
- Performance optimization strategies
- Security threat modeling

✅ **Odoo Forums + Official Docs**
- Need official Odoo responses
- Checking for known bugs in forums
- Reading API documentation
- Migration guides for version upgrades

**Workflow**: Manual activation → 3-phase research → Interactive synthesis

---

### Use Auto Research Script (Automated) When:

✅ **Daily Knowledge Updates**
- Cron job every morning: `0 9 * * * python knowledge/scripts/auto_research.py`
- Keep knowledge base current with latest patterns
- Discover new OCA modules and community solutions

✅ **Pre-Development Research**
- CI/CD step before feature development
- Validate chosen pattern still best practice
- Check for recent OCA updates

✅ **Domain-Specific Investigations**
```bash
# Focused research on specific domain
python auto_research.py --domain module_dev --max-results 10
python auto_research.py --domain docker --test-mode
```

✅ **Quality-Filtered Citations**
- Only want high-quality sources (score ≥60)
- Need structured citations for documentation
- Building knowledge base systematically

**Workflow**: Automated execution → Quality filtering → Daily note generation

---

## Integration Workflow

### Combined Usage Example

**Scenario**: Building OCA-compliant expense approval module

**Step 1: Daily Automation (Auto Research)**
```bash
# Run at 9 AM daily
python knowledge/scripts/auto_research.py --domain module_dev --max-results 10

# Output: knowledge/notes/2025-11-01.md
# Contains 8 high-quality citations (score ≥60) on:
# - @api.depends patterns
# - Record rule examples
# - pytest-odoo test patterns
```

**Step 2: Manual Deep-Dive (Deep Research Skill)**
```
User: "How do I implement multi-level approval workflow in Odoo?"

Claude activates deep-research-oca skill:
1. Search OCA/purchase-workflow for approval patterns
2. Check Reddit r/odoo for community implementations
3. Review Odoo forums for official guidance
4. Synthesize findings with confidence score

Output: Comprehensive research summary with:
- 3 OCA module recommendations
- 5 community solutions from Reddit
- 2 official forum responses
- Confidence: 0.92
```

**Step 3: Implementation (Using Both)**
```
1. Review auto_research daily notes for recent patterns
2. Use deep-research findings for architectural decisions
3. Generate module using odoo-module-dev skill
4. Test with patterns from both sources
```

---

## Validation Checklist

Ensure auto_research.py coordinates properly with deep-research-oca:

- [x] Query sets are complementary (not duplicative)
  - ✅ Auto research uses subset of deep-research sources
  - ✅ Queries focus on high-ROI topics (OCA patterns, common issues)

- [x] Citation format is validated
  - ✅ Both reference URLs, source types, code snippets
  - ⚠️ Different formats (YAML vs Markdown) - justified for use case

- [x] Quality scoring is systematic
  - ✅ Auto research implements scoring algorithm (60+ threshold)
  - ✅ Deep research uses confidence score (0.0-1.0)

- [x] Output locations don't conflict
  - ✅ Deep research: `~/.cline/research/*.md`
  - ✅ Auto research: `knowledge/notes/YYYY-MM-DD.md`

- [x] Tools reference each other
  - ✅ odoo-module-dev skill.yaml references deep-research-oca
  - ✅ auto_research.py docstring references existing skill

---

## Future Enhancements

### Planned Improvements

**1. Odoo Forums Integration**
```python
class OdooForumCrawler:
    """Scrape Odoo forums for official responses"""
    BASE_URL = "https://www.odoo.com/forum"

    def search(self, query: str) -> List[Dict]:
        # HTML scraping with BeautifulSoup
        # Extract questions, answers, official responses
        # Quality score based on official badge
```

**2. Official Documentation Integration**
```python
class OdooDocsCrawler:
    """Fetch Odoo official documentation"""
    BASE_URL = "https://www.odoo.com/documentation/"

    def get_api_reference(self, model: str, version: str) -> str:
        # Fetch API docs for specific model
        # Extract method signatures, examples
```

**3. Machine Learning Ranking**
```python
class MLRanker:
    """Learn from successful vs failed pattern usage"""

    def train_on_outcomes(self, citations: List[Dict], outcomes: List[bool]):
        # Train model on which citations led to successful implementations
        # Adjust quality scores based on real-world effectiveness
```

**4. Automatic Update Alerts**
```python
class ResearchMonitor:
    """Monitor for outdated cached research"""

    def check_freshness(self, note_path: Path) -> bool:
        # Check if citations >7 days old
        # Alert if Odoo version changed
        # Suggest re-research
```

---

## Troubleshooting

### Issue: Duplicate Citations

**Symptom**: Same pattern appears in both manual and automated research

**Resolution**:
1. Check query overlap between deep-research-oca and auto_research.py
2. Ensure auto_research uses distinct query phrasing
3. Add de-duplication logic based on URL matching

**Example Fix**:
```python
def deduplicate_by_url(citations: List[Dict]) -> List[Dict]:
    """Remove duplicate citations based on URL"""
    seen_urls = set()
    unique = []
    for citation in citations:
        if citation['url'] not in seen_urls:
            unique.append(citation)
            seen_urls.add(citation['url'])
    return unique
```

---

### Issue: Low Citation Count

**Symptom**: `auto_research.py` generates <5 citations (warning threshold)

**Diagnosis**:
```bash
# Check if quality threshold too strict
python auto_research.py --test-mode --domain module_dev

# Review score distribution
# If many results scored 50-59 (below threshold), consider lowering to 55
```

**Resolution**:
1. Lower `MIN_ACCEPTABLE_SCORE` from 60 to 55
2. Broaden search queries (e.g., "@api.depends" → "computed field")
3. Increase `--max-results` parameter

---

### Issue: Citation Format Inconsistency

**Symptom**: Markdown citations don't match expected template

**Validation**:
```bash
# Check citation format against template
grep -E "^- \*\*Link\*\*:" knowledge/notes/2025-11-01.md
grep -E "^- \*\*Quality Score\*\*:" knowledge/notes/2025-11-01.md

# Should find consistent format across all citations
```

**Resolution**:
1. Review `CitationFormatter.format()` method (lines 305-338)
2. Ensure all required fields present: Link, Date, Source Type, Quality Score, Takeaway, Snippet, Application, Tags
3. Validate with test case

---

## Conclusion

**Integration Summary**:
- ✅ **Deep-research-oca**: Specification for manual interactive research
- ✅ **auto_research.py**: Automated implementation with quality scoring
- ✅ **Complementary**: Different use cases, non-overlapping outputs
- ✅ **Validated**: Query coordination, citation format, quality thresholds

**Recommendation**:
- Use **deep-research-oca** for complex problem-solving and manual exploration
- Use **auto_research.py** for daily knowledge updates and CI/CD integration
- Combine both for comprehensive research coverage
- Reference this document for coordination details

**Next Steps**:
1. Run auto_research.py daily to build knowledge base
2. Use deep-research-oca for manual deep-dives
3. Validate citation quality scores match expectations
4. Monitor for duplicate citations
5. Plan Odoo Forums and Official Docs integration

**Questions**: See `knowledge/scripts/auto_research.py` for implementation details

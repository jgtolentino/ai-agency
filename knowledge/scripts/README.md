# Research Automation Scripts

Automated knowledge gathering for Odoo expertise skills.

## Overview

This directory contains automation scripts for the deep-research playbook that auto-crawl OCA GitHub, Reddit r/odoo, and Odoo forums to feed knowledge into Cline's context.

## Scripts

### `auto_research.py`

**Purpose**: Core research automation engine

**Features**:
- OCA GitHub code search via GitHub API
- Reddit r/odoo community solutions
- Stack Overflow [odoo] tag search
- Quality scoring (0-120 scale)
- Automatic citation generation
- Citation template compliance

**Usage**:
```bash
# Basic usage
python3 auto_research.py

# Test mode (limited queries, no SO to avoid rate limits)
python3 auto_research.py --test-mode

# Specific domain focus
python3 auto_research.py --domain docker --max-results 10

# Custom output directory
python3 auto_research.py --output /path/to/custom/notes/
```

**Options**:
- `--test-mode`: Run in test mode (limited queries)
- `--domain {module_dev,docker,studio,odoo_sh}`: Research domain
- `--max-results N`: Maximum results per query (default: 5)
- `--output PATH`: Output directory for daily notes

**Requirements**:
```bash
pip3 install requests pyyaml
export GITHUB_TOKEN=your_token_here  # Optional but recommended
```

**Output**: Citations in `knowledge/notes/YYYY-MM-DD.md`

---

### `research_scheduler.sh`

**Purpose**: Cron-compatible daily research automation

**Features**:
- Daily research execution
- Rotating domain schedule (Mon-Sun)
- Dependency checking
- Weekly summary generation
- Log rotation (30-day retention)
- Integration with deep-research-oca skill

**Usage**:
```bash
# Manual execution
./research_scheduler.sh

# Test mode
./research_scheduler.sh --test

# Cron setup (daily at 2 AM UTC)
crontab -e
# Add:
0 2 * * * /path/to/research_scheduler.sh >> /var/log/odoo-research.log 2>&1
```

**Domain Rotation Schedule**:
- Monday: module_dev
- Tuesday: docker
- Wednesday: module_dev
- Thursday: studio
- Friday: module_dev
- Saturday: odoo_sh
- Sunday: module_dev + weekly summary

**Requirements**:
- Bash 4.0+
- Python 3.6+
- requests, pyyaml packages
- GitHub token (optional)

**Output**:
- Daily notes: `knowledge/notes/YYYY-MM-DD.md`
- Weekly summaries: `knowledge/notes/weekly-summary-YYYY-MM-DD.md`
- Logs: `/tmp/odoo-research-YYYYMMDD.log` (30-day retention)

---

## Quality Scoring

All citations are scored using the quality matrix from `playbooks/deep_research_odoo.md`:

**Base Scores**:
- Official Odoo docs: 100
- OCA maintainer response: 95
- OCA repository code: 90
- Stack Overflow (20+ upvotes, accepted): 85
- Reddit (10+ upvotes, solved): 75
- Forum (official response): 70

**Recency Bonus**:
- 2025: +20
- 2024: +15
- 2023: +10
- 2022: 0
- 2021 or older: -20

**Alignment Bonus**:
- OCA compliant: +15
- Self-hosted focus: +10
- Version 16/17/19: +10
- Proprietary only: -30

**Minimum Acceptable**: ≥60 total score

---

## Citation Format

All citations follow the template in `notes/citation_template.md`:

```markdown
## [Title - Brief description]

- **Link**: [Full URL]
- **Date/Version**: [YYYY-MM-DD or Odoo version]
- **Source Type**: [OCA Repository / Reddit / Forum / Stack Overflow / Official Docs]
- **Quality Score**: [Calculated score]
- **Takeaway**: [1-2 line summary of key insight]
- **Snippet**: [≤2 lines of relevant quote or code example]
- **Application**: [odoo-module-dev / odoo-studio-ops / odoo-sh-devops / odoo-docker-claude]
- **Tags**: [Relevant keywords for searchability]
```

---

## Integration with Deep-Research-OCA Skill

### Existing Skill

**Location**: `~/.cline/skills/odoo/deep-research-oca/SKILL.md`

**Capabilities**:
- WebSearch and WebFetch tools
- OCA repository access
- Reddit/Forum crawling
- Research workflow orchestration

### This Automation

**Location**: `knowledge/scripts/`

**Capabilities**:
- Automated query execution
- Quality scoring and filtering
- Citation generation
- Daily scheduling
- Knowledge base updates

### Workflow Integration

1. **Scheduler triggers** daily research (`research_scheduler.sh`)
2. **Auto-research script** executes queries (`auto_research.py`)
3. **Results filtered** by quality score (≥60)
4. **Citations generated** following template
5. **Saved to daily note** (`knowledge/notes/YYYY-MM-DD.md`)
6. **Skill consumes** citations in future research sessions

---

## Testing

### Test Mode

```bash
# Test auto_research.py
python3 auto_research.py --test-mode

# Expected output:
# - ≥5 citations generated
# - Citations follow template format
# - Quality scores calculated
# - Output to knowledge/notes/YYYY-MM-DD.md

# Test scheduler
./research_scheduler.sh --test

# Expected output:
# - Dependency check passes
# - Research executes successfully
# - Citations saved to daily note
# - Exit code 0
```

### Validation Checklist

After test run, verify:

- [ ] `knowledge/notes/YYYY-MM-DD.md` created
- [ ] ≥5 citations present in file
- [ ] Citations follow exact template format
- [ ] Quality scores present (range: 60-120)
- [ ] Links are valid and accessible
- [ ] Snippets are ≤2 lines
- [ ] Tags and applications assigned
- [ ] No duplicate citations

---

## Troubleshooting

### Issue: "Less than 5 citations generated"

**Cause**: Low-quality results filtered out

**Solutions**:
1. Broaden search queries in `auto_research.py`
2. Lower quality threshold (careful - may reduce citation quality)
3. Increase `--max-results` parameter
4. Check if GitHub API rate limited (need `GITHUB_TOKEN`)

---

### Issue: "GitHub API rate limit exceeded"

**Cause**: Unauthenticated requests limited to 60/hour

**Solutions**:
1. Set `GITHUB_TOKEN` environment variable
2. Authenticated rate limit: 5000/hour
3. Reduce `--max-results` parameter
4. Use `--test-mode` (skips some queries)

```bash
# Generate token: https://github.com/settings/tokens
export GITHUB_TOKEN=ghp_your_token_here
```

---

### Issue: "Reddit API timeout"

**Cause**: Reddit API occasionally slow or unavailable

**Solutions**:
1. Retry after 5 minutes
2. Reddit search will be skipped, other sources continue
3. Non-fatal - script continues with partial results

---

### Issue: "Citations not saved to daily note"

**Cause**: Permissions or path issue

**Solutions**:
1. Verify `knowledge/notes/` directory exists and is writable
2. Check absolute path: `ls -la ~/ai-agency/agents/odoo-expertise-skills/knowledge/notes/`
3. Use `--output` parameter to specify custom path

---

## Examples

### Example 1: Manual Research Session

```bash
# Research ORM patterns
cd ~/ai-agency/agents/odoo-expertise-skills
python3 knowledge/scripts/auto_research.py --domain module_dev --max-results 10

# Output: knowledge/notes/2025-11-01.md with 10+ citations
```

---

### Example 2: Weekly Cron Automation

```bash
# Setup cron
crontab -e

# Add daily research at 2 AM UTC
0 2 * * * /Users/tbwa/ai-agency/agents/odoo-expertise-skills/knowledge/scripts/research_scheduler.sh >> /var/log/odoo-research.log 2>&1

# Weekly summary generated automatically on Sundays
```

---

### Example 3: Custom Query Focus

Edit `auto_research.py` to add custom queries:

```python
# In _load_queries() method
'custom_domain': {
    'oca': [
        'my custom OCA query',
    ],
    'reddit': [
        'my custom Reddit query',
    ],
}
```

Then run:
```bash
python3 auto_research.py --domain custom_domain
```

---

## Performance

**Research Session Timing**:
- Discovery: 2-5 minutes (parallel queries)
- Analysis: 1-2 minutes (quality scoring)
- Citation generation: <1 minute
- **Total**: <10 minutes per session

**API Rate Limits**:
- GitHub (unauthenticated): 60/hour
- GitHub (authenticated): 5000/hour
- Reddit: 60/minute
- Stack Overflow: 300/day

**Resource Usage**:
- CPU: Low (I/O bound)
- Memory: <50MB
- Network: <10MB per session

---

## Future Enhancements

Planned improvements (Sprint 5+):

1. **ML-Based Ranking**: Train model on successful vs failed patterns
2. **Auto-Update Alerts**: Notify when cached research becomes outdated
3. **Pattern Library**: Build curated collection of verified patterns
4. **Video Indexing**: Search Odoo YouTube tutorials
5. **Runbot Integration**: Monitor OCA module compatibility

---

## Support

**Issues**: Report to sprint2/skills branch
**Documentation**: See `knowledge/playbooks/deep_research_odoo.md`
**Skill**: `~/.cline/skills/odoo/deep-research-oca/SKILL.md`

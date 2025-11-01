# Anthropic Skills for Repo Auditing

This directory contains Anthropic Skills for automated repository auditing, following the [Anthropic Skills specification](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).

## Available Skills

### 1. repo-auditor (Full Audit)
**Location:** `.claude/skills/repo-auditor/`

A comprehensive audit skill for Odoo+DevOps repositories that checks:
- Odoo OCA compliance (manifest, security, ORM, tests)
- Docker best practices (multi-stage builds, non-root users, healthchecks)
- CI/CD quality (lint, test, scan, deploy pipelines)
- Infrastructure security (Terraform, secrets, backups)
- Observability (monitoring, logging, alerting)

**Usage:**
```bash
# Via GitHub Action (automatic on PRs)
# Or manually trigger via workflow_dispatch

# Via Claude/AI Agent
"Run repo-auditor on this repository"
```

**Outputs:**
- Markdown report with executive summary and prioritized findings
- JSON file with structured findings (matches `findings.json.schema`)

### 2. repo-auditor-security (Security Focus)
**Location:** `.claude/skills/repo-auditor-security/`

A focused security audit that identifies the top 10 most exploitable risks:
- Odoo ACL misconfigurations
- SQL injection risks
- Secrets in CI/CD
- Root containers
- Open firewalls
- Unencrypted backups

**Usage:**
```bash
# Set in GitHub Action workflow
env:
  SKILL: repo-auditor-security
```

### 3. repo-auditor-perf (Performance Focus)
**Location:** `.claude/skills/repo-auditor-perf/`

A performance-focused audit for Odoo and DevOps:
- N+1 query patterns
- Missing database indexes
- Heavy cron jobs
- Chatty RPC calls
- Docker image bloat

**Usage:**
```bash
# Set in GitHub Action workflow
env:
  SKILL: repo-auditor-perf
```

## Directory Structure

```
.claude/skills/
├── README.md (this file)
├── repo-auditor/
│   ├── SKILL.md (skill manifest with YAML front-matter)
│   ├── checklists/
│   │   ├── odoo-oca.md
│   │   ├── docker.md
│   │   ├── ci.md
│   │   ├── terraform.md
│   │   └── observability.md
│   └── templates/
│       ├── report.md.gotmpl (markdown report template)
│       └── findings.json.schema (JSON schema for validation)
├── repo-auditor-security/
│   └── SKILL.md
└── repo-auditor-perf/
    └── SKILL.md
```

## GitHub Action Integration

The repository includes a GitHub Action workflow (`.github/workflows/repo-audit.yml`) that:

1. Runs automatically on pull requests
2. Generates a repository tree
3. Collects key files (Odoo modules, Docker configs, CI workflows, infrastructure)
4. Calls the Anthropic API with the selected skill
5. Posts the audit report as a PR comment
6. Uploads detailed findings as artifacts

### Setup Requirements

Add `ANTHROPIC_API_KEY` to your repository secrets:
1. Go to Settings → Secrets → Actions
2. Add new repository secret: `ANTHROPIC_API_KEY`
3. Set value to your Anthropic API key

### Switching Skills

Edit `.github/workflows/repo-audit.yml` and change the `SKILL` environment variable:

```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  MODEL: claude-3-5-sonnet-20241022
  SKILL: repo-auditor  # Change to: repo-auditor-security or repo-auditor-perf
```

## Customization

### Adding Custom Checklists

Add new checklist files to `repo-auditor/checklists/`:

```markdown
# Custom Checklist
- Check item 1
- Check item 2
- Check item 3
```

The skill will automatically load and use all `.md` files in the checklists directory.

### Modifying Templates

- **Report Template:** Edit `repo-auditor/templates/report.md.gotmpl` (Go template format)
- **JSON Schema:** Edit `repo-auditor/templates/findings.json.schema` to change output structure

### Tuning Severity Levels

Modify the `SKILL.md` file to adjust severity classifications or add custom categories.

## Local Testing

To test the skill locally without running the full GitHub Action:

```bash
# 1. Generate repo tree
tree -a -I 'node_modules|.git|__pycache__' > repo_tree.txt

# 2. Collect files
mkdir -p .audit/in
# (see .github/workflows/repo-audit.yml for collection logic)

# 3. Run the audit script
export ANTHROPIC_API_KEY="your-key-here"
export MODEL="claude-3-5-sonnet-20241022"
export SKILL="repo-auditor"
node .github/scripts/anthropic-audit.js

# 4. View results
cat .audit/out/report.md
cat .audit/out/findings.json
```

## References

- [Anthropic Skills Documentation](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Anthropic Skills GitHub](https://github.com/anthropics/skills)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## Support

For issues or questions about the repo auditor skills:
1. Check the findings in `.audit/out/report.md` after a run
2. Review the raw output in `.audit/out/raw.txt`
3. Verify the JSON schema validation in `.audit/out/findings.json`

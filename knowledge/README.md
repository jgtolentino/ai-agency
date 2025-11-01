# Odoo Agent Knowledge Base (Live)

**Purpose**: Curated, high-signal knowledge repository for Odoo agent expertise

**Last Updated**: 2025-11-01

---

## Overview

This knowledge base serves as the authoritative source for Odoo development patterns, OCA guidelines, community wisdom, and operational runbooks. It feeds the agent skills with validated, production-tested knowledge.

## Curation Rules

### Source Quality Standards

**✅ Include:**
- Official Odoo documentation (2023+, versions 16-19)
- OCA repository patterns and maintainer notes
- High-signal Reddit threads (r/odoo, r/selfhosted, r/devops)
- Stack Overflow answers with ≥10 upvotes (odoo tag)
- Vendor documentation (OCA-compliant services only)

**❌ Exclude:**
- Odoo versions <16.0 (unless migration context)
- Non-OCA patterns without justification
- Reddit threads with <5 upvotes or no resolution
- Proprietary SaaS-only features without self-hosted parity
- Outdated information (pre-2023 unless foundational)

### Citation Format

Every reference must include:
1. **Link**: Full URL to source
2. **Date/Version**: Publication date or Odoo version
3. **Takeaway**: 1-2 line summary of key insight
4. **Snippet**: ≤2 lines of relevant quote or code
5. **Application**: Which skill(s) this applies to (module/studio/sh/docker)

**Template**: See `notes/citation_template.md`

---

## Authoritative Sources

### Official Odoo
- [Developers on Demand](https://www.odoo.com/page/developers-on-demand) - Official development services
- [Studio Features](https://www.odoo.com/app/studio-features) - Studio capabilities and limitations
- [Odoo.sh Features](https://www.odoo.sh/features) - Platform features and deployment options
- [Odoo Documentation](https://www.odoo.com/documentation/) - Official API and framework docs

### OCA (Odoo Community Association)
- [OCA GitHub Organization](https://github.com/OCA) - Community-maintained modules
- [OCA Guidelines](https://github.com/OCA/odoo-community.org) - Module development standards
- [Maintainer Tools](https://github.com/OCA/maintainer-tools) - Pre-commit hooks, linting
- [OCA Addons Repo Template](https://github.com/OCA/oca-addons-repo-template) - Project scaffolding

### Community Forums
- [Reddit r/odoo](https://www.reddit.com/r/odoo/) - Community discussions and troubleshooting
- [Odoo Forums](https://www.odoo.com/forum/help-1) - Official support and feature requests
- [Stack Overflow](https://stackoverflow.com/questions/tagged/odoo) - Technical Q&A

### Vendors & Services
- [Odoo BS Development Services](https://www.odoo-bs.com/odoo-development-services) - OCA-compliant vendor
- Selected OCA maintainers' blogs and documentation

---

## Directory Structure

```
knowledge/
├── README.md                    # This file
├── refs/
│   └── sources.yaml            # Structured source catalog
├── notes/
│   ├── citation_template.md   # Standard citation format
│   ├── 2025-11-01.md           # Daily curated references
│   ├── 2025-11-02.md
│   └── ...
└── playbooks/
    ├── deep_research_odoo.md   # Research automation guide
    ├── orm_patterns.md         # ORM pattern library
    ├── studio/
    │   └── change_plan_template.md
    ├── odoo-sh/
    │   ├── deployment.md
    │   ├── logs.md
    │   └── backups.md
    └── self-hosted/
        └── parity_guide.md
```

---

## Usage Workflows

### Daily Note-Taking

```bash
# Add new reference
echo "## OCA Pattern: Multi-Company Record Rules
- Link: https://github.com/OCA/server-tools/issues/1234
- Date: 2025-10-15
- Takeaway: Use domain with company_id check + multi_company RLS
- Snippet: domain=\"[('company_id', 'in', company_ids)]\"
- Application: odoo-module-dev (security patterns)
" >> knowledge/notes/$(date +%Y-%m-%d).md
```

### Query Research Topics

```bash
# Search existing notes
grep -r "computed field" knowledge/notes/

# Find patterns by skill
grep -r "Application: odoo-docker-claude" knowledge/notes/
```

### Integrate with Deep Research Skill

The `deep_research_odoo.md` playbook defines query sets for automated research. Citations from automated research should be added to daily notes following the same format.

---

## Knowledge Metrics

### Quality Targets
- **Total References**: ≥20 high-signal sources (Sprint 4 target)
- **Recency**: ≥80% from 2023+ (Odoo 16-19 era)
- **OCA Alignment**: ≥90% following OCA patterns
- **Update Cadence**: Daily additions during active development

### Coverage by Skill
- **odoo-module-dev**: ORM patterns, security, testing, migrations
- **odoo-studio-ops**: Studio patterns, export mechanisms, rollback procedures
- **odoo-sh-devops**: Deployment workflows, monitoring, backups
- **odoo-docker-claude**: Docker best practices, SDK integration, security

---

## Contribution Guidelines

### Adding New References

1. **Validate Quality**: Ensure source meets curation standards
2. **Extract Takeaway**: Identify 1-2 line key insight
3. **Cite Properly**: Use citation template format
4. **Tag Application**: Specify which skill(s) benefit from this knowledge
5. **Update Daily Note**: Add to today's note file or create new date file

### Updating Playbooks

1. **Identify Pattern**: New ORM pattern, deployment strategy, etc.
2. **Validate**: Test pattern in practice (eval scenario or real project)
3. **Document**: Add to appropriate playbook with examples
4. **Cross-Reference**: Link from skills and daily notes

### Deprecating Outdated Knowledge

- Mark outdated references with `[DEPRECATED - Odoo X.Y]`
- Add migration note if applicable
- Keep historical context for version upgrade paths

---

## Integration Points

### Existing Skills
- **Deep Research OCA**: `~/.cline/skills/odoo/deep-research-oca/SKILL.md`
  - Auto-crawls OCA GitHub, Reddit r/odoo, Odoo forums
  - Feeds findings into this knowledge base

### Sample Implementations
- **OCA Module**: `~/custom_addons/sc_demo/`
  - Reference implementation for module structure
  - Demonstrates OCA compliance patterns

### Infrastructure
- **Docker Setup**: `~/infra/odoo/`
  - Production Docker configuration
  - Anthropic SDK integration example

---

## Improvement Loop

```
Eval Failure → Identify Knowledge Gap → Research Topic → Add Citation → Update Skill → Retest
```

**Example**:
1. Eval scenario fails: "Record rule causes N+1 queries"
2. Research: Search OCA/server-tools for performance patterns
3. Find solution: Use `search_count` with limit parameter
4. Add citation to knowledge base
5. Update `odoo-module-dev` skill with pattern
6. Rerun eval → pass

---

## Reference Categories

### ORM & Models
- Computed fields (`@api.depends`, stored vs non-stored)
- Related fields and field inheritance
- Constraints (`@api.constrains`, SQL constraints)
- Onchange methods and UI reactivity
- Domain expressions and search patterns

### Security
- Access rights (`ir.model.access.csv`)
- Record rules (domain-based RLS)
- Field-level security
- Multi-company patterns
- User groups and permissions

### Testing
- pytest-odoo framework (TransactionCase, SavepointCase)
- Form API for UI testing
- Business logic validation tests
- Performance testing patterns
- Test data management

### Deployment
- Docker best practices (multi-stage, non-root, secrets)
- Odoo.sh workflows (branches, builds, logs)
- Self-hosted parity (Compose, backups, monitoring)
- Blue-green deployments
- Health checks and auto-restart

### Studio
- Field types and constraints
- View customization (form, list, kanban)
- Server actions and automations
- Export mechanisms (XML, JSON)
- Rollback procedures

---

## Next Actions

1. **Seed Initial References**: Add first 5 high-signal sources (SK2 task)
2. **Create Playbooks**: ORM patterns, deployment runbooks
3. **Automate Research**: Integrate with deep-research-oca skill
4. **Build Citation Habit**: Daily additions during development
5. **Validate Coverage**: Ensure all 4 skills have ≥5 relevant references each

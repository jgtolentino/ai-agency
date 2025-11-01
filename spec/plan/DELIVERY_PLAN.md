# Odoo Agent Expertise – Delivery Plan

**Version**: 1.0
**Last Updated**: 2025-11-01
**Timeline**: 4 Sprints (4 weeks)

---

## Sprint 1: Foundation & Infrastructure (Week 1)

### Objectives
Establish repository structure, skill manifests, knowledge base framework, and CI/CD baseline.

### Deliverables
- ✅ Repository structure at `~/ai-agency/agents/odoo-expertise/`
- ✅ 4 skill manifests (odoo-module-dev, odoo-studio-ops, odoo-sh-devops, odoo-docker-claude)
- ✅ Spec-Kit structure (PRD, Plan, Tasks)
- ✅ Knowledge base skeleton with curation rules
- ✅ CI/CD workflow with pre-commit hooks
- ✅ Integration with Cline/SuperClaude (symlinks + config)

### Success Criteria
- All skills registered in Cline CLI
- Pre-commit hooks passing on sample module
- Knowledge base structure navigable
- CI workflow green on first commit

---

## Sprint 2: Core Development Capabilities (Week 2)

### Objectives
Implement OCA module generation, Studio operations patterns, and deep-research automation.

### Tasks

#### SK2: Deep-Research Playbook
- Create `knowledge/playbooks/deep_research_odoo.md` with query sets
- Implement auto-citation template
- Add note-taking workflow for OCA GitHub, Reddit r/odoo, Odoo forums
- Integration with existing `~/.cline/skills/odoo/deep-research-oca/`

#### DEV1: OCA Module Scaffolding
- Scaffold generator for OCA-compliant modules
- Security templates (`ir.model.access.csv`, record rules)
- pytest-odoo test templates (TransactionCase, SavepointCase)
- Pre-commit hook integration

#### DEV2: ORM Pattern Library
- Computed field templates with `@api.depends`
- `@api.onchange` and `@api.constrains` examples
- Record rule patterns with domain expressions
- Related field and stored field patterns

#### Studio Operations
- Studio change plan template
- XML/JSON export mechanisms
- Rollback procedure documentation
- Safety checklist for Studio modifications

### Deliverables
- OCA module generator functional
- 5 ORM pattern examples in knowledge base
- Studio operation runbooks
- First 5 eval scenarios passing

### Success Criteria
- Generate working OCA module with single command
- Studio change plan template validated
- Deep-research queries returning relevant OCA patterns
- ≥80% pass rate on first 5 evals

---

## Sprint 3: Infrastructure & DevOps (Week 3)

### Objectives
Complete Odoo.sh workflows, Docker image with Claude SDK, and self-hosted parity runbooks.

### Tasks

#### OPS1: Docker Image with Claude SDK
- Multi-stage Dockerfile (Python 3.11 + Odoo 16/17/19)
- wkhtmltopdf + fonts (Noto, DejaVu)
- Anthropic Python SDK (v0.36.0+)
- Non-root user pattern (uid 1000)
- docker-compose.yml with PostgreSQL 15

#### OPS2: Odoo.sh Parity
- Branch strategy documentation (dev → staging → prod)
- Build pipeline runbooks
- Log aggregation patterns
- Backup and restore procedures
- Self-hosted Docker Compose equivalents

#### DevOps Automation
- Deployment checklists with validation gates
- Blue-green deployment strategy
- Health check configurations
- Monitoring dashboard templates

### Deliverables
- Docker image builds successfully with all dependencies
- docker-compose.yml runs Odoo + PostgreSQL
- Odoo.sh runbooks for 5+ operations
- Self-hosted parity guides for all Odoo.sh features
- Remaining 5+ eval scenarios added

### Success Criteria
- Docker image runs wkhtmltopdf without errors
- Anthropic SDK importable in Odoo Python environment
- No hardcoded secrets in any Docker/compose files
- Odoo.sh → self-hosted mapping complete
- ≥90% pass rate on all 10+ evals

---

## Sprint 4: Production Readiness & Polish (Week 4)

### Objectives
Achieve ≥95% eval pass rate, complete documentation, validate cost targets, and optimize performance.

### Tasks

#### QA1: Eval Coverage
- Complete 10+ eval scenarios:
  1. OCA module scaffolding + computed fields
  2. Studio change plan with rollback
  3. Docker image validation (wkhtmltopdf, SDK, non-root)
  4. Odoo.sh deployment plan
  5. Secrets policy compliance
  6. Record rule N+1 optimization
  7. Migration script with openupgradelib
  8. Docker Compose environment
  9. Visual parity validation
  10. Task bus integration
- Gate CI on eval pass
- Regression test suite

#### Documentation
- Main README with quickstart
- Daily usage guide
- Improvement workflow (eval failures → knowledge base updates)
- Troubleshooting section
- Cost breakdown validation

#### Performance Optimization
- OCR processing P95 < 30s validation
- Docker image size optimization
- Build time < 5 minutes
- Deployment time < 10 minutes

#### Cost Validation
- Monthly budget < $20 USD verification
- Supabase free tier usage monitoring
- DigitalOcean App Platform cost tracking
- API usage analysis (DeepSeek vs Claude)

### Deliverables
- ≥95% pass rate on all eval scenarios
- Complete documentation suite
- Cost analysis report
- Performance benchmarks
- Knowledge base with ≥20 curated references

### Success Criteria
- All 10+ evals passing consistently
- Documentation complete and reviewed
- Monthly cost confirmed <$20 USD
- Performance targets met
- Production-ready for real-world usage

---

## Risk Management

### High Priority Risks

**Risk**: OCA guidelines change mid-development
**Mitigation**: Monitor OCA/maintainer-tools repo, flexible skill patterns, version knowledge base entries

**Risk**: DeepSeek API rate limits during heavy usage
**Mitigation**: Implement exponential backoff, use Claude Code as fallback, batch operations

**Risk**: Docker image bloat (>2GB)
**Mitigation**: Multi-stage builds, minimize dependencies, use alpine base where possible

**Risk**: Secrets accidentally committed
**Mitigation**: Pre-commit hooks for secret detection, .gitignore enforcement, PR review checklist

### Medium Priority Risks

**Risk**: Odoo version incompatibility (16 vs 17 vs 19)
**Mitigation**: Test across all three versions, maintain version-specific notes, document differences

**Risk**: Studio export limitations
**Mitigation**: Document manual export steps, provide rollback procedures, test in staging first

**Risk**: Self-hosted parity gaps
**Mitigation**: Comprehensive runbook testing, community validation, alternative solutions documented

---

## Dependencies & Blockers

### Sprint 1 Dependencies
- None (foundational work)

### Sprint 2 Dependencies
- Sprint 1 complete (repository structure, skills registered)
- DeepSeek API key configured
- Existing deep-research skill accessible

### Sprint 3 Dependencies
- Sprint 2 complete (module generator working)
- Docker installed and running
- DigitalOcean account access
- Supabase CLI configured

### Sprint 4 Dependencies
- Sprint 3 complete (Docker image functional)
- All eval scenarios written
- Knowledge base seeded with initial references

---

## Definition of Done

### Sprint-Level DoD
- All tasks completed and verified
- Code passing pre-commit hooks
- Relevant eval scenarios passing
- Documentation updated
- Knowledge base entries added

### Project-Level DoD
- ≥95% pass rate on all eval scenarios
- Monthly cost <$20 USD verified
- Performance targets met (P95 <30s for OCR)
- Complete documentation (README, runbooks, troubleshooting)
- Knowledge base with ≥20 curated, high-signal references
- CI/CD pipeline green
- Production deployment successful (DigitalOcean App Platform)

---

## Metrics & KPIs

### Quality Metrics
- Eval pass rate: Target ≥95%
- Test coverage: Target ≥80%
- Pre-commit hook pass rate: Target 100%

### Performance Metrics
- OCR processing time: P95 <30s
- Docker build time: <5 minutes
- Deployment time: <10 minutes
- Auto-approval rate: ≥85%

### Cost Metrics
- Monthly infrastructure: <$20 USD
- API costs: <$10/month
- Total cost reduction: ≥87% vs Azure baseline

### Knowledge Metrics
- Curated references: ≥20 high-signal sources
- Note-taking cadence: Daily updates
- OCA pattern library: ≥10 validated patterns

---

## Communication Plan

### Daily
- Todo list updates in Cline sessions
- Knowledge base note additions
- Eval scenario results

### Weekly (Sprint Boundaries)
- Sprint review: deliverables vs plan
- Sprint retrospective: what worked, what didn't
- Sprint planning: next sprint tasks

### Ad-Hoc
- Blocker escalation
- Risk mitigation status
- Cost/performance deviation alerts

---

## Next Actions (Post-Sprint 4)

### Continuous Improvement
- Monitor eval pass rate, add scenarios for new failure modes
- Update knowledge base with latest OCA patterns
- Refine model routing based on cost/performance data
- Expand skill capabilities based on real-world usage

### Future Enhancements
- Additional Odoo versions (18.0, 20.0)
- Advanced ORM patterns (custom fields, wizards, multi-company)
- Kubernetes deployment strategies
- Multi-language support in Studio operations
- Advanced monitoring and alerting

### Community Contribution
- Share OCA-compliant templates with community
- Contribute eval scenarios to SuperClaude framework
- Document lessons learned for other agent builders

# Odoo Agent Expertise – Product Requirements Document (v1.0)

**Last Updated**: 2025-11-01
**Status**: Active
**Owner**: SuperClaude Framework + Cline CLI Integration

---

## 1. Executive Summary

Build production-grade agent expertise for full-stack Odoo development, enabling autonomous creation of OCA-compliant modules, safe Studio operations, Odoo.sh lifecycle management, and Docker deployments with Claude SDK integration. Target: replicate enterprise SaaS features (SAP, Salesforce, QuickBooks) at <$20/month cost.

## 2. Objectives

### Primary Objectives
1. **OCA Module Development**: Generate OCA-compliant Odoo modules end-to-end (scaffold → models → security → tests → CI → release)
2. **Studio Operations**: Operate Odoo Studio safely with exportable artifacts, change diffs, and rollback plans
3. **Odoo.sh Lifecycle**: Manage Odoo.sh deployment pipeline (branches, builds, staging, logs, backups) with self-hosted Docker parity
4. **Docker + Claude SDK**: Build/ship production-ready Odoo images with Anthropic SDK and secure secret handling

### Success Metrics
- **Quality Gate**: ≥95% pass rate on eval suite (10+ scenarios)
- **CI/CD**: All PRs pass pre-commit hooks + pytest-odoo
- **Production Readiness**: Docker image runs wkhtmltopdf reliably, non-root user, no hardcoded secrets
- **Cost Efficiency**: Monthly infrastructure <$20 USD (87% reduction from $150 Azure baseline)
- **Auto-Approval Rate**: ≥85% for expense automation workflows
- **Processing Time**: P95 < 30 seconds for OCR + validation

## 3. Non-Goals

❌ **Out of Scope**:
- Proprietary SaaS features that cannot run self-hosted without parity plan
- Odoo versions < 16.0 (focus on 16.0, 17.0, 19.0)
- Non-OCA module patterns (unless explicitly justified)
- Azure services (deprecated - use DigitalOcean + Supabase)
- Local Docker for production deployments (use DigitalOcean App Platform)

## 4. Technical Requirements

### 4.1 Module Development
- **OCA Compliance**: Follow OCA guidelines, manifests, licensing (LGPL-3)
- **ORM Patterns**: Proper use of `@api.depends`, `@api.onchange`, `@api.constrains`
- **Security**: `ir.model.access.csv` + record rules with domain expressions
- **Testing**: pytest-odoo with TransactionCase/SavepointCase, ≥80% coverage
- **Migrations**: openupgradelib patterns for version upgrades

### 4.2 Studio Operations
- **Safety**: Pre-change diffs, export to XML/JSON, documented rollback
- **Documentation**: Change plans in `knowledge/playbooks/studio/`
- **Testing**: Staging/dev environment validation before production
- **Audit Trail**: Every change documented with before/after states

### 4.3 Odoo.sh & DevOps
- **Branch Strategy**: Development → Staging → Production workflow
- **Build Pipeline**: Git push → automated build → deploy
- **Monitoring**: Logs (app, database, web server), performance metrics
- **Backups**: Automated backups with restore procedures
- **Self-Hosted Parity**: Docker Compose equivalents for all Odoo.sh features

### 4.4 Docker Infrastructure
- **Base Image**: Python 3.11-slim with multi-stage builds
- **Dependencies**: wkhtmltopdf, fonts (Noto, DejaVu), system libraries
- **Claude SDK**: Anthropic Python SDK (v0.36.0+) with opt-in pattern
- **Security**: Non-root user (uid 1000), secrets via environment variables only
- **Orchestration**: Docker Compose with PostgreSQL 15, volume mounts, health checks

## 5. Architecture

### 5.1 Skill Hierarchy
```
odoo-expertise/
├── odoo-module-dev       (DeepSeek v3.1 default, R1 for planning)
├── odoo-studio-ops       (DeepSeek v3.1 default)
├── odoo-sh-devops        (DeepSeek R1 for deployment planning)
└── odoo-docker-claude    (DeepSeek v3.1, escalate to Claude Code for complex IaC)
```

### 5.2 Model Routing Strategy
- **DeepSeek v3.1**: Default coding, tool calls, JSON generation (low cost)
- **DeepSeek R1**: Planning, reasoning, architectural decisions (cap think tokens at 1536)
- **Claude Code (Max)**: Repo-wide refactors, complex git operations, shell commands
- **Claude API**: Opt-in for in-app SDK calls (billable via Console)

### 5.3 Integration Points
- **SuperClaude Framework**: 15 unified agents, command system, wave orchestration
- **Cline CLI**: Autonomous coding agent with DeepSeek API integration
- **Existing Infrastructure**: Cross-reference `~/infra/odoo/`, `~/custom_addons/sc_demo/`, `~/.cline/skills/odoo/deep-research-oca/`

## 6. Quality Assurance

### 6.1 Evaluation Suite
10+ scenarios covering:
1. OCA module scaffolding with computed fields and tests
2. Studio change plans with safe rollback procedures
3. Docker image validation (wkhtmltopdf, fonts, non-root, SDK)
4. Odoo.sh deployment plans with staging validation
5. Security/secrets policy compliance (no hardcoded keys)
6. Record rule N+1 detection and optimization
7. Migration script patterns with openupgradelib
8. Docker Compose environment with volume mounts
9. Visual parity gates (SSIM thresholds)
10. Task bus integration for deployment notifications

### 6.2 CI/CD Pipeline
- **Pre-commit Hooks**: black, isort, flake8, pylint-odoo
- **Testing**: pytest-odoo with ≥80% coverage
- **Eval Gates**: All scenarios must pass before merge
- **Drift Detection**: Daily checks (Supabase schema, DO app specs)
- **Visual Parity**: SSIM ≥0.97 (mobile), ≥0.98 (desktop)

## 7. Knowledge Base

### 7.1 Curation Rules
- **Recency**: Prefer sources from 2023+ (Odoo 16-19 era)
- **Alignment**: OCA-aligned posts and official documentation
- **Signal Quality**: High-signal Reddit threads, OCA maintainers' notes
- **Citation**: 1-2 line takeaways per reference in `knowledge/notes/`

### 7.2 Authoritative Sources
- **Official Odoo**: Developers on Demand, Studio features, Odoo.sh features
- **OCA**: GitHub repositories, maintainer-tools, OCA guidelines
- **Community**: Reddit r/odoo, Stack Overflow (odoo tag), Odoo forums
- **Vendors**: OCA-compliant Odoo development services

## 8. Cost & Performance Constraints

### 8.1 Monthly Budget
- **Target**: <$20 USD total infrastructure
  - Supabase Free Tier: $0/month (up to 500MB database)
  - DigitalOcean App Platform: $5/month (basic-xxs)
  - OpenAI/DeepSeek API: ~$10/month (direct, cheaper than Azure)
  - Claude API: ~$5/month (opt-in for SDK features)

### 8.2 Performance Targets
- **OCR Processing**: P95 < 30 seconds
- **Auto-Approval**: ≥85% accuracy
- **Uptime**: 99.9% SLA (8.7 hours downtime/year)
- **Build Time**: <5 minutes for Docker image builds
- **Deployment**: <10 minutes for DigitalOcean App Platform deploys

## 9. Security & Compliance

### 9.1 Secrets Management
- ✅ Environment variables only (`~/.zshrc`, `.env` files)
- ✅ Supabase Vault for sensitive database values
- ❌ NEVER hardcode secrets in Dockerfile, compose files, or code
- ❌ NEVER commit secrets to git repositories

### 9.2 RLS Policies
- All Supabase tables must have Row Level Security (RLS) policies
- Service role key only in backend services (never frontend)
- Anon key safe for frontend (RLS enforces access control)

### 9.3 Supply Chain Security
- Base image pinning with SHA256 digests
- Vulnerability scanning with Trivy or Grype
- Non-root user pattern (uid 1000)
- Read-only root filesystem support

## 10. Delivery Plan

### Sprint 1: Foundation (Week 1)
- ✅ Skills + knowledge base + CI baseline
- ✅ Repository structure and Spec-Kit
- ✅ Integration with Cline/SuperClaude

### Sprint 2: Core Development (Week 2)
- OCA module generator + Studio operations skills
- Deep-research playbook with auto-citation
- First 5 eval scenarios

### Sprint 3: Infrastructure (Week 3)
- Odoo.sh workflows + Docker image with Claude SDK
- Self-hosted parity runbooks
- Remaining 5+ eval scenarios

### Sprint 4: Production Readiness (Week 4)
- Eval coverage + CI/CD polish
- Documentation and usage guides
- Performance optimization and cost validation

## 11. Dependencies

### 11.1 Required
- Cline CLI (v1.0.1+)
- DeepSeek API key
- Claude Max subscription (for Claude Code CLI)
- DigitalOcean account + doctl CLI
- Supabase account + CLI
- Docker + Docker Compose
- Python 3.11+
- Node.js 18+

### 11.2 Optional
- Claude API key (for in-app SDK features)
- GitHub Actions (for CI/CD)
- Vercel account (for frontend deployments)

## 12. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| DeepSeek API rate limits | Medium | Low | Implement exponential backoff, use Claude Code as fallback |
| OCA guideline changes | Medium | Medium | Monitor OCA/maintainer-tools repo, update knowledge base |
| Odoo version incompatibility | High | Low | Test across 16.0, 17.0, 19.0; maintain version-specific notes |
| Docker image size bloat | Low | Medium | Multi-stage builds, minimize dependencies |
| Secrets exposure | Critical | Low | PR checks for hardcoded secrets, .gitignore enforcement |

## 13. Appendix

### 13.1 References
- [Odoo Developers on Demand](https://www.odoo.com/page/developers-on-demand)
- [Odoo Studio Features](https://www.odoo.com/app/studio-features)
- [Odoo.sh Features](https://www.odoo.sh/features)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org)
- [OCA Maintainer Tools](https://github.com/OCA/maintainer-tools)

### 13.2 Glossary
- **OCA**: Odoo Community Association
- **ORM**: Object-Relational Mapping (Odoo's database abstraction)
- **RLS**: Row Level Security (Supabase/PostgreSQL security model)
- **SSIM**: Structural Similarity Index (visual parity metric)
- **P95**: 95th percentile (performance metric)

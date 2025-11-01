# ADR-XXX: [Decision Title]

**Date**: YYYY-MM-DD
**Status**: [Proposed | Accepted | Deprecated | Superseded]
**Module**: [Module Name]
**Decision Makers**: [@username, @username]

## Context

What is the issue that we're seeing that is motivating this decision or change?

Provide background information including:

### Problem Statement

Clear description of the problem being solved or opportunity being addressed.

### Current Situation

How things work today (if applicable). Include:
- Current implementation details
- Known limitations or pain points
- User feedback or data supporting the need

### Requirements

Key functional and non-functional requirements:

- **Functional**:
  - Requirement 1
  - Requirement 2

- **Non-Functional**:
  - Performance targets
  - Scalability needs
  - Security requirements
  - Compliance mandates

### Constraints

Technical, business, or regulatory limitations:

- **Technical**: Infrastructure limitations, technology stack restrictions
- **Business**: Budget constraints, timeline requirements, resource availability
- **Regulatory**: Compliance requirements, industry standards

### Assumptions

What we're assuming to be true:

- Assumption 1: Evidence or rationale
- Assumption 2: Evidence or rationale
- Assumption 3: Evidence or rationale

### Technical Context

- **Odoo Version**: 16.0 / 17.0 / 18.0 / 19.0
- **Python Version**: 3.10 / 3.11 / 3.12
- **Database**: PostgreSQL 14 / 15 / 16
- **Dependencies**: List of critical module dependencies
- **Integration Points**: External systems or third-party services

---

## Decision

What is the change that we're proposing and/or doing?

Be specific and include:

### Chosen Solution

Detailed description of the approach we're taking.

### Architecture Overview

High-level architecture diagram or description:

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Frontend  │──────▶│   Backend   │──────▶│   Database  │
│  (Odoo UI)  │       │  (Python)   │       │ (PostgreSQL)│
└─────────────┘       └─────────────┘       └─────────────┘
```

### Implementation Details

Key technical decisions and patterns:

1. **Data Model**:
   ```python
   # Example model structure
   class Example(models.Model):
       _name = 'example.model'
       _description = 'Example Model'

       name = fields.Char(string="Name", required=True)
       state = fields.Selection([
           ('draft', 'Draft'),
           ('confirmed', 'Confirmed'),
       ], default='draft')
   ```

2. **Business Logic**:
   - Decision point 1 and rationale
   - Decision point 2 and rationale

3. **Security**:
   - Access control strategy
   - Data protection measures
   - RLS (Row Level Security) policies if applicable

4. **Performance**:
   - Caching strategy
   - Query optimization approach
   - Indexing decisions

### Why This Approach

Rationale for choosing this solution over alternatives:

- **Reason 1**: Supporting evidence or metrics
- **Reason 2**: Alignment with requirements
- **Reason 3**: Risk mitigation

### Scope

What is included and excluded from this decision:

**Included**:
- Feature/component 1
- Feature/component 2
- Feature/component 3

**Excluded** (future enhancements):
- Feature/component A (deferred to v2.0)
- Feature/component B (out of scope)

---

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive Consequences

- ✅ **Benefit 1**: Description of advantage
  - Impact: High/Medium/Low
  - Affected stakeholders: [List]

- ✅ **Benefit 2**: Another advantage
  - Impact: High/Medium/Low
  - Affected stakeholders: [List]

- ✅ **Benefit 3**: System improvement
  - Impact: High/Medium/Low
  - Affected stakeholders: [List]

### Negative Consequences

- ❌ **Trade-off 1**: What we're giving up
  - Impact: High/Medium/Low
  - Mitigation: How we'll address this

- ❌ **Trade-off 2**: Added complexity or constraints
  - Impact: High/Medium/Low
  - Mitigation: How we'll address this

- ❌ **Technical Debt**: New debt introduced
  - Impact: High/Medium/Low
  - Mitigation: Plan to address debt

### Neutral Consequences

- ℹ️ **Change 1**: Neither clearly positive nor negative
  - Description and implications

- ℹ️ **Change 2**: Shifts in patterns or approach
  - Description and implications

### Risks and Mitigations

| Risk | Probability | Impact | Mitigation Strategy |
|------|-------------|--------|---------------------|
| Risk description 1 | Low/Med/High | Low/Med/High | How we'll prevent or handle it |
| Risk description 2 | Low/Med/High | Low/Med/High | How we'll prevent or handle it |
| Risk description 3 | Low/Med/High | Low/Med/High | How we'll prevent or handle it |

---

## Alternatives Considered

What other options were evaluated?

### Alternative 1: [Name]

**Description**: Brief description of this alternative approach

**Pros**:
- Advantage 1
- Advantage 2
- Advantage 3

**Cons**:
- Disadvantage 1
- Disadvantage 2
- Disadvantage 3

**Rejection Reason**: Why this wasn't chosen (e.g., higher complexity, doesn't meet requirement X, higher risk)

### Alternative 2: [Name]

**Description**: Brief description of this alternative approach

**Pros**:
- Advantage 1
- Advantage 2

**Cons**:
- Disadvantage 1
- Disadvantage 2

**Rejection Reason**: Why this wasn't chosen

### Alternative 3: Do Nothing

**Description**: Keep current system/approach

**Pros**:
- No development effort
- No risk of regression

**Cons**:
- Problem remains unsolved
- Technical debt accumulates
- User pain points persist

**Rejection Reason**: [Specific reason why status quo is unacceptable]

---

## Implementation Notes

*(Fill in when status changes to "Accepted")*

### Migration Path

If replacing an existing system or changing data structure:

1. **Phase 1: Preparation** (Duration: X days)
   - Backup current data
   - Create migration scripts
   - Test migration in staging

2. **Phase 2: Gradual Rollout** (Duration: X days)
   - Deploy to canary environment (5% traffic)
   - Monitor metrics and error rates
   - Deploy to 25%, 50%, 100% progressively

3. **Phase 3: Validation** (Duration: X days)
   - Verify data integrity
   - Confirm performance targets met
   - User acceptance testing

4. **Phase 4: Deprecation** (Duration: X days)
   - Deprecate old system
   - Archive old data
   - Update documentation

### Rollout Strategy

- **Environment Sequence**: Dev → Staging → Production
- **Deployment Method**: Blue-green deployment with automatic rollback
- **Rollback Criteria**:
  - Health check failure
  - Error rate >1%
  - Performance degradation >20%
  - User-reported critical bugs

### Success Metrics

How we'll measure if this decision achieves its goals:

| Metric | Baseline | Target | Measurement Method |
|--------|----------|--------|-------------------|
| Metric 1 (e.g., response time) | X ms | Y ms | Application performance monitoring |
| Metric 2 (e.g., user satisfaction) | X% | Y% | User surveys |
| Metric 3 (e.g., error rate) | X% | Y% | Error tracking logs |

### Monitoring and Validation

What we'll monitor to ensure success:

- **Health Checks**:
  - Endpoint: `/api/health`
  - Frequency: Every 30 seconds
  - Expected: HTTP 200, response time <500ms

- **Performance Metrics**:
  - Database query time: <100ms P95
  - API response time: <500ms P95
  - Memory usage: <80% of allocated

- **Error Rates**:
  - Application errors: <0.1%
  - 5xx responses: <0.01%
  - Timeout errors: <0.05%

- **Business Metrics**:
  - User adoption rate: >80% within 30 days
  - Feature usage: >500 operations/day
  - Customer satisfaction: >4.5/5 rating

### Rollback Plan

If implementation fails or metrics don't meet targets:

1. **Immediate Rollback** (if critical failure):
   ```bash
   # Automated via GitHub Actions rollback.yml
   gh workflow run rollback.yml -f environment=production
   ```

2. **Manual Rollback Steps**:
   - Revert database migrations
   - Restore previous deployment
   - Verify health checks
   - Notify stakeholders

3. **Post-Mortem**:
   - Create incident report
   - Analyze root cause
   - Update ADR with lessons learned

---

## References

- [OCA Guidelines](https://github.com/OCA/maintainer-tools/wiki)
- [Related ADR-001: Previous Related Decision](../ADR-001-related-decision.md)
- [Related ADR-002: Another Related Decision](../ADR-002-another-decision.md)
- [GitHub Issue #XXX: Feature Request](https://github.com/your-org/your-repo/issues/XXX)
- [GitHub PR #XXX: Implementation PR](https://github.com/your-org/your-repo/pull/XXX)
- [Technical Specification](../specs/technical-spec.md)
- [External Documentation](https://external-resource.com/docs)
- [Research Notes](../notes/research-YYYY-MM-DD.md)

---

## Decision History

| Date | Status | Author | Notes |
|------|--------|--------|-------|
| YYYY-MM-DD | Proposed | @username | Initial proposal |
| YYYY-MM-DD | Under Review | @username | Review comments addressed |
| YYYY-MM-DD | Accepted | @username | Decision approved |
| YYYY-MM-DD | Implemented | @username | Implementation complete |
| YYYY-MM-DD | Superseded | @username | Replaced by ADR-XXX |

---

## Status Definitions

- **Proposed**: Under review and discussion, not yet approved
- **Accepted**: Decision approved and ready for implementation
- **Deprecated**: No longer recommended, superseded by newer ADR
- **Superseded**: Replaced by ADR-XXX (provide link)
- **Rejected**: Considered but not approved

---

## Review Process

1. **Proposal**: Author creates ADR with status "Proposed"
2. **Review**: Team reviews and provides feedback via comments or PR
3. **Discussion**: Address concerns, iterate on proposal, update ADR
4. **Decision**: Team decides to Accept, Reject, or Request Changes
5. **Implementation**: Update status to "Accepted" and begin implementation
6. **Retrospective**: Review decision after implementation, update with lessons learned

---

## Approval Requirements

- **Technical Approval**: 2 engineers with relevant domain expertise
- **Architecture Approval**: 1 architect or technical lead
- **Product Approval**: 1 product manager (for user-facing changes)
- **Security Approval**: 1 security engineer (for security-related changes)

---

**Authors**: @username1, @username2
**Reviewers**: @reviewer1, @reviewer2, @reviewer3
**Approvers**: @approver1, @approver2

---

## Related ADRs

- [ADR-001: Initial Architecture Decision](../ADR-001-initial-architecture.md)
- [ADR-005: Database Schema Design](../ADR-005-database-schema.md)
- [ADR-012: API Versioning Strategy](../ADR-012-api-versioning.md)

---

## Supersedes

If this ADR supersedes previous decisions, list them here:

- [ADR-003: Old Approach to Problem X](../ADR-003-old-approach.md) - Replaced by this decision

---

## Tags

`#architecture` `#database` `#performance` `#security` `#odoo-16` `#module-name`

---

**End of ADR Template**

## Usage Instructions

### Creating a New ADR

1. **Copy This Template**:
   ```bash
   cp templates/ADR_template.md custom_addons/your_module/ADR-001-decision-slug.md
   ```

2. **Number ADRs Sequentially**:
   - Count existing ADRs in module
   - Use next number (e.g., ADR-004)

3. **Use Descriptive Slugs**:
   - ADR-001-state-machine-approval
   - ADR-002-connection-pool-optimization
   - ADR-003-hmac-webhook-security

4. **Fill in All Sections**:
   - Context: Problem, requirements, constraints
   - Decision: Chosen approach and rationale
   - Consequences: Pros, cons, risks
   - Alternatives: Other options considered

5. **Get Reviews**:
   - Create PR with ADR
   - Tag relevant reviewers
   - Address feedback

6. **Update Status**:
   - Proposed → Accepted → Implemented

### Using docgen.py for ADRs

```bash
# Auto-generate ADR with module metadata
python scripts/docgen.py custom_addons/expense_approval \
  --adr "Use state machine for approval flow"

# Generates: ADR-001-use-state-machine-for-approval-flow.md
```

### ADR Review Checklist

Before approving an ADR:

- [ ] Problem clearly stated and justified
- [ ] Requirements complete and testable
- [ ] Decision rationale provided
- [ ] Alternatives considered and documented
- [ ] Consequences (pros/cons/risks) identified
- [ ] Implementation plan included
- [ ] Success metrics defined
- [ ] Rollback plan documented
- [ ] References and related ADRs linked
- [ ] Approvals obtained

### Maintenance

- **Review Frequency**: Quarterly review of all ADRs
- **Update When**: Implementation reveals new information
- **Supersede When**: New ADR replaces old decision
- **Deprecate When**: Decision no longer applicable

---

**Template Version**: 1.0.0
**Last Updated**: 2025-11-01
**Maintainer**: DevOps Team

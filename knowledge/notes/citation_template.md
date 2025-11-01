# Citation Template

**Purpose**: Standard format for all knowledge base citations

**Usage**: Copy this template when adding new references to daily notes

---

## Template

```markdown
## [TITLE - Brief description]

- **Link**: [Full URL]
- **Date/Version**: [Publication date or Odoo version, e.g., "2024-05-15" or "Odoo 17.0"]
- **Source Type**: [OCA Repository / Reddit / Forum / Stack Overflow / Official Docs]
- **Takeaway**: [1-2 line summary of key insight]
- **Snippet**: [≤2 lines of relevant quote or code example]
- **Application**: [Which skill(s) this applies to: odoo-module-dev / odoo-studio-ops / odoo-sh-devops / odoo-docker-claude]
- **Tags**: [Relevant keywords for searchability]
```

---

## Examples

### Example 1: OCA Repository Pattern

```markdown
## OCA Pattern: Computed Field with @api.depends

- **Link**: https://github.com/OCA/server-tools/blob/16.0/base_tier_validation/models/tier_validation.py#L45-L52
- **Date/Version**: 2024-03-12, Odoo 16.0
- **Source Type**: OCA Repository
- **Takeaway**: Use @api.depends with full path for related fields to avoid cache invalidation issues
- **Snippet**: `@api.depends('line_ids.product_id', 'line_ids.quantity')` ensures proper dependency tracking
- **Application**: odoo-module-dev (ORM patterns)
- **Tags**: computed-field, api-depends, cache-invalidation
```

### Example 2: Reddit Community Solution

```markdown
## Docker wkhtmltopdf Font Rendering Fix

- **Link**: https://www.reddit.com/r/odoo/comments/abc123/wkhtmltopdf_fonts_not_rendering/
- **Date/Version**: 2024-08-20
- **Source Type**: Reddit r/odoo
- **Takeaway**: Install fonts-noto and fonts-dejavu-core, then run fc-cache -fv to fix PDF rendering issues
- **Snippet**: `RUN apt-get install fonts-noto fonts-dejavu-core && fc-cache -fv`
- **Application**: odoo-docker-claude (Docker image building)
- **Tags**: docker, wkhtmltopdf, fonts, pdf-rendering
```

### Example 3: Stack Overflow Solution

```markdown
## Record Rule N+1 Query Optimization

- **Link**: https://stackoverflow.com/questions/78901234/odoo-record-rule-causing-n1-queries
- **Date/Version**: 2024-06-05, Odoo 17.0
- **Source Type**: Stack Overflow (35 upvotes, accepted answer)
- **Takeaway**: Avoid using search() in record rule domains; use SQL subqueries or prefetch patterns instead
- **Snippet**: Use `domain = [('id', 'in', allowed_ids)]` where allowed_ids computed once, not per-record search
- **Application**: odoo-module-dev (security, performance)
- **Tags**: record-rules, n+1, performance, security
```

### Example 4: Official Documentation

```markdown
## Odoo.sh Branch Management Best Practices

- **Link**: https://www.odoo.sh/features#branch-management
- **Date/Version**: 2024-09-01, Odoo.sh
- **Source Type**: Official Documentation
- **Takeaway**: Use feature branches from production for bug fixes, from staging for new features; merge staging→prod weekly
- **Snippet**: "Production branch receives bug fixes only. Staging branch is for feature development before promotion."
- **Application**: odoo-sh-devops (deployment workflows)
- **Tags**: odoo-sh, branches, deployment, git-workflow
```

### Example 5: OCA Guidelines

```markdown
## OCA Module Manifest Requirements

- **Link**: https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst#module-manifest
- **Date/Version**: 2024-01-15, OCA Guidelines
- **Source Type**: OCA Guidelines
- **Takeaway**: Manifest must include: name, version (X.Y.Z.A.B format), license (LGPL-3), author (company or OCA), website, depends, data
- **Snippet**: Version format: {Odoo major}.{Odoo minor}.{addon major}.{addon minor}.{addon patch}
- **Application**: odoo-module-dev (module structure, licensing)
- **Tags**: oca, manifest, versioning, licensing
```

---

## Citation Quality Checklist

Before adding a citation, verify:

- [ ] **Link works** and points to specific resource (not just homepage)
- [ ] **Date/Version** is accurate and recent (prefer 2023+)
- [ ] **Takeaway** is clear and actionable (1-2 lines max)
- [ ] **Snippet** provides concrete example (code or quote)
- [ ] **Application** tags correct skill(s)
- [ ] **Source quality** meets curation standards (upvotes, official status, OCA alignment)

---

## Search and Filtering

### Find citations by skill
```bash
grep -r "Application: odoo-module-dev" knowledge/notes/
```

### Find citations by tag
```bash
grep -r "Tags:.*computed-field" knowledge/notes/
```

### Find recent citations
```bash
ls -lt knowledge/notes/*.md | head -10
```

---

## Integration with Automated Research

When the `deep-research-oca` skill finds relevant sources, it should:
1. Extract information matching this citation template
2. Add to today's daily note (`knowledge/notes/YYYY-MM-DD.md`)
3. Tag with appropriate skill application
4. Include quality score metadata (upvotes, official status, etc.)

---

## Notes

- **One citation per topic**: Don't duplicate the same Stack Overflow answer if already cited
- **Update if better source found**: Replace older/lower-quality citations with better ones
- **Deprecation**: Mark outdated citations with `[DEPRECATED - Odoo X.Y]` prefix
- **Cross-references**: Link related citations in different daily notes

#!/usr/bin/env python3
"""
Documentation generator for Odoo modules.
Reads __manifest__.py and generates README.rst, CHANGELOG.md, ADR.

Usage:
    docgen.py <module_path> [--adr 'Decision Title']

Example:
    python scripts/docgen.py custom_addons/expense_approval
    python scripts/docgen.py custom_addons/pulser_webhook --adr 'Use HMAC for webhook security'
"""
import os
import sys
import ast
from pathlib import Path
from datetime import datetime


def read_manifest(module_path):
    """Parse __manifest__.py and return dict."""
    manifest_path = module_path / '__manifest__.py'
    if not manifest_path.exists():
        raise FileNotFoundError(f"No __manifest__.py in {module_path}")

    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Safe eval (AST parse)
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == '__manifest__':
                    return ast.literal_eval(node.value)

    raise ValueError("No __manifest__ dict found in __manifest__.py")


def generate_readme(manifest, module_name):
    """Generate README.rst from manifest following OCA template."""
    name = manifest.get('name', module_name)
    summary = manifest.get('summary', 'No summary provided')
    description = manifest.get('description', 'See manifest for detailed description.')
    author = manifest.get('author', 'Unknown')
    license_name = manifest.get('license', 'LGPL-3')

    # Badge URL based on license
    license_badges = {
        'LGPL-3': ('https://img.shields.io/badge/licence-LGPL--3-blue.svg',
                   'http://www.gnu.org/licenses/lgpl-3.0-standalone.html'),
        'AGPL-3': ('https://img.shields.io/badge/licence-AGPL--3-blue.svg',
                   'http://www.gnu.org/licenses/agpl-3.0-standalone.html'),
        'GPL-3': ('https://img.shields.io/badge/licence-GPL--3-blue.svg',
                  'http://www.gnu.org/licenses/gpl-3.0-standalone.html'),
    }

    badge_url, badge_target = license_badges.get(
        license_name,
        ('https://img.shields.io/badge/licence-LGPL--3-blue.svg',
         'http://www.gnu.org/licenses/lgpl-3.0-standalone.html')
    )

    template = f"""{'=' * len(name)}
{name}
{'=' * len(name)}

.. |badge1| image:: {badge_url}
    :target: {badge_target}
    :alt: License: {license_name}

|badge1|

{summary}

**Table of contents**

.. contents::
   :local:

Overview
========

{description}

Configuration
=============

To configure this module, you need to:

1. Go to Settings > Technical > ... (provide specific configuration steps)
2. Configure the required parameters

Usage
=====

To use this module, you need to:

1. Navigate to the appropriate menu
2. Follow the workflow (provide specific usage instructions)

Known Issues / Roadmap
======================

* Feature request 1
* Bug fix 1

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/your-org/your-repo/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smash it by providing detailed and welcomed feedback.

Credits
=======

Authors
~~~~~~~

* {author}

Contributors
~~~~~~~~~~~~

* Your Name <your.email@example.com>

Maintainers
~~~~~~~~~~~

This module is maintained by your organization.

.. image:: https://via.placeholder.com/200x60/4A90E2/FFFFFF?text=Your+Org
   :alt: Your Organization
   :target: https://your-org.com

To contribute to this module, please visit https://your-org.com/contributing.

Disclaimer
==========

This module is provided as-is without warranty. Use at your own risk.
"""
    return template.strip()


def generate_changelog(module_name, version):
    """Generate CHANGELOG.md seed following Keep a Changelog format."""
    template = f"""# Changelog

All notable changes to {module_name} will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Planned features and enhancements

### Changed
- Planned modifications to existing features

### Deprecated
- Features marked for removal in future versions

### Removed
- Features removed in this version

### Fixed
- Bug fixes and patches

### Security
- Security patches and vulnerability fixes

## [{version}] - {datetime.now().strftime('%Y-%m-%d')}

### Added
- Initial release
- Module scaffolding with OCA compliance
- Basic functionality and core features
- Unit tests and integration tests
- Documentation (README, this CHANGELOG)

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- N/A (initial release)

## Development Guidelines

### Version Numbering
- **Major** (X.0.0): Breaking changes, incompatible API changes
- **Minor** (0.X.0): New features, backward-compatible
- **Patch** (0.0.X): Bug fixes, backward-compatible

### Release Process
1. Update CHANGELOG.md with all changes
2. Update version in __manifest__.py
3. Run full test suite: `pytest custom_addons/{module_name}/tests/ -v`
4. Validate OCA compliance: `pre-commit run --all-files`
5. Create git tag: `git tag -a v{version} -m "Release v{version}"`
6. Push changes and tags: `git push origin main --tags`
7. Create GitHub release with CHANGELOG excerpt

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

[Unreleased]: https://github.com/your-org/your-repo/compare/v{version}...HEAD
[{version}]: https://github.com/your-org/your-repo/releases/tag/v{version}
"""
    return template.strip()


def generate_adr(module_name, decision_title):
    """Generate ADR (Architecture Decision Record) following Michael Nygard template."""
    date_str = datetime.now().strftime('%Y%m%d')
    slug = decision_title.lower().replace(' ', '-').replace('_', '-')

    # Extract ADR number from existing ADRs if any
    adr_files = list(Path('.').glob('ADR-*.md'))
    adr_number = len(adr_files) + 1

    template = f"""# ADR-{adr_number:03d}: {decision_title}

**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: Proposed
**Module**: {module_name}

## Context

What is the issue that we're seeing that is motivating this decision or change?

Provide background information including:

- **Problem Statement**: Clear description of the problem being solved
- **Current Situation**: How things work today (if applicable)
- **Requirements**: Key functional and non-functional requirements
- **Constraints**: Technical, business, or regulatory limitations
- **Assumptions**: What we're assuming to be true

### Technical Context

- Odoo version: 16.0 / 17.0 / 18.0
- Dependencies: List of module dependencies
- Integration points: External systems or modules

## Decision

What is the change that we're proposing and/or doing?

Be specific and include:

- **Chosen Solution**: Detailed description of the approach
- **Implementation Details**: Key technical decisions and patterns
- **Why This Approach**: Rationale for choosing this over alternatives
- **Scope**: What is included and excluded from this decision

### Technical Specification

```python
# Example code or configuration
class Example(models.Model):
    _name = 'example.model'

    field_name = fields.Char(string="Field")
```

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive Consequences

- ✅ **Benefit 1**: Description of how this helps
- ✅ **Benefit 2**: Another advantage
- ✅ **Benefit 3**: System improvement

### Negative Consequences

- ❌ **Trade-off 1**: What we're giving up
- ❌ **Trade-off 2**: Added complexity or constraints
- ❌ **Technical Debt**: New debt introduced

### Neutral Consequences

- ℹ️ **Change 1**: Neither clearly positive nor negative
- ℹ️ **Change 2**: Shifts in patterns or approach

### Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Risk description | Low/Med/High | Low/Med/High | Mitigation strategy |

## Alternatives Considered

### Alternative 1: [Name]

**Description**: Brief description of the alternative

**Pros**:
- Advantage 1
- Advantage 2

**Cons**:
- Disadvantage 1
- Disadvantage 2

**Rejection Reason**: Why this wasn't chosen

### Alternative 2: [Name]

**Description**: Brief description of the alternative

**Pros**:
- Advantage 1

**Cons**:
- Disadvantage 1

**Rejection Reason**: Why this wasn't chosen

## Implementation Notes

*(Fill in when status changes to Accepted)*

### Migration Path

If replacing an existing system:

1. Step 1: Preparation
2. Step 2: Gradual rollout
3. Step 3: Validation
4. Step 4: Deprecation of old system

### Rollout Strategy

- **Phase 1**: Development and testing
- **Phase 2**: Staging environment validation
- **Phase 3**: Production deployment
- **Phase 4**: Monitoring and optimization

### Success Metrics

- Metric 1: Target value
- Metric 2: Target value
- Metric 3: Target value

### Monitoring and Validation

- Health checks: What to monitor
- Performance metrics: Expected thresholds
- Error rates: Acceptable error rates
- Rollback criteria: When to rollback

## References

- [OCA Guidelines](https://github.com/OCA/maintainer-tools/wiki)
- [Related ADR](#): Link to related decisions
- [GitHub Issue #XXX](#): Link to issue
- [External Documentation](#): Relevant external resources
- [Technical Specification](#): Detailed specs

## Decision History

| Date | Status | Author | Notes |
|------|--------|--------|-------|
| {datetime.now().strftime('%Y-%m-%d')} | Proposed | @username | Initial proposal |

---

## Status Definitions

- **Proposed**: Under review and discussion
- **Accepted**: Decision approved and ready for implementation
- **Deprecated**: No longer recommended, superseded by newer ADR
- **Superseded**: Replaced by ADR-XXX (provide link)
- **Rejected**: Considered but not approved

## Review Process

1. **Proposal**: Author creates ADR with status "Proposed"
2. **Review**: Team reviews and provides feedback
3. **Discussion**: Address concerns and iterate
4. **Decision**: Team decides to Accept, Reject, or Request Changes
5. **Implementation**: Update status to "Accepted" and implement
6. **Retrospective**: Review decision after implementation

---

**Authors**: @username
**Reviewers**: @reviewer1, @reviewer2
**Approvers**: @approver1
"""
    return template.strip()


def main():
    """Main entry point for documentation generator."""
    if len(sys.argv) < 2:
        print("Usage: docgen.py <module_path> [--adr 'Decision Title']")
        print("\nExamples:")
        print("  docgen.py custom_addons/expense_approval")
        print("  docgen.py custom_addons/pulser_webhook --adr 'Use HMAC for webhook security'")
        sys.exit(1)

    module_path = Path(sys.argv[1])
    if not module_path.is_dir():
        print(f"Error: {module_path} is not a directory")
        sys.exit(1)

    try:
        # Read manifest
        manifest = read_manifest(module_path)
        module_name = module_path.name
        version = manifest.get('version', '1.0.0')

        # Generate README
        readme_content = generate_readme(manifest, module_name)
        readme_path = module_path / 'README.rst'
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print(f"✅ Generated {readme_path}")

        # Generate CHANGELOG
        changelog_content = generate_changelog(module_name, version)
        changelog_path = module_path / 'CHANGELOG.md'
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(changelog_content)
        print(f"✅ Generated {changelog_path}")

        # Generate ADR if requested
        if '--adr' in sys.argv:
            adr_idx = sys.argv.index('--adr')
            if adr_idx + 1 < len(sys.argv):
                decision_title = sys.argv[adr_idx + 1]
                adr_content = generate_adr(module_name, decision_title)

                # Count existing ADRs for numbering
                adr_files = list(module_path.glob('ADR-*.md'))
                adr_number = len(adr_files) + 1

                slug = decision_title.lower().replace(' ', '-').replace('_', '-')
                adr_path = module_path / f'ADR-{adr_number:03d}-{slug}.md'

                with open(adr_path, 'w', encoding='utf-8') as f:
                    f.write(adr_content)
                print(f"✅ Generated {adr_path}")
            else:
                print("Warning: --adr flag provided but no decision title specified")

        print(f"\n✅ Documentation generation complete for {module_name}")

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

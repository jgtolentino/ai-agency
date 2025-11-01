# Migration Guide: Restructured Repository

This guide explains the restructuring of the ai-agency repository to align with the Microsoft Agent Framework structure.

## Overview

The repository has been restructured to follow modern Python package standards and align with the Microsoft Agent Framework architecture. This provides better modularity, maintainability, and follows industry best practices.

## What Changed

### Directory Structure

**Before:**
```
ai-agency/
├── skills/                    # Skill YAML files
│   ├── odoo-module-dev/
│   ├── odoo-studio-ops/
│   ├── odoo-sh-devops/
│   └── odoo-docker-claude/
├── custom_addons/            # Sample modules
├── knowledge/                # Knowledge base
├── spec/                     # Specifications
├── evals/                    # Evaluation suite
├── infra/                    # Infrastructure
└── README.md
```

**After:**
```
ai-agency/
├── packages/                  # Python packages (NEW)
│   ├── odoo-core/
│   ├── odoo-module-dev/
│   ├── odoo-studio-ops/
│   ├── odoo-sh-devops/
│   └── odoo-docker-claude/
├── samples/                   # Example code (NEW)
│   └── getting_started/
│       ├── agents/
│       ├── workflows/
│       └── tools/
├── tests/                     # Centralized tests (NEW)
│   ├── unit/
│   └── integration/
├── skills/                    # Legacy (DEPRECATED)
├── custom_addons/            # Unchanged
├── knowledge/                # Unchanged
├── spec/                     # Unchanged
├── evals/                    # Unchanged
├── infra/                    # Unchanged
├── pyproject.toml            # Workspace config (NEW)
├── CONTRIBUTING.md           # Contributing guide (NEW)
├── SUPPORT.md                # Support guide (NEW)
└── README.md                 # Updated
```

### Key Changes

#### 1. Package Structure

Skills are now Python packages with proper structure:

- `pyproject.toml` - Package metadata and dependencies
- `README.md` - Package documentation
- `package_name/` - Python module directory
- `tests/` - Package-specific tests

#### 2. Import Changes

**Before (skill-based):**
```bash
# Skills were YAML-based and used by Cline
cline-odoo "Create module..."
```

**After (package-based):**
```python
# Now proper Python packages
from odoo_agent_core import BaseAgent, AgentConfig
from odoo_agent_module_dev import ModuleDevelopmentAgent, ModuleConfig

# Create and use agents programmatically
config = ModuleConfig(name="ModuleDev", module_name="task_priority")
agent = ModuleDevelopmentAgent(config)
result = await agent.run("Create OCA module")
```

#### 3. Installation

**Before:**
```bash
# Clone and symlink
git clone https://github.com/jgtolentino/ai-agency.git
ln -s ~/ai-agency/skills ~/.cline/skills/odoo-expertise
```

**After:**
```bash
# Install as Python packages
pip install -e packages/odoo-core
pip install -e packages/odoo-module-dev
# Or from PyPI (when published)
pip install odoo-agent-framework
```

## Migration Steps

### For Users

#### 1. Update Installation

```bash
# Navigate to repository
cd ~/ai-agency

# Pull latest changes
git pull origin main

# Install packages
pip install -e packages/odoo-core
pip install -e packages/odoo-module-dev

# Install all packages at once
pip install -e .
```

#### 2. Update Code

If you have custom code using the old structure:

```python
# OLD: Skills were external
# No direct Python imports

# NEW: Import packages
from odoo_agent_core import BaseAgent, AgentConfig
from odoo_agent_module_dev import ModuleDevelopmentAgent, ModuleConfig
```

#### 3. Update Configuration

No changes needed for:
- `knowledge/` directory
- `custom_addons/` directory
- `spec/` files
- `evals/` scenarios

### For Contributors

#### 1. Development Setup

```bash
# Clone repository
git clone https://github.com/jgtolentino/ai-agency.git
cd ai-agency

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e packages/odoo-core[dev]
pip install -e packages/odoo-module-dev[dev]

# Install pre-commit hooks
pre-commit install
```

#### 2. Running Tests

```bash
# Run all tests
pytest

# Run specific package tests
pytest packages/odoo-core/tests

# Run with coverage
pytest --cov
```

#### 3. Adding New Packages

See [CONTRIBUTING.md](./CONTRIBUTING.md) for detailed instructions on adding new packages.

### For CI/CD

#### Update Workflows

```yaml
# .github/workflows/ci.yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -e packages/odoo-core[dev]
          pip install -e packages/odoo-module-dev[dev]
      
      - name: Run tests
        run: pytest
      
      - name: Run linters
        run: |
          black --check .
          isort --check .
          flake8 .
```

## Benefits of Restructuring

### 1. **Modularity**
- Each package is independent
- Clear dependencies between packages
- Easy to use individual components

### 2. **Standard Python Packaging**
- Follows PEP 517/518 standards
- Can be published to PyPI
- Standard installation with pip

### 3. **Better Testing**
- Centralized test infrastructure
- Per-package test suites
- Easy to run tests locally and in CI

### 4. **Improved Documentation**
- README for each package
- Clear API documentation
- Example code in samples/

### 5. **Microsoft Framework Alignment**
- Consistent with industry standards
- Familiar structure for developers
- Better integration potential

## Backward Compatibility

### Skills Directory

The `skills/` directory is maintained for backward compatibility but is now **DEPRECATED**.

**Timeline:**
- **Now**: Both structures available
- **v2.1.0**: Deprecation warnings
- **v3.0.0**: Skills directory removed

### Migration Path

1. **Phase 1 (Current)**: Both old and new structures exist
2. **Phase 2 (v2.1.0)**: Add deprecation warnings
3. **Phase 3 (v3.0.0)**: Remove old structure

## Troubleshooting

### Import Errors

```bash
# Error: ModuleNotFoundError: No module named 'odoo_agent_core'

# Solution: Install packages
pip install -e packages/odoo-core
```

### Pre-commit Hook Failures

```bash
# Error: black/isort/flake8 failures

# Solution: Run formatters
black .
isort .

# Or install pre-commit
pre-commit install
pre-commit run --all-files
```

### Test Failures

```bash
# Error: Tests fail after restructuring

# Solution: Reinstall packages
pip install --force-reinstall -e packages/odoo-core
pip install --force-reinstall -e packages/odoo-module-dev

# Run tests
pytest -v
```

## Getting Help

- **Documentation**: See [SUPPORT.md](./SUPPORT.md)
- **Issues**: [GitHub Issues](https://github.com/jgtolentino/ai-agency/issues)
- **Discussions**: [GitHub Discussions](https://github.com/jgtolentino/ai-agency/discussions)

## Feedback

We welcome feedback on this restructuring! Please:

1. Open an issue for bugs or problems
2. Start a discussion for questions or suggestions
3. Submit a PR for improvements

Thank you for using the Odoo AI Agent Framework!

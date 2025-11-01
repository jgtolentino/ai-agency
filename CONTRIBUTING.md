# Contributing to Odoo AI Agent Framework

Thank you for your interest in contributing to the Odoo AI Agent Framework! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please be respectful and constructive in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/ai-agency.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Submit a pull request

## How to Contribute

### Reporting Bugs

- Use the GitHub issue tracker
- Include detailed steps to reproduce
- Provide system information (OS, Python version, etc.)
- Include error messages and stack traces

### Suggesting Enhancements

- Use the GitHub issue tracker with the "enhancement" label
- Clearly describe the feature and its benefits
- Provide examples of how it would be used

### Contributing Code

- Fix bugs
- Implement new features
- Improve documentation
- Add tests
- Optimize performance

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- pip and virtualenv

### Setup Steps

```bash
# Clone the repository
git clone https://github.com/jgtolentino/ai-agency.git
cd ai-agency

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e packages/odoo-core[dev]
pip install -e packages/odoo-module-dev[dev]

# Install pre-commit hooks
pre-commit install
```

## Coding Standards

### Python Style

- Follow PEP 8 style guide
- Use Black for code formatting (line length: 120)
- Use isort for import sorting
- Use type hints where appropriate
- Write docstrings for all public functions and classes

### Example

```python
"""Module for agent configuration."""

from typing import Optional
from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Base configuration for agents.
    
    Args:
        name: Agent name
        version: Agent version
        description: Optional description
    """

    name: str = Field(..., description="Agent name")
    version: str = Field(default="0.1.0", description="Agent version")
    description: Optional[str] = Field(None, description="Agent description")
```

### Commit Messages

Follow conventional commits format:

```
type(scope): brief description

Longer description if needed

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific package tests
pytest packages/odoo-core/tests

# Run with coverage
pytest --cov=odoo_agent_core --cov-report=html
```

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern

```python
def test_agent_initialization():
    """Test that agent initializes correctly."""
    # Arrange
    config = AgentConfig(name="TestAgent", version="1.0.0")
    
    # Act
    agent = BaseAgent(config)
    
    # Assert
    assert agent.name == "TestAgent"
    assert agent.version == "1.0.0"
```

## Submitting Changes

### Pull Request Process

1. Update documentation as needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Run pre-commit hooks
5. Update CHANGELOG.md if applicable
6. Submit pull request with clear description

### Pull Request Checklist

- [ ] Code follows style guidelines
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] Pre-commit hooks pass
- [ ] Commit messages follow convention
- [ ] PR description is clear and complete

### Review Process

- Maintainers will review your PR
- Address any feedback or requested changes
- Once approved, your PR will be merged

## Project Structure

### Package Organization

```
packages/
├── odoo-core/              # Core functionality
│   ├── odoo_agent_core/
│   ├── tests/
│   ├── pyproject.toml
│   └── README.md
└── odoo-module-dev/        # Module development
    ├── odoo_agent_module_dev/
    ├── tests/
    ├── pyproject.toml
    └── README.md
```

### Adding a New Package

1. Create package directory in `packages/`
2. Add `pyproject.toml` with proper metadata
3. Create package module directory
4. Add `__init__.py` and core modules
5. Add tests directory with test files
6. Add README.md with package documentation

## Knowledge Base Contributions

### Adding Citations

1. Follow citation template in `knowledge/notes/citation_template.md`
2. Add to daily note in `knowledge/notes/YYYY-MM-DD.md`
3. Ensure OCA alignment and source quality
4. Update playbooks with validated patterns

### Pattern Documentation

- Document OCA patterns in `knowledge/patterns/`
- Include examples and use cases
- Reference official OCA sources
- Keep patterns up to date

## Questions?

- Open a discussion on GitHub
- Check existing issues and PRs
- Review documentation

Thank you for contributing to the Odoo AI Agent Framework!

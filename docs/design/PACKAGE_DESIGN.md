# Package Design

This document describes the design of individual packages in the Odoo AI Agent Framework.

## Package Philosophy

Each package should:

1. **Have a single responsibility**
2. **Be independently usable**
3. **Follow Python packaging standards**
4. **Include comprehensive tests**
5. **Provide clear documentation**

## Package Structure

### Standard Layout

```
package-name/
├── pyproject.toml              # Package metadata and dependencies
├── README.md                   # Package documentation
├── LICENSE                     # Package license (if different from main)
├── package_module/             # Python module directory
│   ├── __init__.py            # Package exports
│   ├── agent.py               # Main agent implementation
│   ├── config.py              # Configuration classes
│   ├── utils.py               # Utility functions
│   └── constants.py           # Constants and enums
├── tests/                      # Test directory
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_agent.py          # Agent tests
│   ├── test_config.py         # Config tests
│   └── test_utils.py          # Utility tests
└── examples/                   # Optional examples
    └── basic_usage.py
```

### pyproject.toml

Every package should have a complete `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "package-name"
version = "0.1.0"
description = "Description of package"
readme = "README.md"
requires-python = ">=3.10"
license = {text = "Apache-2.0"}
authors = [{name = "Author Name"}]
keywords = ["odoo", "ai", "agent"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python :: 3.10",
]

dependencies = [
    "odoo-agent-core>=0.1.0",
    # Add other dependencies
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
]

[project.urls]
Homepage = "https://github.com/jgtolentino/ai-agency"
Repository = "https://github.com/jgtolentino/ai-agency"
```

## Core Package

### odoo-agent-core

**Purpose**: Provide base classes and utilities for all other packages.

**Key Components**:
- `BaseAgent`: Abstract base class for agents
- `AgentConfig`: Base configuration class
- Utility functions
- Common constants

**Dependencies**: Minimal (pydantic, pyyaml)

**API Stability**: Stable - changes here affect all packages

## Specialized Packages

### odoo-agent-module-dev

**Purpose**: OCA-compliant Odoo module development.

**Key Components**:
- `ModuleDevelopmentAgent`: Module generation agent
- `ModuleConfig`: Module configuration
- Scaffolding utilities
- OCA compliance checks

**Dependencies**: odoo-agent-core

### odoo-agent-studio-ops

**Purpose**: Safe Odoo Studio operations.

**Key Components**:
- `StudioOpsAgent`: Studio operations agent
- `StudioConfig`: Studio configuration
- Export/import utilities
- Rollback mechanisms

**Dependencies**: odoo-agent-core

### odoo-agent-sh-devops

**Purpose**: Odoo.sh deployment automation.

**Key Components**:
- `DeploymentAgent`: Deployment agent
- `DeploymentConfig`: Deployment configuration
- API clients
- Pipeline utilities

**Dependencies**: odoo-agent-core, requests

### odoo-agent-docker

**Purpose**: Docker image and container management.

**Key Components**:
- `DockerAgent`: Docker management agent
- `DockerConfig`: Docker configuration
- Image building utilities
- Container orchestration

**Dependencies**: odoo-agent-core, docker

## Inter-Package Dependencies

```
odoo-agent-core (foundation)
    ↓
    ├── odoo-agent-module-dev
    ├── odoo-agent-studio-ops
    ├── odoo-agent-sh-devops
    └── odoo-agent-docker
```

**Rules**:
1. All packages depend on `odoo-agent-core`
2. Specialized packages don't depend on each other
3. Keep dependency tree flat

## Configuration Design

### Base Configuration

```python
from odoo_agent_core import AgentConfig

class SpecializedConfig(AgentConfig):
    """Extend base configuration."""
    
    # Add specialized fields
    specific_field: str
    optional_field: Optional[int] = None
```

### Configuration Loading

Support multiple configuration sources:

```python
# From dictionary
config = SpecializedConfig(**config_dict)

# From YAML file
with open("config.yaml") as f:
    config = SpecializedConfig(**yaml.safe_load(f))

# From environment variables
config = SpecializedConfig.from_env()
```

## Agent Design

### Base Pattern

```python
from odoo_agent_core import BaseAgent

class SpecializedAgent(BaseAgent):
    """Specialized agent implementation."""
    
    def __init__(self, config: SpecializedConfig):
        super().__init__(config)
        self.specialized_config = config
        # Initialize specialized components
    
    async def run(self, task: str, context=None) -> str:
        """Execute specialized task."""
        # 1. Parse task
        # 2. Validate inputs
        # 3. Execute operations
        # 4. Return result
        pass
```

### Tool Integration

```python
class SpecializedAgent(BaseAgent):
    """Agent with tools."""
    
    def __init__(self, config: SpecializedConfig):
        super().__init__(config)
        self.tools = self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize available tools."""
        return {
            "file_ops": FileOperations(),
            "shell": ShellExecutor(),
        }
    
    async def run(self, task: str, context=None) -> str:
        """Execute with tools."""
        # Use self.tools as needed
        pass
```

## Testing Design

### Test Organization

```python
# tests/conftest.py
import pytest

@pytest.fixture
def agent_config():
    """Provide test configuration."""
    return SpecializedConfig(
        name="TestAgent",
        version="0.1.0"
    )

@pytest.fixture
def agent(agent_config):
    """Provide test agent."""
    return SpecializedAgent(agent_config)

# tests/test_agent.py
import pytest

class TestSpecializedAgent:
    """Test specialized agent."""
    
    async def test_initialization(self, agent_config):
        """Test agent initializes correctly."""
        agent = SpecializedAgent(agent_config)
        assert agent.name == "TestAgent"
    
    async def test_run(self, agent):
        """Test agent executes task."""
        result = await agent.run("test task")
        assert result is not None
```

### Test Coverage

Target coverage levels:
- Overall: >80%
- Core classes: >90%
- Critical paths: 100%

## Documentation Standards

### README Template

Each package README should include:

1. **Title and description**
2. **Features list**
3. **Installation instructions**
4. **Quick start example**
5. **API overview**
6. **License**

### Code Documentation

```python
def function_name(param: str) -> str:
    """One-line summary.
    
    Detailed description if needed.
    
    Args:
        param: Parameter description
        
    Returns:
        Return value description
        
    Raises:
        Exception: When raised
        
    Example:
        >>> result = function_name("test")
        >>> print(result)
        "result"
    """
    pass
```

## Versioning

Follow Semantic Versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Version Synchronization

- Core package: Independent versioning
- Specialized packages: Can have different versions
- Framework: Overall version in root pyproject.toml

## Publishing

### Pre-release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped
- [ ] Examples verified

### PyPI Publishing

```bash
# Build package
python -m build

# Check distribution
twine check dist/*

# Upload to test PyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Maintenance

### Backward Compatibility

- Maintain backward compatibility within major versions
- Deprecate features with warnings
- Document breaking changes clearly

### Security

- Regular dependency updates
- Security scanning
- Vulnerability reporting

## References

- [Python Packaging Guide](https://packaging.python.org/)
- [PEP 517](https://peps.python.org/pep-0517/)
- [PEP 518](https://peps.python.org/pep-0518/)

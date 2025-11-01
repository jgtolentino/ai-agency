# Odoo Agent Core

Core functionality for the Odoo AI Agent Framework - provides base classes, utilities, and shared functionality for building AI agents that work with Odoo.

## Features

- Base agent classes and interfaces
- Configuration management
- Utility functions for Odoo integration
- Common patterns and helpers

## Installation

```bash
pip install odoo-agent-core
```

## Quick Start

```python
from odoo_agent_core import AgentConfig, BaseAgent

# Configure your agent
config = AgentConfig(
    name="MyOdooAgent",
    version="0.1.0"
)

# Create and use agent
agent = BaseAgent(config)
```

## Documentation

For detailed documentation, see the [main repository](https://github.com/jgtolentino/ai-agency).

## License

Apache-2.0

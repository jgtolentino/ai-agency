# Odoo Module Development Agent

Generate OCA-compliant Odoo modules with proper structure, security, tests, and migrations.

## Features

- **OCA Compliance**: Follow OCA guidelines, manifests, licensing (LGPL-3)
- **ORM Patterns**: Proper use of `@api.depends`, `@api.onchange`, `@api.constrains`
- **Security**: `ir.model.access.csv` + record rules with domain expressions
- **Testing**: pytest-odoo with TransactionCase/SavepointCase
- **Migrations**: openupgradelib patterns for version upgrades

## Installation

```bash
pip install odoo-agent-module-dev
```

## Quick Start

```python
from odoo_agent_module_dev import ModuleDevelopmentAgent, ModuleConfig

# Configure the agent
config = ModuleConfig(
    name="ModuleDev",
    module_name="task_priority",
    version="16.0.1.0.0"
)

# Create agent
agent = ModuleDevelopmentAgent(config)

# Generate module
result = await agent.run("Create OCA module with model task.priority")
```

## Agent Capabilities

### ORM
- `_name` vs `_inherit` patterns
- `@api.depends`, `@api.onchange`, `@api.constrains` decorators
- Computed fields, related fields, stored vs non-stored
- Record rules and domain expressions

### Security
- `ir.model.access.csv` (CRUD permissions)
- Record rules (domain-based RLS)
- Field-level security

### Testing
- pytest-odoo test structure
- TransactionCase vs SavepointCase
- Form API for UI testing

## License

Apache-2.0

# Getting Started with Odoo AI Agent Framework

This directory contains examples and tutorials to help you get started with the Odoo AI Agent Framework.

## Quick Start

### 1. Installation

```bash
# Install all packages
pip install -e packages/odoo-core
pip install -e packages/odoo-module-dev

# Or install from PyPI (when published)
pip install odoo-agent-core odoo-agent-module-dev
```

### 2. Basic Agent Example

See [agents/01_simple_agent.py](agents/01_simple_agent.py) for a simple agent example.

### 3. Module Development

See [agents/02_module_dev_agent.py](agents/02_module_dev_agent.py) for OCA module generation.

## Directory Structure

- **agents/**: Basic agent creation and usage examples
- **workflows/**: Multi-agent workflow examples
- **tools/**: Custom tool integration examples

## Prerequisites

- Python 3.10 or higher
- Basic understanding of Odoo development
- API keys for LLM providers (OpenAI, Azure, etc.)

## Next Steps

1. Follow the [agents tutorial](agents/)
2. Explore [workflow patterns](workflows/)
3. Learn about [custom tools](tools/)
4. Check the [main documentation](../../README.md)

## Support

For issues and questions, see the [main repository](https://github.com/jgtolentino/ai-agency).

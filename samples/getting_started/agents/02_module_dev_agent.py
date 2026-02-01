"""Module development agent example - OCA-compliant module generation."""

import asyncio
from odoo_agent_module_dev import ModuleDevelopmentAgent, ModuleConfig


async def main():
    """Main function demonstrating module development agent."""
    # Create module configuration
    config = ModuleConfig(
        name="ModuleDevAgent",
        version="0.1.0",
        module_name="task_priority",
        odoo_version="16.0",
        oca_compliant=True,
        include_tests=True,
        include_migrations=True
    )

    # Initialize agent
    agent = ModuleDevelopmentAgent(config)

    # Generate a module
    task = """
    Create an OCA-compliant module named 'task_priority' with:
    - Model: task.priority
    - Fields: name (Char), level (Integer), color (Char)
    - Security: CRUD permissions for user group
    - Tests: Basic CRUD test cases
    """
    
    result = await agent.run(task)
    print(f"Agent: {agent.name}")
    print(f"Module: {agent.module_config.module_name}")
    print(f"Result: {result}")
    
    # Scaffold module structure
    files = agent.scaffold_module("task_priority")
    print("\nGenerated files:")
    for path, content in files.items():
        print(f"  - {path}")


if __name__ == "__main__":
    asyncio.run(main())

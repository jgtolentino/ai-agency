"""Simple agent example - Basic Odoo agent usage."""

import asyncio
from odoo_agent_core import BaseAgent, AgentConfig


class SimpleOdooAgent(BaseAgent):
    """A simple Odoo agent example."""

    async def run(self, task: str, context=None):
        """Execute a simple task."""
        return f"Executed task: {task}"


async def main():
    """Main function demonstrating simple agent usage."""
    # Create agent configuration
    config = AgentConfig(
        name="SimpleAgent",
        version="0.1.0",
        role="Simple Odoo assistant",
        description="A basic agent for Odoo operations"
    )

    # Initialize agent
    agent = SimpleOdooAgent(config)

    # Run a task
    result = await agent.run("List all installed Odoo modules")
    print(f"Agent: {agent.name}")
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())

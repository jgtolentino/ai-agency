"""Base agent implementation."""

from typing import Any, Dict, Optional
from .config import AgentConfig


class BaseAgent:
    """Base class for Odoo AI agents."""

    def __init__(self, config: AgentConfig):
        """Initialize the agent.
        
        Args:
            config: Agent configuration
        """
        self.config = config
        self.name = config.name
        self.version = config.version

    async def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Run the agent with a given task.
        
        Args:
            task: Task description
            context: Optional context dictionary
            
        Returns:
            Task result
        """
        raise NotImplementedError("Subclasses must implement run()")

    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}(name={self.name}, version={self.version})>"

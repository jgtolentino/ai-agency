"""Odoo Agent Core - Base functionality for Odoo AI agents."""

__version__ = "0.1.0"

from .agent import BaseAgent
from .config import AgentConfig

__all__ = ["BaseAgent", "AgentConfig", "__version__"]

"""Odoo Module Development Agent - OCA-compliant module generation."""

__version__ = "0.1.0"

from .agent import ModuleDevelopmentAgent
from .config import ModuleConfig

__all__ = ["ModuleDevelopmentAgent", "ModuleConfig", "__version__"]

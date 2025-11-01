"""Configuration for module development agent."""

from typing import Optional, List
from pydantic import Field
from odoo_agent_core import AgentConfig


class ModuleConfig(AgentConfig):
    """Configuration for Odoo module development."""

    module_name: str = Field(..., description="Name of the Odoo module to create")
    odoo_version: str = Field(default="16.0", description="Odoo version (16.0, 17.0, 19.0)")
    oca_compliant: bool = Field(default=True, description="Follow OCA guidelines")
    include_tests: bool = Field(default=True, description="Generate test files")
    include_migrations: bool = Field(default=True, description="Generate migration scripts")
    allowed_tools: List[str] = Field(
        default=["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
        description="Allowed tools for the agent"
    )

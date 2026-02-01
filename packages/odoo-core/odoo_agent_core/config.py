"""Configuration management for Odoo agents."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AgentConfig(BaseModel):
    """Base configuration for Odoo agents."""

    model_config = ConfigDict(extra="allow")

    name: str = Field(..., description="Agent name")
    version: str = Field(default="0.1.0", description="Agent version")
    role: Optional[str] = Field(None, description="Agent role description")
    description: Optional[str] = Field(None, description="Agent description")
    license: str = Field(default="Apache-2.0", description="License type")

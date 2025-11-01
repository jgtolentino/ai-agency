"""Tests for agent configuration."""

import pytest
from odoo_agent_core import AgentConfig


def test_agent_config_creation():
    """Test creating basic agent configuration."""
    config = AgentConfig(
        name="TestAgent",
        version="1.0.0",
        role="Test role",
        description="Test description"
    )
    
    assert config.name == "TestAgent"
    assert config.version == "1.0.0"
    assert config.role == "Test role"
    assert config.description == "Test description"
    assert config.license == "Apache-2.0"


def test_agent_config_defaults():
    """Test default values in configuration."""
    config = AgentConfig(name="MinimalAgent")
    
    assert config.name == "MinimalAgent"
    assert config.version == "0.1.0"
    assert config.license == "Apache-2.0"
    assert config.role is None
    assert config.description is None


def test_agent_config_validation():
    """Test configuration validation."""
    # Name is required
    with pytest.raises(Exception):
        AgentConfig()

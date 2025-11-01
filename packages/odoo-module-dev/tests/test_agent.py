"""Tests for module development agent."""

import pytest
from odoo_agent_module_dev import ModuleDevelopmentAgent, ModuleConfig


@pytest.fixture
def module_config():
    """Provide test module configuration."""
    return ModuleConfig(
        name="TestModuleDev",
        module_name="test_module",
        odoo_version="16.0"
    )


@pytest.fixture
def agent(module_config):
    """Provide test agent."""
    return ModuleDevelopmentAgent(module_config)


def test_agent_initialization(module_config):
    """Test agent initializes correctly."""
    agent = ModuleDevelopmentAgent(module_config)
    
    assert agent.name == "TestModuleDev"
    assert agent.module_config.module_name == "test_module"


@pytest.mark.asyncio
async def test_agent_run(agent):
    """Test agent run method."""
    result = await agent.run("Create test module")
    
    # Basic test - actual implementation would do more
    assert result is not None
    assert "test module" in result.lower()


def test_scaffold_module(agent):
    """Test module scaffolding."""
    files = agent.scaffold_module("test_module")
    
    assert isinstance(files, dict)
    assert "__manifest__.py" in files
    assert "__init__.py" in files
    assert "models/__init__.py" in files

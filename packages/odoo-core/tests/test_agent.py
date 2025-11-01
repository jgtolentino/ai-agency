"""Tests for base agent."""

import pytest
from odoo_agent_core import BaseAgent, AgentConfig


@pytest.fixture
def agent_config():
    """Provide test configuration."""
    return AgentConfig(
        name="TestAgent",
        version="1.0.0"
    )


@pytest.fixture
def agent(agent_config):
    """Provide test agent."""
    return BaseAgent(agent_config)


def test_agent_initialization(agent_config):
    """Test that agent initializes correctly."""
    agent = BaseAgent(agent_config)
    
    assert agent.name == "TestAgent"
    assert agent.version == "1.0.0"
    assert agent.config == agent_config


def test_agent_repr(agent):
    """Test agent string representation."""
    repr_str = repr(agent)
    
    assert "BaseAgent" in repr_str
    assert "TestAgent" in repr_str
    assert "1.0.0" in repr_str


@pytest.mark.asyncio
async def test_agent_run_not_implemented(agent):
    """Test that base agent run raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        await agent.run("test task")

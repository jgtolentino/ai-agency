"""Tests for module development configuration."""

import pytest
from odoo_agent_module_dev import ModuleConfig


def test_module_config_creation():
    """Test creating module configuration."""
    config = ModuleConfig(
        name="ModuleDev",
        module_name="task_priority",
        odoo_version="16.0",
        oca_compliant=True,
        include_tests=True
    )
    
    assert config.name == "ModuleDev"
    assert config.module_name == "task_priority"
    assert config.odoo_version == "16.0"
    assert config.oca_compliant is True
    assert config.include_tests is True


def test_module_config_defaults():
    """Test default values."""
    config = ModuleConfig(
        name="ModuleDev",
        module_name="test_module"
    )
    
    assert config.odoo_version == "16.0"
    assert config.oca_compliant is True
    assert config.include_tests is True
    assert config.include_migrations is True


def test_module_config_allowed_tools():
    """Test allowed tools configuration."""
    config = ModuleConfig(
        name="ModuleDev",
        module_name="test_module"
    )
    
    assert "Read" in config.allowed_tools
    assert "Write" in config.allowed_tools
    assert "Edit" in config.allowed_tools

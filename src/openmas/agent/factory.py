"""
OpenMAS Agent Factory

This module provides factory functions and classes for creating, configuring,
and managing OpenMAS agents. It supports different agent types and handles
configuration validation.

Based on specifications in:
- refactoring_work/planning/TASK_basic_agent_framework_implementation.md
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

import yaml

from .base_agent import Agent, AgentConfig, IAgentStateManager, IProtocolAdapter
from .exceptions import AgentConfigurationError, AgentCreationError

# ============================================================================
# Configuration Loading and Validation
# ============================================================================


class ConfigLoader:
    """Handles loading and validation of agent configurations."""

    @staticmethod
    def load_from_file(config_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load configuration from a file.

        Args:
            config_path: Path to configuration file (JSON or YAML)

        Returns:
            Configuration dictionary

        Raises:
            AgentConfigurationError: If file cannot be loaded or parsed
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise AgentConfigurationError(
                f"Configuration file not found: {config_path}"
            )

        try:
            with open(config_path, "r") as f:
                if config_path.suffix.lower() in [".yaml", ".yml"]:
                    return yaml.safe_load(f)
                elif config_path.suffix.lower() == ".json":
                    return json.load(f)
                else:
                    raise AgentConfigurationError(
                        f"Unsupported config file format: {config_path.suffix}"
                    )

        except Exception as e:
            raise AgentConfigurationError(
                f"Failed to load configuration from {config_path}: {e}"
            )

    @staticmethod
    def validate_config(config: Dict[str, Any]) -> None:
        """
        Validate agent configuration.

        Args:
            config: Configuration dictionary to validate

        Raises:
            AgentConfigurationError: If configuration is invalid
        """
        required_fields = ["agent_id", "name"]

        for field in required_fields:
            if field not in config:
                raise AgentConfigurationError(f"Missing required field: {field}")

        # Validate agent_id format
        agent_id = config["agent_id"]
        if not isinstance(agent_id, str) or not agent_id.strip():
            raise AgentConfigurationError("agent_id must be a non-empty string")

        # Validate name
        name = config["name"]
        if not isinstance(name, str) or not name.strip():
            raise AgentConfigurationError("name must be a non-empty string")

        # Validate optional fields
        if "capabilities" in config:
            if not isinstance(config["capabilities"], list):
                raise AgentConfigurationError("capabilities must be a list")

        if "protocol_configs" in config:
            if not isinstance(config["protocol_configs"], dict):
                raise AgentConfigurationError("protocol_configs must be a dictionary")


# ============================================================================
# Agent Factory
# ============================================================================


class AgentFactory:
    """
    Factory for creating and configuring OpenMAS agents.

    Supports different agent types, configuration validation, and dependency injection.
    """

    def __init__(self):
        """Initialize the agent factory."""
        self.logger = logging.getLogger(f"{__name__}.AgentFactory")
        self._agent_types: Dict[str, Type[Agent]] = {}
        self._default_state_manager: Optional[IAgentStateManager] = None
        self._protocol_adapters: Dict[str, IProtocolAdapter] = {}

        # Register default agent type
        self.register_agent_type("base", Agent)

    def register_agent_type(self, type_name: str, agent_class: Type[Agent]) -> None:
        """
        Register a new agent type.

        Args:
            type_name: Name identifier for the agent type
            agent_class: Agent class to register
        """
        self._agent_types[type_name] = agent_class
        self.logger.info(f"Registered agent type: {type_name}")

    def register_protocol_adapter(
        self, protocol_name: str, adapter: IProtocolAdapter
    ) -> None:
        """
        Register a protocol adapter.

        Args:
            protocol_name: Name identifier for the protocol
            adapter: Protocol adapter instance
        """
        self._protocol_adapters[protocol_name] = adapter
        self.logger.info(f"Registered protocol adapter: {protocol_name}")

    def set_default_state_manager(self, state_manager: IAgentStateManager) -> None:
        """
        Set the default state manager for new agents.

        Args:
            state_manager: State manager instance
        """
        self._default_state_manager = state_manager
        self.logger.info("Set default state manager")

    def create_agent_from_config(
        self,
        config: Dict[str, Any],
        agent_type: Optional[str] = None,
        state_manager: Optional[IAgentStateManager] = None,
        protocol_adapters: Optional[Dict[str, IProtocolAdapter]] = None,
    ) -> Agent:
        """
        Create an agent from configuration.

        Args:
            config: Agent configuration dictionary
            agent_type: Type of agent to create (defaults to "base")
            state_manager: State manager instance (optional)
            protocol_adapters: Protocol adapters for this agent (optional)

        Returns:
            Configured agent instance

        Raises:
            AgentCreationError: If agent creation fails
        """
        try:
            # Validate configuration
            ConfigLoader.validate_config(config)

            # Determine agent type
            agent_type = agent_type or config.get("type", "base")
            if agent_type not in self._agent_types:
                raise AgentCreationError(f"Unknown agent type: {agent_type}")

            # Create agent configuration object
            agent_config = AgentConfig(
                agent_id=config["agent_id"],
                name=config["name"],
                protocol_configs=config.get("protocol_configs", {}),
                capabilities=config.get("capabilities", []),
                metadata=config.get("metadata", {}),
            )

            # Determine state manager
            final_state_manager = state_manager or self._default_state_manager

            # Determine protocol adapters
            final_protocol_adapters = protocol_adapters or {}

            # Add registered adapters if agent config specifies them
            for protocol_name in agent_config.protocol_configs.keys():
                if (
                    protocol_name in self._protocol_adapters
                    and protocol_name not in final_protocol_adapters
                ):
                    final_protocol_adapters[protocol_name] = self._protocol_adapters[
                        protocol_name
                    ]

            # Create agent instance
            agent_class = self._agent_types[agent_type]
            agent = agent_class(
                config=agent_config,
                state_manager=final_state_manager,
                protocol_adapters=final_protocol_adapters,
            )

            self.logger.info(
                f"Created agent {agent_config.agent_id} of type {agent_type}"
            )
            return agent

        except Exception as e:
            self.logger.error(f"Failed to create agent: {e}")
            raise AgentCreationError(f"Agent creation failed: {e}")

    def create_agent_from_file(
        self,
        config_path: Union[str, Path],
        agent_type: Optional[str] = None,
        state_manager: Optional[IAgentStateManager] = None,
        protocol_adapters: Optional[Dict[str, IProtocolAdapter]] = None,
    ) -> Agent:
        """
        Create an agent from a configuration file.

        Args:
            config_path: Path to configuration file
            agent_type: Type of agent to create (optional)
            state_manager: State manager instance (optional)
            protocol_adapters: Protocol adapters for this agent (optional)

        Returns:
            Configured agent instance
        """
        config = ConfigLoader.load_from_file(config_path)
        return self.create_agent_from_config(
            config=config,
            agent_type=agent_type,
            state_manager=state_manager,
            protocol_adapters=protocol_adapters,
        )

    def create_simple_agent(
        self,
        agent_id: str,
        name: str,
        capabilities: Optional[List[str]] = None,
        protocol_configs: Optional[Dict[str, Dict[str, Any]]] = None,
        agent_type: str = "base",
    ) -> Agent:
        """
        Create a simple agent with minimal configuration.

        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            capabilities: List of capabilities (optional)
            protocol_configs: Protocol configurations (optional)
            agent_type: Type of agent to create

        Returns:
            Configured agent instance
        """
        config = {
            "agent_id": agent_id,
            "name": name,
            "capabilities": capabilities or [],
            "protocol_configs": protocol_configs or {},
        }

        return self.create_agent_from_config(config, agent_type=agent_type)

    def get_registered_agent_types(self) -> List[str]:
        """Get list of registered agent types."""
        return list(self._agent_types.keys())

    def get_registered_protocol_adapters(self) -> List[str]:
        """Get list of registered protocol adapters."""
        return list(self._protocol_adapters.keys())


# ============================================================================
# Default Factory Instance
# ============================================================================

# Global factory instance for convenience
default_factory = AgentFactory()


# ============================================================================
# Convenience Functions
# ============================================================================


def create_agent_from_config(config: Dict[str, Any], **kwargs) -> Agent:
    """
    Create an agent from configuration using the default factory.

    Args:
        config: Agent configuration dictionary
        **kwargs: Additional arguments passed to factory

    Returns:
        Configured agent instance
    """
    return default_factory.create_agent_from_config(config, **kwargs)


def create_agent_from_file(config_path: Union[str, Path], **kwargs) -> Agent:
    """
    Create an agent from a configuration file using the default factory.

    Args:
        config_path: Path to configuration file
        **kwargs: Additional arguments passed to factory

    Returns:
        Configured agent instance
    """
    return default_factory.create_agent_from_file(config_path, **kwargs)


def create_simple_agent(agent_id: str, name: str, **kwargs) -> Agent:
    """
    Create a simple agent using the default factory.

    Args:
        agent_id: Unique identifier for the agent
        name: Human-readable name for the agent
        **kwargs: Additional arguments passed to factory

    Returns:
        Configured agent instance
    """
    return default_factory.create_simple_agent(agent_id, name, **kwargs)


def register_agent_type(type_name: str, agent_class: Type[Agent]) -> None:
    """Register an agent type with the default factory."""
    default_factory.register_agent_type(type_name, agent_class)


def register_protocol_adapter(protocol_name: str, adapter: IProtocolAdapter) -> None:
    """Register a protocol adapter with the default factory."""
    default_factory.register_protocol_adapter(protocol_name, adapter)

"""
Factory Classes for OpenMAS Agent Body-Brain Separation

This module provides factory classes for creating communicator and reasoning engine
components, supporting proper dependency injection and configuration management.
"""

import logging
from typing import Dict, List, Optional, Any, Set
from .interfaces.communicator import ICommunicator
from .base_agent import IProtocolAdapter
from .interfaces.reasoning import IReasoningEngine
from .communicator import DefaultCommunicator
from .reasoning.simple_reasoning import SimpleReasoningEngine


class CommunicatorFactory:
    """
    Factory for creating ICommunicator implementations.
    
    Provides centralized creation and configuration of communicator components
    while supporting different implementation types and configurations.
    """
    
    @staticmethod
    def create_default_communicator(
        agent_id: str,
        protocol_adapters: Dict[str, "IProtocolAdapter"] | None = None
    ) -> ICommunicator:
        """
        Create a DefaultCommunicator instance.
        
        Args:
            agent_id: ID of the agent this communicator serves
            protocol_adapters: Dictionary of protocol adapters
            
        Returns:
            Configured DefaultCommunicator instance
        """
        return DefaultCommunicator(agent_id, protocol_adapters)
    
    @staticmethod
    def create_communicator(
        communicator_type: str,
        agent_id: str,
        config: Dict[str, Any] | None = None
    ) -> ICommunicator:
        """
        Create a communicator based on type specification.
        
        Args:
            communicator_type: Type of communicator to create
            agent_id: ID of the agent this communicator serves
            config: Configuration dictionary
            
        Returns:
            Configured communicator instance
            
        Raises:
            ValueError: If communicator_type is not supported
        """
        config = config or {}
        
        if communicator_type == "default":
            protocol_adapters = config.get("protocol_adapters", {})
            return DefaultCommunicator(agent_id, protocol_adapters)
        else:
            raise ValueError(f"Unsupported communicator type: {communicator_type}")


class ReasoningEngineFactory:
    """
    Factory for creating IReasoningEngine implementations.
    
    Provides centralized creation and configuration of reasoning engine components
    while supporting different reasoning paradigms and configurations.
    """
    
    @staticmethod
    def create_simple_reasoning_engine(
        capabilities: Set[str] | None = None
    ) -> IReasoningEngine:
        """
        Create a SimpleReasoningEngine instance.
        
        Args:
            capabilities: Set of capabilities the reasoning engine supports
            
        Returns:
            Configured SimpleReasoningEngine instance
        """
        return SimpleReasoningEngine(capabilities)
    
    @staticmethod
    def create_reasoning_engine(
        reasoning_type: str,
        config: Dict[str, Any] | None = None
    ) -> IReasoningEngine:
        """
        Create a reasoning engine based on type specification.
        
        Args:
            reasoning_type: Type of reasoning engine to create
            config: Configuration dictionary
            
        Returns:
            Configured reasoning engine instance
            
        Raises:
            ValueError: If reasoning_type is not supported
        """
        config = config or {}
        
        if reasoning_type == "simple" or reasoning_type == "rule-based":
            capabilities = set(config.get("capabilities", []))
            return SimpleReasoningEngine(capabilities)
        else:
            raise ValueError(f"Unsupported reasoning type: {reasoning_type}")


class AgentComponentFactory:
    """
    High-level factory for creating complete agent component sets.
    
    Provides convenient methods for creating properly configured communicator
    and reasoning engine pairs for different agent configurations.
    """
    
    def __init__(self):
        """Initialize the agent component factory."""
        self.logger = logging.getLogger("openmas.factories.agent")
    
    def create_basic_components(
        self,
        agent_id: str,
        capabilities: Set[str] | None = None,
        protocol_adapters: Dict[str, "IProtocolAdapter"] | None = None
    ) -> tuple[ICommunicator, IReasoningEngine]:
        """
        Create basic agent components with default implementations.
        
        Args:
            agent_id: ID of the agent
            capabilities: Set of capabilities for the reasoning engine
            protocol_adapters: Dictionary of protocol adapters for communicator
            
        Returns:
            Tuple of (communicator, reasoning_engine)
        """
        communicator = CommunicatorFactory.create_default_communicator(
            agent_id, protocol_adapters
        )
        
        reasoning_engine = ReasoningEngineFactory.create_simple_reasoning_engine(
            capabilities
        )
        
        self.logger.info(f"Created basic components for agent {agent_id}")
        return communicator, reasoning_engine
    
    def create_components_from_config(
        self,
        agent_id: str,
        config: Dict[str, Any]
    ) -> tuple[ICommunicator, IReasoningEngine]:
        """
        Create agent components from configuration dictionary.
        
        Args:
            agent_id: ID of the agent
            config: Configuration dictionary with keys:
                - communicator: Dict with type and config
                - reasoning: Dict with type and config
                
        Returns:
            Tuple of (communicator, reasoning_engine)
        """
        # Extract communicator configuration
        communicator_config = config.get("communicator", {"type": "default"})
        communicator_type = communicator_config.get("type", "default")
        communicator_params = communicator_config.get("config", {})
        
        # Extract reasoning engine configuration
        reasoning_config = config.get("reasoning", {"type": "simple"})
        reasoning_type = reasoning_config.get("type", "simple")
        reasoning_params = reasoning_config.get("config", {})
        
        # Create components
        communicator = CommunicatorFactory.create_communicator(
            communicator_type, agent_id, communicator_params
        )
        
        reasoning_engine = ReasoningEngineFactory.create_reasoning_engine(
            reasoning_type, reasoning_params
        )
        
        self.logger.info(
            f"Created components for agent {agent_id}: "
            f"communicator={communicator_type}, reasoning={reasoning_type}"
        )
        
        return communicator, reasoning_engine

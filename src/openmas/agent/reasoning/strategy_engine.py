"""
Strategy-Enabled Reasoning Engine for OpenMAS Strategy Pattern Integration

This module provides the StrategyReasoningEngine class that implements the
IReasoningEngine interface using the Strategy pattern, enabling runtime
switching between different reasoning approaches.

Based on specifications in:
- refactoring_work/planning/01_READY_TO_START/TASK_strategy_pattern_reasoning_remediation.md
"""

import logging
from typing import Any, Dict, Set
from ..interfaces.reasoning import IReasoningEngine
from .strategy import ReasoningStrategy, ReasoningContext, ReasoningType
from .context import ReasoningStrategyContext
from .rule_based_strategy import RuleBasedReasoningStrategy


class StrategyReasoningEngine(IReasoningEngine):
    """
    Reasoning engine implementation using Strategy pattern.
    
    Integrates the Strategy pattern with the existing IReasoningEngine interface,
    enabling runtime switching between different reasoning approaches while
    maintaining compatibility with the Agent framework.
    """
    
    def __init__(self, default_strategy: ReasoningStrategy | None = None):
        """
        Initialize strategy reasoning engine.
        
        Args:
            default_strategy: Initial reasoning strategy to use.
                             If None, creates a basic rule-based strategy.
        """
        if default_strategy is None:
            # Create default rule-based strategy
            default_strategy = RuleBasedReasoningStrategy({
                "capabilities": ["message_handling", "basic_reasoning"],
                "rules": [],
                "default_actions": {
                    "TEXT": {
                        "type": "text",
                        "content": {"message": "Message processed with rule-based reasoning"}
                    },
                    "USER_QUERY": {
                        "type": "text", 
                        "content": {"message": "Query processed with rule-based reasoning"}
                    },
                    "default": {
                        "type": "text",
                        "content": {"message": "Message processed with default reasoning"}
                    }
                }
            })
        
        self.strategy_context = ReasoningStrategyContext(default_strategy)
        self.logger = logging.getLogger("openmas.reasoning.strategy_engine")
        
        self.logger.info(f"Initialized strategy reasoning engine with {default_strategy.get_reasoning_type().value} strategy")
    
    async def decide_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make reasoning decision using current strategy.
        
        Converts the standard context format to ReasoningContext for strategy processing,
        then converts the result back to the standard format expected by the Agent.
        
        Args:
            context: Standardized context dictionary from communicator
            
        Returns:
            Action dictionary with standard format
        """
        # Convert context to ReasoningContext format
        reasoning_context = ReasoningContext(
            message_type=context.get("message_type", "unknown"),
            payload=context.get("content", {}),
            sender=context.get("sender", "unknown"),
            session_id=context.get("session"),
            agent_capabilities=context.get("metadata", {}).get("agent_capabilities"),
            agent_state=context.get("metadata", {}).get("agent_state")
        )
        
        # Add invocation-specific context if present
        if "invocation_name" in context:
            reasoning_context.payload["invocation_name"] = context["invocation_name"]
        if "arguments" in context:
            reasoning_context.payload["arguments"] = context["arguments"]
        
        self.logger.debug(f"Processing {reasoning_context.message_type} with {self.get_reasoning_type()} strategy")
        
        # Execute reasoning through strategy context
        result = await self.strategy_context.reason(reasoning_context)
        
        # Convert back to standard format
        return {
            "type": result.action_type,
            "content": result.content,
            "sender": context.get("metadata", {}).get("target_agent_id", "agent"),
            "session": context.get("session", "default"),
            "target": context.get("sender", "unknown"),
            "confidence": result.confidence,
            "reasoning_trace": result.reasoning_trace
        }
    
    async def update_knowledge(self, knowledge: Dict[str, Any]) -> None:
        """
        Update current strategy's knowledge base.
        
        Args:
            knowledge: Knowledge update dictionary
        """
        await self.strategy_context.update_knowledge(knowledge)
        self.logger.debug(f"Updated knowledge for {self.get_reasoning_type()} strategy")
    
    async def get_capabilities(self) -> Set[str]:
        """
        Get capabilities of current strategy.
        
        Returns:
            Set of capability names from current strategy
        """
        return await self.strategy_context.get_capabilities()
    
    def get_reasoning_type(self) -> str:
        """
        Get current reasoning strategy type as string.
        
        Returns:
            String representation of current strategy type
        """
        return self.strategy_context.get_current_strategy_type().value
    
    def set_reasoning_strategy(self, strategy: ReasoningStrategy) -> None:
        """
        Set a new reasoning strategy.
        
        Args:
            strategy: New reasoning strategy to use
        """
        strategy_type = strategy.get_reasoning_type()
        self.strategy_context.add_strategy(strategy)
        self.strategy_context.set_strategy(strategy_type)
        
        self.logger.info(f"Switched to {strategy_type.value} reasoning strategy")
    
    def switch_strategy(self, strategy_type: ReasoningType) -> None:
        """
        Switch to an existing reasoning strategy by type.
        
        Args:
            strategy_type: Type of strategy to switch to
            
        Raises:
            ValueError: If strategy type is not available
        """
        self.strategy_context.set_strategy(strategy_type)
        self.logger.info(f"Switched to {strategy_type.value} reasoning strategy")
    
    def add_strategy(self, strategy: ReasoningStrategy) -> None:
        """
        Add a new reasoning strategy to available strategies.
        
        Args:
            strategy: Reasoning strategy to add
        """
        self.strategy_context.add_strategy(strategy)
        strategy_type = strategy.get_reasoning_type()
        self.logger.info(f"Added {strategy_type.value} reasoning strategy")
    
    def get_available_strategies(self) -> list[ReasoningType]:
        """
        Get list of available reasoning strategy types.
        
        Returns:
            List of available strategy types
        """
        return self.strategy_context.get_available_strategies()
    
    def get_current_strategy(self) -> ReasoningStrategy:
        """
        Get the current reasoning strategy instance.
        
        Returns:
            Current reasoning strategy
        """
        return self.strategy_context.current_strategy
    
    def get_strategy_history(self) -> list[ReasoningType]:
        """
        Get history of strategy switches.
        
        Returns:
            List of strategy types in chronological order
        """
        return self.strategy_context.get_strategy_history()
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the strategy engine.
        
        Returns:
            Dictionary with engine and strategy information
        """
        return {
            "engine_type": "strategy_reasoning_engine",
            "current_strategy": self.get_reasoning_type(),
            "available_strategies": [t.value for t in self.get_available_strategies()],
            "strategy_history": [t.value for t in self.get_strategy_history()],
            "context_info": self.strategy_context.get_context_info()
        }

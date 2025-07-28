"""
Strategy Context Management for OpenMAS Reasoning Engine Strategy Pattern

This module provides the ReasoningStrategyContext class that manages reasoning
strategies and enables runtime switching between different reasoning approaches.

Based on specifications in:
- refactoring_work/planning/01_READY_TO_START/TASK_strategy_pattern_reasoning_remediation.md
"""

import logging
from typing import Any, Dict, List
from .strategy import ReasoningStrategy, ReasoningContext, ReasoningResult, ReasoningType


class ReasoningStrategyContext:
    """
    Context for managing reasoning strategies.
    
    Provides runtime strategy switching and manages the lifecycle of different
    reasoning strategies while maintaining a consistent interface.
    """
    
    def __init__(self, default_strategy: ReasoningStrategy):
        """
        Initialize strategy context with a default strategy.
        
        Args:
            default_strategy: The initial reasoning strategy to use
        """
        self.current_strategy = default_strategy
        self.available_strategies: Dict[ReasoningType, ReasoningStrategy] = {
            default_strategy.get_reasoning_type(): default_strategy
        }
        self.strategy_history: List[ReasoningType] = [default_strategy.get_reasoning_type()]
        self.logger = logging.getLogger("openmas.reasoning.context")
        
        self.logger.info(f"Initialized reasoning context with {default_strategy.get_reasoning_type().value} strategy")
    
    def add_strategy(self, strategy: ReasoningStrategy) -> None:
        """
        Add a new reasoning strategy to the available strategies.
        
        Args:
            strategy: Reasoning strategy to add
        """
        strategy_type = strategy.get_reasoning_type()
        self.available_strategies[strategy_type] = strategy
        self.logger.info(f"Added {strategy_type.value} reasoning strategy")
    
    def set_strategy(self, strategy_type: ReasoningType) -> None:
        """
        Switch to a different reasoning strategy.
        
        Args:
            strategy_type: Type of reasoning strategy to switch to
            
        Raises:
            ValueError: If the requested strategy type is not available
        """
        if strategy_type not in self.available_strategies:
            available_types = [t.value for t in self.available_strategies.keys()]
            raise ValueError(
                f"Reasoning strategy '{strategy_type.value}' not available. "
                f"Available strategies: {available_types}"
            )
        
        old_strategy = self.current_strategy.get_reasoning_type()
        self.current_strategy = self.available_strategies[strategy_type]
        self.strategy_history.append(strategy_type)
        
        self.logger.info(f"Reasoning strategy changed from {old_strategy.value} to {strategy_type.value}")
    
    async def reason(self, context: ReasoningContext) -> ReasoningResult:
        """
        Execute reasoning using current strategy.
        
        Args:
            context: Reasoning context
            
        Returns:
            Reasoning result from current strategy
        """
        self.logger.debug(f"Executing reasoning with {self.current_strategy.get_reasoning_type().value} strategy")
        return await self.current_strategy.reason(context)
    
    async def update_knowledge(self, knowledge: Dict[str, Any]) -> None:
        """
        Update knowledge base of current strategy.
        
        Args:
            knowledge: Knowledge update dictionary
        """
        await self.current_strategy.update_knowledge(knowledge)
        self.logger.debug(f"Updated knowledge base for {self.current_strategy.get_reasoning_type().value} strategy")
    
    async def get_capabilities(self) -> set[str]:
        """
        Get capabilities of current strategy.
        
        Returns:
            Set of capability names from current strategy
        """
        return await self.current_strategy.get_capabilities()
    
    def get_current_strategy_type(self) -> ReasoningType:
        """
        Get the type of the current reasoning strategy.
        
        Returns:
            Current strategy type
        """
        return self.current_strategy.get_reasoning_type()
    
    def get_available_strategies(self) -> List[ReasoningType]:
        """
        Get list of available reasoning strategy types.
        
        Returns:
            List of available strategy types
        """
        return list(self.available_strategies.keys())
    
    def get_strategy_history(self) -> List[ReasoningType]:
        """
        Get history of strategy switches.
        
        Returns:
            List of strategy types in chronological order
        """
        return self.strategy_history.copy()
    
    def get_context_info(self) -> Dict[str, Any]:
        """
        Get information about the strategy context.
        
        Returns:
            Dictionary with context metadata
        """
        return {
            "current_strategy": self.current_strategy.get_reasoning_type().value,
            "available_strategies": [t.value for t in self.available_strategies.keys()],
            "strategy_history": [t.value for t in self.strategy_history],
            "current_strategy_info": self.current_strategy.get_strategy_info()
        }

"""
Strategy Pattern Foundation for OpenMAS Reasoning Engine Abstraction

This module provides the abstract base class and supporting types for implementing
the Strategy Pattern in reasoning engines, enabling runtime swapping of reasoning
approaches while maintaining clean separation from communication protocols.

Based on specifications in:
- refactoring_work/planning/01_READY_TO_START/TASK_strategy_pattern_reasoning_remediation.md
- refactoring_work/design/01_architecture/architectural_patterns.md (lines 495-535)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class ReasoningType(Enum):
    """Enumeration of supported reasoning types."""
    RULE_BASED = "rule_based"
    LLM_BASED = "llm_based"
    BDI = "bdi"
    HYBRID = "hybrid"
    MOCK = "mock"


@dataclass
class ReasoningContext:
    """Context information for reasoning decisions."""
    message_type: str
    payload: Dict[str, Any]
    sender: str
    session_id: Optional[str] = None
    agent_capabilities: Optional[List[str]] = None
    agent_state: Optional[Dict[str, Any]] = None


@dataclass
class ReasoningResult:
    """Result of reasoning process."""
    action_type: str
    content: Dict[str, Any]
    confidence: float = 1.0
    reasoning_trace: Optional[List[str]] = None


class ReasoningStrategy(ABC):
    """
    Abstract base class for reasoning strategies.
    
    Defines the interface for different reasoning approaches that can be
    swapped at runtime. Each strategy encapsulates a specific reasoning
    paradigm (rule-based, LLM, BDI, etc.) while remaining protocol-agnostic.
    """
    
    def __init__(self, config: Dict[str, Any] | None = None):
        """
        Initialize reasoning strategy.
        
        Args:
            config: Strategy-specific configuration dictionary
        """
        self.config = config or {}
        self.knowledge_base: Dict[str, Any] = {}
    
    @abstractmethod
    async def reason(self, context: ReasoningContext) -> ReasoningResult:
        """
        Execute reasoning process based on context.
        
        Core reasoning method that processes context and returns a decision.
        This method should contain the strategy's specific reasoning logic.
        
        Args:
            context: Reasoning context with message information
            
        Returns:
            Reasoning result with action decision and metadata
        """
        pass
    
    @abstractmethod
    def get_reasoning_type(self) -> ReasoningType:
        """
        Get the type of this reasoning strategy.
        
        Returns:
            ReasoningType enum value identifying this strategy
        """
        pass
    
    @abstractmethod
    async def update_knowledge(self, knowledge: Dict[str, Any]) -> None:
        """
        Update strategy's knowledge base.
        
        Args:
            knowledge: Knowledge update dictionary
        """
        pass
    
    @abstractmethod
    async def get_capabilities(self) -> Set[str]:
        """
        Get set of capabilities this strategy supports.
        
        Returns:
            Set of capability names
        """
        pass
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """
        Get information about this strategy.
        
        Returns:
            Dictionary with strategy metadata
        """
        return {
            "type": self.get_reasoning_type().value,
            "config": self.config,
            "knowledge_items": len(self.knowledge_base)
        }

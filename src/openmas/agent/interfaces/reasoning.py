"""
IReasoningEngine Interface for OpenMAS Agent Body-Brain Separation

This module defines the IReasoningEngine interface that represents the "brain" of an agent,
handling all decision-making logic while remaining agnostic to communication protocols.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Set


class IReasoningEngine(ABC):
    """
    Interface for agent reasoning logic (brain).
    
    The reasoning engine handles all decision-making and cognitive processes
    while remaining completely agnostic to communication protocols. This
    enables reasoning agnosticism and supports multiple reasoning paradigms
    (rule-based, BDI, LLM, hybrid, etc.).
    """
    
    @abstractmethod
    async def decide_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make reasoning decision based on context.
        
        Core reasoning method that processes context from the communicator
        and returns an action decision. This method should contain all the
        agent's decision-making logic.
        
        Args:
            context: Standardized context dictionary from communicator:
            - message_type: str
            - content: Any
            - sender: str
            - session: str
            - metadata: Dict[str, Any]
            
        Returns:
            Action dictionary with keys:
            - type: str (e.g., "text", "invocation", "error")
            - content: Any
            - sender: str
            - session: str
        """
        pass
    
    @abstractmethod
    async def update_knowledge(self, knowledge: Dict[str, Any]) -> None:
        """
        Update reasoning engine's knowledge base.
        
        Args:
            knowledge: Knowledge update dictionary
        """
        pass
    
    @abstractmethod
    async def get_capabilities(self) -> Set[str]:
        """
        Get set of capabilities this reasoning engine supports.
        
        Returns:
            Set of capability names
        """
        pass
    
    @abstractmethod
    def get_reasoning_type(self) -> str:
        """
        Get type of reasoning engine.
        
        Returns:
            Reasoning type identifier (e.g., 'rule-based', 'llm', 'bdi', 'hybrid')
        """
        pass

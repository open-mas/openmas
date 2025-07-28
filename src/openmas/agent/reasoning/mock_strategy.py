"""
Mock Reasoning Strategy Implementation for OpenMAS Strategy Pattern

This module provides the MockReasoningStrategy class that implements
predictable mock reasoning for testing and development purposes.

Based on specifications in:
- refactoring_work/planning/01_READY_TO_START/TASK_strategy_pattern_reasoning_remediation.md
"""

import logging
from typing import Any, Dict, Set
from .strategy import ReasoningStrategy, ReasoningContext, ReasoningResult, ReasoningType


class MockReasoningStrategy(ReasoningStrategy):
    """
    Mock reasoning strategy for testing and development.
    
    Provides predictable, controllable responses for testing scenarios
    while maintaining the same interface as other reasoning strategies.
    """
    
    def __init__(self, config: Dict[str, Any] | None = None):
        """
        Initialize mock reasoning strategy.
        
        Args:
            config: Configuration dictionary with optional keys:
                - mock_responses: Dictionary of predefined responses
                - capabilities: Set of supported capabilities
                - default_response: Default response when no mock is defined
                - always_succeed: Whether to always return success responses
        """
        super().__init__(config)
        self.mock_responses: Dict[str, Dict[str, Any]] = self.config.get("mock_responses", {})
        self.capabilities: Set[str] = set(self.config.get("capabilities", ["mock_capability", "testing"]))
        self.default_response: Dict[str, Any] = self.config.get("default_response", {
            "action_type": "text",
            "content": {"message": "Mock reasoning response"}
        })
        self.always_succeed: bool = self.config.get("always_succeed", True)
        self.call_count: int = 0
        self.call_history: list[Dict[str, Any]] = []
        self.logger = logging.getLogger("openmas.reasoning.mock")
        
        self.logger.info(f"Initialized mock strategy with {len(self.mock_responses)} predefined responses")
    
    def get_reasoning_type(self) -> ReasoningType:
        """Get reasoning type."""
        return ReasoningType.MOCK
    
    async def reason(self, context: ReasoningContext) -> ReasoningResult:
        """
        Execute mock reasoning.
        
        Returns predefined responses based on context or default mock responses.
        Tracks all calls for testing verification.
        """
        self.call_count += 1
        reasoning_trace = [f"Mock reasoning call #{self.call_count}"]
        
        # Record call for testing verification
        call_record = {
            "call_number": self.call_count,
            "message_type": context.message_type,
            "sender": context.sender,
            "payload": context.payload,
            "session_id": context.session_id
        }
        self.call_history.append(call_record)
        
        self.logger.debug(f"Mock reasoning processing call #{self.call_count} for {context.message_type}")
        
        # Check for specific mock response based on message type
        mock_key = f"{context.message_type}_{context.sender}"
        if mock_key in self.mock_responses:
            reasoning_trace.append(f"Using specific mock response for {mock_key}")
            response = self.mock_responses[mock_key]
            return ReasoningResult(
                action_type=response.get("action_type", "text"),
                content=response.get("content", {"message": "Specific mock response"}),
                confidence=response.get("confidence", 1.0),
                reasoning_trace=reasoning_trace
            )
        
        # Check for message type mock response
        if context.message_type in self.mock_responses:
            reasoning_trace.append(f"Using message type mock response for {context.message_type}")
            response = self.mock_responses[context.message_type]
            return ReasoningResult(
                action_type=response.get("action_type", "text"),
                content=response.get("content", {"message": "Message type mock response"}),
                confidence=response.get("confidence", 1.0),
                reasoning_trace=reasoning_trace
            )
        
        # Handle capability invocations
        if context.message_type == "CAPABILITY_INVOCATION":
            capability_name = context.payload.get("invocation_name") or context.payload.get("capability")
            
            if capability_name in self.capabilities or self.always_succeed:
                reasoning_trace.append(f"Mock capability execution: {capability_name}")
                return ReasoningResult(
                    action_type="invocation_result",
                    content={
                        "invocation_name": capability_name,
                        "result": {
                            "status": "success",
                            "message": f"Mock execution of {capability_name}",
                            "call_count": self.call_count,
                            "mock_data": {"test": True, "reasoning_type": "mock"}
                        }
                    },
                    confidence=1.0,
                    reasoning_trace=reasoning_trace
                )
            else:
                reasoning_trace.append(f"Mock capability not found: {capability_name}")
                return ReasoningResult(
                    action_type="error",
                    content={
                        "error_code": "MOCK_CAPABILITY_NOT_FOUND",
                        "error_message": f"Mock strategy: capability '{capability_name}' not found"
                    },
                    confidence=1.0,
                    reasoning_trace=reasoning_trace
                )
        
        # Default mock response
        reasoning_trace.append("Using default mock response")
        return ReasoningResult(
            action_type=self.default_response.get("action_type", "text"),
            content=self.default_response.get("content", {
                "message": f"Mock reasoning processed {context.message_type} (call #{self.call_count})"
            }),
            confidence=self.default_response.get("confidence", 1.0),
            reasoning_trace=reasoning_trace
        )
    
    async def update_knowledge(self, knowledge: Dict[str, Any]) -> None:
        """
        Update mock strategy knowledge base.
        
        Can update mock responses, capabilities, and configuration.
        """
        if "mock_responses" in knowledge:
            self.mock_responses.update(knowledge["mock_responses"])
            self.logger.info(f"Updated mock responses: {list(knowledge['mock_responses'].keys())}")
        
        if "capabilities" in knowledge:
            new_capabilities = knowledge["capabilities"]
            if isinstance(new_capabilities, (list, set)):
                self.capabilities.update(new_capabilities)
                self.logger.info(f"Added mock capabilities: {new_capabilities}")
        
        if "default_response" in knowledge:
            self.default_response = knowledge["default_response"]
            self.logger.info("Updated default mock response")
        
        if "always_succeed" in knowledge:
            self.always_succeed = bool(knowledge["always_succeed"])
            self.logger.info(f"Updated always_succeed to: {self.always_succeed}")
        
        # Update general knowledge base
        self.knowledge_base.update(knowledge)
    
    async def get_capabilities(self) -> Set[str]:
        """Get set of capabilities this strategy supports."""
        return self.capabilities.copy()
    
    def add_mock_response(self, key: str, response: Dict[str, Any]) -> None:
        """
        Add a mock response for a specific key.
        
        Args:
            key: Response key (e.g., message type or "message_type_sender")
            response: Mock response dictionary
        """
        self.mock_responses[key] = response
        self.logger.info(f"Added mock response for key: {key}")
    
    def remove_mock_response(self, key: str) -> bool:
        """
        Remove a mock response by key.
        
        Args:
            key: Response key to remove
            
        Returns:
            True if response was removed, False if not found
        """
        if key in self.mock_responses:
            del self.mock_responses[key]
            self.logger.info(f"Removed mock response for key: {key}")
            return True
        return False
    
    def get_call_count(self) -> int:
        """
        Get the number of times this strategy has been called.
        
        Returns:
            Number of reasoning calls
        """
        return self.call_count
    
    def get_call_history(self) -> list[Dict[str, Any]]:
        """
        Get the history of all reasoning calls.
        
        Returns:
            List of call records
        """
        return self.call_history.copy()
    
    def reset_call_tracking(self) -> None:
        """Reset call count and history for testing."""
        self.call_count = 0
        self.call_history.clear()
        self.logger.info("Reset mock strategy call tracking")
    
    def get_mock_info(self) -> Dict[str, Any]:
        """
        Get information about the mock strategy state.
        
        Returns:
            Dictionary with mock strategy metadata
        """
        return {
            "call_count": self.call_count,
            "mock_responses_count": len(self.mock_responses),
            "mock_response_keys": list(self.mock_responses.keys()),
            "always_succeed": self.always_succeed,
            "capabilities_count": len(self.capabilities)
        }

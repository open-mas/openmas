"""
Simple Reasoning Engine Implementation for OpenMAS Agent Body-Brain Separation

This module provides the SimpleReasoningEngine class that implements basic rule-based
reasoning while remaining agnostic to communication protocols.
"""

import logging
from typing import Any, Dict, Set
from ..interfaces.reasoning import IReasoningEngine


class SimpleReasoningEngine(IReasoningEngine):
    """
    Simple rule-based reasoning engine for basic agent behavior.
    
    Provides basic decision-making capabilities using rule-based logic
    while remaining completely agnostic to communication protocols.
    This serves as a foundation for more sophisticated reasoning engines.
    """
    
    def __init__(self, capabilities: Set[str] | None = None):
        """
        Initialize simple reasoning engine.
        
        Args:
            capabilities: Set of capabilities this reasoning engine supports
        """
        self.capabilities = capabilities or set()
        self.knowledge_base: Dict[str, Any] = {}
        self.logger = logging.getLogger("openmas.reasoning.simple")
        
    async def decide_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean decision making interface.
        
        Converts context format to reasoning decision using simple rule-based logic.
        This method contains the agent's decision-making logic while remaining
        completely agnostic to communication protocols.
        """
        message_type = context.get("message_type", "unknown")
        content = context.get("content", {})
        sender = context.get("sender", "unknown")
        session = context.get("session", "default")
        
        self.logger.debug(f"Processing {message_type} message from {sender}")
        
        # Handle capability invocation
        if message_type == "CAPABILITY_INVOCATION":
            invocation_name = context.get("invocation_name")
            arguments = context.get("arguments", {})
            
            if invocation_name in self.capabilities:
                try:
                    result = await self._execute_capability(invocation_name, arguments)
                    return {
                        "type": "invocation_result",
                        "content": {
                            "invocation_name": invocation_name,
                            "result": result
                        },
                        "sender": context.get("metadata", {}).get("target_agent_id", "agent"),  
                        "session": session,
                        "target": sender  
                    }
                except Exception as e:
                    return {
                        "type": "error",
                        "content": {
                            "error_code": "CAPABILITY_EXECUTION_ERROR",
                            "error_message": str(e)
                        },
                        "sender": context.get("metadata", {}).get("target_agent_id", "agent"),  
                        "session": session,
                        "target": sender  
                    }
            else:
                return {
                    "type": "error",
                    "content": {
                        "error_code": "CAPABILITY_NOT_FOUND",
                        "error_message": f"Capability '{invocation_name}' not supported"
                    },
                    "sender": context.get("metadata", {}).get("target_agent_id", "agent"),  
                    "session": session,
                    "target": sender  
                }
        
        # Handle user query
        elif message_type == "USER_QUERY":
            response_content = await self._process_user_query(content, context)
            return {
                "type": "text",
                "content": {"message": response_content},
                "sender": context.get("metadata", {}).get("target_agent_id", "agent"),  
                "session": session,
                "target": sender  
            }
        
        # Handle text message
        elif message_type == "PLAIN_TEXT_MESSAGE":
            response_content = await self._process_text_message(content, context)
            return {
                "type": "text",
                "content": {"message": response_content},
                "sender": context.get("metadata", {}).get("target_agent_id", "agent"),  
                "session": session,
                "target": sender  
            }
        
        # Default response for unknown message types
        return {
            "type": "text",
            "content": {"message": f"Received {message_type} message. Processing..."},
            "sender": context.get("metadata", {}).get("target_agent_id", "agent"),  
            "session": session,
            "target": sender  
        }
    
    async def update_knowledge(self, knowledge: Dict[str, Any]) -> None:
        """
        Update reasoning engine's knowledge base.
        
        Simple implementation that merges new knowledge into the knowledge base.
        """
        self.knowledge_base.update(knowledge)
        self.logger.debug(f"Knowledge base updated with {len(knowledge)} items")
    
    async def get_capabilities(self) -> Set[str]:
        """
        Get set of capabilities this reasoning engine supports.
        """
        return self.capabilities.copy()
    
    def get_reasoning_type(self) -> str:
        """
        Get type of reasoning engine.
        """
        return "rule-based"
    
    async def _execute_capability(self, capability_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a capability with the given arguments.
        
        This is a simple implementation that can be extended for specific capabilities.
        """
        self.logger.info(f"Executing capability: {capability_name}")
        
        # Simple capability implementations
        if capability_name == "echo":
            return {"echo": arguments.get("message", "No message provided")}
        elif capability_name == "status":
            return {
                "status": "active",
                "capabilities": list(self.capabilities),
                "knowledge_items": len(self.knowledge_base)
            }
        elif capability_name == "calculate":
            # Simple calculator capability
            operation = arguments.get("operation")
            operands = arguments.get("operands", [])
            
            if operation == "add" and len(operands) >= 2:
                return {"result": sum(operands)}
            elif operation == "multiply" and len(operands) >= 2:
                result = 1
                for operand in operands:
                    result *= operand
                return {"result": result}
            else:
                raise ValueError(f"Unsupported operation: {operation}")
        else:
            # Generic capability execution
            return {
                "capability": capability_name,
                "arguments": arguments,
                "executed": True,
                "reasoning_type": self.get_reasoning_type()
            }
    
    async def _process_user_query(self, content: Any, context: Dict[str, Any]) -> str:
        """
        Process user query and generate response.
        
        Simple implementation that provides basic query processing.
        """
        query = str(content)
        
        # Simple query processing rules
        if "hello" in query.lower() or "hi" in query.lower():
            return "Hello! I'm a simple reasoning agent. How can I help you?"
        elif "capabilities" in query.lower():
            caps = ", ".join(self.capabilities) if self.capabilities else "none"
            return f"My capabilities are: {caps}"
        elif "status" in query.lower():
            return f"I'm active and running with {len(self.knowledge_base)} knowledge items."
        else:
            return f"I received your query: '{query}'. I'm processing it with simple rule-based reasoning."
    
    async def _process_text_message(self, content: Any, context: Dict[str, Any]) -> str:
        """
        Process text message and generate response.
        
        Simple implementation for handling text messages.
        """
        message = str(content)
        sender = context.get("sender", "unknown")
        
        return f"Message received from {sender}: '{message}'. Thank you for the communication."

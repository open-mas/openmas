"""
LLM-Based Reasoning Strategy Implementation for OpenMAS Strategy Pattern

This module provides the LLMReasoningStrategy class that implements
LLM-based reasoning for natural language understanding while remaining protocol-agnostic.

Based on specifications in:
- refactoring_work/planning/01_READY_TO_START/TASK_strategy_pattern_reasoning_remediation.md
"""

import json
import logging
from typing import Any, Dict, Set
from .strategy import ReasoningStrategy, ReasoningContext, ReasoningResult, ReasoningType


class LLMReasoningStrategy(ReasoningStrategy):
    """
    LLM-based reasoning strategy for natural language understanding.
    
    Implements reasoning using language model patterns for complex natural
    language processing and decision-making scenarios.
    """
    
    def __init__(self, config: Dict[str, Any] | None = None):
        """
        Initialize LLM-based reasoning strategy.
        
        Args:
            config: Configuration dictionary with optional keys:
                - model_name: Name of the LLM model to use
                - system_prompt: System prompt for the LLM
                - capabilities: Set of supported capabilities
                - temperature: Sampling temperature for responses
                - max_tokens: Maximum tokens for responses
        """
        super().__init__(config)
        self.model_name: str = self.config.get("model_name", "simulated-llm")
        self.system_prompt: str = self.config.get("system_prompt", self._get_default_system_prompt())
        self.capabilities: Set[str] = set(self.config.get("capabilities", [
            "natural_language_processing", "text_analysis", "question_answering"
        ]))
        self.temperature: float = self.config.get("temperature", 0.7)
        self.max_tokens: int = self.config.get("max_tokens", 150)
        self.logger = logging.getLogger("openmas.reasoning.llm")
        
        self.logger.info(f"Initialized LLM strategy with model '{self.model_name}' and {len(self.capabilities)} capabilities")
    
    def get_reasoning_type(self) -> ReasoningType:
        """Get reasoning type."""
        return ReasoningType.LLM_BASED
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for LLM reasoning."""
        return """You are an intelligent agent reasoning engine. 
        Analyze the given context and decide on the appropriate action.
        Respond with JSON containing 'action_type' and 'content' fields.
        Be helpful, accurate, and concise in your responses."""
    
    async def reason(self, context: ReasoningContext) -> ReasoningResult:
        """
        Execute LLM-based reasoning.
        
        Uses language model patterns to process natural language and
        generate appropriate responses based on context.
        """
        reasoning_trace = ["Starting LLM-based reasoning"]
        
        # Prepare prompt for LLM processing
        prompt = self._build_prompt(context)
        reasoning_trace.append(f"Built prompt for {self.model_name}")
        
        self.logger.debug(f"Processing {context.message_type} message with LLM reasoning")
        
        try:
            # Simulate LLM processing (in real implementation, this would call actual LLM)
            llm_response = await self._simulate_llm_processing(prompt, context)
            reasoning_trace.append("LLM processing completed")
            
            # Parse LLM response
            if isinstance(llm_response, dict):
                return ReasoningResult(
                    action_type=llm_response.get("action_type", "text"),
                    content=llm_response.get("content", {"message": "LLM response processed"}),
                    confidence=llm_response.get("confidence", 0.8),
                    reasoning_trace=reasoning_trace
                )
            else:
                # Handle text response
                return ReasoningResult(
                    action_type="text",
                    content={"message": str(llm_response)},
                    confidence=0.7,
                    reasoning_trace=reasoning_trace
                )
                
        except Exception as e:
            reasoning_trace.append(f"LLM processing error: {str(e)}")
            self.logger.error(f"LLM reasoning error: {e}")
            
            return ReasoningResult(
                action_type="error",
                content={
                    "error_code": "LLM_PROCESSING_ERROR",
                    "error_message": f"LLM reasoning failed: {str(e)}"
                },
                confidence=0.1,
                reasoning_trace=reasoning_trace
            )
    
    def _build_prompt(self, context: ReasoningContext) -> str:
        """
        Build prompt for LLM processing.
        
        Args:
            context: Reasoning context
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = [
            self.system_prompt,
            "",
            f"Message Type: {context.message_type}",
            f"Sender: {context.sender}",
            f"Session: {context.session_id or 'default'}",
            f"Payload: {json.dumps(context.payload, indent=2)}",
        ]
        
        if context.agent_capabilities:
            prompt_parts.append(f"Available Capabilities: {', '.join(context.agent_capabilities)}")
        
        if context.agent_state:
            prompt_parts.append(f"Agent State: {json.dumps(context.agent_state, indent=2)}")
        
        prompt_parts.extend([
            "",
            "Please analyze this context and provide an appropriate response.",
            "Format your response as JSON with 'action_type' and 'content' fields."
        ])
        
        return "\n".join(prompt_parts)
    
    async def _simulate_llm_processing(self, prompt: str, context: ReasoningContext) -> Dict[str, Any]:
        """
        Simulate LLM processing for demonstration purposes.
        
        In a real implementation, this would call an actual LLM API.
        
        Args:
            prompt: Formatted prompt string
            context: Reasoning context
            
        Returns:
            Simulated LLM response
        """
        message_type = context.message_type
        payload = context.payload
        
        # Simulate different response patterns based on message type
        if message_type == "CAPABILITY_INVOCATION":
            capability_name = payload.get("invocation_name") or payload.get("capability")
            if capability_name in self.capabilities:
                return {
                    "action_type": "invocation_result",
                    "content": {
                        "invocation_name": capability_name,
                        "result": {
                            "status": "success",
                            "message": f"LLM processed capability: {capability_name}",
                            "reasoning_type": "llm_based"
                        }
                    },
                    "confidence": 0.85
                }
            else:
                return {
                    "action_type": "error",
                    "content": {
                        "error_code": "CAPABILITY_NOT_FOUND",
                        "error_message": f"LLM strategy does not support capability: {capability_name}"
                    },
                    "confidence": 0.9
                }
        
        elif message_type == "USER_QUERY":
            query_text = str(payload.get("content", ""))
            return {
                "action_type": "text",
                "content": {
                    "message": f"LLM Analysis: I understand you're asking about '{query_text}'. "
                              f"Based on my natural language processing capabilities, I can help you with this query."
                },
                "confidence": 0.8
            }
        
        elif message_type == "TEXT":
            text_content = str(payload.get("content", ""))
            return {
                "action_type": "text",
                "content": {
                    "message": f"LLM Response: I've processed your message '{text_content}' using natural language understanding. "
                              f"How can I assist you further?"
                },
                "confidence": 0.75
            }
        
        else:
            return {
                "action_type": "text",
                "content": {
                    "message": f"LLM processed {message_type} message using advanced natural language reasoning."
                },
                "confidence": 0.7
            }
    
    async def update_knowledge(self, knowledge: Dict[str, Any]) -> None:
        """
        Update LLM strategy knowledge base.
        
        Can update system prompt, capabilities, and model parameters.
        """
        if "system_prompt" in knowledge:
            self.system_prompt = knowledge["system_prompt"]
            self.logger.info("Updated system prompt")
        
        if "capabilities" in knowledge:
            new_capabilities = knowledge["capabilities"]
            if isinstance(new_capabilities, (list, set)):
                self.capabilities.update(new_capabilities)
                self.logger.info(f"Added capabilities: {new_capabilities}")
        
        if "model_name" in knowledge:
            self.model_name = knowledge["model_name"]
            self.logger.info(f"Updated model name to: {self.model_name}")
        
        if "temperature" in knowledge:
            self.temperature = float(knowledge["temperature"])
            self.logger.info(f"Updated temperature to: {self.temperature}")
        
        if "max_tokens" in knowledge:
            self.max_tokens = int(knowledge["max_tokens"])
            self.logger.info(f"Updated max_tokens to: {self.max_tokens}")
        
        # Update general knowledge base
        self.knowledge_base.update(knowledge)
    
    async def get_capabilities(self) -> Set[str]:
        """Get set of capabilities this strategy supports."""
        return self.capabilities.copy()
    
    def update_system_prompt(self, new_prompt: str) -> None:
        """
        Update the system prompt for LLM processing.
        
        Args:
            new_prompt: New system prompt string
        """
        self.system_prompt = new_prompt
        self.logger.info("System prompt updated")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the LLM model configuration.
        
        Returns:
            Dictionary with model configuration
        """
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "system_prompt_length": len(self.system_prompt)
        }

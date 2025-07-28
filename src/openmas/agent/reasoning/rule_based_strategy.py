"""
Rule-Based Reasoning Strategy Implementation for OpenMAS Strategy Pattern

This module provides the RuleBasedReasoningStrategy class that implements
rule-based reasoning using if-then-else logic while remaining protocol-agnostic.

Based on specifications in:
- refactoring_work/planning/01_READY_TO_START/TASK_strategy_pattern_reasoning_remediation.md
"""

import logging
from typing import Any, Dict, List, Set
from .strategy import ReasoningStrategy, ReasoningContext, ReasoningResult, ReasoningType


class RuleBasedReasoningStrategy(ReasoningStrategy):
    """
    Rule-based reasoning strategy using if-then-else logic.
    
    Implements deterministic reasoning based on predefined rules and patterns.
    Suitable for scenarios requiring predictable, explainable decision-making.
    """
    
    def __init__(self, config: Dict[str, Any] | None = None):
        """
        Initialize rule-based reasoning strategy.
        
        Args:
            config: Configuration dictionary with optional keys:
                - rules: List of rule dictionaries
                - default_actions: Default actions for different message types
                - capabilities: Set of supported capabilities
        """
        super().__init__(config)
        self.rules: List[Dict[str, Any]] = self.config.get("rules", [])
        self.default_actions: Dict[str, Dict[str, Any]] = self.config.get("default_actions", {})
        self.capabilities: Set[str] = set(self.config.get("capabilities", ["message_handling"]))
        self.logger = logging.getLogger("openmas.reasoning.rule_based")
        
        self.logger.info(f"Initialized rule-based strategy with {len(self.rules)} rules and {len(self.capabilities)} capabilities")
    
    def get_reasoning_type(self) -> ReasoningType:
        """Get reasoning type."""
        return ReasoningType.RULE_BASED
    
    async def reason(self, context: ReasoningContext) -> ReasoningResult:
        """
        Execute rule-based reasoning.
        
        Applies rules in order and returns the first matching action,
        or falls back to default actions based on message type.
        """
        reasoning_trace = ["Starting rule-based reasoning"]
        message_type = context.message_type
        payload = context.payload
        
        self.logger.debug(f"Processing {message_type} message with rule-based reasoning")
        
        # Check capabilities first for capability invocation messages
        if message_type == "CAPABILITY_INVOCATION":
            capability_name = payload.get("invocation_name") or payload.get("capability")
            if capability_name and capability_name not in self.capabilities:
                reasoning_trace.append(f"Capability {capability_name} not supported")
                return ReasoningResult(
                    action_type="error",
                    content={
                        "error_code": "CAPABILITY_NOT_FOUND",
                        "error_message": f"Capability '{capability_name}' not supported"
                    },
                    confidence=1.0,
                    reasoning_trace=reasoning_trace
                )
        
        # Apply custom rules
        for i, rule in enumerate(self.rules):
            if await self._evaluate_rule(rule, context):
                reasoning_trace.append(f"Rule {i+1} matched: {rule.get('name', 'unnamed')}")
                action = rule.get("action", {})
                return ReasoningResult(
                    action_type=action.get("type", "text"),
                    content=action.get("content", {"message": "Rule executed"}),
                    confidence=rule.get("confidence", 0.9),
                    reasoning_trace=reasoning_trace
                )
        
        # Apply default actions based on message type
        reasoning_trace.append(f"No rules matched, applying default action for {message_type}")
        default_action = self.default_actions.get(
            message_type,
            self.default_actions.get("default", {
                "type": "text",
                "content": {"message": f"Processed {message_type} message with rule-based reasoning"}
            })
        )
        
        return ReasoningResult(
            action_type=default_action.get("type", "text"),
            content=default_action.get("content", {"message": "Default response"}),
            confidence=0.5,
            reasoning_trace=reasoning_trace
        )
    
    async def _evaluate_rule(self, rule: Dict[str, Any], context: ReasoningContext) -> bool:
        """
        Evaluate if a rule matches the current context.
        
        Args:
            rule: Rule dictionary with conditions
            context: Current reasoning context
            
        Returns:
            True if rule matches, False otherwise
        """
        conditions = rule.get("conditions", {})
        
        # Check message type condition
        if "message_type" in conditions:
            if context.message_type != conditions["message_type"]:
                return False
        
        # Check sender condition
        if "sender" in conditions:
            if context.sender != conditions["sender"]:
                return False
        
        # Check payload conditions
        if "payload" in conditions:
            payload_conditions = conditions["payload"]
            for key, expected_value in payload_conditions.items():
                if key not in context.payload or context.payload[key] != expected_value:
                    return False
        
        # Check capability condition for capability invocations
        if "capability" in conditions:
            capability_name = context.payload.get("invocation_name") or context.payload.get("capability")
            if capability_name != conditions["capability"]:
                return False
        
        # Check content pattern condition
        if "content_pattern" in conditions:
            content = str(context.payload.get("content", "")).lower()
            pattern = conditions["content_pattern"].lower()
            if pattern not in content:
                return False
        
        return True
    
    async def update_knowledge(self, knowledge: Dict[str, Any]) -> None:
        """
        Update rule-based knowledge base.
        
        Can update rules, default actions, and capabilities dynamically.
        """
        if "rules" in knowledge:
            new_rules = knowledge["rules"]
            if isinstance(new_rules, list):
                self.rules.extend(new_rules)
                self.logger.info(f"Added {len(new_rules)} new rules")
        
        if "default_actions" in knowledge:
            self.default_actions.update(knowledge["default_actions"])
            self.logger.info("Updated default actions")
        
        if "capabilities" in knowledge:
            new_capabilities = knowledge["capabilities"]
            if isinstance(new_capabilities, (list, set)):
                self.capabilities.update(new_capabilities)
                self.logger.info(f"Added capabilities: {new_capabilities}")
        
        # Update general knowledge base
        self.knowledge_base.update(knowledge)
    
    async def get_capabilities(self) -> Set[str]:
        """Get set of capabilities this strategy supports."""
        return self.capabilities.copy()
    
    def add_rule(self, rule: Dict[str, Any]) -> None:
        """
        Add a new rule to the strategy.
        
        Args:
            rule: Rule dictionary with conditions and action
        """
        self.rules.append(rule)
        self.logger.info(f"Added new rule: {rule.get('name', 'unnamed')}")
    
    def remove_rule(self, rule_name: str) -> bool:
        """
        Remove a rule by name.
        
        Args:
            rule_name: Name of the rule to remove
            
        Returns:
            True if rule was removed, False if not found
        """
        for i, rule in enumerate(self.rules):
            if rule.get("name") == rule_name:
                removed_rule = self.rules.pop(i)
                self.logger.info(f"Removed rule: {rule_name}")
                return True
        return False
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """
        Get copy of current rules.
        
        Returns:
            List of rule dictionaries
        """
        return self.rules.copy()

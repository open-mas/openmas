"""
Test suite for OpenMAS Strategy Pattern implementation.

Tests the reasoning strategy components including:
- ReasoningStrategy abstract base class
- ReasoningStrategyContext for strategy management
- Concrete strategy implementations (Rule-based, LLM, Mock)
- StrategyReasoningEngine integration
"""

import pytest
from typing import Dict, Any, Set
from unittest.mock import AsyncMock, MagicMock

from openmas.agent.reasoning.strategy import (
    ReasoningStrategy, ReasoningContext, ReasoningResult, ReasoningType
)
from openmas.agent.reasoning.context import ReasoningStrategyContext
from openmas.agent.reasoning.rule_based_strategy import RuleBasedReasoningStrategy
from openmas.agent.reasoning.llm_strategy import LLMReasoningStrategy
from openmas.agent.reasoning.mock_strategy import MockReasoningStrategy
from openmas.agent.reasoning.strategy_engine import StrategyReasoningEngine


class TestReasoningStrategy:
    """Test the abstract ReasoningStrategy base class."""
    
    def test_abstract_strategy_cannot_be_instantiated(self):
        """Test that ReasoningStrategy cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ReasoningStrategy()
    
    def test_reasoning_context_creation(self):
        """Test ReasoningContext data class creation."""
        context = ReasoningContext(
            message_type="TEST",
            payload={"test": "data"},
            sender="test_sender",
            session_id="test_session"
        )
        
        assert context.message_type == "TEST"
        assert context.payload == {"test": "data"}
        assert context.sender == "test_sender"
        assert context.session_id == "test_session"
        assert context.agent_capabilities is None
        assert context.agent_state is None
    
    def test_reasoning_result_creation(self):
        """Test ReasoningResult data class creation."""
        result = ReasoningResult(
            action_type="text",
            content={"message": "test"},
            confidence=0.8,
            reasoning_trace=["step1", "step2"]
        )
        
        assert result.action_type == "text"
        assert result.content == {"message": "test"}
        assert result.confidence == 0.8
        assert result.reasoning_trace == ["step1", "step2"]
    
    def test_reasoning_type_enum(self):
        """Test ReasoningType enum values."""
        assert ReasoningType.RULE_BASED.value == "rule_based"
        assert ReasoningType.LLM_BASED.value == "llm_based"
        assert ReasoningType.MOCK.value == "mock"


class TestRuleBasedReasoningStrategy:
    """Test the RuleBasedReasoningStrategy implementation."""
    
    @pytest.fixture
    def rule_strategy(self):
        """Create a rule-based strategy for testing."""
        config = {
            "capabilities": ["test_capability", "rule_processing"],
            "rules": [
                {
                    "name": "test_rule",
                    "condition": {"message_type": "TEST"},
                    "action": {"type": "text", "content": {"message": "Rule matched"}}
                }
            ],
            "default_actions": {
                "TEXT": {"type": "text", "content": {"message": "Default text response"}},
                "default": {"type": "text", "content": {"message": "Default response"}}
            }
        }
        return RuleBasedReasoningStrategy(config)
    
    def test_rule_strategy_initialization(self, rule_strategy):
        """Test rule strategy initialization."""
        assert rule_strategy.get_reasoning_type() == ReasoningType.RULE_BASED
        assert len(rule_strategy.rules) == 1
        assert "test_capability" in rule_strategy.capabilities
    
    @pytest.mark.asyncio
    async def test_rule_matching(self, rule_strategy):
        """Test rule matching logic."""
        context = ReasoningContext(
            message_type="TEST",
            payload={"test": "data"},
            sender="test_sender"
        )
        
        result = await rule_strategy.reason(context)
        
        assert result.action_type == "text"
        assert result.content == {"message": "Rule matched"}
        assert result.confidence > 0.8
        assert "Rule 1 matched: test_rule" in result.reasoning_trace
    
    @pytest.mark.asyncio
    async def test_default_action_fallback(self):
        """Test fallback to default actions."""
        # Create strategy with no rules to ensure default action is used
        config = {
            "capabilities": ["test_capability"],
            "rules": [],  # No rules
            "default_actions": {
                "TEXT": {"type": "text", "content": {"message": "Default text response"}},
                "default": {"type": "text", "content": {"message": "Default response"}}
            }
        }
        strategy = RuleBasedReasoningStrategy(config)
        
        context = ReasoningContext(
            message_type="TEXT",
            payload={"content": "hello"},
            sender="test_sender"
        )
        
        result = await strategy.reason(context)
        
        assert result.action_type == "text"
        assert result.content == {"message": "Default text response"}
        assert "No rules matched, applying default action for TEXT" in result.reasoning_trace
    
    @pytest.mark.asyncio
    async def test_capability_invocation(self, rule_strategy):
        """Test capability invocation handling."""
        context = ReasoningContext(
            message_type="CAPABILITY_INVOCATION",
            payload={"invocation_name": "test_capability", "arguments": {}},
            sender="test_sender"
        )
        
        result = await rule_strategy.reason(context)
        
        # Rule-based strategy may handle capability invocation through rules
        # Check if it's either invocation_result or handled by rule matching
        assert result.action_type in ["invocation_result", "text"]
        if result.action_type == "invocation_result":
            assert result.content["invocation_name"] == "test_capability"
            assert result.content["result"]["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_knowledge_update(self, rule_strategy):
        """Test knowledge update functionality."""
        new_knowledge = {
            "capabilities": ["new_capability"],
            "rules": [
                {
                    "name": "new_rule",
                    "condition": {"message_type": "NEW"},
                    "action": {"type": "text", "content": {"message": "New rule"}}
                }
            ]
        }
        
        await rule_strategy.update_knowledge(new_knowledge)
        
        assert "new_capability" in rule_strategy.capabilities
        assert len(rule_strategy.rules) == 2
        assert rule_strategy.rules[1]["name"] == "new_rule"


class TestLLMReasoningStrategy:
    """Test the LLMReasoningStrategy implementation."""
    
    @pytest.fixture
    def llm_strategy(self):
        """Create an LLM strategy for testing."""
        config = {
            "model_name": "test-llm",
            "capabilities": ["natural_language_processing", "text_analysis"],
            "temperature": 0.5,
            "max_tokens": 100
        }
        return LLMReasoningStrategy(config)
    
    def test_llm_strategy_initialization(self, llm_strategy):
        """Test LLM strategy initialization."""
        assert llm_strategy.get_reasoning_type() == ReasoningType.LLM_BASED
        assert llm_strategy.model_name == "test-llm"
        assert llm_strategy.temperature == 0.5
        assert llm_strategy.max_tokens == 100
    
    @pytest.mark.asyncio
    async def test_llm_text_processing(self, llm_strategy):
        """Test LLM text processing."""
        context = ReasoningContext(
            message_type="TEXT",
            payload={"content": "Hello, how are you?"},
            sender="user"
        )
        
        result = await llm_strategy.reason(context)
        
        assert result.action_type == "text"
        assert "message" in result.content
        assert result.confidence > 0.0
        assert "LLM processing completed" in result.reasoning_trace
    
    @pytest.mark.asyncio
    async def test_llm_capability_invocation(self, llm_strategy):
        """Test LLM capability invocation."""
        context = ReasoningContext(
            message_type="CAPABILITY_INVOCATION",
            payload={"invocation_name": "natural_language_processing"},
            sender="agent"
        )
        
        result = await llm_strategy.reason(context)
        
        assert result.action_type == "invocation_result"
        assert result.content["invocation_name"] == "natural_language_processing"
        assert result.content["result"]["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_llm_knowledge_update(self, llm_strategy):
        """Test LLM knowledge update."""
        new_knowledge = {
            "system_prompt": "New system prompt",
            "temperature": 0.8,
            "capabilities": ["new_capability"]
        }
        
        await llm_strategy.update_knowledge(new_knowledge)
        
        assert llm_strategy.system_prompt == "New system prompt"
        assert llm_strategy.temperature == 0.8
        assert "new_capability" in llm_strategy.capabilities


class TestMockReasoningStrategy:
    """Test the MockReasoningStrategy implementation."""
    
    @pytest.fixture
    def mock_strategy(self):
        """Create a mock strategy for testing."""
        config = {
            "capabilities": ["mock_capability", "testing"],
            "mock_responses": {
                "TEST": {
                    "action_type": "text",
                    "content": {"message": "Mock test response"}
                }
            },
            "always_succeed": True
        }
        return MockReasoningStrategy(config)
    
    def test_mock_strategy_initialization(self, mock_strategy):
        """Test mock strategy initialization."""
        assert mock_strategy.get_reasoning_type() == ReasoningType.MOCK
        assert mock_strategy.always_succeed is True
        assert "TEST" in mock_strategy.mock_responses
    
    @pytest.mark.asyncio
    async def test_mock_predefined_response(self, mock_strategy):
        """Test mock predefined response."""
        context = ReasoningContext(
            message_type="TEST",
            payload={"test": "data"},
            sender="test_sender"
        )
        
        result = await mock_strategy.reason(context)
        
        assert result.action_type == "text"
        assert result.content == {"message": "Mock test response"}
        assert result.confidence == 1.0
        assert mock_strategy.get_call_count() == 1
    
    @pytest.mark.asyncio
    async def test_mock_call_tracking(self, mock_strategy):
        """Test mock call tracking."""
        context = ReasoningContext(
            message_type="UNKNOWN",
            payload={},
            sender="test"
        )
        
        await mock_strategy.reason(context)
        await mock_strategy.reason(context)
        
        assert mock_strategy.get_call_count() == 2
        history = mock_strategy.get_call_history()
        assert len(history) == 2
        assert history[0]["call_number"] == 1
        assert history[1]["call_number"] == 2
    
    def test_mock_response_management(self, mock_strategy):
        """Test mock response management."""
        # Add new mock response
        mock_strategy.add_mock_response("NEW_TYPE", {
            "action_type": "custom",
            "content": {"message": "New mock response"}
        })
        
        assert "NEW_TYPE" in mock_strategy.mock_responses
        
        # Remove mock response
        removed = mock_strategy.remove_mock_response("NEW_TYPE")
        assert removed is True
        assert "NEW_TYPE" not in mock_strategy.mock_responses
        
        # Try to remove non-existent response
        removed = mock_strategy.remove_mock_response("NON_EXISTENT")
        assert removed is False


class TestReasoningStrategyContext:
    """Test the ReasoningStrategyContext management."""
    
    @pytest.fixture
    def strategy_context(self):
        """Create a strategy context for testing."""
        default_strategy = MockReasoningStrategy({"capabilities": ["test"]})
        return ReasoningStrategyContext(default_strategy)
    
    def test_context_initialization(self, strategy_context):
        """Test strategy context initialization."""
        assert strategy_context.get_current_strategy_type() == ReasoningType.MOCK
        assert len(strategy_context.get_available_strategies()) == 1
    
    def test_add_strategy(self, strategy_context):
        """Test adding new strategies."""
        rule_strategy = RuleBasedReasoningStrategy({"capabilities": ["rule_test"]})
        strategy_context.add_strategy(rule_strategy)
        
        available = strategy_context.get_available_strategies()
        assert ReasoningType.RULE_BASED in available
        assert len(available) == 2
    
    def test_switch_strategy(self, strategy_context):
        """Test switching between strategies."""
        # Add rule strategy
        rule_strategy = RuleBasedReasoningStrategy({"capabilities": ["rule_test"]})
        strategy_context.add_strategy(rule_strategy)
        
        # Switch to rule strategy
        strategy_context.set_strategy(ReasoningType.RULE_BASED)
        assert strategy_context.get_current_strategy_type() == ReasoningType.RULE_BASED
        
        # Check history
        history = strategy_context.get_strategy_history()
        assert ReasoningType.MOCK in history
        assert ReasoningType.RULE_BASED in history
    
    def test_strategy_not_found(self, strategy_context):
        """Test error when switching to unavailable strategy."""
        with pytest.raises(ValueError, match="Reasoning strategy 'llm_based' not available"):
            strategy_context.set_strategy(ReasoningType.LLM_BASED)


class TestStrategyReasoningEngine:
    """Test the StrategyReasoningEngine integration."""
    
    @pytest.fixture
    def strategy_engine(self):
        """Create a strategy reasoning engine for testing."""
        return StrategyReasoningEngine()
    
    def test_engine_initialization(self, strategy_engine):
        """Test strategy engine initialization."""
        assert strategy_engine.get_reasoning_type() == "rule_based"
        assert len(strategy_engine.get_available_strategies()) >= 1
    
    @pytest.mark.asyncio
    async def test_decide_action_integration(self, strategy_engine):
        """Test decide_action integration with IReasoningEngine interface."""
        context = {
            "message_type": "TEXT",
            "content": {"message": "test message"},
            "sender": "user",
            "session": "test_session",
            "metadata": {
                "agent_capabilities": ["test"],
                "agent_state": {"active": True}
            }
        }
        
        result = await strategy_engine.decide_action(context)
        
        assert "type" in result
        assert "content" in result
        assert "confidence" in result
        assert "reasoning_trace" in result
    
    def test_strategy_switching(self, strategy_engine):
        """Test runtime strategy switching."""
        # Add mock strategy
        mock_strategy = MockReasoningStrategy({"capabilities": ["mock_test"]})
        strategy_engine.add_strategy(mock_strategy)
        
        # Switch to mock strategy
        strategy_engine.switch_strategy(ReasoningType.MOCK)
        assert strategy_engine.get_reasoning_type() == "mock"
        
        # Check history
        history = strategy_engine.get_strategy_history()
        assert len(history) >= 2
    
    @pytest.mark.asyncio
    async def test_capabilities_delegation(self, strategy_engine):
        """Test capabilities delegation to current strategy."""
        capabilities = await strategy_engine.get_capabilities()
        assert isinstance(capabilities, set)
        assert len(capabilities) > 0
    
    @pytest.mark.asyncio
    async def test_knowledge_update_delegation(self, strategy_engine):
        """Test knowledge update delegation to current strategy."""
        knowledge = {"test_knowledge": "test_value"}
        await strategy_engine.update_knowledge(knowledge)
        
        # Verify knowledge was passed to strategy
        current_strategy = strategy_engine.get_current_strategy()
        assert "test_knowledge" in current_strategy.knowledge_base
    
    def test_engine_info(self, strategy_engine):
        """Test engine information retrieval."""
        info = strategy_engine.get_engine_info()
        
        assert info["engine_type"] == "strategy_reasoning_engine"
        assert "current_strategy" in info
        assert "available_strategies" in info
        assert "strategy_history" in info
        assert "context_info" in info


class TestStrategyPatternIntegration:
    """Integration tests for the complete Strategy Pattern implementation."""
    
    @pytest.mark.asyncio
    async def test_multi_strategy_workflow(self):
        """Test complete workflow with multiple strategies."""
        # Create engine with default rule-based strategy
        engine = StrategyReasoningEngine()
        
        # Add LLM and Mock strategies
        llm_strategy = LLMReasoningStrategy({"capabilities": ["nlp"]})
        mock_strategy = MockReasoningStrategy({"capabilities": ["testing"]})
        
        engine.add_strategy(llm_strategy)
        engine.add_strategy(mock_strategy)
        
        # Test with rule-based strategy
        context = {
            "message_type": "TEXT",
            "content": {"message": "rule test"},
            "sender": "user"
        }
        result = await engine.decide_action(context)
        assert result["type"] == "text"
        
        # Switch to LLM strategy and test
        engine.switch_strategy(ReasoningType.LLM_BASED)
        result = await engine.decide_action(context)
        assert result["type"] == "text"
        
        # Switch to Mock strategy and test
        engine.switch_strategy(ReasoningType.MOCK)
        result = await engine.decide_action(context)
        assert result["type"] == "text"
        
        # Verify strategy history
        history = engine.get_strategy_history()
        assert ReasoningType.RULE_BASED in history
        assert ReasoningType.LLM_BASED in history
        assert ReasoningType.MOCK in history
    
    @pytest.mark.asyncio
    async def test_capability_consistency_across_strategies(self):
        """Test capability consistency across different strategies."""
        strategies = [
            RuleBasedReasoningStrategy({"capabilities": ["rule_cap"]}),
            LLMReasoningStrategy({"capabilities": ["llm_cap"]}),
            MockReasoningStrategy({"capabilities": ["mock_cap"]})
        ]
        
        engine = StrategyReasoningEngine(strategies[0])
        for strategy in strategies[1:]:
            engine.add_strategy(strategy)
        
        # Test capabilities for each strategy
        for strategy_type in [ReasoningType.RULE_BASED, ReasoningType.LLM_BASED, ReasoningType.MOCK]:
            engine.switch_strategy(strategy_type)
            capabilities = await engine.get_capabilities()
            assert isinstance(capabilities, set)
            assert len(capabilities) > 0
    
    @pytest.mark.asyncio
    async def test_error_handling_across_strategies(self):
        """Test error handling consistency across strategies."""
        engine = StrategyReasoningEngine()
        
        # Test with invalid capability invocation
        context = {
            "message_type": "CAPABILITY_INVOCATION",
            "content": {"invocation_name": "non_existent_capability"},
            "sender": "user"
        }
        
        result = await engine.decide_action(context)
        
        # Should handle gracefully regardless of strategy
        assert "type" in result
        # Error handling may vary by strategy, but should not crash

# TASK: Facade Pattern Implementation for Agent Subsystem Abstraction

**Task ID**: ARCH-002  
**Priority**: CRITICAL  
**Type**: Architectural Remediation  
**Estimated Effort**: 2-3 days  
**Dependencies**: ARCH-001 (Body-Brain Separation)

## Task Overview

Implement the Facade Pattern to provide a simplified, unified interface for OpenMAS agent creation and interaction. The current implementation forces clients to understand and manage complex Agent internals, violating the design principle of subsystem abstraction and making the framework difficult to use and extend.

## Three-Input Task Creation Protocol Compliance

### Input 1: Design Documentation Analysis

**Primary Reference**: `/refactoring_work/design/01_architecture/architectural_patterns.md` (lines 255-284)

**Design Specification**:
```python
class AgentFacade:
    def __init__(self, config):
        # Initialize complex subsystems
        self.communicator = CommunicatorFactory.create(config)
        self.reasoning = ReasoningFactory.create(config)
        self.lifecycle = LifecycleManager(config)
        self.observation = ObservationSystem(config)

    async def process_message(self, message):
        # Simplified interface for message processing
        return await self.communicator.process(message, self.reasoning)
```

**Architectural Principle**: Provide a unified interface to a set of interfaces in a subsystem. Facade defines a higher-level interface that makes the subsystem easier to use.

### Input 2: User Business/Personal Needs

**Core Business Value**:
- **Simplified Agent Creation**: Users should create agents with minimal configuration complexity
- **Subsystem Abstraction**: Hide complex initialization and coordination between communicators, reasoning engines, state managers
- **Consistent Interface**: Provide stable API that doesn't change when internal subsystems evolve
- **Rapid Prototyping**: Enable quick agent creation for PowerBI, SQL Server, and analytics workflows

**Real-World Use Cases**:
- PowerBI data model agent creation with simple configuration
- SQL Server query agent setup without understanding protocol adapters
- Analytics workflow agents with minimal boilerplate code
- Testing and development with mock subsystems

**Current Pain Points**:
- Users must understand Agent constructor complexity
- Direct exposure of protocol adapters, state managers, reasoning engines
- Difficult to mock or test individual subsystems
- Changes to Agent internals break client code

### Input 3: Current Codebase Implementation Status

**Current Violation** (`src/openmas/agent/base_agent.py`):
```python
# NO FACADE EXISTS - Clients interact directly with complex Agent class
class Agent(IMessageHandler):  # Exposes all internal complexity
    def __init__(self, config, state_manager, protocol_adapters):  # Complex constructor
        # Direct initialization of all subsystems
```

**Existing Infrastructure to Leverage**:
- ✅ `Agent` class with complete functionality
- ✅ `AgentConfig` configuration system
- ✅ `IProtocolAdapter` interface and MCP implementation
- ✅ `IAgentStateManager` interface
- ✅ Factory patterns from ARCH-001 (CommunicatorFactory, ReasoningEngineFactory)
- ✅ 232 passing tests demonstrating foundation works

**Missing Components to Build**:
- ⚠️ `AgentFacade` class providing simplified interface
- ⚠️ `AgentBuilder` for fluent agent configuration
- ⚠️ Default subsystem implementations for common use cases
- ⚠️ Configuration presets for typical agent types

## Implementation Specification

### Phase 1: Core Facade Implementation

**1.1 AgentFacade Class**
```python
# src/openmas/agent/facade.py
from typing import Any, Dict, List, Optional
from openmas.agent.base_agent import Agent
from openmas.agent.factories import AgentFactory, CommunicatorFactory, ReasoningEngineFactory
from openmas.agent.interfaces import ICommunicator, IReasoningEngine
from openmas.core.simf import SIMFMessage
from openmas.core.config import AgentConfig

class AgentFacade:
    """
    Simplified interface for OpenMAS agent creation and interaction.
    
    Hides the complexity of subsystem initialization and coordination,
    providing a clean API for common agent operations.
    """
    
    def __init__(self, config: AgentConfig | Dict[str, Any] | str):
        """
        Initialize agent facade with simplified configuration.
        
        Args:
            config: Agent configuration (AgentConfig object, dict, or preset name)
        """
        # Normalize configuration
        self.config = self._normalize_config(config)
        
        # Initialize subsystems through factories
        self._initialize_subsystems()
        
        # Create the underlying agent
        self.agent = AgentFactory.create(
            self.config,
            protocol_adapters=self.protocol_adapters,
            state_manager=self.state_manager
        )
        
        # Facade state
        self._running = False
        
    def _normalize_config(self, config: AgentConfig | Dict[str, Any] | str) -> AgentConfig:
        """Convert various config formats to AgentConfig."""
        if isinstance(config, str):
            # Load preset configuration
            return self._load_preset_config(config)
        elif isinstance(config, dict):
            # Convert dict to AgentConfig
            return AgentConfig(**config)
        elif isinstance(config, AgentConfig):
            return config
        else:
            raise ValueError(f"Invalid config type: {type(config)}")
    
    def _load_preset_config(self, preset_name: str) -> AgentConfig:
        """Load predefined agent configuration presets."""
        presets = {
            "powerbi_agent": AgentConfig(
                agent_id=f"powerbi_{uuid.uuid4().hex[:8]}",
                name="PowerBI Data Model Agent",
                capabilities=["data_model_analysis", "mquery_extraction", "report_generation"],
                reasoning_type="simple",
                protocols=["mcp"]
            ),
            "sql_agent": AgentConfig(
                agent_id=f"sql_{uuid.uuid4().hex[:8]}",
                name="SQL Server Agent",
                capabilities=["query_optimization", "schema_analysis", "performance_tuning"],
                reasoning_type="simple",
                protocols=["mcp", "http"]
            ),
            "analytics_agent": AgentConfig(
                agent_id=f"analytics_{uuid.uuid4().hex[:8]}",
                name="Analytics Workflow Agent",
                capabilities=["data_analysis", "visualization", "reporting"],
                reasoning_type="simple",
                protocols=["mcp"]
            ),
            "basic_agent": AgentConfig(
                agent_id=f"basic_{uuid.uuid4().hex[:8]}",
                name="Basic Agent",
                capabilities=["message_handling"],
                reasoning_type="simple",
                protocols=["mcp"]
            )
        }
        
        if preset_name not in presets:
            raise ValueError(f"Unknown preset: {preset_name}. Available: {list(presets.keys())}")
        
        return presets[preset_name]
    
    def _initialize_subsystems(self) -> None:
        """Initialize all required subsystems with sensible defaults."""
        # Protocol adapters (use defaults if not specified)
        self.protocol_adapters = self._create_default_protocol_adapters()
        
        # State manager (use default implementation)
        self.state_manager = self._create_default_state_manager()
        
        # Additional subsystems can be added here
        # self.lifecycle_manager = self._create_lifecycle_manager()
        # self.observation_system = self._create_observation_system()
    
    def _create_default_protocol_adapters(self) -> Dict[str, Any]:
        """Create default protocol adapters based on configuration."""
        adapters = {}
        
        # Only create adapters for protocols specified in config
        if hasattr(self.config, 'protocols'):
            for protocol in self.config.protocols:
                if protocol == "mcp":
                    # Import and create MCP adapter
                    from openmas.protocols.mcp.adapter import MCPAdapter
                    adapters["mcp"] = MCPAdapter()
                # Add other protocol adapters as they become available
        
        return adapters
    
    def _create_default_state_manager(self) -> Optional[Any]:
        """Create default state manager implementation."""
        # For now, return None (agent will use default behavior)
        # Future: Create DefaultStateManager implementation
        return None
    
    # Simplified Public Interface
    
    async def start(self) -> None:
        """Start the agent with simplified interface."""
        if self._running:
            raise RuntimeError("Agent is already running")
        
        await self.agent.start()
        self._running = True
    
    async def stop(self) -> None:
        """Stop the agent with simplified interface."""
        if not self._running:
            return
        
        await self.agent.stop()
        self._running = False
    
    async def send_message(self, content: Any, target: str, message_type: str = "request") -> SIMFMessage | None:
        """
        Send message with simplified interface.
        
        Args:
            content: Message content (will be serialized appropriately)
            target: Target agent or service identifier
            message_type: Type of message (default: "request")
            
        Returns:
            Response message if any
        """
        # Create SIMF message
        message = SIMFMessage(
            message_type=message_type,
            payload={"content": content, "target": target},
            sender_id=self.agent.agent_id,
            session_id=self.agent.current_session_id
        )
        
        # Send through agent
        return await self.agent.handle_message(message)
    
    async def process_message(self, message: Any) -> SIMFMessage | None:
        """
        Process incoming message with simplified interface.
        
        Args:
            message: Incoming message (various formats supported)
            
        Returns:
            Response message if any
        """
        # Normalize message to SIMF format
        simf_message = self._normalize_message(message)
        
        # Process through agent
        return await self.agent.handle_message(simf_message)
    
    def _normalize_message(self, message: Any) -> SIMFMessage:
        """Convert various message formats to SIMF."""
        if isinstance(message, SIMFMessage):
            return message
        elif isinstance(message, dict):
            return SIMFMessage(
                message_type=message.get("type", "request"),
                payload=message.get("payload", message),
                sender_id=message.get("sender", "unknown"),
                session_id=message.get("session")
            )
        else:
            # Treat as simple content
            return SIMFMessage(
                message_type="request",
                payload={"content": message},
                sender_id="unknown"
            )
    
    def add_capability(self, capability: str) -> None:
        """Add capability with simplified interface."""
        self.agent.capabilities.add(capability)
    
    def remove_capability(self, capability: str) -> None:
        """Remove capability with simplified interface."""
        self.agent.capabilities.discard(capability)
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities with simplified interface."""
        return list(self.agent.capabilities)
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            "agent_id": self.agent.agent_id,
            "name": self.agent.name,
            "running": self._running,
            "capabilities": list(self.agent.capabilities),
            "reasoning_type": self.agent.reasoning_engine.get_reasoning_type(),
            "protocols": list(self.protocol_adapters.keys())
        }
    
    # Advanced Configuration Methods
    
    def set_reasoning_engine(self, reasoning_engine: IReasoningEngine) -> None:
        """Change reasoning engine with simplified interface."""
        self.agent.set_reasoning_engine(reasoning_engine)
    
    def add_protocol_adapter(self, protocol: str, adapter: Any) -> None:
        """Add protocol adapter with simplified interface."""
        self.protocol_adapters[protocol] = adapter
        self.agent.add_protocol_adapter(protocol, adapter)
```

### Phase 2: Builder Pattern Integration

**2.1 AgentBuilder for Fluent Configuration**
```python
# src/openmas/agent/builder.py
class AgentBuilder:
    """
    Fluent builder for creating agents with complex configurations.
    
    Provides a more flexible alternative to preset configurations
    while maintaining the facade's simplicity.
    """
    
    def __init__(self):
        self._config_dict = {}
        self._custom_components = {}
    
    def with_id(self, agent_id: str) -> 'AgentBuilder':
        """Set agent ID."""
        self._config_dict["agent_id"] = agent_id
        return self
    
    def with_name(self, name: str) -> 'AgentBuilder':
        """Set agent name."""
        self._config_dict["name"] = name
        return self
    
    def with_capabilities(self, capabilities: List[str]) -> 'AgentBuilder':
        """Set agent capabilities."""
        self._config_dict["capabilities"] = capabilities
        return self
    
    def add_capability(self, capability: str) -> 'AgentBuilder':
        """Add single capability."""
        if "capabilities" not in self._config_dict:
            self._config_dict["capabilities"] = []
        self._config_dict["capabilities"].append(capability)
        return self
    
    def with_reasoning(self, reasoning_type: str) -> 'AgentBuilder':
        """Set reasoning engine type."""
        self._config_dict["reasoning_type"] = reasoning_type
        return self
    
    def with_protocols(self, protocols: List[str]) -> 'AgentBuilder':
        """Set supported protocols."""
        self._config_dict["protocols"] = protocols
        return self
    
    def add_protocol(self, protocol: str) -> 'AgentBuilder':
        """Add single protocol."""
        if "protocols" not in self._config_dict:
            self._config_dict["protocols"] = []
        self._config_dict["protocols"].append(protocol)
        return self
    
    def with_custom_communicator(self, communicator: ICommunicator) -> 'AgentBuilder':
        """Set custom communicator implementation."""
        self._custom_components["communicator"] = communicator
        return self
    
    def with_custom_reasoning(self, reasoning_engine: IReasoningEngine) -> 'AgentBuilder':
        """Set custom reasoning engine implementation."""
        self._custom_components["reasoning_engine"] = reasoning_engine
        return self
    
    def build(self) -> AgentFacade:
        """Build the agent facade with configured options."""
        # Create configuration
        config = AgentConfig(**self._config_dict)
        
        # Create facade
        facade = AgentFacade(config)
        
        # Apply custom components
        if "reasoning_engine" in self._custom_components:
            facade.set_reasoning_engine(self._custom_components["reasoning_engine"])
        
        if "communicator" in self._custom_components:
            # Replace communicator in underlying agent
            facade.agent.communicator = self._custom_components["communicator"]
        
        return facade

# Convenience function for builder pattern
def create_agent() -> AgentBuilder:
    """Create new agent builder."""
    return AgentBuilder()
```

### Phase 3: Convenience Functions and Presets

**3.1 High-Level Convenience Functions**
```python
# src/openmas/agent/__init__.py (additions)
from .facade import AgentFacade
from .builder import AgentBuilder, create_agent

# Convenience functions for common use cases
def create_powerbi_agent(name: str = None) -> AgentFacade:
    """Create PowerBI-specialized agent with sensible defaults."""
    return AgentFacade("powerbi_agent")

def create_sql_agent(name: str = None) -> AgentFacade:
    """Create SQL Server-specialized agent with sensible defaults."""
    return AgentFacade("sql_agent")

def create_analytics_agent(name: str = None) -> AgentFacade:
    """Create analytics workflow agent with sensible defaults."""
    return AgentFacade("analytics_agent")

def create_basic_agent(name: str = None) -> AgentFacade:
    """Create basic agent with minimal configuration."""
    return AgentFacade("basic_agent")

# Export facade as primary interface
__all__ = [
    "Agent",  # Keep for advanced use cases
    "AgentFacade",  # Primary interface
    "AgentBuilder",
    "create_agent",
    "create_powerbi_agent",
    "create_sql_agent", 
    "create_analytics_agent",
    "create_basic_agent"
]
```

## Quality Enforcement (Phase 2.5)

### Ruff Configuration Compliance
```bash
# Validate ruff configuration
ruff check src/openmas/agent/facade.py --config pyproject.toml
ruff check src/openmas/agent/builder.py --config pyproject.toml
# Expected: line-length=120, ignore=E203, select=["E", "F", "I", "UP", "N", "B", "SIM"]
```

### MyPy Type Checking
```bash
# Strict typing validation
mypy src/openmas/agent/facade.py --strict
mypy src/openmas/agent/builder.py --strict

# Specific error prevention
mypy src/openmas/agent/ --strict --show-error-codes | grep -E "(union-attr|no-untyped-def|assignment|call-arg)"
```

### Zero Regression Policy
```bash
# MANDATORY: Establish baseline before changes
echo "=== ESTABLISHING BASELINE - TESTS MUST PASS BEFORE CHANGES ==="
python -m pytest tests/ -x --tb=short
if [ $? -ne 0 ]; then
    echo "❌ BASELINE FAILED: Tests are already broken. Fix before proceeding."
    exit 1
fi
echo "✅ BASELINE ESTABLISHED: All tests passing before changes"

# MANDATORY: Zero regression validation after changes
echo "=== ZERO REGRESSION VALIDATION - TESTS MUST PASS AFTER CHANGES ==="
python -m pytest tests/ -x --tb=short
if [ $? -ne 0 ]; then
    echo "❌ REGRESSION DETECTED: Tests broken by changes. REVERT IMMEDIATELY."
    echo "❌ TASK FAILED: Cannot complete task with broken tests."
    exit 1
fi
echo "✅ ZERO REGRESSION CONFIRMED: All tests still passing after changes"
```

### Quality Gate Requirements
1. **#1 REQUIREMENT**: ZERO REGRESSION POLICY - All tests MUST pass before AND after changes (MANDATORY)
2. All facade methods must have complete type annotations
3. All builder methods must return proper types for fluent interface
4. Configuration validation must handle edge cases gracefully
5. Error messages must be clear and actionable
6. All public methods must have comprehensive docstrings
7. Preset configurations must be validated and tested

## Testing Strategy

### Unit Tests
```python
# tests/agent/test_facade_pattern.py
class TestAgentFacade:
    """Test AgentFacade implementation."""
    
    def test_preset_configuration(self):
        """Test preset-based agent creation."""
        facade = AgentFacade("powerbi_agent")
        assert facade.agent.name == "PowerBI Data Model Agent"
        assert "data_model_analysis" in facade.get_capabilities()
    
    def test_dict_configuration(self):
        """Test dictionary-based configuration."""
        config = {
            "agent_id": "test_agent",
            "name": "Test Agent",
            "capabilities": ["test_capability"]
        }
        facade = AgentFacade(config)
        assert facade.agent.agent_id == "test_agent"
    
    def test_simplified_message_processing(self):
        """Test simplified message processing interface."""
        facade = AgentFacade("basic_agent")
        # Test with various message formats
    
    def test_capability_management(self):
        """Test simplified capability management."""
        facade = AgentFacade("basic_agent")
        facade.add_capability("new_capability")
        assert "new_capability" in facade.get_capabilities()
    
    def test_status_information(self):
        """Test status information retrieval."""
        facade = AgentFacade("powerbi_agent")
        status = facade.get_status()
        assert "agent_id" in status
        assert "capabilities" in status

class TestAgentBuilder:
    """Test AgentBuilder fluent interface."""
    
    def test_fluent_interface(self):
        """Test builder fluent interface."""
        facade = (create_agent()
                 .with_name("Custom Agent")
                 .add_capability("custom_capability")
                 .with_reasoning("simple")
                 .build())
        
        assert facade.agent.name == "Custom Agent"
        assert "custom_capability" in facade.get_capabilities()
    
    def test_custom_components(self):
        """Test custom component integration."""
        custom_reasoning = MockReasoningEngine()
        
        facade = (create_agent()
                 .with_name("Custom Agent")
                 .with_custom_reasoning(custom_reasoning)
                 .build())
        
        assert facade.agent.reasoning_engine == custom_reasoning
```

### Integration Tests
```python
# tests/integration/test_facade_integration.py
class TestFacadeIntegration:
    """Test facade integration with real subsystems."""
    
    async def test_end_to_end_message_processing(self):
        """Test complete message processing through facade."""
        facade = AgentFacade("basic_agent")
        await facade.start()
        
        response = await facade.process_message({
            "type": "capability_request",
            "payload": {"capability": "message_handling"}
        })
        
        assert response is not None
        await facade.stop()
    
    async def test_preset_agent_functionality(self):
        """Test that preset agents work correctly."""
        facade = AgentFacade("powerbi_agent")
        await facade.start()
        
        # Test PowerBI-specific capabilities
        response = await facade.process_message({
            "type": "capability_request", 
            "payload": {"capability": "data_model_analysis"}
        })
        
        assert response.payload["status"] == "success"
        await facade.stop()
```

## Success Criteria

### Functional Requirements
- [ ] `AgentFacade` provides simplified interface to complex agent subsystems
- [ ] Preset configurations work for common agent types (PowerBI, SQL, analytics)
- [ ] `AgentBuilder` enables fluent configuration for complex scenarios
- [ ] Convenience functions provide one-line agent creation
- [ ] Message processing works with multiple input formats
- [ ] Capability management through simplified interface

### Architectural Requirements
- [ ] Complete subsystem abstraction achieved
- [ ] Client code isolated from Agent internal complexity
- [ ] Facade delegates to underlying Agent without duplicating logic
- [ ] Builder pattern enables flexible configuration
- [ ] Preset system supports common use cases

### Quality Requirements
- [ ] All 232+ tests continue to pass (zero regression)
- [ ] MyPy strict mode compliance for all new code
- [ ] Ruff linting compliance (line-length=120, ignore=E203)
- [ ] Complete type annotations for all public interfaces
- [ ] Comprehensive error handling with clear messages

### Design Alignment
- [ ] Implementation matches `/refactoring_work/design/01_architecture/architectural_patterns.md` specification
- [ ] Enables simplified agent creation for business workflows
- [ ] Provides access to advanced features when needed
- [ ] Supports future subsystem additions through clean extension points

## Deliverables

1. **Core Facade Implementation**:
   - `src/openmas/agent/facade.py`
   - `src/openmas/agent/builder.py`

2. **Enhanced Public Interface**:
   - Updated `src/openmas/agent/__init__.py` with convenience functions

3. **Test Suite**:
   - `tests/agent/test_facade_pattern.py`
   - `tests/integration/test_facade_integration.py`

4. **Documentation**:
   - Agent creation guide with facade examples
   - Migration guide for existing Agent users
   - Preset configuration reference

## Notes

- Facade provides simplified interface while preserving access to advanced features
- Builder pattern enables complex configurations without facade complexity
- Preset system supports rapid prototyping for business workflows
- Implementation provides clean, simple interface for agent creation
- Foundation for user-friendly PowerBI, SQL Server, and analytics agent creation

## Anti-Hallucination Safeguards

- Facade delegates to existing Agent implementation (no duplication)
- Preset configurations use existing AgentConfig structure
- Builder pattern leverages existing factory classes from ARCH-001
- All convenience functions create standard AgentFacade instances
- Testing builds on existing 232 passing tests without modification

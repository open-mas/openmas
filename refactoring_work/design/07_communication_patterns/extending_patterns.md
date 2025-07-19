# Extending Communication Patterns

This document describes how to extend the OpenMAS communication patterns with custom implementations to support specialized use cases while maintaining compatibility with the core framework.

## Overview

OpenMAS is designed with extensibility in mind, allowing developers to:

1. Add custom pattern implementations
2. Extend existing patterns with new features
3. Create domain-specific pattern variations
4. Implement protocol-specific optimizations

All extensions maintain the core principles of OpenMAS:
- Reasoning agnosticism
- Protocol independence
- Consistent API interfaces
- Observability integration

## Extension Methods

### 1. Custom Pattern Implementation

The simplest way to extend OpenMAS communication patterns is to create a new pattern implementation that adheres to the pattern interface contract.

```python
from openmas.patterns.base import BasePattern

class CustomPattern(BasePattern):
    """Custom pattern implementation for specialized communication needs."""
    
    def __init__(self, config):
        super().__init__(config)
        self.pattern_type = "custom"
        
        # Initialize custom state
        self.custom_state = {}
        
    async def initialize(self, context):
        """Initialize the pattern with the provided context."""
        await super().initialize(context)
        
        # Custom initialization logic
        self.communicator = await context.get_communicator()
        
        # Register custom message handlers
        await self.communicator.register_handler(
            message_type="custom_message",
            handler=self.handle_custom_message
        )
        
    async def handle_custom_message(self, message):
        """Handle custom message types."""
        # Custom message handling logic
        pass
        
    # Implement custom pattern-specific methods
    async def custom_operation(self, target_id, data):
        """Perform a custom operation with another agent."""
        # Implementation
        
        # Use the communicator to send messages
        await self.communicator.send_message(
            target_id=target_id,
            message_type="custom_operation",
            content=data
        )
```

### 2. Extending an Existing Pattern

You can extend an existing pattern to add additional functionality:

```python
from openmas.patterns.request_response import RequestResponsePattern

class EnhancedRequestResponsePattern(RequestResponsePattern):
    """Extended Request-Response pattern with additional features."""
    
    def __init__(self, config):
        super().__init__(config)
        
        # Initialize enhanced features
        self.response_cache = {}
        self.cache_enabled = config.get("cache_enabled", False)
        self.cache_ttl = config.get("cache_ttl", 300)  # 5 minutes default
        
    async def send_request(self, target_agent_id, request_type, content):
        """Send a request with optional caching."""
        # Check cache if enabled
        if self.cache_enabled:
            cache_key = f"{target_agent_id}:{request_type}:{hash(str(content))}"
            cached_response = self.get_from_cache(cache_key)
            
            if cached_response:
                return cached_response
                
        # Call the parent implementation
        response = await super().send_request(target_agent_id, request_type, content)
        
        # Cache the response if enabled
        if self.cache_enabled and response:
            self.add_to_cache(cache_key, response)
            
        return response
        
    def get_from_cache(self, key):
        """Get a response from the cache if still valid."""
        if key not in self.response_cache:
            return None
            
        entry = self.response_cache[key]
        
        # Check if entry is expired
        if time.time() - entry["timestamp"] > self.cache_ttl:
            del self.response_cache[key]
            return None
            
        return entry["response"]
        
    def add_to_cache(self, key, response):
        """Add a response to the cache."""
        self.response_cache[key] = {
            "response": response,
            "timestamp": time.time()
        }
```

### 3. Protocol-Specific Optimizations

You can create protocol-specific pattern implementations that optimize for particular protocols:

```python
from openmas.patterns.publish_subscribe import PublishSubscribePattern

class A2AOptimizedPubSubPattern(PublishSubscribePattern):
    """Publish-Subscribe pattern optimized for Google A2A protocol."""
    
    def __init__(self, config):
        super().__init__(config)
        
        # A2A-specific configuration
        self.a2a_topic_prefix = config.get("a2a_topic_prefix", "a2a_topic_")
        
    async def initialize(self, context):
        """Initialize the A2A-optimized pattern."""
        await super().initialize(context)
        
        # Get A2A-specific communicator
        self.a2a_communicator = await context.get_communicator("a2a")
        
        # Set up A2A-specific topic handling
        # ... A2A-specific initialization ...
        
    async def create_topic(self, topic_id, metadata=None):
        """Create a topic optimized for A2A protocol."""
        # A2A-specific topic creation logic
        a2a_topic_id = f"{self.a2a_topic_prefix}{topic_id}"
        
        # Use A2A card system for topic definitions
        topic_card = {
            "topic_id": a2a_topic_id,
            "metadata": metadata or {},
            "schema": metadata.get("schema") if metadata else None
        }
        
        # Register with A2A system
        await self.a2a_communicator.register_topic(topic_card)
        
        # Store in parent class tracking
        return await super().create_topic(topic_id, metadata)
```

### 4. Domain-Specific Pattern Variations

Domain-specific patterns can be created for specialized fields:

```python
from openmas.patterns.event_based import EventBasedPattern

class MedicalAlertPattern(EventBasedPattern):
    """Event-Based pattern specialized for medical alerting scenarios."""
    
    def __init__(self, config):
        super().__init__(config)
        
        # Medical-specific configuration
        self.alert_priorities = {
            "critical": 1,
            "urgent": 2,
            "important": 3,
            "routine": 4,
            "informational": 5
        }
        
        self.default_priority = config.get("default_priority", "routine")
        self.escalation_timeout = config.get("escalation_timeout_seconds", 60)
        
    async def emit_medical_alert(self, alert_type, patient_data, priority=None, escalation_path=None):
        """Emit a medical alert with domain-specific handling."""
        if priority is None:
            priority = self.default_priority
            
        priority_level = self.alert_priorities.get(priority, 4)
        
        # Create alert data
        alert_data = {
            "alert_type": alert_type,
            "patient_data": patient_data,
            "priority": priority,
            "priority_level": priority_level,
            "timestamp": datetime.now().isoformat(),
            "escalation_path": escalation_path
        }
        
        # Use the base event emission
        event_id = await self.emit_event(
            event_type=f"medical_alert.{alert_type}",
            content=alert_data
        )
        
        # Set up escalation if needed
        if escalation_path and priority_level <= 3:  # Important or higher
            await self.schedule_escalation(event_id, alert_data, escalation_path)
            
        return event_id
        
    async def schedule_escalation(self, event_id, alert_data, escalation_path):
        """Schedule alert escalation if no acknowledgment received."""
        # Implementation details for escalation logic
        pass
```

## Registration and Usage

To make your custom patterns available in the OpenMAS pattern registry:

```python
# In your agent initialization
async def initialize(self, context):
    # Register custom patterns
    pattern_registry = context.get_pattern_registry()
    
    # Register with a custom pattern type name
    await pattern_registry.register_pattern_implementation(
        pattern_type="custom",
        implementation_class=CustomPattern
    )
    
    # Override an existing pattern with enhanced version
    await pattern_registry.register_pattern_implementation(
        pattern_type="request_response",
        implementation_class=EnhancedRequestResponsePattern,
        variant="enhanced"
    )
    
    # Later, get the pattern instance
    self.custom_pattern = await pattern_registry.get_pattern(
        "custom",
        self.config.get("patterns", {}).get("custom")
    )
    
    self.enhanced_request_response = await pattern_registry.get_pattern(
        "request_response",
        self.config.get("patterns", {}).get("request_response"),
        variant="enhanced"
    )
```

## Best Practices for Pattern Extensions

1. **Maintain Interface Contracts**: Ensure your extensions adhere to the established pattern interfaces to maintain compatibility with other parts of OpenMAS.

2. **Preserving Protocol Independence**: Even when optimizing for specific protocols, maintain the ability to work with other protocols through the standard interfaces.

3. **Reasoning Agnosticism**: Pattern extensions should not make assumptions about the reasoning approaches used by agents.

4. **Observability Integration**: Ensure your custom patterns integrate with OpenMAS observability infrastructure for monitoring and debugging.

5. **Documentation**: Thoroughly document your pattern extensions, especially any new interfaces or behaviors that differ from the standard patterns.

6. **Testing**: Create comprehensive tests for your extensions to ensure they behave correctly in various scenarios.

7. **Error Handling**: Implement robust error handling to gracefully manage failures in your extensions.

## Testing Custom Patterns

OpenMAS provides a pattern testing framework to ensure custom implementations adhere to the required interfaces:

```python
from openmas.testing.patterns import PatternTestSuite

# Create test suite for your pattern
test_suite = PatternTestSuite(CustomPattern)

# Run interface compatibility tests
await test_suite.test_interface_compatibility()

# Run functional tests
await test_suite.test_functional_behavior({
    "custom_config": "value"
})

# Run protocol independence tests
for protocol in ["a2a", "mcp", "http"]:
    await test_suite.test_protocol_compatibility(protocol)
```

## Common Extension Scenarios

### 1. Adding Security Enhancements

```python
class SecureRequestResponsePattern(RequestResponsePattern):
    """Request-Response pattern with additional security features."""
    
    async def send_request(self, target_agent_id, request_type, content):
        """Send a request with additional security measures."""
        # Add security context
        secured_content = await self.security_service.encrypt_content(content)
        
        # Add integrity verification
        integrity_hash = await self.security_service.generate_integrity_hash(content)
        
        enhanced_content = {
            "original_content": secured_content,
            "integrity_hash": integrity_hash,
            "security_level": self.config.get("security_level", "standard")
        }
        
        # Use parent implementation with enhanced content
        return await super().send_request(target_agent_id, request_type, enhanced_content)
```

### 2. Adding Domain-Specific Semantics

```python
class SemanticEventPattern(EventBasedPattern):
    """Event-Based pattern with semantic classification."""
    
    def __init__(self, config):
        super().__init__(config)
        
        # Initialize knowledge service
        self.knowledge_service = None
        self.semantic_classifier = None
        
    async def initialize(self, context):
        """Initialize the semantic event pattern."""
        await super().initialize(context)
        
        # Get knowledge service
        self.knowledge_service = await context.get_service("knowledge")
        
        # Initialize semantic classifier
        self.semantic_classifier = await self.knowledge_service.get_classifier(
            self.config.get("classifier_type", "general")
        )
        
    async def emit_event(self, event_type, content):
        """Emit an event with semantic enrichment."""
        # Extract and classify semantic content
        semantic_tags = await self.semantic_classifier.classify_content(content)
        
        # Enhance content with semantic information
        enhanced_content = {
            "original_content": content,
            "semantic_tags": semantic_tags,
            "semantic_categories": await self.knowledge_service.get_categories(semantic_tags)
        }
        
        # Use parent implementation with enhanced content
        return await super().emit_event(event_type, enhanced_content)
```

## Conclusion

Extending OpenMAS communication patterns allows for customization while maintaining the framework's architectural principles. By following the established interfaces and best practices, custom pattern implementations can seamlessly integrate with the broader ecosystem of agents and patterns.

For further details on specific pattern interfaces, refer to the individual pattern documentation.

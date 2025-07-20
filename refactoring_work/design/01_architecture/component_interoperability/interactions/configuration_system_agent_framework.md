# Configuration System ↔ Agent Framework

## Relationship Summary
- **Configuration System → Agent Framework**: Configures
- **Agent Framework → Configuration System**: Depends On

## Interface Definitions

### Configuration System → Agent Framework

#### Methods/Functions
```python
def initialize(config: AgentFrameworkConfig,
             options: Optional[InitializationOptions] = None) -> InitializationResult:
    """
    Initialize the Agent Framework with configuration parameters.

    Args:
        config: AgentFrameworkConfig - Configuration object containing all Agent Framework settings
        options: Optional[InitializationOptions] - Additional initialization options

    Returns:
        InitializationResult - Detailed result of the initialization process

    Raises:
        ConfigurationValidationError - If configuration validation fails
        ComponentInitializationError - If component initialization fails
        DependencyMissingError - If required dependencies are missing
    """
```

**Data Structures:**

```python
class AgentType:
    """
    Configuration for a specific agent type supported by the framework.
    """
    type: str  # Unique identifier for this agent type
    implementation_class: str  # Class that implements this agent type
    default_capabilities: List[str]  # Default capabilities for this agent type
    description: Optional[str] = None  # Description of this agent type
    is_enabled: bool = True  # Whether this agent type is enabled
    requires_reasoning_engine: bool = False  # Whether this agent type requires a reasoning engine
    supported_reasoning_engines: List[str] = []  # Reasoning engines supported by this agent type
    supported_protocols: List[str] = []  # Communication protocols supported by this agent type
    configuration_schema: Optional[Dict[str, Any]] = None  # JSON Schema for agent-specific configuration
    lifecycle_hooks: Dict[str, str] = {}  # Lifecycle event hooks for this agent type
    metadata: Dict[str, Any] = {}  # Additional metadata for this agent type

class MessageProcessingConfig:
    """
    Configuration for message processing in the Agent Framework.
    """
    max_queue_size: int  # Maximum size of the message queue
    processing_threads: int  # Number of threads for message processing
    priority_levels: int  # Number of priority levels for messages
    batch_size: Optional[int] = None  # Number of messages to process in a batch
    processing_strategy: str = "thread_pool"  # Strategy for message processing ("thread_pool", "async_io", "process_pool")
    max_retries: int = 3  # Maximum number of retries for failed message processing
    retry_delay_ms: int = 1000  # Delay between retries in milliseconds
    monitoring_enabled: bool = True  # Whether to enable monitoring of message processing
    failure_handling_strategy: str = "dead_letter_queue"  # Strategy for handling failed messages
    dead_letter_queue_size: int = 100  # Size of the dead letter queue

class ComponentConfig:
    """
    Configuration for a specific Agent Framework component.
    """
    enabled: bool  # Whether the component is enabled
    implementation_class: str  # Class that implements the component
    config: Dict[str, Any] = {}  # Component-specific configuration

class AgentFrameworkConfig:
    """
    Configuration for the Agent Framework.
    """
    agent_types: List[AgentType]  # Supported agent types
    message_processing: MessageProcessingConfig  # Message processing configuration
    default_timeout_seconds: int = 30  # Default timeout for operations
    components: Dict[str, ComponentConfig] = {}  # Component configurations
    extensions: Dict[str, Dict[str, Any]] = {}  # Extension configurations
    default_reasoning_engine: Optional[str] = None  # Default reasoning engine
    session_management: Dict[str, Any] = {}  # Session management configuration
    capability_registry: Dict[str, Any] = {}  # Capability registry configuration
    protocol_adapters: Dict[str, Dict[str, Any]] = {}  # Protocol adapter configurations
    security_integration: Dict[str, Any] = {}  # Security integration configuration
    observability_integration: Dict[str, Any] = {}  # Observability integration configuration

class InitializationOptions:
    """
    Options for Agent Framework initialization.
    """
    validate_only: bool = False  # Whether to only validate the configuration without initialization
    skip_dependency_check: bool = False  # Whether to skip dependency checking
    fail_fast: bool = True  # Whether to fail on first error
    initialization_timeout_seconds: int = 60  # Timeout for initialization
    initialize_components: List[str] = []  # Specific components to initialize (empty means all)
    skip_components: List[str] = []  # Components to skip during initialization
    initialization_log_level: str = "info"  # Log level for initialization
    require_secure_channel: bool = True  # Whether to require secure communication channel
    require_protocol_compatibility: bool = True  # Whether to verify protocol compatibility

class ComponentInitializationResult:
    """
    Result of a component initialization.
    """
    component_name: str  # Name of the component
    success: bool  # Whether initialization was successful
    implementation_class: str  # Actual implementation class used
    initialization_time_ms: int  # Time taken for initialization in milliseconds
    error_message: Optional[str] = None  # Error message if initialization failed
    warnings: List[str] = []  # Warnings during initialization
    metadata: Dict[str, Any] = {}  # Additional metadata about initialization

class InitializationResult:
    """
    Result of the Agent Framework initialization.
    """
    success: bool  # Whether initialization was successful
    initialized_components: List[ComponentInitializationResult] = []  # Results of component initializations
    initialization_time_ms: int  # Total time taken for initialization in milliseconds
    error_message: Optional[str] = None  # Error message if initialization failed
    warnings: List[str] = []  # Warnings during initialization
    initialized_agent_types: List[str] = []  # Agent types that were successfully initialized
    initialized_protocols: List[str] = []  # Protocols that were successfully initialized
    initialized_reasoning_engines: List[str] = []  # Reasoning engines that were successfully initialized
    skipped_components: List[str] = []  # Components that were skipped during initialization
    failed_components: List[str] = []  # Components that failed to initialize
    missing_dependencies: List[str] = []  # Dependencies that were missing
    metadata: Dict[str, Any] = {}  # Additional metadata about initialization
```

**Example Usage:**

```python
# Example 1: Initialize Agent Framework with multiple agent types and reasoning engines

# Define agent types configuration
agent_types = [
    AgentType(
        type="reasoning_agent",
        implementation_class="openmas.agents.ReasoningAgent",
        default_capabilities=["reasoning", "tool_use", "memory_access"],
        description="Agent capable of performing reasoning tasks",
        requires_reasoning_engine=True,
        supported_reasoning_engines=["bdi", "llm", "rule_based", "hybrid"],
        supported_protocols=["a2a", "mcp"],
        configuration_schema={
            "type": "object",
            "properties": {
                "reasoning_config": {
                    "type": "object",
                    "properties": {
                        "max_reasoning_steps": {"type": "integer", "minimum": 1},
                        "reasoning_timeout_ms": {"type": "integer", "minimum": 100}
                    }
                }
            }
        }
    ),
    AgentType(
        type="task_agent",
        implementation_class="openmas.agents.TaskAgent",
        default_capabilities=["task_execution", "reporting", "resource_access"],
        description="Agent specialized in executing concrete tasks",
        requires_reasoning_engine=False,
        supported_protocols=["a2a", "mcp", "http"],
        lifecycle_hooks={
            "pre_task_execution": "task_validation_hook",
            "post_task_execution": "task_reporting_hook"
        }
    ),
    AgentType(
        type="conversational_agent",
        implementation_class="openmas.agents.ConversationalAgent",
        default_capabilities=["conversation", "memory_access", "tool_use"],
        description="Agent specialized in natural language conversations",
        requires_reasoning_engine=True,
        supported_reasoning_engines=["llm", "hybrid"],
        supported_protocols=["a2a", "mcp", "http"],
        metadata={
            "recommended_llm_models": ["gpt-4", "claude-2", "llama-3"]
        }
    )
]

# Define message processing configuration
message_processing = MessageProcessingConfig(
    max_queue_size=2000,
    processing_threads=8,
    priority_levels=5,
    batch_size=20,
    processing_strategy="async_io",
    max_retries=5,
    retry_delay_ms=500,
    monitoring_enabled=True,
    failure_handling_strategy="dead_letter_queue",
    dead_letter_queue_size=200
)

# Define component configurations
components = {
    "lifecycle_manager": ComponentConfig(
        enabled=True,
        implementation_class="openmas.components.DefaultLifecycleManager",
        config={
            "agent_lifecycle_events": ["create", "initialize", "start", "pause", "resume", "stop", "destroy"],
            "event_handlers": {
                "create": "on_agent_create",
                "destroy": "on_agent_destroy"
            }
        }
    ),
    "message_router": ComponentConfig(
        enabled=True,
        implementation_class="openmas.components.DefaultMessageRouter",
        config={
            "routing_strategies": ["direct", "broadcast", "multicast", "content_based"],
            "default_strategy": "direct",
            "routing_rules": [
                {
                    "pattern": "broadcast.*",
                    "strategy": "broadcast"
                },
                {
                    "pattern": "agent.*.emergency",
                    "strategy": "priority_direct",
                    "priority": "high"
                }
            ]
        }
    ),
    "capability_registry": ComponentConfig(
        enabled=True,
        implementation_class="openmas.components.DefaultCapabilityRegistry",
        config={
            "capability_discovery_enabled": True,
            "capability_validation_enabled": True,
            "capability_categories": ["reasoning", "tool_use", "communication", "data_access", "system"]
        }
    )
}

# Define protocol adapters configuration
protocol_adapters = {
    "a2a": {
        "enabled": True,
        "implementation_class": "openmas.protocols.A2AProtocolAdapter",
        "config": {
            "endpoint": "http://localhost:8080/a2a",
            "message_format": "json",
            "security": {
                "authentication_required": True,
                "authentication_method": "jwt"
            },
            "capabilities": {
                "support_streaming": True,
                "support_attachments": True,
                "max_message_size_bytes": 1048576
            }
        }
    },
    "mcp": {
        "enabled": True,
        "implementation_class": "openmas.protocols.MCPProtocolAdapter",
        "config": {
            "endpoint": "http://localhost:8090/mcp",
            "message_format": "json",
            "capability_mapping": {
                "reasoning": "mcp:reasoning",
                "tool_use": "mcp:tool_invocation",
                "resource_access": "mcp:resource_access"
            },
            "security": {
                "authentication_required": True,
                "authentication_method": "api_key"
            }
        }
    }
}

# Create the full Agent Framework configuration
agent_framework_config = AgentFrameworkConfig(
    agent_types=agent_types,
    message_processing=message_processing,
    default_timeout_seconds=45,
    components=components,
    default_reasoning_engine="hybrid",
    protocol_adapters=protocol_adapters,
    security_integration={
        "enabled": True,
        "authentication_required": True,
        "authorization_required": True,
        "default_auth_level": "medium"
    },
    observability_integration={
        "enabled": True,
        "log_level": "info",
        "metrics_enabled": True,
        "tracing_enabled": True
    }
)

# Define initialization options
initialization_options = InitializationOptions(
    fail_fast=True,
    initialization_timeout_seconds=120,
    initialization_log_level="debug",
    require_secure_channel=True,
    require_protocol_compatibility=True
)

# Initialize the Agent Framework
try:
    # Initialize with comprehensive configuration
    result = agent_framework.initialize(
        config=agent_framework_config,
        options=initialization_options
    )

    if result.success:
        logger.info(f"Agent Framework initialized successfully in {result.initialization_time_ms}ms")
        logger.info(f"Initialized components: {len(result.initialized_components)}")
        logger.info(f"Initialized agent types: {result.initialized_agent_types}")
        logger.info(f"Initialized protocols: {result.initialized_protocols}")
        logger.info(f"Initialized reasoning engines: {result.initialized_reasoning_engines}")

        # Emit initialization complete event
        event_system.emit("agent_framework_initialized", {
            "initialization_time_ms": result.initialization_time_ms,
            "agent_types": result.initialized_agent_types,
            "protocols": result.initialized_protocols,
            "timestamp": datetime.now().isoformat()
        })
    else:
        logger.error(f"Agent Framework initialization failed: {result.error_message}")
        logger.error(f"Failed components: {result.failed_components}")
        logger.error(f"Missing dependencies: {result.missing_dependencies}")

        # Handle initialization failure
        if result.failed_components:
            logger.info("Attempting to initialize with reduced functionality")

            # Create new initialization options skipping failed components
            retry_options = InitializationOptions(
                fail_fast=False,
                skip_components=result.failed_components,
                initialization_log_level="debug"
            )

            # Retry initialization with reduced functionality
            retry_result = agent_framework.initialize(
                config=agent_framework_config,
                options=retry_options
            )

            if retry_result.success:
                logger.info("Agent Framework initialized with reduced functionality")
            else:
                logger.error("Agent Framework initialization failed even with reduced functionality")
                # Notify system administrators
                notification_service.send_admin_notification(
                    severity="critical",
                    title="Agent Framework Initialization Failed",
                    message="Agent Framework failed to initialize even with reduced functionality",
                    details={
                        "error": retry_result.error_message,
                        "failed_components": retry_result.failed_components,
                        "timestamp": datetime.now().isoformat()
                    }
                )

except ConfigurationValidationError as e:
    logger.error(f"Configuration validation failed: {str(e)}")
    # Log detailed validation errors
    for error in e.validation_errors:
        logger.error(f"Validation error at {error.path}: {error.message}")

except ComponentInitializationError as e:
    logger.error(f"Component initialization failed: {str(e)}")
    # Log detailed component initialization error
    logger.error(f"Failed component: {e.component_name}, Error: {e.error_message}")

except DependencyMissingError as e:
    logger.error(f"Missing dependency: {str(e)}")
    # Log missing dependency details
    logger.error(f"Required dependency: {e.dependency_name}, Required by: {e.requester_name}")

except Exception as e:
    logger.error(f"Unexpected error during initialization: {str(e)}")
    # Log detailed error information and stack trace
    logger.exception("Initialization exception details:")
```

```python
def update_configuration(updates: Dict[str, Any],
                       options: Optional[ConfigurationUpdateOptions] = None) -> ConfigurationUpdateResult:
    """
    Update specific configuration parameters at runtime.

    Args:
        updates: Dict[str, Any] - Dictionary with configuration updates using dot notation paths
        options: Optional[ConfigurationUpdateOptions] - Options for the configuration update

    Returns:
        ConfigurationUpdateResult - Detailed result of the configuration update

    Raises:
        ConfigurationValidationError - If the updated configuration fails validation
        InvalidConfigurationPathError - If a configuration path is invalid
        ReadOnlyConfigurationError - If attempting to update read-only configuration
        DynamicConfigurationNotSupportedError - If dynamic configuration updates are not supported for a component
    """
```

**Data Structures:**

```python
class ConfigurationUpdateOptions:
    """
    Options for configuration updates.
    """
    validate_only: bool = False  # Whether to only validate the updates without applying
    skip_validation: bool = False  # Whether to skip validation (not recommended)
    notify_components: bool = True  # Whether to notify affected components of the update
    update_persistence: bool = True  # Whether to persist the update to storage
    reload_affected_components: bool = False  # Whether to reload affected components
    update_reason: Optional[str] = None  # Reason for the update (for audit purposes)
    update_source: Optional[str] = None  # Source of the update (user, system, etc.)
    ignore_errors: bool = False  # Whether to ignore errors and continue with valid updates
    update_priority: str = "normal"  # Priority of the update ("low", "normal", "high", "critical")
    apply_immediately: bool = True  # Whether to apply immediately or queue for later
    metadata: Dict[str, Any] = {}  # Additional metadata about the update

class ConfigurationPathStatus:
    """
    Status of a configuration path update.
    """
    path: str  # Configuration path
    success: bool  # Whether the update was successful
    previous_value: Any  # Previous value before update
    new_value: Any  # New value after update
    error_message: Optional[str] = None  # Error message if update failed
    validation_errors: List[Dict[str, Any]] = []  # Validation errors if any
    affected_components: List[str] = []  # Components affected by this update
    requires_restart: bool = False  # Whether this update requires a restart
    metadata: Dict[str, Any] = {}  # Additional metadata about the update

class ConfigurationUpdateResult:
    """
    Result of a configuration update operation.
    """
    success: bool  # Whether the overall update was successful
    update_time: datetime  # When the update was performed
    path_results: List[ConfigurationPathStatus] = []  # Status of each path update
    paths_updated: int = 0  # Number of paths successfully updated
    paths_failed: int = 0  # Number of paths that failed to update
    error_message: Optional[str] = None  # Error message if update failed
    validation_errors: List[Dict[str, Any]] = []  # Validation errors if any
    affected_components: List[str] = []  # Components affected by the update
    requires_restart: bool = False  # Whether any updates require a restart
    update_id: Optional[str] = None  # Unique ID for this update (for tracking)
    metadata: Dict[str, Any] = {}  # Additional metadata about the update

class InvalidConfigurationPathError(Exception):
    """
    Raised when a configuration path is invalid.
    """
    def __init__(self, path: str, message: str = "Invalid configuration path"):
        self.path = path
        self.message = message
        super().__init__(f"{message}: {path}")

class ReadOnlyConfigurationError(Exception):
    """
    Raised when attempting to update read-only configuration.
    """
    def __init__(self, path: str, message: str = "Cannot update read-only configuration"):
        self.path = path
        self.message = message
        super().__init__(f"{message}: {path}")

class DynamicConfigurationNotSupportedError(Exception):
    """
    Raised when dynamic configuration updates are not supported for a component.
    """
    def __init__(self, component: str, message: str = "Dynamic configuration not supported"):
        self.component = component
        self.message = message
        super().__init__(f"{message} for component: {component}")
```

**Example Usage:**

```python
# Example 1: Update message processing configuration and agent type capabilities

# Define configuration updates
updates = {
    # Update message processing configuration
    "message_processing.processing_threads": 12,  # Increase thread count
    "message_processing.max_queue_size": 3000,  # Increase queue size
    "message_processing.batch_size": 30,  # Increase batch size

    # Update timeout and priorities
    "default_timeout_seconds": 60,  # Increase default timeout

    # Update specific component configuration
    "components.message_router.config.default_strategy": "content_based",  # Change routing strategy

    # Enable additional capabilities for an agent type
    "agent_types[type=reasoning_agent].default_capabilities": [
        "reasoning", "tool_use", "memory_access", "planning", "knowledge_retrieval"
    ],

    # Update protocol adapter configuration
    "protocol_adapters.mcp.config.capability_mapping.knowledge_retrieval": "mcp:knowledge_access",

    # Update security integration
    "security_integration.authorization_required": True
}

# Define update options
update_options = ConfigurationUpdateOptions(
    validate_only=False,
    notify_components=True,
    update_persistence=True,
    reload_affected_components=True,
    update_reason="Performance optimization and capability enhancement",
    update_source="system_administrator",
    update_priority="high"
)

# Update the configuration
try:
    # Perform the update with comprehensive error handling
    result = agent_framework.update_configuration(
        updates=updates,
        options=update_options
    )

    if result.success:
        logger.info(f"Configuration updated successfully at {result.update_time}")
        logger.info(f"Updated {result.paths_updated} configuration paths")

        # Check if restart is required
        if result.requires_restart:
            logger.warning("Some configuration changes require a framework restart")
            # Notify administrators about restart requirement
            notification_service.send_admin_notification(
                severity="warning",
                title="Framework Restart Required",
                message="Some configuration changes require an Agent Framework restart",
                details={
                    "update_id": result.update_id,
                    "update_time": result.update_time.isoformat(),
                    "affected_components": result.affected_components
                }
            )

        # Log details about affected components
        if result.affected_components:
            logger.info(f"Affected components: {', '.join(result.affected_components)}")

            # If components were reloaded, verify their status
            if update_options.reload_affected_components:
                for component in result.affected_components:
                    component_status = agent_framework.get_component_status(component)
                    if component_status.status == "active":
                        logger.info(f"Component {component} successfully reloaded")
                    else:
                        logger.error(f"Component {component} failed to reload: {component_status.error_message}")

        # Emit configuration updated event with details
        event_system.emit("configuration_updated", {
            "update_id": result.update_id,
            "update_time": result.update_time.isoformat(),
            "paths_updated": result.paths_updated,
            "affected_components": result.affected_components,
            "update_reason": update_options.update_reason,
            "update_source": update_options.update_source,
            "requires_restart": result.requires_restart
        })
    else:
        logger.error(f"Configuration update failed: {result.error_message}")

        # Log detailed validation errors
        if result.validation_errors:
            logger.error("Validation errors:")
            for error in result.validation_errors:
                logger.error(f"Error at path {error['path']}: {error['message']}")

        # Log paths that were successfully updated before failure
        if result.paths_updated > 0:
            logger.info(f"Note: {result.paths_updated} paths were updated before failure")

            # Get list of successful paths
            successful_paths = [status.path for status in result.path_results if status.success]
            logger.info(f"Successfully updated paths: {', '.join(successful_paths)}")

            # Check if a rollback is needed
            if not update_options.ignore_errors:
                logger.info("Initiating rollback of partial updates...")

                # Create rollback updates to restore previous values
                rollback_updates = {}
                for status in result.path_results:
                    if status.success:
                        rollback_updates[status.path] = status.previous_value

                # Perform rollback
                rollback_result = agent_framework.update_configuration(
                    updates=rollback_updates,
                    options=ConfigurationUpdateOptions(
                        validate_only=False,
                        notify_components=True,
                        update_persistence=True,
                        update_reason="Rollback of failed update",
                        update_source="system",
                        update_priority="critical"
                    )
                )

                if rollback_result.success:
                    logger.info("Rollback completed successfully")
                else:
                    logger.error(f"Rollback failed: {rollback_result.error_message}")
                    # Critical system state, escalate to administrators
                    notification_service.send_admin_notification(
                        severity="critical",
                        title="Configuration Rollback Failed",
                        message="Configuration update failed and rollback was unsuccessful",
                        details={
                            "update_id": result.update_id,
                            "rollback_error": rollback_result.error_message,
                            "timestamp": datetime.now().isoformat()
                        }
                    )

except InvalidConfigurationPathError as e:
    logger.error(f"Invalid configuration path: {e.path}")
    logger.error(f"Error details: {e.message}")

except ReadOnlyConfigurationError as e:
    logger.error(f"Cannot update read-only configuration: {e.path}")
    logger.error(f"Error details: {e.message}")

except DynamicConfigurationNotSupportedError as e:
    logger.error(f"Dynamic configuration not supported for component: {e.component}")
    logger.error(f"Error details: {e.message}")
    logger.error("Restart required to apply configuration changes")

except Exception as e:
    logger.error(f"Unexpected error during configuration update: {str(e)}")
    logger.exception("Update exception details:")


# Example 2: Protocol-specific configuration update with validation only

# Define A2A protocol-specific configuration updates
a2a_protocol_updates = {
    # Update A2A protocol adapter configuration
    "protocol_adapters.a2a.config.endpoint": "https://new-a2a-endpoint.openmas.org/a2a",
    "protocol_adapters.a2a.config.security.authentication_required": True,
    "protocol_adapters.a2a.config.security.authentication_method": "oauth2",  # Change from JWT to OAuth2
    "protocol_adapters.a2a.config.security.oauth2_config": {
        "client_id": "${ENV:A2A_CLIENT_ID}",
        "token_endpoint": "https://auth.openmas.org/oauth2/token",
        "scope": "openmas.a2a.agent"
    },
    "protocol_adapters.a2a.config.capabilities.support_multipart": True,  # Enable multipart message support
    "protocol_adapters.a2a.config.rate_limit.max_requests_per_minute": 120  # Update rate limit
}

# Define validation-only options
validation_options = ConfigurationUpdateOptions(
    validate_only=True,  # Only validate, don't apply changes
    update_reason="A2A protocol endpoint migration",
    update_source="system_migration"
)

# Validate the configuration updates
try:
    # Perform validation only
    validation_result = agent_framework.update_configuration(
        updates=a2a_protocol_updates,
        options=validation_options
    )

    if validation_result.success:
        logger.info("A2A protocol configuration updates validated successfully")

        # Notify about upcoming changes
        notification_service.notify_upcoming_changes(
            title="A2A Protocol Endpoint Migration",
            message="The A2A protocol endpoint will be migrated to a new URL",
            scheduled_time=datetime.now() + timedelta(days=2),
            details={
                "current_endpoint": "http://localhost:8080/a2a",
                "new_endpoint": "https://new-a2a-endpoint.openmas.org/a2a",
                "migration_time": (datetime.now() + timedelta(days=2)).isoformat(),
                "auth_changes": "Switching from JWT to OAuth2 authentication"
            }
        )

        # Schedule the actual update for later
        scheduler.schedule_task(
            task_type="configuration_update",
            execution_time=datetime.now() + timedelta(days=2),
            parameters={
                "updates": a2a_protocol_updates,
                "options": ConfigurationUpdateOptions(
                    validate_only=False,
                    notify_components=True,
                    update_persistence=True,
                    reload_affected_components=True,
                    update_reason="A2A protocol endpoint migration",
                    update_source="scheduled_migration",
                    update_priority="high"
                )
            },
            task_id="a2a_protocol_migration"
        )

        logger.info("A2A protocol migration scheduled for execution in 2 days")
    else:
        logger.error(f"A2A protocol configuration validation failed: {validation_result.error_message}")

        # Log validation errors in detail
        for error in validation_result.validation_errors:
            logger.error(f"Validation error at {error['path']}: {error['message']}")

        # Cancel the scheduled migration if it exists
        if scheduler.task_exists("a2a_protocol_migration"):
            scheduler.cancel_task("a2a_protocol_migration")
            logger.info("Scheduled A2A protocol migration has been canceled due to validation failure")

except Exception as e:
    logger.error(f"Error validating A2A protocol configuration: {str(e)}")

    # Cancel the migration if scheduled
    if scheduler.task_exists("a2a_protocol_migration"):
        scheduler.cancel_task("a2a_protocol_migration")
        logger.info("Scheduled A2A protocol migration has been canceled due to validation error")
```

```python
def create_agent_from_config(agent_config: AgentConfig,
                           options: Optional[AgentCreationOptions] = None) -> AgentCreationResult:
    """
    Create an agent instance based on configuration.

    Args:
        agent_config: AgentConfig - Agent configuration object
        options: Optional[AgentCreationOptions] - Options for agent creation

    Returns:
        AgentCreationResult - Result containing the created agent and metadata

    Raises:
        ConfigurationValidationError - If the agent configuration fails validation
        AgentTypeNotFoundError - If the specified agent type is not found
        CapabilityNotFoundError - If a requested capability is not found
        ReasoningEngineNotFoundError - If the requested reasoning engine is not found
        ProtocolNotFoundError - If a requested protocol is not found
        AgentCreationError - If there was an error creating the agent
    """
```

**Data Structures:**

```python
class AgentCapability:
    """
    Configuration for an agent capability.
    """
    name: str  # Name of the capability
    enabled: bool = True  # Whether the capability is enabled
    configuration: Dict[str, Any] = {}  # Capability-specific configuration
    dependencies: List[str] = []  # Other capabilities this capability depends on
    protocol_mappings: Dict[str, str] = {}  # Protocol-specific capability mappings
    parameters: Dict[str, Any] = {}  # Parameters for the capability
    metadata: Dict[str, Any] = {}  # Additional metadata about the capability

class AgentProtocolConfig:
    """
    Configuration for an agent's protocol support.
    """
    name: str  # Name of the protocol
    enabled: bool = True  # Whether the protocol is enabled
    configuration: Dict[str, Any] = {}  # Protocol-specific configuration
    adapter_instance: Optional[str] = None  # Optional adapter instance name
    capability_mappings: Dict[str, str] = {}  # Capability mappings for this protocol
    metadata: Dict[str, Any] = {}  # Additional metadata about the protocol configuration

class AgentReasoningEngineConfig:
    """
    Configuration for an agent's reasoning engine.
    """
    name: str  # Name of the reasoning engine
    enabled: bool = True  # Whether the reasoning engine is enabled
    configuration: Dict[str, Any] = {}  # Reasoning engine-specific configuration
    model_config: Optional[Dict[str, Any]] = None  # Configuration for the model (if applicable)
    parameters: Dict[str, Any] = {}  # Parameters for the reasoning engine
    metadata: Dict[str, Any] = {}  # Additional metadata about the reasoning engine

class AgentConfig:
    """
    Configuration for an agent instance.
    """
    id: str  # Unique identifier for this agent
    type: str  # Type of agent
    name: Optional[str] = None  # Human-readable name for this agent
    description: Optional[str] = None  # Description of this agent
    capabilities: List[Union[str, AgentCapability]] = []  # Capabilities of this agent
    reasoning_engine: Optional[Union[str, AgentReasoningEngineConfig]] = None  # Reasoning engine for this agent
    protocols: List[Union[str, AgentProtocolConfig]] = []  # Protocols supported by this agent
    configuration: Dict[str, Any] = {}  # Agent-specific configuration
    lifecycle: Dict[str, Any] = {}  # Lifecycle configuration for this agent
    security: Dict[str, Any] = {}  # Security configuration for this agent
    observability: Dict[str, Any] = {}  # Observability configuration for this agent
    resource_limits: Dict[str, Any] = {}  # Resource limits for this agent
    metadata: Dict[str, Any] = {}  # Additional metadata about this agent

class AgentCreationOptions:
    """
    Options for agent creation.
    """
    validate_only: bool = False  # Whether to only validate the configuration without creating the agent
    start_immediately: bool = True  # Whether to start the agent immediately after creation
    validate_capabilities: bool = True  # Whether to validate the agent's capabilities
    validate_protocols: bool = True  # Whether to validate the agent's protocols
    auto_resolve_dependencies: bool = True  # Whether to automatically resolve capability dependencies
    creation_context: Dict[str, Any] = {}  # Additional context for agent creation
    creation_reason: Optional[str] = None  # Reason for creating this agent
    creation_source: Optional[str] = None  # Source of the creation request
    security_context: Optional[Dict[str, Any]] = None  # Security context for agent creation
    creation_timeout_seconds: int = 30  # Timeout for agent creation

class AgentCreationResult:
    """
    Result of agent creation.
    """
    success: bool  # Whether the agent was created successfully
    agent: Optional[Agent] = None  # The created agent instance
    agent_id: str  # ID of the created agent
    agent_type: str  # Type of the created agent
    creation_time: datetime  # When the agent was created
    started: bool = False  # Whether the agent was started
    error_message: Optional[str] = None  # Error message if creation failed
    validation_errors: List[Dict[str, Any]] = []  # Validation errors if any
    enabled_capabilities: List[str] = []  # Capabilities that were enabled
    enabled_protocols: List[str] = []  # Protocols that were enabled
    reasoning_engine: Optional[str] = None  # Reasoning engine that was configured
    warnings: List[str] = []  # Warnings during agent creation
    metadata: Dict[str, Any] = {}  # Additional metadata about the agent creation

class AgentTypeNotFoundError(Exception):
    """
    Raised when the specified agent type is not found.
    """
    def __init__(self, agent_type: str, available_types: List[str]):
        self.agent_type = agent_type
        self.available_types = available_types
        message = f"Agent type '{agent_type}' not found. Available types: {', '.join(available_types)}"
        super().__init__(message)

class CapabilityNotFoundError(Exception):
    """
    Raised when a requested capability is not found.
    """
    def __init__(self, capability: str, agent_type: str, available_capabilities: List[str]):
        self.capability = capability
        self.agent_type = agent_type
        self.available_capabilities = available_capabilities
        message = f"Capability '{capability}' not found for agent type '{agent_type}'. Available capabilities: {', '.join(available_capabilities)}"
        super().__init__(message)

class ReasoningEngineNotFoundError(Exception):
    """
    Raised when the requested reasoning engine is not found.
    """
    def __init__(self, reasoning_engine: str, agent_type: str, available_engines: List[str]):
        self.reasoning_engine = reasoning_engine
        self.agent_type = agent_type
        self.available_engines = available_engines
        message = f"Reasoning engine '{reasoning_engine}' not found for agent type '{agent_type}'. Available engines: {', '.join(available_engines)}"
        super().__init__(message)

class ProtocolNotFoundError(Exception):
    """
    Raised when a requested protocol is not found.
    """
    def __init__(self, protocol: str, available_protocols: List[str]):
        self.protocol = protocol
        self.available_protocols = available_protocols
        message = f"Protocol '{protocol}' not found. Available protocols: {', '.join(available_protocols)}"
        super().__init__(message)

class AgentCreationError(Exception):
    """
    Raised when there is an error creating an agent.
    """
    def __init__(self, agent_id: str, agent_type: str, message: str, details: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.details = details or {}
        error_message = f"Error creating agent '{agent_id}' of type '{agent_type}': {message}"
        super().__init__(error_message)
```

**Example Usage:**

```python
# Example 1: Create a BDI reasoning agent with multi-protocol support

# Define reasoning engine configuration for BDI
bdi_config = AgentReasoningEngineConfig(
    name="bdi",
    configuration={
        "belief_update_strategy": "probabilistic",
        "desire_selection_strategy": "utility_based",
        "intention_revision_strategy": "priority_based",
        "planning": {
            "planning_depth": 5,
            "replanning_threshold": 0.7,
            "plan_library_path": "plans/agent_plans.json"
        },
        "belief_base": {
            "storage_type": "in_memory",
            "consistency_check_enabled": True
        }
    },
    parameters={
        "max_beliefs": 1000,
        "max_desires": 50,
        "max_intentions": 10,
        "reasoning_interval_ms": 200
    }
)

# Define capabilities with protocol-specific mappings
capabilities = [
    AgentCapability(
        name="reasoning",
        configuration={
            "max_reasoning_depth": 5,
            "reasoning_timeout_ms": 2000
        },
        protocol_mappings={
            "a2a": "a2a:reasoning",
            "mcp": "mcp:reasoning"
        }
    ),
    AgentCapability(
        name="planning",
        configuration={
            "plan_selection_strategy": "hierarchical",
            "plan_adaptation_enabled": True
        },
        protocol_mappings={
            "a2a": "a2a:planning",
            "mcp": "mcp:planning"
        },
        dependencies=["reasoning"]
    ),
    AgentCapability(
        name="tool_use",
        configuration={
            "tool_discovery_enabled": True,
            "tool_result_caching_enabled": True
        },
        protocol_mappings={
            "a2a": "a2a:tool_use",
            "mcp": "mcp:tool_invocation"
        }
    ),
    AgentCapability(
        name="knowledge_retrieval",
        configuration={
            "knowledge_sources": ["agent_kb", "shared_kb", "external_sources"],
            "retrieval_strategy": "semantic"
        },
        protocol_mappings={
            "a2a": "a2a:knowledge_access",
            "mcp": "mcp:knowledge_access"
        }
    )
]

# Define protocol configurations
protocols = [
    AgentProtocolConfig(
        name="a2a",
        configuration={
            "endpoint_type": "active",  # Agent initiates connections
            "message_format": "json",
            "request_timeout_ms": 5000,
            "use_compression": True
        },
        capability_mappings={
            "reasoning": "a2a:reasoning",
            "planning": "a2a:planning",
            "tool_use": "a2a:tool_use",
            "knowledge_retrieval": "a2a:knowledge_access"
        }
    ),
    AgentProtocolConfig(
        name="mcp",
        configuration={
            "endpoint_type": "passive",  # Agent responds to requests
            "message_format": "json",
            "request_timeout_ms": 10000,
            "streaming_enabled": True
        },
        capability_mappings={
            "reasoning": "mcp:reasoning",
            "planning": "mcp:planning",
            "tool_use": "mcp:tool_invocation",
            "knowledge_retrieval": "mcp:knowledge_access"
        }
    )
]

# Create the agent configuration
agent_config = AgentConfig(
    id="strategic_reasoning_agent_01",
    type="reasoning_agent",
    name="Strategic Reasoning Agent",
    description="Agent specialized in strategic reasoning and planning",
    capabilities=capabilities,
    reasoning_engine=bdi_config,
    protocols=protocols,
    configuration={
        "specialization": "strategic_planning",
        "response_generation": {
            "format": "structured",
            "detail_level": "high"
        },
        "execution_mode": "autonomous"
    },
    lifecycle={
        "startup_sequence": ["initialize_kb", "load_plans", "register_capabilities"],
        "shutdown_sequence": ["complete_intentions", "persist_state", "deregister_capabilities"],
        "heartbeat_interval_seconds": 60
    },
    security={
        "authentication_required": True,
        "authorization_level": "agent",
        "secure_communication": True
    },
    observability={
        "logging_level": "info",
        "metrics_enabled": True,
        "tracing_enabled": True,
        "event_recording": {
            "belief_changes": True,
            "intention_changes": True,
            "plan_execution": True
        }
    },
    resource_limits={
        "max_memory_mb": 512,
        "max_cpu_percent": 50,
        "max_active_tasks": 5,
        "max_concurrent_conversations": 10
    },
    metadata={
        "created_by": "system_admin",
        "creation_reason": "strategic_planning_capability",
        "tags": ["reasoning", "planning", "strategic", "autonomous"],
        "priority": "high"
    }
)

# Define agent creation options
creation_options = AgentCreationOptions(
    start_immediately=True,
    validate_capabilities=True,
    validate_protocols=True,
    auto_resolve_dependencies=True,
    creation_reason="Deploy strategic reasoning capability",
    creation_source="deployment_system",
    creation_timeout_seconds=60
)

# Create the agent
try:
    # Create agent with complete configuration
    result = agent_framework.create_agent_from_config(
        agent_config=agent_config,
        options=creation_options
    )

    if result.success:
        logger.info(f"Agent created successfully: {result.agent_id}")
        logger.info(f"Agent type: {result.agent_type}")
        logger.info(f"Reasoning engine: {result.reasoning_engine}")
        logger.info(f"Enabled capabilities: {result.enabled_capabilities}")
        logger.info(f"Enabled protocols: {result.enabled_protocols}")

        # Access the agent instance
        agent = result.agent

        # Check if agent was started
        if result.started:
            logger.info("Agent was started automatically")

            # Get agent status
            status = agent.get_status()
            logger.info(f"Agent status: {status.state}")

            # Initialize agent with domain-specific knowledge if needed
            if status.state == "active":
                # Load domain knowledge
                domain_knowledge = knowledge_repository.get_domain_knowledge("strategic_planning")

                # Initialize agent with domain knowledge
                agent.initialize_knowledge_base(domain_knowledge)
                logger.info("Agent initialized with strategic planning domain knowledge")

                # Assign initial tasks if needed
                initial_task = task_repository.get_task("strategic_analysis_01")
                agent.assign_task(initial_task)
                logger.info(f"Assigned initial task to agent: {initial_task.id}")
        else:
            logger.info("Agent created but not started")

            # Start the agent manually if needed
            agent.start()
            logger.info("Agent started manually")

        # Emit agent created event
        event_system.emit("agent_created", {
            "agent_id": result.agent_id,
            "agent_type": result.agent_type,
            "reasoning_engine": result.reasoning_engine,
            "capabilities": result.enabled_capabilities,
            "protocols": result.enabled_protocols,
            "creation_time": result.creation_time.isoformat(),
            "created_by": creation_options.creation_source
        })
    else:
        logger.error(f"Agent creation failed: {result.error_message}")

        # Log detailed validation errors
        if result.validation_errors:
            logger.error("Validation errors:")
            for error in result.validation_errors:
                logger.error(f"Error at {error['path']}: {error['message']}")

        # Log warnings
        if result.warnings:
            logger.warning("Creation warnings:")
            for warning in result.warnings:
                logger.warning(warning)

except AgentTypeNotFoundError as e:
    logger.error(f"Agent type not found: {e.agent_type}")
    logger.error(f"Available agent types: {', '.join(e.available_types)}")

except CapabilityNotFoundError as e:
    logger.error(f"Capability not found: {e.capability}")
    logger.error(f"Available capabilities for agent type '{e.agent_type}': {', '.join(e.available_capabilities)}")

except ReasoningEngineNotFoundError as e:
    logger.error(f"Reasoning engine not found: {e.reasoning_engine}")
    logger.error(f"Available reasoning engines for agent type '{e.agent_type}': {', '.join(e.available_engines)}")

except ProtocolNotFoundError as e:
    logger.error(f"Protocol not found: {e.protocol}")
    logger.error(f"Available protocols: {', '.join(e.available_protocols)}")

except AgentCreationError as e:
    logger.error(f"Error creating agent: {str(e)}")
    if e.details:
        logger.error("Error details:")
        for key, value in e.details.items():
            logger.error(f"  {key}: {value}")

except Exception as e:
    logger.error(f"Unexpected error during agent creation: {str(e)}")
    logger.exception("Creation exception details:")


# Example 2: Create a conversational agent with LLM reasoning engine

# Define LLM reasoning engine configuration
llm_config = AgentReasoningEngineConfig(
    name="llm",
    configuration={
        "model_provider": "openai",
        "inference_mode": "streaming",
        "context_management": "window_based",
        "prompt_management": {
            "template_path": "prompts/conversational_agent.yaml",
            "system_message": "You are a helpful assistant specialized in conversation."
        }
    },
    model_config={
        "model_name": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000,
        "top_p": 0.95,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5
    },
    parameters={
        "max_context_length": 8000,
        "context_window_overlap": 200,
        "reasoning_steps_per_response": 3,
        "memory_retention_strategy": "importance_based"
    }
)

# Create the conversational agent configuration
conversational_agent_config = AgentConfig(
    id="conversational_agent_03",
    type="conversational_agent",
    name="Customer Support Assistant",
    description="Conversational agent specialized in customer support",
    capabilities=[
        "conversation",
        "memory_access",
        "knowledge_retrieval",
        "tool_use"
    ],
    reasoning_engine=llm_config,
    protocols=["mcp", "http"],  # Support MCP and HTTP protocols
    configuration={
        "specialization": "customer_support",
        "domain": "product_assistance",
        "conversation_style": "helpful_professional",
        "knowledge_bases": ["product_documentation", "faq", "troubleshooting"]
    },
    security={
        "authentication_required": True,
        "pii_handling": "mask_and_log",
        "content_filtering": "moderate"
    },
    observability={
        "conversation_logging": True,
        "session_recording": True,
        "performance_metrics": True
    }
)

# Create the agent with minimal options
try:
    # Create the conversational agent
    result = agent_framework.create_agent_from_config(
        agent_config=conversational_agent_config
    )  # Using default options

    if result.success:
        logger.info(f"Conversational agent created: {result.agent_id}")

        # Register agent with the conversation service
        conversation_service.register_agent(
            agent_id=result.agent_id,
            agent_name=conversational_agent_config.name,
            specialization="customer_support",
            supported_protocols=["mcp", "http"]
        )

        logger.info("Agent registered with conversation service")
    else:
        logger.error(f"Failed to create conversational agent: {result.error_message}")

except Exception as e:
    logger.error(f"Error creating conversational agent: {str(e)}")
```

#### Events

```python
class ConfigurationUpdatedEvent:
    """
    Event emitted when configuration has been updated.
    """
    event_name: str = "configuration_updated"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        update_id: str  # Unique identifier for this update
        update_time: datetime  # When the update was performed
        updated_paths: List[str]  # Configuration paths that were updated
        affected_components: List[str]  # Components affected by the update
        update_source: Optional[str] = None  # Source of the update (user, system, etc.)
        update_reason: Optional[str] = None  # Reason for the update
        requires_restart: bool = False  # Whether any updates require a restart
        update_details: Dict[str, Any] = {}  # Detailed information about the updates
        metadata: Dict[str, Any] = {}  # Additional metadata about the update
```

**Example Usage:**
```python
# Subscribe to configuration updated events
@event_system.subscribe(ConfigurationUpdatedEvent.event_name)
def handle_configuration_update(event: ConfigurationUpdatedEvent):
    payload = event.payload
    update_id = payload.update_id
    updated_paths = payload.updated_paths
    affected_components = payload.affected_components

    logger.info(f"Configuration update {update_id} received with {len(updated_paths)} path updates")

    # Check if this component is affected
    component_name = get_current_component_name()
    if component_name in affected_components:
        logger.info(f"This component ({component_name}) is affected by the update")

        # Process updates relevant to this component
        component_updates = {}
        for path in updated_paths:
            if path.startswith(f"components.{component_name}"):
                # Get the updated configuration value
                config_value = configuration_system.get_configuration_value(path)
                # Store in component updates
                component_updates[path] = config_value

        if component_updates:
            logger.info(f"Processing {len(component_updates)} updates for this component")

            # Apply the updates to the component
            try:
                result = apply_component_updates(component_updates)
                logger.info(f"Applied {result.applied_count} updates successfully")

                # If any updates require a component restart
                if result.requires_restart:
                    logger.info("Component restart required after configuration update")

                    # Check if we should restart automatically
                    if payload.update_details.get("auto_restart_components", False):
                        logger.info("Automatically restarting component...")
                        restart_component()
                    else:
                        logger.warning("Manual restart required for component to apply all updates")

                # Emit component updated event
                event_system.emit("component_configuration_updated", {
                    "component_name": component_name,
                    "update_id": update_id,
                    "updated_paths": list(component_updates.keys()),
                    "requires_restart": result.requires_restart
                })

            except Exception as e:
                logger.error(f"Error applying configuration updates: {str(e)}")

                # Report configuration update failure
                error_reporting.report_error(
                    error_type="configuration_update_failure",
                    component=component_name,
                    details={
                        "update_id": update_id,
                        "error_message": str(e),
                        "updated_paths": list(component_updates.keys())
                    }
                )

    # If framework restart is required, notify administrators
    if payload.requires_restart:
        logger.warning("Framework restart required to apply all configuration updates")

        # Send notification if configured
        if notification_config.get("notify_on_restart_required", True):
            notification_service.send_admin_notification(
                severity="warning",
                title="Framework Restart Required",
                message="A configuration update requires an Agent Framework restart",
                details={
                    "update_id": update_id,
                    "update_time": payload.update_time.isoformat(),
                    "affected_components": affected_components,
                    "update_source": payload.update_source
                }
            )
```

```python
class AgentConfigurationValidatedEvent:
    """
    Event emitted when agent configuration has been validated.
    """
    event_name: str = "agent_configuration_validated"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        agent_id: str  # ID of the agent whose configuration was validated
        agent_type: str  # Type of the agent
        validation_id: str  # Unique identifier for this validation
        is_valid: bool  # Whether the configuration is valid
        validation_errors: List[Dict[str, Any]] = []  # Validation errors if any
        validation_warnings: List[Dict[str, Any]] = []  # Validation warnings if any
        validated_capabilities: List[str] = []  # Capabilities that were validated
        validated_protocols: List[str] = []  # Protocols that were validated
        reasoning_engine: Optional[str] = None  # Reasoning engine that was validated
        validation_context: Dict[str, Any] = {}  # Context in which validation was performed
        metadata: Dict[str, Any] = {}  # Additional metadata about the validation
```

**Example Usage:**
```python
# Subscribe to agent configuration validated events
@event_system.subscribe(AgentConfigurationValidatedEvent.event_name)
def handle_agent_configuration_validation(event: AgentConfigurationValidatedEvent):
    payload = event.payload
    agent_id = payload.agent_id
    agent_type = payload.agent_type
    is_valid = payload.is_valid

    logger.info(f"Agent configuration validation for {agent_id} (type: {agent_type}): Valid={is_valid}")

    # If validation was successful
    if is_valid:
        logger.info(f"Validated capabilities: {', '.join(payload.validated_capabilities)}")
        logger.info(f"Validated protocols: {', '.join(payload.validated_protocols)}")

        if payload.reasoning_engine:
            logger.info(f"Validated reasoning engine: {payload.reasoning_engine}")

        # If we're in agent creation process, proceed with creation
        creation_context = payload.validation_context.get("creation_context")
        if creation_context and creation_context.get("is_creation_validation", False):
            logger.info("Proceeding with agent creation after successful validation")

            # Retrieve the validated configuration
            agent_config = configuration_system.get_agent_configuration(agent_id)

            # Create the agent
            creation_options = creation_context.get("creation_options", {})
            result = agent_framework.create_agent_instance(agent_config, creation_options)

            if result.success:
                logger.info(f"Agent {agent_id} created successfully after validation")
            else:
                logger.error(f"Agent creation failed after validation: {result.error_message}")
    else:
        # Log validation errors
        logger.error(f"Agent configuration validation failed with {len(payload.validation_errors)} errors")
        for error in payload.validation_errors:
            logger.error(f"Validation error at {error['path']}: {error['message']}")

        # Log validation warnings
        if payload.validation_warnings:
            logger.warning(f"Validation produced {len(payload.validation_warnings)} warnings")
            for warning in payload.validation_warnings:
                logger.warning(f"Validation warning at {warning['path']}: {warning['message']}")

        # If in creation process, report failure
        creation_context = payload.validation_context.get("creation_context")
        if creation_context and creation_context.get("is_creation_validation", False):
            logger.error("Agent creation aborted due to validation failure")

            # Notify creator about validation failure
            creator_id = creation_context.get("creator_id")
            if creator_id:
                notification_service.notify_user(
                    user_id=creator_id,
                    notification_type="validation_failure",
                    title=f"Agent Configuration Validation Failed: {agent_id}",
                    message=f"The configuration for agent {agent_id} failed validation with {len(payload.validation_errors)} errors.",
                    details={
                        "agent_id": agent_id,
                        "agent_type": agent_type,
                        "validation_errors": payload.validation_errors,
                        "validation_warnings": payload.validation_warnings
                    }
                )
```

```python
class AgentConfigurationChangedEvent:
    """
    Event emitted when agent configuration has been changed.
    """
    event_name: str = "agent_configuration_changed"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        agent_id: str  # ID of the agent whose configuration was changed
        agent_type: str  # Type of the agent
        change_id: str  # Unique identifier for this change
        change_time: datetime  # When the change was performed
        changed_paths: List[str]  # Configuration paths that were changed
        change_source: Optional[str] = None  # Source of the change (user, system, etc.)
        change_reason: Optional[str] = None  # Reason for the change
        requires_agent_restart: bool = False  # Whether the agent needs to be restarted
        active_session_affected: bool = False  # Whether active sessions are affected
        change_details: Dict[str, Any] = {}  # Detailed information about the changes
        metadata: Dict[str, Any] = {}  # Additional metadata about the change
```

**Example Usage:**
```python
# Example: Emitting an agent configuration changed event

def update_agent_protocol_config(agent_id: str, protocol_name: str, protocol_config: Dict[str, Any]) -> bool:
    # Get the current agent configuration
    agent_config = configuration_system.get_agent_configuration(agent_id)

    if not agent_config:
        logger.error(f"Cannot update protocol config: Agent {agent_id} not found")
        return False

    # Check if the protocol exists in the agent configuration
    protocol_found = False
    for protocol in agent_config.protocols:
        if isinstance(protocol, str):
            if protocol == protocol_name:
                protocol_found = True
                break
        else:  # AgentProtocolConfig instance
            if protocol.name == protocol_name:
                protocol_found = True
                break

    if not protocol_found:
        logger.error(f"Protocol {protocol_name} not found in agent {agent_id} configuration")
        return False

    # Build the configuration path
    config_path = f"agents[id={agent_id}].protocols[name={protocol_name}].configuration"

    # Update the protocol configuration
    update_result = configuration_system.update_configuration({
        config_path: protocol_config
    })

    if update_result.success:
        # Determine if restart is required based on protocol configuration changes
        requires_restart = any(key in protocol_config for key in ["endpoint_type", "adapter_instance"])
        active_session_affected = "message_format" in protocol_config or "streaming_enabled" in protocol_config

        # Emit agent configuration changed event
        event_system.emit(
            event_name="agent_configuration_changed",
            payload=AgentConfigurationChangedEvent.Payload(
                agent_id=agent_id,
                agent_type=agent_config.type,
                change_id=f"protocol_update_{uuid.uuid4().hex[:8]}",
                change_time=datetime.now(),
                changed_paths=[config_path],
                change_source="agent_management_api",
                change_reason=f"Protocol {protocol_name} configuration update",
                requires_agent_restart=requires_restart,
                active_session_affected=active_session_affected,
                change_details={
                    "protocol": protocol_name,
                    "updated_config_keys": list(protocol_config.keys()),
                    "previous_config": get_previous_protocol_config(agent_id, protocol_name)
                }
            )
        )

        logger.info(f"Protocol {protocol_name} configuration updated for agent {agent_id}")

        # If restart is required, notify agent manager
        if requires_restart:
            agent_manager.queue_agent_restart(
                agent_id=agent_id,
                restart_reason=f"Protocol {protocol_name} configuration update requires restart",
                restart_delay_seconds=30  # Give time for current operations to complete
            )

            logger.info(f"Agent {agent_id} restart queued due to protocol configuration change")

        # If active sessions are affected, notify session manager
        if active_session_affected:
            session_manager.notify_protocol_config_change(
                agent_id=agent_id,
                protocol_name=protocol_name,
                affected_config_keys=list(protocol_config.keys())
            )

            logger.info(f"Session manager notified of protocol configuration change affecting active sessions")

        return True
    else:
        logger.error(f"Failed to update protocol {protocol_name} configuration: {update_result.error_message}")
        return False

# Function to get previous protocol configuration (for comparison)
def get_previous_protocol_config(agent_id: str, protocol_name: str) -> Dict[str, Any]:
    agent_config = configuration_system.get_agent_configuration(agent_id)

    for protocol in agent_config.protocols:
        if isinstance(protocol, str):
            continue
        if protocol.name == protocol_name:
            return protocol.configuration

    return {}
```

```python
class ConfigurationSchemaRegisteredEvent:
    """
    Event emitted when a configuration schema is registered.
    """
    event_name: str = "configuration_schema_registered"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        schema_name: str  # Name of the schema that was registered
        schema_id: str  # Unique identifier for the schema
        registration_time: datetime  # When the schema was registered
        component_name: str  # Component that owns the schema
        schema_version: str  # Version of the schema
        schema_type: str  # Type of schema ("component", "agent", "capability", etc.)
        schema_description: Optional[str] = None  # Description of the schema
        replaced_existing: bool = False  # Whether an existing schema was replaced
        schema_properties_count: int = 0  # Number of properties in the schema
        required_properties: List[str] = []  # Required properties in the schema
        metadata: Dict[str, Any] = {}  # Additional metadata about the schema
```

**Example Usage:**
```python
# Subscribe to configuration schema registered events
@event_system.subscribe(ConfigurationSchemaRegisteredEvent.event_name)
def handle_schema_registration(event: ConfigurationSchemaRegisteredEvent):
    payload = event.payload
    schema_name = payload.schema_name
    component_name = payload.component_name
    schema_version = payload.schema_version

    logger.info(f"Configuration schema '{schema_name}' registered by component '{component_name}' (version: {schema_version})")

    # If this is a schema for your component, update your validation logic
    if component_name == get_current_component_name():
        logger.info("Updating local schema validation rules based on registered schema")

        # Retrieve the full schema
        schema = configuration_system.get_configuration_schema(schema_name)

        # Update local validation rules
        update_validation_rules(schema)

        logger.info(f"Updated validation rules with {payload.schema_properties_count} properties from schema")

    # If this is a new agent type schema, update agent type registry
    if payload.schema_type == "agent" and not payload.replaced_existing:
        logger.info(f"New agent type schema registered: {schema_name}")

        # Update agent type registry
        agent_type_registry.add_agent_type(
            type_name=schema_name,
            schema_id=payload.schema_id,
            schema_version=schema_version,
            required_properties=payload.required_properties,
            metadata=payload.metadata
        )

        logger.info(f"Agent type {schema_name} added to registry")

    # If this is a capability schema, update capability registry
    if payload.schema_type == "capability":
        logger.info(f"Capability schema registered: {schema_name}")

        # Update capability registry
        capability_registry.update_capability_schema(
            capability_name=schema_name,
            schema_id=payload.schema_id,
            schema_version=schema_version,
            required_properties=payload.required_properties,
            metadata=payload.metadata
        )

        logger.info(f"Capability {schema_name} updated in registry")
```

### Agent Framework → Configuration System

#### Methods/Functions
- `configuration_system.get_agent_configuration(agent_id: str) → AgentConfig`
  - **Purpose**: Retrieve configuration for a specific agent
  - **Parameters**: Agent identifier
  - **Returns**: Agent configuration object
  - **Example**:
    ```python
    config = configuration_system.get_agent_configuration(
        agent_id="reasoning_agent_01"
    )
    ```

- `configuration_system.validate_agent_configuration(config: AgentConfig) → ValidationResult`
  - **Purpose**: Validate agent configuration against schema
  - **Parameters**: Agent configuration object
  - **Returns**: Validation result with any errors
  - **Example**:
    ```python
    result = configuration_system.validate_agent_configuration(
        config=agent_config
    )
    ```

- `configuration_system.register_configuration_schema(schema_name: str, schema: ConfigSchema) → bool`
  - **Purpose**: Register a configuration schema for component
  - **Parameters**:
    - `schema_name`: Name for the schema
    - `schema`: Schema definition
  - **Returns**: Boolean indicating successful registration
  - **Example**:
    ```python
    success = configuration_system.register_configuration_schema(
        schema_name="agent_capabilities",
        schema=capability_schema
    )
    ```

#### Events
- `configuration_requested`
  - **Purpose**: Notifies when configuration is requested
  - **Payload**: Requester ID, configuration path
  - **Subscribers**: Configuration System audit log

- `configuration_validation_failed`
  - **Purpose**: Notifies when configuration validation fails
  - **Payload**: Validation errors, configuration object
  - **Subscribers**: Configuration System error handler

## Data Flows

### Agent Framework Initialization Flow
1. **Configuration System → Agent Framework**: Configuration System provides initialization configuration
2. **Agent Framework Processing**: Agent Framework initializes components based on configuration
3. **Agent Framework → Configuration System**: Agent Framework registers component schemas
4. **Agent Framework → Observers**: Agent Framework notifies observers of successful initialization

### Agent Creation Flow
1. **Agent Framework → Configuration System**: Agent Framework requests agent configuration
2. **Configuration System Processing**: Configuration System validates and retrieves configuration
3. **Configuration System → Agent Framework**: Configuration System returns validated configuration
4. **Agent Framework Processing**: Agent Framework creates agent based on configuration

## Configuration Dependencies

The following configuration parameters affect this interaction:

```yaml
agent_framework:
  agent_types:
    - type: "reasoning_agent"
      implementation_class: "ReasoningAgent"
      default_capabilities: ["reasoning", "tool_use"]

    - type: "task_agent"
      implementation_class: "TaskAgent"
      default_capabilities: ["task_execution", "reporting"]

  message_processing:
    max_queue_size: 1000
    processing_threads: 4
    priority_levels: 3

  default_timeout_seconds: 30

  components:
    lifecycle_manager:
      enabled: true
      implementation_class: "DefaultLifecycleManager"

    message_router:
      enabled: true
      implementation_class: "DefaultMessageRouter"

    capability_registry:
      enabled: true
      implementation_class: "DefaultCapabilityRegistry"

agents:
  - id: "reasoning_agent_01"
    type: "reasoning_agent"
    capabilities: ["reasoning", "tool_use", "planning"]
    reasoning_engine: "bdi"
    protocols: ["a2a", "mcp"]
```

## Error Handling

1. **Configuration Validation Failures**:
   - Detailed validation error reports with path information
   - Support for partial initialization with validated configuration
   - Fallback to default values for invalid configuration

2. **Missing Configuration**:
   - Automatic use of defaults for missing optional configuration
   - Clear error reporting for missing required configuration
   - Configuration path resolution to find configuration in alternative locations

3. **Runtime Configuration Updates**:
   - Validation of updates before application
   - Atomic updates to prevent partial configuration states
   - Rollback capability for failed updates

## Extension Points

1. **Custom Agent Types**:
   - New agent types can be defined through configuration
   - Agent type registry allows dynamic registration
   - Example:
     ```yaml
     agent_framework:
       agent_types:
         - type: "custom_agent"
           implementation_class: "my_package.CustomAgent"
           default_capabilities: ["my_capability", "standard_capability"]
           initialization_parameters:
             custom_param1: "value1"
             custom_param2: 42
     ```

2. **Configuration Providers**:
   - Custom configuration source implementations can be added
   - ConfigurationProvider interface:
     ```python
     class ConfigurationProvider:
         def get_configuration(self, path: str) → Any:
             # Get configuration at specified path
             pass

         def set_configuration(self, path: str, value: Any) → bool:
             # Set configuration at specified path
             pass

         def validate_configuration(self, schema_name: str, config: Any) → ValidationResult:
             # Validate configuration against named schema
             pass
     ```

## Notes on Multi-Protocol Design

The Configuration System ↔ Agent Framework interface supports OpenMAS's multi-protocol design by:

- Providing configuration structures for multiple protocols (A2A, MCP, HTTP, MQTT, gRPC)
- Enabling protocol-specific agent configuration
- Supporting protocol capability configuration
- Allowing runtime protocol selection through configuration

## Notes on Reasoning Agnosticism

The Configuration System supports OpenMAS's reasoning agnostic architecture by:

- Providing configuration options for different reasoning approaches
- Maintaining separation between communication configuration and reasoning configuration
- Supporting hybrid reasoning configuration
- Enabling runtime reasoning engine selection

## Example: Unified Configuration Schema for Agent Framework

```yaml
# Extract from the unified configuration schema showing Agent Framework configuration

agent_framework:
  type: "object"
  description: "Configuration for the Agent Framework component"
  required: ["agent_types", "message_processing"]
  properties:
    agent_types:
      type: "array"
      description: "Available agent type definitions"
      items:
        type: "object"
        required: ["type", "implementation_class"]
        properties:
          type:
            type: "string"
            description: "Type identifier for this agent type"
          implementation_class:
            type: "string"
            description: "Fully qualified class name implementing this agent type"
          default_capabilities:
            type: "array"
            description: "Default capabilities for this agent type"
            items:
              type: "string"

    message_processing:
      type: "object"
      description: "Message processing configuration"
      required: ["max_queue_size"]
      properties:
        max_queue_size:
          type: "integer"
          description: "Maximum size of message queue"
          minimum: 1
        processing_threads:
          type: "integer"
          description: "Number of message processing threads"
          default: 4
          minimum: 1
        priority_levels:
          type: "integer"
          description: "Number of priority levels for messages"
          default: 3
          minimum: 1

    default_timeout_seconds:
      type: "integer"
      description: "Default timeout for operations in seconds"
      default: 30
      minimum: 1

    components:
      type: "object"
      description: "Configuration for Agent Framework subcomponents"
      properties:
        lifecycle_manager:
          type: "object"
          properties:
            enabled:
              type: "boolean"
              default: true
            implementation_class:
              type: "string"
              default: "DefaultLifecycleManager"

        message_router:
          type: "object"
          properties:
            enabled:
              type: "boolean"
              default: true
            implementation_class:
              type: "string"
              default: "DefaultMessageRouter"

        capability_registry:
          type: "object"
          properties:
            enabled:
              type: "boolean"
              default: true
            implementation_class:
              type: "string"
              default: "DefaultCapabilityRegistry"
```

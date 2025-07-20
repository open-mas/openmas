# Configuration System ↔ Protocol Layer

## Relationship Summary
- **Configuration System → Protocol Layer**: Configures
- **Protocol Layer → Configuration System**: Depends On

## Interface Definitions

### Configuration System → Protocol Layer

#### Methods/Functions
- `protocol_layer.initialize(config: ProtocolLayerConfig) → bool`
  - **Purpose**: Initialize the Protocol Layer with configuration parameters
  - **Parameters**: Configuration object containing all Protocol Layer settings
  - **Returns**: Boolean indicating successful initialization
  - **Example**:
    ```python
    success = protocol_layer.initialize(
        config=ProtocolLayerConfig(
            protocols=[
                {
                    "type": "a2a",
                    "enabled": true,
                    "adapter_class": "A2AProtocolAdapter",
                    "config": {
                        "version": "v1",
                        "server_mode": true,
                        "endpoint": "/a2a"
                    }
                },
                {
                    "type": "mcp",
                    "enabled": true,
                    "adapter_class": "MCPProtocolAdapter",
                    "config": {
                        "version": "v1",
                        "server_mode": true,
                        "endpoint": "/mcp"
                    }
                }
            ],
            default_protocol="a2a",
            connection_settings={
                "max_retries": 3,
                "timeout_seconds": 30,
                "keepalive_interval": 60
            }
        )
    )
    ```

- `protocol_layer.update_protocol_config(protocol_type: str, updates: Dict[str, Any]) → bool`
  - **Purpose**: Update configuration for a specific protocol
  - **Parameters**:
    - `protocol_type`: Protocol identifier (e.g., "a2a", "mcp")
    - `updates`: Configuration updates
  - **Returns**: Boolean indicating successful update
  - **Example**:
    ```python
    success = protocol_layer.update_protocol_config(
        protocol_type="a2a",
        updates={
            "server_mode": false,
            "client_endpoint": "https://external-a2a-service.com/a2a",
            "authentication": {
                "type": "oauth2",
                "client_id": "openmas_client"
            }
        }
    )
    ```

- `protocol_layer.configure_protocol_capability(protocol_type: str, capability: ProtocolCapability) → bool`
  - **Purpose**: Configure a protocol-specific capability
  - **Parameters**:
    - `protocol_type`: Protocol identifier
    - `capability`: Capability configuration
  - **Returns**: Boolean indicating successful configuration
  - **Example**:
    ```python
    success = protocol_layer.configure_protocol_capability(
        protocol_type="mcp",
        capability=ProtocolCapability(
            id="sequential-thinking",
            schema_url="https://mcp-spec.org/schemas/sequential-thinking.json",
            version="1.0",
            enabled=true
        )
    )
    ```

#### Events

```python
class ProtocolConfigurationUpdatedEvent:
    """
    Event emitted when protocol configuration has been updated.
    """
    event_name: str = "protocol_configuration_updated"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        protocol_type: str  # Type of the protocol (a2a, mcp, etc.)
        protocol_version: str  # Version of the protocol
        update_id: str  # Unique identifier for this update
        update_time: datetime  # When the update was performed
        updated_paths: List[str]  # Configuration paths that were updated
        update_source: str  # Source of the update (user, system, api, etc.)
        update_reason: Optional[str] = None  # Reason for the update
        requires_adapter_restart: bool = False  # Whether the protocol adapter needs to be restarted
        requires_endpoint_reconfiguration: bool = False  # Whether endpoints need to be reconfigured
        affects_active_connections: bool = False  # Whether active connections are affected
        update_details: Dict[str, Any] = {}  # Detailed information about the updates
        metadata: Dict[str, Any] = {}  # Additional metadata about the update
```

**Example Usage:**
```python
# Subscribe to protocol configuration updated events
@event_system.subscribe(ProtocolConfigurationUpdatedEvent.event_name)
def handle_protocol_configuration_update(event: ProtocolConfigurationUpdatedEvent):
    payload = event.payload
    protocol_type = payload.protocol_type
    protocol_version = payload.protocol_version
    updated_paths = payload.updated_paths

    logger.info(f"Protocol configuration update for {protocol_type} v{protocol_version} with {len(updated_paths)} path updates")

    # Get the protocol adapter
    adapter = protocol_layer.get_protocol_adapter(protocol_type)
    if not adapter:
        logger.error(f"No adapter found for protocol type: {protocol_type}")
        return

    # Apply the configuration updates to the adapter
    try:
        # Get the updated protocol configuration
        protocol_config = configuration_system.get_protocol_configuration(protocol_type)

        # Apply the configuration to the adapter
        result = adapter.update_configuration(protocol_config)

        logger.info(f"Applied configuration update to {protocol_type} adapter: Success={result.success}")

        # Handle server mode changes which may require endpoint reconfiguration
        if payload.requires_endpoint_reconfiguration:
            logger.info(f"Reconfiguring endpoints for {protocol_type} protocol")

            # Check if server mode changed
            if "server_mode" in [path.split('.')[-1] for path in updated_paths]:
                is_server_mode = protocol_config.get("server_mode", True)

                if is_server_mode:
                    logger.info(f"Switching {protocol_type} adapter to server mode")
                    result = adapter.switch_to_server_mode()
                else:
                    logger.info(f"Switching {protocol_type} adapter to client mode")
                    result = adapter.switch_to_client_mode()

                if not result.success:
                    logger.error(f"Failed to switch {protocol_type} adapter mode: {result.error_message}")

            # Update endpoints
            if any(path.endswith("endpoint") for path in updated_paths):
                logger.info(f"Updating endpoints for {protocol_type} protocol")
                result = adapter.reconfigure_endpoints()

                if not result.success:
                    logger.error(f"Failed to reconfigure endpoints for {protocol_type}: {result.error_message}")

        # Handle connection settings updates
        if any(path.startswith(f"protocol_layer.protocols[type={protocol_type}].config.connection_settings") for path in updated_paths):
            logger.info(f"Updating connection settings for {protocol_type} protocol")
            result = adapter.update_connection_settings()

            if not result.success:
                logger.error(f"Failed to update connection settings for {protocol_type}: {result.error_message}")

        # Handle adapter restart if needed
        if payload.requires_adapter_restart:
            logger.info(f"Protocol adapter {protocol_type} requires restart due to configuration changes")

            # Check if we're configured to auto-restart protocol adapters
            protocol_layer_config = configuration_system.get_configuration_value("protocol_layer")
            auto_restart = protocol_layer_config.get("auto_restart_on_config_change", False)

            if auto_restart:
                logger.info(f"Auto-restarting {protocol_type} protocol adapter")

                # Restart the protocol adapter
                restart_result = protocol_layer.restart_protocol_adapter(protocol_type)

                if restart_result.success:
                    logger.info(f"Successfully restarted {protocol_type} protocol adapter")

                    # Notify interested components
                    event_system.emit("protocol_adapter_restarted", {
                        "protocol_type": protocol_type,
                        "protocol_version": protocol_version,
                        "restart_reason": "configuration_update",
                        "restart_time": datetime.now().isoformat()
                    })
                else:
                    logger.error(f"Failed to restart {protocol_type} protocol adapter: {restart_result.error_message}")

                    # Report the error
                    error_reporting.report_error(
                        error_type="protocol_adapter_restart_failure",
                        component="protocol_layer",
                        details={
                            "protocol_type": protocol_type,
                            "protocol_version": protocol_version,
                            "error_message": restart_result.error_message,
                            "trigger": "configuration_update"
                        }
                    )
            else:
                logger.warning(f"Protocol adapter {protocol_type} needs manual restart to apply configuration changes")

                # Notify administrators
                notification_service.send_admin_notification(
                    severity="warning",
                    title=f"Protocol Adapter Requires Restart: {protocol_type}",
                    message=f"Protocol adapter {protocol_type} requires restart to apply configuration changes.",
                    details={
                        "protocol_type": protocol_type,
                        "protocol_version": protocol_version,
                        "update_id": payload.update_id,
                        "update_time": payload.update_time.isoformat(),
                        "update_source": payload.update_source
                    }
                )

        # Handle active connections
        if payload.affects_active_connections:
            logger.warning(f"Configuration update affects active {protocol_type} connections")

            # Get active connections count
            active_connections = adapter.get_active_connections_count()

            if active_connections > 0:
                logger.warning(f"Configuration update affects {active_connections} active {protocol_type} connections")

                # Notify clients if applicable
                if protocol_config.get("notify_clients_on_config_change", False):
                    logger.info(f"Notifying clients of configuration change for {protocol_type}")
                    adapter.notify_clients_of_configuration_change()

                # Refresh connections if needed
                if protocol_config.get("auto_refresh_connections_on_config_change", False):
                    logger.info(f"Auto-refreshing {active_connections} connections for {protocol_type}")
                    adapter.refresh_connections()

    except Exception as e:
        logger.error(f"Error applying configuration update to {protocol_type} adapter: {str(e)}")

        # Report the error
        error_reporting.report_error(
            error_type="protocol_configuration_update_failure",
            component="protocol_layer",
            details={
                "protocol_type": protocol_type,
                "protocol_version": protocol_version,
                "error_message": str(e),
                "updated_paths": updated_paths
            }
        )
```

```python
class ProtocolCapabilityConfiguredEvent:
    """
    Event emitted when a protocol capability has been configured.
    """
    event_name: str = "protocol_capability_configured"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        protocol_type: str  # Type of the protocol (a2a, mcp, etc.)
        protocol_version: str  # Version of the protocol
        capability_id: str  # Identifier of the capability
        capability_version: str  # Version of the capability
        configuration_id: str  # Unique identifier for this configuration
        configuration_time: datetime  # When the configuration was performed
        is_enabled: bool  # Whether the capability is enabled
        configuration_source: str  # Source of the configuration (user, system, default, etc.)
        schema_url: Optional[str] = None  # URL to the capability schema
        requires_adapter_restart: bool = False  # Whether the protocol adapter needs to be restarted
        capability_configuration: Dict[str, Any] = {}  # Capability-specific configuration
        capability_metadata: Dict[str, Any] = {}  # Additional metadata about the capability
```

**Example Usage:**
```python
# Subscribe to protocol capability configured events
@event_system.subscribe(ProtocolCapabilityConfiguredEvent.event_name)
def handle_protocol_capability_configuration(event: ProtocolCapabilityConfiguredEvent):
    payload = event.payload
    protocol_type = payload.protocol_type
    capability_id = payload.capability_id
    capability_version = payload.capability_version
    is_enabled = payload.is_enabled

    logger.info(f"Protocol capability {capability_id} v{capability_version} for {protocol_type} configured: Enabled={is_enabled}")

    # Get the protocol adapter
    adapter = protocol_layer.get_protocol_adapter(protocol_type)
    if not adapter:
        logger.error(f"No adapter found for protocol type: {protocol_type}")
        return

    # Apply the capability configuration to the adapter
    try:
        # Configure the capability in the adapter
        result = adapter.configure_capability(
            capability_id=capability_id,
            capability_version=capability_version,
            is_enabled=is_enabled,
            configuration=payload.capability_configuration
        )

        if result.success:
            logger.info(f"Successfully configured capability {capability_id} for {protocol_type}")

            # Update protocol capability registry
            capability_registry.update_protocol_capability(
                protocol_type=protocol_type,
                capability_id=capability_id,
                capability_version=capability_version,
                is_enabled=is_enabled,
                metadata=payload.capability_metadata
            )

            # If the capability is enabled, ensure the necessary handlers are registered
            if is_enabled:
                logger.info(f"Registering handlers for capability {capability_id}")

                handler_result = adapter.register_capability_handlers(capability_id)

                if not handler_result.success:
                    logger.error(f"Failed to register handlers for capability {capability_id}: {handler_result.error_message}")
            else:
                logger.info(f"Unregistering handlers for capability {capability_id}")

                adapter.unregister_capability_handlers(capability_id)

            # Handle adapter restart if needed
            if payload.requires_adapter_restart:
                logger.info(f"Protocol adapter {protocol_type} requires restart due to capability configuration changes")

                # Check if we're configured to auto-restart protocol adapters
                protocol_layer_config = configuration_system.get_configuration_value("protocol_layer")
                auto_restart = protocol_layer_config.get("auto_restart_on_capability_change", False)

                if auto_restart:
                    logger.info(f"Auto-restarting {protocol_type} protocol adapter")
                    protocol_layer.restart_protocol_adapter(protocol_type)
                else:
                    logger.warning(f"Protocol adapter {protocol_type} needs manual restart to apply capability changes")

                    # Notify administrators
                    notification_service.send_admin_notification(
                        severity="warning",
                        title=f"Protocol Adapter Requires Restart: {protocol_type}",
                        message=f"Protocol adapter {protocol_type} requires restart to apply capability configuration changes.",
                        details={
                            "protocol_type": protocol_type,
                            "capability_id": capability_id,
                            "capability_version": capability_version,
                            "configuration_time": payload.configuration_time.isoformat(),
                            "configuration_source": payload.configuration_source
                        }
                    )
        else:
            logger.error(f"Failed to configure capability {capability_id} for {protocol_type}: {result.error_message}")

    except Exception as e:
        logger.error(f"Error configuring capability {capability_id} for {protocol_type}: {str(e)}")

        # Report the error
        error_reporting.report_error(
            error_type="protocol_capability_configuration_failure",
            component="protocol_layer",
            details={
                "protocol_type": protocol_type,
                "capability_id": capability_id,
                "capability_version": capability_version,
                "error_message": str(e),
                "is_enabled": is_enabled
            }
        )
```

```python
class A2AProtocolConfigurationUpdatedEvent(ProtocolConfigurationUpdatedEvent):
    """
    Event emitted when A2A protocol configuration has been updated.
    Extends ProtocolConfigurationUpdatedEvent with A2A-specific fields.
    """
    event_name: str = "a2a_protocol_configuration_updated"  # Override event name

    class Payload(ProtocolConfigurationUpdatedEvent.Payload):
        agent_card_validation_enabled: Optional[bool] = None  # Whether agent card validation is enabled
        agent_card_schema_updated: bool = False  # Whether the agent card schema was updated
        oauth_configuration_updated: bool = False  # Whether OAuth configuration was updated
        rate_limit_updated: bool = False  # Whether rate limit configuration was updated
        streaming_configuration_updated: bool = False  # Whether streaming configuration was updated
        multipart_message_config_updated: bool = False  # Whether multipart message configuration was updated
        a2a_specific_details: Dict[str, Any] = {}  # A2A-specific configuration details
```

**Example Usage:**
```python
# Example: Emitting an A2A protocol configuration updated event

def update_a2a_protocol_configuration(updates: Dict[str, Any]) -> bool:
    # Validate the configuration updates
    validation_result = configuration_system.validate_partial_protocol_configuration("a2a", updates)

    if not validation_result.is_valid:
        logger.error(f"Invalid A2A protocol configuration updates: {validation_result.errors}")
        return False

    # Build the configuration path
    config_path = "protocol_layer.protocols[type=a2a].config"

    # Apply the updates to the configuration system
    update_result = configuration_system.update_configuration({
        config_path: updates
    })

    if update_result.success:
        # Determine what aspects of the configuration were updated
        agent_card_validation_updated = "agent_card_validation" in updates
        agent_card_schema_updated = "agent_card_schema" in updates
        oauth_configuration_updated = "oauth" in updates
        rate_limit_updated = "rate_limit" in updates
        streaming_configuration_updated = "streaming" in updates
        multipart_message_config_updated = "multipart_message" in updates

        # Determine if adapter restart is required
        requires_adapter_restart = any([
            "server_mode" in updates,
            "adapter_class" in updates,
            oauth_configuration_updated
        ])

        # Determine if endpoint reconfiguration is required
        requires_endpoint_reconfiguration = any([
            "server_mode" in updates,
            "endpoint" in updates,
            "client_endpoint" in updates
        ])

        # Determine if active connections are affected
        affects_active_connections = any([
            streaming_configuration_updated,
            multipart_message_config_updated,
            rate_limit_updated
        ])

        # Get the current protocol configuration to extract version
        a2a_config = configuration_system.get_protocol_configuration("a2a")
        protocol_version = a2a_config.get("version", "v1")

        # Emit A2A protocol configuration updated event
        update_id = f"a2a_config_{uuid.uuid4().hex[:8]}"
        update_time = datetime.now()

        event_system.emit(
            event_name="a2a_protocol_configuration_updated",
            payload=A2AProtocolConfigurationUpdatedEvent.Payload(
                protocol_type="a2a",
                protocol_version=protocol_version,
                update_id=update_id,
                update_time=update_time,
                updated_paths=[f"{config_path}.{key}" for key in updates.keys()],
                update_source="api",
                update_reason="A2A protocol configuration update",
                requires_adapter_restart=requires_adapter_restart,
                requires_endpoint_reconfiguration=requires_endpoint_reconfiguration,
                affects_active_connections=affects_active_connections,
                update_details=updates,
                agent_card_validation_enabled=updates.get("agent_card_validation"),
                agent_card_schema_updated=agent_card_schema_updated,
                oauth_configuration_updated=oauth_configuration_updated,
                rate_limit_updated=rate_limit_updated,
                streaming_configuration_updated=streaming_configuration_updated,
                multipart_message_config_updated=multipart_message_config_updated,
                a2a_specific_details={
                    key: value for key, value in updates.items()
                    if key in ["agent_card_validation", "agent_card_schema", "oauth",
                              "rate_limit", "streaming", "multipart_message"]
                }
            )
        )

        logger.info(f"A2A protocol configuration updated successfully")
        return True
    else:
        logger.error(f"Failed to update A2A protocol configuration: {update_result.error_message}")
        return False
```

```python
class MCPProtocolConfigurationUpdatedEvent(ProtocolConfigurationUpdatedEvent):
    """
    Event emitted when MCP protocol configuration has been updated.
    Extends ProtocolConfigurationUpdatedEvent with MCP-specific fields.
    """
    event_name: str = "mcp_protocol_configuration_updated"  # Override event name

    class Payload(ProtocolConfigurationUpdatedEvent.Payload):
        server_capabilities_updated: bool = False  # Whether server capabilities were updated
        server_capabilities_added: List[str] = []  # Capabilities that were added
        server_capabilities_removed: List[str] = []  # Capabilities that were removed
        tool_validation_updated: bool = False  # Whether tool validation configuration was updated
        resource_handling_updated: bool = False  # Whether resource handling configuration was updated
        streaming_configuration_updated: bool = False  # Whether streaming configuration was updated
        mcp_specific_details: Dict[str, Any] = {}  # MCP-specific configuration details
```

**Example Usage:**
```python
# Example: Emitting an MCP protocol configuration updated event

def update_mcp_protocol_configuration(updates: Dict[str, Any]) -> bool:
    # Validate the configuration updates
    validation_result = configuration_system.validate_partial_protocol_configuration("mcp", updates)

    if not validation_result.is_valid:
        logger.error(f"Invalid MCP protocol configuration updates: {validation_result.errors}")
        return False

    # Get the current MCP protocol configuration
    current_config = configuration_system.get_protocol_configuration("mcp")

    # Build the configuration path
    config_path = "protocol_layer.protocols[type=mcp].config"

    # Apply the updates to the configuration system
    update_result = configuration_system.update_configuration({
        config_path: updates
    })

    if update_result.success:
        # Determine what aspects of the configuration were updated
        server_capabilities_updated = "server_capabilities" in updates
        tool_validation_updated = "tool_validation" in updates
        resource_handling_updated = "resource_handling" in updates
        streaming_configuration_updated = "streaming" in updates

        # If server capabilities were updated, determine what was added/removed
        server_capabilities_added = []
        server_capabilities_removed = []

        if server_capabilities_updated:
            current_capabilities = set(current_config.get("server_capabilities", []))
            new_capabilities = set(updates.get("server_capabilities", []))

            server_capabilities_added = list(new_capabilities - current_capabilities)
            server_capabilities_removed = list(current_capabilities - new_capabilities)

        # Determine if adapter restart is required
        requires_adapter_restart = any([
            "server_mode" in updates,
            "adapter_class" in updates,
            "authentication" in updates
        ])

        # Determine if endpoint reconfiguration is required
        requires_endpoint_reconfiguration = any([
            "server_mode" in updates,
            "endpoint" in updates,
            "client_endpoint" in updates
        ])

        # Determine if active connections are affected
        affects_active_connections = any([
            streaming_configuration_updated,
            tool_validation_updated,
            resource_handling_updated
        ])

        # Get protocol version
        protocol_version = current_config.get("version", "v1")

        # Emit MCP protocol configuration updated event
        update_id = f"mcp_config_{uuid.uuid4().hex[:8]}"
        update_time = datetime.now()

        event_system.emit(
            event_name="mcp_protocol_configuration_updated",
            payload=MCPProtocolConfigurationUpdatedEvent.Payload(
                protocol_type="mcp",
                protocol_version=protocol_version,
                update_id=update_id,
                update_time=update_time,
                updated_paths=[f"{config_path}.{key}" for key in updates.keys()],
                update_source="api",
                update_reason="MCP protocol configuration update",
                requires_adapter_restart=requires_adapter_restart,
                requires_endpoint_reconfiguration=requires_endpoint_reconfiguration,
                affects_active_connections=affects_active_connections,
                update_details=updates,
                server_capabilities_updated=server_capabilities_updated,
                server_capabilities_added=server_capabilities_added,
                server_capabilities_removed=server_capabilities_removed,
                tool_validation_updated=tool_validation_updated,
                resource_handling_updated=resource_handling_updated,
                streaming_configuration_updated=streaming_configuration_updated,
                mcp_specific_details={
                    key: value for key, value in updates.items()
                    if key in ["server_capabilities", "tool_validation",
                              "resource_handling", "streaming"]
                }
            )
        )

        logger.info(f"MCP protocol configuration updated successfully")
        return True
    else:
        logger.error(f"Failed to update MCP protocol configuration: {update_result.error_message}")
        return False
```

### Protocol Layer → Configuration System

#### Methods/Functions
- `configuration_system.get_protocol_configuration(protocol_type: str) → ProtocolConfig`
  - **Purpose**: Retrieve configuration for a specific protocol
  - **Parameters**: Protocol identifier
  - **Returns**: Protocol configuration object
  - **Example**:
    ```python
    config = configuration_system.get_protocol_configuration(
        protocol_type="a2a"
    )
    ```

- `configuration_system.validate_protocol_configuration(protocol_type: str, config: ProtocolConfig) → ValidationResult`
  - **Purpose**: Validate protocol configuration against schema
  - **Parameters**:
    - `protocol_type`: Protocol identifier
    - `config`: Protocol configuration
  - **Returns**: Validation result with any errors
  - **Example**:
    ```python
    result = configuration_system.validate_protocol_configuration(
        protocol_type="mcp",
        config=mcp_config
    )
    ```

- `configuration_system.register_protocol_schema(protocol_type: str, schema: ConfigSchema) → bool`
  - **Purpose**: Register a configuration schema for a protocol
  - **Parameters**:
    - `protocol_type`: Protocol identifier
    - `schema`: Configuration schema
  - **Returns**: Boolean indicating successful registration
  - **Example**:
    ```python
    success = configuration_system.register_protocol_schema(
        protocol_type="mqtt",
        schema=mqtt_protocol_schema
    )
    ```

#### Events
- `protocol_configuration_requested`
  - **Purpose**: Notifies when protocol configuration is requested
  - **Payload**: Protocol type, requester ID
  - **Subscribers**: Configuration System audit log

- `protocol_schema_updated`
  - **Purpose**: Notifies when a protocol schema is updated
  - **Payload**: Protocol type, schema changes
  - **Subscribers**: Configuration System validation components

## Data Flows

### Protocol Layer Initialization Flow
1. **Configuration System → Protocol Layer**: Configuration System provides protocol configurations
2. **Protocol Layer Processing**: Protocol Layer initializes protocol adapters based on configuration
3. **Protocol Layer → Configuration System**: Protocol Layer registers protocol schemas
4. **Protocol Layer → Observers**: Protocol Layer notifies observers of successful initialization

### Protocol Configuration Update Flow
1. **Configuration System → Protocol Layer**: Configuration System provides updated protocol configuration
2. **Protocol Layer Processing**: Protocol Layer validates and applies configuration updates
3. **Protocol Layer → Protocol Handlers**: Protocol Layer notifies handlers of updated configuration
4. **Protocol Layer → Configuration System**: Protocol Layer confirms successful update

## Configuration Dependencies

The following configuration parameters affect this interaction:

```yaml
protocol_layer:
  protocols:
    - type: "a2a"
      enabled: true
      adapter_class: "A2AProtocolAdapter"
      config:
        version: "v1"
        server_mode: true
        endpoint: "/a2a"
        rate_limit:
          max_requests_per_minute: 60
        agent_card_validation: true

    - type: "mcp"
      enabled: true
      adapter_class: "MCPProtocolAdapter"
      config:
        version: "v1"
        server_mode: true
        endpoint: "/mcp"
        rate_limit:
          max_requests_per_minute: 60
        server_capabilities:
          - "sequential-thinking"
          - "agentic-actions"

  default_protocol: "a2a"

  connection_settings:
    max_retries: 3
    timeout_seconds: 30
    keepalive_interval: 60

  communication_patterns:
    enabled: true
    pattern_validation: true

security:
  protocol_authentication:
    a2a:
      type: "oauth2"
      required: true
      provider: "default_oauth_provider"

    mcp:
      type: "api_key"
      required: true
      header_name: "X-MCP-API-Key"
```

## Error Handling

1. **Protocol Initialization Failures**:
   - Graceful failure handling for individual protocols
   - System can continue with successfully initialized protocols
   - Detailed error logging for initialization failures

2. **Invalid Protocol Configuration**:
   - Configuration validation before application
   - Detailed validation error reporting
   - Automatic use of defaults for invalid configuration items

3. **Protocol Communication Failures**:
   - Configurable retry strategies
   - Circuit breaker pattern implementation
   - Fallback to alternative protocols when available

## Extension Points

1. **Protocol Adapters**:
   - New protocol adapters can be registered through configuration
   - ProtocolAdapter interface:
     ```python
     class ProtocolAdapter:
         def initialize(self, config: Dict[str, Any]) → bool:
             # Initialize adapter with configuration
             pass

         def translate_incoming(self, external_message: Any) → Message:
             # Translate external protocol message to internal format
             pass

         def translate_outgoing(self, internal_message: Message) → Any:
             # Translate internal message to external protocol format
             pass
     ```

2. **Protocol Capabilities**:
   - Protocol-specific capabilities can be defined in configuration
   - Example MCP configuration:
     ```yaml
     protocols:
       - type: "mcp"
         enabled: true
         adapter_class: "MCPProtocolAdapter"
         config:
           version: "v1"
           server_capabilities:
             - id: "sequential-thinking"
               implementation_class: "SequentialThinkingCapability"
               enabled: true
             - id: "agentic-actions"
               implementation_class: "AgenticActionsCapability"
               enabled: true
     ```

## Notes on A2A and MCP Protocol Support

The Configuration System ↔ Protocol Layer interface provides specific support for both Google's A2A protocol and the Model Context Protocol (MCP):

### A2A Protocol Configuration

```yaml
protocols:
  - type: "a2a"
    enabled: true
    adapter_class: "A2AProtocolAdapter"
    config:
      version: "v1"
      server_mode: true
      endpoint: "/a2a"
      agent_card:
        api_version: "v1"
        agent_id: "openmas_agent"
        display_name: "OpenMAS Agent"
        description: "Multi-protocol agent using OpenMAS framework"
        tools:
          - name: "search_web"
            description: "Search the web for information"
            input_schema:
              type: "object"
              properties:
                query:
                  type: "string"
                  description: "Search query"
          - name: "calculate"
            description: "Perform a calculation"
            input_schema:
              type: "object"
              properties:
                expression:
                  type: "string"
                  description: "Mathematical expression to evaluate"
      authentication:
        type: "oauth2"
        client_id: "openmas_client"
        client_secret: "${A2A_CLIENT_SECRET}"
        token_endpoint: "https://auth.example.com/token"
```

### MCP Protocol Configuration

```yaml
protocols:
  - type: "mcp"
    enabled: true
    adapter_class: "MCPProtocolAdapter"
    config:
      version: "v1"
      server_mode: true
      endpoint: "/mcp"
      servers:
        - name: "sequential-thinking"
          implementation_class: "SequentialThinkingServer"
          description: "A server for sequential thinking capability"
        - name: "agentic-actions"
          implementation_class: "AgenticActionsServer"
          description: "A server for agentic actions capability"
      authentication:
        type: "api_key"
        header_name: "X-MCP-API-Key"
        key_validation_endpoint: "https://auth.example.com/validate-key"
```

## Notes on Reasoning Agnosticism

The Configuration System ↔ Protocol Layer interface supports OpenMAS's reasoning agnostic architecture by:

- Keeping protocol configuration separate from reasoning configuration
- Allowing protocol adapters to work with any reasoning approach
- Ensuring protocol message translation preserves reasoning-specific information
- Supporting communication patterns that can be used with different reasoning paradigms

This separation maintains the "body-brain" division central to OpenMAS's architecture, where protocols form part of the agent "body" (communication infrastructure) that can be paired with different "brains" (reasoning approaches).

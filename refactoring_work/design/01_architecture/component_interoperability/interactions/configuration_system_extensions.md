# Configuration System ↔ Extension System

## Relationship Summary
- **Configuration System → Extension System**: Configures
- **Extension System → Configuration System**: Depends On

## Interface Definitions

### Configuration System → Extension System

#### Methods/Functions
- `extension_system.initialize(config: ExtensionSystemConfig) → bool`
  - **Purpose**: Initialize the Extension System with configuration parameters
  - **Parameters**: Configuration object containing all Extension System settings
  - **Returns**: Boolean indicating successful initialization
  - **Example**:
    ```python
    success = extension_system.initialize(
        config=ExtensionSystemConfig(
            extension_directories=["extensions/", "custom_extensions/"],
            auto_discovery=True,
            extension_types=[
                {
                    "type": "capability",
                    "interface": "CapabilityExtension",
                    "loader": "CapabilityLoader"
                },
                {
                    "type": "protocol",
                    "interface": "ProtocolExtension",
                    "loader": "ProtocolLoader"
                }
            ],
            extension_validation=True,
            isolation_level="process"
        )
    )
    ```

- `extension_system.configure_extension(extension_id: str, config: Dict[str, Any]) → bool`
  - **Purpose**: Configure a specific extension with custom parameters
  - **Parameters**:
    - `extension_id`: Extension identifier
    - `config`: Extension-specific configuration
  - **Returns**: Boolean indicating successful configuration
  - **Example**:
    ```python
    success = extension_system.configure_extension(
        extension_id="custom_reasoning",
        config={
            "enabled": True,
            "model": "gpt-4",
            "max_tokens": 2000,
            "temperature": 0.7,
            "api_parameters": {
                "timeout_seconds": 30,
                "retry_count": 3
            }
        }
    )
    ```

- `extension_system.update_extension_registry(registry_config: ExtensionRegistryConfig) → bool`
  - **Purpose**: Update the extension registry configuration
  - **Parameters**: Registry configuration object
  - **Returns**: Boolean indicating successful update
  - **Example**:
    ```python
    success = extension_system.update_extension_registry(
        registry_config=ExtensionRegistryConfig(
            remote_registries=[
                {
                    "url": "https://extensions.openmas.org/registry",
                    "auth_type": "api_key",
                    "api_key_env": "OPENMAS_REGISTRY_KEY"
                }
            ],
            local_registry_path="local_extensions/registry.json",
            auto_update=True,
            update_interval_hours=24
        )
    )
    ```

#### Events

```python
class ExtensionConfigurationUpdatedEvent:
    """
    Event emitted when extension configuration has been updated.
    """
    event_name: str = "extension_configuration_updated"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        extension_id: str  # Identifier of the extension
        extension_type: str  # Type of extension (capability, protocol, reasoning, etc.)
        update_id: str  # Unique identifier for this update
        update_time: datetime  # When the update was performed
        updated_paths: List[str]  # Configuration paths that were updated
        update_source: Optional[str] = None  # Source of the update (user, system, etc.)
        update_reason: Optional[str] = None  # Reason for the update
        requires_extension_restart: bool = False  # Whether the extension needs to be restarted
        update_details: Dict[str, Any] = {}  # Detailed information about the updates
        metadata: Dict[str, Any] = {}  # Additional metadata about the update
```

**Example Usage:**
```python
# Subscribe to extension configuration updated events
@event_system.subscribe(ExtensionConfigurationUpdatedEvent.event_name)
def handle_extension_configuration_update(event: ExtensionConfigurationUpdatedEvent):
    payload = event.payload
    extension_id = payload.extension_id
    extension_type = payload.extension_type
    updated_paths = payload.updated_paths

    logger.info(f"Extension configuration update for {extension_id} (type: {extension_type}) with {len(updated_paths)} path updates")

    # Get the extension loader for this extension type
    loader = extension_system.get_loader_for_type(extension_type)
    if not loader:
        logger.error(f"No loader found for extension type: {extension_type}")
        return

    # Check if this is an extension managed by this loader
    if loader.has_extension(extension_id):
        logger.info(f"Handling configuration update for extension {extension_id}")

        # Get the updated configuration
        extension_config = configuration_system.get_extension_configuration(extension_id)

        # Apply the configuration to the extension
        try:
            result = loader.update_extension_configuration(extension_id, extension_config)

            logger.info(f"Applied configuration update to extension {extension_id}: Success={result.success}")

            # Handle extension restart if needed
            if result.success and payload.requires_extension_restart:
                logger.info(f"Extension {extension_id} requires restart due to configuration changes")

                # Check if we're configured to auto-restart extensions
                extension_system_config = configuration_system.get_configuration_value("extension_system")
                auto_restart = extension_system_config.get("auto_restart_on_config_change", False)

                if auto_restart:
                    logger.info(f"Auto-restarting extension {extension_id}")

                    # Restart the extension
                    restart_result = loader.restart_extension(extension_id)

                    if restart_result.success:
                        logger.info(f"Successfully restarted extension {extension_id}")

                        # Notify interested components
                        event_system.emit("extension_restarted", {
                            "extension_id": extension_id,
                            "extension_type": extension_type,
                            "restart_reason": "configuration_update",
                            "restart_time": datetime.now().isoformat()
                        })
                    else:
                        logger.error(f"Failed to restart extension {extension_id}: {restart_result.error_message}")

                        # Report the error
                        error_reporting.report_error(
                            error_type="extension_restart_failure",
                            component="extension_system",
                            details={
                                "extension_id": extension_id,
                                "extension_type": extension_type,
                                "error_message": restart_result.error_message,
                                "trigger": "configuration_update"
                            }
                        )
                else:
                    logger.warning(f"Extension {extension_id} needs manual restart to apply configuration changes")

                    # Notify administrators
                    notification_service.send_admin_notification(
                        severity="warning",
                        title=f"Extension Requires Restart: {extension_id}",
                        message=f"Extension {extension_id} requires restart to apply configuration changes.",
                        details={
                            "extension_id": extension_id,
                            "extension_type": extension_type,
                            "update_id": payload.update_id,
                            "update_time": payload.update_time.isoformat(),
                            "update_source": payload.update_source
                        }
                    )
        except Exception as e:
            logger.error(f"Error applying configuration update to extension {extension_id}: {str(e)}")

            # Report the error
            error_reporting.report_error(
                error_type="extension_configuration_failure",
                component="extension_system",
                details={
                    "extension_id": extension_id,
                    "extension_type": extension_type,
                    "error_message": str(e),
                    "updated_paths": updated_paths
                }
            )
```

```python
class ExtensionRegistryUpdatedEvent:
    """
    Event emitted when the extension registry has been updated.
    """
    event_name: str = "extension_registry_updated"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        update_id: str  # Unique identifier for this update
        update_time: datetime  # When the update was performed
        update_source: str  # Source of the update ("auto", "manual", "remote")
        update_type: str  # Type of update ("full_sync", "incremental", "metadata_only")
        affected_registries: List[str] = []  # Registries that were affected
        added_extensions: List[Dict[str, Any]] = []  # Extensions that were added
        updated_extensions: List[Dict[str, Any]] = []  # Extensions that were updated
        removed_extensions: List[Dict[str, Any]] = []  # Extensions that were removed
        registry_metadata: Dict[str, Any] = {}  # Metadata about the registry update
```

**Example Usage:**
```python
# Subscribe to extension registry updated events
@event_system.subscribe(ExtensionRegistryUpdatedEvent.event_name)
def handle_extension_registry_update(event: ExtensionRegistryUpdatedEvent):
    payload = event.payload
    update_type = payload.update_type
    added_count = len(payload.added_extensions)
    updated_count = len(payload.updated_extensions)
    removed_count = len(payload.removed_extensions)

    logger.info(f"Extension registry update ({update_type}): {added_count} added, {updated_count} updated, {removed_count} removed")

    # Update the discovery system with new registry information
    extension_system.discovery_service.process_registry_update(
        added_extensions=payload.added_extensions,
        updated_extensions=payload.updated_extensions,
        removed_extensions=payload.removed_extensions
    )

    # If any extensions were added, check if they should be auto-installed
    if payload.added_extensions:
        extension_system_config = configuration_system.get_configuration_value("extension_system")
        auto_install = extension_system_config.get("auto_install_new_extensions", False)

        if auto_install:
            logger.info(f"Auto-installing {added_count} new extensions")

            # Queue extensions for installation
            for extension_info in payload.added_extensions:
                extension_id = extension_info.get("id")
                extension_version = extension_info.get("version")

                if extension_id and extension_version:
                    logger.info(f"Queueing installation of extension {extension_id} version {extension_version}")

                    # Queue the installation
                    extension_system.installation_queue.add({
                        "extension_id": extension_id,
                        "version": extension_version,
                        "priority": "normal",
                        "auto_install": True,
                        "install_dependencies": True
                    })

    # If any extensions were updated, check if current installations should be upgraded
    if payload.updated_extensions:
        extension_system_config = configuration_system.get_configuration_value("extension_system")
        auto_upgrade = extension_system_config.get("auto_upgrade_extensions", False)

        if auto_upgrade:
            logger.info(f"Checking {updated_count} extensions for possible upgrade")

            # Get currently installed extensions
            installed_extensions = extension_system.get_installed_extensions()

            # Check each updated extension
            for extension_info in payload.updated_extensions:
                extension_id = extension_info.get("id")
                extension_version = extension_info.get("version")

                # If extension is installed, check if upgrade is needed
                if extension_id in installed_extensions:
                    installed_version = installed_extensions[extension_id].get("version")

                    if installed_version and extension_version and installed_version != extension_version:
                        logger.info(f"Queueing upgrade of extension {extension_id} from version {installed_version} to {extension_version}")

                        # Queue the upgrade
                        extension_system.installation_queue.add({
                            "extension_id": extension_id,
                            "version": extension_version,
                            "priority": "normal",
                            "auto_install": True,
                            "install_dependencies": True,
                            "upgrade": True
                        })

    # Process installation queue
    extension_system.process_installation_queue()
```

```python
class ExtensionInstalledEvent:
    """
    Event emitted when an extension has been installed.
    """
    event_name: str = "extension_installed"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        extension_id: str  # Identifier of the installed extension
        extension_type: str  # Type of extension (capability, protocol, reasoning, etc.)
        extension_version: str  # Version of the installed extension
        installation_id: str  # Unique identifier for this installation
        installation_time: datetime  # When the installation was performed
        installer: str  # Component or user that performed the installation
        is_upgrade: bool = False  # Whether this was an upgrade installation
        previous_version: Optional[str] = None  # Previous version if this was an upgrade
        auto_installed: bool = False  # Whether the extension was auto-installed
        installed_dependencies: List[Dict[str, Any]] = []  # Dependencies that were installed
        installation_details: Dict[str, Any] = {}  # Detailed information about the installation
```

**Example Usage:**
```python
# Example: Emitting an extension installed event

def install_extension(extension_id: str, version: str, installer: str = "user", auto_install: bool = False) -> bool:
    # Check if extension exists in registry
    extension_info = extension_system.registry.get_extension_info(extension_id, version)

    if not extension_info:
        logger.error(f"Extension {extension_id} version {version} not found in registry")
        return False

    # Extract extension type
    extension_type = extension_info.get("type")
    if not extension_type:
        logger.error(f"Extension {extension_id} is missing type information")
        return False

    # Get the extension loader for this extension type
    loader = extension_system.get_loader_for_type(extension_type)
    if not loader:
        logger.error(f"No loader found for extension type: {extension_type}")
        return False

    # Check if extension is already installed
    is_upgrade = False
    previous_version = None
    if loader.has_extension(extension_id):
        existing_extension = loader.get_extension(extension_id)
        if existing_extension:
            is_upgrade = True
            previous_version = existing_extension.get("version")

            logger.info(f"Upgrading extension {extension_id} from version {previous_version} to {version}")

    # Install or upgrade the extension
    installation_id = f"install_{uuid.uuid4().hex[:8]}"
    installation_time = datetime.now()

    try:
        # Resolve and install dependencies first
        dependencies = extension_info.get("dependencies", [])
        installed_dependencies = []

        for dependency in dependencies:
            dependency_id = dependency.get("id")
            dependency_version = dependency.get("version")

            if dependency_id and dependency_version:
                # Check if dependency is already installed
                if not extension_system.is_extension_installed(dependency_id, dependency_version):
                    logger.info(f"Installing dependency {dependency_id} version {dependency_version}")

                    # Install the dependency
                    dependency_result = install_extension(
                        extension_id=dependency_id,
                        version=dependency_version,
                        installer=f"dependency_of_{extension_id}",
                        auto_install=True
                    )

                    if dependency_result:
                        installed_dependencies.append({
                            "id": dependency_id,
                            "version": dependency_version
                        })
                    else:
                        logger.error(f"Failed to install dependency {dependency_id}, aborting installation of {extension_id}")
                        return False

        # Install the extension itself
        installation_result = loader.install_extension(extension_id, extension_info)

        if installation_result.success:
            logger.info(f"Successfully installed extension {extension_id} version {version}")

            # Configure the extension with defaults
            if "default_configuration" in extension_info:
                logger.info(f"Applying default configuration to extension {extension_id}")

                default_config = extension_info["default_configuration"]
                config_result = extension_system.configure_extension(extension_id, default_config)

                if not config_result:
                    logger.warning(f"Failed to apply default configuration to extension {extension_id}")

            # Emit extension installed event
            event_system.emit(
                event_name="extension_installed",
                payload=ExtensionInstalledEvent.Payload(
                    extension_id=extension_id,
                    extension_type=extension_type,
                    extension_version=version,
                    installation_id=installation_id,
                    installation_time=installation_time,
                    installer=installer,
                    is_upgrade=is_upgrade,
                    previous_version=previous_version,
                    auto_installed=auto_install,
                    installed_dependencies=installed_dependencies,
                    installation_details=installation_result.details
                )
            )

            # If this is a protocol extension, update protocol registry
            if extension_type == "protocol":
                protocol_registry.register_protocol_extension(extension_id, extension_info)

            # If this is a reasoning extension, update reasoning registry
            elif extension_type == "reasoning":
                reasoning_registry.register_reasoning_extension(extension_id, extension_info)

            # If this is a capability extension, update capability registry
            elif extension_type == "capability":
                capability_registry.register_capability_extension(extension_id, extension_info)

            return True
        else:
            logger.error(f"Failed to install extension {extension_id}: {installation_result.error_message}")
            return False

    except Exception as e:
        logger.error(f"Error installing extension {extension_id}: {str(e)}")

        # Report the error
        error_reporting.report_error(
            error_type="extension_installation_failure",
            component="extension_system",
            details={
                "extension_id": extension_id,
                "extension_type": extension_type,
                "extension_version": version,
                "error_message": str(e),
                "is_upgrade": is_upgrade
            }
        )

        return False
```

```python
class ExtensionSchemaRegisteredEvent:
    """
    Event emitted when an extension schema is registered with the configuration system.
    """
    event_name: str = "extension_schema_registered"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        extension_id: str  # Identifier of the extension
        extension_type: str  # Type of extension (capability, protocol, reasoning, etc.)
        schema_id: str  # Unique identifier for the schema
        schema_version: str  # Version of the schema
        registration_time: datetime  # When the schema was registered
        schema_properties_count: int = 0  # Number of properties in the schema
        required_properties: List[str] = []  # Required properties in the schema
        is_update: bool = False  # Whether this is an update to an existing schema
        metadata: Dict[str, Any] = {}  # Additional metadata about the schema
```

**Example Usage:**
```python
# Subscribe to extension schema registered events
@event_system.subscribe(ExtensionSchemaRegisteredEvent.event_name)
def handle_extension_schema_registration(event: ExtensionSchemaRegisteredEvent):
    payload = event.payload
    extension_id = payload.extension_id
    extension_type = payload.extension_type

    logger.info(f"Extension schema registered for {extension_id} (type: {extension_type})")

    # If this is a protocol extension schema, update protocol adapters
    if extension_type == "protocol":
        logger.info(f"Updating protocol adapters for extension {extension_id}")

        # Get the protocol extension loader
        protocol_loader = extension_system.get_loader_for_type("protocol")

        if protocol_loader and protocol_loader.has_extension(extension_id):
            # Retrieve the protocol extension
            protocol_extension = protocol_loader.get_extension(extension_id)

            # Update protocol registry with schema information
            protocol_registry.update_protocol_schema(
                protocol_id=extension_id,
                schema_id=payload.schema_id,
                schema_version=payload.schema_version,
                required_properties=payload.required_properties,
                metadata=payload.metadata
            )

            logger.info(f"Updated protocol registry for {extension_id}")

    # If this is a reasoning extension schema, update reasoning adapters
    elif extension_type == "reasoning":
        logger.info(f"Updating reasoning registry for extension {extension_id}")

        # Update reasoning registry with schema information
        reasoning_registry.update_reasoning_schema(
            reasoning_id=extension_id,
            schema_id=payload.schema_id,
            schema_version=payload.schema_version,
            required_properties=payload.required_properties,
            metadata=payload.metadata
        )

        logger.info(f"Updated reasoning registry for {extension_id}")

    # If this is a capability extension schema, update capability registry
    elif extension_type == "capability":
        logger.info(f"Updating capability registry for extension {extension_id}")

        # Update capability registry with schema information
        capability_registry.update_capability_schema(
            capability_id=extension_id,
            schema_id=payload.schema_id,
            schema_version=payload.schema_version,
            required_properties=payload.required_properties,
            metadata=payload.metadata
        )

        logger.info(f"Updated capability registry for {extension_id}")

    # Notify configuration validator about new schema
    configuration_validator.register_schema(payload.schema_id, extension_id)
```

### Extension System → Configuration System

#### Methods/Functions
- `configuration_system.get_extension_configuration(extension_id: str) → Dict[str, Any]`
  - **Purpose**: Retrieve configuration for a specific extension
  - **Parameters**: Extension identifier
  - **Returns**: Extension configuration object
  - **Example**:
    ```python
    config = configuration_system.get_extension_configuration(
        extension_id="custom_reasoning"
    )
    ```

- `configuration_system.validate_extension_configuration(extension_id: str, config: Dict[str, Any]) → ValidationResult`
  - **Purpose**: Validate extension configuration against schema
  - **Parameters**:
    - `extension_id`: Extension identifier
    - `config`: Extension configuration
  - **Returns**: Validation result with any errors
  - **Example**:
    ```python
    result = configuration_system.validate_extension_configuration(
        extension_id="custom_reasoning",
        config=extension_config
    )
    ```

- `configuration_system.register_extension_schema(extension_id: str, schema: ConfigSchema) → bool`
  - **Purpose**: Register a configuration schema for an extension
  - **Parameters**:
    - `extension_id`: Extension identifier
    - `schema`: Configuration schema
  - **Returns**: Boolean indicating successful registration
  - **Example**:
    ```python
    success = configuration_system.register_extension_schema(
        extension_id="custom_reasoning",
        schema=reasoning_extension_schema
    )
    ```

#### Events
- `extension_configuration_requested`
  - **Purpose**: Notifies when extension configuration is requested
  - **Payload**: Extension ID, requester ID
  - **Subscribers**: Configuration System audit log

- `extension_schema_registered`
  - **Purpose**: Notifies when an extension schema is registered
  - **Payload**: Extension ID, schema details
  - **Subscribers**: Configuration System validation components

## Data Flows

### Extension System Initialization Flow
1. **Configuration System → Extension System**: Configuration System provides extension system configuration
2. **Extension System Processing**: Extension System initializes based on configuration
3. **Extension System → Configuration System**: Extension System registers schemas for discovered extensions
4. **Extension System → Observers**: Extension System notifies observers of discovered extensions

### Extension Configuration Flow
1. **Extension System → Configuration System**: Extension System requests extension configuration
2. **Configuration System Processing**: Configuration System validates and provides configuration
3. **Configuration System → Extension System**: Configuration System returns valid configuration
4. **Extension System Processing**: Extension System configures extension with parameters

## Configuration Dependencies

The following configuration parameters affect this interaction:

```yaml
extension_system:
  extension_directories:
    - "extensions/"
    - "custom_extensions/"

  auto_discovery: true

  extension_types:
    - type: "capability"
      interface: "CapabilityExtension"
      loader: "CapabilityLoader"

    - type: "protocol"
      interface: "ProtocolExtension"
      loader: "ProtocolLoader"

    - type: "reasoning"
      interface: "ReasoningExtension"
      loader: "ReasoningLoader"

  extension_validation: true
  isolation_level: "process"  # process, thread, none

  registry:
    remote_registries:
      - url: "https://extensions.openmas.org/registry"
        auth_type: "api_key"
        api_key_env: "OPENMAS_REGISTRY_KEY"

    local_registry_path: "local_extensions/registry.json"
    auto_update: true
    update_interval_hours: 24

extensions:
  custom_reasoning:
    enabled: true
    type: "reasoning"
    implementation_class: "CustomReasoningExtension"
    model: "gpt-4"
    max_tokens: 2000
    temperature: 0.7
    api_parameters:
      timeout_seconds: 30
      retry_count: 3

  web_search:
    enabled: true
    type: "capability"
    implementation_class: "WebSearchCapability"
    search_providers:
      - name: "google"
        enabled: true
        api_key_env: "GOOGLE_API_KEY"
      - name: "bing"
        enabled: false
```

## Error Handling

1. **Extension Loading Failures**:
   - Graceful failure handling for individual extensions
   - System can continue with successfully loaded extensions
   - Detailed error logging for loading failures
   - Configurable policy for extension failures (fail-fast vs. continue)

2. **Invalid Extension Configuration**:
   - Configuration validation before extension initialization
   - Detailed validation error reporting with schema references
   - Default values for missing optional configuration

3. **Extension Isolation Failures**:
   - Containment of extension failures to prevent system-wide impacts
   - Automatic restart of failed extensions based on policy
   - Resource limits for extensions to prevent resource exhaustion

## Extension Points

1. **Extension Loaders**:
   - Custom extension loading mechanisms can be implemented
   - ExtensionLoader interface:
     ```python
     class ExtensionLoader:
         def load_extension(self, extension_id: str, config: Dict[str, Any]) → ExtensionInstance:
             # Load extension with configuration
             pass

         def unload_extension(self, extension_id: str) → bool:
             # Unload extension safely
             pass

         def reload_extension(self, extension_id: str, config: Dict[str, Any]) → ExtensionInstance:
             # Reload extension with new configuration
             pass
     ```

2. **Extension Discovery Mechanisms**:
   - Custom discovery methods can be added
   - Example filesystem discovery configuration:
     ```yaml
     extension_system:
       discovery_mechanisms:
         filesystem:
           enabled: true
           paths: ["extensions/", "custom_extensions/"]
           patterns: ["*.extension.py", "extension.json"]

         registry:
           enabled: true
           registry_urls: ["https://extensions.openmas.org/registry"]
     ```

## Notes on Reasoning Agnosticism

The Configuration System ↔ Extension System interface supports OpenMAS's reasoning agnostic architecture by:

- Providing extension mechanisms for different reasoning approaches
- Maintaining separation between reasoning extensions and protocol extensions
- Supporting dynamic loading of reasoning implementations
- Allowing multiple reasoning approaches to coexist in the system

This supports the "body-brain" separation central to OpenMAS, where reasoning approaches (the "brain") can be implemented as extensions while maintaining clear separation from communication components (the "body").

## Example: Reasoning Extension Configuration

```yaml
extensions:
  bdi_reasoning:
    enabled: true
    type: "reasoning"
    implementation_class: "BDIReasoningExtension"
    config:
      belief_database:
        type: "in_memory"
        constraints_file: "bdi/constraints.json"

      plan_library:
        path: "bdi/plans/"
        auto_reload: true

      intention_selection:
        strategy: "priority_based"
        max_concurrent_intentions: 5

  llm_reasoning:
    enabled: true
    type: "reasoning"
    implementation_class: "LLMReasoningExtension"
    config:
      model: "gpt-4"
      system_prompt_file: "llm/system_prompt.txt"
      reasoning_templates:
        - name: "sequential_thinking"
          file: "llm/templates/sequential_thinking.prompt"
        - name: "chain_of_thought"
          file: "llm/templates/chain_of_thought.prompt"

      model_parameters:
        temperature: 0.7
        max_tokens: 2000
        top_p: 1.0

      capability_mapping:
        - capability: "reasoning"
          template: "sequential_thinking"
        - capability: "planning"
          template: "chain_of_thought"
```

This configuration demonstrates how different reasoning approaches can be configured as extensions, allowing OpenMAS to support both classical AI (BDI) and neural approaches (LLM) concurrently.

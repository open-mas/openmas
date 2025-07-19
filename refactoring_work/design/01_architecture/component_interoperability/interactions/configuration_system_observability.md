# Configuration System ↔ Observability System

## Relationship Summary
- **Configuration System → Observability System**: Configures
- **Observability System → Configuration System**: Depends On

## Interface Definitions

### Configuration System → Observability System

#### Methods/Functions
- `observability_system.initialize(config: ObservabilityConfig) → bool`
  - **Purpose**: Initialize the Observability System with configuration parameters
  - **Parameters**: Configuration object containing all Observability System settings
  - **Returns**: Boolean indicating successful initialization
  - **Example**:
    ```python
    success = observability_system.initialize(
        config=ObservabilityConfig(
            logging={
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "output": ["console", "file"],
                "file_path": "logs/openmas.log",
                "rotation": {
                    "max_bytes": 10485760,  # 10MB
                    "backup_count": 5
                }
            },
            metrics={
                "enabled": True,
                "collection_interval_seconds": 15,
                "exporters": ["prometheus", "datadog"],
                "prometheus": {
                    "port": 9090,
                    "endpoint": "/metrics"
                },
                "datadog": {
                    "api_key_env": "DATADOG_API_KEY",
                    "app_key_env": "DATADOG_APP_KEY"
                }
            },
            tracing={
                "enabled": True,
                "sampling_rate": 0.1,
                "exporters": ["jaeger", "zipkin"],
                "jaeger": {
                    "agent_host": "localhost",
                    "agent_port": 6831
                },
                "zipkin": {
                    "url": "http://localhost:9411/api/v2/spans"
                }
            },
            events={
                "enabled": True,
                "buffer_size": 1000,
                "flush_interval_seconds": 5,
                "exporters": ["elasticsearch", "kafka"],
                "elasticsearch": {
                    "hosts": ["http://localhost:9200"],
                    "index_prefix": "openmas-events-"
                },
                "kafka": {
                    "bootstrap_servers": ["localhost:9092"],
                    "topic": "openmas-events"
                }
            }
        )
    )
    ```

- `observability_system.update_logging_config(logging_config: LoggingConfig) → bool`
  - **Purpose**: Update logging configuration at runtime
  - **Parameters**: Logging configuration object
  - **Returns**: Boolean indicating successful update
  - **Example**:
    ```python
    success = observability_system.update_logging_config(
        logging_config=LoggingConfig(
            level="DEBUG",
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            output=["console", "file"],
            file_path="logs/openmas-debug.log"
        )
    )
    ```

- `observability_system.configure_component_observability(component_id: str, config: ComponentObservabilityConfig) → bool`
  - **Purpose**: Configure observability settings for a specific component
  - **Parameters**:
    - `component_id`: Component identifier
    - `config`: Component-specific observability configuration
  - **Returns**: Boolean indicating successful configuration
  - **Example**:
    ```python
    success = observability_system.configure_component_observability(
        component_id="agent_framework",
        config=ComponentObservabilityConfig(
            logging_level="DEBUG",
            metrics_enabled=True,
            tracing_enabled=True,
            event_types=["agent_created", "message_processed", "error"],
            custom_metrics=[
                {
                    "name": "messages_processed",
                    "type": "counter",
                    "description": "Number of messages processed"
                },
                {
                    "name": "message_processing_time",
                    "type": "histogram",
                    "description": "Time taken to process messages",
                    "unit": "ms",
                    "buckets": [10, 50, 100, 500, 1000]
                }
            ]
        )
    )
    ```

#### Events

```python
class ObservabilityConfigurationUpdatedEvent:
    """
    Event emitted when observability configuration has been updated.
    """
    event_name: str = "observability_configuration_updated"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")
    
    class Payload:
        update_id: str  # Unique identifier for this update
        update_time: datetime  # When the update was performed
        updated_systems: List[str]  # Observability systems that were updated (logging, metrics, tracing, events)
        updated_exporters: List[str] = []  # Exporters that were updated
        update_source: str  # Source of the update (user, system, API, etc.)
        update_reason: Optional[str] = None  # Reason for the update
        requires_restart: bool = False  # Whether any updates require a restart of observability components
        requires_reconfiguration: bool = False  # Whether any updates require reconfiguration of existing instrumentation
        update_details: Dict[str, Any] = {}  # Detailed information about the updates
        metadata: Dict[str, Any] = {}  # Additional metadata about the update
```

**Example Usage:**
```python
# Subscribe to observability configuration updated events
@event_system.subscribe(ObservabilityConfigurationUpdatedEvent.event_name)
def handle_observability_configuration_update(event: ObservabilityConfigurationUpdatedEvent):
    payload = event.payload
    updated_systems = payload.updated_systems
    
    logger.info(f"Observability configuration update: {', '.join(updated_systems)} systems affected")
    
    # Reconfigure logging if it was updated
    if "logging" in updated_systems:
        logger.info("Reconfiguring logging system")
        
        # Get the updated logging configuration
        logging_config = configuration_system.get_configuration_value("observability.logging")
        
        # Apply the logging configuration
        try:
            result = observability_system.logging_service.reconfigure(logging_config)
            logger.info(f"Logging reconfiguration result: Success={result.success}")
            
            if not result.success:
                logger.error(f"Failed to reconfigure logging: {result.error_message}")
        except Exception as e:
            logger.error(f"Error reconfiguring logging: {str(e)}")
    
    # Reconfigure metrics if they were updated
    if "metrics" in updated_systems:
        logger.info("Reconfiguring metrics system")
        
        # Get the updated metrics configuration
        metrics_config = configuration_system.get_configuration_value("observability.metrics")
        
        # Check if any exporters were added or removed
        current_exporters = observability_system.metrics_service.get_exporters()
        new_exporters = set(metrics_config.get("exporters", []))
        added_exporters = new_exporters - set(current_exporters)
        removed_exporters = set(current_exporters) - new_exporters
        
        if added_exporters:
            logger.info(f"Adding new metrics exporters: {', '.join(added_exporters)}")
            
            for exporter in added_exporters:
                exporter_config = metrics_config.get(exporter, {})
                observability_system.metrics_service.add_exporter(exporter, exporter_config)
        
        if removed_exporters:
            logger.info(f"Removing metrics exporters: {', '.join(removed_exporters)}")
            
            for exporter in removed_exporters:
                observability_system.metrics_service.remove_exporter(exporter)
        
        # Update collection interval if changed
        if "collection_interval_seconds" in metrics_config:
            current_interval = observability_system.metrics_service.get_collection_interval()
            new_interval = metrics_config["collection_interval_seconds"]
            
            if current_interval != new_interval:
                logger.info(f"Updating metrics collection interval from {current_interval}s to {new_interval}s")
                observability_system.metrics_service.set_collection_interval(new_interval)
    
    # Reconfigure tracing if it was updated
    if "tracing" in updated_systems:
        logger.info("Reconfiguring tracing system")
        
        # Get the updated tracing configuration
        tracing_config = configuration_system.get_configuration_value("observability.tracing")
        
        # Check if tracing was enabled or disabled
        tracing_enabled = tracing_config.get("enabled", False)
        currently_enabled = observability_system.tracing_service.is_enabled()
        
        if tracing_enabled != currently_enabled:
            if tracing_enabled:
                logger.info("Enabling tracing system")
                observability_system.tracing_service.enable()
            else:
                logger.info("Disabling tracing system")
                observability_system.tracing_service.disable()
        
        # Update sampling rate if changed
        if "sampling_rate" in tracing_config:
            current_rate = observability_system.tracing_service.get_sampling_rate()
            new_rate = tracing_config["sampling_rate"]
            
            if current_rate != new_rate:
                logger.info(f"Updating tracing sampling rate from {current_rate} to {new_rate}")
                observability_system.tracing_service.set_sampling_rate(new_rate)
        
        # Update tracing exporters
        if "exporters" in tracing_config:
            current_exporters = observability_system.tracing_service.get_exporters()
            new_exporters = set(tracing_config["exporters"])
            
            for exporter in new_exporters - set(current_exporters):
                logger.info(f"Adding tracing exporter: {exporter}")
                exporter_config = tracing_config.get(exporter, {})
                observability_system.tracing_service.add_exporter(exporter, exporter_config)
            
            for exporter in set(current_exporters) - new_exporters:
                logger.info(f"Removing tracing exporter: {exporter}")
                observability_system.tracing_service.remove_exporter(exporter)
    
    # Reconfigure events if they were updated
    if "events" in updated_systems:
        logger.info("Reconfiguring events system")
        
        # Get the updated events configuration
        events_config = configuration_system.get_configuration_value("observability.events")
        
        # Update buffer settings if changed
        if "buffer_size" in events_config:
            current_size = observability_system.events_service.get_buffer_size()
            new_size = events_config["buffer_size"]
            
            if current_size != new_size:
                logger.info(f"Updating events buffer size from {current_size} to {new_size}")
                observability_system.events_service.set_buffer_size(new_size)
        
        if "flush_interval_seconds" in events_config:
            current_interval = observability_system.events_service.get_flush_interval()
            new_interval = events_config["flush_interval_seconds"]
            
            if current_interval != new_interval:
                logger.info(f"Updating events flush interval from {current_interval}s to {new_interval}s")
                observability_system.events_service.set_flush_interval(new_interval)
        
        # Update event exporters
        if "exporters" in events_config:
            current_exporters = observability_system.events_service.get_exporters()
            new_exporters = set(events_config["exporters"])
            
            for exporter in new_exporters - set(current_exporters):
                logger.info(f"Adding events exporter: {exporter}")
                exporter_config = events_config.get(exporter, {})
                observability_system.events_service.add_exporter(exporter, exporter_config)
            
            for exporter in set(current_exporters) - new_exporters:
                logger.info(f"Removing events exporter: {exporter}")
                observability_system.events_service.remove_exporter(exporter)
    
    # Handle cases where restart is required
    if payload.requires_restart:
        logger.warning("Some observability configuration changes require a restart to take full effect")
        
        # Notify administrators
        notification_service.send_admin_notification(
            severity="warning",
            title="Observability System Restart Required",
            message="Some observability configuration changes require a restart to take full effect.",
            details={
                "updated_systems": updated_systems,
                "update_source": payload.update_source,
                "update_time": payload.update_time.isoformat()
            }
        )
```

```python
class ComponentObservabilityConfiguredEvent:
    """
    Event emitted when component-specific observability is configured.
    """
    event_name: str = "component_observability_configured"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")
    
    class Payload:
        component_id: str  # Identifier of the component
        component_type: str  # Type of component (agent_framework, protocol_layer, etc.)
        configuration_id: str  # Unique identifier for this configuration
        configuration_time: datetime  # When the configuration was performed
        logging_level: Optional[str] = None  # Configured logging level for the component
        metrics_enabled: Optional[bool] = None  # Whether metrics are enabled for the component
        tracing_enabled: Optional[bool] = None  # Whether tracing is enabled for the component
        events_enabled: Optional[bool] = None  # Whether events are enabled for the component
        custom_metrics: List[Dict[str, Any]] = []  # Custom metrics configured for the component
        monitored_event_types: List[str] = []  # Event types being monitored for the component
        configuration_source: str  # Source of the configuration (user, system, default, etc.)
        configuration_details: Dict[str, Any] = {}  # Detailed information about the configuration
```

**Example Usage:**
```python
# Subscribe to component observability configured events
@event_system.subscribe(ComponentObservabilityConfiguredEvent.event_name)
def handle_component_observability_configuration(event: ComponentObservabilityConfiguredEvent):
    payload = event.payload
    component_id = payload.component_id
    component_type = payload.component_type
    
    logger.info(f"Observability configured for component {component_id} (type: {component_type})")
    
    # Get the component's observability handler if available
    handler = observability_system.get_component_handler(component_id)
    
    if handler:
        logger.info(f"Configuring observability handler for component {component_id}")
        
        # Configure the handler based on the updated configuration
        if payload.logging_level:
            logger.info(f"Setting logging level for {component_id} to {payload.logging_level}")
            handler.set_logging_level(payload.logging_level)
        
        if payload.metrics_enabled is not None:
            if payload.metrics_enabled:
                logger.info(f"Enabling metrics for {component_id}")
                handler.enable_metrics()
                
                # Configure custom metrics if provided
                if payload.custom_metrics:
                    logger.info(f"Configuring {len(payload.custom_metrics)} custom metrics for {component_id}")
                    
                    for metric_config in payload.custom_metrics:
                        metric_name = metric_config.get("name")
                        metric_type = metric_config.get("type")
                        
                        if metric_name and metric_type:
                            handler.configure_metric(
                                name=metric_name,
                                metric_type=metric_type,
                                description=metric_config.get("description", ""),
                                unit=metric_config.get("unit"),
                                buckets=metric_config.get("buckets"),
                                labels=metric_config.get("labels", [])
                            )
            else:
                logger.info(f"Disabling metrics for {component_id}")
                handler.disable_metrics()
        
        if payload.tracing_enabled is not None:
            if payload.tracing_enabled:
                logger.info(f"Enabling tracing for {component_id}")
                handler.enable_tracing()
            else:
                logger.info(f"Disabling tracing for {component_id}")
                handler.disable_tracing()
        
        if payload.events_enabled is not None:
            if payload.events_enabled:
                logger.info(f"Enabling event monitoring for {component_id}")
                handler.enable_event_monitoring()
                
                # Configure monitored event types if provided
                if payload.monitored_event_types:
                    logger.info(f"Configuring {len(payload.monitored_event_types)} event types for monitoring in {component_id}")
                    handler.set_monitored_event_types(payload.monitored_event_types)
            else:
                logger.info(f"Disabling event monitoring for {component_id}")
                handler.disable_event_monitoring()
        
        # Apply any component-specific configuration details
        if payload.configuration_details:
            logger.info(f"Applying additional configuration details to {component_id}")
            handler.apply_configuration_details(payload.configuration_details)
    else:
        logger.warning(f"No observability handler found for component {component_id}")
        
        # Create a new handler if the component exists but doesn't have a handler yet
        if component_registry.component_exists(component_id):
            logger.info(f"Creating new observability handler for component {component_id}")
            
            # Create the handler
            new_handler = observability_system.create_component_handler(
                component_id=component_id,
                component_type=component_type,
                logging_level=payload.logging_level,
                metrics_enabled=payload.metrics_enabled or False,
                tracing_enabled=payload.tracing_enabled or False,
                events_enabled=payload.events_enabled or False
            )
            
            if new_handler:
                logger.info(f"Successfully created observability handler for {component_id}")
                
                # Configure the new handler with any additional settings
                if payload.custom_metrics:
                    for metric_config in payload.custom_metrics:
                        new_handler.configure_metric(**metric_config)
                
                if payload.monitored_event_types:
                    new_handler.set_monitored_event_types(payload.monitored_event_types)
                
                if payload.configuration_details:
                    new_handler.apply_configuration_details(payload.configuration_details)
            else:
                logger.error(f"Failed to create observability handler for {component_id}")
```

```python
class ProtocolObservabilityConfiguredEvent:
    """
    Event emitted when protocol-specific observability is configured.
    This extends component observability with protocol-specific monitoring.
    """
    event_name: str = "protocol_observability_configured"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")
    
    class Payload:
        protocol_id: str  # Identifier of the protocol
        protocol_version: str  # Version of the protocol
        configuration_id: str  # Unique identifier for this configuration
        configuration_time: datetime  # When the configuration was performed
        message_tracing_enabled: bool = False  # Whether message tracing is enabled for this protocol
        payload_sampling_enabled: bool = False  # Whether payload sampling is enabled
        payload_sampling_rate: float = 0.0  # Rate at which payloads are sampled (0.0 - 1.0)
        message_size_metrics_enabled: bool = False  # Whether message size metrics are enabled
        latency_metrics_enabled: bool = False  # Whether latency metrics are enabled
        error_rate_metrics_enabled: bool = False  # Whether error rate metrics are enabled
        custom_protocol_metrics: List[Dict[str, Any]] = []  # Custom metrics specific to this protocol
        monitored_message_types: List[str] = []  # Message types being monitored for this protocol
        configuration_source: str  # Source of the configuration (user, system, default, etc.)
        configuration_details: Dict[str, Any] = {}  # Detailed information about the configuration
```

**Example Usage:**
```python
# Example: Configuring protocol-specific observability

def configure_protocol_observability(protocol_id: str, config: Dict[str, Any]) -> bool:
    # Validate the configuration
    validation_result = configuration_system.validate_protocol_observability_configuration(protocol_id, config)
    
    if not validation_result.is_valid:
        logger.error(f"Invalid protocol observability configuration for {protocol_id}: {validation_result.errors}")
        return False
    
    # Get protocol information
    protocol_info = protocol_registry.get_protocol_info(protocol_id)
    if not protocol_info:
        logger.error(f"Protocol {protocol_id} not found in registry")
        return False
    
    protocol_version = protocol_info.get("version", "unknown")
    
    # Apply the configuration
    try:
        # Configure the protocol observability handler
        handler = observability_system.get_protocol_handler(protocol_id)
        
        if not handler:
            logger.info(f"Creating new observability handler for protocol {protocol_id}")
            handler = observability_system.create_protocol_handler(protocol_id)
        
        if not handler:
            logger.error(f"Failed to create observability handler for protocol {protocol_id}")
            return False
        
        # Configure message tracing
        message_tracing_enabled = config.get("message_tracing_enabled", False)
        handler.set_message_tracing_enabled(message_tracing_enabled)
        
        # Configure payload sampling
        payload_sampling_enabled = config.get("payload_sampling_enabled", False)
        payload_sampling_rate = config.get("payload_sampling_rate", 0.0)
        
        if payload_sampling_enabled:
            handler.enable_payload_sampling(payload_sampling_rate)
        else:
            handler.disable_payload_sampling()
        
        # Configure metrics
        metrics_config = {
            "message_size": config.get("message_size_metrics_enabled", False),
            "latency": config.get("latency_metrics_enabled", False),
            "error_rate": config.get("error_rate_metrics_enabled", False)
        }
        
        handler.configure_metrics(metrics_config)
        
        # Configure custom protocol metrics
        custom_metrics = config.get("custom_protocol_metrics", [])
        for metric_config in custom_metrics:
            handler.configure_custom_metric(**metric_config)
        
        # Configure monitored message types
        monitored_message_types = config.get("monitored_message_types", [])
        handler.set_monitored_message_types(monitored_message_types)
        
        # Apply any additional configuration details
        configuration_details = config.get("configuration_details", {})
        handler.apply_configuration_details(configuration_details)
        
        # Emit protocol observability configured event
        configuration_id = f"protocol_obs_{uuid.uuid4().hex[:8]}"
        configuration_time = datetime.now()
        
        event_system.emit(
            event_name="protocol_observability_configured",
            payload=ProtocolObservabilityConfiguredEvent.Payload(
                protocol_id=protocol_id,
                protocol_version=protocol_version,
                configuration_id=configuration_id,
                configuration_time=configuration_time,
                message_tracing_enabled=message_tracing_enabled,
                payload_sampling_enabled=payload_sampling_enabled,
                payload_sampling_rate=payload_sampling_rate,
                message_size_metrics_enabled=metrics_config["message_size"],
                latency_metrics_enabled=metrics_config["latency"],
                error_rate_metrics_enabled=metrics_config["error_rate"],
                custom_protocol_metrics=custom_metrics,
                monitored_message_types=monitored_message_types,
                configuration_source="api",
                configuration_details=configuration_details
            )
        )
        
        logger.info(f"Successfully configured observability for protocol {protocol_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error configuring observability for protocol {protocol_id}: {str(e)}")
        
        # Report the error
        error_reporting.report_error(
            error_type="protocol_observability_configuration_failure",
            component="observability_system",
            details={
                "protocol_id": protocol_id,
                "protocol_version": protocol_version,
                "error_message": str(e),
                "configuration": config
            }
        )
        
        return False
```

```python
class ReasoningObservabilityConfiguredEvent:
    """
    Event emitted when reasoning-specific observability is configured.
    This extends component observability with reasoning-specific monitoring.
    """
    event_name: str = "reasoning_observability_configured"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")
    
    class Payload:
        reasoning_id: str  # Identifier of the reasoning engine
        reasoning_type: str  # Type of reasoning engine (llm, rule-based, bdi, etc.)
        configuration_id: str  # Unique identifier for this configuration
        configuration_time: datetime  # When the configuration was performed
        reasoning_tracing_enabled: bool = False  # Whether reasoning tracing is enabled
        reasoning_step_logging_enabled: bool = False  # Whether logging of reasoning steps is enabled
        reasoning_explanation_enabled: bool = False  # Whether explanation generation is enabled
        reasoning_performance_metrics_enabled: bool = False  # Whether performance metrics are enabled
        knowledge_access_tracing_enabled: bool = False  # Whether knowledge access tracing is enabled
        custom_reasoning_metrics: List[Dict[str, Any]] = []  # Custom metrics for this reasoning engine
        monitored_reasoning_events: List[str] = []  # Reasoning events being monitored
        configuration_source: str  # Source of the configuration (user, system, default, etc.)
        configuration_details: Dict[str, Any] = {}  # Detailed information about the configuration
```

**Example Usage:**
```python
# Example: Configuring reasoning-specific observability

def configure_reasoning_observability(reasoning_id: str, config: Dict[str, Any]) -> bool:
    # Validate the configuration
    validation_result = configuration_system.validate_reasoning_observability_configuration(reasoning_id, config)
    
    if not validation_result.is_valid:
        logger.error(f"Invalid reasoning observability configuration for {reasoning_id}: {validation_result.errors}")
        return False
    
    # Get reasoning engine information
    reasoning_info = reasoning_registry.get_reasoning_info(reasoning_id)
    if not reasoning_info:
        logger.error(f"Reasoning engine {reasoning_id} not found in registry")
        return False
    
    reasoning_type = reasoning_info.get("type", "unknown")
    
    # Apply the configuration
    try:
        # Configure the reasoning observability handler
        handler = observability_system.get_reasoning_handler(reasoning_id)
        
        if not handler:
            logger.info(f"Creating new observability handler for reasoning engine {reasoning_id}")
            handler = observability_system.create_reasoning_handler(reasoning_id, reasoning_type)
        
        if not handler:
            logger.error(f"Failed to create observability handler for reasoning engine {reasoning_id}")
            return False
        
        # Configure reasoning tracing
        reasoning_tracing_enabled = config.get("reasoning_tracing_enabled", False)
        handler.set_reasoning_tracing_enabled(reasoning_tracing_enabled)
        
        # Configure reasoning step logging
        reasoning_step_logging_enabled = config.get("reasoning_step_logging_enabled", False)
        handler.set_reasoning_step_logging_enabled(reasoning_step_logging_enabled)
        
        # Configure explanation generation
        reasoning_explanation_enabled = config.get("reasoning_explanation_enabled", False)
        handler.set_reasoning_explanation_enabled(reasoning_explanation_enabled)
        
        # Configure performance metrics
        reasoning_performance_metrics_enabled = config.get("reasoning_performance_metrics_enabled", False)
        handler.set_performance_metrics_enabled(reasoning_performance_metrics_enabled)
        
        # Configure knowledge access tracing
        knowledge_access_tracing_enabled = config.get("knowledge_access_tracing_enabled", False)
        handler.set_knowledge_access_tracing_enabled(knowledge_access_tracing_enabled)
        
        # Configure custom reasoning metrics
        custom_metrics = config.get("custom_reasoning_metrics", [])
        for metric_config in custom_metrics:
            handler.configure_custom_metric(**metric_config)
        
        # Configure monitored reasoning events
        monitored_reasoning_events = config.get("monitored_reasoning_events", [])
        handler.set_monitored_reasoning_events(monitored_reasoning_events)
        
        # Apply any additional configuration details
        configuration_details = config.get("configuration_details", {})
        handler.apply_configuration_details(configuration_details)
        
        # Emit reasoning observability configured event
        configuration_id = f"reasoning_obs_{uuid.uuid4().hex[:8]}"
        configuration_time = datetime.now()
        
        event_system.emit(
            event_name="reasoning_observability_configured",
            payload=ReasoningObservabilityConfiguredEvent.Payload(
                reasoning_id=reasoning_id,
                reasoning_type=reasoning_type,
                configuration_id=configuration_id,
                configuration_time=configuration_time,
                reasoning_tracing_enabled=reasoning_tracing_enabled,
                reasoning_step_logging_enabled=reasoning_step_logging_enabled,
                reasoning_explanation_enabled=reasoning_explanation_enabled,
                reasoning_performance_metrics_enabled=reasoning_performance_metrics_enabled,
                knowledge_access_tracing_enabled=knowledge_access_tracing_enabled,
                custom_reasoning_metrics=custom_metrics,
                monitored_reasoning_events=monitored_reasoning_events,
                configuration_source="api",
                configuration_details=configuration_details
            )
        )
        
        logger.info(f"Successfully configured observability for reasoning engine {reasoning_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error configuring observability for reasoning engine {reasoning_id}: {str(e)}")
        
        # Report the error
        error_reporting.report_error(
            error_type="reasoning_observability_configuration_failure",
            component="observability_system",
            details={
                "reasoning_id": reasoning_id,
                "reasoning_type": reasoning_type,
                "error_message": str(e),
                "configuration": config
            }
        )
        
        return False
```

### Observability System → Configuration System

#### Methods/Functions
- `configuration_system.get_observability_configuration() → ObservabilityConfig`
  - **Purpose**: Retrieve the current observability configuration
  - **Parameters**: None
  - **Returns**: Current observability configuration
  - **Example**:
    ```python
    config = configuration_system.get_observability_configuration()
    ```

- `configuration_system.validate_observability_configuration(config: ObservabilityConfig) → ValidationResult`
  - **Purpose**: Validate observability configuration against schema
  - **Parameters**: Observability configuration object
  - **Returns**: Validation result with any errors
  - **Example**:
    ```python
    result = configuration_system.validate_observability_configuration(
        config=updated_observability_config
    )
    ```

- `configuration_system.get_component_observability_configuration(component_id: str) → ComponentObservabilityConfig`
  - **Purpose**: Retrieve observability configuration for a specific component
  - **Parameters**: Component identifier
  - **Returns**: Component-specific observability configuration
  - **Example**:
    ```python
    config = configuration_system.get_component_observability_configuration(
        component_id="agent_framework"
    )
    ```

#### Events
- `observability_configuration_requested`
  - **Purpose**: Notifies when observability configuration is requested
  - **Payload**: Requester ID, configuration path
  - **Subscribers**: Configuration System audit log

- `observability_configuration_validation_failed`
  - **Purpose**: Notifies when observability configuration validation fails
  - **Payload**: Validation errors, configuration object
  - **Subscribers**: Configuration System error handler

## Data Flows

### Observability System Initialization Flow
1. **Configuration System → Observability System**: Configuration System provides observability configuration
2. **Observability System Processing**: Observability System initializes components based on configuration
3. **Observability System → Configuration System**: Observability System validates configuration
4. **Observability System → All Components**: Observability System establishes monitoring for all components

### Component Observability Configuration Flow
1. **Configuration System → Observability System**: Configuration System provides component-specific configuration
2. **Observability System Processing**: Observability System configures component-specific monitoring
3. **Observability System → Component**: Observability System attaches monitoring to component
4. **Component → Observability System**: Component emits telemetry data based on configuration

## Configuration Dependencies

The following configuration parameters affect this interaction:

```yaml
observability:
  logging:
    level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    output: ["console", "file"]
    file_path: "logs/openmas.log"
    rotation:
      max_bytes: 10485760  # 10MB
      backup_count: 5
  
  metrics:
    enabled: true
    collection_interval_seconds: 15
    exporters: ["prometheus", "datadog"]
    prometheus:
      port: 9090
      endpoint: "/metrics"
    datadog:
      api_key_env: "DATADOG_API_KEY"
      app_key_env: "DATADOG_APP_KEY"
  
  tracing:
    enabled: true
    sampling_rate: 0.1  # 10% of transactions
    exporters: ["jaeger", "zipkin"]
    jaeger:
      agent_host: "localhost"
      agent_port: 6831
    zipkin:
      url: "http://localhost:9411/api/v2/spans"
  
  events:
    enabled: true
    buffer_size: 1000
    flush_interval_seconds: 5
    exporters: ["elasticsearch", "kafka"]
    elasticsearch:
      hosts: ["http://localhost:9200"]
      index_prefix: "openmas-events-"
    kafka:
      bootstrap_servers: ["localhost:9092"]
      topic: "openmas-events"

  components:
    agent_framework:
      logging_level: "INFO"
      metrics_enabled: true
      tracing_enabled: true
      event_types: ["agent_created", "message_processed", "error"]
      custom_metrics:
        - name: "messages_processed"
          type: "counter"
          description: "Number of messages processed"
        - name: "message_processing_time"
          type: "histogram"
          description: "Time taken to process messages"
          unit: "ms"
          buckets: [10, 50, 100, 500, 1000]
    
    protocol_layer:
      logging_level: "INFO"
      metrics_enabled: true
      tracing_enabled: true
      event_types: ["message_sent", "message_received", "protocol_error"]
      custom_metrics:
        - name: "messages_sent"
          type: "counter"
          description: "Number of messages sent per protocol"
          labels: ["protocol"]
        - name: "message_size"
          type: "histogram"
          description: "Size of messages in bytes"
          unit: "bytes"
          buckets: [100, 1000, 10000, 100000, 1000000]
```

## Error Handling

1. **Configuration Validation Failures**:
   - Validation errors are logged at ERROR level
   - Fallback to default configuration for invalid components
   - Configuration errors trigger alerts to system administrators

2. **Exporter Configuration Issues**:
   - Automatic disabling of misconfigured exporters
   - Retry logic for temporary connectivity issues
   - Queueing of telemetry data during outages with configurable limits

3. **Performance Impact Management**:
   - Adaptive sampling based on system load
   - Circuit breaker pattern for telemetry collection under high load
   - Monitoring of the monitoring system itself (meta-monitoring)

## Extension Points

1. **Custom Exporters**:
   - New telemetry exporters can be registered
   - Exporter interface:
     ```python
     class TelemetryExporter:
         def initialize(self, config: Dict[str, Any]) → bool:
             # Initialize exporter with config
             pass
         
         def export(self, telemetry_data: List[TelemetryRecord]) → bool:
             # Export telemetry data to external system
             pass
             
         def shutdown(self) → None:
             # Clean shutdown of exporter
             pass
     ```

2. **Custom Metric Types**:
   - Support for custom metric types beyond standard types
   - Example custom metric configuration:
     ```yaml
     custom_metrics:
       - name: "conversation_quality"
         type: "custom"
         implementation_class: "ConversationQualityMetric"
         config:
           scoring_algorithm: "sentiment_based"
           threshold: 0.7
     ```

## Notes on Multi-Protocol Design

The Configuration System ↔ Observability System interface supports OpenMAS's multi-protocol design by:

- Providing protocol-specific monitoring configurations
- Collecting protocol-specific metrics and events
- Maintaining protocol identification in tracing and logging
- Supporting consistent observability across protocol boundaries

This enables proper monitoring of multi-protocol interactions while maintaining clear boundaries between protocol-specific and protocol-agnostic telemetry.

## Notes on Reasoning Agnosticism

The Observability System configuration supports OpenMAS's reasoning agnostic architecture by:

- Separating communication monitoring (body) from reasoning monitoring (brain)
- Providing specialized monitoring for different reasoning approaches
- Maintaining consistent telemetry interfaces regardless of reasoning implementation
- Supporting correlated tracing between communication and reasoning components while preserving separation

## Example: Protocol-Specific vs. Reasoning-Specific Observability

```yaml
observability:
  components:
    # Protocol Layer Observability (Body)
    protocol_layer:
      metrics_enabled: true
      custom_metrics:
        - name: "protocol_message_count"
          type: "counter"
          labels: ["protocol", "direction", "message_type"]
        - name: "protocol_latency"
          type: "histogram"
          unit: "ms"
          buckets: [10, 50, 100, 500, 1000]
      
      tracing:
        enabled: true
        span_processor: "protocol_spans"
        attributes:
          - "protocol.type"
          - "protocol.version"
          - "message.id"
          - "message.type"
    
    # Reasoning Monitoring (Brain)
    krr:
      metrics_enabled: true
      custom_metrics:
        - name: "reasoning_time"
          type: "histogram"
          labels: ["reasoning_type", "complexity"]
          unit: "ms"
          buckets: [10, 50, 100, 500, 1000, 5000]
        - name: "reasoning_confidence"
          type: "gauge"
          labels: ["reasoning_type", "decision_type"]
          unit: "score"
      
      tracing:
        enabled: true
        span_processor: "reasoning_spans"
        attributes:
          - "reasoning.type"
          - "reasoning.input_complexity"
          - "reasoning.decision_type"
          - "reasoning.iterations"
```

This configuration example shows how the Observability System maintains separate monitoring for communication components (protocol layer) and reasoning components (KR&R) while providing correlated data through distributed tracing.

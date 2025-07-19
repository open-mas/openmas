# Configuration System ↔ Security System

## Relationship Summary
- **Configuration System → Security System**: Configures
- **Security System → Configuration System**: Depends On

## Interface Definitions

### Configuration System → Security System

#### Methods/Functions
- `security_system.initialize(config: SecurityConfig) → bool`
  - **Purpose**: Initialize the Security System with configuration parameters
  - **Parameters**: Configuration object containing all Security System settings
  - **Returns**: Boolean indicating successful initialization
  - **Example**:
    ```python
    success = security_system.initialize(
        config=SecurityConfig(
            authentication={
                "providers": [
                    {
                        "name": "oauth2",
                        "type": "oauth2",
                        "implementation_class": "OAuth2Provider",
                        "config": {
                            "client_id": "${OAUTH_CLIENT_ID}",
                            "client_secret": "${OAUTH_CLIENT_SECRET}",
                            "token_url": "https://auth.example.com/token",
                            "auth_url": "https://auth.example.com/authorize",
                            "scopes": ["openmas.read", "openmas.write"]
                        }
                    },
                    {
                        "name": "api_key",
                        "type": "api_key",
                        "implementation_class": "ApiKeyProvider",
                        "config": {
                            "header_name": "X-API-Key",
                            "key_validation": {
                                "method": "database",
                                "database_table": "api_keys"
                            }
                        }
                    }
                ],
                "default_provider": "oauth2"
            },
            authorization={
                "method": "role_based",
                "implementation_class": "RoleBasedAuthorization",
                "roles": [
                    {
                        "name": "admin",
                        "permissions": ["*"]
                    },
                    {
                        "name": "agent",
                        "permissions": ["agent.read", "agent.write", "message.send", "message.receive"]
                    },
                    {
                        "name": "observer",
                        "permissions": ["agent.read", "message.read"]
                    }
                ],
                "default_role": "observer"
            },
            encryption={
                "message_encryption": {
                    "enabled": true,
                    "algorithm": "AES-256-GCM",
                    "key_management": "vault"
                },
                "storage_encryption": {
                    "enabled": true,
                    "algorithm": "AES-256-GCM",
                    "key_management": "vault"
                },
                "key_providers": {
                    "vault": {
                        "implementation_class": "VaultKeyProvider",
                        "config": {
                            "url": "https://vault.example.com",
                            "token_env": "VAULT_TOKEN",
                            "key_path": "secret/openmas/keys"
                        }
                    }
                }
            },
            rate_limiting={
                "enabled": true,
                "implementation_class": "TokenBucketRateLimiter",
                "global_limits": {
                    "requests_per_minute": 1000
                },
                "per_client_limits": {
                    "requests_per_minute": 100
                },
                "per_endpoint_limits": {
                    "/api/agents": {
                        "requests_per_minute": 200
                    },
                    "/api/messages": {
                        "requests_per_minute": 500
                    }
                }
            }
        )
    )
    ```

- `security_system.update_authentication_config(auth_config: AuthenticationConfig) → bool`
  - **Purpose**: Update authentication configuration at runtime
  - **Parameters**: Authentication configuration object
  - **Returns**: Boolean indicating successful update
  - **Example**:
    ```python
    success = security_system.update_authentication_config(
        auth_config=AuthenticationConfig(
            providers=[
                {
                    "name": "jwt",
                    "type": "jwt",
                    "implementation_class": "JWTProvider",
                    "config": {
                        "secret_key_env": "JWT_SECRET_KEY",
                        "algorithm": "HS256",
                        "token_expiry_minutes": 60
                    }
                }
            ],
            default_provider="jwt"
        )
    )
    ```

- `security_system.configure_protocol_security(protocol_type: str, config: ProtocolSecurityConfig) → bool`
  - **Purpose**: Configure security settings for a specific protocol
  - **Parameters**:
    - `protocol_type`: Protocol identifier
    - `config`: Protocol-specific security configuration
  - **Returns**: Boolean indicating successful configuration
  - **Example**:
    ```python
    success = security_system.configure_protocol_security(
        protocol_type="a2a",
        config=ProtocolSecurityConfig(
            authentication={
                "provider": "oauth2",
                "required": true
            },
            authorization={
                "roles_allowed": ["agent", "admin"],
                "default_role": "agent"
            },
            message_encryption={
                "enabled": true,
                "algorithm": "AES-256-GCM"
            },
            rate_limiting={
                "requests_per_minute": 200
            }
        )
    )
    ```

#### Events

```python
class SecurityConfigurationUpdatedEvent:
    """
    Event emitted when security configuration has been updated.
    """
    event_name: str = "security_configuration_updated"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")
    
    class Payload:
        update_id: str  # Unique identifier for this update
        update_time: datetime  # When the update was performed
        updated_systems: List[str]  # Security systems that were updated (authentication, authorization, encryption, rate_limiting)
        update_source: str  # Source of the update (user, system, API, etc.)
        update_reason: Optional[str] = None  # Reason for the update
        requires_restart: bool = False  # Whether any updates require a restart of security components
        authentication_updated: bool = False  # Whether authentication configuration was updated
        authorization_updated: bool = False  # Whether authorization configuration was updated
        encryption_updated: bool = False  # Whether encryption configuration was updated
        rate_limiting_updated: bool = False  # Whether rate limiting configuration was updated
        update_details: Dict[str, Any] = {}  # Detailed information about the updates
        metadata: Dict[str, Any] = {}  # Additional metadata about the update
```

**Example Usage:**
```python
# Subscribe to security configuration updated events
@event_system.subscribe(SecurityConfigurationUpdatedEvent.event_name)
def handle_security_configuration_update(event: SecurityConfigurationUpdatedEvent):
    payload = event.payload
    updated_systems = payload.updated_systems
    
    logger.info(f"Security configuration update: {', '.join(updated_systems)} systems affected")
    
    # Reconfigure authentication if it was updated
    if "authentication" in updated_systems and payload.authentication_updated:
        logger.info("Reconfiguring authentication system")
        
        # Get the updated authentication configuration
        auth_config = configuration_system.get_configuration_value("security.authentication")
        
        # Apply the authentication configuration
        try:
            result = security_system.authentication_service.reconfigure(auth_config)
            logger.info(f"Authentication reconfiguration result: Success={result.success}")
            
            if not result.success:
                logger.error(f"Failed to reconfigure authentication: {result.error_message}")
        except Exception as e:
            logger.error(f"Error reconfiguring authentication: {str(e)}")
    
    # Reconfigure authorization if it was updated
    if "authorization" in updated_systems and payload.authorization_updated:
        logger.info("Reconfiguring authorization system")
        
        # Get the updated authorization configuration
        authz_config = configuration_system.get_configuration_value("security.authorization")
        
        # Apply the authorization configuration
        try:
            result = security_system.authorization_service.reconfigure(authz_config)
            logger.info(f"Authorization reconfiguration result: Success={result.success}")
            
            if not result.success:
                logger.error(f"Failed to reconfigure authorization: {result.error_message}")
                
            # Refresh role cache if necessary
            if "roles" in payload.update_details.get("authorization", {}):
                logger.info("Refreshing role cache after role configuration update")
                security_system.authorization_service.refresh_role_cache()
        except Exception as e:
            logger.error(f"Error reconfiguring authorization: {str(e)}")
    
    # Reconfigure encryption if it was updated
    if "encryption" in updated_systems and payload.encryption_updated:
        logger.info("Reconfiguring encryption system")
        
        # Get the updated encryption configuration
        encryption_config = configuration_system.get_configuration_value("security.encryption")
        
        # Apply the encryption configuration
        try:
            result = security_system.encryption_service.reconfigure(encryption_config)
            logger.info(f"Encryption reconfiguration result: Success={result.success}")
            
            if not result.success:
                logger.error(f"Failed to reconfigure encryption: {result.error_message}")
                
            # Handle key rotation if necessary
            if "key_rotation" in payload.update_details.get("encryption", {}):
                logger.info("Initiating key rotation after encryption configuration update")
                rotation_result = security_system.encryption_service.rotate_keys()
                
                if rotation_result.success:
                    logger.info("Key rotation completed successfully")
                else:
                    logger.error(f"Key rotation failed: {rotation_result.error_message}")
        except Exception as e:
            logger.error(f"Error reconfiguring encryption: {str(e)}")
    
    # Reconfigure rate limiting if it was updated
    if "rate_limiting" in updated_systems and payload.rate_limiting_updated:
        logger.info("Reconfiguring rate limiting system")
        
        # Get the updated rate limiting configuration
        rate_limit_config = configuration_system.get_configuration_value("security.rate_limiting")
        
        # Apply the rate limiting configuration
        try:
            result = security_system.rate_limiting_service.reconfigure(rate_limit_config)
            logger.info(f"Rate limiting reconfiguration result: Success={result.success}")
            
            if not result.success:
                logger.error(f"Failed to reconfigure rate limiting: {result.error_message}")
                
            # Reset rate limit counters if configured to do so
            if payload.update_details.get("rate_limiting", {}).get("reset_counters", False):
                logger.info("Resetting rate limit counters after configuration update")
                security_system.rate_limiting_service.reset_counters()
        except Exception as e:
            logger.error(f"Error reconfiguring rate limiting: {str(e)}")
    
    # Handle cases where restart is required
    if payload.requires_restart:
        logger.warning("Some security configuration changes require a restart to take full effect")
        
        # Notify administrators
        notification_service.send_admin_notification(
            severity="warning",
            title="Security System Restart Required",
            message="Some security configuration changes require a restart to take full effect.",
            details={
                "updated_systems": updated_systems,
                "update_source": payload.update_source,
                "update_time": payload.update_time.isoformat()
            }
        )
        
        # Check if automated restart is enabled
        if configuration_system.get_configuration_value("security.auto_restart_on_config_change", False):
            logger.info("Initiating automated security system restart")
            
            # Schedule restart with delay to allow current operations to complete
            restart_scheduler.schedule_task(
                task_name="security_system_restart",
                delay_seconds=30,
                task_function=security_system.restart,
                task_args={"reason": "configuration_update"}
            )
```

```python
class ProtocolSecurityConfiguredEvent:
    """
    Event emitted when protocol-specific security is configured.
    """
    event_name: str = "protocol_security_configured"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")
    
    class Payload:
        protocol_type: str  # Type of the protocol (a2a, mcp, etc.)
        protocol_version: str  # Version of the protocol
        configuration_id: str  # Unique identifier for this configuration
        configuration_time: datetime  # When the configuration was performed
        authentication_configured: bool = False  # Whether authentication was configured
        authorization_configured: bool = False  # Whether authorization was configured
        encryption_configured: bool = False  # Whether encryption was configured
        rate_limiting_configured: bool = False  # Whether rate limiting was configured
        authentication_provider: Optional[str] = None  # Name of the configured authentication provider
        authentication_required: bool = False  # Whether authentication is required
        allowed_roles: List[str] = []  # Roles allowed to use this protocol
        encryption_enabled: bool = False  # Whether message encryption is enabled
        encryption_algorithm: Optional[str] = None  # Encryption algorithm used
        rate_limit: Optional[int] = None  # Rate limit in requests per minute
        configuration_source: str  # Source of the configuration (user, system, default, etc.)
        configuration_details: Dict[str, Any] = {}  # Detailed information about the configuration
```

**Example Usage:**
```python
# Subscribe to protocol security configured events
@event_system.subscribe(ProtocolSecurityConfiguredEvent.event_name)
def handle_protocol_security_configuration(event: ProtocolSecurityConfiguredEvent):
    payload = event.payload
    protocol_type = payload.protocol_type
    protocol_version = payload.protocol_version
    
    logger.info(f"Security configured for protocol {protocol_type} v{protocol_version}")
    
    # Get the protocol security handler
    handler = security_system.get_protocol_security_handler(protocol_type)
    
    if handler:
        logger.info(f"Configuring security handler for protocol {protocol_type}")
        
        # Configure the handler based on the updated configuration
        if payload.authentication_configured:
            logger.info(f"Configuring authentication for {protocol_type} with provider {payload.authentication_provider}")
            
            # Get the authentication provider
            provider = security_system.authentication_service.get_provider(payload.authentication_provider)
            
            if provider:
                # Configure the authentication provider for this protocol
                handler.configure_authentication(
                    provider=provider,
                    required=payload.authentication_required
                )
            else:
                logger.error(f"Authentication provider {payload.authentication_provider} not found")
        
        if payload.authorization_configured:
            logger.info(f"Configuring authorization for {protocol_type} with allowed roles: {', '.join(payload.allowed_roles)}")
            
            # Configure authorization for this protocol
            handler.configure_authorization(
                allowed_roles=payload.allowed_roles,
                default_role=payload.configuration_details.get("authorization", {}).get("default_role")
            )
        
        if payload.encryption_configured:
            logger.info(f"Configuring encryption for {protocol_type}: Enabled={payload.encryption_enabled}")
            
            if payload.encryption_enabled:
                # Configure encryption for this protocol
                handler.configure_encryption(
                    algorithm=payload.encryption_algorithm,
                    config=payload.configuration_details.get("encryption", {})
                )
            else:
                # Disable encryption for this protocol
                handler.disable_encryption()
        
        if payload.rate_limiting_configured:
            logger.info(f"Configuring rate limiting for {protocol_type}: {payload.rate_limit} requests per minute")
            
            # Configure rate limiting for this protocol
            handler.configure_rate_limiting(
                requests_per_minute=payload.rate_limit,
                config=payload.configuration_details.get("rate_limiting", {})
            )
        
        # Apply any additional configuration details
        handler.apply_configuration_details(payload.configuration_details)
        
        logger.info(f"Successfully configured security for protocol {protocol_type}")
        
        # Notify protocol layer about security configuration
        event_system.emit("protocol_security_ready", {
            "protocol_type": protocol_type,
            "protocol_version": protocol_version,
            "configuration_id": payload.configuration_id,
            "configuration_time": payload.configuration_time.isoformat()
        })
    else:
        logger.warning(f"No security handler found for protocol {protocol_type}")
        
        # Create a new handler if the protocol exists but doesn't have a handler yet
        protocol_info = protocol_registry.get_protocol_info(protocol_type)
        
        if protocol_info:
            logger.info(f"Creating new security handler for protocol {protocol_type}")
            
            # Create the handler
            new_handler = security_system.create_protocol_security_handler(
                protocol_type=protocol_type,
                protocol_version=protocol_version
            )
            
            if new_handler:
                logger.info(f"Successfully created security handler for {protocol_type}")
                
                # Recursively call this event handler with the same event to configure the new handler
                handle_protocol_security_configuration(event)
            else:
                logger.error(f"Failed to create security handler for {protocol_type}")
```

```python
class A2AProtocolSecurityConfiguredEvent(ProtocolSecurityConfiguredEvent):
    """
    Event emitted when A2A protocol-specific security is configured.
    Extends ProtocolSecurityConfiguredEvent with A2A-specific fields.
    """
    event_name: str = "a2a_protocol_security_configured"  # Override event name
    
    class Payload(ProtocolSecurityConfiguredEvent.Payload):
        oauth_configured: bool = False  # Whether OAuth is configured
        oauth_scopes: List[str] = []  # OAuth scopes required
        agent_card_validation_enabled: bool = False  # Whether agent card validation is enabled
        multipart_message_signing_enabled: bool = False  # Whether multipart message signing is enabled
        a2a_specific_security_details: Dict[str, Any] = {}  # A2A-specific security details
```

**Example Usage:**
```python
# Example: Configuring A2A protocol security

def configure_a2a_protocol_security(config: Dict[str, Any]) -> bool:
    # Validate the configuration
    validation_result = configuration_system.validate_protocol_security_configuration("a2a", config)
    
    if not validation_result.is_valid:
        logger.error(f"Invalid A2A protocol security configuration: {validation_result.errors}")
        return False
    
    # Get protocol information
    protocol_info = protocol_registry.get_protocol_info("a2a")
    if not protocol_info:
        logger.error("A2A protocol not found in registry")
        return False
    
    protocol_version = protocol_info.get("version", "v1")
    
    # Extract configuration components
    authentication_config = config.get("authentication", {})
    authorization_config = config.get("authorization", {})
    encryption_config = config.get("encryption", {})
    rate_limiting_config = config.get("rate_limiting", {})
    oauth_config = config.get("oauth", {})
    agent_card_config = config.get("agent_card_validation", {})
    multipart_message_config = config.get("multipart_message", {})
    
    # Apply the configuration
    try:
        # Configure the A2A protocol security handler
        handler = security_system.get_protocol_security_handler("a2a")
        
        if not handler:
            logger.info("Creating new security handler for A2A protocol")
            handler = security_system.create_protocol_security_handler("a2a", protocol_version)
        
        if not handler:
            logger.error("Failed to create security handler for A2A protocol")
            return False
        
        # Configure authentication
        authentication_configured = "provider" in authentication_config
        authentication_provider = authentication_config.get("provider")
        authentication_required = authentication_config.get("required", True)
        
        if authentication_configured:
            auth_provider = security_system.authentication_service.get_provider(authentication_provider)
            handler.configure_authentication(auth_provider, authentication_required)
        
        # Configure authorization
        authorization_configured = "roles_allowed" in authorization_config
        allowed_roles = authorization_config.get("roles_allowed", [])
        default_role = authorization_config.get("default_role")
        
        if authorization_configured:
            handler.configure_authorization(allowed_roles, default_role)
        
        # Configure encryption
        encryption_configured = "enabled" in encryption_config
        encryption_enabled = encryption_config.get("enabled", False)
        encryption_algorithm = encryption_config.get("algorithm")
        
        if encryption_configured:
            if encryption_enabled:
                handler.configure_encryption(encryption_algorithm, encryption_config)
            else:
                handler.disable_encryption()
        
        # Configure rate limiting
        rate_limiting_configured = "requests_per_minute" in rate_limiting_config
        rate_limit = rate_limiting_config.get("requests_per_minute")
        
        if rate_limiting_configured:
            handler.configure_rate_limiting(rate_limit, rate_limiting_config)
        
        # Configure A2A-specific security features
        
        # OAuth configuration
        oauth_configured = len(oauth_config) > 0
        oauth_scopes = oauth_config.get("scopes", [])
        
        if oauth_configured:
            handler.configure_oauth(oauth_config)
        
        # Agent card validation
        agent_card_validation_enabled = agent_card_config.get("enabled", False)
        
        if "enabled" in agent_card_config:
            handler.configure_agent_card_validation(agent_card_validation_enabled, agent_card_config)
        
        # Multipart message signing
        multipart_message_signing_enabled = multipart_message_config.get("signing_enabled", False)
        
        if "signing_enabled" in multipart_message_config:
            handler.configure_multipart_message_signing(multipart_message_signing_enabled, multipart_message_config)
        
        # Emit A2A protocol security configured event
        configuration_id = f"a2a_security_{uuid.uuid4().hex[:8]}"
        configuration_time = datetime.now()
        
        event_system.emit(
            event_name="a2a_protocol_security_configured",
            payload=A2AProtocolSecurityConfiguredEvent.Payload(
                protocol_type="a2a",
                protocol_version=protocol_version,
                configuration_id=configuration_id,
                configuration_time=configuration_time,
                authentication_configured=authentication_configured,
                authorization_configured=authorization_configured,
                encryption_configured=encryption_configured,
                rate_limiting_configured=rate_limiting_configured,
                authentication_provider=authentication_provider,
                authentication_required=authentication_required,
                allowed_roles=allowed_roles,
                encryption_enabled=encryption_enabled,
                encryption_algorithm=encryption_algorithm,
                rate_limit=rate_limit,
                configuration_source="api",
                configuration_details=config,
                oauth_configured=oauth_configured,
                oauth_scopes=oauth_scopes,
                agent_card_validation_enabled=agent_card_validation_enabled,
                multipart_message_signing_enabled=multipart_message_signing_enabled,
                a2a_specific_security_details={
                    "oauth": oauth_config,
                    "agent_card_validation": agent_card_config,
                    "multipart_message": multipart_message_config
                }
            )
        )
        
        logger.info("A2A protocol security configuration applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error configuring A2A protocol security: {str(e)}")
        
        # Report the error
        error_reporting.report_error(
            error_type="a2a_protocol_security_configuration_failure",
            component="security_system",
            details={
                "protocol_version": protocol_version,
                "error_message": str(e),
                "configuration": config
            }
        )
        
        return False
```

```python
class MCPProtocolSecurityConfiguredEvent(ProtocolSecurityConfiguredEvent):
    """
    Event emitted when MCP protocol-specific security is configured.
    Extends ProtocolSecurityConfiguredEvent with MCP-specific fields.
    """
    event_name: str = "mcp_protocol_security_configured"  # Override event name
    
    class Payload(ProtocolSecurityConfiguredEvent.Payload):
        tool_validation_enabled: bool = False  # Whether tool validation is enabled
        tool_validation_strictness: str = "moderate"  # Strictness level for tool validation (low, moderate, strict)
        resource_access_control_enabled: bool = False  # Whether resource access control is enabled
        resource_permission_scopes: List[str] = []  # Permission scopes for resource access
        capability_authorization_enabled: bool = False  # Whether capability-specific authorization is enabled
        capability_permissions: Dict[str, List[str]] = {}  # Permissions required for each capability
        mcp_specific_security_details: Dict[str, Any] = {}  # MCP-specific security details
```

**Example Usage:**
```python
# Example: Configuring MCP protocol security

def configure_mcp_protocol_security(config: Dict[str, Any]) -> bool:
    # Validate the configuration
    validation_result = configuration_system.validate_protocol_security_configuration("mcp", config)
    
    if not validation_result.is_valid:
        logger.error(f"Invalid MCP protocol security configuration: {validation_result.errors}")
        return False
    
    # Get protocol information
    protocol_info = protocol_registry.get_protocol_info("mcp")
    if not protocol_info:
        logger.error("MCP protocol not found in registry")
        return False
    
    protocol_version = protocol_info.get("version", "v1")
    
    # Extract configuration components
    authentication_config = config.get("authentication", {})
    authorization_config = config.get("authorization", {})
    encryption_config = config.get("encryption", {})
    rate_limiting_config = config.get("rate_limiting", {})
    tool_validation_config = config.get("tool_validation", {})
    resource_access_config = config.get("resource_access_control", {})
    capability_auth_config = config.get("capability_authorization", {})
    
    # Apply the configuration
    try:
        # Configure the MCP protocol security handler
        handler = security_system.get_protocol_security_handler("mcp")
        
        if not handler:
            logger.info("Creating new security handler for MCP protocol")
            handler = security_system.create_protocol_security_handler("mcp", protocol_version)
        
        if not handler:
            logger.error("Failed to create security handler for MCP protocol")
            return False
        
        # Configure authentication
        authentication_configured = "provider" in authentication_config
        authentication_provider = authentication_config.get("provider")
        authentication_required = authentication_config.get("required", True)
        
        if authentication_configured:
            auth_provider = security_system.authentication_service.get_provider(authentication_provider)
            handler.configure_authentication(auth_provider, authentication_required)
        
        # Configure authorization
        authorization_configured = "roles_allowed" in authorization_config
        allowed_roles = authorization_config.get("roles_allowed", [])
        default_role = authorization_config.get("default_role")
        
        if authorization_configured:
            handler.configure_authorization(allowed_roles, default_role)
        
        # Configure encryption
        encryption_configured = "enabled" in encryption_config
        encryption_enabled = encryption_config.get("enabled", False)
        encryption_algorithm = encryption_config.get("algorithm")
        
        if encryption_configured:
            if encryption_enabled:
                handler.configure_encryption(encryption_algorithm, encryption_config)
            else:
                handler.disable_encryption()
        
        # Configure rate limiting
        rate_limiting_configured = "requests_per_minute" in rate_limiting_config
        rate_limit = rate_limiting_config.get("requests_per_minute")
        
        if rate_limiting_configured:
            handler.configure_rate_limiting(rate_limit, rate_limiting_config)
        
        # Configure MCP-specific security features
        
        # Tool validation
        tool_validation_enabled = tool_validation_config.get("enabled", False)
        tool_validation_strictness = tool_validation_config.get("strictness", "moderate")
        
        if "enabled" in tool_validation_config:
            handler.configure_tool_validation(tool_validation_enabled, tool_validation_strictness, tool_validation_config)
        
        # Resource access control
        resource_access_control_enabled = resource_access_config.get("enabled", False)
        resource_permission_scopes = resource_access_config.get("permission_scopes", [])
        
        if "enabled" in resource_access_config:
            handler.configure_resource_access_control(resource_access_control_enabled, resource_permission_scopes, resource_access_config)
        
        # Capability authorization
        capability_authorization_enabled = capability_auth_config.get("enabled", False)
        capability_permissions = capability_auth_config.get("capability_permissions", {})
        
        if "enabled" in capability_auth_config:
            handler.configure_capability_authorization(capability_authorization_enabled, capability_permissions, capability_auth_config)
        
        # Emit MCP protocol security configured event
        configuration_id = f"mcp_security_{uuid.uuid4().hex[:8]}"
        configuration_time = datetime.now()
        
        event_system.emit(
            event_name="mcp_protocol_security_configured",
            payload=MCPProtocolSecurityConfiguredEvent.Payload(
                protocol_type="mcp",
                protocol_version=protocol_version,
                configuration_id=configuration_id,
                configuration_time=configuration_time,
                authentication_configured=authentication_configured,
                authorization_configured=authorization_configured,
                encryption_configured=encryption_configured,
                rate_limiting_configured=rate_limiting_configured,
                authentication_provider=authentication_provider,
                authentication_required=authentication_required,
                allowed_roles=allowed_roles,
                encryption_enabled=encryption_enabled,
                encryption_algorithm=encryption_algorithm,
                rate_limit=rate_limit,
                configuration_source="api",
                configuration_details=config,
                tool_validation_enabled=tool_validation_enabled,
                tool_validation_strictness=tool_validation_strictness,
                resource_access_control_enabled=resource_access_control_enabled,
                resource_permission_scopes=resource_permission_scopes,
                capability_authorization_enabled=capability_authorization_enabled,
                capability_permissions=capability_permissions,
                mcp_specific_security_details={
                    "tool_validation": tool_validation_config,
                    "resource_access_control": resource_access_config,
                    "capability_authorization": capability_auth_config
                }
            )
        )
        
        logger.info("MCP protocol security configuration applied successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error configuring MCP protocol security: {str(e)}")
        
        # Report the error
        error_reporting.report_error(
            error_type="mcp_protocol_security_configuration_failure",
            component="security_system",
            details={
                "protocol_version": protocol_version,
                "error_message": str(e),
                "configuration": config
            }
        )
        
        return False
```

### Security System → Configuration System

#### Methods/Functions
- `configuration_system.get_security_configuration() → SecurityConfig`
  - **Purpose**: Retrieve the current security configuration
  - **Parameters**: None
  - **Returns**: Current security configuration
  - **Example**:
    ```python
    config = configuration_system.get_security_configuration()
    ```

- `configuration_system.validate_security_configuration(config: SecurityConfig) → ValidationResult`
  - **Purpose**: Validate security configuration against schema
  - **Parameters**: Security configuration object
  - **Returns**: Validation result with any errors
  - **Example**:
    ```python
    result = configuration_system.validate_security_configuration(
        config=updated_security_config
    )
    ```

- `configuration_system.get_protocol_security_configuration(protocol_type: str) → ProtocolSecurityConfig`
  - **Purpose**: Retrieve security configuration for a specific protocol
  - **Parameters**: Protocol identifier
  - **Returns**: Protocol-specific security configuration
  - **Example**:
    ```python
    config = configuration_system.get_protocol_security_configuration(
        protocol_type="a2a"
    )
    ```

#### Events
- `security_configuration_requested`
  - **Purpose**: Notifies when security configuration is requested
  - **Payload**: Requester ID, configuration path
  - **Subscribers**: Configuration System audit log

- `security_configuration_validation_failed`
  - **Purpose**: Notifies when security configuration validation fails
  - **Payload**: Validation errors, configuration object
  - **Subscribers**: Configuration System error handler

## Data Flows

### Security System Initialization Flow
1. **Configuration System → Security System**: Configuration System provides security configuration
2. **Security System Processing**: Security System initializes components based on configuration
3. **Security System → Configuration System**: Security System validates configuration
4. **Security System → All Components**: Security System applies security policies to components

### Protocol Security Configuration Flow
1. **Configuration System → Security System**: Configuration System provides protocol-specific security config
2. **Security System Processing**: Security System configures protocol-specific security
3. **Security System → Protocol Layer**: Security System applies security to the protocol
4. **Protocol Layer → Security System**: Protocol Layer authenticates/authorizes using Security System

## Configuration Dependencies

The following configuration parameters affect this interaction:

```yaml
security:
  authentication:
    providers:
      - name: "oauth2"
        type: "oauth2"
        implementation_class: "OAuth2Provider"
        config:
          client_id: "${OAUTH_CLIENT_ID}"
          client_secret: "${OAUTH_CLIENT_SECRET}"
          token_url: "https://auth.example.com/token"
          auth_url: "https://auth.example.com/authorize"
          scopes: ["openmas.read", "openmas.write"]
      
      - name: "api_key"
        type: "api_key"
        implementation_class: "ApiKeyProvider"
        config:
          header_name: "X-API-Key"
          key_validation:
            method: "database"
            database_table: "api_keys"
    
    default_provider: "oauth2"
  
  authorization:
    method: "role_based"
    implementation_class: "RoleBasedAuthorization"
    roles:
      - name: "admin"
        permissions: ["*"]
      
      - name: "agent"
        permissions: ["agent.read", "agent.write", "message.send", "message.receive"]
      
      - name: "observer"
        permissions: ["agent.read", "message.read"]
    
    default_role: "observer"
  
  encryption:
    message_encryption:
      enabled: true
      algorithm: "AES-256-GCM"
      key_management: "vault"
    
    storage_encryption:
      enabled: true
      algorithm: "AES-256-GCM"
      key_management: "vault"
    
    key_providers:
      vault:
        implementation_class: "VaultKeyProvider"
        config:
          url: "https://vault.example.com"
          token_env: "VAULT_TOKEN"
          key_path: "secret/openmas/keys"
  
  rate_limiting:
    enabled: true
    implementation_class: "TokenBucketRateLimiter"
    global_limits:
      requests_per_minute: 1000
    per_client_limits:
      requests_per_minute: 100
    per_endpoint_limits:
      "/api/agents":
        requests_per_minute: 200
      "/api/messages":
        requests_per_minute: 500
  
  protocol_security:
    a2a:
      authentication:
        provider: "oauth2"
        required: true
      authorization:
        roles_allowed: ["agent", "admin"]
        default_role: "agent"
      message_encryption:
        enabled: true
        algorithm: "AES-256-GCM"
      rate_limiting:
        requests_per_minute: 200
    
    mcp:
      authentication:
        provider: "api_key"
        required: true
      authorization:
        roles_allowed: ["agent", "admin"]
        default_role: "agent"
      message_encryption:
        enabled: true
        algorithm: "AES-256-GCM"
      rate_limiting:
        requests_per_minute: 200
```

## Error Handling

1. **Security Configuration Errors**:
   - Strict validation of security configuration to prevent insecure settings
   - Rejection of configuration that could compromise security
   - Detailed security audit logs for configuration changes

2. **Authentication/Authorization Failures**:
   - Comprehensive logging of authentication failures with context
   - Rate limiting of failed authentication attempts
   - Configurable policies for account locking after repeated failures

3. **Encryption Errors**:
   - Secure handling of encryption failures to prevent data leakage
   - Key rotation mechanisms for compromised keys
   - Backup procedures for key recovery

## Extension Points

1. **Authentication Providers**:
   - Custom authentication mechanisms can be implemented
   - AuthenticationProvider interface:
     ```python
     class AuthenticationProvider:
         def initialize(self, config: Dict[str, Any]) → bool:
             # Initialize provider with configuration
             pass
         
         def authenticate(self, credentials: Dict[str, Any]) → AuthResult:
             # Authenticate using provided credentials
             pass
             
         def validate_token(self, token: str) → TokenValidationResult:
             # Validate authentication token
             pass
     ```

2. **Encryption Providers**:
   - Custom encryption implementations can be added
   - Example custom encryption provider:
     ```yaml
     security:
       encryption:
         key_providers:
           custom_hsm:
             implementation_class: "HSMKeyProvider"
             config:
               hsm_url: "https://hsm.example.com"
               client_certificate: "${HSM_CLIENT_CERT}"
               client_key: "${HSM_CLIENT_KEY}"
     ```

## Notes on Multi-Protocol Design

The Configuration System ↔ Security System interface supports OpenMAS's multi-protocol design by:

- Providing protocol-specific security configurations
- Supporting different authentication mechanisms for different protocols
- Ensuring consistent authorization across protocol boundaries
- Maintaining protocol-specific rate limiting and encryption settings

This enables secure multi-protocol communication while adapting to the security requirements of each protocol.

## Notes on A2A and MCP Protocol Support

The security configuration specifically addresses both Google's A2A protocol and the Model Context Protocol (MCP):

### A2A Protocol Security

```yaml
protocol_security:
  a2a:
    authentication:
      provider: "oauth2"
      required: true
    authorization:
      roles_allowed: ["agent", "admin"]
      default_role: "agent"
    message_encryption:
      enabled: true
      algorithm: "AES-256-GCM"
    agent_card_validation:
      enabled: true
      validation_level: "strict"  # strict, lenient, none
    rate_limiting:
      requests_per_minute: 200
```

### MCP Protocol Security

```yaml
protocol_security:
  mcp:
    authentication:
      provider: "api_key"
      required: true
    authorization:
      roles_allowed: ["agent", "admin"]
      default_role: "agent"
    message_encryption:
      enabled: true
      algorithm: "AES-256-GCM"
    server_validation:
      enabled: true
      validation_level: "strict"  # strict, lenient, none
    rate_limiting:
      requests_per_minute: 200
```

Both protocol configurations provide appropriate security measures while accounting for protocol-specific requirements.

## Notes on Reasoning Agnosticism

The Security System configuration supports OpenMAS's reasoning agnostic architecture by:

- Separating security concerns for communication components from reasoning components
- Providing authorization mechanisms that can restrict access to different reasoning capabilities
- Supporting secure interaction between different reasoning approaches
- Enabling encryption of sensitive reasoning data while maintaining the "body-brain" separation

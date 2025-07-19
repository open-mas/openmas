# Agent Framework ↔ Security System

## Relationship Summary
- **Security System → Agent Framework**: Provides authentication and authorization services for incoming requests
- **Agent Framework → Security System**: Mediates security context propagation to reasoning engines via the Reasoning Security Interface (RSI)

## Interface Definitions

### Security System → Agent Framework

#### Methods/Functions

```python
def authenticate_request(request: ProtocolRequest, auth_context: Optional[AuthContext] = None) -> AuthenticationResult:
    """
    Authenticates an incoming request from the Protocol Layer.
    
    Args:
        request: ProtocolRequest - Protocol-specific request object containing authentication credentials
        auth_context: Optional[AuthContext] - Additional context for authentication decisions
        
    Returns:
        AuthenticationResult - Authentication result containing principal information and status
        
    Raises:
        InvalidCredentialsError - If the credentials are invalid
        AuthenticationMechanismError - If there's an error with the authentication mechanism
        MalformedRequestError - If the request format is invalid
    """
```

**Data Structures:**

```python
class ProtocolRequest:
    """
    Protocol-specific request object.
    """
    protocol_type: ProtocolType  # Type of protocol (A2A, MCP, etc.)
    raw_request: Any  # Raw protocol-specific request data
    headers: Dict[str, str] = {}  # Protocol headers or metadata
    credentials: Optional[Dict[str, Any]] = None  # Authentication credentials
    request_id: str  # Unique identifier for the request
    timestamp: datetime = datetime.now()  # When the request was received
    source_address: Optional[str] = None  # Source address of the request
    target_agent_id: Optional[str] = None  # Target agent ID if known
    metadata: Dict[str, Any] = {}  # Additional metadata about the request

class AuthContext:
    """
    Additional context for authentication decisions.
    """
    session_id: Optional[str] = None  # ID of an existing session, if any
    previous_auth_result: Optional[AuthenticationResult] = None  # Result of a previous authentication
    auth_mechanism_override: Optional[str] = None  # Override the default authentication mechanism
    environment_info: Dict[str, Any] = {}  # Information about the execution environment
    security_level: str = "standard"  # Security level for this authentication
    trace_context: Optional[Dict[str, Any]] = None  # Distributed tracing context

class AuthenticationResult:
    """
    Result of an authentication attempt.
    """
    is_authenticated: bool  # Whether the authentication was successful
    principal_info: Optional[SecurityPrincipalInfo] = None  # Information about the authenticated principal
    auth_mechanism_used: str  # Authentication mechanism that was used
    auth_timestamp: datetime = datetime.now()  # When the authentication was performed
    auth_token: Optional[str] = None  # Authentication token, if generated
    token_expiration: Optional[datetime] = None  # Expiration time of the auth token
    error_message: Optional[str] = None  # Error message if authentication failed
    error_code: Optional[str] = None  # Error code if authentication failed
    session_id: Optional[str] = None  # Session ID if a session was created
    metadata: Dict[str, Any] = {}  # Additional metadata about the authentication

class SecurityPrincipalInfo:
    """
    Information about an authenticated security principal.
    """
    id: str  # Unique identifier for the principal
    type: str  # Type of principal (user, agent, system, etc.)
    name: Optional[str] = None  # Name of the principal
    roles: List[str] = []  # Roles assigned to the principal
    permissions: List[str] = []  # Permissions granted to the principal
    attributes: Dict[str, Any] = {}  # Additional attributes of the principal
    authentication_level: str = "standard"  # Level of authentication (standard, mfa, etc.)
    tenant_id: Optional[str] = None  # ID of the tenant the principal belongs to
    issuer: Optional[str] = None  # Issuer of the principal's identity
    created_at: Optional[datetime] = None  # When the principal was created
```

**Example Usage:**
```python
auth_result = security_system.authenticate_request(
    request=ProtocolRequest(
        protocol_type=ProtocolType.MCP_SSE,
        raw_request=mcp_request_data,
        headers={
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "Content-Type": "application/json"
        },
        request_id="req-123",
        source_address="192.168.1.1",
        target_agent_id="assistant_agent"
    ),
    auth_context=AuthContext(
        session_id="session-456",
        security_level="high",
        environment_info={
            "deployment_environment": "production",
            "region": "us-west"
        }
    )
)

if auth_result.is_authenticated:
    principal_info = auth_result.principal_info
    # Proceed with processing using the authenticated principal information
    print(f"Authenticated principal: {principal_info.id}, roles: {principal_info.roles}")
    # Store auth token for future requests if provided
    if auth_result.auth_token:
        token_storage.store(auth_result.auth_token, expiration=auth_result.token_expiration)
    # Initialize a session if one was created
    if auth_result.session_id:
        session_manager.initialize_session(auth_result.session_id, principal_info)
        
else:
    # Handle authentication failure
    error_message = auth_result.error_message or "Authentication failed"
    error_code = auth_result.error_code or "UNKNOWN_ERROR"
    print(f"Authentication failed: {error_message} (code: {error_code})")
    # Respond with appropriate error
    response = create_error_response(error_code, error_message)
```

```python
def authorize_agent_access(principal_info: SecurityPrincipalInfo, agent_id: str, 
                           access_context: Optional[AccessContext] = None) -> AuthorizationResult:
    """
    Authorizes access to a specific agent by the authenticated principal.
    
    Args:
        principal_info: SecurityPrincipalInfo - Information about the authenticated principal
        agent_id: str - Identifier of the agent being accessed
        access_context: Optional[AccessContext] - Additional context for authorization decisions
        
    Returns:
        AuthorizationResult - Authorization result indicating whether access is allowed
        
    Raises:
        UnknownAgentError - If the agent doesn't exist
        InvalidPrincipalError - If the principal information is invalid
        AuthorizationError - If the authorization process fails
    """
```

**Data Structures:**

```python
class AccessContext:
    """
    Additional context for authorization decisions.
    """
    operation_type: str = "access"  # Type of operation being performed
    session_id: Optional[str] = None  # ID of the current session, if any
    request_id: Optional[str] = None  # ID of the request being authorized
    protocol_type: Optional[ProtocolType] = None  # Protocol being used
    source_address: Optional[str] = None  # Source address of the request
    timestamp: datetime = datetime.now()  # When the access is being requested
    trace_context: Optional[Dict[str, Any]] = None  # Distributed tracing context
    security_level: str = "standard"  # Security level for this authorization
    environment_info: Dict[str, Any] = {}  # Information about the execution environment
    attributes: Dict[str, Any] = {}  # Additional attributes relevant to the access

class AuthorizationResult:
    """
    Result of an authorization decision.
    """
    is_authorized: bool  # Whether the access is authorized
    decision_id: str  # Unique identifier for the authorization decision
    principal_id: str  # ID of the principal that was authorized
    resource_id: str  # ID of the resource that was accessed
    permission: str  # Permission that was checked
    decision_timestamp: datetime = datetime.now()  # When the decision was made
    decision_reason: Optional[str] = None  # Reason for the decision
    decision_factors: List[str] = []  # Factors that influenced the decision
    constraints: Optional[Dict[str, Any]] = None  # Constraints on the authorized access
    expiration: Optional[datetime] = None  # When the authorization expires
    audit_record: Optional[Dict[str, Any]] = None  # Audit information for the decision
    metadata: Dict[str, Any] = {}  # Additional metadata about the authorization
```

**Example Usage:**
```python
auth_result = security_system.authorize_agent_access(
    principal_info=SecurityPrincipalInfo(
        id="user-123",
        type="user",
        roles=["standard_user"],
        permissions=["access_support_agents"],
        authentication_level="standard",
        tenant_id="tenant-456"
    ),
    agent_id="customer_support_agent",
    access_context=AccessContext(
        operation_type="invoke",
        session_id="session-789",
        protocol_type=ProtocolType.A2A_HTTP,
        source_address="192.168.1.1",
        security_level="standard",
        environment_info={
            "deployment_environment": "production",
            "region": "us-west"
        }
    )
)

if auth_result.is_authorized:
    # Proceed with agent invocation
    print(f"Access to agent {agent_id} authorized for {principal_info.id}")
    if auth_result.constraints:
        # Apply any constraints to the invocation
        apply_access_constraints(auth_result.constraints)
        
else:
    # Handle authorization failure
    reason = auth_result.decision_reason or "Access denied"
    print(f"Access denied: {reason}")
    # Respond with appropriate error
    response = create_access_denied_response(reason, auth_result.decision_id)
```

```python
def authorize_capability_invocation(principal_info: SecurityPrincipalInfo, agent_id: str, capability_id: str,
                                   capability_params: Optional[Dict[str, Any]] = None,
                                   access_context: Optional[AccessContext] = None) -> AuthorizationResult:
    """
    Authorizes invocation of a specific agent capability by the authenticated principal.
    
    Args:
        principal_info: SecurityPrincipalInfo - Information about the authenticated principal
        agent_id: str - Identifier of the agent being accessed
        capability_id: str - Identifier of the capability being invoked
        capability_params: Optional[Dict[str, Any]] - Parameters for the capability invocation
        access_context: Optional[AccessContext] - Additional context for authorization decisions
        
    Returns:
        AuthorizationResult - Authorization result indicating whether the capability invocation is allowed
        
    Raises:
        UnknownAgentError - If the agent doesn't exist
        UnknownCapabilityError - If the capability doesn't exist
        InvalidPrincipalError - If the principal information is invalid
        AuthorizationError - If the authorization process fails
    """
```

**Example Usage:**
```python
auth_result = security_system.authorize_capability_invocation(
    principal_info=SecurityPrincipalInfo(
        id="user-123",
        type="user",
        roles=["customer_service_rep"],
        permissions=["view_customer_data", "modify_customer_data"],
        authentication_level="mfa",
        tenant_id="tenant-456"
    ),
    agent_id="customer_support_agent",
    capability_id="access_customer_data",
    capability_params={
        "customer_id": "cust-789",
        "data_fields": ["name", "email", "account_status"],
        "purpose": "support_ticket_resolution"
    },
    access_context=AccessContext(
        operation_type="capability_invoke",
        session_id="session-789",
        protocol_type=ProtocolType.A2A_HTTP,
        security_level="high",
        attributes={
            "support_ticket_id": "ticket-123",
            "customer_consent": True
        }
    )
)

if auth_result.is_authorized:
    # Proceed with capability invocation
    print(f"Capability {capability_id} invocation authorized for {principal_info.id}")
    # Apply any constraints to the invocation
    if auth_result.constraints:
        filtered_params = apply_capability_constraints(
            capability_params, 
            auth_result.constraints
        )
        invoke_capability(agent_id, capability_id, filtered_params)
    else:
        invoke_capability(agent_id, capability_id, capability_params)
        
else:
    # Handle authorization failure
    reason = auth_result.decision_reason or "Capability invocation denied"
    print(f"Capability invocation denied: {reason}")
    # Log the denial for audit purposes
    security_audit_log.log_denial(
        principal_id=principal_info.id,
        resource_id=f"{agent_id}/{capability_id}",
        reason=reason,
        decision_id=auth_result.decision_id
    )
    # Respond with appropriate error
    response = create_capability_denied_response(reason, auth_result.decision_id)
```

#### Events

```python
class AuthenticationCompletedEvent:
    """
    Event fired when authentication is completed for a request.
    """
    authentication_id: str  # Unique identifier for the authentication operation
    request_id: str  # ID of the request that was authenticated
    is_authenticated: bool  # Whether authentication was successful
    principal_id: Optional[str] = None  # ID of the authenticated principal, if successful
    principal_type: Optional[str] = None  # Type of the principal, if successful
    auth_mechanism: str  # Authentication mechanism that was used
    auth_level: str  # Level of authentication (standard, mfa, etc.)
    protocol_type: ProtocolType  # Protocol type for the authentication
    timestamp: datetime = datetime.now()  # When authentication was completed
    duration_ms: int = 0  # Time taken for authentication in milliseconds
    error_code: Optional[str] = None  # Error code if authentication failed
    session_id: Optional[str] = None  # Session ID if a session was created/used
    security_tokens: Dict[str, str] = {}  # Security tokens issued during authentication
    metadata: Dict[str, Any] = {}  # Additional metadata about the authentication

class AuthorizationCompletedEvent:
    """
    Event fired when authorization is completed for an agent or capability access.
    """
    authorization_id: str  # Unique identifier for the authorization operation
    principal_id: str  # ID of the principal that was authorized
    resource_type: str  # Type of resource (agent, capability, etc.)
    resource_id: str  # ID of the resource that was accessed
    is_authorized: bool  # Whether the access was authorized
    permission: str  # Permission that was checked
    action: str  # Action that was authorized (access, invoke, etc.)
    agent_id: Optional[str] = None  # ID of the agent, if applicable
    capability_id: Optional[str] = None  # ID of the capability, if applicable
    timestamp: datetime = datetime.now()  # When authorization was completed
    duration_ms: int = 0  # Time taken for authorization in milliseconds
    decision_factors: List[str] = []  # Factors that influenced the decision
    constraints_applied: Optional[Dict[str, Any]] = None  # Constraints that were applied
    metadata: Dict[str, Any] = {}  # Additional metadata about the authorization
```

**Subscribers:**
- `AuthenticationCompletedEvent`: Agent lifecycle manager, observability system, session management, security audit log
- `AuthorizationCompletedEvent`: Agent lifecycle manager, observability system, security audit log, permission caching

### Agent Framework → Security System (RSI Implementation)

#### Methods/Functions

```python
def create_reasoning_security_interface(principal_info: SecurityPrincipalInfo, 
                                          rsi_config: Optional[RSIConfig] = None) -> ReasoningSecurityInterface:
    """
    Creates a Reasoning Security Interface (RSI) implementation for a specific authenticated principal.
    
    Args:
        principal_info: SecurityPrincipalInfo - Information about the authenticated principal
        rsi_config: Optional[RSIConfig] - Configuration for the RSI implementation
        
    Returns:
        ReasoningSecurityInterface - Implementation of the RSI that can be passed to the reasoning engine
        
    Raises:
        InvalidPrincipalError - If the principal information is invalid
        RSICreationError - If the RSI cannot be created
    """
```

**Data Structures:**

```python
class RSIConfig:
    """
    Configuration for a Reasoning Security Interface implementation.
    """
    security_level: str = "standard"  # Security level for the RSI
    permission_caching: bool = True  # Whether to cache permission check results
    cache_ttl_seconds: int = 300  # Time to live for cached permissions
    detailed_audit: bool = False  # Whether to enable detailed audit logging
    max_auth_cache_size: int = 1000  # Maximum size of the authorization cache
    reasoning_approach: Optional[str] = None  # Specific reasoning approach for specialized RSI implementation
    context_binding: Dict[str, Any] = {}  # Additional context to bind to the RSI
    permission_strategy: str = "default"  # Strategy for permission checks (default, strict, permissive)
    metadata: Dict[str, Any] = {}  # Additional metadata for the RSI

class ReasoningSecurityInterface(Protocol):
    """
    Interface for security operations within reasoning engines.
    Allows reasoning engines to access security principal information and perform permission checks.
    """
    
    def get_current_principal(self) -> SecurityPrincipalInfo:
        """
        Get information about the current authenticated principal.
        
        Returns:
            SecurityPrincipalInfo - Information about the authenticated principal
        """
        pass
    
    def check_permission(self, action: str, resource_identifier: str, 
                         context: Optional[Dict[str, Any]] = None) -> AuthZResult:
        """
        Check if the current principal has permission to perform an action on a resource.
        
        Args:
            action: str - The action to check permission for
            resource_identifier: str - Identifier for the resource
            context: Optional[Dict[str, Any]] - Additional context for the permission check
            
        Returns:
            AuthZResult - Result of the permission check
            
        Raises:
            PermissionCheckError - If the permission check fails
        """
        pass
    
    def get_security_context(self) -> Dict[str, Any]:
        """
        Get the current security context.
        
        Returns:
            Dict[str, Any] - The current security context
        """
        pass
    
    def generate_secure_token(self, token_type: str, expiration_seconds: int = 3600, 
                              claims: Optional[Dict[str, Any]] = None) -> SecureToken:
        """
        Generate a secure token for use in further operations.
        
        Args:
            token_type: str - Type of token to generate
            expiration_seconds: int - Token expiration time in seconds
            claims: Optional[Dict[str, Any]] - Claims to include in the token
            
        Returns:
            SecureToken - The generated token
            
        Raises:
            TokenGenerationError - If the token generation fails
        """
        pass

class AuthZResult:
    """
    Result of a permission check.
    """
    allowed: bool  # Whether the permission is granted
    decision_id: str  # Unique identifier for the decision
    principal_id: str  # ID of the principal
    action: str  # Action that was checked
    resource: str  # Resource that was checked
    reason: Optional[str] = None  # Reason for the decision
    constraints: Optional[Dict[str, Any]] = None  # Constraints on the permission
    timestamp: datetime = datetime.now()  # When the check was performed
    expiration: Optional[datetime] = None  # When the decision expires
    metadata: Dict[str, Any] = {}  # Additional metadata about the decision

class SecureToken:
    """
    A secure token for use in security operations.
    """
    token_id: str  # Unique identifier for the token
    token_value: str  # The actual token value
    token_type: str  # Type of token
    issued_at: datetime = datetime.now()  # When the token was issued
    expires_at: datetime  # When the token expires
    issuer: str  # Issuer of the token
    claims: Dict[str, Any] = {}  # Claims included in the token
    metadata: Dict[str, Any] = {}  # Additional metadata about the token
```

**Example Usage:**
```python
# Agent Framework creates an RSI for the reasoning engine
rsi = security_system.create_reasoning_security_interface(
    principal_info=SecurityPrincipalInfo(
        id="user-123",
        type="user",
        roles=["premium_user"],
        permissions=["access_knowledge_base", "invoke_reasoning"],
        authentication_level="standard",
        attributes={
            "subscription_level": "premium",
            "usage_quota": {"daily_limit": 100, "used_today": 45}
        }
    ),
    rsi_config=RSIConfig(
        security_level="high",
        permission_caching=True,
        detailed_audit=True,
        reasoning_approach="llm",
        permission_strategy="strict"
    )
)

# Pass RSI to reasoning engine during initialization
reasoning_engine.initialize(
    config=agent_config.reasoning,
    knowledge_client=knowledge_client,
    reasoning_security_interface=rsi
)

# The reasoning engine can then use the RSI during processing
def process_message(self, message, context):
    # Access security principal information
    principal = self.rsi.get_current_principal()
    print(f"Processing message for {principal.id} with roles: {principal.roles}")
    
    # Check permission to access knowledge base
    kb_permission = self.rsi.check_permission(
        action="query",
        resource_identifier="knowledge_base:customer_data",
        context={"purpose": "answer_user_query", "query_type": "sensitive"}
    )
    
    if kb_permission.allowed:
        # Access knowledge base with any constraints
        constraints = kb_permission.constraints or {}
        result = self.query_knowledge_base("customer_data", message.content, constraints)
        # Generate secure token for result if needed
        if requires_secure_access(result):
            token = self.rsi.generate_secure_token(
                token_type="data_access",
                expiration_seconds=300,
                claims={"data_type": "customer_data", "access_level": "read"}
            )
            return create_secured_response(result, token)
        return create_response(result)
    else:
        # Handle permission denial
        return create_permission_denied_response(kb_permission.reason)
```

#### RSI Implementation

The Security System provides an implementation of the Reasoning Security Interface (RSI) which allows reasoning engines to interact with the security system:

```python
class ReasoningSecurityInterfaceImpl(ReasoningSecurityInterface):
    """
    Implementation of the Reasoning Security Interface provided by the Security System.
    """
    
    def __init__(self, principal_info: SecurityPrincipalInfo, security_system: SecuritySystem,
                 config: RSIConfig = RSIConfig()):
        """
        Initialize the RSI implementation.
        
        Args:
            principal_info: SecurityPrincipalInfo - Information about the authenticated principal
            security_system: SecuritySystem - Reference to the security system
            config: RSIConfig - Configuration for the RSI implementation
        """
        self._principal_info = principal_info
        self._security_system = security_system
        self._config = config
        self._context = {}
        self._permission_cache = {} if config.permission_caching else None
        self._created_at = datetime.now()
        self._request_count = 0
        
    def get_current_principal(self) -> SecurityPrincipalInfo:
        """
        Get information about the current authenticated principal.
        
        Returns:
            SecurityPrincipalInfo - Information about the authenticated principal
        """
        # Log access if detailed audit is enabled
        if self._config.detailed_audit:
            self._log_principal_access()
        
        # Return the principal information
        return self._principal_info
    
    def check_permission(self, action: str, resource_identifier: str, 
                        context: Optional[Dict[str, Any]] = None) -> AuthZResult:
        """
        Check if the current principal has permission to perform an action on a resource.
        
        Args:
            action: str - The action to check permission for
            resource_identifier: str - Identifier for the resource
            context: Optional[Dict[str, Any]] - Additional context for the permission check
            
        Returns:
            AuthZResult - Result of the permission check
            
        Raises:
            PermissionCheckError - If the permission check fails
        """
        # Check cache if enabled
        if self._permission_cache is not None:
            cache_key = self._generate_cache_key(action, resource_identifier, context)
            cached_result = self._permission_cache.get(cache_key)
            if cached_result and not self._is_cache_expired(cached_result):
                return cached_result
        
        # Perform the permission check
        result = self._security_system.check_permission(
            principal=self._principal_info,
            action=action,
            resource=resource_identifier,
            context=context or {},
            security_level=self._config.security_level,
            strategy=self._config.permission_strategy
        )
        
        # Update cache if enabled
        if self._permission_cache is not None:
            if len(self._permission_cache) >= self._config.max_auth_cache_size:
                # Evict oldest entry if cache is full
                self._evict_oldest_cache_entry()
            cache_key = self._generate_cache_key(action, resource_identifier, context)
            self._permission_cache[cache_key] = result
        
        # Track request
        self._request_count += 1
        
        # Return the result
        return result
    
    def get_security_context(self) -> Dict[str, Any]:
        """
        Get the current security context.
        
        Returns:
            Dict[str, Any] - The current security context
        """
        context = {
            "principal_id": self._principal_info.id,
            "principal_type": self._principal_info.type,
            "security_level": self._config.security_level,
            "authentication_level": self._principal_info.authentication_level,
            "roles": self._principal_info.roles,
            **self._config.context_binding
        }
        return context
    
    def generate_secure_token(self, token_type: str, expiration_seconds: int = 3600, 
                            claims: Optional[Dict[str, Any]] = None) -> SecureToken:
        """
        Generate a secure token for use in further operations.
        
        Args:
            token_type: str - Type of token to generate
            expiration_seconds: int - Token expiration time in seconds
            claims: Optional[Dict[str, Any]] - Claims to include in the token
            
        Returns:
            SecureToken - The generated token
            
        Raises:
            TokenGenerationError - If the token generation fails
        """
        # Merge claims with principal information
        merged_claims = {
            "sub": self._principal_info.id,
            "type": token_type,
            "roles": self._principal_info.roles,
            **self._config.context_binding,
            **(claims or {})
        }
        
        # Generate the token
        return self._security_system.generate_token(
            token_type=token_type,
            expiration_seconds=expiration_seconds,
            claims=merged_claims,
            issuer=f"rsi:{self._principal_info.id}"
        )
    
    # Private helper methods
    def _generate_cache_key(self, action: str, resource: str, context: Optional[Dict] = None) -> str:
        """Generate a cache key for permission checks."""
        ctx_str = ""
        if context:
            # Sort context keys for consistent cache keys
            ctx_str = json.dumps(context, sort_keys=True)
        return f"{action}:{resource}:{ctx_str}"
    
    def _is_cache_expired(self, result: AuthZResult) -> bool:
        """Check if a cached result has expired."""
        if result.expiration and result.expiration <= datetime.now():
            return True
        cache_age = (datetime.now() - result.timestamp).total_seconds()
        return cache_age > self._config.cache_ttl_seconds
    
    def _evict_oldest_cache_entry(self) -> None:
        """Evict the oldest entry from the permission cache."""
        if not self._permission_cache:
            return
        oldest_key = min(self._permission_cache.keys(), 
                        key=lambda k: self._permission_cache[k].timestamp)
        del self._permission_cache[oldest_key]
    
    def _log_principal_access(self) -> None:
        """Log access to principal information for audit purposes."""
        self._security_system.log_audit_event(
            event_type="rsi_principal_access",
            principal_id=self._principal_info.id,
            resource=None,
            action="get_principal_info",
            success=True,
            context={
                "rsi_instance_id": id(self),
                "request_count": self._request_count
            }
        )
```

#### Events

```python
class RSICreatedEvent:
    """
    Event fired when a Reasoning Security Interface (RSI) is created for a reasoning engine.
    """
    rsi_id: str  # Unique identifier for the RSI instance
    principal_id: str  # ID of the principal the RSI is created for
    principal_type: str  # Type of principal
    agent_id: str  # ID of the agent using the RSI
    reasoning_approach: str  # Reasoning approach for the RSI
    security_level: str  # Security level configured for the RSI
    permission_caching_enabled: bool  # Whether permission caching is enabled
    timestamp: datetime = datetime.now()  # When the RSI was created
    session_id: Optional[str] = None  # ID of the session, if applicable
    rsi_config_hash: str  # Hash of the RSI configuration for tracking
    metadata: Dict[str, Any] = {}  # Additional metadata about the RSI creation
    
    class Payload:
        """
        Payload containing details of the RSI creation event.
        """
        rsi_id: str  # Unique identifier for the RSI instance
        creation_details: Dict[str, Any] = {  # Details about the RSI creation
            "timestamp": None,  # ISO-8601 timestamp of when the RSI was created
            "principal_id": "",  # ID of the principal the RSI is created for
            "principal_type": "",  # Type of principal (user, agent, system, etc.)
            "agent_id": "",  # ID of the agent using the RSI
            "session_id": None  # ID of the session, if applicable
        }
        configuration: Dict[str, Any] = {  # Configuration of the RSI
            "reasoning_approach": "",  # Reasoning approach the RSI is configured for
            "security_level": "",  # Security level (standard, elevated, etc.)
            "permission_caching_enabled": False,  # Whether permission caching is enabled
            "config_hash": ""  # Hash of the complete RSI configuration
        }
        principal_details: Dict[str, Any] = {  # Details about the security principal
            "roles": [],  # Roles assigned to the principal
            "permissions": [],  # Direct permissions granted to the principal
            "attributes": {}  # Additional attributes of the principal
        }
        context: Dict[str, Any] = {}  # Additional context information

class RSIPermissionCheckEvent:
    """
    Event fired when a permission check is performed via the RSI.
    """
    check_id: str  # Unique identifier for the permission check
    principal_id: str  # ID of the principal
    action: str  # Action being checked
    resource: str  # Resource being accessed
    is_allowed: bool  # Whether the permission is granted
    reason: Optional[str] = None  # Reason for the decision
    agent_id: str  # ID of the agent performing the check
    rsi_id: str  # ID of the RSI instance
    timestamp: datetime = datetime.now()  # When the check was performed
    context_summary: Dict[str, Any] = {}  # Summary of the check context
    from_cache: bool = False  # Whether the result was from cache
    duration_ms: int = 0  # Time taken for the check in milliseconds
    constraints_applied: Optional[Dict[str, Any]] = None  # Constraints applied to the permission
    metadata: Dict[str, Any] = {}  # Additional metadata about the check
    
    class Payload:
        """
        Payload containing details of the RSI permission check event.
        """
        check_id: str  # Unique identifier for the permission check
        permission_details: Dict[str, Any] = {  # Details about the permission check
            "principal_id": "",  # ID of the principal
            "action": "",  # Action being checked (e.g., "read", "write", "execute")
            "resource": "",  # Resource being accessed (e.g., "document:123")
            "is_allowed": False,  # Whether the permission is granted
            "reason": None,  # Reason for the decision
            "timestamp": None  # ISO-8601 timestamp of when the check was performed
        }
        performance_metrics: Dict[str, Any] = {  # Performance metrics for the check
            "duration_ms": 0,  # Time taken for the check in milliseconds
            "from_cache": False,  # Whether the result was from cache
            "cache_key": None  # Cache key used, if applicable
        }
        context: Dict[str, Any] = {  # Context for the permission check
            "agent_id": "",  # ID of the agent performing the check
            "rsi_id": "",  # ID of the RSI instance
            "reasoning_approach": "",  # Reasoning approach associated with the check
            "session_id": None,  # ID of the session, if applicable
            "invocation_point": None,  # Point in code where the check was invoked
            "constraints_applied": None  # Constraints applied to the permission
        }
```

**Subscribers:**
- `RSICreatedEvent`: Observability system, security administration interface, RSI lifecycle manager
- `RSIPermissionCheckEvent`: Observability system, security audit log, permission analytics system, anomaly detection

**Example: Handling RSI Creation**

```python
# Example: Subscribing to RSICreatedEvent in the Security Administration Interface
@event_bus.subscribe(RSICreatedEvent)
def handle_rsi_created(event: RSICreatedEvent):
    # Log the RSI creation
    logger.info(
        f"RSI created for agent {event.agent_id} with principal {event.principal_id} "
        f"using {event.reasoning_approach} reasoning approach"
    )
    
    # Register the RSI in the security administration interface
    admin_interface.register_active_rsi(
        rsi_id=event.rsi_id,
        agent_id=event.agent_id,
        principal_id=event.principal_id,
        principal_type=event.principal_type,
        reasoning_approach=event.reasoning_approach,
        security_level=event.security_level,
        session_id=event.session_id
    )
    
    # Store the configuration hash for integrity verification
    rsi_integrity_checker.store_config_hash(
        rsi_id=event.rsi_id,
        config_hash=event.rsi_config_hash
    )
    
    # If this is a BDI reasoning approach, apply additional security monitoring
    if event.reasoning_approach == "bdi":
        bdi_security_monitor.monitor_rsi(
            rsi_id=event.rsi_id,
            agent_id=event.agent_id,
            principal_id=event.principal_id
        )
        logger.debug(f"Applied BDI-specific security monitoring to RSI {event.rsi_id}")
    
    # If this is an LLM-based reasoning approach, apply content filtering
    elif event.reasoning_approach == "llm":
        llm_content_filter.configure_for_rsi(
            rsi_id=event.rsi_id,
            security_level=event.security_level,
            principal_type=event.principal_type
        )
        logger.debug(f"Applied LLM-specific content filtering to RSI {event.rsi_id}")
```

**Example: Handling Permission Checks**

```python
# Example: Subscribing to RSIPermissionCheckEvent in the Security Audit System
@event_bus.subscribe(RSIPermissionCheckEvent)
def handle_permission_check(event: RSIPermissionCheckEvent):
    # Log the permission check for auditing
    audit_logger.info(
        f"Permission check: Principal {event.principal_id} attempting {event.action} "
        f"on {event.resource}. Result: {'ALLOWED' if event.is_allowed else 'DENIED'}"
    )
    
    # Record detailed audit entry
    security_audit_system.record_permission_check(
        check_id=event.check_id,
        principal_id=event.principal_id,
        action=event.action,
        resource=event.resource,
        is_allowed=event.is_allowed,
        reason=event.reason,
        agent_id=event.agent_id,
        rsi_id=event.rsi_id,
        timestamp=event.timestamp,
        context=event.context_summary,
        from_cache=event.from_cache,
        duration_ms=event.duration_ms
    )
    
    # Detect and respond to potential security anomalies
    if anomaly_detector.is_anomalous(event):
        security_response_system.trigger_investigation(
            check_id=event.check_id,
            principal_id=event.principal_id,
            action=event.action,
            resource=event.resource,
            agent_id=event.agent_id,
            context=event.context_summary
        )
        logger.warning(f"Security anomaly detected for permission check {event.check_id}")
    
    # Update permission analytics
    analytics_system.update_permission_metrics(
        principal_id=event.principal_id,
        action=event.action,
        resource_type=event.resource.split(':')[0] if ':' in event.resource else event.resource,
        is_allowed=event.is_allowed,
        from_cache=event.from_cache,
        duration_ms=event.duration_ms
    )
```

## Data Flows

### Authentication Flow
```
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│ Protocol Layer│         │Agent Framework │         │Security System│
└───────┬───────┘         └───────┬───────┘         └───────┬───────┘
        │                         │                         │
        │ Incoming Request        │                         │
        │ (with auth credentials) │                         │
        │─────────────────────────>                         │
        │                         │                         │
        │                         │ authenticate_request()  │
        │                         │────────────────────────>│
        │                         │                         │
        │                         │ AuthenticationResult    │
        │                         │ (SecurityPrincipalInfo) │
        │                         │<────────────────────────│
        │                         │                         │
        │                         │ authorize_agent_access()│
        │                         │────────────────────────>│
        │                         │                         │
        │                         │ AuthorizationResult     │
        │                         │<────────────────────────│
        │                         │                         │
```

### Reasoning Security Interface (RSI) Flow
```
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│Agent Framework │         │ReasoningEngine│         │Security System│
└───────┬───────┘         └───────┬───────┘         └───────┬───────┘
        │                         │                         │
        │ create_reasoning_       │                         │
        │ security_interface()    │                         │
        │────────────────────────────────────────────────────>
        │                         │                         │
        │ RSI implementation      │                         │
        │<────────────────────────────────────────────────────
        │                         │                         │
        │ Initialize with RSI     │                         │
        │────────────────────────>│                         │
        │                         │                         │
        │ process_message()       │                         │
        │ (with context)          │                         │
        │────────────────────────>│                         │
        │                         │                         │
        │                         │ RSI.get_current_        │
        │                         │ principal()             │
        │                         │────────────────────────>│
        │                         │                         │
        │                         │ SecurityPrincipalInfo   │
        │                         │<────────────────────────│
        │                         │                         │
        │                         │ RSI.check_permission()  │
        │                         │────────────────────────>│
        │                         │                         │
        │                         │ AuthZResult             │
        │                         │<────────────────────────│
        │                         │                         │
```

## Configuration Dependencies

The following configuration parameters affect this interaction:

```yaml
agents:
  example_agent:
    # Agent's security configuration
    security:
      authorization:
        required_roles: ["user", "admin"]
        required_permissions: ["read_data", "write_data"]
      
    # Reasoning security integration configuration
    reasoning:
      # ... other reasoning configuration ...
      security_integration:
        rsi_enabled: true
        rsi_policy_profile: "standard"
        permission_check_behavior: "strict"

# Global security system configuration
security_system:
  providers:
    authentication:
      provider: "jwt"
      settings:
        # JWT settings...
    authorization:
      provider: "rbac"
      settings:
        # RBAC settings...
  reasoning_security:
    enabled: true
    policy_profiles:
      - name: "standard"
        permissions:
          - action: "access_knowledge"
            resources: ["knowledge:*"]
          - action: "use_tool"
            resources: ["tool:*"]
      - name: "restricted"
        permissions:
          - action: "access_knowledge"
            resources: ["knowledge:public_*"]
          - action: "use_tool"
            resources: ["tool:safe_*"]
```

## Extension Points

1. **Security Providers**:
   - Additional authentication and authorization providers can be implemented and plugged into the Security System.
   - Provider interface:
     ```python
     class AuthenticationProvider:
         def authenticate(self, credentials: Any) -> AuthenticationResult:
             # Provider-specific implementation
             
     class AuthorizationProvider:
         def authorize(self, principal: SecurityPrincipalInfo, action: str, resource: str) -> AuthorizationResult:
             # Provider-specific implementation
     ```

2. **RSI Extensions**:
   - The RSI can be extended with additional security-related methods specific to certain reasoning approaches.
   - Example extension for LLM reasoning:
     ```python
     class LLMReasoningSecurityInterface(ReasoningSecurityInterface):
         # Inherit base RSI methods
         
         def check_tool_permission(self, tool_name: str) -> AuthZResult:
             """Check if the current principal has permission to use a specific LLM tool."""
             return self.check_permission(action="use_tool", resource_identifier=f"tool:{tool_name}")
     ```

## Related Documentation

- [Security System Architecture](../../../17_security/architecture/README.md)
- [Authentication Mechanisms](../../../17_security/authentication/auth_mechanisms.md)
- [Authorization Models](../../../17_security/authorization/authorization_models.md)
- [Reasoning Security Interface (RSI)](../../../17_security/reasoning_security_interface.md)
- [Agent Framework ↔ KR&R System](./agent_framework_krr.md)
- [Protocol Layer ↔ Security System](./protocol_layer_security.md)

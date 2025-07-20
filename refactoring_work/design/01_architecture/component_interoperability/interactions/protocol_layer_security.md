# Protocol Layer ↔ Security System

## Relationship Summary
- **Protocol Layer → Security System**: Depends On
- **Security System → Protocol Layer**: Provides To

## Interface Definitions

### Protocol Layer → Security System

#### Methods/Functions
```python
def authenticate_protocol_request(protocol_type: str,
                              request_data: Dict[str, Any],
                              auth_options: Optional[ProtocolAuthOptions] = None) -> AuthenticationResult:
    """
    Authenticate an incoming protocol request.

    Args:
        protocol_type: str - Protocol identifier (e.g., "a2a", "mcp", "http")
        request_data: Dict[str, Any] - Protocol request data containing authentication information
        auth_options: Optional[ProtocolAuthOptions] - Authentication options/settings

    Returns:
        AuthenticationResult - Result of authentication process with security principal info

    Raises:
        AuthenticationProviderNotFoundError - If no authentication provider is configured for the protocol
        MalformedCredentialsError - If credentials are malformed or cannot be extracted
        UnsupportedAuthMechanismError - If the authentication mechanism is not supported
    """
```

**Data Structures:**

```python
class AuthenticationType(Enum):
    """
    Type of authentication mechanism.
    """
    NONE = "none"  # No authentication
    API_KEY = "api_key"  # API key-based authentication
    JWT = "jwt"  # JSON Web Token authentication
    OAUTH2 = "oauth2"  # OAuth 2.0 authentication
    MTLS = "mtls"  # Mutual TLS authentication
    BASIC = "basic"  # HTTP Basic authentication
    DIGEST = "digest"  # HTTP Digest authentication
    CUSTOM = "custom"  # Custom authentication mechanism

class SecurityPrincipalType(Enum):
    """
    Type of security principal.
    """
    USER = "user"  # Human user
    SERVICE = "service"  # Service account
    AGENT = "agent"  # AI agent
    SYSTEM = "system"  # System component
    ANONYMOUS = "anonymous"  # Anonymous/unauthenticated principal
    FEDERATED = "federated"  # Federated identity

class AuthLevel(Enum):
    """
    Level of authentication required.
    """
    NONE = "none"  # No authentication required
    LOW = "low"  # Low-security authentication (e.g., API key)
    MEDIUM = "medium"  # Medium-security authentication (e.g., JWT)
    HIGH = "high"  # High-security authentication (e.g., multi-factor)

class SecurityPrincipal:
    """
    Represents an authenticated security principal.
    """
    id: str  # Unique identifier for the principal
    name: str  # Display name of the principal
    type: SecurityPrincipalType  # Type of security principal
    auth_level: AuthLevel  # Level of authentication
    auth_time: datetime  # When the principal was authenticated
    expiration_time: Optional[datetime] = None  # When the authentication expires
    roles: List[str] = []  # Roles assigned to the principal
    permissions: List[str] = []  # Explicit permissions assigned to the principal
    attributes: Dict[str, Any] = {}  # Additional attributes of the principal
    tokens: Dict[str, str] = {}  # Authentication tokens (access token, refresh token, etc.)
    scope: str = ""  # OAuth scope or permission scope
    tenant_id: Optional[str] = None  # Multi-tenant identifier
    protocol_specific: Dict[str, Any] = {}  # Protocol-specific authentication info

class AuthenticationResult:
    """
    Result of an authentication operation.
    """
    is_authenticated: bool  # Whether authentication was successful
    principal: Optional[SecurityPrincipal] = None  # Authenticated principal if successful
    error_code: Optional[str] = None  # Error code if authentication failed
    error_message: Optional[str] = None  # Error message if authentication failed
    auth_mechanism_used: AuthenticationType  # Authentication mechanism that was used
    protocol_type: str  # Protocol type that was authenticated
    auth_provider: str  # Authentication provider that was used
    additional_factors_required: List[str] = []  # Additional authentication factors required
    auth_metadata: Dict[str, Any] = {}  # Additional metadata about the authentication
    trace_id: Optional[str] = None  # Trace ID for debugging

class ProtocolAuthOptions:
    """
    Options for protocol authentication.
    """
    required_auth_level: AuthLevel = AuthLevel.MEDIUM  # Required authentication level
    allowed_mechanisms: List[AuthenticationType] = []  # Allowed authentication mechanisms
    credential_location: Optional[str] = None  # Where to look for credentials (header, query, etc.)
    additional_factors: List[str] = []  # Additional authentication factors to require
    jwt_validation_options: Dict[str, Any] = {}  # Options for JWT validation
    timeout_seconds: int = 30  # Timeout for authentication process
    scope_validation: bool = False  # Whether to validate scopes
    required_scopes: List[str] = []  # Scopes required for authentication
    tenant_specific: bool = False  # Whether authentication is tenant-specific
    tenant_id: Optional[str] = None  # Tenant ID for tenant-specific authentication
    protocol_specific_options: Dict[str, Any] = {}  # Protocol-specific options

class MalformedCredentialsError(Exception):
    """
    Raised when credentials are malformed or cannot be extracted.
    """
    pass

class UnsupportedAuthMechanismError(Exception):
    """
    Raised when an unsupported authentication mechanism is requested.
    """
    pass

class AuthenticationProviderNotFoundError(Exception):
    """
    Raised when no authentication provider is configured for a protocol.
    """
    pass
```

**Example Usage:**

```python
# Example 1: Authenticating an A2A protocol request with JWT

try:
    # Extract the A2A request from an incoming HTTP request
    a2a_request = {
        "headers": {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "Content-Type": "application/json"
        },
        "body": {
            "messageId": "msg_123",
            "agent": {
                "id": "agent_456",
                "apiVersion": "v1"
            },
            "message": {
                "text": "Hello, can you help me with a task?"
            }
        },
        "path": "/a2a/agents/assistant1",
        "method": "POST"
    }

    # Configure authentication options for A2A protocol
    a2a_auth_options = ProtocolAuthOptions(
        required_auth_level=AuthLevel.MEDIUM,
        allowed_mechanisms=[AuthenticationType.JWT, AuthenticationType.OAUTH2],
        credential_location="Authorization",
        jwt_validation_options={
            "verify_signature": True,
            "verify_exp": True,
            "audience": "openmas-a2a-api",
            "issuer": "https://auth.openmas.org"
        },
        scope_validation=True,
        required_scopes=["a2a:invoke", "agents:read"]
    )

    # Authenticate the A2A request
    auth_result = security_system.authenticate_protocol_request(
        protocol_type="a2a",
        request_data=a2a_request,
        auth_options=a2a_auth_options
    )

    # Handle authentication result
    if auth_result.is_authenticated and auth_result.principal:
        logger.info(f"A2A request authenticated successfully for principal: {auth_result.principal.name}")

        # Check if the principal has the necessary roles
        if "agent_invoker" in auth_result.principal.roles:
            # Process the authenticated request
            agent_framework.process_authenticated_request(
                request=a2a_request["body"],
                principal=auth_result.principal
            )
        else:
            logger.warning(f"Principal {auth_result.principal.id} lacks required role 'agent_invoker'")
            protocol_layer.send_authorization_error_response(
                request=a2a_request,
                error_code="insufficient_permissions",
                error_message="You do not have the required role to invoke this agent."
            )
    else:
        # Log authentication failure
        logger.warning(f"A2A authentication failed: {auth_result.error_code} - {auth_result.error_message}")

        # Send authentication error response
        protocol_layer.send_authentication_error_response(
            request=a2a_request,
            error_code=auth_result.error_code or "authentication_failed",
            error_message=auth_result.error_message or "Authentication failed"
        )

        # Emit authentication failure event
        event_system.emit("protocol_authentication_failed", {
            "protocol_type": "a2a",
            "error_code": auth_result.error_code,
            "error_message": auth_result.error_message,
            "request_metadata": {
                "path": a2a_request["path"],
                "method": a2a_request["method"],
                "message_id": a2a_request["body"].get("messageId")
            },
            "timestamp": datetime.now().isoformat()
        })

except MalformedCredentialsError as e:
    logger.error(f"Malformed credentials in A2A request: {str(e)}")
    protocol_layer.send_authentication_error_response(
        request=a2a_request,
        error_code="malformed_credentials",
        error_message="The provided authentication credentials are malformed or invalid."
    )

except AuthenticationProviderNotFoundError as e:
    logger.error(f"Authentication provider not found for A2A protocol: {str(e)}")
    protocol_layer.send_authentication_error_response(
        request=a2a_request,
        error_code="auth_provider_not_found",
        error_message="No authentication provider is configured for this protocol."
    )


# Example 2: Authenticating an MCP protocol request with API key

try:
    # Extract the MCP request
    mcp_request = {
        "headers": {
            "X-MCP-API-Key": "mcp_api_key_12345",
            "Content-Type": "application/json"
        },
        "body": {
            "id": "req_789",
            "capability": "sequential-thinking",
            "parameters": {
                "query": "Analyze the impact of climate change on global agriculture."
            }
        },
        "path": "/mcp/capabilities/sequential-thinking",
        "method": "POST"
    }

    # Configure authentication options for MCP protocol
    mcp_auth_options = ProtocolAuthOptions(
        required_auth_level=AuthLevel.MEDIUM,
        allowed_mechanisms=[AuthenticationType.API_KEY],
        credential_location="X-MCP-API-Key",
        protocol_specific_options={
            "api_key_validation": "database",  # Validate API key against database
            "rate_limit_by_key": True,  # Apply rate limiting per API key
            "rate_limit": 100  # Maximum requests per minute
        }
    )

    # Authenticate the MCP request
    auth_result = security_system.authenticate_protocol_request(
        protocol_type="mcp",
        request_data=mcp_request,
        auth_options=mcp_auth_options
    )

    # Handle authentication result
    if auth_result.is_authenticated and auth_result.principal:
        logger.info(f"MCP request authenticated successfully for service: {auth_result.principal.name}")

        # Check rate limits (could be handled internally by the auth system)
        if is_rate_limited(auth_result.principal.id):
            logger.warning(f"Rate limit exceeded for principal {auth_result.principal.id}")
            protocol_layer.send_rate_limit_error_response(
                request=mcp_request,
                error_message="Rate limit exceeded. Please try again later.",
                retry_after=calculate_retry_after(auth_result.principal.id)
            )
        else:
            # Process the authenticated request
            mcp_handler.process_capability_request(
                request=mcp_request["body"],
                principal=auth_result.principal
            )
    else:
        # Log authentication failure
        logger.warning(f"MCP authentication failed: {auth_result.error_code} - {auth_result.error_message}")

        # Send authentication error response
        protocol_layer.send_authentication_error_response(
            request=mcp_request,
            error_code=auth_result.error_code or "invalid_api_key",
            error_message=auth_result.error_message or "Invalid API key"
        )

except Exception as e:
    logger.error(f"Error authenticating MCP request: {str(e)}")
    protocol_layer.send_error_response(
        request=mcp_request,
        error_code="authentication_error",
        error_message="An error occurred during authentication."
    )
```

```python
def authorize_protocol_action(protocol_type: str,
                         principal: SecurityPrincipal,
                         action: str,
                         resource: str,
                         auth_context: Optional[AuthorizationContext] = None) -> AuthorizationResult:
    """
    Authorize a protocol action for an authenticated principal.

    Args:
        protocol_type: str - Protocol identifier (e.g., "a2a", "mcp", "http")
        principal: SecurityPrincipal - Authenticated security principal
        action: str - Action being performed (e.g., "INVOKE_CAPABILITY", "READ_AGENT")
        resource: str - Resource being accessed (e.g., "sequential-thinking", "agent:123")
        auth_context: Optional[AuthorizationContext] - Additional context for authorization decision

    Returns:
        AuthorizationResult - Result of authorization process with decision

    Raises:
        AuthorizationProviderNotFoundError - If no authorization provider is configured for the protocol
        InvalidPrincipalError - If the provided principal is invalid or expired
        InvalidActionError - If the provided action is not recognized
        InvalidResourceError - If the provided resource is not recognized
    """
```

**Data Structures:**

```python
class AuthorizationDecision(Enum):
    """
    Result of an authorization decision.
    """
    ALLOW = "allow"  # Access is allowed
    DENY = "deny"  # Access is denied
    INDETERMINATE = "indeterminate"  # Unable to determine (e.g., policy error)

class AuthorizationResult:
    """
    Result of an authorization operation.
    """
    decision: AuthorizationDecision  # Authorization decision
    resource: str  # Resource that was evaluated
    action: str  # Action that was evaluated
    principal_id: str  # ID of the principal that was evaluated
    protocol_type: str  # Protocol type for which authorization was performed
    policy_id: Optional[str] = None  # ID of the policy that made the decision
    reason: Optional[str] = None  # Reason for the decision
    expiration: Optional[datetime] = None  # When this authorization decision expires
    obligations: List[Dict[str, Any]] = []  # Obligations that must be fulfilled
    advice: List[Dict[str, Any]] = []  # Non-mandatory advice for the requester
    trace_id: Optional[str] = None  # Trace ID for debugging
    evaluation_metadata: Dict[str, Any] = {}  # Additional metadata about the evaluation

class AuthorizationContext:
    """
    Additional context for authorization decisions.
    """
    environment: Dict[str, Any] = {}  # Environmental attributes (time, IP, etc.)
    resource_attributes: Dict[str, Any] = {}  # Additional resource attributes
    action_attributes: Dict[str, Any] = {}  # Additional action attributes
    principal_attributes: Dict[str, Any] = {}  # Additional principal attributes
    protocol_attributes: Dict[str, Any] = {}  # Protocol-specific attributes
    request_id: Optional[str] = None  # ID of the request being authorized
    session_id: Optional[str] = None  # ID of the session
    context_id: Optional[str] = None  # ID of the authorization context

class InvalidPrincipalError(Exception):
    """
    Raised when the provided principal is invalid or expired.
    """
    pass

class InvalidActionError(Exception):
    """
    Raised when the provided action is not recognized.
    """
    pass

class InvalidResourceError(Exception):
    """
    Raised when the provided resource is not recognized.
    """
    pass

class AuthorizationProviderNotFoundError(Exception):
    """
    Raised when no authorization provider is configured for a protocol.
    """
    pass
```

**Example Usage:**

```python
# Example 1: Authorizing an MCP capability invocation

try:
    # Create authorization context with additional information
    auth_context = AuthorizationContext(
        environment={
            "client_ip": "192.168.1.100",
            "request_time": datetime.now().isoformat(),
            "client_user_agent": "OpenMAS-Client/1.0"
        },
        resource_attributes={
            "capability_type": "reasoning",
            "capability_version": "2.0",
            "capability_provider": "openmas-reasoning-service"
        },
        action_attributes={
            "operation": "invoke",
            "parameters_provided": ["query", "max_tokens"]
        },
        protocol_attributes={
            "protocol_version": "1.0",
            "content_type": "application/json"
        },
        request_id="req_789"
    )

    # Authorize the MCP capability invocation
    auth_result = security_system.authorize_protocol_action(
        protocol_type="mcp",
        principal=authenticated_principal,  # Principal from previous authentication
        action="INVOKE_CAPABILITY",
        resource="sequential-thinking",
        auth_context=auth_context
    )

    # Handle authorization result
    if auth_result.decision == AuthorizationDecision.ALLOW:
        logger.info(f"MCP capability invocation authorized for principal: {authenticated_principal.id}")

        # Check if there are any obligations to fulfill
        if auth_result.obligations:
            # Handle obligations (e.g., logging, notifications)
            for obligation in auth_result.obligations:
                fulfill_obligation(obligation)

        # Process the capability invocation
        capability_result = mcp_handler.invoke_capability(
            capability_name="sequential-thinking",
            parameters=request_body["parameters"],
            principal=authenticated_principal
        )

        # Send successful response
        protocol_layer.send_capability_response(request, capability_result)

    elif auth_result.decision == AuthorizationDecision.DENY:
        logger.warning(f"MCP capability invocation denied for principal: {authenticated_principal.id}, reason: {auth_result.reason}")

        # Send authorization error response
        protocol_layer.send_authorization_error_response(
            request=request,
            error_code="authorization_denied",
            error_message=auth_result.reason or "You are not authorized to invoke this capability."
        )

        # Emit authorization denied event
        event_system.emit("protocol_authorization_denied", {
            "protocol_type": "mcp",
            "principal_id": authenticated_principal.id,
            "action": "INVOKE_CAPABILITY",
            "resource": "sequential-thinking",
            "reason": auth_result.reason,
            "request_id": auth_context.request_id,
            "timestamp": datetime.now().isoformat()
        })
    else:  # INDETERMINATE
        logger.error(f"MCP capability authorization indeterminate for principal: {authenticated_principal.id}")

        # Send error response
        protocol_layer.send_error_response(
            request=request,
            error_code="authorization_error",
            error_message="Unable to determine authorization. Please try again later."
        )

except InvalidPrincipalError as e:
    logger.error(f"Invalid principal in MCP authorization: {str(e)}")
    protocol_layer.send_authentication_error_response(
        request=request,
        error_code="invalid_principal",
        error_message="The provided authentication is invalid or expired."
    )

except InvalidActionError as e:
    logger.error(f"Invalid action in MCP authorization: {str(e)}")
    protocol_layer.send_error_response(
        request=request,
        error_code="invalid_action",
        error_message="The requested action is not recognized."
    )

except Exception as e:
    logger.error(f"Error authorizing MCP request: {str(e)}")
    protocol_layer.send_error_response(
        request=request,
        error_code="authorization_error",
        error_message="An error occurred during authorization."
    )


# Example 2: Authorizing an A2A agent invocation with fine-grained permissions

try:
    # Define the resource with more specificity
    resource = f"agent:{agent_id}"

    # Create authorization context with additional information
    auth_context = AuthorizationContext(
        environment={
            "client_ip": client_ip,
            "request_time": datetime.now().isoformat(),
            "client_location": geo_location
        },
        resource_attributes={
            "agent_type": agent_type,
            "agent_capabilities": agent_capabilities,
            "agent_provider": agent_provider,
            "agent_visibility": agent_visibility  # public, private, shared
        },
        action_attributes={
            "interaction_type": "conversation",
            "contains_file_attachments": has_attachments,
            "contains_tool_calls": has_tool_calls
        },
        protocol_attributes={
            "protocol_version": "1.0",
            "conversation_id": conversation_id,
            "turn_id": turn_id
        },
        session_id=session_id
    )

    # Authorize the A2A agent invocation
    auth_result = security_system.authorize_protocol_action(
        protocol_type="a2a",
        principal=authenticated_principal,
        action="INVOKE_AGENT",
        resource=resource,
        auth_context=auth_context
    )

    # Handle authorization result
    if auth_result.decision == AuthorizationDecision.ALLOW:
        logger.info(f"A2A agent invocation authorized for principal: {authenticated_principal.id}")

        # Process the agent invocation
        agent_framework.process_agent_request(
            agent_id=agent_id,
            request=request_body,
            principal=authenticated_principal,
            session_id=session_id
        )

    elif auth_result.decision == AuthorizationDecision.DENY:
        logger.warning(f"A2A agent invocation denied for principal: {authenticated_principal.id}, reason: {auth_result.reason}")

        # Send authorization error response
        protocol_layer.send_authorization_error_response(
            request=request,
            error_code="authorization_denied",
            error_message=auth_result.reason or "You are not authorized to invoke this agent."
        )

        # If there's advice in the authorization result, include it in the response
        if auth_result.advice:
            additional_info = {}
            for advice_item in auth_result.advice:
                if advice_item.get("type") == "request_access":
                    additional_info["request_access_url"] = advice_item.get("url")
                elif advice_item.get("type") == "documentation":
                    additional_info["documentation_url"] = advice_item.get("url")

            if additional_info:
                protocol_layer.add_response_metadata(request, additional_info)
    else:  # INDETERMINATE
        logger.error(f"A2A agent authorization indeterminate for principal: {authenticated_principal.id}")

        # Send error response
        protocol_layer.send_error_response(
            request=request,
            error_code="authorization_error",
            error_message="Unable to determine authorization. Please try again later."
        )

except Exception as e:
    logger.error(f"Error authorizing A2A request: {str(e)}")
    protocol_layer.send_error_response(
        request=request,
        error_code="authorization_error",
        error_message="An error occurred during authorization."
    )
```

```python
def encrypt_protocol_message(protocol_type: str,
                        message: Dict[str, Any],
                        recipient_id: str,
                        encryption_options: Optional[EncryptionOptions] = None) -> EncryptedMessage:
    """
    Encrypt a protocol message for secure transmission.

    Args:
        protocol_type: str - Protocol identifier (e.g., "a2a", "mcp", "http")
        message: Dict[str, Any] - Message to encrypt
        recipient_id: str - Identifier of the recipient
        encryption_options: Optional[EncryptionOptions] - Options for encryption

    Returns:
        EncryptedMessage - Encrypted message with metadata

    Raises:
        EncryptionProviderNotFoundError - If no encryption provider is configured for the protocol
        RecipientKeyNotFoundError - If the recipient's public key cannot be found
        EncryptionError - If encryption fails
        InvalidMessageFormatError - If the message format is invalid for the protocol
    """
```

**Data Structures:**

```python
class EncryptionAlgorithm(Enum):
    """
    Encryption algorithms supported by the system.
    """
    AES_GCM = "aes-gcm"  # AES in Galois/Counter Mode
    AES_CBC = "aes-cbc"  # AES in Cipher Block Chaining mode
    CHACHA20_POLY1305 = "chacha20-poly1305"  # ChaCha20-Poly1305
    RSA_OAEP = "rsa-oaep"  # RSA with OAEP padding
    ECDH_P256 = "ecdh-p256"  # ECDH using P-256 curve
    ECDH_X25519 = "ecdh-x25519"  # ECDH using X25519 curve

class EncryptionMode(Enum):
    """
    Mode of encryption.
    """
    SYMMETRIC = "symmetric"  # Symmetric encryption (same key for encryption and decryption)
    ASYMMETRIC = "asymmetric"  # Asymmetric encryption (public/private key pair)
    HYBRID = "hybrid"  # Hybrid encryption (combination of symmetric and asymmetric)

class EncryptedMessage:
    """
    Represents an encrypted message.
    """
    protocol_type: str  # Protocol type the message belongs to
    ciphertext: bytes  # Encrypted message content
    iv: Optional[bytes] = None  # Initialization vector (if applicable)
    auth_tag: Optional[bytes] = None  # Authentication tag (if applicable)
    encrypted_key: Optional[bytes] = None  # Encrypted symmetric key (for hybrid encryption)
    sender_id: Optional[str] = None  # Identifier of the sender
    recipient_id: str  # Identifier of the recipient
    algorithm: EncryptionAlgorithm  # Encryption algorithm used
    mode: EncryptionMode  # Encryption mode used
    key_id: Optional[str] = None  # Identifier of the key used for encryption
    encryption_timestamp: datetime  # When the message was encrypted
    expiration_timestamp: Optional[datetime] = None  # When the encrypted message expires
    metadata: Dict[str, Any] = {}  # Additional metadata
    format: str = "binary"  # Format of the encrypted message ("binary", "base64", "hex")
    protocol_headers: Dict[str, Any] = {}  # Protocol-specific headers

class EncryptionOptions:
    """
    Options for message encryption.
    """
    algorithm: Optional[EncryptionAlgorithm] = None  # Encryption algorithm to use
    mode: EncryptionMode = EncryptionMode.HYBRID  # Encryption mode to use
    key_id: Optional[str] = None  # Specific key ID to use for encryption
    include_sender_id: bool = True  # Whether to include sender ID in encrypted message
    expiration_seconds: Optional[int] = None  # Seconds until encrypted message expires
    protocol_specific_options: Dict[str, Any] = {}  # Protocol-specific encryption options
    sensitive_fields: List[str] = []  # Fields to encrypt (if partial encryption)
    encrypt_all: bool = True  # Whether to encrypt the entire message
    format: str = "binary"  # Output format ("binary", "base64", "hex")
    compression: bool = False  # Whether to compress before encryption
    padding: bool = True  # Whether to add padding
    aad: Optional[bytes] = None  # Additional authenticated data (for AEAD algorithms)

class EncryptionError(Exception):
    """
    Raised when encryption fails.
    """
    pass

class RecipientKeyNotFoundError(Exception):
    """
    Raised when the recipient's public key cannot be found.
    """
    pass

class EncryptionProviderNotFoundError(Exception):
    """
    Raised when no encryption provider is configured for a protocol.
    """
    pass

class InvalidMessageFormatError(Exception):
    """
    Raised when the message format is invalid for the protocol.
    """
    pass
```

**Example Usage:**

```python
# Example 1: Encrypting an A2A protocol message for secure agent-to-agent communication

try:
    # Prepare an A2A message to be sent securely
    a2a_message = {
        "messageId": "msg_456",
        "agent": {
            "id": "agent_789",
            "apiVersion": "v1"
        },
        "agentResponse": {
            "text": "This is a secure message containing sensitive information.",
            "context": {
                "conversationId": "conv_123",
                "turnId": "turn_5"
            }
        },
        "metadata": {
            "security": {
                "classification": "confidential",
                "requiredProtection": "encryption"
            }
        }
    }

    # Configure encryption options for A2A protocol
    encryption_options = EncryptionOptions(
        algorithm=EncryptionAlgorithm.AES_GCM,
        mode=EncryptionMode.HYBRID,
        include_sender_id=True,
        expiration_seconds=3600,  # Encrypted message expires after 1 hour
        format="base64",  # Return base64-encoded ciphertext for easier transmission
        compression=True,  # Compress the message before encryption
        protocol_specific_options={
            "signature_required": True,  # Sign the message for integrity verification
            "encrypt_attachments": True  # Encrypt any file attachments
        }
    )

    # Encrypt the A2A message
    encrypted_message = security_system.encrypt_protocol_message(
        protocol_type="a2a",
        message=a2a_message,
        recipient_id="agent_456",  # The recipient agent
        encryption_options=encryption_options
    )

    # Log encryption success
    logger.info(f"A2A message encrypted successfully for recipient: {encrypted_message.recipient_id}")
    logger.debug(f"Encryption algorithm: {encrypted_message.algorithm.value}, Mode: {encrypted_message.mode.value}")

    # Prepare the encrypted message for transmission
    secure_a2a_message = {
        "messageId": a2a_message["messageId"],
        "agent": a2a_message["agent"],
        "encryptedContent": {
            "ciphertext": encrypted_message.ciphertext.decode() if isinstance(encrypted_message.ciphertext, bytes) else encrypted_message.ciphertext,
            "encryptedKey": encrypted_message.encrypted_key.decode() if isinstance(encrypted_message.encrypted_key, bytes) else encrypted_message.encrypted_key,
            "iv": encrypted_message.iv.decode() if isinstance(encrypted_message.iv, bytes) else encrypted_message.iv,
            "authTag": encrypted_message.auth_tag.decode() if isinstance(encrypted_message.auth_tag, bytes) else encrypted_message.auth_tag,
            "algorithm": encrypted_message.algorithm.value,
            "keyId": encrypted_message.key_id,
            "senderId": encrypted_message.sender_id,
            "timestamp": encrypted_message.encryption_timestamp.isoformat(),
            "expiration": encrypted_message.expiration_timestamp.isoformat() if encrypted_message.expiration_timestamp else None
        },
        "metadata": {
            "security": {
                "classification": "confidential",
                "protection": "encrypted"
            }
        }
    }

    # Send the encrypted message
    protocol_layer.send_message(secure_a2a_message)

    logger.info(f"Encrypted A2A message sent successfully to {secure_a2a_message['encryptedContent']['senderId']}")

except RecipientKeyNotFoundError as e:
    logger.error(f"Recipient key not found: {str(e)}")

    # Handle missing recipient key
    key_request = create_key_request("agent_456")
    key_management_system.request_recipient_key(key_request)

    # Send unencrypted message with reduced sensitive information
    fallback_message = create_fallback_message(a2a_message)
    protocol_layer.send_message(fallback_message)

except EncryptionError as e:
    logger.error(f"Encryption failed: {str(e)}")

    # Send error notification to the sender
    protocol_layer.send_error_notification(
        sender_id="agent_789",
        error_code="encryption_failed",
        error_message="Failed to encrypt message. The message was not sent."
    )


# Example 2: Encrypting an MCP protocol message with field-level encryption

try:
    # Prepare an MCP message with sensitive data
    mcp_message = {
        "id": "req_789",
        "capability": "personal-data-analysis",
        "parameters": {
            "userData": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "ssn": "123-45-6789",  # Sensitive field
                "creditCard": "4111-1111-1111-1111",  # Sensitive field
                "address": "123 Main St, Anytown, USA"
            },
            "analysisType": "financial",
            "includePersonalRecommendations": True
        }
    }

    # Configure encryption options for MCP protocol with field-level encryption
    encryption_options = EncryptionOptions(
        algorithm=EncryptionAlgorithm.AES_GCM,
        mode=EncryptionMode.HYBRID,
        encrypt_all=False,  # Don't encrypt the entire message
        sensitive_fields=[
            "parameters.userData.ssn",
            "parameters.userData.creditCard"
        ],  # Only encrypt these sensitive fields
        format="base64",
        protocol_specific_options={
            "field_level_encryption": True,
            "integrity_protection": "hmac"
        }
    )

    # Get the recipient service ID for the capability provider
    recipient_id = capability_registry.get_capability_provider_id("personal-data-analysis")

    # Encrypt the MCP message (or just sensitive fields)
    encrypted_message = security_system.encrypt_protocol_message(
        protocol_type="mcp",
        message=mcp_message,
        recipient_id=recipient_id,
        encryption_options=encryption_options
    )

    # For field-level encryption, the system returns a modified message with encrypted fields
    if encryption_options.encrypt_all:
        # Handle fully encrypted message
        secure_mcp_message = {
            "id": mcp_message["id"],
            "capability": mcp_message["capability"],
            "encryptedContent": {
                # Similar to A2A example
            }
        }
    else:
        # With field-level encryption, the original message structure is preserved
        # but sensitive fields are replaced with encrypted values
        secure_mcp_message = encrypted_message.metadata["field_encrypted_message"]

        logger.info(f"MCP message encrypted with field-level encryption. {len(encryption_options.sensitive_fields)} fields protected.")

    # Send the secure MCP message
    protocol_layer.send_capability_request(secure_mcp_message)

except Exception as e:
    logger.error(f"Error encrypting MCP message: {str(e)}")

    # Handle encryption failure
    if isinstance(e, RecipientKeyNotFoundError):
        # Try to fetch the recipient's key
        fetch_recipient_key(recipient_id)

        # Notify the user about the delay
        user_notification.send(
            user_id=get_current_user_id(),
            notification_type="encryption_delay",
            message="Your request contains sensitive data and requires secure encryption. Please try again in a few moments."
        )
    else:
        # For other errors, send a generic error response
        protocol_layer.send_error_response(
            request_id=mcp_message["id"],
            error_code="encryption_error",
            error_message="Failed to secure sensitive data. Please try again later."
        )
```

#### Events

```python
class ProtocolAuthenticationFailedEvent:
    """
    Event emitted when protocol authentication fails.
    """
    event_name: str = "protocol_authentication_failed"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "warning"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        protocol_type: str  # Protocol type for which authentication failed
        error_code: str  # Error code indicating reason for failure
        error_message: str  # Human-readable error message
        failure_reason: str  # Detailed reason for failure
        auth_mechanism: Optional[str] = None  # Authentication mechanism that failed
        ip_address: Optional[str] = None  # IP address of the client
        request_details: Dict[str, Any] = {}  # Details about the request that failed authentication
        user_id: Optional[str] = None  # User ID if known
        correlation_id: Optional[str] = None  # Correlation ID for tracing
        attempt_count: int = 1  # Number of failed authentication attempts
        metadata: Dict[str, Any] = {}  # Additional metadata about the authentication failure

        class AuthenticationDetails:
            """
            Detailed information about the authentication failure.
            """
            request_id: str  # Unique identifier for the request
            auth_provider: str  # Authentication provider that processed the request
            auth_type: str  # Type of authentication attempted (jwt, api_key, etc.)
            token_details: Dict[str, Any] = {}  # Details about the authentication token if applicable
            credential_problems: List[str] = []  # Specific problems with the credentials
            timestamp: str  # ISO-8601 timestamp of the failure
            trace_id: Optional[str] = None  # Distributed tracing ID

        class ProtocolSpecificDetails:
            """
            Protocol-specific details about the authentication failure.
            """
            a2a_specific: Dict[str, Any] = {  # A2A protocol-specific details
                "agent_card_id": None,  # Agent card ID if available
                "api_version": None,  # A2A API version
                "card_schema_version": None,  # Agent card schema version
                "issuer": None,  # JWT issuer if applicable
                "token_expiration": None  # Token expiration time if applicable
            }
            mcp_specific: Dict[str, Any] = {  # MCP protocol-specific details
                "tool_id": None,  # Tool ID if available
                "capability_id": None,  # Capability ID if available
                "api_key_id": None,  # API key ID if applicable
                "session_id": None,  # Session ID if available
                "request_type": None  # Type of MCP request
            }
            security_impact: str = "low"  # Security impact of the failure (low, medium, high, critical)
```

**Example Usage:**
```python
# Subscribe to protocol authentication failed events
@event_system.subscribe(ProtocolAuthenticationFailedEvent.event_name)
def handle_authentication_failure(event: ProtocolAuthenticationFailedEvent):
    payload = event.payload
    protocol_type = payload.protocol_type
    error_code = payload.error_code

    logger.warning(f"Authentication failed for {protocol_type} protocol: {error_code}")

    # Log details for security monitoring
    security_logger.log(
        level="WARNING",
        message=f"Authentication failure detected for {protocol_type}",
        context={
            "protocol": protocol_type,
            "error_code": error_code,
            "error_message": payload.error_message,
            "ip_address": payload.ip_address,
            "timestamp": event.timestamp.isoformat(),
            "correlation_id": payload.correlation_id
        }
    )

    # Protocol-specific handling based on protocol type
    if protocol_type == "a2a":
        # Handle A2A-specific authentication failures
        a2a_auth_details = payload.request_details.get("a2a", {})
        agent_card_id = a2a_auth_details.get("agent_card_id")

        if agent_card_id:
            # Update agent card authentication status
            a2a_agent_registry.update_authentication_status(
                agent_card_id=agent_card_id,
                status="failed",
                reason=error_code,
                timestamp=event.timestamp
            )
            logger.debug(f"Updated authentication status for A2A agent card {agent_card_id}")

        # Send appropriate A2A error response
        a2a_response_formatter.create_auth_error_response(
            error_code=error_code,
            error_message=payload.error_message,
            request_id=payload.request_details.get("request_id"),
            correlation_id=payload.correlation_id
        )

    elif protocol_type == "mcp":
        # Handle MCP-specific authentication failures
        mcp_auth_details = payload.request_details.get("mcp", {})
        tool_id = mcp_auth_details.get("tool_id")
        capability_id = mcp_auth_details.get("capability_id")

        if tool_id or capability_id:
            # Update MCP capability/tool access status
            mcp_registry.update_access_status(
                tool_id=tool_id,
                capability_id=capability_id,
                status="auth_failed",
                reason=error_code,
                timestamp=event.timestamp
            )
            logger.debug(f"Updated access status for MCP tool {tool_id} or capability {capability_id}")

        # Send appropriate MCP error response
        mcp_response_formatter.create_auth_error_response(
            error_code=error_code,
            error_message=payload.error_message,
            request_id=payload.request_details.get("request_id"),
            correlation_id=payload.correlation_id
        )

    # Check for potential security threats
    if payload.attempt_count >= 3:
        # Potential brute force attack
        security_monitoring.flag_potential_threat(
            threat_type="brute_force_attempt",
            source_ip=payload.ip_address,
            protocol=protocol_type,
            details={
                "attempt_count": payload.attempt_count,
                "user_id": payload.user_id,
                "timestamp": event.timestamp.isoformat()
            }
        )

        # Apply temporary IP ban if configured
        if security_config.get("auto_block_repeated_failures", False):
            security_system.temporary_block_ip(
                ip_address=payload.ip_address,
                duration_seconds=300,  # 5 minutes
                reason=f"Multiple authentication failures for {protocol_type}"
            )
            logger.info(f"Temporarily blocked IP {payload.ip_address} after multiple authentication failures")

    # Update observability metrics
    metrics_service.increment(
        metric_name="authentication_failures",
        dimensions={
            "protocol": protocol_type,
            "error_code": error_code,
            "auth_mechanism": payload.auth_mechanism or "unknown"
        }
    )
```

```python
class ProtocolAuthorizationDeniedEvent:
    """
    Event emitted when protocol authorization is denied.
    """
    event_name: str = "protocol_authorization_denied"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "warning"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        protocol_type: str  # Protocol type for which authorization was denied
        principal_id: str  # ID of the principal that was denied
        principal_type: str  # Type of principal (e.g., "user", "service", "agent")
        action: str  # Action that was attempted
        resource: str  # Resource that was accessed
        policy_id: Optional[str] = None  # ID of the policy that denied access
        reason: Optional[str] = None  # Reason for denial
        request_id: Optional[str] = None  # ID of the request
        session_id: Optional[str] = None  # ID of the session
        ip_address: Optional[str] = None  # IP address of the client
        request_details: Dict[str, Any] = {}  # Details about the request that was denied
        context: Dict[str, Any] = {}  # Authorization context
        metadata: Dict[str, Any] = {}  # Additional metadata about the authorization denial
```

**Example Usage:**
```python
# Subscribe to protocol authorization denied events
@event_system.subscribe(ProtocolAuthorizationDeniedEvent.event_name)
def handle_authorization_denial(event: ProtocolAuthorizationDeniedEvent):
    payload = event.payload
    protocol_type = payload.protocol_type
    principal_id = payload.principal_id
    action = payload.action
    resource = payload.resource

    logger.warning(f"Authorization denied for {protocol_type} protocol: {principal_id} attempted {action} on {resource}")

    # Log details for security monitoring
    security_logger.log(
        level="WARNING",
        message=f"Authorization denied for {protocol_type}",
        context={
            "protocol": protocol_type,
            "principal_id": principal_id,
            "principal_type": payload.principal_type,
            "action": action,
            "resource": resource,
            "reason": payload.reason,
            "policy_id": payload.policy_id,
            "timestamp": event.timestamp.isoformat(),
            "request_id": payload.request_id,
            "session_id": payload.session_id
        }
    )

    # Check for potential security violations
    security_monitoring.record_authorization_denial(
        protocol=protocol_type,
        principal_id=principal_id,
        action=action,
        resource=resource,
        timestamp=event.timestamp
    )

    # Check if this is a sensitive resource that requires additional monitoring
    if is_sensitive_resource(resource):
        # Send alert to security team
        security_alerts.send(
            alert_type="sensitive_resource_access_attempt",
            severity="medium",
            details={
                "protocol": protocol_type,
                "principal_id": principal_id,
                "principal_type": payload.principal_type,
                "action": action,
                "resource": resource,
                "timestamp": event.timestamp.isoformat(),
                "ip_address": payload.ip_address
            }
        )

    # If multiple denials for the same principal in a short time, escalate
    recent_denials = security_monitoring.get_recent_denials(
        principal_id=principal_id,
        time_window_seconds=300  # 5 minutes
    )

    if len(recent_denials) >= 5:  # 5 or more denials in 5 minutes
        # Potential privilege escalation attempt
        security_alerts.send(
            alert_type="potential_privilege_escalation",
            severity="high",
            details={
                "protocol": protocol_type,
                "principal_id": principal_id,
                "denial_count": len(recent_denials),
                "resources_attempted": [d["resource"] for d in recent_denials],
                "timestamp": event.timestamp.isoformat()
            }
        )

        # Optionally lock account if configured
        if security_config.get("lock_account_on_suspicious_activity", False):
            security_system.lock_principal(
                principal_id=principal_id,
                reason="Multiple authorization denials in short time period",
                lock_duration_minutes=30
            )
            logger.info(f"Locked account for principal {principal_id} due to suspicious authorization activity")
```

```python
class ProtocolSecurityViolationEvent:
    """
    Event emitted when a protocol security violation is detected.
    """
    event_name: str = "protocol_security_violation"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "error"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        protocol_type: str  # Protocol type where violation was detected
        violation_type: str  # Type of security violation
        description: str  # Description of the violation
        severity: str  # Severity of the violation ("low", "medium", "high", "critical")
        principal_id: Optional[str] = None  # ID of the principal associated with the violation
        ip_address: Optional[str] = None  # IP address associated with the violation
        request_id: Optional[str] = None  # ID of the request
        session_id: Optional[str] = None  # ID of the session
        resource: Optional[str] = None  # Resource associated with the violation
        action_taken: Optional[str] = None  # Action taken in response to the violation
        evidence: Dict[str, Any] = {}  # Evidence of the violation
        metadata: Dict[str, Any] = {}  # Additional metadata about the violation
```

**Example Usage:**
```python
# Example: Emitting a protocol security violation event for a potential MCP message tampering

# Detected message tampering in MCP protocol
def detect_mcp_message_tampering(message: Dict[str, Any], signature: str) -> bool:
    # Verify the message signature
    calculated_signature = calculate_message_signature(message)

    if calculated_signature != signature:
        # Signature doesn't match, potential tampering
        event_system.emit(
            event_name="protocol_security_violation",
            payload=ProtocolSecurityViolationEvent.Payload(
                protocol_type="mcp",
                violation_type="message_tampering",
                description="Message signature verification failed, potential tampering detected",
                severity="high",
                principal_id=message.get("sender_id"),
                ip_address=get_client_ip(),
                request_id=message.get("id"),
                session_id=get_current_session_id(),
                resource=f"capability:{message.get('capability')}",
                action_taken="message_rejected",
                evidence={
                    "expected_signature": calculated_signature,
                    "received_signature": signature,
                    "message_id": message.get("id"),
                    "timestamp": datetime.now().isoformat()
                }
            )
        )

        # Log the violation
        logger.error(f"MCP message tampering detected for message {message.get('id')}")

        # Block the sender temporarily
        security_system.block_sender(
            sender_id=message.get("sender_id"),
            duration_minutes=15,
            reason="Message tampering detected"
        )

        return True  # Tampering detected

    return False  # No tampering detected
```

### Security System → Protocol Layer

#### Methods/Functions
```python
def register_protocol_authentication_handler(protocol_type: str,
                                       handler: ProtocolAuthHandler,
                                       registration_options: Optional[HandlerRegistrationOptions] = None) -> RegistrationResult:
    """
    Register an authentication handler for a specific protocol.

    Args:
        protocol_type: str - Protocol identifier (e.g., "a2a", "mcp", "http")
        handler: ProtocolAuthHandler - Authentication handler implementation
        registration_options: Optional[HandlerRegistrationOptions] - Options for handler registration

    Returns:
        RegistrationResult - Result of handler registration with details

    Raises:
        HandlerRegistrationError - If registration fails
        HandlerAlreadyRegisteredError - If a handler is already registered for the protocol
        InvalidHandlerError - If the handler is invalid
    """
```

**Data Structures:**

```python
class ProtocolAuthHandler:
    """
    Base class for protocol authentication handlers.
    """
    def extract_credentials(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract credentials from a protocol request.

        Args:
            request: Dict[str, Any] - Protocol request data

        Returns:
            Dict[str, Any] - Extracted credentials
        """
        raise NotImplementedError("Subclasses must implement extract_credentials")

    def validate_credentials(self, credentials: Dict[str, Any]) -> AuthenticationResult:
        """
        Validate extracted credentials.

        Args:
            credentials: Dict[str, Any] - Credentials extracted from request

        Returns:
            AuthenticationResult - Result of credential validation
        """
        raise NotImplementedError("Subclasses must implement validate_credentials")

    def handle_authentication_failure(self, request: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """
        Handle authentication failure.

        Args:
            request: Dict[str, Any] - Original request data
            error: Exception - Error that occurred during authentication

        Returns:
            Dict[str, Any] - Response to send back for authentication failure
        """
        raise NotImplementedError("Subclasses must implement handle_authentication_failure")

class HandlerRegistrationOptions:
    """
    Options for handler registration.
    """
    override_existing: bool = False  # Whether to override an existing handler
    handler_priority: int = 100  # Priority of the handler (higher takes precedence)
    enable_immediately: bool = True  # Whether to enable the handler immediately
    failure_strategy: str = "reject"  # What to do on authentication failure ("reject", "anonymize", "redirect")
    protocol_specific_options: Dict[str, Any] = {}  # Protocol-specific options
    custom_failure_response: Optional[Dict[str, Any]] = None  # Custom response for authentication failure
    metadata: Dict[str, Any] = {}  # Additional metadata about the handler

class RegistrationResult:
    """
    Result of handler registration.
    """
    success: bool  # Whether registration was successful
    handler_id: Optional[str] = None  # ID of the registered handler
    protocol_type: str  # Protocol type for which the handler was registered
    registration_time: datetime  # When the handler was registered
    replaced_existing: bool = False  # Whether an existing handler was replaced
    message: Optional[str] = None  # Message about the registration
    error: Optional[str] = None  # Error message if registration failed
    metadata: Dict[str, Any] = {}  # Additional metadata about the registration

class HandlerRegistrationError(Exception):
    """
    Raised when handler registration fails.
    """
    pass

class HandlerAlreadyRegisteredError(Exception):
    """
    Raised when a handler is already registered for a protocol.
    """
    pass

class InvalidHandlerError(Exception):
    """
    Raised when an invalid handler is provided.
    """
    pass
```

**Example Usage:**

```python
# Example 1: Registering an A2A authentication handler

# Define an A2A-specific authentication handler
class A2AAuthHandler(ProtocolAuthHandler):
    def __init__(self, auth_config: Dict[str, Any]):
        self.auth_config = auth_config
        self.jwt_verifier = JWTVerifier(auth_config.get("jwt_verification", {}))

    def extract_credentials(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract JWT credentials from A2A request.
        """
        headers = request.get("headers", {})
        auth_header = headers.get("Authorization", "")

        # Check for Bearer token
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            return {"token_type": "jwt", "token": token}

        # Check for API key
        api_key = headers.get("X-API-Key")
        if api_key:
            return {"token_type": "api_key", "token": api_key}

        # No valid credentials found
        raise MalformedCredentialsError("No valid authentication credentials found in A2A request")

    def validate_credentials(self, credentials: Dict[str, Any]) -> AuthenticationResult:
        """
        Validate A2A credentials.
        """
        token_type = credentials.get("token_type")
        token = credentials.get("token")

        if token_type == "jwt":
            try:
                # Verify JWT token
                jwt_claims = self.jwt_verifier.verify(token)

                # Create security principal from JWT claims
                principal = SecurityPrincipal(
                    id=jwt_claims.get("sub"),
                    name=jwt_claims.get("name", jwt_claims.get("sub")),
                    type=SecurityPrincipalType.USER,
                    auth_level=AuthLevel.MEDIUM,
                    auth_time=datetime.now(),
                    expiration_time=datetime.fromtimestamp(jwt_claims.get("exp")) if "exp" in jwt_claims else None,
                    roles=jwt_claims.get("roles", []),
                    permissions=jwt_claims.get("permissions", []),
                    scope=jwt_claims.get("scope", ""),
                    attributes={
                        "email": jwt_claims.get("email"),
                        "email_verified": jwt_claims.get("email_verified", False),
                        "issuer": jwt_claims.get("iss"),
                        "audience": jwt_claims.get("aud")
                    }
                )

                return AuthenticationResult(
                    is_authenticated=True,
                    principal=principal,
                    auth_mechanism_used=AuthenticationType.JWT,
                    protocol_type="a2a",
                    auth_provider="jwt"
                )

            except Exception as e:
                # JWT validation failed
                return AuthenticationResult(
                    is_authenticated=False,
                    error_code="invalid_token",
                    error_message=str(e),
                    auth_mechanism_used=AuthenticationType.JWT,
                    protocol_type="a2a",
                    auth_provider="jwt"
                )

        elif token_type == "api_key":
            # Validate API key (simplified for example)
            api_key_valid = self.validate_api_key(token)

            if api_key_valid:
                # Get principal information for API key
                principal_info = self.get_principal_for_api_key(token)

                return AuthenticationResult(
                    is_authenticated=True,
                    principal=principal_info,
                    auth_mechanism_used=AuthenticationType.API_KEY,
                    protocol_type="a2a",
                    auth_provider="api_key"
                )
            else:
                return AuthenticationResult(
                    is_authenticated=False,
                    error_code="invalid_api_key",
                    error_message="Invalid API key",
                    auth_mechanism_used=AuthenticationType.API_KEY,
                    protocol_type="a2a",
                    auth_provider="api_key"
                )

        else:
            # Unsupported token type
            return AuthenticationResult(
                is_authenticated=False,
                error_code="unsupported_auth_type",
                error_message=f"Unsupported authentication type: {token_type}",
                auth_mechanism_used=AuthenticationType.NONE,
                protocol_type="a2a",
                auth_provider="none"
            )

    def handle_authentication_failure(self, request: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """
        Handle A2A authentication failure.
        """
        error_message = str(error)
        error_code = "authentication_failed"

        if isinstance(error, MalformedCredentialsError):
            error_code = "malformed_credentials"
        elif isinstance(error, UnsupportedAuthMechanismError):
            error_code = "unsupported_auth_mechanism"

        # Create A2A error response
        return {
            "error": {
                "code": error_code,
                "message": error_message,
                "details": {
                    "request_id": request.get("body", {}).get("messageId", "unknown"),
                    "timestamp": datetime.now().isoformat()
                }
            }
        }

    # Helper methods
    def validate_api_key(self, api_key: str) -> bool:
        # Implementation for API key validation
        pass

    def get_principal_for_api_key(self, api_key: str) -> SecurityPrincipal:
        # Implementation to get principal info for API key
        pass

# Register the A2A authentication handler
try:
    # Create the A2A authentication handler with configuration
    a2a_auth_config = {
        "jwt_verification": {
            "jwks_uri": "https://auth.openmas.org/.well-known/jwks.json",
            "issuer": "https://auth.openmas.org/",
            "audience": "openmas-a2a-api",
            "verify_exp": True,
            "verify_signature": True
        },
        "api_key_validation": {
            "source": "database",
            "database_connection": "api_keys_db",
            "cache_duration_seconds": 300
        }
    }

    a2a_auth_handler = A2AAuthHandler(a2a_auth_config)

    # Configure registration options
    registration_options = HandlerRegistrationOptions(
        override_existing=True,  # Replace any existing handler
        handler_priority=200,  # Higher priority than default
        failure_strategy="reject",  # Reject requests on authentication failure
        protocol_specific_options={
            "support_jwt": True,
            "support_api_key": True,
            "jwt_header_name": "Authorization",
            "api_key_header_name": "X-API-Key"
        }
    )

    # Register the handler
    registration_result = protocol_layer.register_protocol_authentication_handler(
        protocol_type="a2a",
        handler=a2a_auth_handler,
        registration_options=registration_options
    )

    if registration_result.success:
        logger.info(f"Successfully registered A2A authentication handler. Handler ID: {registration_result.handler_id}")

        # Emit event for handler registration
        event_system.emit("protocol_security_handler_registered", {
            "protocol_type": "a2a",
            "handler_type": "authentication",
            "handler_id": registration_result.handler_id,
            "registration_time": registration_result.registration_time.isoformat(),
            "handler_priority": registration_options.handler_priority
        })
    else:
        logger.error(f"Failed to register A2A authentication handler: {registration_result.error}")

except HandlerAlreadyRegisteredError as e:
    logger.warning(f"A2A authentication handler already registered: {str(e)}")
    # Optionally force override
    # registration_options.override_existing = True
    # protocol_layer.register_protocol_authentication_handler(...)

except InvalidHandlerError as e:
    logger.error(f"Invalid A2A authentication handler: {str(e)}")
    # Implement fallback or notify administrators

except Exception as e:
    logger.error(f"Unexpected error registering A2A authentication handler: {str(e)}")
    # Handle general errors


# Example 2: Registering an MCP authentication handler

# Define an MCP-specific authentication handler
class MCPAuthHandler(ProtocolAuthHandler):
    def __init__(self, auth_config: Dict[str, Any]):
        self.auth_config = auth_config
        self.api_key_validator = APIKeyValidator(auth_config.get("api_key_validation", {}))

    def extract_credentials(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract API key credentials from MCP request.
        """
        headers = request.get("headers", {})
        api_key = headers.get("X-MCP-API-Key")

        if api_key:
            return {"token_type": "api_key", "token": api_key}

        # Check for alternative location in header
        api_key = headers.get("X-API-Key")
        if api_key:
            return {"token_type": "api_key", "token": api_key}

        # Check for API key in query parameters
        query_params = request.get("query_params", {})
        api_key = query_params.get("api_key")
        if api_key:
            return {"token_type": "api_key", "token": api_key, "location": "query"}

        # No valid credentials found
        raise MalformedCredentialsError("No valid API key found in MCP request")

    def validate_credentials(self, credentials: Dict[str, Any]) -> AuthenticationResult:
        """
        Validate MCP credentials (primarily API key).
        """
        token = credentials.get("token")

        try:
            # Validate API key
            validation_result = self.api_key_validator.validate(token)

            if validation_result.is_valid:
                # Create security principal from API key info
                principal = SecurityPrincipal(
                    id=validation_result.principal_id,
                    name=validation_result.principal_name,
                    type=SecurityPrincipalType.SERVICE,  # MCP typically uses service accounts
                    auth_level=AuthLevel.MEDIUM,
                    auth_time=datetime.now(),
                    expiration_time=validation_result.expiration_time,
                    roles=validation_result.roles,
                    permissions=validation_result.permissions,
                    scope=validation_result.scope,
                    attributes=validation_result.attributes
                )

                return AuthenticationResult(
                    is_authenticated=True,
                    principal=principal,
                    auth_mechanism_used=AuthenticationType.API_KEY,
                    protocol_type="mcp",
                    auth_provider="api_key",
                    auth_metadata={
                        "key_type": validation_result.key_type,
                        "rate_limit": validation_result.rate_limit,
                        "usage_metrics": validation_result.usage_metrics
                    }
                )
            else:
                return AuthenticationResult(
                    is_authenticated=False,
                    error_code=validation_result.error_code,
                    error_message=validation_result.error_message,
                    auth_mechanism_used=AuthenticationType.API_KEY,
                    protocol_type="mcp",
                    auth_provider="api_key"
                )

        except Exception as e:
            # API key validation failed
            return AuthenticationResult(
                is_authenticated=False,
                error_code="api_key_validation_error",
                error_message=str(e),
                auth_mechanism_used=AuthenticationType.API_KEY,
                protocol_type="mcp",
                auth_provider="api_key"
            )

    def handle_authentication_failure(self, request: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """
        Handle MCP authentication failure.
        """
        error_message = str(error)
        error_code = "authentication_failed"

        if isinstance(error, MalformedCredentialsError):
            error_code = "missing_api_key"
            error_message = "API key is missing or malformed"

        # Create MCP error response
        return {
            "error": {
                "code": error_code,
                "message": error_message,
                "request_id": request.get("body", {}).get("id", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
        }

# Register the MCP authentication handler
try:
    # Create the MCP authentication handler with configuration
    mcp_auth_config = {
        "api_key_validation": {
            "validation_mode": "database",
            "database_connection": "mcp_api_keys",
            "cache_enabled": True,
            "cache_ttl_seconds": 300,
            "rate_limiting": {
                "enabled": True,
                "default_rate": 100,  # requests per minute
                "per_key_configuration": True
            }
        }
    }

    mcp_auth_handler = MCPAuthHandler(mcp_auth_config)

    # Configure registration options
    registration_options = HandlerRegistrationOptions(
        override_existing=False,  # Don't replace existing handler
        handler_priority=150,
        protocol_specific_options={
            "header_name": "X-MCP-API-Key",
            "alternative_header": "X-API-Key",
            "allow_query_param": True,
            "apply_rate_limiting": True
        }
    )

    # Register the handler
    registration_result = protocol_layer.register_protocol_authentication_handler(
        protocol_type="mcp",
        handler=mcp_auth_handler,
        registration_options=registration_options
    )

    if registration_result.success:
        logger.info(f"Successfully registered MCP authentication handler. Handler ID: {registration_result.handler_id}")
    else:
        logger.error(f"Failed to register MCP authentication handler: {registration_result.error}")

except Exception as e:
    logger.error(f"Error registering MCP authentication handler: {str(e)}")
```

```python
def register_protocol_security_validator(protocol_type: str,
                                      validator: ProtocolSecurityValidator,
                                      registration_options: Optional[ValidatorRegistrationOptions] = None) -> RegistrationResult:
    """
    Register a security validator for a specific protocol.

    Args:
        protocol_type: str - Protocol identifier (e.g., "a2a", "mcp", "http")
        validator: ProtocolSecurityValidator - Security validator implementation
        registration_options: Optional[ValidatorRegistrationOptions] - Options for validator registration

    Returns:
        RegistrationResult - Result of validator registration with details

    Raises:
        ValidatorRegistrationError - If registration fails
        ValidatorAlreadyRegisteredError - If a validator is already registered for the protocol
        InvalidValidatorError - If the validator is invalid
    """
```

**Data Structures:**

```python
class ProtocolSecurityValidator:
    """
    Base class for protocol security validators.
    """
    def validate_message_integrity(self, message: Dict[str, Any]) -> ValidationResult:
        """
        Validate the integrity of a protocol message.

        Args:
            message: Dict[str, Any] - Protocol message to validate

        Returns:
            ValidationResult - Result of message integrity validation
        """
        raise NotImplementedError("Subclasses must implement validate_message_integrity")

    def validate_security_constraints(self, message: Dict[str, Any], principal: SecurityPrincipal) -> ValidationResult:
        """
        Validate security constraints for a protocol message.

        Args:
            message: Dict[str, Any] - Protocol message to validate
            principal: SecurityPrincipal - The authenticated principal

        Returns:
            ValidationResult - Result of security constraints validation
        """
        raise NotImplementedError("Subclasses must implement validate_security_constraints")

    def handle_validation_failure(self, message: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """
        Handle validation failure.

        Args:
            message: Dict[str, Any] - Original message
            error: Exception - Error that occurred during validation

        Returns:
            Dict[str, Any] - Response to send back for validation failure
        """
        raise NotImplementedError("Subclasses must implement handle_validation_failure")

class ValidatorRegistrationOptions:
    """
    Options for validator registration.
    """
    override_existing: bool = False  # Whether to override an existing validator
    validator_priority: int = 100  # Priority of the validator (higher takes precedence)
    enable_immediately: bool = True  # Whether to enable the validator immediately
    failure_strategy: str = "reject"  # What to do on validation failure ("reject", "sanitize", "log_only")
    protocol_specific_options: Dict[str, Any] = {}  # Protocol-specific options
    custom_failure_response: Optional[Dict[str, Any]] = None  # Custom response for validation failure
    metadata: Dict[str, Any] = {}  # Additional metadata about the validator

class ValidationResult:
    """
    Result of message validation.
    """
    is_valid: bool  # Whether the message is valid
    error_code: Optional[str] = None  # Error code if validation failed
    error_message: Optional[str] = None  # Error message if validation failed
    validation_time: datetime  # When the validation was performed
    validator_id: str  # ID of the validator that performed the validation
    sanitized_message: Optional[Dict[str, Any]] = None  # Sanitized message if applicable
    security_level: str = "standard"  # Security level of the validation ("basic", "standard", "strict")
    validation_details: Dict[str, Any] = {}  # Additional details about the validation
    metadata: Dict[str, Any] = {}  # Additional metadata about the validation

class ValidatorRegistrationError(Exception):
    """
    Raised when validator registration fails.
    """
    pass

class ValidatorAlreadyRegisteredError(Exception):
    """
    Raised when a validator is already registered for a protocol.
    """
    pass

class InvalidValidatorError(Exception):
    """
    Raised when an invalid validator is provided.
    """
    pass
```

**Example Usage:**

```python
# Example 1: Registering an MCP security validator

# Define an MCP-specific security validator
class MCPSecurityValidator(ProtocolSecurityValidator):
    def __init__(self, validator_config: Dict[str, Any]):
        self.validator_config = validator_config
        self.signature_verifier = SignatureVerifier(validator_config.get("signature_verification", {}))
        self.content_validator = ContentValidator(validator_config.get("content_validation", {}))

    def validate_message_integrity(self, message: Dict[str, Any]) -> ValidationResult:
        """
        Validate the integrity of an MCP message.
        """
        try:
            # Extract message signature
            headers = message.get("headers", {})
            signature = headers.get("X-MCP-Signature")

            if not signature:
                return ValidationResult(
                    is_valid=False,
                    error_code="missing_signature",
                    error_message="Message signature is missing",
                    validation_time=datetime.now(),
                    validator_id="mcp_security_validator"
                )

            # Verify signature
            payload = message.get("body", {})
            sender_id = payload.get("sender_id")

            # Get sender's public key or shared secret
            key_info = self.get_key_for_sender(sender_id)

            if not key_info:
                return ValidationResult(
                    is_valid=False,
                    error_code="unknown_sender",
                    error_message=f"No key information found for sender: {sender_id}",
                    validation_time=datetime.now(),
                    validator_id="mcp_security_validator"
                )

            # Verify signature using the sender's key
            is_valid = self.signature_verifier.verify(
                payload=json.dumps(payload),
                signature=signature,
                key_info=key_info
            )

            if not is_valid:
                return ValidationResult(
                    is_valid=False,
                    error_code="invalid_signature",
                    error_message="Message signature is invalid",
                    validation_time=datetime.now(),
                    validator_id="mcp_security_validator",
                    validation_details={
                        "sender_id": sender_id,
                        "key_id": key_info.get("key_id")
                    }
                )

            # Message integrity is valid
            return ValidationResult(
                is_valid=True,
                validation_time=datetime.now(),
                validator_id="mcp_security_validator",
                security_level="standard",
                validation_details={
                    "sender_id": sender_id,
                    "key_id": key_info.get("key_id"),
                    "signature_algorithm": key_info.get("algorithm")
                }
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_code="validation_error",
                error_message=str(e),
                validation_time=datetime.now(),
                validator_id="mcp_security_validator"
            )

    def validate_security_constraints(self, message: Dict[str, Any], principal: SecurityPrincipal) -> ValidationResult:
        """
        Validate security constraints for an MCP message.
        """
        try:
            payload = message.get("body", {})
            message_type = payload.get("type")
            content = payload.get("content", {})
            capability = payload.get("capability")

            # Validate content based on message type
            if message_type == "capability_invocation":
                # Validate capability invocation
                if not capability:
                    return ValidationResult(
                        is_valid=False,
                        error_code="missing_capability",
                        error_message="Capability name is required for capability_invocation messages",
                        validation_time=datetime.now(),
                        validator_id="mcp_security_validator"
                    )

                # Check if principal has permission to invoke this capability
                has_permission = self.check_capability_permission(principal, capability)

                if not has_permission:
                    return ValidationResult(
                        is_valid=False,
                        error_code="capability_not_authorized",
                        error_message=f"Principal {principal.id} is not authorized to invoke capability {capability}",
                        validation_time=datetime.now(),
                        validator_id="mcp_security_validator",
                        validation_details={
                            "principal_id": principal.id,
                            "capability": capability,
                            "principal_roles": principal.roles
                        }
                    )

                # Validate capability parameters
                params_validation = self.content_validator.validate_capability_params(
                    capability=capability,
                    params=content.get("params", {})
                )

                if not params_validation.is_valid:
                    return ValidationResult(
                        is_valid=False,
                        error_code="invalid_capability_params",
                        error_message=params_validation.error_message,
                        validation_time=datetime.now(),
                        validator_id="mcp_security_validator",
                        validation_details=params_validation.validation_details
                    )

            elif message_type == "resource_access":
                # Validate resource access
                resource_id = content.get("resource_id")
                access_type = content.get("access_type")

                if not resource_id or not access_type:
                    return ValidationResult(
                        is_valid=False,
                        error_code="missing_resource_info",
                        error_message="Resource ID and access type are required for resource_access messages",
                        validation_time=datetime.now(),
                        validator_id="mcp_security_validator"
                    )

                # Check if principal has permission to access this resource
                has_permission = self.check_resource_permission(principal, resource_id, access_type)

                if not has_permission:
                    return ValidationResult(
                        is_valid=False,
                        error_code="resource_not_authorized",
                        error_message=f"Principal {principal.id} is not authorized for {access_type} access to resource {resource_id}",
                        validation_time=datetime.now(),
                        validator_id="mcp_security_validator",
                        validation_details={
                            "principal_id": principal.id,
                            "resource_id": resource_id,
                            "access_type": access_type,
                            "principal_roles": principal.roles
                        }
                    )

            # Additional security checks based on configuration
            if self.validator_config.get("enable_content_scanning", False):
                # Scan message content for security threats
                content_scan_result = self.scan_content_for_threats(content)

                if content_scan_result.has_threats:
                    return ValidationResult(
                        is_valid=False,
                        error_code="security_threat_detected",
                        error_message=f"Security threat detected: {content_scan_result.threat_type}",
                        validation_time=datetime.now(),
                        validator_id="mcp_security_validator",
                        validation_details={
                            "threat_type": content_scan_result.threat_type,
                            "threat_description": content_scan_result.threat_description,
                            "threat_severity": content_scan_result.threat_severity
                        }
                    )

            # All security constraints passed
            return ValidationResult(
                is_valid=True,
                validation_time=datetime.now(),
                validator_id="mcp_security_validator",
                security_level=self.validator_config.get("security_level", "standard"),
                validation_details={
                    "message_type": message_type,
                    "principal_id": principal.id,
                    "checks_performed": ["signature", "permissions", "content"]
                }
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_code="validation_error",
                error_message=str(e),
                validation_time=datetime.now(),
                validator_id="mcp_security_validator"
            )

    def handle_validation_failure(self, message: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """
        Handle MCP validation failure.
        """
        error_message = str(error)
        error_code = "validation_failed"

        if isinstance(error, SignatureVerificationError):
            error_code = "signature_verification_failed"
        elif isinstance(error, ContentValidationError):
            error_code = "content_validation_failed"
        elif isinstance(error, SecurityConstraintViolationError):
            error_code = "security_constraint_violation"

        # Create MCP error response
        return {
            "error": {
                "code": error_code,
                "message": error_message,
                "request_id": message.get("body", {}).get("id", "unknown"),
                "timestamp": datetime.now().isoformat()
            }
        }

    # Helper methods
    def get_key_for_sender(self, sender_id: str) -> Dict[str, Any]:
        # Implementation to get key information for a sender
        pass

    def check_capability_permission(self, principal: SecurityPrincipal, capability: str) -> bool:
        # Implementation to check if principal has permission to invoke capability
        pass

    def check_resource_permission(self, principal: SecurityPrincipal, resource_id: str, access_type: str) -> bool:
        # Implementation to check if principal has permission to access resource
        pass

    def scan_content_for_threats(self, content: Dict[str, Any]) -> ContentScanResult:
        # Implementation to scan content for security threats
        pass

# Register the MCP security validator
try:
    # Create the MCP security validator with configuration
    mcp_validator_config = {
        "signature_verification": {
            "required": True,
            "algorithms": ["RS256", "ES256", "HS256"],
            "key_provider": "key_management_service"
        },
        "content_validation": {
            "capability_schema_validation": True,
            "input_sanitization": True,
            "max_payload_size_kb": 1024
        },
        "enable_content_scanning": True,
        "security_level": "standard"
    }

    mcp_security_validator = MCPSecurityValidator(mcp_validator_config)

    # Configure registration options
    registration_options = ValidatorRegistrationOptions(
        override_existing=False,  # Don't replace existing validator
        validator_priority=200,  # High priority
        failure_strategy="reject",  # Reject requests on validation failure
        protocol_specific_options={
            "signature_header": "X-MCP-Signature",
            "timestamp_header": "X-MCP-Timestamp",
            "require_timestamp": True,
            "timestamp_tolerance_seconds": 300  # 5 minutes
        }
    )

    # Register the validator
    registration_result = protocol_layer.register_protocol_security_validator(
        protocol_type="mcp",
        validator=mcp_security_validator,
        registration_options=registration_options
    )

    if registration_result.success:
        logger.info(f"Successfully registered MCP security validator. Validator ID: {registration_result.handler_id}")

        # Emit event for validator registration
        event_system.emit("protocol_security_validator_registered", {
            "protocol_type": "mcp",
            "validator_id": registration_result.handler_id,
            "registration_time": registration_result.registration_time.isoformat(),
            "security_level": mcp_validator_config["security_level"]
        })
    else:
        logger.error(f"Failed to register MCP security validator: {registration_result.error}")

except Exception as e:
    logger.error(f"Error registering MCP security validator: {str(e)}")


# Example 2: Registering an A2A security validator

# Define an A2A-specific security validator
class A2ASecurityValidator(ProtocolSecurityValidator):
    def __init__(self, validator_config: Dict[str, Any]):
        self.validator_config = validator_config
        # Initialize A2A-specific validation components

    def validate_message_integrity(self, message: Dict[str, Any]) -> ValidationResult:
        # A2A-specific message integrity validation
        # Similar structure to MCP validator but with A2A-specific logic
        pass

    def validate_security_constraints(self, message: Dict[str, Any], principal: SecurityPrincipal) -> ValidationResult:
        # A2A-specific security constraints validation
        # Similar structure to MCP validator but with A2A-specific logic
        pass

    def handle_validation_failure(self, message: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        # A2A-specific validation failure handling
        # Similar structure to MCP validator but with A2A-specific error response format
        pass

# Register the A2A security validator
try:
    # Create the A2A security validator with configuration
    a2a_validator_config = {
        # A2A-specific configuration
    }

    a2a_security_validator = A2ASecurityValidator(a2a_validator_config)

    # Configure registration options
    registration_options = ValidatorRegistrationOptions(
        # A2A-specific registration options
    )

    # Register the validator
    registration_result = protocol_layer.register_protocol_security_validator(
        protocol_type="a2a",
        validator=a2a_security_validator,
        registration_options=registration_options
    )

    if registration_result.success:
        logger.info(f"Successfully registered A2A security validator. Validator ID: {registration_result.handler_id}")
    else:
        logger.error(f"Failed to register A2A security validator: {registration_result.error}")
except Exception as e:
    logger.error(f"Error registering A2A security validator: {str(e)}")

```python
def notify_security_policy_update(protocol_type: str,
                             policy_update: SecurityPolicyUpdate,
                             notification_options: Optional[PolicyNotificationOptions] = None) -> PolicyUpdateResult:
    """
    Notify Protocol Layer of security policy updates.

    Args:
        protocol_type: str - Protocol identifier (e.g., "a2a", "mcp", "http")
        policy_update: SecurityPolicyUpdate - Security policy update details
        notification_options: Optional[PolicyNotificationOptions] - Options for policy notification

    Returns:
        PolicyUpdateResult - Result of policy update notification with details

    Raises:
        InvalidProtocolError - If the protocol type is invalid
        InvalidPolicyUpdateError - If the policy update is invalid
        PolicyUpdateRejectedError - If the policy update is rejected by the protocol layer
    """
```

**Data Structures:**

```python
class SecurityPolicyUpdateType(Enum):
    """
    Types of security policy updates.
    """
    CREATE = "create"  # Create a new policy
    MODIFY = "modify"  # Modify an existing policy
    DELETE = "delete"  # Delete an existing policy
    ENABLE = "enable"  # Enable a disabled policy
    DISABLE = "disable"  # Disable an enabled policy
    REPLACE = "replace"  # Replace an existing policy completely
    VERSION = "version"  # Update policy version

class SecurityPolicyType(Enum):
    """
    Types of security policies.
    """
    AUTHENTICATION = "authentication"  # Authentication policies
    AUTHORIZATION = "authorization"  # Authorization policies
    ENCRYPTION = "encryption"  # Encryption policies
    RATE_LIMITING = "rate_limiting"  # Rate limiting policies
    INPUT_VALIDATION = "input_validation"  # Input validation policies
    IP_FILTERING = "ip_filtering"  # IP filtering policies
    CONTENT_FILTERING = "content_filtering"  # Content filtering policies
    AUDIT = "audit"  # Audit policies

class SecurityPolicyScope(Enum):
    """
    Scopes of security policies.
    """
    GLOBAL = "global"  # Applies to all protocols
    PROTOCOL = "protocol"  # Applies to a specific protocol
    ENDPOINT = "endpoint"  # Applies to a specific endpoint
    RESOURCE = "resource"  # Applies to a specific resource
    PRINCIPAL = "principal"  # Applies to a specific principal
    ACTION = "action"  # Applies to a specific action

class SecurityPolicyStatus(Enum):
    """
    Status of security policies.
    """
    ACTIVE = "active"  # Policy is active and enforced
    INACTIVE = "inactive"  # Policy is inactive and not enforced
    PENDING = "pending"  # Policy is pending activation
    DEPRECATED = "deprecated"  # Policy is deprecated but still enforced
    ARCHIVED = "archived"  # Policy is archived and not enforced

class SecurityPolicyPriority(Enum):
    """
    Priority levels of security policies.
    """
    CRITICAL = 100  # Critical priority, evaluated first
    HIGH = 75  # High priority
    MEDIUM = 50  # Medium priority
    LOW = 25  # Low priority
    DEFAULT = 0  # Default priority, evaluated last

class SecurityPolicyUpdate:
    """
    Security policy update details.
    """
    policy_id: str  # ID of the policy being updated
    update_type: SecurityPolicyUpdateType  # Type of update
    policy_type: SecurityPolicyType  # Type of security policy
    policy_scope: SecurityPolicyScope  # Scope of the policy
    policy_name: str  # Name of the policy
    policy_description: Optional[str] = None  # Description of the policy
    policy_version: str = "1.0.0"  # Version of the policy
    policy_status: SecurityPolicyStatus = SecurityPolicyStatus.ACTIVE  # Status of the policy
    policy_priority: SecurityPolicyPriority = SecurityPolicyPriority.DEFAULT  # Priority of the policy
    policy_data: Dict[str, Any] = {}  # Actual policy data/rules
    effective_from: Optional[datetime] = None  # When the policy becomes effective
    effective_until: Optional[datetime] = None  # When the policy expires
    applies_to_principals: List[str] = []  # Principals this policy applies to
    applies_to_resources: List[str] = []  # Resources this policy applies to
    applies_to_actions: List[str] = []  # Actions this policy applies to
    metadata: Dict[str, Any] = {}  # Additional metadata about the policy

class PolicyNotificationOptions:
    """
    Options for policy notification.
    """
    immediate_application: bool = True  # Whether to apply the policy immediately
    force_update: bool = False  # Whether to force the update even if there are conflicts
    cascade_update: bool = False  # Whether to cascade the update to dependent policies
    notify_affected_principals: bool = False  # Whether to notify affected principals
    require_acknowledgment: bool = False  # Whether to require acknowledgment of the update
    update_reason: Optional[str] = None  # Reason for the update
    update_source: Optional[str] = None  # Source of the update
    metadata: Dict[str, Any] = {}  # Additional metadata about the notification

class PolicyUpdateResult:
    """
    Result of policy update notification.
    """
    success: bool  # Whether the notification was successful
    update_id: Optional[str] = None  # ID of the update
    policy_id: str  # ID of the policy that was updated
    update_time: datetime  # When the update was processed
    effective_time: Optional[datetime] = None  # When the update becomes effective
    affected_principals_count: int = 0  # Number of principals affected by the update
    affected_resources_count: int = 0  # Number of resources affected by the update
    message: Optional[str] = None  # Message about the update
    error: Optional[str] = None  # Error message if notification failed
    acknowledgment_required: bool = False  # Whether acknowledgment is required
    acknowledgment_id: Optional[str] = None  # ID for acknowledgment if required
    metadata: Dict[str, Any] = {}  # Additional metadata about the update result

class InvalidProtocolError(Exception):
    """
    Raised when an invalid protocol type is provided.
    """
    pass

class InvalidPolicyUpdateError(Exception):
    """
    Raised when an invalid policy update is provided.
    """
    pass

class PolicyUpdateRejectedError(Exception):
    """
    Raised when a policy update is rejected by the protocol layer.
    """
    pass
```

**Example Usage:**

```python
# Example 1: Updating authentication policy for A2A protocol

try:
    # Create a policy update for A2A authentication
    auth_policy_update = SecurityPolicyUpdate(
        policy_id="a2a-auth-policy-1",
        update_type=SecurityPolicyUpdateType.MODIFY,
        policy_type=SecurityPolicyType.AUTHENTICATION,
        policy_scope=SecurityPolicyScope.PROTOCOL,
        policy_name="A2A JWT Authentication Policy",
        policy_description="Updated JWT authentication requirements for A2A protocol",
        policy_version="1.2.0",  # Incremented version
        policy_status=SecurityPolicyStatus.ACTIVE,
        policy_priority=SecurityPolicyPriority.HIGH,
        policy_data={
            "auth_mechanisms": ["jwt", "api_key"],
            "jwt_requirements": {
                "algorithms": ["RS256"],
                "issuer": "https://auth.openmas.org/",
                "audience": "openmas-a2a-api",
                "require_exp": True,
                "max_token_age_seconds": 3600,  # 1 hour
                "require_auth_time": True,
                "auth_time_tolerance_seconds": 300  # 5 minutes
            },
            "api_key_requirements": {
                "header_name": "X-API-Key",
                "key_format": "^[a-zA-Z0-9]{32}$",  # Regex for key format
                "require_key_validation": True
            },
            "minimum_auth_level": "medium",
            "allow_anonymous": False,
            "require_tls": True
        },
        effective_from=datetime.now(),
        metadata={
            "last_updated_by": "security_admin",
            "update_reason": "Strengthen JWT validation requirements",
            "approved_by": "security_team",
            "risk_assessment": "low"
        }
    )

    # Configure notification options
    notification_options = PolicyNotificationOptions(
        immediate_application=True,  # Apply immediately
        force_update=False,  # Don't force if there are conflicts
        notify_affected_principals=True,  # Notify affected principals
        update_reason="Enhanced security for JWT validation",
        update_source="security_compliance_review"
    )

    # Notify protocol layer of the policy update
    result = protocol_layer.notify_security_policy_update(
        protocol_type="a2a",
        policy_update=auth_policy_update,
        notification_options=notification_options
    )

    if result.success:
        logger.info(f"Successfully updated A2A authentication policy. Update ID: {result.update_id}")
        logger.info(f"Policy will be effective from: {result.effective_time}")

        # If acknowledgment is required, store the acknowledgment ID
        if result.acknowledgment_required:
            logger.info(f"Acknowledgment required. ID: {result.acknowledgment_id}")

            # Store acknowledgment requirement for later verification
            acknowledgment_registry.add_pending_acknowledgment(
                acknowledgment_id=result.acknowledgment_id,
                policy_id=auth_policy_update.policy_id,
                protocol_type="a2a",
                deadline=datetime.now() + timedelta(hours=24)  # 24-hour deadline
            )

        # Emit event for policy update
        event_system.emit("security_policy_updated", {
            "policy_id": auth_policy_update.policy_id,
            "policy_type": auth_policy_update.policy_type.value,
            "protocol_type": "a2a",
            "update_type": auth_policy_update.update_type.value,
            "update_time": result.update_time.isoformat(),
            "affected_principals": result.affected_principals_count
        })
    else:
        logger.error(f"Failed to update A2A authentication policy: {result.error}")

except InvalidProtocolError as e:
    logger.error(f"Invalid protocol type: {str(e)}")
    # Handle invalid protocol error

except InvalidPolicyUpdateError as e:
    logger.error(f"Invalid policy update: {str(e)}")
    # Handle invalid policy update error

except PolicyUpdateRejectedError as e:
    logger.error(f"Policy update rejected: {str(e)}")
    # Handle rejected policy update

except Exception as e:
    logger.error(f"Unexpected error updating A2A authentication policy: {str(e)}")
    # Handle general errors


# Example 2: Creating a new rate limiting policy for MCP protocol

try:
    # Create a new rate limiting policy for MCP
    rate_limit_policy = SecurityPolicyUpdate(
        policy_id="mcp-rate-limit-policy-1",  # New policy ID
        update_type=SecurityPolicyUpdateType.CREATE,  # Creating a new policy
        policy_type=SecurityPolicyType.RATE_LIMITING,
        policy_scope=SecurityPolicyScope.PROTOCOL,
        policy_name="MCP API Rate Limiting Policy",
        policy_description="Rate limiting for MCP API to prevent abuse",
        policy_version="1.0.0",  # Initial version
        policy_status=SecurityPolicyStatus.ACTIVE,
        policy_priority=SecurityPolicyPriority.MEDIUM,
        policy_data={
            "default_rate": {
                "requests_per_minute": 60,  # 1 request per second on average
                "burst": 10  # Allow bursts of up to 10 requests
            },
            "tier_rates": {
                "basic": {
                    "requests_per_minute": 30,
                    "burst": 5
                },
                "premium": {
                    "requests_per_minute": 300,
                    "burst": 30
                },
                "enterprise": {
                    "requests_per_minute": 600,
                    "burst": 60
                }
            },
            "scope": "per_principal",  # Rate limits are per principal
            "exceed_action": "reject",  # Reject requests that exceed limits
            "headers": {
                "remaining": "X-RateLimit-Remaining",
                "limit": "X-RateLimit-Limit",
                "reset": "X-RateLimit-Reset"
            },
            "exempted_principals": ["system", "monitoring"],  # Principals exempt from rate limiting
            "per_endpoint_overrides": {
                "/high-traffic-endpoint": {
                    "requests_per_minute": 30,  # Lower limit for high-traffic endpoints
                    "burst": 5
                }
            }
        },
        effective_from=datetime.now() + timedelta(days=7),  # Effective in 7 days
        metadata={
            "created_by": "api_team",
            "creation_reason": "Prevent API abuse and ensure fair usage",
            "approved_by": "operations_team",
            "risk_assessment": "low"
        }
    )

    # Configure notification options
    notification_options = PolicyNotificationOptions(
        immediate_application=False,  # Don't apply immediately, respect effective_from
        notify_affected_principals=True,  # Notify affected principals
        require_acknowledgment=True,  # Require acknowledgment from principals
        update_reason="Implementing rate limiting to ensure fair API usage",
        update_source="api_governance_team"
    )

    # Notify protocol layer of the new policy
    result = protocol_layer.notify_security_policy_update(
        protocol_type="mcp",
        policy_update=rate_limit_policy,
        notification_options=notification_options
    )

    if result.success:
        logger.info(f"Successfully created MCP rate limiting policy. Update ID: {result.update_id}")
        logger.info(f"Policy will be effective from: {result.effective_time}")

        # Since this affects many principals, prepare notifications
        if result.affected_principals_count > 0:
            # Send notifications to affected principals
            notification_service.send_policy_notification(
                principals=result.metadata.get("affected_principals", []),
                notification_type="policy_update",
                title="New Rate Limiting Policy for MCP API",
                message=f"A new rate limiting policy will be effective from {result.effective_time.strftime('%Y-%m-%d')}. "
                        f"Please review and acknowledge the changes.",
                details={
                    "policy_id": rate_limit_policy.policy_id,
                    "policy_name": rate_limit_policy.policy_name,
                    "policy_description": rate_limit_policy.policy_description,
                    "effective_from": result.effective_time.isoformat(),
                    "acknowledgment_id": result.acknowledgment_id,
                    "acknowledgment_deadline": (datetime.now() + timedelta(days=5)).isoformat()  # 5-day deadline
                }
            )

            logger.info(f"Sent notifications to {result.affected_principals_count} affected principals")
    else:
        logger.error(f"Failed to create MCP rate limiting policy: {result.error}")

except Exception as e:
    logger.error(f"Error creating MCP rate limiting policy: {str(e)}")
```

#### Events

```python
class ProtocolSecurityHandlerRegisteredEvent:
    """
    Event emitted when a protocol security handler is registered.
    """
    event_name: str = "protocol_security_handler_registered"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        protocol_type: str  # Protocol type for which the handler was registered
        handler_type: str  # Type of handler ("authentication", "authorization", "validation")
        handler_id: str  # ID of the registered handler
        registration_time: datetime  # When the handler was registered
        handler_priority: int  # Priority of the handler
        replaced_existing: bool = False  # Whether an existing handler was replaced
        enabled: bool = True  # Whether the handler is enabled
        handler_name: Optional[str] = None  # Name of the handler if available
        handler_version: Optional[str] = None  # Version of the handler if available
        protocol_specific_options: Dict[str, Any] = {}  # Protocol-specific options
    """
    Event emitted when a security policy is applied to a protocol.
    """
    event_name: str = "security_policy_applied"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        protocol_type: str  # Protocol type to which the policy was applied
        policy_id: str  # ID of the applied policy
        policy_type: str  # Type of security policy ("authentication", "authorization", "rate_limiting", etc.)
        policy_name: str  # Name of the policy
        policy_version: str  # Version of the policy
        policy_status: str  # Status of the policy ("active", "inactive", "pending", etc.)
        application_time: datetime  # When the policy was applied
        effective_time: Optional[datetime] = None  # When the policy becomes effective
        expiration_time: Optional[datetime] = None  # When the policy expires
        affected_principals_count: int = 0  # Number of principals affected by the policy
        affected_resources_count: int = 0  # Number of resources affected by the policy
        applied_by: Optional[str] = None  # Who applied the policy
        policy_data: Dict[str, Any] = {}  # Policy data/rules
        policy_scope: str  # Scope of the policy ("global", "protocol", "endpoint", etc.)
        policy_priority: int  # Priority of the policy
        replaced_policy_id: Optional[str] = None  # ID of the policy that was replaced
        metadata: Dict[str, Any] = {}  # Additional metadata about the policy application

        class PolicyDetails:
            """
            Detailed information about the security policy.
            """
            rules: List[Dict[str, Any]] = []  # List of specific policy rules
            conditions: Dict[str, Any] = {}  # Conditions under which the policy applies
            exceptions: List[Dict[str, Any]] = []  # Exceptions to the policy
            action_on_violation: str = "deny"  # Action to take on policy violation
            notification_level: str = "warning"  # Level of notification on policy violation
            audit_level: str = "standard"  # Level of auditing for the policy
            reasoning_approach_constraints: Dict[str, Any] = {}  # Constraints specific to reasoning approaches

        class ProtocolSpecificDetails:
            """
            Protocol-specific details about the security policy application.
            """
            a2a_specific: Dict[str, Any] = {}  # A2A protocol-specific details
            mcp_specific: Dict[str, Any] = {}  # MCP protocol-specific details
            http_specific: Dict[str, Any] = {}  # HTTP protocol-specific details
            mqtt_specific: Dict[str, Any] = {}  # MQTT protocol-specific details
            grpc_specific: Dict[str, Any] = {}  # gRPC protocol-specific details
```

**Example Usage:**
```python
# Subscribe to security policy applied events
@event_system.subscribe(SecurityPolicyAppliedEvent.event_name)
def handle_security_policy_application(event: SecurityPolicyAppliedEvent):
    payload = event.payload
    protocol_type = payload.protocol_type
    policy_id = payload.policy_id
    policy_type = payload.policy_type

    logger.info(f"Security policy applied to {protocol_type} protocol: {policy_type} (ID: {policy_id})")

    # Record policy application in observability system
    observability_system.record_policy_application(
        timestamp=event.timestamp,
        protocol_type=protocol_type,
        policy_id=policy_id,
        policy_type=policy_type,
        policy_name=payload.policy_name,
        policy_version=payload.policy_version,
        affected_principals=payload.affected_principals_count,
        affected_resources=payload.affected_resources_count
    )

    # Log metric for security policy application
    metrics_system.increment(
        metric_name="security_policies_applied",
        value=1,
        dimensions={
            "protocol": protocol_type,
            "policy_type": policy_type,
            "policy_id": policy_id
        }
    )

    # If policy is effective immediately, perform additional actions
    if payload.effective_time is None or payload.effective_time <= datetime.now():
        logger.info(f"Policy {policy_id} is effective immediately")

        # Record policy effectiveness
        observability_system.record_policy_effectiveness(
            timestamp=datetime.now(),
            protocol_type=protocol_type,
            policy_id=policy_id,
            status="effective"
        )

        # If notifications are needed for affected principals
        if payload.affected_principals_count > 0 and payload.metadata.get("notify_principals", False):
            # Send notifications to affected principals
            notification_service.send_policy_notification(
                principals=payload.metadata.get("affected_principals", []),
                notification_type="policy_effective",
                title=f"Security Policy Now Effective: {payload.policy_name}",
                message=f"A security policy affecting your access to {protocol_type} protocol resources is now effective.",
                details={
                    "policy_id": policy_id,
                    "policy_name": payload.policy_name,
                    "policy_type": policy_type,
                    "effective_from": datetime.now().isoformat(),
                    "policy_scope": payload.policy_scope
                }
            )
    else:
        # Schedule effectiveness tracking for future activation
        scheduler.schedule_task(
            task="track_policy_effectiveness",
            execution_time=payload.effective_time,
            params={
                "protocol_type": protocol_type,
                "policy_id": policy_id,
                "policy_type": policy_type
            }
        )

        logger.info(f"Scheduled effectiveness tracking for policy {policy_id} at {payload.effective_time}")
```

```python
class SecurityPolicyUpdatedEvent:
    """
    Event emitted when a security policy is updated.
    """
    event_name: str = "security_policy_updated"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "info"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        protocol_type: str  # Protocol type for which the policy was updated
        policy_id: str  # ID of the updated policy
        policy_type: str  # Type of security policy
        update_type: str  # Type of update ("create", "modify", "delete", "enable", "disable")
        update_time: datetime  # When the update was performed
        updated_by: Optional[str] = None  # Who updated the policy
        previous_version: Optional[str] = None  # Previous version of the policy
        new_version: str  # New version of the policy
        changes: Dict[str, Any] = {}  # Changes made to the policy
        update_reason: Optional[str] = None  # Reason for the update
        effective_time: Optional[datetime] = None  # When the update becomes effective
        affected_principals_count: int = 0  # Number of principals affected by the update
        requires_acknowledgment: bool = False  # Whether acknowledgment is required
        acknowledgment_deadline: Optional[datetime] = None  # Deadline for acknowledgment
        metadata: Dict[str, Any] = {}  # Additional metadata about the update
```

**Example Usage:**
```python
# Example: Emitting a security policy updated event for A2A authentication policy

def update_authentication_policy(policy_id: str, protocol_type: str, changes: Dict[str, Any]) -> bool:
    # Update the policy in the database or configuration
    policy = policy_repository.get_policy(policy_id)

    if policy is None:
        logger.error(f"Cannot update policy {policy_id}: policy not found")
        return False

    # Apply changes to the policy
    previous_version = policy.version
    updated_policy = policy_repository.update_policy(policy_id, changes)

    if updated_policy is None:
        logger.error(f"Failed to update policy {policy_id}")
        return False

    # Emit policy updated event
    event_system.emit(
        event_name="security_policy_updated",
        payload=SecurityPolicyUpdatedEvent.Payload(
            protocol_type=protocol_type,
            policy_id=policy_id,
            policy_type="authentication",
            update_type="modify",
            update_time=datetime.now(),
            updated_by=get_current_user_id(),
            previous_version=previous_version,
            new_version=updated_policy.version,
            changes=changes,
            update_reason="Enhanced security requirements",
            effective_time=updated_policy.effective_from,
            affected_principals_count=policy_analysis.count_affected_principals(policy_id),
            requires_acknowledgment=updated_policy.requires_acknowledgment,
            acknowledgment_deadline=updated_policy.acknowledgment_deadline,
            metadata={
                "risk_assessment": "low",
                "approved_by": "security_team",
                "compliance_requirement": "SOC2"
            }
        )
    )

    logger.info(f"Security policy {policy_id} updated and event emitted")
    return True
```

```python
class SecurityViolationEvent:
    """
    Event emitted when a security violation is detected.
    """
    event_name: str = "security_violation"  # Name of the event
    event_version: str = "1.0.0"  # Version of the event schema
    event_id: str  # Unique identifier for this event instance
    timestamp: datetime  # When the event was generated
    source_component: str  # Component that generated the event
    severity: str = "warning"  # Severity of the event ("info", "warning", "error", "critical")

    class Payload:
        protocol_type: str  # Protocol type where violation was detected
        violation_type: str  # Type of security violation
        severity: str  # Severity of the violation ("low", "medium", "high", "critical")
        description: str  # Description of the violation
        principal_id: Optional[str] = None  # ID of the principal involved
        resource_id: Optional[str] = None  # ID of the resource involved
        action: Optional[str] = None  # Action that caused the violation
        policy_id: Optional[str] = None  # ID of the policy that was violated
        request_id: Optional[str] = None  # ID of the request
        ip_address: Optional[str] = None  # IP address associated with the violation
        detection_time: datetime  # When the violation was detected
        violation_id: str  # Unique ID for the violation
        action_taken: Optional[str] = None  # Action taken in response to the violation
        evidence: Dict[str, Any] = {}  # Evidence of the violation
        metadata: Dict[str, Any] = {}  # Additional metadata about the violation
```

**Example Usage:**
```python
# Subscribe to security violation events
@event_system.subscribe(SecurityViolationEvent.event_name)
def handle_security_violation(event: SecurityViolationEvent):
    payload = event.payload
    protocol_type = payload.protocol_type
    violation_type = payload.violation_type
    severity = payload.severity

    logger.warning(f"Security violation detected in {protocol_type} protocol: {violation_type} (Severity: {severity})")

    # Record the violation in the security monitoring system
    security_monitoring.record_violation(
        violation_id=payload.violation_id,
        timestamp=event.timestamp,
        protocol_type=protocol_type,
        violation_type=violation_type,
        severity=severity,
        description=payload.description,
        principal_id=payload.principal_id,
        resource_id=payload.resource_id,
        action=payload.action,
        policy_id=payload.policy_id,
        ip_address=payload.ip_address,
        evidence=payload.evidence
    )

    # Take appropriate action based on severity
    if severity == "critical" or severity == "high":
        # Alert security team for high-severity violations
        security_alerts.send_alert(
            alert_type="security_violation",
            severity=severity,
            details={
                "violation_id": payload.violation_id,
                "protocol": protocol_type,
                "violation_type": violation_type,
                "description": payload.description,
                "principal_id": payload.principal_id,
                "ip_address": payload.ip_address,
                "timestamp": event.timestamp.isoformat()
            }
        )

        # For critical violations, take immediate protective action
        if severity == "critical":
            if payload.principal_id:
                # Temporarily lock the principal
                security_system.lock_principal(
                    principal_id=payload.principal_id,
                    reason=f"Critical security violation: {violation_type}",
                    lock_duration_minutes=30
                )
                logger.info(f"Locked principal {payload.principal_id} due to critical security violation")

            if payload.ip_address:
                # Temporarily block the IP address
                security_system.block_ip(
                    ip_address=payload.ip_address,
                    duration_minutes=60,
                    reason=f"Critical security violation: {violation_type}"
                )
                logger.info(f"Blocked IP address {payload.ip_address} due to critical security violation")

    # Record metrics about security violations
    metrics_system.increment(
        metric_name="security_violations",
        value=1,
        dimensions={
            "protocol": protocol_type,
            "violation_type": violation_type,
            "severity": severity
        }
    )

    # Create an incident ticket for tracking and resolution
    if severity in ["medium", "high", "critical"]:
        incident_id = incident_management.create_incident(
            incident_type="security_violation",
            severity=severity,
            title=f"{severity.capitalize()} security violation in {protocol_type} protocol",
            description=payload.description,
            details={
                "violation_id": payload.violation_id,
                "protocol": protocol_type,
                "violation_type": violation_type,
                "principal_id": payload.principal_id,
                "resource_id": payload.resource_id,
                "action": payload.action,
                "ip_address": payload.ip_address,
                "timestamp": event.timestamp.isoformat(),
                "evidence": payload.evidence
            }
        )
        logger.info(f"Created incident ticket {incident_id} for security violation")
```

## Data Flows

### Protocol Request Authentication Flow
1. **External → Protocol Layer**: External component sends request to Protocol Layer
2. **Protocol Layer → Security System**: Protocol Layer forwards request for authentication
3. **Security System Processing**: Security System authenticates request
4. **Security System → Protocol Layer**: Security System returns authentication result
5. **Protocol Layer Processing**: Protocol Layer proceeds based on authentication result

### Protocol Message Encryption Flow
1. **Protocol Layer → Security System**: Protocol Layer requests message encryption
2. **Security System Processing**: Security System encrypts message
3. **Security System → Protocol Layer**: Security System returns encrypted message
4. **Protocol Layer → External**: Protocol Layer sends encrypted message

## Configuration Dependencies

The following configuration parameters affect this interaction:

```yaml
protocol_layer:
  security:
    authentication_required:
      a2a: true
      mcp: true
      http: true
      mqtt: false
      grpc: true

    credential_extraction:
      a2a:
        header_name: "Authorization"
        token_prefix: "Bearer "
      mcp:
        header_name: "X-MCP-API-Key"
      http:
        header_name: "Authorization"
        token_prefix: "Bearer "

    rate_limiting_enabled:
      a2a: true
      mcp: true
      http: true
      mqtt: false
      grpc: true

security:
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
      agent_card_validation:
        enabled: true
        validation_level: "strict"

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
      server_validation:
        enabled: true
        validation_level: "strict"
```

## Error Handling

1. **Authentication Failures**:
   - Appropriate HTTP error responses (401 Unauthorized)
   - Rate limiting for failed authentication attempts
   - Detailed logging with client information
   - Optional challenge-response mechanism for certain protocols

2. **Authorization Failures**:
   - Appropriate HTTP error responses (403 Forbidden)
   - Clear error messages indicating permission issues (without leaking sensitive information)
   - Audit logging of denied actions
   - Graceful handling of partially authorized requests when applicable

3. **Encryption Failures**:
   - Fallback mechanisms for encryption failures
   - Session termination on critical encryption failures
   - Secure logging of encryption issues (without exposing sensitive data)

## Extension Points

1. **Protocol Authentication Handlers**:
   - Custom authentication mechanisms for specific protocols
   - ProtocolAuthHandler interface:
     ```python
     class ProtocolAuthHandler:
         def extract_credentials(self, request: Dict[str, Any]) → Dict[str, Any]:
             # Extract credentials from protocol-specific request
             pass

         def create_auth_challenge(self, auth_method: str) → Dict[str, Any]:
             # Create authentication challenge for specified method
             pass

         def format_auth_error(self, error: AuthError) → Dict[str, Any]:
             # Format authentication error for protocol response
             pass
     ```

2. **Protocol Security Validators**:
   - Custom security validation for protocol-specific requirements
   - Example A2A agent card validator:
     ```yaml
     security:
       protocol_security:
         a2a:
           validators:
             - name: "agent_card_validator"
               implementation_class: "A2AAgentCardValidator"
               config:
                 validation_rules:
                   - "require_api_version"
                   - "validate_tool_schemas"
                   - "validate_description_quality"
     ```

## Notes on Multi-Protocol Design

The Protocol Layer ↔ Security System interface supports OpenMAS's multi-protocol design by:

- Providing protocol-specific security handlers
- Supporting different authentication mechanisms for different protocols
- Enforcing consistent security policies across protocols
- Enabling secure cross-protocol communication

This interface ensures that each protocol can implement its security requirements while maintaining system-wide security standards.

## Notes on A2A and MCP Protocol Support

This interface explicitly addresses both Google's A2A protocol and the Model Context Protocol (MCP) with their specific security requirements:

### A2A Protocol Security

A2A protocol security has these specific characteristics:

1. **OAuth2 Authentication**: A2A typically uses OAuth2 for authentication
2. **Agent Card Validation**: A2A requires validation of agent cards for security
3. **Bearer Token Format**: Authentication uses standard Bearer token format
4. **Tool Permission Model**: A2A implements a permission model for tool access

Example A2A authentication:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### MCP Protocol Security

MCP protocol security has these specific characteristics:

1. **API Key Authentication**: MCP often uses API keys for authentication
2. **Server Capability Validation**: MCP validates server capabilities
3. **Custom Header Format**: Authentication uses custom headers
4. **Capability Permission Model**: MCP implements permissions at the capability level

Example MCP authentication:
```
X-MCP-API-Key: mcp_sk_12345abcdef6789...
```

The Security System provides handlers for both protocols while maintaining consistent security policies.

## Example: Protocol-Specific Authentication Implementation

The implementation of protocol-specific authentication demonstrates how the Security System adapts to different protocols:

```python
class A2AAuthHandler(ProtocolAuthHandler):
    def extract_credentials(self, request: Dict[str, Any]) → Dict[str, Any]:
        """Extract credentials from A2A protocol request"""
        auth_header = request.get("headers", {}).get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            return {
                "type": "bearer_token",
                "token": token
            }
        return {"type": "none"}

    def create_auth_challenge(self, auth_method: str) → Dict[str, Any]:
        """Create A2A authentication challenge"""
        if auth_method == "oauth2":
            return {
                "error": "unauthorized",
                "auth_required": True,
                "auth_methods": ["bearer"],
                "error_description": "Authentication required"
            }
        return {}

    def format_auth_error(self, error: AuthError) → Dict[str, Any]:
        """Format A2A authentication error"""
        return {
            "error": error.error_code,
            "error_description": error.error_message
        }


class MCPAuthHandler(ProtocolAuthHandler):
    def extract_credentials(self, request: Dict[str, Any]) → Dict[str, Any]:
        """Extract credentials from MCP protocol request"""
        api_key = request.get("headers", {}).get("X-MCP-API-Key", "")
        if api_key:
            return {
                "type": "api_key",
                "api_key": api_key
            }
        return {"type": "none"}

    def create_auth_challenge(self, auth_method: str) → Dict[str, Any]:
        """Create MCP authentication challenge"""
        if auth_method == "api_key":
            return {
                "error": "unauthorized",
                "required_header": "X-MCP-API-Key",
                "error_description": "API key required"
            }
        return {}

    def format_auth_error(self, error: AuthError) → Dict[str, Any]:
        """Format MCP authentication error"""
        return {
            "error": error.error_code,
            "message": error.error_message
        }
```

These protocol-specific handlers enable the Security System to work with multiple protocols while maintaining consistent security standards.

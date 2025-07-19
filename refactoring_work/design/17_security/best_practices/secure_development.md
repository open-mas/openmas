# Secure Development Practices

## Overview

This document provides guidance on secure development practices for OpenMAS agents and applications. Following these practices helps ensure that OpenMAS-based systems are secure by design, while maintaining the framework's reasoning-agnostic architecture and multi-protocol support.

## Secure Design Principles

### 1. Security by Design

Incorporate security throughout the development lifecycle:

- Start with a threat model to identify potential vulnerabilities
- Design security controls to address identified threats
- Validate security assumptions through review and testing
- Include security in architectural decisions
- Follow the principle of least privilege
- Create defense-in-depth strategies

### 2. Maintain Reasoning-Agnostic Security

Ensure security mechanisms work across reasoning approaches:

- Create clear security boundaries between communication ("body") and reasoning ("brain")
- Design security interfaces that work with all reasoning approaches
- Avoid security mechanisms that depend on specific reasoning implementations
- Test security controls with different reasoning approaches
- Ensure security mechanisms don't leak reasoning details

### 3. Protocol-Independent Security

Design security mechanisms that work across protocols:

- Create a common security model that applies to all protocols
- Implement protocol-specific security adapters
- Avoid tight coupling between security logic and protocol implementation
- Ensure security mechanisms can evolve independently of protocols
- Test security across all supported protocols

## Secure Coding Practices

### 1. Input Validation

Validate all inputs from untrusted sources:

```python
# Bad practice - no validation
def handle_message(message):
    content = message.get("content")
    process_content(content)

# Good practice - with validation
def handle_message(message):
    if not isinstance(message, dict):
        raise ValueError("Message must be a dictionary")
    
    content = message.get("content")
    if content is None:
        raise ValueError("Message must contain 'content'")
    
    # Validate content structure
    validate_content_schema(content)
    
    # Process validated content
    process_content(content)
```

Key practices:
- Validate all inputs against expected types and schemas
- Verify message format and contents
- Enforce constraints on inputs (e.g., length, range, format)
- Use schema validation for complex structures
- Apply contextual validation based on message type

### 2. Secure Authentication Implementation

Implement authentication securely:

```python
# Bad practice - insecure token comparison
def verify_token(provided_token, expected_token):
    return provided_token == expected_token

# Good practice - secure token comparison
def verify_token(provided_token, expected_token):
    # Use constant-time comparison to prevent timing attacks
    return secrets.compare_digest(provided_token, expected_token)
```

Key practices:
- Use constant-time comparison for credentials
- Never store credentials in plain text
- Implement proper token validation
- Use secure random number generation for tokens
- Apply appropriate key derivation functions for passwords

### 3. Secure Authorization Implementation

Implement authorization securely:

```python
# Bad practice - insufficient authorization
async def handle_function_call(agent, function_name, parameters):
    # No authorization check
    return await agent.execute_function(function_name, parameters)

# Good practice - with authorization
async def handle_function_call(agent, function_name, parameters):
    # Check if agent is authorized to call this function
    if not await agent.is_authorized_for_function(function_name):
        raise PermissionError(f"Agent not authorized to call {function_name}")
    
    # Check if parameters are valid for this function
    if not await validate_function_parameters(function_name, parameters):
        raise ValueError(f"Invalid parameters for {function_name}")
    
    # Execute function with validated parameters
    return await agent.execute_function(function_name, parameters)
```

Key practices:
- Implement authorization checks at all entry points
- Use principle of least privilege
- Implement defense in depth with multiple authorization layers
- Validate authorization context for each operation
- Enforce authorization across all protocols

### 4. Secure Cryptography Usage

Use cryptography correctly:

```python
# Bad practice - insecure encryption
def encrypt_message(message, key):
    # Using ECB mode (insecure)
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    encryptor = cipher.encryptor()
    return encryptor.update(message) + encryptor.finalize()

# Good practice - secure encryption
def encrypt_message(message, key):
    # Generate a random IV
    iv = os.urandom(16)
    
    # Use GCM mode for authenticated encryption
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    
    # Add authenticated data if needed
    # encryptor.authenticate_additional_data(associated_data)
    
    # Encrypt the message
    ciphertext = encryptor.update(message) + encryptor.finalize()
    
    # Return IV, ciphertext, and tag for verification
    return {
        "iv": base64.b64encode(iv).decode("utf-8"),
        "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
        "tag": base64.b64encode(encryptor.tag).decode("utf-8")
    }
```

Key practices:
- Use modern, authenticated encryption algorithms
- Generate cryptographically secure random numbers
- Use appropriate key lengths and algorithms
- Don't implement custom cryptography
- Use established libraries with good security track records
- Keep cryptographic dependencies up to date

### 5. Error Handling and Logging

Implement secure error handling and logging:

```python
# Bad practice - insecure error handling
def process_request(request):
    try:
        result = process_data(request.data)
        return {"success": True, "result": result}
    except Exception as e:
        # Exposes potentially sensitive error details
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}

# Good practice - secure error handling
def process_request(request):
    try:
        result = process_data(request.data)
        return {"success": True, "result": result}
    except ValueError as e:
        # Log detailed error for debugging
        logger.error(f"ValueError in process_request: {e}", exc_info=True)
        # Return generic error to user
        return {"success": False, "error": "Invalid input data"}
    except Exception as e:
        # Log unexpected errors with full details
        logger.error(f"Unexpected error in process_request: {e}", exc_info=True)
        # Return generic error to user
        return {"success": False, "error": "An unexpected error occurred"}
```

Key practices:
- Don't expose sensitive information in error messages
- Log sufficient information for debugging but sanitize sensitive data
- Use structured logging for machine-readable logs
- Implement appropriate log levels
- Handle all error cases gracefully
- Fail securely when errors occur

### 6. Secure Dependencies Management

Manage dependencies securely:

```python
# requirements.txt example with pinned versions
cryptography==41.0.3
pyjwt==2.8.0
pydantic==2.4.2
```

Key practices:
- Pin dependency versions for reproducibility
- Regularly update dependencies for security patches
- Use dependency security scanning tools
- Minimize dependencies to reduce attack surface
- Verify dependency integrity with checksums
- Review dependency security policies

## Protocol-Specific Security Practices

### 1. MCP Security Practices

Implement secure Model Context Protocol agents:

```python
# Good practice - secure MCP function handling
def register_mcp_functions(agent):
    @agent.function(authorized_roles=["admin"])
    async def sensitive_function(param1: str) -> dict:
        # Function implementation with proper validation
        if not validate_parameter(param1):
            raise ValueError("Invalid parameter")
        return {"result": "success"}
```

Key practices:
- Validate all function parameters
- Implement function-level authorization
- Protect sensitive function parameters
- Validate function returns
- Implement context-aware function security

### 2. A2A Security Practices

Implement secure Agent-to-Agent Protocol agents:

```python
# Good practice - secure agent capability verification
async def handle_a2a_message(message, sender_card):
    # Verify the agent card signature
    if not verify_agent_card_signature(sender_card):
        raise SecurityError("Invalid agent card signature")
    
    # Check required capabilities
    required_capability = "conversation"
    if required_capability not in sender_card.get("capabilities", []):
        raise PermissionError(f"Agent lacks required capability: {required_capability}")
    
    # Process the message with validated capabilities
    return await process_a2a_message(message, sender_card)
```

Key practices:
- Verify agent card signatures
- Validate required capabilities
- Implement message signing and verification
- Verify agent identity
- Implement secure capability negotiation

### 3. HTTP Security Practices

Implement secure HTTP-based agents:

```python
# Good practice - HTTP security headers
def add_security_headers(response):
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

Key practices:
- Implement proper HTTP authentication
- Use security headers
- Validate request parameters
- Implement CSRF protection
- Enforce HTTPS
- Implement proper CORS policies

### 4. MQTT Security Practices

Implement secure MQTT-based agents:

```python
# Good practice - secure MQTT client
def create_secure_mqtt_client(client_id, broker_host, broker_port):
    client = mqtt.Client(client_id=client_id)
    
    # Configure TLS
    client.tls_set(
        ca_certs="/path/to/ca.crt",
        certfile="/path/to/client.crt",
        keyfile="/path/to/client.key",
        tls_version=ssl.PROTOCOL_TLS_CLIENT
    )
    
    # Set username and password
    client.username_pw_set("username", "password")
    
    # Add secure callback handlers
    client.on_message = secure_on_message
    
    return client
```

Key practices:
- Use TLS for transport security
- Implement client certificate authentication
- Use secure topic patterns
- Validate message payloads
- Implement topic-based authorization
- Secure client identification

### 5. gRPC Security Practices

Implement secure gRPC-based agents:

```python
# Good practice - secure gRPC server
def create_secure_grpc_server(server_cert, server_key, ca_cert):
    # Load credentials
    server_credentials = grpc.ssl_server_credentials(
        [(server_key, server_cert)],
        root_certificates=ca_cert,
        require_client_auth=True
    )
    
    # Create server with credentials
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server.add_secure_port("[::]:50051", server_credentials)
    
    # Add secure service handlers
    add_secure_services(server)
    
    return server
```

Key practices:
- Implement mutual TLS (mTLS)
- Use secure channel credentials
- Implement interceptors for security checks
- Validate messages against schemas
- Implement proper error handling
- Secure metadata handling

## Testing for Security

### 1. Security Unit Testing

Write security-specific unit tests:

```python
# Good practice - security unit test
def test_token_verification():
    # Test with valid token
    valid_token = generate_test_token("user1", ["read"])
    assert verify_token(valid_token) is True
    
    # Test with expired token
    expired_token = generate_expired_test_token("user1", ["read"])
    assert verify_token(expired_token) is False
    
    # Test with tampered token
    tampered_token = tamper_with_token(valid_token)
    assert verify_token(tampered_token) is False
    
    # Test with token using wrong key
    wrong_key_token = generate_token_with_wrong_key("user1", ["read"])
    assert verify_token(wrong_key_token) is False
```

Key practices:
- Test both positive and negative security cases
- Test boundary conditions
- Test security failure modes
- Test with malformed inputs
- Implement security regression tests
- Test across protocol boundaries

### 2. Security Integration Testing

Write security-focused integration tests:

```python
# Good practice - security integration test
async def test_cross_protocol_security():
    # Create agents using different protocols
    agent1 = await create_test_agent("agent1", protocol="a2a")
    agent2 = await create_test_agent("agent2", protocol="mcp")
    
    # Test secure communication between protocols
    message = {"content": "secure test", "sensitive": True}
    
    # Send message from agent1 to agent2
    response = await agent1.send_to(agent2.id, message)
    
    # Verify security properties
    assert response["success"] is True
    assert verify_message_integrity(response["message"]) is True
    
    # Test with insufficient permissions
    limited_agent = await create_test_agent("limited", protocol="a2a", roles=["limited"])
    response = await limited_agent.send_to(agent2.id, message)
    assert response["success"] is False
    assert "permission denied" in response["error"].lower()
```

Key practices:
- Test interactions between different protocols
- Test security across trust boundaries
- Test with different authentication mechanisms
- Test authorization across components
- Test secure communication patterns
- Test failure recovery from security errors

### 3. Security Fuzzing

Implement security fuzzing tests:

```python
# Good practice - security fuzzing
@hypothesis.given(hypothesis.strategies.text())
def test_message_handler_fuzzing(random_input):
    # Wrap in try/except to catch any unhandled exceptions
    try:
        result = message_handler.process_message(random_input)
        # If no exception, verify it either rejected the input or processed it safely
        assert result["success"] is False or validate_result(result)
    except Exception as e:
        # Make sure it's an expected exception type for invalid input
        assert isinstance(e, (ValueError, TypeError, ValidationError))
```

Key practices:
- Use automated fuzzing tools
- Test with malformed inputs
- Test with unexpected data types
- Test with boundary values
- Test with large inputs
- Test with malicious payloads

## Secure Configuration Practices

### 1. Default-Secure Configuration

Provide secure default configurations:

```yaml
# Good practice - secure defaults
security:
  authentication:
    enabled: true
    token_expiration: 3600  # 1 hour
  authorization:
    default_policy: "deny"  # Deny by default
  encryption:
    data_at_rest: true
    data_in_transit: true
  transport_security:
    tls:
      enabled: true
      version: "1.3"
```

Key practices:
- Enable security by default
- Use restrictive default permissions
- Provide secure configuration templates
- Document security implications of configuration changes
- Validate security-critical configuration

### 2. Environment-Based Configuration

Use environment-based configuration for secrets:

```python
# Good practice - environment-based secrets
def load_security_config():
    config = {
        "auth": {
            "key_id": os.environ.get("AUTH_KEY_ID"),
            "key_secret": os.environ.get("AUTH_KEY_SECRET"),
            "issuer": os.environ.get("AUTH_ISSUER", "https://auth.example.com")
        },
        "encryption": {
            "key_path": os.environ.get("ENCRYPTION_KEY_PATH"),
            "algorithm": os.environ.get("ENCRYPTION_ALGORITHM", "AES-256-GCM")
        }
    }
    
    # Validate required configuration
    if not config["auth"]["key_id"] or not config["auth"]["key_secret"]:
        raise ConfigError("Missing required authentication configuration")
    
    return config
```

Key practices:
- Use environment variables for secrets
- Don't hardcode sensitive values
- Provide clear variable naming
- Validate required security configuration
- Use secure environment variable handling
- Document required environment variables

### 3. Secure Configuration Validation

Validate security configuration before use:

```python
# Good practice - configuration validation
def validate_security_config(config):
    # Check TLS configuration
    if config.get("tls", {}).get("enabled", False):
        tls_config = config["tls"]
        
        # Validate TLS version
        valid_versions = ["1.2", "1.3"]
        if tls_config.get("version") not in valid_versions:
            raise ConfigError(f"TLS version must be one of: {valid_versions}")
        
        # Validate certificate paths
        cert_file = tls_config.get("cert_file")
        key_file = tls_config.get("key_file")
        
        if not cert_file or not os.path.exists(cert_file):
            raise ConfigError(f"TLS certificate file not found: {cert_file}")
        
        if not key_file or not os.path.exists(key_file):
            raise ConfigError(f"TLS key file not found: {key_file}")
    
    # Additional validation for other security settings
    # ...
    
    return True
```

Key practices:
- Validate configuration before use
- Check for required security settings
- Verify file paths exist and are accessible
- Validate security parameter values
- Provide clear error messages for invalid configuration
- Document configuration requirements

## Secure CI/CD Practices

### 1. Automated Security Testing

Integrate security testing into CI/CD:

```yaml
# Good practice - CI/CD security testing
name: Security CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install bandit safety
      
      - name: Run Bandit (SAST)
        run: bandit -r ./src -f json -o bandit-results.json
      
      - name: Check dependencies for vulnerabilities
        run: safety check -r requirements.txt
      
      - name: Run security unit tests
        run: pytest -xvs tests/security
```

Key practices:
- Integrate SAST (Static Application Security Testing)
- Scan dependencies for vulnerabilities
- Run security-specific tests
- Fail builds on security issues
- Maintain security gate thresholds
- Automate security regression testing

### 2. Secure Build and Release

Implement secure build and release processes:

```yaml
# Good practice - secure build process
name: Secure Build

on:
  release:
    types: [created]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install build twine
      
      - name: Build package
        run: python -m build
      
      - name: Generate checksums
        run: |
          sha256sum dist/*.tar.gz dist/*.whl > dist/checksums.txt
      
      - name: Sign package
        run: |
          echo "${{ secrets.GPG_PRIVATE_KEY }}" | gpg --import
          gpg --detach-sign -a dist/*.tar.gz
          gpg --detach-sign -a dist/*.whl
      
      - name: Upload to PyPI
        run: twine upload dist/*
        env:
          TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
          TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
```

Key practices:
- Sign build artifacts
- Generate and publish checksums
- Use secure credential handling
- Implement release approvals
- Version security controls
- Document security changes in releases

## Related Documentation

- [Security Principles](../architecture/security_principles.md)
- [Authentication](../authentication/README.md)
- [Authorization](../authorization/README.md)
- [Data Protection](../data_protection/README.md)
- [Communication Security](../communication/README.md)
- [Testing Framework](../../16_testing/README.md)

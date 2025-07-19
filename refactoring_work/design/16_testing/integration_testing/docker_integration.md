# Docker Integration Testing

## Overview

This document describes approaches and best practices for testing OpenMAS components and systems in Docker containers. Docker integration testing ensures that OpenMAS deployments work correctly in containerized environments, which is crucial for production deployments in container-based infrastructure.

## Key Docker Testing Scenarios

OpenMAS Docker integration testing focuses on these key scenarios:

1. **Container Deployment**: Testing deployment of OpenMAS components in containers
2. **Multi-Container Systems**: Testing multi-agent systems across multiple containers
3. **Configuration Injection**: Testing configuration through environment variables and volumes
4. **Resource Management**: Testing resource constraints and limits
5. **Container Networking**: Testing communication between containerized components
6. **Container Orchestration**: Testing with Docker Compose and other orchestration tools

## Testing Approach

### Docker Test Fixtures

```python
import pytest
import docker
import asyncio
import os
from openmas.testing import DockerTestHarness

@pytest.fixture
async def docker_harness():
    """Create a Docker test harness."""
    harness = DockerTestHarness()
    await harness.initialize()
    
    yield harness
    
    await harness.shutdown()

@pytest.fixture
async def agent_container(docker_harness):
    """Create a containerized OpenMAS agent."""
    # Agent configuration
    config = {
        "id": "test_agent",
        "name": "Test Agent",
        "type": "assistant",
        "capabilities": [
            {"id": "messaging", "type": "messaging"}
        ],
        "protocol": {
            "type": "mcp",
            "transport": "http",
            "settings": {
                "host": "0.0.0.0",
                "port": 8080
            }
        }
    }
    
    # Create agent container
    container = await docker_harness.create_agent_container(
        image="openmas/agent:0.3.0",
        config=config,
        ports={"8080/tcp": None}  # Assign a random host port
    )
    
    yield container
    
    # Cleanup
    await docker_harness.remove_container(container)

@pytest.fixture
async def multi_agent_system(docker_harness):
    """Create a multi-container agent system."""
    # System configuration
    system_config = {
        "version": "0.3.0",
        "system": {
            "name": "test_system",
            "description": "Test multi-agent system"
        },
        "agents": [
            {
                "id": "agent1",
                "name": "Agent 1",
                "type": "assistant",
                "capabilities": [{"id": "messaging", "type": "messaging"}]
            },
            {
                "id": "agent2",
                "name": "Agent 2",
                "type": "user",
                "capabilities": [{"id": "messaging", "type": "messaging"}]
            }
        ],
        "protocols": [
            {
                "type": "mcp",
                "transport": "http"
            }
        ]
    }
    
    # Create containers for the system
    system = await docker_harness.create_multi_container_system(system_config)
    
    yield system
    
    # Cleanup
    await docker_harness.remove_system(system)
```

### Testing Container Deployment

```python
async def test_agent_container_deployment(agent_container, docker_harness):
    """Test deployment of an OpenMAS agent in a container."""
    # Get container status
    status = await docker_harness.get_container_status(agent_container)
    
    # Assert container is running
    assert status["State"]["Running"] is True
    
    # Get exposed port
    host_port = docker_harness.get_host_port(agent_container, 8080)
    
    # Test agent health endpoint
    response = await docker_harness.http_get(f"http://localhost:{host_port}/health")
    
    # Assert agent is healthy
    assert response.status == 200
    
    health_data = await response.json()
    assert health_data["status"] == "healthy"
    assert health_data["agent_id"] == "test_agent"
```

### Testing Multi-Container Systems

```python
async def test_multi_container_system(multi_agent_system, docker_harness):
    """Test a multi-container OpenMAS system."""
    # Get status of all containers
    statuses = await docker_harness.get_system_container_statuses(multi_agent_system)
    
    # Assert all containers are running
    for container_id, status in statuses.items():
        assert status["State"]["Running"] is True
    
    # Get agent endpoints
    agent1_endpoint = docker_harness.get_agent_endpoint(multi_agent_system, "agent1")
    agent2_endpoint = docker_harness.get_agent_endpoint(multi_agent_system, "agent2")
    
    # Test communication between agents
    message = {
        "content": "Hello from Docker test",
        "type": "text"
    }
    
    # Send message from agent1 to agent2
    send_response = await docker_harness.http_post(
        f"{agent1_endpoint}/messages",
        json={
            "receiver": "agent2",
            "message": message
        }
    )
    
    assert send_response.status == 200
    
    # Verify agent2 received the message
    await docker_harness.wait_for_condition(
        lambda: docker_harness.check_message_received(agent2_endpoint, "agent1", message),
        timeout=5.0
    )
    
    # Get messages received by agent2
    messages_response = await docker_harness.http_get(f"{agent2_endpoint}/messages")
    assert messages_response.status == 200
    
    messages = await messages_response.json()
    assert len(messages) >= 1
    
    # Find the message from agent1
    agent1_messages = [m for m in messages if m["sender"] == "agent1"]
    assert len(agent1_messages) >= 1
    assert agent1_messages[0]["content"] == message["content"]
```

### Testing Configuration Injection

```python
async def test_configuration_injection(docker_harness):
    """Test configuration injection via environment variables and volumes."""
    # Create configuration file
    config = {
        "id": "configured_agent",
        "name": "Configured Agent",
        "type": "assistant",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {
            "type": "mcp",
            "transport": "http",
            "settings": {
                "host": "0.0.0.0",
                "port": 8080
            }
        }
    }
    
    config_path = await docker_harness.create_config_file(config)
    
    # Environment variables
    environment = {
        "OPENMAS_LOG_LEVEL": "DEBUG",
        "OPENMAS_CONFIG_PATH": "/app/config/agent.yaml"
    }
    
    # Volumes
    volumes = {
        config_path: {
            "bind": "/app/config/agent.yaml",
            "mode": "ro"
        }
    }
    
    # Create container with config
    container = await docker_harness.create_container(
        image="openmas/agent:0.3.0",
        environment=environment,
        volumes=volumes,
        ports={"8080/tcp": None}
    )
    
    try:
        # Wait for container to start
        await docker_harness.wait_for_container_status(container, "running")
        
        # Get exposed port
        host_port = docker_harness.get_host_port(container, 8080)
        
        # Test agent info endpoint
        response = await docker_harness.http_get(f"http://localhost:{host_port}/info")
        
        # Assert configuration was properly injected
        assert response.status == 200
        
        info = await response.json()
        assert info["agent_id"] == "configured_agent"
        assert info["agent_name"] == "Configured Agent"
        
        # Verify environment variables were applied
        logs = await docker_harness.get_container_logs(container)
        assert "Log level set to DEBUG" in logs
    
    finally:
        # Cleanup
        await docker_harness.remove_container(container)
```

### Testing Resource Management

```python
async def test_resource_constraints(docker_harness):
    """Test container resource constraints."""
    # Agent configuration
    config = {
        "id": "resource_test_agent",
        "name": "Resource Test Agent",
        "type": "assistant",
        "capabilities": [{"id": "messaging", "type": "messaging"}]
    }
    
    # Resource constraints
    resources = {
        "cpu_limit": "0.5",  # 50% of a CPU core
        "memory_limit": "512m",  # 512MB memory
        "memory_reservation": "256m"  # 256MB memory reservation
    }
    
    # Create container with resource constraints
    container = await docker_harness.create_agent_container(
        image="openmas/agent:0.3.0",
        config=config,
        resources=resources,
        ports={"8080/tcp": None}
    )
    
    try:
        # Wait for container to start
        await docker_harness.wait_for_container_status(container, "running")
        
        # Get container stats
        stats = await docker_harness.get_container_stats(container)
        
        # Verify CPU limit is applied
        assert stats["cpu_percent"] <= 50.0, "CPU usage exceeds limit"
        
        # Verify memory limit is applied
        assert stats["memory_usage_mb"] <= 512.0, "Memory usage exceeds limit"
    
    finally:
        # Cleanup
        await docker_harness.remove_container(container)
```

### Testing Container Networking

```python
async def test_container_networking(docker_harness):
    """Test networking between containers in a custom network."""
    # Create a custom bridge network
    network = await docker_harness.create_network("openmas_test_network")
    
    try:
        # Create first agent container
        agent1_config = {
            "id": "network_agent1",
            "name": "Network Agent 1",
            "type": "assistant",
            "capabilities": [{"id": "messaging", "type": "messaging"}],
            "protocol": {
                "type": "mcp",
                "transport": "http",
                "settings": {
                    "host": "0.0.0.0",
                    "port": 8080
                }
            }
        }
        
        agent1_container = await docker_harness.create_agent_container(
            image="openmas/agent:0.3.0",
            config=agent1_config,
            network=network.name,
            network_aliases=["agent1"],
            ports={"8080/tcp": None}
        )
        
        # Create second agent container
        agent2_config = {
            "id": "network_agent2",
            "name": "Network Agent 2",
            "type": "user",
            "capabilities": [{"id": "messaging", "type": "messaging"}],
            "protocol": {
                "type": "mcp",
                "transport": "http",
                "settings": {
                    "host": "0.0.0.0",
                    "port": 8080
                }
            }
        }
        
        agent2_container = await docker_harness.create_agent_container(
            image="openmas/agent:0.3.0",
            config=agent2_config,
            network=network.name,
            network_aliases=["agent2"],
            ports={"8080/tcp": None}
        )
        
        try:
            # Wait for both containers to start
            await docker_harness.wait_for_container_status(agent1_container, "running")
            await docker_harness.wait_for_container_status(agent2_container, "running")
            
            # Get external ports for API access
            agent1_ext_port = docker_harness.get_host_port(agent1_container, 8080)
            
            # Test DNS resolution within the network by sending a message to agent2
            # using its network alias
            message = {
                "receiver": "network_agent2",
                "message": {
                    "content": "Hello via Docker network",
                    "type": "text"
                }
            }
            
            # Configure agent1 to use internal DNS name for agent2
            config_cmd = [
                "curl", "-X", "POST", "http://localhost:8080/config", 
                "-H", "Content-Type: application/json",
                "-d", '{"endpoint_mapping": {"network_agent2": "http://agent2:8080"}}'
            ]
            
            await docker_harness.exec_command(agent1_container, config_cmd)
            
            # Send message from agent1 to agent2
            send_cmd = [
                "curl", "-X", "POST", "http://localhost:8080/messages",
                "-H", "Content-Type: application/json",
                "-d", '{"receiver":"network_agent2","message":{"content":"Hello via Docker network","type":"text"}}'
            ]
            
            exec_result = await docker_harness.exec_command(agent1_container, send_cmd)
            assert "success" in exec_result.lower()
            
            # Verify agent2 received the message (via external port)
            agent2_ext_port = docker_harness.get_host_port(agent2_container, 8080)
            
            # Wait for message to be received
            await docker_harness.wait_for_condition(
                lambda: docker_harness.check_message_received(
                    f"http://localhost:{agent2_ext_port}",
                    "network_agent1",
                    {"content": "Hello via Docker network"}
                ),
                timeout=5.0
            )
            
            # Get messages from agent2
            response = await docker_harness.http_get(f"http://localhost:{agent2_ext_port}/messages")
            messages = await response.json()
            
            # Find message from agent1
            agent1_messages = [m for m in messages if m["sender"] == "network_agent1"]
            assert len(agent1_messages) >= 1
            assert agent1_messages[0]["content"] == "Hello via Docker network"
        
        finally:
            # Cleanup containers
            await docker_harness.remove_container(agent1_container)
            await docker_harness.remove_container(agent2_container)
    
    finally:
        # Cleanup network
        await docker_harness.remove_network(network)
```

### Testing with Docker Compose

```python
async def test_docker_compose_deployment(docker_harness):
    """Test OpenMAS deployment using Docker Compose."""
    # Create Docker Compose file
    compose_content = """
    version: '3.8'
    
    services:
      agent1:
        image: openmas/agent:0.3.0
        environment:
          - OPENMAS_CONFIG=/app/config/agent1.yaml
          - OPENMAS_LOG_LEVEL=INFO
        volumes:
          - ./configs:/app/config
        ports:
          - "8081:8080"
        networks:
          - openmas_network
        healthcheck:
          test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
          interval: 10s
          timeout: 5s
          retries: 3
          start_period: 5s
      
      agent2:
        image: openmas/agent:0.3.0
        environment:
          - OPENMAS_CONFIG=/app/config/agent2.yaml
          - OPENMAS_LOG_LEVEL=INFO
        volumes:
          - ./configs:/app/config
        ports:
          - "8082:8080"
        networks:
          - openmas_network
        depends_on:
          - agent1
        healthcheck:
          test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
          interval: 10s
          timeout: 5s
          retries: 3
          start_period: 5s
    
    networks:
      openmas_network:
        driver: bridge
    """
    
    # Create agent configurations
    agent1_config = {
        "id": "compose_agent1",
        "name": "Compose Agent 1",
        "type": "assistant",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {
            "type": "mcp",
            "transport": "http",
            "settings": {
                "host": "0.0.0.0",
                "port": 8080
            }
        },
        "endpoint_mapping": {
            "compose_agent2": "http://agent2:8080"
        }
    }
    
    agent2_config = {
        "id": "compose_agent2",
        "name": "Compose Agent 2",
        "type": "user",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {
            "type": "mcp",
            "transport": "http",
            "settings": {
                "host": "0.0.0.0",
                "port": 8080
            }
        },
        "endpoint_mapping": {
            "compose_agent1": "http://agent1:8080"
        }
    }
    
    # Create test directory with configs and compose file
    test_dir = await docker_harness.create_test_directory()
    config_dir = os.path.join(test_dir, "configs")
    os.makedirs(config_dir, exist_ok=True)
    
    # Write configs
    with open(os.path.join(config_dir, "agent1.yaml"), "w") as f:
        docker_harness.write_yaml(agent1_config, f)
    
    with open(os.path.join(config_dir, "agent2.yaml"), "w") as f:
        docker_harness.write_yaml(agent2_config, f)
    
    # Write compose file
    with open(os.path.join(test_dir, "docker-compose.yml"), "w") as f:
        f.write(compose_content)
    
    try:
        # Start docker-compose
        await docker_harness.docker_compose_up(test_dir)
        
        # Wait for services to be healthy
        await docker_harness.wait_for_docker_compose_healthy(test_dir, timeout=30.0)
        
        # Test communication between agents
        message = {
            "content": "Hello via Docker Compose",
            "type": "text"
        }
        
        # Send message from agent1 to agent2
        send_response = await docker_harness.http_post(
            "http://localhost:8081/messages",
            json={
                "receiver": "compose_agent2",
                "message": message
            }
        )
        
        assert send_response.status == 200
        
        # Verify agent2 received the message
        await docker_harness.wait_for_condition(
            lambda: docker_harness.check_message_received(
                "http://localhost:8082",
                "compose_agent1",
                message
            ),
            timeout=5.0
        )
        
        # Get messages from agent2
        response = await docker_harness.http_get("http://localhost:8082/messages")
        messages = await response.json()
        
        # Find message from agent1
        agent1_messages = [m for m in messages if m["sender"] == "compose_agent1"]
        assert len(agent1_messages) >= 1
        assert agent1_messages[0]["content"] == message["content"]
    
    finally:
        # Stop docker-compose
        await docker_harness.docker_compose_down(test_dir)
```

## Protocol-Specific Docker Testing

Testing different protocols in Docker containers:

```python
@pytest.mark.parametrize("protocol_type,transport_type", [
    ("mcp", "http"),
    ("mcp", "websocket"),
    ("a2a", "http"),
    ("mqtt", "mqtt"),
    ("grpc", "grpc")
])
async def test_protocol_in_docker(docker_harness, protocol_type, transport_type):
    """Test protocol-specific functionality in Docker containers."""
    # Agent configuration with specified protocol
    agent_config = {
        "id": f"{protocol_type}_agent",
        "name": f"{protocol_type.upper()} Agent",
        "type": "assistant",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {
            "type": protocol_type,
            "transport": transport_type,
            "settings": {
                "host": "0.0.0.0",
                "port": 8080
            }
        }
    }
    
    # Create protocol-specific container
    container = await docker_harness.create_agent_container(
        image=f"openmas/{protocol_type}-agent:0.3.0",
        config=agent_config,
        ports={"8080/tcp": None}
    )
    
    try:
        # Wait for container to start
        await docker_harness.wait_for_container_status(container, "running")
        
        # Protocol-specific tests
        host_port = docker_harness.get_host_port(container, 8080)
        endpoint = f"http://localhost:{host_port}"
        
        # Test protocol-specific endpoint
        if protocol_type == "mcp":
            response = await docker_harness.http_get(f"{endpoint}/mcp/info")
            assert response.status == 200
            
            info = await response.json()
            assert info["protocol"] == "mcp"
            assert info["transport"] == transport_type
        
        # Other protocol-specific tests...
    
    finally:
        # Cleanup
        await docker_harness.remove_container(container)
```

## Testing Reasoning Approaches in Docker

Testing different reasoning approaches in Docker containers, respecting OpenMAS's reasoning agnosticism:

```python
@pytest.mark.parametrize("reasoning_type", ["llm", "rule_based", "bdi", "hybrid"])
async def test_reasoning_in_docker(docker_harness, reasoning_type):
    """Test different reasoning approaches in Docker containers."""
    # Agent configuration with specified reasoning type
    agent_config = {
        "id": f"{reasoning_type}_agent",
        "name": f"{reasoning_type.capitalize()} Agent",
        "type": "assistant",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {
            "type": "mcp",
            "transport": "http",
            "settings": {
                "host": "0.0.0.0",
                "port": 8080
            }
        },
        "reasoning": {
            "type": reasoning_type,
            # Reasoning-specific configuration...
        }
    }
    
    # Add reasoning-specific configuration
    if reasoning_type == "llm":
        agent_config["reasoning"]["model"] = "test-model"
        agent_config["reasoning"]["settings"] = {
            "temperature": 0.7,
            "max_tokens": 100,
            "mock_mode": True  # Use mock responses for testing
        }
    elif reasoning_type == "rule_based":
        agent_config["reasoning"]["rules"] = [
            {"pattern": "Hello", "response": "Hi there!"},
            {"pattern": "Help", "response": "How can I assist you?"}
        ]
    elif reasoning_type == "bdi":
        agent_config["reasoning"]["beliefs"] = [
            {"name": "greeting", "value": "Hello"}
        ]
        agent_config["reasoning"]["desires"] = [
            {"name": "be_helpful", "priority": 1}
        ]
        agent_config["reasoning"]["intentions"] = [
            {"desire": "be_helpful", "action": "respond_greeting"}
        ]
    elif reasoning_type == "hybrid":
        agent_config["reasoning"]["components"] = [
            {"type": "llm", "weight": 0.7},
            {"type": "rule_based", "weight": 0.3}
        ]
    
    # Create container for reasoning agent
    container = await docker_harness.create_agent_container(
        image=f"openmas/{reasoning_type}-agent:0.3.0",
        config=agent_config,
        ports={"8080/tcp": None}
    )
    
    try:
        # Wait for container to start
        await docker_harness.wait_for_container_status(container, "running")
        
        # Get endpoint
        host_port = docker_harness.get_host_port(container, 8080)
        endpoint = f"http://localhost:{host_port}"
        
        # Test reasoning capability
        message = {
            "content": "Hello",
            "type": "text"
        }
        
        response = await docker_harness.http_post(
            f"{endpoint}/reasoning",
            json={"input": message}
        )
        
        assert response.status == 200
        
        result = await response.json()
        assert "response" in result
        
        # Reasoning-specific assertions
        if reasoning_type == "llm":
            assert "model" in result
            assert result["model"] == "test-model"
        elif reasoning_type == "rule_based":
            assert "rule_matched" in result
            assert result["rule_matched"] is True
        elif reasoning_type == "bdi":
            assert "belief_updated" in result
        elif reasoning_type == "hybrid":
            assert "components_used" in result
            assert len(result["components_used"]) >= 1
    
    finally:
        # Cleanup
        await docker_harness.remove_container(container)
```

## Best Practices

1. **Clean Container Environment**: Ensure tests start with a clean container environment
2. **Resource Cleanup**: Always clean up containers, networks, and volumes after tests
3. **Container Health Checks**: Use health checks to verify containers are ready
4. **Timeout Management**: Set appropriate timeouts for container operations
5. **Resource Limitations**: Test with resource constraints to simulate real environments
6. **Network Isolation**: Use isolated networks for tests
7. **Configuration Externalization**: Test configuration via environment variables and volumes
8. **Realistic Testing**: Simulate real-world deployment scenarios
9. **Performance Monitoring**: Monitor container performance during tests
10. **Docker Compose Testing**: Test multi-container deployments with Docker Compose
11. **Protocol Agnosticism**: Test all supported protocols in containers
12. **Reasoning Agnosticism**: Test all reasoning approaches in containers

## Related Documentation

- [Containerization](../../15_deployment/containerization/README.md)
- [Docker Compose](../../15_deployment/containerization/docker_compose.md)
- [Kubernetes Deployment](../../15_deployment/kubernetes/README.md)
- [Protocol Testing](./protocol_testing.md)
- [Multi-Agent Testing](./multi_agent_testing.md)

# Multi-Agent Testing

## Overview

This document describes approaches and best practices for testing interactions between multiple OpenMAS agents. Multi-agent testing ensures that agents can communicate, coordinate, and collaborate effectively while maintaining OpenMAS's reasoning-agnostic design and multi-protocol support.

## Key Multi-Agent Testing Scenarios

OpenMAS multi-agent testing focuses on these key scenarios:

1. **Agent Communication**: Testing message exchange between agents
2. **Agent Coordination**: Testing coordination patterns between agents
3. **Workflow Execution**: Testing multi-agent workflows and tasks
4. **Error Handling**: Testing system resilience to agent failures
5. **Resource Sharing**: Testing shared resource access
6. **Protocol Interoperability**: Testing agents using different protocols

## Testing Approach

### Multi-Agent Test Fixtures

```python
import pytest
import asyncio
from openmas.testing import MultiAgentTestHarness

@pytest.fixture
async def agent_harness():
    """Create a multi-agent test harness."""
    harness = MultiAgentTestHarness()
    await harness.initialize()
    
    yield harness
    
    await harness.shutdown()

@pytest.fixture
async def two_agent_system(agent_harness):
    """Create a two-agent test system."""
    # Create assistant agent
    assistant_config = {
        "id": "assistant",
        "name": "Assistant Agent",
        "type": "assistant",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {"type": "mcp", "transport": "memory"}
    }
    
    # Create user agent
    user_config = {
        "id": "user",
        "name": "User Agent",
        "type": "user",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {"type": "mcp", "transport": "memory"}
    }
    
    # Add agents to harness
    assistant = await agent_harness.add_agent(assistant_config)
    user = await agent_harness.add_agent(user_config)
    
    yield {
        "assistant": assistant,
        "user": user,
        "harness": agent_harness
    }
```

### Testing Agent Communication

```python
async def test_agent_communication(two_agent_system):
    """Test basic communication between agents."""
    assistant = two_agent_system["assistant"]
    user = two_agent_system["user"]
    harness = two_agent_system["harness"]
    
    # Send message from user to assistant
    message = {
        "content": "Hello, Assistant!",
        "type": "text"
    }
    
    await harness.send_message(user, assistant, message)
    
    # Verify assistant received the message
    received = await harness.get_received_messages(assistant)
    assert len(received) == 1
    assert received[0]["content"] == message["content"]
    assert received[0]["sender"] == user.id
    
    # Send response from assistant to user
    response = {
        "content": "Hello, User! How can I help you?",
        "type": "text"
    }
    
    await harness.send_message(assistant, user, response)
    
    # Verify user received the response
    received = await harness.get_received_messages(user)
    assert len(received) == 1
    assert received[0]["content"] == response["content"]
    assert received[0]["sender"] == assistant.id
```

### Testing Multi-Agent Workflows

```python
async def test_multi_agent_workflow(agent_harness):
    """Test a multi-agent workflow."""
    # Create a multi-agent system with specific roles
    coordinator = await agent_harness.add_agent({
        "id": "coordinator",
        "name": "Coordinator Agent",
        "type": "coordinator",
        "capabilities": [{"id": "coordination", "type": "coordination"}]
    })
    
    worker1 = await agent_harness.add_agent({
        "id": "worker1",
        "name": "Worker Agent 1",
        "type": "worker",
        "capabilities": [{"id": "task_execution", "type": "task_execution"}]
    })
    
    worker2 = await agent_harness.add_agent({
        "id": "worker2",
        "name": "Worker Agent 2",
        "type": "worker",
        "capabilities": [{"id": "task_execution", "type": "task_execution"}]
    })
    
    # Define workflow
    workflow = {
        "id": "test_workflow",
        "steps": [
            {
                "id": "step1",
                "agent": "worker1",
                "action": "process_data",
                "input": {"data": "raw_data"}
            },
            {
                "id": "step2",
                "agent": "worker2",
                "action": "analyze_data",
                "input": {"data": "{{step1.output}}"}
            }
        ]
    }
    
    # Execute workflow
    result = await agent_harness.execute_workflow(coordinator, workflow)
    
    # Verify workflow execution
    assert result["status"] == "completed"
    assert "step1" in result["steps"]
    assert "step2" in result["steps"]
    assert result["steps"]["step1"]["status"] == "completed"
    assert result["steps"]["step2"]["status"] == "completed"
    
    # Verify message exchanges
    coordinator_messages = await agent_harness.get_sent_messages(coordinator)
    worker1_messages = await agent_harness.get_sent_messages(worker1)
    worker2_messages = await agent_harness.get_sent_messages(worker2)
    
    assert len(coordinator_messages) >= 2  # At least one message to each worker
    assert len(worker1_messages) >= 1  # At least one response to coordinator
    assert len(worker2_messages) >= 1  # At least one response to coordinator
```

### Testing Error Handling and Recovery

```python
async def test_agent_failure_handling(agent_harness):
    """Test handling of agent failures in a multi-agent system."""
    # Create agents
    coordinator = await agent_harness.add_agent({
        "id": "coordinator",
        "name": "Coordinator Agent",
        "type": "coordinator",
        "capabilities": [{"id": "coordination", "type": "coordination"}]
    })
    
    worker1 = await agent_harness.add_agent({
        "id": "worker1",
        "name": "Worker Agent 1",
        "type": "worker",
        "capabilities": [{"id": "task_execution", "type": "task_execution"}]
    })
    
    worker2 = await agent_harness.add_agent({
        "id": "worker2",
        "name": "Worker Agent 2",
        "type": "worker",
        "capabilities": [{"id": "task_execution", "type": "task_execution"}]
    })
    
    backup = await agent_harness.add_agent({
        "id": "backup",
        "name": "Backup Agent",
        "type": "worker",
        "capabilities": [{"id": "task_execution", "type": "task_execution"}]
    })
    
    # Configure worker1 to fail
    await agent_harness.configure_agent_failure(worker1, {
        "trigger": "process_data",
        "failure_type": "crash",
        "recovery_time": 2.0  # seconds
    })
    
    # Define workflow with failure handling
    workflow = {
        "id": "resilient_workflow",
        "steps": [
            {
                "id": "step1",
                "agent": "worker1",
                "action": "process_data",
                "input": {"data": "raw_data"},
                "fallback": {
                    "agent": "backup",
                    "action": "process_data"
                }
            },
            {
                "id": "step2",
                "agent": "worker2",
                "action": "analyze_data",
                "input": {"data": "{{step1.output}}"}
            }
        ]
    }
    
    # Execute workflow
    result = await agent_harness.execute_workflow(coordinator, workflow)
    
    # Verify workflow execution with failure handling
    assert result["status"] == "completed"
    assert result["steps"]["step1"]["status"] == "completed"
    assert result["steps"]["step1"]["agent"] == "backup"  # Fallback agent was used
    assert result["steps"]["step2"]["status"] == "completed"
    
    # Verify failure was detected
    failures = await agent_harness.get_agent_failures()
    assert len(failures) == 1
    assert failures[0]["agent_id"] == "worker1"
    assert failures[0]["failure_type"] == "crash"
    
    # Verify recovery
    await asyncio.sleep(2.5)  # Wait for recovery
    assert await agent_harness.is_agent_healthy(worker1)
```

### Testing Protocol Interoperability

```python
async def test_cross_protocol_communication(agent_harness):
    """Test communication between agents using different protocols."""
    # Create MCP agent
    mcp_agent = await agent_harness.add_agent({
        "id": "mcp_agent",
        "name": "MCP Agent",
        "type": "assistant",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {"type": "mcp", "transport": "memory"}
    })
    
    # Create A2A agent
    a2a_agent = await agent_harness.add_agent({
        "id": "a2a_agent",
        "name": "A2A Agent",
        "type": "user",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {"type": "a2a", "transport": "memory"}
    })
    
    # Enable protocol bridge
    await agent_harness.enable_protocol_bridge([mcp_agent, a2a_agent])
    
    # Send message from MCP agent to A2A agent
    message = {
        "content": "Hello from MCP",
        "type": "text"
    }
    
    await agent_harness.send_message(mcp_agent, a2a_agent, message)
    
    # Verify A2A agent received the message
    received = await agent_harness.get_received_messages(a2a_agent)
    assert len(received) == 1
    assert received[0]["content"] == message["content"]
    
    # Send message from A2A agent to MCP agent
    response = {
        "content": "Hello from A2A",
        "type": "text"
    }
    
    await agent_harness.send_message(a2a_agent, mcp_agent, response)
    
    # Verify MCP agent received the message
    received = await agent_harness.get_received_messages(mcp_agent)
    assert len(received) == 1
    assert received[0]["content"] == response["content"]
```

## Testing Multi-Agent with Different Reasoning Approaches

Testing interactions between agents with different reasoning approaches, respecting OpenMAS's reasoning agnosticism:

```python
async def test_mixed_reasoning_agents(agent_harness):
    """Test interaction between agents with different reasoning approaches."""
    # Create LLM-based assistant agent
    llm_agent = await agent_harness.add_agent({
        "id": "llm_agent",
        "name": "LLM Agent",
        "type": "assistant",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {"type": "mcp", "transport": "memory"},
        "reasoning": {
            "type": "llm",
            "model": "test-model",
            "settings": {"temperature": 0.7, "mock_mode": True}
        }
    })
    
    # Create rule-based agent
    rule_agent = await agent_harness.add_agent({
        "id": "rule_agent",
        "name": "Rule Agent",
        "type": "assistant",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {"type": "mcp", "transport": "memory"},
        "reasoning": {
            "type": "rule_based",
            "rules": [
                {"pattern": "Hello", "response": "Hi there!"},
                {"pattern": "Help", "response": "How can I assist?"}
            ]
        }
    })
    
    # Create BDI agent
    bdi_agent = await agent_harness.add_agent({
        "id": "bdi_agent",
        "name": "BDI Agent",
        "type": "assistant",
        "capabilities": [{"id": "messaging", "type": "messaging"}],
        "protocol": {"type": "mcp", "transport": "memory"},
        "reasoning": {
            "type": "bdi",
            "beliefs": [
                {"name": "can_help", "value": True}
            ],
            "desires": [
                {"name": "be_helpful", "priority": 1}
            ],
            "intentions": [
                {"desire": "be_helpful", "action": "respond_helpfully"}
            ]
        }
    })
    
    # Configure mock responses
    await agent_harness.configure_mock_response(
        llm_agent,
        input={"content": "Hello", "type": "text"},
        output={"content": "Hello from LLM!", "type": "text"}
    )
    
    # Test communication between different reasoning agents
    message = {"content": "Hello", "type": "text"}
    
    # Send message to LLM agent
    response1 = await agent_harness.send_and_receive_message(rule_agent, llm_agent, message)
    assert response1["content"] == "Hello from LLM!"
    
    # Send message to Rule agent
    response2 = await agent_harness.send_and_receive_message(llm_agent, rule_agent, message)
    assert response2["content"] == "Hi there!"
    
    # Send message to BDI agent
    response3 = await agent_harness.send_and_receive_message(llm_agent, bdi_agent, message)
    assert "help" in response3["content"].lower()
    
    # Test multi-step conversation
    conversation = [
        {"from": "llm_agent", "to": "rule_agent", "message": {"content": "Hello", "type": "text"}},
        {"from": "rule_agent", "to": "bdi_agent", "message": {"content": "Help", "type": "text"}},
        {"from": "bdi_agent", "to": "llm_agent", "message": {"content": "Working together", "type": "text"}}
    ]
    
    await agent_harness.execute_conversation(conversation)
    
    # Verify message flow
    llm_received = await agent_harness.get_received_messages(llm_agent)
    rule_received = await agent_harness.get_received_messages(rule_agent)
    bdi_received = await agent_harness.get_received_messages(bdi_agent)
    
    assert len(llm_received) >= 1
    assert len(rule_received) >= 1
    assert len(bdi_received) >= 1
    
    assert any("Working together" in msg["content"] for msg in llm_received)
    assert any("Hello" in msg["content"] for msg in rule_received)
    assert any("Help" in msg["content"] for msg in bdi_received)
```

## Scenario-Based Testing

```python
async def test_collaborative_task_scenario(agent_harness):
    """Test a collaborative task scenario with multiple agents."""
    # Create a system of specialized agents
    prompter = await agent_harness.add_agent({
        "id": "prompter",
        "name": "Prompter Agent",
        "type": "user",
        "capabilities": [{"id": "messaging", "type": "messaging"}]
    })
    
    planner = await agent_harness.add_agent({
        "id": "planner",
        "name": "Planner Agent",
        "type": "assistant",
        "capabilities": [{"id": "planning", "type": "planning"}]
    })
    
    researcher = await agent_harness.add_agent({
        "id": "researcher",
        "name": "Researcher Agent",
        "type": "assistant",
        "capabilities": [{"id": "research", "type": "research"}]
    })
    
    writer = await agent_harness.add_agent({
        "id": "writer",
        "name": "Writer Agent",
        "type": "assistant",
        "capabilities": [{"id": "writing", "type": "writing"}]
    })
    
    # Configure the scenario
    scenario = {
        "name": "collaborative_writing",
        "task": "Write a short article about AI",
        "steps": [
            {"agent": "prompter", "action": "send_request", "target": "planner"},
            {"agent": "planner", "action": "create_plan", "target": "researcher"},
            {"agent": "researcher", "action": "gather_information", "target": "writer"},
            {"agent": "writer", "action": "write_article", "target": "prompter"}
        ],
        "expected_result": {
            "article_written": True,
            "article_quality": "high"
        }
    }
    
    # Run the scenario
    result = await agent_harness.run_scenario(scenario)
    
    # Verify scenario execution
    assert result["status"] == "completed"
    assert result["steps_completed"] == len(scenario["steps"])
    assert "article" in result["artifacts"]
    assert result["success"] is True
```

## Best Practices

1. **Isolated Testing**: Test each agent interaction in isolation
2. **Comprehensive Scenarios**: Test realistic multi-agent scenarios
3. **Protocol Variety**: Test interactions across different protocols
4. **Error Resilience**: Test recovery from agent failures
5. **Resource Management**: Test resource sharing and contention
6. **Reasoning Agnosticism**: Test interactions between different reasoning approaches
7. **Observable Interactions**: Monitor all message exchanges
8. **Deterministic Testing**: Ensure reproducible test results
9. **Realistic Latency**: Simulate realistic network conditions
10. **Scalability Testing**: Test with varying numbers of agents

## Related Documentation

- [Test Supervisor](../framework/test_supervisor.md)
- [Protocol Testing](./protocol_testing.md)
- [Async Integration](./async_integration.md)
- [Docker Integration](./docker_integration.md)
- [Agent Supervisor](../../15_deployment/local/agent_supervisor.md)
- [Multi-Agent Local Deployment](../../15_deployment/local/multi_agent_local.md)

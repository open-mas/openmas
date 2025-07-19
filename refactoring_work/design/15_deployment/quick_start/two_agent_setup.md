# Two Agent Setup: Quick Start Guide

This guide provides a quick start approach to set up and deploy two communicating OpenMAS agents on a single machine. This is the simplest deployment scenario and serves as an excellent introduction to OpenMAS's multi-agent capabilities.

## Overview

In this guide, you'll set up:

1. A "sender" agent that generates and sends messages
2. A "receiver" agent that receives and processes messages
3. Communication between agents using either A2A or MCP protocol

## Prerequisites

- OpenMAS CLI tools installed (see [Installation Guide](../../13_cli_tools/installation/installation_guide.md))
- Python 3.9 or higher

## Step 1: Initialize a New OpenMAS Project

```bash
# Create a new project directory
mkdir openmas-two-agent-demo
cd openmas-two-agent-demo

# Initialize a new OpenMAS project
openmas init --name two-agent-demo
```

This creates a basic OpenMAS project structure with configuration templates.

## Step 2: Create Agent Configurations

Create configuration files for both agents:

```bash
# Generate configuration templates for two agents
openmas config create --agent sender --protocol a2a
openmas config create --agent receiver --protocol a2a
```

## Step 3: Customize Agent Configurations

Edit the generated configuration files to define agent capabilities:

**sender_config.yaml**:
```yaml
name: sender
version: "1.0"
agent_type: sender
description: "Agent that sends messages"

multi_protocol_capabilities:
  core:
    - name: send_message
      description: "Capability to send messages"
      parameters:
        message_type: string
        content: object
  protocol_mapping:
    a2a:
      send_message:
        function_name: send_text_content
        parameter_mapping:
          message_type: type
          content: content

communication:
  primary_protocol: a2a
  protocols:
    a2a:
      mode: client
      endpoint: http://localhost:8080
      authenticator:
        type: basic
        api_key: ${OPENMAS_API_KEY}

reasoning:
  engine: simple_rule
  rules:
    - when: startup
      then: send_greeting
  actions:
    send_greeting:
      capability: send_message
      parameters:
        message_type: greeting
        content: { "text": "Hello from sender agent!" }
```

**receiver_config.yaml**:
```yaml
name: receiver
version: "1.0"
agent_type: receiver
description: "Agent that receives messages"

multi_protocol_capabilities:
  core:
    - name: receive_message
      description: "Capability to receive messages"
      parameters:
        message_type: string
        content: object
  protocol_mapping:
    a2a:
      receive_message:
        function_name: receive_content
        parameter_mapping:
          message_type: type
          content: content

communication:
  primary_protocol: a2a
  protocols:
    a2a:
      mode: server
      endpoint: http://localhost:8080
      authenticator:
        type: basic
        api_key: ${OPENMAS_API_KEY}

reasoning:
  engine: simple_rule
  rules:
    - when: message_received
      then: log_message
  actions:
    log_message:
      capability: internal.log
      parameters:
        level: info
        message: "Received message: {{message.content}}"
```

## Step 4: Deploy and Run the Agents

Use the deploy command to run both agents:

```bash
# First, set environment variables
export OPENMAS_API_KEY=demo123

# Start the receiver agent
openmas run agent --config receiver_config.yaml &

# Wait a moment for the receiver to start
sleep 2

# Start the sender agent
openmas run agent --config sender_config.yaml
```

Alternatively, use the deploy command for a more managed deployment:

```bash
# Create a deployment configuration
cat > deployment.yaml << EOF
version: "1"
environment: local

components:
  receiver:
    type: agent
    config: receiver_config.yaml
  
  sender:
    type: agent
    config: sender_config.yaml
    depends_on:
      - receiver
EOF

# Deploy both agents
openmas deploy up --file deployment.yaml
```

## Step 5: Verify Communication

You should see output indicating that:
1. The receiver agent started and is listening for messages
2. The sender agent started and sent a greeting message
3. The receiver agent received and logged the greeting message

## Extending This Example

This simple setup can be extended to:

1. Use the MCP protocol instead of A2A by changing the protocol configuration
2. Add more complex reasoning via LLM-based engines or BDI architecture
3. Add more agents to create larger networks

## Related Documentation

- [Local Deployment](../local/README.md)
- [Agent Configuration](../../03_configuration/schema/agents.md)
- [Protocol Configuration](../../03_configuration/schema/protocols.md)
- [Deploy Command](../../13_cli_tools/commands/deploy.md)

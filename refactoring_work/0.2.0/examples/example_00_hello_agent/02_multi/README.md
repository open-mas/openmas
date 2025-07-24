# Hello World Multi-Agent Example (Real Communicator)

This example demonstrates a simple two-agent interaction using real HTTP communicators (not mocks).

## Overview

This example consists of two agents:

1. **Sender Agent** - Actively sends a greeting message to the receiver agent
2. **Receiver Agent** - Passively waits for and responds to messages from sender

Both agents use real HTTP communicators to enable actual network communication.

## Purpose

This example demonstrates:
- How to set up multiple agents with proper HTTP communication channels
- How to implement request/response patterns between agents
- How to make agents wait for each other before sending messages
- How to handle simple message passing in a distributed system

## Running the Example

This example requires running the agents in separate terminals to enable real communication between them.

### Method 1: Running from the OpenMAS project root

To run this example from the OpenMAS project root, open **two separate terminal windows** and run:

```bash
# In terminal 1 - Start the receiver agent
tox -e example-00-hello-agent-02-multi-receiver

# In terminal 2 - Start the sender agent
tox -e example-00-hello-agent-02-multi-sender
```

### Method 2: Running directly using OpenMAS CLI

Alternatively, you can navigate to the example directory and run the agents using the OpenMAS CLI:

```bash
# In terminal 1 - Start the receiver agent
cd examples/example_00_hello_agent/02_multi
openmas run receiver

# In terminal 2 - Start the sender agent
cd examples/example_00_hello_agent/02_multi
openmas run sender
```

## What You'll See

1. The receiver agent will start and wait for incoming messages
2. The sender agent will start and automatically detect when the receiver is available
3. Once connected, the sender will send a greeting message to the receiver
4. The receiver will process the message and send a response
5. Both agents will log their activities
6. The sender will perform a countdown and terminate automatically

## Example Logs

The sender and receiver logs can be captured to files using output redirection:

```bash
# Capture receiver logs
openmas run receiver > receiver_logs.txt 2>&1

# Capture sender logs
openmas run sender > sender_logs.txt 2>&1
```

## Automated Testing Solution

This example includes a programmatic solution for running and testing multiple agents simultaneously within a single test script. This approach solves several key challenges:

1. **Running multiple blocking agents**: Uses subprocess to run each agent in separate processes
2. **Log capture**: Redirects all agent output to temporary log files for analysis
3. **Communication verification**: Monitors agent logs to confirm successful message exchange
4. **Graceful termination**: Implements proper process cleanup with SIGTERM/SIGKILL signals

To run the automated test:

```bash
# From the OpenMAS project root
tox -e example-00-hello-agent-02-multi-test
```

Or directly with pytest:

```bash
cd examples/example_00_hello_agent/02_multi
pytest test_example.py -v
```

This solution provides a template for creating more complex multi-agent tests that require real communication between agents without manual intervention.

## Troubleshooting

- If the agents fail to connect, ensure both are running and their ports (8001 and 8002) are not in use
- Check the `openmas_project.yml` file to verify the communication settings
- Ensure no firewall is blocking the communication between the agents

## Learning Goals

This example demonstrates:
1. Setting up real HTTP-based communication between agents
2. Implementing agent communication with proper request/response patterns
3. Using agent background tasks to wait for other agents to come online
4. Setting up port configurations to prevent conflicts
5. Properly handling message exchange between distributed agents

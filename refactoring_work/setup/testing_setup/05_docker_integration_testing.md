# Docker-Based Integration Testing for OpenMAS 0.3.0

## Overview

This document outlines a comprehensive Docker-based approach for real integration testing of OpenMAS agents, focusing on testing with actual AI components and real protocol interactions. This strategy ensures we validate the complete system with real-world interactions rather than mocks.

## Why Docker for Integration Testing

For OpenMAS's reasoning-agnostic architecture, Docker provides several critical advantages:

1. **Environment Isolation**: Each agent runs in its own container with a controlled environment
2. **Protocol Independence**: Tests real network communications between containers
3. **Reasoning Diversity**: Can test different reasoning approaches in parallel
4. **Resource Management**: Clean resource allocation and cleanup
5. **CI/CD Integration**: Reproducible tests in automated pipelines
6. **Scale Testing**: Ability to test with many agents at scale

## Docker-Based Testing Architecture

### 1. Multi-Container Test Framework

Each integration test scenario uses a Docker Compose configuration with multiple containers:

```
+-----------------+     +------------------+     +------------------+
| Test Controller |     | OpenMAS Agent 1  |     | OpenMAS Agent 2  |
| (pytest)        |<--->| (A2A Protocol)   |<--->| (MCP Protocol)   |
+-----------------+     +------------------+     +------------------+
        |                        |                       |
        v                        v                       v
+--------------------------------------------------------------------+
|                   Shared Docker Network                            |
+--------------------------------------------------------------------+
        |                        |                       |
        v                        v                       v
+-----------------+     +------------------+     +------------------+
| LLM Service     |     | External Service |     | Monitoring       |
| (LLM API)       |     | (if needed)      |     | (Observability)  |
+-----------------+     +------------------+     +------------------+
```

### 2. Base Docker Compose Template

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  # Test controller - runs the integration tests
  test-controller:
    build:
      context: .
      dockerfile: Dockerfile.test
    volumes:
      - ./test-results:/app/test-results
    networks:
      - openmas-test-network
    depends_on:
      - agent1
      - agent2
    environment:
      - TEST_TIMEOUT=60
      - AGENT1_URL=http://agent1:8080
      - AGENT2_URL=http://agent2:8080
    command: ["pytest", "tests/integration/docker/", "-v", "--junit-xml=/app/test-results/results.xml"]

  # Agent 1 - using A2A protocol
  agent1:
    build:
      context: .
      dockerfile: Dockerfile.agent
    volumes:
      - ./test-configs/agent1:/app/config
    networks:
      - openmas-test-network
    environment:
      - OPENMAS_CONFIG_PATH=/app/config/config.yaml
      - OPENMAS_LOG_LEVEL=DEBUG
    command: ["python", "-m", "openmas.cli", "start", "--config", "/app/config/config.yaml"]
    ports:
      - "8081:8080"  # exposed for debugging

  # Agent 2 - using MCP protocol
  agent2:
    build:
      context: .
      dockerfile: Dockerfile.agent
    volumes:
      - ./test-configs/agent2:/app/config
    networks:
      - openmas-test-network
    environment:
      - OPENMAS_CONFIG_PATH=/app/config/config.yaml
      - OPENMAS_LOG_LEVEL=DEBUG
    command: ["python", "-m", "openmas.cli", "start", "--config", "/app/config/config.yaml"]
    ports:
      - "8082:8080"  # exposed for debugging

  # If needed: Mock LLM service for consistent test responses
  llm-service:
    build:
      context: ./tests/integration/docker/llm-service
      dockerfile: Dockerfile
    networks:
      - openmas-test-network
    ports:
      - "8090:8080"  # exposed for debugging
    environment:
      - RESPONSE_MODE=deterministic
      - RESPONSE_DELAY=0.5

networks:
  openmas-test-network:
    driver: bridge
```

### 3. Dockerfiles

#### Agent Dockerfile

```dockerfile
# Dockerfile.agent
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --extras "all"

# Copy application code
COPY src/ /app/src/

# Health check to ensure agent is running
HEALTHCHECK --interval=5s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080

# Default command runs the agent (overridden in docker-compose)
CMD ["python", "-m", "openmas.cli", "start"]
```

#### Test Controller Dockerfile

```dockerfile
# Dockerfile.test
FROM python:3.10-slim

WORKDIR /app

# Install dependencies including test requirements
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --extras "all"

# Copy application code and tests
COPY src/ /app/src/
COPY tests/ /app/tests/

# Default command runs integration tests (overridden in docker-compose)
CMD ["pytest", "tests/integration/docker/", "-v"]
```

## Test Implementation

### 1. Test Configuration

Create protocol-specific configurations for test agents:

```yaml
# test-configs/agent1/config.yaml
name: "test-agent1"
version: "0.3.0"
description: "Test Agent with A2A Protocol"

agents:
  agent1:
    class: "openmas.agent.Agent"
    type: "test"
    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://agent1:8080"
          agent_card:
            name: "Test Agent 1"
            description: "A2A Test Agent"
            capabilities:
              text:
                enabled: true
                models: ["test-model"]
    capabilities:
      text_generation:
        enabled: true
        options:
          model: "test-model"
          max_tokens: 100
    reasoning:
      type: "rule_based"  # Can test different reasoning types
```

```yaml
# test-configs/agent2/config.yaml
name: "test-agent2"
version: "0.3.0"
description: "Test Agent with MCP Protocol"

agents:
  agent2:
    class: "openmas.agent.Agent"
    type: "test"
    protocols:
      - type: "mcp-sse"
        enabled: true
        options:
          server_mode: true
          http_port: 8080
          server_name: "Test MCP Server"
    capabilities:
      search:
        enabled: true
        options:
          max_results: 5
    reasoning:
      type: "llm_based"  # Can test different reasoning types
      service_url: "http://llm-service:8080/generate"
```

### 2. Integration Test Structure

```python
# tests/integration/docker/test_a2a_mcp_integration.py
import pytest
import requests
import time
import os
import json

# URLs provided by docker-compose environment variables
AGENT1_URL = os.environ.get("AGENT1_URL", "http://agent1:8080")
AGENT2_URL = os.environ.get("AGENT2_URL", "http://agent2:8080")
TEST_TIMEOUT = int(os.environ.get("TEST_TIMEOUT", "60"))

def wait_for_agent_ready(url, max_attempts=10, delay=1):
    """Wait for an agent to be ready."""
    for _ in range(max_attempts):
        try:
            response = requests.get(f"{url}/health")
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(delay)
    return False

@pytest.fixture(scope="module")
def setup_agents():
    """Ensure agents are ready before testing."""
    assert wait_for_agent_ready(AGENT1_URL), "Agent 1 is not ready"
    assert wait_for_agent_ready(AGENT2_URL), "Agent 2 is not ready"

    # Give agents additional time to initialize fully
    time.sleep(2)

    # Return agent URLs for convenience
    return AGENT1_URL, AGENT2_URL

def test_a2a_to_mcp_communication(setup_agents):
    """Test A2A agent can communicate with MCP agent."""
    agent1_url, agent2_url = setup_agents

    # Get A2A agent card
    response = requests.get(f"{agent1_url}/.well-known/agent.json")
    assert response.status_code == 200
    agent_card = response.json()
    assert agent_card["name"] == "Test Agent 1"

    # Send message from A2A agent to MCP agent
    message = {
        "target_agent_id": "agent2",
        "message": {
            "content": "Hello from A2A agent",
            "task_id": "test-task-1"
        }
    }
    response = requests.post(
        f"{agent1_url}/messages/send",
        json=message
    )
    assert response.status_code == 200

    # Check if message was received by MCP agent
    # Wait with retry since async communication may have delays
    max_retries = 5
    for i in range(max_retries):
        response = requests.get(f"{agent2_url}/messages/received")
        if response.status_code == 200 and len(response.json()) > 0:
            received_messages = response.json()
            assert any(msg["content"] == "Hello from A2A agent" for msg in received_messages)
            break
        if i < max_retries - 1:
            time.sleep(2)  # Wait before retry
    else:
        pytest.fail("Message not received by MCP agent")

def test_mcp_to_a2a_communication(setup_agents):
    """Test MCP agent can communicate with A2A agent."""
    agent1_url, agent2_url = setup_agents

    # Get MCP tools list
    response = requests.get(f"{agent2_url}/tools")
    assert response.status_code == 200
    tools = response.json()
    assert any(tool["name"] == "search" for tool in tools)

    # Execute MCP tool that sends message to A2A agent
    tool_request = {
        "name": "send_message",
        "parameters": {
            "target_agent_id": "agent1",
            "content": "Hello from MCP agent"
        }
    }
    response = requests.post(
        f"{agent2_url}/tools/execute",
        json=tool_request
    )
    assert response.status_code == 200

    # Check if message was received by A2A agent
    max_retries = 5
    for i in range(max_retries):
        response = requests.get(f"{agent1_url}/messages/received")
        if response.status_code == 200 and len(response.json()) > 0:
            received_messages = response.json()
            assert any(msg["content"] == "Hello from MCP agent" for msg in received_messages)
            break
        if i < max_retries - 1:
            time.sleep(2)  # Wait before retry
    else:
        pytest.fail("Message not received by A2A agent")

def test_agent_reasoning_capabilities(setup_agents):
    """Test agents with different reasoning capabilities."""
    agent1_url, agent2_url = setup_agents

    # Test rule-based reasoning in Agent 1 (A2A)
    rule_test = {
        "input": "test rule",
        "expected_action": "rule_response"
    }
    response = requests.post(
        f"{agent1_url}/reasoning/process",
        json=rule_test
    )
    assert response.status_code == 200
    result = response.json()
    assert result["action"] == "rule_response"

    # Test LLM-based reasoning in Agent 2 (MCP)
    llm_test = {
        "input": "test llm",
        "max_tokens": 50
    }
    response = requests.post(
        f"{agent2_url}/reasoning/process",
        json=llm_test
    )
    assert response.status_code == 200
    result = response.json()
    assert "generated_text" in result
```

### 3. Mock LLM Service for Deterministic Testing

Create a simple mock LLM service for consistent test responses:

```python
# tests/integration/docker/llm-service/app.py
from fastapi import FastAPI, HTTPException
import time
import os
import random
import json

app = FastAPI(title="Mock LLM Service")

# Configuration from environment
RESPONSE_MODE = os.environ.get("RESPONSE_MODE", "deterministic")
RESPONSE_DELAY = float(os.environ.get("RESPONSE_DELAY", "0.0"))
ERROR_RATE = float(os.environ.get("ERROR_RATE", "0.0"))

# Predefined responses for deterministic testing
CANNED_RESPONSES = {
    "test llm": "This is a test response from the mock LLM service.",
    "search weather": "The weather is sunny today.",
    "generate story": "Once upon a time in a test environment...",
    "default": "I'm a mock LLM service for testing."
}

@app.post("/generate")
async def generate_text(request: dict):
    """Mock LLM generation endpoint."""
    # Simulate processing delay
    if RESPONSE_DELAY > 0:
        time.sleep(RESPONSE_DELAY)

    # Simulate random errors if configured
    if ERROR_RATE > 0 and random.random() < ERROR_RATE:
        raise HTTPException(status_code=500, detail="Simulated error")

    # Get input text from request
    input_text = request.get("prompt", "")
    max_tokens = request.get("max_tokens", 100)

    # Generate response based on mode
    if RESPONSE_MODE == "deterministic":
        # Use canned responses for deterministic testing
        for key, response in CANNED_RESPONSES.items():
            if key in input_text.lower():
                return {"generated_text": response[:max_tokens]}
        return {"generated_text": CANNED_RESPONSES["default"][:max_tokens]}
    else:
        # Simple echo mode for testing
        return {"generated_text": f"Echo: {input_text[:max_tokens]}"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
```

```dockerfile
# tests/integration/docker/llm-service/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
RUN pip install fastapi uvicorn

# Copy application code
COPY app.py .

# Expose port
EXPOSE 8080

# Run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Running Integration Tests

### 1. Manually Running Tests

```bash
# Build and run the Docker Compose setup
docker-compose -f docker-compose.test.yml build
docker-compose -f docker-compose.test.yml up --abort-on-container-exit

# View test results
cat test-results/results.xml
```

### 2. CI/CD Implementation for OpenMAS

Implementing a comprehensive CI/CD pipeline for OpenMAS integration tests requires careful consideration of the framework's reasoning-agnostic architecture and multi-protocol support. Here's how to set it up:

#### a. GitHub Actions Workflow with Smart Test Selection

```yaml
# .github/workflows/integration-tests.yml
name: OpenMAS Integration Tests

on:
  push:
    branches: [ main, 030 ]
    paths-ignore:
      - '**.md'
      - 'docs/**'
  pull_request:
    branches: [ main, 030 ]
  workflow_dispatch:  # Allow manual triggering

jobs:
  # First job: Determine which tests to run based on changed files
  determine-test-matrix:
    runs-on: ubuntu-latest
    outputs:
      test-matrix: ${{ steps.set-matrix.outputs.matrix }}

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0  # Fetch all history for file change detection

      - name: Determine test matrix
        id: set-matrix
        run: |
          # Analyze changed files to determine which tests to run
          if [ "${{ github.event_name }}" = "pull_request" ]; then
            CHANGED_FILES=$(git diff --name-only origin/${{ github.base_ref }}...HEAD)
          else
            # For push events, get changed files in the last commit
            CHANGED_FILES=$(git diff-tree --no-commit-id --name-only -r ${{ github.sha }})
          fi

          # Initialize test configurations array
          CONFIGS=()

          # Always include basic protocol tests
          CONFIGS+=('{\'name\': \'protocol-basic\', \'compose\': \'docker-compose.test.yml\'}')

          # Check for A2A-specific changes
          if echo "$CHANGED_FILES" | grep -q "src/openmas/protocols/a2a\|src/openmas/communicators/a2a"; then
            CONFIGS+=('{\'name\': \'protocol-a2a\', \'compose\': \'docker-compose.a2a.yml\'}')
          fi

          # Check for MCP-specific changes
          if echo "$CHANGED_FILES" | grep -q "src/openmas/protocols/mcp\|src/openmas/communicators/mcp"; then
            CONFIGS+=('{\'name\': \'protocol-mcp\', \'compose\': \'docker-compose.mcp.yml\'}')
          fi

          # Check for changes in reasoning modules
          if echo "$CHANGED_FILES" | grep -q "src/openmas/reasoning"; then
            CONFIGS+=('{\'name\': \'reasoning-tests\', \'compose\': \'docker-compose.reasoning.yml\'}')
          fi

          # For PRs to main or manual triggers, run all test suites
          if [ "${{ github.event_name }}" = "workflow_dispatch" ] || \
             [ "${{ github.base_ref }}" = "main" ]; then
            CONFIGS=(
              '{\'name\': \'protocol-basic\', \'compose\': \'docker-compose.test.yml\'}'
              '{\'name\': \'protocol-a2a\', \'compose\': \'docker-compose.a2a.yml\'}'
              '{\'name\': \'protocol-mcp\', \'compose\': \'docker-compose.mcp.yml\'}'
              '{\'name\': \'reasoning-tests\', \'compose\': \'docker-compose.reasoning.yml\'}'
              '{\'name\': \'performance\', \'compose\': \'docker-compose.performance.yml\'}'
            )
          fi

          # Output the matrix for the next job
          echo "matrix={\"include\":[$(IFS=,; echo "${CONFIGS[*]}")]}"
          echo "matrix={\"include\":[$(IFS=,; echo "${CONFIGS[*]}")]}"

  # Main job: Run tests in parallel based on matrix
  integration-tests:
    needs: determine-test-matrix
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false  # Continue running tests even if one fails
      matrix: ${{fromJson(needs.determine-test-matrix.outputs.test-matrix)}}

    steps:
      - uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      # Cache Docker layers for faster builds
      - name: Cache Docker layers
        uses: actions/cache@v3
        with:
          path: /tmp/.buildx-cache
          key: ${{ runner.os }}-buildx-${{ github.sha }}-${{ matrix.name }}
          restore-keys: |
            ${{ runner.os }}-buildx-

      # Generate agent configurations from the unified schema
      - name: Generate test configurations
        run: |
          mkdir -p test-configs
          # Use the OpenMAS configuration CLI to generate test configs
          python -m openmas.cli config generate \
            --template=tests/templates/${{ matrix.name }}.yaml \
            --output-dir=test-configs/${{ matrix.name }}

      # Build and run tests with timeout
      - name: Build and run integration tests
        run: |
          # Build with cache
          docker-compose -f ${{ matrix.compose }} build \
            --build-arg BUILDKIT_INLINE_CACHE=1

          # Set a timeout to prevent hung tests from blocking CI
          timeout 15m docker-compose -f ${{ matrix.compose }} up \
            --abort-on-container-exit \
            --exit-code-from test-controller

      # Upload test results and logs
      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: test-results-${{ matrix.name }}
          path: test-results/
          if-no-files-found: error

      - name: Upload test logs
        uses: actions/upload-artifact@v3
        with:
          name: test-logs-${{ matrix.name }}
          path: test-results/logs/
          if-no-files-found: warn

      # Add PR comment with results summary
      - name: Comment on PR with test results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            const summary = fs.readFileSync('test-results/summary.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `## Integration Test Results: ${{ matrix.name }}\n\n${summary}`
            });

  # Final job: Combine test results
  test-summary:
    needs: integration-tests
    runs-on: ubuntu-latest
    if: always()  # Run even if previous jobs failed

    steps:
      - uses: actions/checkout@v3

      - name: Download all test results
        uses: actions/download-artifact@v3
        with:
          path: all-test-results

      - name: Generate summary report
        run: |
          python tools/ci/generate_test_report.py \
            --results-dir=all-test-results \
            --output-html=test-report.html \
            --output-badge=badge.svg

      - name: Upload combined report
        uses: actions/upload-artifact@v3
        with:
          name: test-report
          path: |
            test-report.html
            badge.svg
```

#### b. Supporting Tools & Scripts

To support the CI/CD pipeline, the following scripts are needed:

1. **Test Configuration Generator** - Creates Docker configurations from the unified schema:

```python
# tools/ci/generate_test_configs.py
import argparse
import yaml
import os
from openmas.config import ConfigurationManager

def main():
    parser = argparse.ArgumentParser(description="Generate OpenMAS test configurations")
    parser.add_argument("--protocol", choices=["a2a", "mcp", "all"], default="all")
    parser.add_argument("--reasoning", choices=["rule", "bdi", "llm", "hybrid", "all"], default="all")
    parser.add_argument("--output-dir", default="test-configs")
    args = parser.parse_args()

    config_manager = ConfigurationManager()

    # Generate configurations for each requested protocol
    protocols = ["a2a", "mcp"] if args.protocol == "all" else [args.protocol]
    reasoning_types = (["rule_based", "bdi", "llm_based", "hybrid"]
                      if args.reasoning == "all" else [args.reasoning])

    for protocol in protocols:
        for reasoning in reasoning_types:
            config = config_manager.create_test_config(protocol, reasoning)

            # Save configuration
            output_path = f"{args.output_dir}/{protocol}_{reasoning}"
            os.makedirs(output_path, exist_ok=True)

            with open(f"{output_path}/config.yaml", "w") as f:
                yaml.dump(config, f)

if __name__ == "__main__":
    main()
```

2. **Test Result Processor** - Processes test results and generates reports:

```python
# tools/ci/process_test_results.py
import argparse
import xml.etree.ElementTree as ET
import json
import os

def main():
    parser = argparse.ArgumentParser(description="Process test results")
    parser.add_argument("--results-file", required=True)
    parser.add_argument("--output-markdown", required=True)
    args = parser.parse_args()

    tree = ET.parse(args.results_file)
    root = tree.getroot()

    # Extract test results
    total_tests = int(root.attrib.get("tests", 0))
    failures = int(root.attrib.get("failures", 0))
    errors = int(root.attrib.get("errors", 0))
    skipped = int(root.attrib.get("skipped", 0))
    time = float(root.attrib.get("time", 0))

    # Generate markdown summary
    with open(args.output_markdown, "w") as f:
        f.write(f"### Test Summary\n\n")
        f.write(f"- Total Tests: {total_tests}\n")
        f.write(f"- Passed: {total_tests - failures - errors - skipped}\n")
        f.write(f"- Failed: {failures}\n")
        f.write(f"- Errors: {errors}\n")
        f.write(f"- Skipped: {skipped}\n")
        f.write(f"- Total Time: {time:.2f}s\n\n")

        # Add failure details if any
        if failures > 0 or errors > 0:
            f.write("### Failures and Errors\n\n")
            for testcase in root.findall(".//testcase"):
                failure = testcase.find("failure")
                error = testcase.find("error")

                if failure is not None or error is not None:
                    problem = failure if failure is not None else error
                    f.write(f"**{testcase.attrib.get('classname')}.{testcase.attrib.get('name')}**\n\n")
                    f.write(f"```\n{problem.text}\n```\n\n")

if __name__ == "__main__":
    main()
```

#### c. Docker Configuration Templates

Create Docker Compose templates for different test scenarios:

1. **A2A Protocol Testing**

```yaml
# docker-compose.a2a.yml
version: '3.8'

services:
  test-controller:
    build:
      context: .
      dockerfile: Dockerfile.test
    volumes:
      - ./test-results:/app/test-results
    networks:
      - openmas-test-network
    depends_on:
      - agent1
      - agent2
    environment:
      - TEST_PATTERN=tests/integration/protocols/a2a/*.py
      - AGENT1_URL=http://agent1:8080
      - AGENT2_URL=http://agent2:8080
    command: ["python", "-m", "pytest", "${TEST_PATTERN}", "-v", "--junit-xml=/app/test-results/results.xml"]

  agent1:
    build:
      context: .
      dockerfile: Dockerfile.agent
    volumes:
      - ./test-configs/a2a_rule_based/agent1:/app/config
    networks:
      - openmas-test-network
    environment:
      - OPENMAS_CONFIG_PATH=/app/config/config.yaml
      - OPENMAS_LOG_LEVEL=DEBUG
    command: ["python", "-m", "openmas.cli", "start", "--config", "/app/config/config.yaml"]

  agent2:
    build:
      context: .
      dockerfile: Dockerfile.agent
    volumes:
      - ./test-configs/a2a_rule_based/agent2:/app/config
    networks:
      - openmas-test-network
    environment:
      - OPENMAS_CONFIG_PATH=/app/config/config.yaml
      - OPENMAS_LOG_LEVEL=DEBUG
    command: ["python", "-m", "openmas.cli", "start", "--config", "/app/config/config.yaml"]

networks:
  openmas-test-network:
    driver: bridge
```

2. **Reasoning Tests**

```yaml
# docker-compose.reasoning.yml
version: '3.8'

services:
  test-controller:
    build:
      context: .
      dockerfile: Dockerfile.test
    volumes:
      - ./test-results:/app/test-results
    networks:
      - openmas-test-network
    depends_on:
      - rule-agent
      - bdi-agent
      - llm-agent
      - hybrid-agent
      - llm-service
    environment:
      - TEST_PATTERN=tests/integration/reasoning/*.py
      - RULE_AGENT_URL=http://rule-agent:8080
      - BDI_AGENT_URL=http://bdi-agent:8080
      - LLM_AGENT_URL=http://llm-agent:8080
      - HYBRID_AGENT_URL=http://hybrid-agent:8080
    command: ["python", "-m", "pytest", "${TEST_PATTERN}", "-v", "--junit-xml=/app/test-results/results.xml"]

  rule-agent:
    build:
      context: .
      dockerfile: Dockerfile.agent
    volumes:
      - ./test-configs/a2a_rule_based/agent1:/app/config
    networks:
      - openmas-test-network
    environment:
      - OPENMAS_CONFIG_PATH=/app/config/config.yaml
      - OPENMAS_LOG_LEVEL=DEBUG

  bdi-agent:
    build:
      context: .
      dockerfile: Dockerfile.agent
    volumes:
      - ./test-configs/a2a_bdi/agent1:/app/config
    networks:
      - openmas-test-network
    environment:
      - OPENMAS_CONFIG_PATH=/app/config/config.yaml
      - OPENMAS_LOG_LEVEL=DEBUG

  llm-agent:
    build:
      context: .
      dockerfile: Dockerfile.agent
    volumes:
      - ./test-configs/a2a_llm_based/agent1:/app/config
    networks:
      - openmas-test-network
    environment:
      - OPENMAS_CONFIG_PATH=/app/config/config.yaml
      - OPENMAS_LOG_LEVEL=DEBUG
      - LLM_SERVICE_URL=http://llm-service:8080/generate

  hybrid-agent:
    build:
      context: .
      dockerfile: Dockerfile.agent
    volumes:
      - ./test-configs/a2a_hybrid/agent1:/app/config
    networks:
      - openmas-test-network
    environment:
      - OPENMAS_CONFIG_PATH=/app/config/config.yaml
      - OPENMAS_LOG_LEVEL=DEBUG
      - LLM_SERVICE_URL=http://llm-service:8080/generate

  llm-service:
    build:
      context: ./tests/integration/docker/llm-service
      dockerfile: Dockerfile
    networks:
      - openmas-test-network
    environment:
      - RESPONSE_MODE=deterministic
      - RESPONSE_DELAY=0.2

networks:
  openmas-test-network:
    driver: bridge
```

#### d. Testing OpenMAS's Reasoning Agnosticism

The CI/CD pipeline specifically addresses OpenMAS's reasoning-agnostic architecture by:

1. **Protocol-Independent Testing** - Tests verify each protocol operates correctly independent of the reasoning approach
2. **Reasoning Module Interchangeability** - Tests validate that different reasoning modules can be swapped without breaking protocol functionality
3. **Configuration-Driven Testing** - Using the unified configuration schema to generate test configurations ensures configuration correctness
4. **Cross-Protocol Communication** - Tests verify that agents using different reasoning approaches can communicate properly across protocols

#### e. CI/CD Pipeline Integration with OpenMAS Development

```
graph TD
    A[Developer Push] --> B[Determine Test Matrix]
    B --> C[Run Protocol Tests]
    B --> D[Run Reasoning Tests]
    B --> E[Run Performance Tests]
    C --> F[Generate Test Report]
    D --> F
    E --> F
    F --> G[PR Review with Test Results]
    G --> H{Merge?}
    H -->|Yes| I[Run Full Test Suite]
    H -->|No| J[Address Test Failures]
    J --> A
    I --> K[Generate Release Artifacts]
    K --> L[Deploy to Registry]
```

#### f. Local Development Testing

For developers working on OpenMAS, simplified Docker Compose commands can be used:

```bash
# Run all tests
docker-compose -f docker-compose.test.yml up --build

# Run specific protocol tests
TEST_PATTERN="tests/integration/protocols/a2a/*.py" docker-compose -f docker-compose.test.yml up --build

# Test with specific reasoning approach
docker-compose -f docker-compose.reasoning.yml up --build rule-agent test-controller
```

The CI/CD pipeline integrates seamlessly with GitHub's code review process, providing detailed feedback on integration test results directly in PR comments, making it easier to identify and resolve issues related to OpenMAS's reasoning-agnostic architecture and multi-protocol capabilities.

## Testing Different Reasoning Approaches

To test OpenMAS's reasoning agnosticism, create different agent configurations with various reasoning approaches:

### Rule-Based Agent Configuration

```yaml
reasoning:
  type: "rule_based"
  rules_file: "/app/config/rules.json"
```

### BDI Agent Configuration

```yaml
reasoning:
  type: "bdi"
  beliefs_file: "/app/config/initial_beliefs.json"
  desires_file: "/app/config/desires.json"
  intentions_file: "/app/config/intentions.json"
```

### LLM-Based Agent Configuration

```yaml
reasoning:
  type: "llm_based"
  service_url: "http://llm-service:8080/generate"
  model: "test-model"
  system_prompt: "You are a helpful assistant."
```

### Hybrid Agent Configuration

```yaml
reasoning:
  type: "hybrid"
  components:
    - type: "rule_based"
      rules_file: "/app/config/rules.json"
      priority: 1
    - type: "llm_based"
      service_url: "http://llm-service:8080/generate"
      model: "test-model"
      priority: 2
  fallback: "llm_based"
```

## Testing Protocol Compatibility

Create test scenarios to verify protocol interoperability:

1. **A2A-A2A Communication**: Test two A2A agents communicating
2. **MCP-MCP Communication**: Test two MCP agents communicating
3. **A2A-MCP Communication**: Test A2A agent communicating with MCP agent
4. **Multi-Protocol Agent**: Test agent supporting both A2A and MCP simultaneously

## Observability and Debugging

Add a monitoring container to capture logs and metrics:

```yaml
# Add to docker-compose.test.yml
monitoring:
  build:
    context: ./tests/integration/docker/monitoring
    dockerfile: Dockerfile
  volumes:
    - ./test-results/logs:/logs
  networks:
    - openmas-test-network
  depends_on:
    - agent1
    - agent2
  environment:
    - AGENT1_URL=http://agent1:8080
    - AGENT2_URL=http://agent2:8080
    - COLLECT_INTERVAL=1
```

This container can collect logs, metrics, and other diagnostic information to help debug test failures.

## Advanced Testing Scenarios

### 1. Protocol Stress Testing

```python
def test_protocol_stress(setup_agents):
    """Test protocol performance under load."""
    agent1_url, _ = setup_agents

    # Send 100 messages in quick succession
    results = []
    for i in range(100):
        message = {
            "target_agent_id": "agent2",
            "message": {
                "content": f"Message {i}",
                "task_id": f"stress-test-{i}"
            }
        }
        response = requests.post(
            f"{agent1_url}/messages/send",
            json=message
        )
        results.append(response.status_code == 200)

    # Verify success rate
    success_rate = sum(results) / len(results)
    assert success_rate > 0.95  # Allow for small failure rate
```

### 2. Multi-Agent System Testing

Create a larger system with multiple agents interacting:

```yaml
# docker-compose.multi-agent.yml
version: '3.8'

services:
  # Similar to original but with more agents
  agent1:
    # A2A agent

  agent2:
    # MCP agent

  agent3:
    # Hybrid A2A+MCP agent

  agent4:
    # Rule-based agent

  agent5:
    # LLM-based agent

  # ... more agents

  test-controller:
    # Test runner
```

### 3. Protocol Failover Testing

```python
def test_protocol_failover(setup_agents):
    """Test agent's ability to use alternative protocols when primary fails."""
    agent1_url, agent2_url = setup_agents

    # Agent with dual protocol support
    hybrid_agent_url = os.environ.get("HYBRID_AGENT_URL", "http://agent3:8080")

    # Disable primary protocol
    requests.post(f"{hybrid_agent_url}/protocols/a2a-http/disable")

    # Send message - should automatically use MCP
    message = {
        "target_agent_id": "agent1",
        "message": {"content": "Failover test"}
    }
    response = requests.post(
        f"{hybrid_agent_url}/messages/send",
        json=message
    )
    assert response.status_code == 200

    # Verify message was sent via MCP
    response = requests.get(f"{hybrid_agent_url}/protocols/active")
    active_protocols = response.json()
    assert active_protocols["last_used"] == "mcp-sse"
```

## Best Practices

1. **Isolation**: Each test should run in isolation
2. **Deterministic**: Tests should produce the same results each run
3. **Comprehensive**: Test all protocols and reasoning approaches
4. **Realistic**: Use realistic agent configurations
5. **Observability**: Include proper logging and monitoring
6. **Performance**: Include performance and stress tests
7. **Protocol Coverage**: Test all protocol features
8. **Edge Cases**: Test error handling and edge cases
9. **Compatibility**: Test cross-protocol communication
10. **Cleanup**: Ensure proper resource cleanup

## Implementation Plan

1. **Infrastructure Setup** (Week 1)
   - Create Docker configurations
   - Set up base test framework
   - Create mock services

2. **Basic Tests** (Week 2)
   - Implement basic protocol tests
   - Test agent lifecycle management
   - Basic communication tests

3. **Advanced Tests** (Week 3)
   - Multi-protocol testing
   - Reasoning approach testing
   - Error handling and failover testing

4. **Performance & Scale** (Week 4)
   - Stress testing
   - Multi-agent system testing
   - Large-scale performance testing

## Conclusion

This Docker-based approach for integration testing ensures that OpenMAS 0.3.0 can be thoroughly tested with real components, validating its reasoning-agnostic architecture and multi-protocol support. By running tests in isolated containers, we can create reproducible, realistic test scenarios that verify the system's behavior in production-like environments.

# CLI Workflow Diagrams

## Overview

This document provides workflow diagrams that visualize how OpenMAS CLI tools interact with different components in common usage scenarios. These workflows demonstrate the interoperability of CLI tools with other parts of the OpenMAS ecosystem.

## Development Workflows

### Agent Development Workflow

This workflow shows how CLI tools are used during agent development to scaffold, configure, test, and deploy agents:

```
┌───────────────────────────────────────────────────────────────────────┐
│                        Agent Development Workflow                     │
└───────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas scaffold │      │ openmas config  │      │ openmas agent     │
│ --type agent     │─────►│ validate        │─────►│ create            │
│ --name myagent   │      │ --file config.yml│      │ --from config.yml │
└──────────────────┘      └─────────────────┘      └─────────┬─────────┘
                                                              │
                                                              ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas deploy   │      │ openmas test    │      │ openmas agent     │
│ --agent myagent  │◄─────│ --agent myagent │◄─────│ start             │
│ --env production │      │ --suite basic   │      │ --id myagent      │
└──────────────────┘      └─────────────────┘      └───────────────────┘
```

**Description:**
1. `openmas scaffold` creates the initial agent structure
2. `openmas config validate` validates the agent configuration
3. `openmas agent create` creates the agent from the configuration
4. `openmas agent start` starts the agent for testing
5. `openmas test` runs test suites against the agent
6. `openmas deploy` deploys the agent to a production environment

### Protocol Development Workflow

This workflow shows how CLI tools are used during protocol adapter development:

```
┌───────────────────────────────────────────────────────────────────────┐
│                     Protocol Development Workflow                     │
└───────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas scaffold │      │ openmas config  │      │ openmas protocol  │
│ --type protocol  │─────►│ validate        │─────►│ register          │
│ --name myprotocol│      │ --file proto.yml│      │ --from proto.yml  │
└──────────────────┘      └─────────────────┘      └─────────┬─────────┘
                                                              │
                                                              ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas deploy   │      │ openmas test    │      │ openmas protocol  │
│ --protocol       │◄─────│ --protocol      │◄─────│ test              │
│ --env production │      │ --suite comms   │      │ --id myprotocol   │
└──────────────────┘      └─────────────────┘      └───────────────────┘
```

**Description:**
1. `openmas scaffold` creates the protocol adapter structure
2. `openmas config validate` validates the protocol configuration
3. `openmas protocol register` registers the protocol with the system
4. `openmas protocol test` tests the protocol adapter
5. `openmas test` runs integration tests for the protocol
6. `openmas deploy` deploys the protocol adapter

## Deployment Workflows

### Local Deployment Workflow

This workflow demonstrates using CLI tools for local deployment of a multi-agent system:

```
┌───────────────────────────────────────────────────────────────────────┐
│                       Local Deployment Workflow                       │
└───────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas config   │      │ openmas agent   │      │ openmas agent     │
│ generate --local │─────►│ create --all    │─────►│ start --all       │
│ --output local.yml│     │ --from local.yml│      │                   │
└──────────────────┘      └─────────────────┘      └─────────┬─────────┘
                                                              │
                                                              ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas agent    │      │ openmas monitor │      │ openmas supervisor│
│ status           │◄─────│ --local         │◄─────│ start             │
│ --all            │      │ --dashboard     │      │ --config local.yml│
└──────────────────┘      └─────────────────┘      └───────────────────┘
```

**Description:**
1. `openmas config generate` creates a local deployment configuration
2. `openmas agent create --all` creates all agents defined in the configuration
3. `openmas agent start --all` starts all the created agents
4. `openmas supervisor start` starts the agent supervisor for managing agents
5. `openmas monitor` launches monitoring dashboard
6. `openmas agent status` checks the status of all agents

### Container Deployment Workflow

This workflow demonstrates using CLI tools for containerized deployment:

```
┌───────────────────────────────────────────────────────────────────────┐
│                     Container Deployment Workflow                     │
└───────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas config   │      │ openmas deploy  │      │ openmas deploy    │
│ generate --docker│─────►│ build           │─────►│ up                │
│ --output docker.yml     │ --from docker.yml      │ --from docker.yml │
└──────────────────┘      └─────────────────┘      └─────────┬─────────┘
                                                              │
                                                              ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas deploy   │      │ openmas deploy  │      │ openmas monitor   │
│ logs             │◄─────│ status          │◄─────│ --remote          │
│ --follow         │      │ --all           │      │ --dashboard       │
└──────────────────┘      └─────────────────┘      └───────────────────┘
```

**Description:**
1. `openmas config generate --docker` creates a Docker deployment configuration
2. `openmas deploy build` builds the Docker images
3. `openmas deploy up` starts the Docker containers
4. `openmas monitor --remote` launches remote monitoring dashboard
5. `openmas deploy status` checks deployment status
6. `openmas deploy logs` monitors deployment logs

### Cloud Deployment Workflow

This workflow demonstrates using CLI tools for cloud deployment:

```
┌───────────────────────────────────────────────────────────────────────┐
│                       Cloud Deployment Workflow                       │
└───────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas config   │      │ openmas cloud   │      │ openmas deploy    │
│ generate --cloud │─────►│ init            │─────►│ apply             │
│ --output cloud.yml      │ --provider aws  │      │ --from cloud.yml  │
└──────────────────┘      └─────────────────┘      └─────────┬─────────┘
                                                              │
                                                              ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas deploy   │      │ openmas deploy  │      │ openmas cloud     │
│ logs --cloud     │◄─────│ status --cloud  │◄─────│ dashboard         │
│ --follow         │      │ --all           │      │ --provider aws    │
└──────────────────┘      └─────────────────┘      └───────────────────┘
```

**Description:**
1. `openmas config generate --cloud` creates a cloud deployment configuration
2. `openmas cloud init` initializes cloud provider
3. `openmas deploy apply` deploys to cloud
4. `openmas cloud dashboard` opens cloud provider dashboard
5. `openmas deploy status --cloud` checks cloud deployment status
6. `openmas deploy logs --cloud` monitors cloud deployment logs

## Testing Workflows

### Integration Testing Workflow

This workflow demonstrates using CLI tools for integration testing:

```
┌───────────────────────────────────────────────────────────────────────┐
│                     Integration Testing Workflow                      │
└───────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas test     │      │ openmas test    │      │ openmas test      │
│ setup            │─────►│ supervisor start│─────►│ suite run         │
│ --integration    │      │                 │      │ --integration     │
└──────────────────┘      └─────────────────┘      └─────────┬─────────┘
                                                              │
                                                              ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas test     │      │ openmas test    │      │ openmas test      │
│ report           │◄─────│ analyze         │◄─────│ supervisor stop   │
│ --format html    │      │ --coverage      │      │                   │
└──────────────────┘      └─────────────────┘      └───────────────────┘
```

**Description:**
1. `openmas test setup` prepares the integration test environment
2. `openmas test supervisor start` starts the test supervisor
3. `openmas test suite run` runs integration test suites
4. `openmas test supervisor stop` stops the test supervisor
5. `openmas test analyze` analyzes test results and coverage
6. `openmas test report` generates test reports

### Multi-Agent Testing Workflow

This workflow demonstrates using CLI tools for multi-agent testing:

```
┌───────────────────────────────────────────────────────────────────────┐
│                     Multi-Agent Testing Workflow                      │
└───────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas test     │      │ openmas agent   │      │ openmas test      │
│ scenario create  │─────►│ create --test   │─────►│ harness start     │
│ --multi-agent    │      │ --count 5       │      │ --scenario test1  │
└──────────────────┘      └─────────────────┘      └─────────┬─────────┘
                                                              │
                                                              ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas test     │      │ openmas test    │      │ openmas test      │
│ replay           │◄─────│ analyze         │◄─────│ harness stop      │
│ --recording test1│      │ --interactions  │      │ --scenario test1  │
└──────────────────┘      └─────────────────┘      └───────────────────┘
```

**Description:**
1. `openmas test scenario create` creates a multi-agent test scenario
2. `openmas agent create --test` creates test agents
3. `openmas test harness start` starts the test harness with the scenario
4. `openmas test harness stop` stops the test harness
5. `openmas test analyze` analyzes agent interactions
6. `openmas test replay` replays recorded test interactions

## Security Workflows

### Security Configuration Workflow

This workflow demonstrates using CLI tools for security configuration:

```
┌───────────────────────────────────────────────────────────────────────┐
│                    Security Configuration Workflow                    │
└───────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas security │      │ openmas security│      │ openmas security  │
│ init             │─────►│ keys generate   │─────►│ config create     │
│                  │      │ --type jwt      │      │ --auth jwt        │
└──────────────────┘      └─────────────────┘      └─────────┬─────────┘
                                                              │
                                                              ▼
┌──────────────────┐      ┌─────────────────┐      ┌───────────────────┐
│ openmas security │      │ openmas deploy  │      │ openmas security  │
│ audit            │◄─────│ --security      │◄─────│ config apply      │
│ --full           │      │ --env production│      │ --env production  │
└──────────────────┘      └─────────────────┘      └───────────────────┘
```

**Description:**
1. `openmas security init` initializes security infrastructure
2. `openmas security keys generate` generates security keys
3. `openmas security config create` creates security configuration
4. `openmas security config apply` applies security configuration
5. `openmas deploy --security` deploys with security configuration
6. `openmas security audit` audits security configuration

## Related Documentation

- [CLI Component Interoperability](./component_interoperability.md)
- [CLI Commands](../commands/README.md)
- [Testing Framework](../../16_testing/framework/README.md)
- [Deployment Documentation](../../15_deployment/README.md)
- [Security Configuration](../../17_security/architecture/README.md)

# Deployment Variables

This document provides a comprehensive reference for environment variables and configuration parameters used in OpenMAS deployments.

## Overview

OpenMAS deployments use a combination of environment variables and configuration files to manage deployment-specific settings. These variables allow for flexible deployments across different environments while maintaining OpenMAS's reasoning-agnostic architecture and multi-protocol support.

## Environment Variables

Environment variables provide a way to configure deployments without modifying configuration files, which is particularly useful for:

- Sensitive information (API keys, credentials)
- Environment-specific values (hostnames, ports)
- Runtime configuration (resource limits, feature flags)

### Core Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENMAS_ENV` | Deployment environment | `development` | `production` |
| `OPENMAS_LOG_LEVEL` | Logging level | `info` | `debug` |
| `OPENMAS_CONFIG_PATH` | Path to configuration file | `./config.yaml` | `/etc/openmas/config.yaml` |
| `OPENMAS_PORT` | Default port for agents | `8080` | `9000` |
| `OPENMAS_HOST` | Default host binding | `0.0.0.0` | `127.0.0.1` |

### Protocol-Specific Variables

#### A2A Protocol Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENMAS_A2A_ENDPOINT` | A2A protocol endpoint | `http://localhost:8000` | `https://a2a.example.com` |
| `OPENMAS_A2A_API_KEY` | A2A protocol API key | - | `sk_a2a_12345` |
| `OPENMAS_A2A_TIMEOUT` | A2A protocol timeout (seconds) | `30` | `60` |

#### MCP Protocol Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENMAS_MCP_ENDPOINT` | MCP protocol endpoint | `http://localhost:8080` | `https://mcp.example.com` |
| `OPENMAS_MCP_API_KEY` | MCP protocol API key | - | `sk_mcp_12345` |
| `OPENMAS_MCP_SERVER_MODE` | MCP server mode | `server` | `client` |

#### HTTP Protocol Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENMAS_HTTP_TIMEOUT` | HTTP request timeout (seconds) | `30` | `60` |
| `OPENMAS_HTTP_MAX_RETRIES` | Maximum HTTP retry attempts | `3` | `5` |

### Reasoning-Specific Variables

Variables for different reasoning approaches maintain the reasoning-agnostic architecture:

#### LLM Reasoning Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENMAS_LLM_PROVIDER` | LLM provider | `openai` | `anthropic` |
| `OPENMAS_LLM_MODEL` | LLM model | `gpt-4` | `claude-3-opus-20240229` |
| `OPENMAS_OPENAI_API_KEY` | OpenAI API key | - | `sk-...` |
| `OPENMAS_ANTHROPIC_API_KEY` | Anthropic API key | - | `sk-ant-...` |

#### Rule-Based Reasoning Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENMAS_RULES_PATH` | Path to rule definitions | `./rules` | `/etc/openmas/rules` |
| `OPENMAS_RULES_REFRESH_INTERVAL` | Rule refresh interval (seconds) | `300` | `60` |

#### BDI Reasoning Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENMAS_BDI_BELIEFS_PATH` | Path to belief definitions | `./beliefs` | `/etc/openmas/beliefs` |
| `OPENMAS_BDI_PLANS_PATH` | Path to plan definitions | `./plans` | `/etc/openmas/plans` |
| `OPENMAS_BDI_INTENTIONS_PATH` | Path to intention definitions | `./intentions` | `/etc/openmas/intentions` |

### Deployment-Specific Variables

#### Local Deployment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENMAS_LOCAL_AGENTS_PATH` | Path to local agent definitions | `./agents` | `/path/to/agents` |
| `OPENMAS_LOCAL_SUPERVISOR_PORT` | Agent supervisor port | `8081` | `9001` |

#### Container Deployment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENMAS_CONTAINER_REGISTRY` | Container registry for images | `docker.io/openmas` | `gcr.io/myproject` |
| `OPENMAS_CONTAINER_TAG` | Container image tag | `latest` | `v0.3.0` |
| `OPENMAS_CONTAINER_PULL_POLICY` | Image pull policy | `IfNotPresent` | `Always` |

#### Kubernetes Deployment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENMAS_K8S_NAMESPACE` | Kubernetes namespace | `default` | `openmas` |
| `OPENMAS_K8S_SERVICE_ACCOUNT` | Kubernetes service account | `default` | `openmas-sa` |
| `OPENMAS_K8S_RESOURCE_CPU` | CPU resource allocation | `0.5` | `1.0` |
| `OPENMAS_K8S_RESOURCE_MEMORY` | Memory resource allocation | `512Mi` | `1Gi` |

#### Cloud Deployment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `OPENMAS_CLOUD_PROVIDER` | Cloud provider | `aws` | `gcp` |
| `OPENMAS_CLOUD_REGION` | Cloud region | `us-west-2` | `us-central1` |
| `OPENMAS_CLOUD_PROJECT` | Cloud project identifier | - | `my-project-id` |

## Configuration File Variables

In addition to environment variables, OpenMAS deployments can be configured through deployment-specific configuration files. These files extend the unified configuration schema with deployment parameters.

### Deployment Configuration Structure

```yaml
version: "1"

deployment:
  environment: docker

  resources:
    default:
      cpu: 0.5
      memory: 512Mi

  networking:
    ports:
      - name: api
        port: 8080
        target: agent1

  storage:
    volumes:
      - name: data
        size: 1Gi
        path: /data

  observability:
    logging:
      level: info
      format: json
    metrics:
      enabled: true
      port: 9090
    tracing:
      enabled: true

  components:
    agent1:
      type: agent
      config: config/agent1_config.yaml
      replicas: 1
      resources:
        cpu: 0.5
        memory: 512Mi

    agent2:
      type: agent
      config: config/agent2_config.yaml
      replicas: 1
      resources:
        cpu: 0.5
        memory: 512Mi
```

## Variable Precedence

When multiple sources define the same variable, OpenMAS follows this precedence order (highest to lowest):

1. Command-line arguments
2. Environment variables
3. Deployment-specific configuration file
4. Project-specific configuration file
5. Global configuration file
6. Default values

## Variable Templating

OpenMAS supports variable templating in configuration files to reference other variables:

```yaml
deployment:
  environment: ${OPENMAS_ENV:development}

  components:
    agent1:
      config: config/${OPENMAS_ENV:development}/agent1_config.yaml
```

## Environment-Specific Configuration

Create environment-specific deployments using profiles:

```yaml
deployment:
  profiles:
    development:
      resources:
        default:
          cpu: 0.25
          memory: 256Mi

    production:
      resources:
        default:
          cpu: 1.0
          memory: 1Gi
      replicas: 3
```

Apply profiles with:

```bash
openmas deploy up --profile production
```

## Best Practices

1. **Use Environment Variables for Secrets**: Never store API keys or credentials in configuration files
2. **Define Defaults**: Provide sensible defaults for all configuration parameters
3. **Document Variables**: Clearly document custom variables and their purpose
4. **Use Profiles**: Create environment-specific profiles for different deployment targets
5. **Validate Configurations**: Use `openmas validate config` to validate configurations
6. **Version Control**: Store non-sensitive configuration in version control
7. **Parameter Grouping**: Group related parameters together for better organization
8. **Minimize Redundancy**: Use variable references to avoid duplication

## See Also

- [Deployment Overview](../README.md)
- [Local Deployment](../local/README.md)
- [Containerization](../containerization/README.md)
- [Kubernetes Deployment](../kubernetes/README.md)
- [Cloud Deployment](../cloud/README.md)
- [Deploy Command](../../13_cli_tools/commands/deploy.md)

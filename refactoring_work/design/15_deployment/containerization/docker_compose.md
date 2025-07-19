# Docker Compose Deployment

## Overview

This document provides guidance for deploying OpenMAS multi-agent systems using Docker Compose. Docker Compose simplifies the deployment of multiple interconnected containers, making it ideal for multi-agent systems with complex dependencies.

## Prerequisites

- Docker Engine (20.10.0+)
- Docker Compose (2.0.0+)
- OpenMAS configuration files

## Basic Docker Compose Setup

### Directory Structure

A typical OpenMAS Docker Compose project follows this structure:

```
openmas-compose/
├── docker-compose.yml           # Main Docker Compose configuration
├── .env                         # Environment variables
├── configs/                     # Configuration files
│   ├── system.yaml              # System configuration
│   ├── agents/                  # Agent configurations
│   │   ├── agent1.yaml
│   │   └── agent2.yaml
│   └── protocols/               # Protocol configurations
│       ├── mcp_config.yaml
│       └── a2a_config.yaml
├── data/                        # Persistent data
│   └── .gitkeep
└── logs/                        # Log files
    └── .gitkeep
```

### Docker Compose File

A basic `docker-compose.yml` for a two-agent system:

```yaml
version: '3.8'

services:
  # Agent 1: Assistant Agent
  assistant-agent:
    image: openmas/agent:0.3.0
    container_name: assistant-agent
    environment:
      - OPENMAS_CONFIG=/app/configs/agents/assistant_agent.yaml
      - OPENMAS_LOG_LEVEL=INFO
      - OPENMAS_PROTOCOL_HOST=0.0.0.0
      - OPENMAS_PROTOCOL_PORT=8080
    volumes:
      - ./configs:/app/configs
      - ./data/assistant:/app/data
      - ./logs/assistant:/app/logs
    ports:
      - "8080:8080"
    networks:
      - openmas-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  # Agent 2: User Agent
  user-agent:
    image: openmas/agent:0.3.0
    container_name: user-agent
    environment:
      - OPENMAS_CONFIG=/app/configs/agents/user_agent.yaml
      - OPENMAS_LOG_LEVEL=INFO
      - OPENMAS_PROTOCOL_HOST=0.0.0.0
      - OPENMAS_PROTOCOL_PORT=8081
    volumes:
      - ./configs:/app/configs
      - ./data/user:/app/data
      - ./logs/user:/app/logs
    ports:
      - "8081:8081"
    networks:
      - openmas-network
    restart: unless-stopped
    depends_on:
      - assistant-agent
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  # Observability: Prometheus
  prometheus:
    image: prom/prometheus:v2.37.0
    container_name: prometheus
    volumes:
      - ./configs/prometheus:/etc/prometheus
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - openmas-network
    restart: unless-stopped

  # Observability: Grafana
  grafana:
    image: grafana/grafana:9.0.0
    container_name: grafana
    volumes:
      - ./configs/grafana:/etc/grafana/provisioning
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - openmas-network
    restart: unless-stopped
    depends_on:
      - prometheus

networks:
  openmas-network:
    driver: bridge

volumes:
  prometheus-data:
  grafana-data:
```

## Environment Variables

Use a `.env` file to configure environment variables:

```
# OpenMAS Version
OPENMAS_VERSION=0.3.0

# Protocol Configuration
OPENMAS_PROTOCOL=mcp
OPENMAS_TRANSPORT=http

# Resource Limits
OPENMAS_MEMORY_LIMIT=500m
OPENMAS_CPU_LIMIT=0.5

# Security
OPENMAS_API_KEY=your-secret-api-key
```

## Deployment Patterns

### 1. Single Agent Per Container

The standard approach where each agent runs in its own container:

```yaml
services:
  agent1:
    image: openmas/agent:0.3.0
    # configuration for agent1
    
  agent2:
    image: openmas/agent:0.3.0
    # configuration for agent2
    
  agent3:
    image: openmas/agent:0.3.0
    # configuration for agent3
```

### 2. Multi-Agent Supervisor

A supervisor container manages multiple agents:

```yaml
services:
  supervisor:
    image: openmas/supervisor:0.3.0
    volumes:
      - ./configs:/app/configs
    ports:
      - "8000:8000"
    environment:
      - OPENMAS_CONFIG=/app/configs/supervisor.yaml
```

### 3. Microservices Architecture

Each component runs as a separate service:

```yaml
services:
  # Agent services
  agent-service:
    image: openmas/agent-service:0.3.0
    # configuration
    
  # Protocol services
  protocol-service:
    image: openmas/protocol-service:0.3.0
    # configuration
    
  # Knowledge services
  knowledge-service:
    image: openmas/knowledge-service:0.3.0
    # configuration
    
  # Database services
  database:
    image: postgres:14
    # configuration
```

## Resource Management

Configure container resource limits:

```yaml
services:
  agent1:
    image: openmas/agent:0.3.0
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 500M
        reservations:
          cpus: '0.1'
          memory: 100M
```

## Persistent Data

Configure volumes for persistent data:

```yaml
services:
  agent1:
    image: openmas/agent:0.3.0
    volumes:
      - agent1-data:/app/data
      
volumes:
  agent1-data:
    driver: local
```

## Networking

Configure container networking:

```yaml
services:
  agent1:
    image: openmas/agent:0.3.0
    networks:
      - frontend-network
      - backend-network
      
  agent2:
    image: openmas/agent:0.3.0
    networks:
      - backend-network
      
networks:
  frontend-network:
    driver: bridge
  backend-network:
    driver: bridge
```

## Health Checks

Configure health checks:

```yaml
services:
  agent1:
    image: openmas/agent:0.3.0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

## Scaling

Scale services with Docker Compose:

```yaml
services:
  worker-agent:
    image: openmas/worker-agent:0.3.0
    deploy:
      mode: replicated
      replicas: 3
```

## Docker Compose Commands

Common Docker Compose commands for OpenMAS:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View logs for a specific service
docker-compose logs -f assistant-agent

# Stop all services
docker-compose down

# Restart a specific service
docker-compose restart assistant-agent

# Scale a service
docker-compose up -d --scale worker-agent=5

# View container status
docker-compose ps
```

## Best Practices

1. **Configuration Management**: Store configurations outside containers
2. **Environment Variables**: Use environment variables for deployment-specific settings
3. **Resource Limits**: Always set memory and CPU limits
4. **Health Checks**: Implement health checks for all services
5. **Persistent Volumes**: Use volumes for persistent data
6. **Security**: Never hardcode sensitive information
7. **Observability**: Include monitoring and logging services
8. **Container Optimization**: Use multi-stage builds for smaller images
9. **Docker Compose Versioning**: Use docker-compose.override.yml for environment-specific settings

## Related Documentation

- [Testing Containers](./testing_containers.md)
- [Development Containers](./development_containers.md)
- [Kubernetes Deployment](../kubernetes/README.md)
- [Docker Integration Testing](../../16_testing/integration_testing/docker_integration.md)

# Azure Deployment

This document provides guidance on deploying OpenMAS agents and systems on Microsoft Azure.

## Overview

Microsoft Azure offers a range of services that align well with OpenMAS's reasoning-agnostic architecture and multi-protocol support. This guide covers deployment options, architecture patterns, and best practices for Azure deployments.

## Deployment Options

### 1. Azure Functions (Serverless)

**Best for**: Event-driven agents, low to moderate traffic, cost-sensitive deployments
- Deploy agent communication layer as serverless functions
- Trigger agents via HTTP endpoints, Event Grid, or Service Bus
- Store state in Cosmos DB or Azure SQL
- Integrate with Azure AI services or custom reasoning services

```json
// Example host.json for OpenMAS Azure Functions
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    }
  },
  "extensions": {
    "http": {
      "routePrefix": "api",
      "maxOutstandingRequests": 200,
      "maxConcurrentRequests": 100
    }
  },
  "functionTimeout": "00:10:00"
}
```

```python
# Example function.json for an agent endpoint
{
  "bindings": [
    {
      "authLevel": "function",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["post"],
      "route": "agent/{agent_id}"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
```

### 2. Azure Container Apps / Azure Container Instances

**Best for**: Continuous operation, moderate traffic, balanced cost/performance
- Deploy agents as containerized services on Azure Container Apps
- Use API Management for traffic routing
- Store state in Cosmos DB, Azure SQL, or Redis Cache
- Scale with KEDA-powered autoscaling

```yaml
# Example container app YAML
name: openmas-agent
resourceGroup: openmas-resources
location: westus
properties:
  managedEnvironmentId: /subscriptions/.../managedEnvironments/openmas-env
  configuration:
    ingress:
      external: true
      targetPort: 8080
    secrets:
      - name: openai-api-key
        value: "sk-..."
  template:
    containers:
      - name: agent
        image: myregistry.azurecr.io/openmas:latest
        resources:
          cpu: 1.0
          memory: 2Gi
        env:
          - name: OPENMAS_ENV
            value: production
          - name: OPENMAS_PROTOCOL
            value: a2a
          - name: OPENAI_API_KEY
            secretRef: openai-api-key
    scale:
      minReplicas: 1
      maxReplicas: 10
      rules:
        - name: http-rule
          http:
            metadata:
              concurrentRequests: "20"
```

### 3. AKS (Kubernetes)

**Best for**: Complex multi-agent systems, high traffic, advanced orchestration needs
- Deploy on Azure Kubernetes Service with Kubernetes orchestration
- Scale horizontally with Kubernetes HPA
- Use Azure Disk/File Storage for persistent storage
- Leverage service mesh (like Istio or Linkerd) for inter-agent communication

For detailed AKS deployment, see [Kubernetes Deployment](../kubernetes/README.md).

## Azure Deployment Architecture

### Reference Architecture 1: Serverless Multi-Agent System

![Azure Serverless Architecture](https://via.placeholder.com/800x500?text=Azure+Serverless+OpenMAS+Architecture)

Components:
1. **API Management**: API gateway for external systems
2. **Azure Functions**: Individual agent communication handlers
3. **Event Grid**: Event bus for inter-agent communication
4. **Cosmos DB**: State storage and knowledge base
5. **Azure AD B2C**: Authentication and authorization
6. **Application Insights**: Monitoring and logging
7. **Blob Storage**: Configuration and asset storage
8. **Service Bus**: Asynchronous messaging between agents

### Reference Architecture 2: Container-Based Multi-Agent System

![Azure Container Architecture](https://via.placeholder.com/800x500?text=Azure+Container+OpenMAS+Architecture)

Components:
1. **Azure Container Apps**: Container orchestration for agents
2. **API Management**: Traffic distribution and routing
3. **Azure SQL/Cosmos DB**: Database for state
4. **Redis Cache**: In-memory caching for performance
5. **Container Registry**: Registry for agent images
6. **Azure Monitor**: Monitoring and logging
7. **Key Vault**: Secret management
8. **Application Insights**: Distributed tracing

## Maintaining Reasoning Agnosticism

Azure deployments maintain OpenMAS's reasoning-agnostic architecture through:

1. **Communication Layer ("Body")**: 
   - Deployed as Azure Functions or containers
   - Handles protocol-specific messaging (A2A, MCP, HTTP, etc.)
   - Manages service discovery and routing

2. **Reasoning Engines ("Brain")**:
   - LLM-based: Integrated with Azure OpenAI Service or third-party APIs
   - Rule-based: Embedded in agent containers or separate services
   - BDI: Implemented as dedicated services with state management
   - Hybrid: Orchestrated through event-driven architecture

## Protocol Support

Azure deployments support multiple communication protocols:

1. **A2A Protocol**:
   - API Management + Azure Functions for request/response
   - Service Bus for asynchronous messaging
   - Event Grid for event-driven patterns

2. **MCP Protocol**:
   - API Management with WebSockets
   - Azure Functions or Container Apps for server implementation
   - Azure SignalR Service for real-time communication

3. **HTTP/MQTT/gRPC**:
   - API Management for HTTP
   - IoT Hub for MQTT
   - Container Apps with Envoy for gRPC

## Deployment Process

### Prerequisites
- Azure CLI installed and configured
- Docker for container builds
- Terraform or Azure Resource Manager templates (optional)
- OpenMAS CLI installed

### Deployment Steps

#### 1. Configure Azure Authentication
```bash
az login
az account set --subscription <subscription-id>
```

#### 2. Initialize Deployment Configuration
```bash
openmas deploy init --environment azure
```

#### 3. Configure Deployment Variables
Edit the generated `deployment/azure.yaml` file:
```yaml
environment: azure
location: westus2
resource_group: openmas-resources

components:
  agent1:
    type: agent
    config: config/agent1_config.yaml
    deployment:
      type: function
      memory: 512
      timeout: 300
  
  agent2:
    type: agent
    config: config/agent2_config.yaml
    deployment:
      type: container_app
      cpu: 0.5
      memory: 1024
```

#### 4. Build Deployment Artifacts
```bash
openmas deploy build --file deployment/azure.yaml
```

#### 5. Deploy to Azure
```bash
openmas deploy up --file deployment/azure.yaml
```

## Observability

Azure provides comprehensive observability solutions for OpenMAS:

1. **Logging**:
   - Azure Monitor Logs for centralized log collection
   - Log Analytics for log analysis
   - Configure log levels through environment variables

2. **Metrics**:
   - Azure Monitor Metrics for performance monitoring
   - Custom metrics for agent-specific measurements
   - Dashboards for visualization

3. **Tracing**:
   - Application Insights for distributed tracing
   - Trace agent interactions and dependencies
   - Analyze performance bottlenecks

4. **Alerting**:
   - Azure Monitor Alerts for threshold-based alerts
   - Event Grid for event-based notifications
   - Action Groups for notification delivery

## Security Best Practices

1. **Role-Based Access Control (RBAC)**:
   - Use least privilege principle
   - Create custom roles for different agent types
   - Use managed identities for service-to-service authentication

2. **Secret Management**:
   - Store secrets in Azure Key Vault
   - Use managed identities for key vault access
   - Rotate credentials regularly

3. **Network Security**:
   - Use Virtual Networks for network isolation
   - Implement Network Security Groups for access control
   - Enable Private Endpoints for Azure services

4. **Data Protection**:
   - Encrypt data at rest (Blob Storage, Cosmos DB, SQL)
   - Encrypt data in transit (HTTPS, TLS)
   - Implement data access controls

## Cost Optimization

1. **Right-sizing**:
   - Match resources to workload requirements
   - Use autoscaling to adjust capacity
   - Implement scheduled scaling for predictable patterns

2. **Serverless for Variable Workloads**:
   - Use Azure Functions for sporadic workloads
   - Leverage Consumption Plan for pay-per-use
   - Premium Plan for more predictable workloads

3. **Reserved Capacity**:
   - Use Reserved Instances for stable workloads
   - Consider Spot Instances for fault-tolerant components
   - Implement lifecycle management for ephemeral resources

## Azure OpenAI Service Integration

OpenMAS can leverage Azure OpenAI Service for LLM-based reasoning:

```yaml
# Example Azure OpenAI configuration in OpenMAS
reasoning:
  llm:
    provider: azure
    model: gpt-4
    endpoint: https://myopenai.openai.azure.com/
    api_version: 2023-05-15
    deployment_name: my-gpt4-deployment
```

Implementation in agent code:
```python
from openmas.reasoning.llm.azure import AzureOpenAIReasoning

# Configure Azure OpenAI reasoning engine
reasoning_engine = AzureOpenAIReasoning(
    endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
    api_version="2023-05-15"
)

# Use reasoning engine while maintaining separation from communication layer
agent = OpenMASAgent(
    communication=A2ACommunicator(...),  # Communication "body"
    reasoning=reasoning_engine            # Reasoning "brain"
)
```

## See Also

- [Deployment Configuration](../configuration/README.md)
- [Kubernetes Deployment](../kubernetes/README.md)
- [Deploy Command](../../13_cli_tools/commands/deploy.md)

# Google Cloud Platform Deployment

This document provides guidance on deploying OpenMAS agents and systems on Google Cloud Platform (GCP).

## Overview

Google Cloud Platform offers various services that align with OpenMAS's reasoning-agnostic architecture and multi-protocol support. This guide covers deployment options, architecture patterns, and best practices for GCP deployments.

## Deployment Options

### 1. Cloud Functions / Cloud Run Functions (Serverless)

**Best for**: Event-driven agents, low to moderate traffic, cost-sensitive deployments
- Deploy agent communication layer as serverless functions
- Trigger agents via HTTP, Cloud Pub/Sub, or Cloud Events
- Store state in Firestore, Cloud SQL, or Datastore
- Integrate with Vertex AI or third-party APIs for reasoning

```yaml
# Example cloudbuild.yaml for Cloud Functions deployment
steps:
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  args:
  - gcloud
  - functions
  - deploy
  - openmas-agent
  - --runtime=python310
  - --trigger-http
  - --entry-point=handle_agent_request
  - --memory=512MB
  - --timeout=540s
  - --set-env-vars=OPENMAS_ENV=production,OPENMAS_PROTOCOL=a2a
```

```python
# Example Cloud Functions implementation
import functions_framework
from openmas.agent import Agent
from openmas.protocol.a2a import A2ACommunicator

@functions_framework.http
def handle_agent_request(request):
    # Create agent with reasoning-agnostic architecture
    agent = Agent(
        communicator=A2ACommunicator(),
        reasoning=get_reasoning_engine()  # Implementation-specific
    )
    
    # Process request
    result = agent.process_request(request.json)
    
    # Return response
    return result
```

### 2. Cloud Run (Containers)

**Best for**: Continuous operation, moderate traffic, balanced cost/performance
- Deploy agents as containerized services on Cloud Run
- Use API Gateway or Cloud Endpoints for traffic routing
- Store state in Firestore, Cloud SQL, or Memorystore
- Scale automatically with Cloud Run's auto-scaling

```yaml
# Example service.yaml for Cloud Run
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: openmas-agent
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containers:
      - image: gcr.io/my-project/openmas:latest
        ports:
        - containerPort: 8080
        env:
        - name: OPENMAS_ENV
          value: "production"
        - name: OPENMAS_PROTOCOL
          value: "a2a"
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
```

### 3. GKE (Kubernetes)

**Best for**: Complex multi-agent systems, high traffic, advanced orchestration needs
- Deploy on Google Kubernetes Engine with Kubernetes orchestration
- Scale horizontally with Kubernetes HPA
- Use Persistent Disks or Filestore for persistent storage
- Leverage service mesh (like Istio or Cloud Service Mesh) for inter-agent communication

For detailed GKE deployment, see [Kubernetes Deployment](../kubernetes/README.md).

## GCP Deployment Architecture

### Reference Architecture 1: Serverless Multi-Agent System

![GCP Serverless Architecture](https://via.placeholder.com/800x500?text=GCP+Serverless+OpenMAS+Architecture)

Components:
1. **API Gateway**: API endpoint for external systems
2. **Cloud Functions/Cloud Run Functions**: Individual agent communication handlers
3. **Eventarc/Cloud Pub/Sub**: Event bus for inter-agent communication
4. **Firestore/Datastore**: State storage and knowledge base
5. **Identity Platform**: Authentication and authorization
6. **Cloud Logging/Monitoring**: Monitoring and logging
7. **Cloud Storage**: Configuration and asset storage
8. **Cloud Pub/Sub**: Asynchronous messaging between agents

### Reference Architecture 2: Container-Based Multi-Agent System

![GCP Container Architecture](https://via.placeholder.com/800x500?text=GCP+Container+OpenMAS+Architecture)

Components:
1. **Cloud Run**: Container orchestration for agents
2. **API Gateway**: Traffic distribution and routing
3. **Cloud SQL/Firestore**: Database for state
4. **Memorystore**: In-memory caching for performance
5. **Container Registry**: Registry for agent images
6. **Cloud Monitoring**: Monitoring and logging
7. **Secret Manager**: Secret management
8. **Cloud Trace**: Distributed tracing

## Maintaining Reasoning Agnosticism

GCP deployments maintain OpenMAS's reasoning-agnostic architecture through:

1. **Communication Layer ("Body")**: 
   - Deployed as Cloud Functions or Cloud Run services
   - Handles protocol-specific messaging (A2A, MCP, HTTP, etc.)
   - Manages service discovery and routing

2. **Reasoning Engines ("Brain")**:
   - LLM-based: Integrated with Vertex AI or third-party APIs
   - Rule-based: Embedded in agent containers or separate services
   - BDI: Implemented as dedicated services with state management
   - Hybrid: Orchestrated through event-driven architecture

## Protocol Support

GCP deployments support multiple communication protocols:

1. **A2A Protocol**:
   - API Gateway + Cloud Functions/Run for request/response
   - Cloud Pub/Sub for asynchronous messaging
   - Eventarc for event-driven patterns

2. **MCP Protocol**:
   - WebSockets through Cloud Run
   - Custom server implementation on Cloud Run
   - Firebase Realtime Database for real-time communication

3. **HTTP/MQTT/gRPC**:
   - API Gateway for HTTP
   - IoT Core for MQTT
   - Cloud Run with proxy for gRPC

## Deployment Process

### Prerequisites
- Google Cloud SDK installed and configured
- Docker for container builds
- Terraform or Deployment Manager templates (optional)
- OpenMAS CLI installed

### Deployment Steps

#### 1. Configure GCP Authentication
```bash
gcloud auth login
gcloud config set project <project-id>
```

#### 2. Initialize Deployment Configuration
```bash
openmas deploy init --environment gcp
```

#### 3. Configure Deployment Variables
Edit the generated `deployment/gcp.yaml` file:
```yaml
environment: gcp
project: my-openmas-project
region: us-central1

components:
  agent1:
    type: agent
    config: config/agent1_config.yaml
    deployment:
      type: cloud_function
      memory: 512
      timeout: 540
  
  agent2:
    type: agent
    config: config/agent2_config.yaml
    deployment:
      type: cloud_run
      cpu: 1
      memory: 512
      min_instances: 1
```

#### 4. Build Deployment Artifacts
```bash
openmas deploy build --file deployment/gcp.yaml
```

#### 5. Deploy to GCP
```bash
openmas deploy up --file deployment/gcp.yaml
```

## Observability

GCP provides comprehensive observability solutions for OpenMAS:

1. **Logging**:
   - Cloud Logging for centralized log collection
   - Log Explorer for log analysis
   - Configure log levels through environment variables

2. **Metrics**:
   - Cloud Monitoring for performance monitoring
   - Custom metrics for agent-specific measurements
   - Monitoring dashboards for visualization

3. **Tracing**:
   - Cloud Trace for distributed tracing
   - Trace agent interactions and dependencies
   - Analyze performance bottlenecks

4. **Alerting**:
   - Cloud Monitoring Alerts for threshold-based alerts
   - Alerting policies for notification settings
   - Notification channels for alert delivery

## Security Best Practices

1. **IAM and Service Accounts**:
   - Use least privilege principle
   - Create separate service accounts for different agent types
   - Use workload identity for GKE

2. **Secret Management**:
   - Store secrets in Secret Manager
   - Use environment variables for configuration
   - Rotate credentials regularly

3. **Network Security**:
   - Use VPC for network isolation
   - Implement firewall rules for access control
   - Enable Private Service Connect for Google APIs

4. **Data Protection**:
   - Encrypt data at rest (Cloud Storage, Firestore, Cloud SQL)
   - Encrypt data in transit (HTTPS, TLS)
   - Implement data access controls

## Cost Optimization

1. **Right-sizing**:
   - Match resources to workload requirements
   - Use auto-scaling to adjust capacity
   - Implement scheduled scaling for predictable patterns

2. **Serverless for Variable Workloads**:
   - Use Cloud Functions for sporadic workloads
   - Leverage Cloud Run for containerized applications
   - Implement tiered storage strategies

3. **Committed Use Discounts**:
   - Use committed use discounts for stable workloads
   - Consider Spot VMs for fault-tolerant components
   - Implement lifecycle policies for ephemeral resources

## Vertex AI Integration

OpenMAS can leverage Vertex AI for LLM-based reasoning:

```yaml
# Example Vertex AI configuration in OpenMAS
reasoning:
  llm:
    provider: vertex_ai
    model: text-bison
    project_id: my-project
    location: us-central1
```

Implementation in agent code:
```python
from openmas.reasoning.llm.vertex import VertexAIReasoning

# Configure Vertex AI reasoning engine
reasoning_engine = VertexAIReasoning(
    project=os.environ.get("GCP_PROJECT_ID"),
    location=os.environ.get("GCP_LOCATION"),
    model_name="text-bison"
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

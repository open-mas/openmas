# AWS Deployment

This document provides guidance on deploying OpenMAS agents and systems on Amazon Web Services (AWS).

## Overview

AWS offers multiple services that can be used to deploy OpenMAS agents while maintaining the framework's reasoning-agnostic architecture and multi-protocol capabilities. This guide covers the deployment options, architecture patterns, and best practices for AWS deployments.

## Deployment Options

### 1. AWS Lambda (Serverless)

**Best for**: Event-driven agents, low to moderate traffic, cost-sensitive deployments
- Deploy agent communication layer as serverless functions
- Trigger agents via API Gateway, EventBridge, or SQS
- Store state in DynamoDB or other AWS database services
- Use managed reasoning services or self-hosted models

```yaml
# Example serverless.yml configuration for OpenMAS agents
service: openmas-agents

provider:
  name: aws
  runtime: python3.9
  region: us-west-2
  environment:
    OPENMAS_ENV: production
    OPENMAS_CONFIG_PATH: s3://my-bucket/config.yaml

functions:
  agent-handler:
    handler: handler.handle_agent_request
    events:
      - http:
          path: agent/{agent_id}
          method: any
          cors: true
    environment:
      OPENMAS_AGENT_TYPE: a2a
    timeout: 30
```

### 2. ECS/Fargate (Containers)

**Best for**: Continuous operation, moderate traffic, balanced cost/performance
- Deploy agents as containerized services on ECS/Fargate
- Use Application Load Balancer for traffic routing
- Store state in RDS, DynamoDB, or ElastiCache
- Scale with service auto-scaling policies

```yaml
# Example ECS Task Definition
{
  "family": "openmas-agent",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::123456789012:role/openmas-agent-role",
  "networkMode": "awsvpc",
  "containerDefinitions": [
    {
      "name": "openmas-agent",
      "image": "123456789012.dkr.ecr.us-west-2.amazonaws.com/openmas:latest",
      "essential": true,
      "command": ["openmas", "run", "agent", "my-agent"],
      "environment": [
        {"name": "OPENMAS_ENV", "value": "production"},
        {"name": "OPENMAS_PROTOCOL", "value": "a2a"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/openmas-agent",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "portMappings": [
        {
          "containerPort": 8080,
          "hostPort": 8080,
          "protocol": "tcp"
        }
      ]
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048"
}
```

### 3. EKS (Kubernetes)

**Best for**: Complex multi-agent systems, high traffic, advanced orchestration needs
- Deploy on Amazon EKS with Kubernetes orchestration
- Scale horizontally with Kubernetes HPA
- Use EBS or EFS for persistent storage
- Leverage service mesh for inter-agent communication

For detailed EKS deployment, see [Kubernetes Deployment](../kubernetes/README.md).

## AWS Deployment Architecture

### Reference Architecture 1: Serverless Multi-Agent System

![AWS Serverless Architecture](https://via.placeholder.com/800x500?text=AWS+Serverless+OpenMAS+Architecture)

Components:
1. **API Gateway**: API endpoint for external systems
2. **Lambda Functions**: Individual agent communication handlers
3. **EventBridge**: Event bus for inter-agent communication
4. **DynamoDB**: State storage and knowledge base
5. **Cognito**: Authentication and authorization
6. **CloudWatch**: Monitoring and logging
7. **S3**: Configuration and asset storage
8. **SQS/SNS**: Asynchronous messaging between agents

### Reference Architecture 2: Container-Based Multi-Agent System

![AWS Container Architecture](https://via.placeholder.com/800x500?text=AWS+Container+OpenMAS+Architecture)

Components:
1. **ECS/Fargate**: Container orchestration for agents
2. **Application Load Balancer**: Traffic distribution
3. **RDS/Aurora**: Relational database for state
4. **ElastiCache**: In-memory caching for performance
5. **ECR**: Container registry for agent images
6. **CloudMap**: Service discovery
7. **CloudWatch**: Monitoring and logging
8. **S3**: Configuration and asset storage

## Maintaining Reasoning Agnosticism

AWS deployments maintain OpenMAS's reasoning-agnostic architecture through:

1. **Communication Layer ("Body")**:
   - Deployed as Lambda functions or containers
   - Handles protocol-specific messaging (A2A, MCP, HTTP, etc.)
   - Manages service discovery and routing

2. **Reasoning Engines ("Brain")**:
   - LLM-based: Integrated with Amazon Bedrock or third-party APIs
   - Rule-based: Embedded in agent containers or separate services
   - BDI: Implemented as dedicated services with state management
   - Hybrid: Orchestrated through event-driven architecture

## Protocol Support

AWS deployments support multiple communication protocols:

1. **A2A Protocol**:
   - API Gateway + Lambda for request/response
   - SQS/SNS for asynchronous messaging
   - EventBridge for event-driven patterns

2. **MCP Protocol**:
   - API Gateway with WebSocket API
   - Lambda or ECS for server implementation
   - DynamoDB for connection management

3. **HTTP/MQTT/gRPC**:
   - API Gateway for HTTP
   - IoT Core for MQTT
   - Application Load Balancer + ECS for gRPC

## Deployment Process

### Prerequisites
- AWS CLI installed and configured
- Docker for container builds
- Terraform or CloudFormation for infrastructure as code (optional)
- OpenMAS CLI installed

### Deployment Steps

#### 1. Configure AWS Credentials
```bash
aws configure
```

#### 2. Initialize Deployment Configuration
```bash
openmas deploy init --environment aws
```

#### 3. Configure Deployment Variables
Edit the generated `deployment/aws.yaml` file:
```yaml
environment: aws
region: us-west-2
profile: default

components:
  # A2A protocol agent deployed as Lambda
  a2a_agent:
    type: agent
    config: config/a2a_agent_config.yaml
    deployment:
      type: lambda
      memory: 512
      timeout: 30
    communication:
      primary_protocol: a2a
      protocols:
        a2a:
          mode: server
          endpoint: ${API_GATEWAY_URL}

  # MCP protocol agent deployed on ECS
  mcp_agent:
    type: agent
    config: config/mcp_agent_config.yaml
    deployment:
      type: ecs
      cpu: 0.5
      memory: 1024
    communication:
      primary_protocol: mcp
      protocols:
        mcp:
          mode: client
          endpoint: ${MCP_SERVER_URL}

  # Agent with rule-based reasoning
  rule_agent:
    type: agent
    config: config/rule_agent_config.yaml
    deployment:
      type: lambda
      memory: 256
      timeout: 30
    reasoning:
      engine: simple_rule

  # Agent with BDI reasoning
  bdi_agent:
    type: agent
    config: config/bdi_agent_config.yaml
    deployment:
      type: ecs
      cpu: 1.0
      memory: 2048
    reasoning:
      engine: bdi
```

#### 3.1 Modifying Configuration with CLI
You can also use the CLI to modify the deployment configuration:

```bash
# Set the AWS region
openmas config set --file deployment/aws.yaml --path "region" --value "us-east-1"

# Configure an agent's reasoning engine
openmas config set --file deployment/aws.yaml --path "components.rule_agent.reasoning.engine" --value "simple_rule"

# Configure protocol settings
openmas config set --file deployment/aws.yaml --path "components.a2a_agent.communication.primary_protocol" --value "a2a"
```

#### 4. Build Deployment Artifacts
```bash
openmas deploy build --file deployment/aws.yaml
```

#### 5. Deploy to AWS
```bash
openmas deploy up --file deployment/aws.yaml
```

## Observability

AWS provides comprehensive observability solutions for OpenMAS:

1. **Logging**:
   - CloudWatch Logs for centralized log collection
   - Logs Insights for log analysis
   - Configure log levels through environment variables

2. **Metrics**:
   - CloudWatch Metrics for performance monitoring
   - Custom metrics for agent-specific measurements
   - Dashboards for visualization

3. **Tracing**:
   - AWS X-Ray for distributed tracing
   - Trace agent interactions and dependencies
   - Analyze performance bottlenecks

4. **Alerting**:
   - CloudWatch Alarms for threshold-based alerts
   - EventBridge for event-based notifications
   - SNS for notification delivery

## Security Best Practices

1. **IAM Roles and Policies**:
   - Use least privilege principle
   - Create separate roles for different agent types
   - Use resource-based policies for cross-service access

2. **Secret Management**:
   - Store secrets in AWS Secrets Manager
   - Use environment variables for configuration
   - Rotate credentials regularly

3. **Network Security**:
   - Use VPC for network isolation
   - Implement security groups for access control
   - Enable VPC endpoints for AWS services

4. **Data Protection**:
   - Encrypt data at rest (S3, DynamoDB, RDS)
   - Encrypt data in transit (HTTPS, TLS)
   - Implement data access controls

## Cost Optimization

1. **Right-sizing**:
   - Match resources to workload requirements
   - Use auto-scaling to adjust capacity
   - Implement scheduled scaling for predictable patterns

2. **Serverless for Variable Workloads**:
   - Use Lambda for sporadic workloads
   - Leverage provisioned concurrency for predictable loads
   - Implement tiered storage strategies

3. **Reserved Capacity**:
   - Use Savings Plans or Reserved Instances for stable workloads
   - Consider Spot Instances for fault-tolerant components
   - Implement lifecycle policies for ephemeral resources

## See Also

- [Deployment Configuration](../configuration/README.md)
- [Kubernetes Deployment](../kubernetes/README.md)
- [Deploy Command](../../13_cli_tools/commands/deploy.md)

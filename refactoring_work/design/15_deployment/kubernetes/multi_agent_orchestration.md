# Multi-Agent Orchestration in Kubernetes

## Overview

This document provides guidance on orchestrating multiple OpenMAS agents within Kubernetes environments while maintaining the core architectural principles of reasoning agnosticism and multi-protocol support. The orchestration model preserves the separation between communication infrastructure ("body") and reasoning approaches ("brain") across distributed deployments.

## Key Concepts

### Agent Orchestration Models

OpenMAS supports several orchestration models in Kubernetes:

1. **Individual Agent Pods**: Each agent runs in its own pod with dedicated resources
2. **Protocol-Grouped Deployments**: Agents sharing the same protocol stack deployed together
3. **Reasoning-Grouped Deployments**: Agents sharing reasoning engines deployed together
4. **Hybrid Deployments**: Combination of the above based on scaling requirements

### Scaling Considerations

The optimal orchestration model depends on:

- Communication patterns between agents
- Resource utilization characteristics of different reasoning engines
- Protocol overhead and bandwidth requirements
- State persistence requirements
- Fault tolerance needs

## Implementation

### Basic Multi-Agent Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openmas-agent-deployment
  labels:
    app: openmas-multi-agent
spec:
  replicas: 3  # Number of agent pods to run
  selector:
    matchLabels:
      app: openmas-agent
  template:
    metadata:
      labels:
        app: openmas-agent
    spec:
      containers:
      - name: agent-container
        image: openmas/agent:latest
        ports:
        - containerPort: 8080  # HTTP protocol
        - containerPort: 1883  # MQTT protocol
        - containerPort: 50051 # gRPC protocol
        env:
        - name: OPENMAS_AGENT_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: OPENMAS_CONFIG_PATH
          value: "/etc/openmas/config.yaml"
        volumeMounts:
        - name: config-volume
          mountPath: /etc/openmas
      volumes:
      - name: config-volume
        configMap:
          name: agent-config
```

### Protocol-Specific Service Discovery

```yaml
apiVersion: v1
kind: Service
metadata:
  name: openmas-http-service
spec:
  selector:
    app: openmas-agent
    protocol: http
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: openmas-mqtt-service
spec:
  selector:
    app: openmas-agent
    protocol: mqtt
  ports:
  - port: 1883
    targetPort: 1883
  type: ClusterIP
---
apiVersion: v1
kind: Service
metadata:
  name: openmas-grpc-service
spec:
  selector:
    app: openmas-agent
    protocol: grpc
  ports:
  - port: 50051
    targetPort: 50051
  type: ClusterIP
```

### Agent Configuration via ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-config
data:
  config.yaml: |
    version: "0.3.0"
    agent:
      id: "${OPENMAS_AGENT_ID}"
      name: "kubernetes-agent"
      description: "Agent deployed in Kubernetes"
      capabilities:
        definitions:
          - id: "capability-1"
            name: "Example Capability"
            description: "An example capability"
            parameters:
              - name: "param1"
                type: "string"
                required: true
      multi_protocol_capabilities:
        core:
          - id: "capability-1"
        protocol_mapping:
          http:
            - id: "capability-1"
              endpoint: "/api/capability-1"
          mqtt:
            - id: "capability-1"
              topic: "agents/${OPENMAS_AGENT_ID}/capability-1"
          grpc:
            - id: "capability-1"
              service: "CapabilityService"
              method: "ExecuteCapability"
    protocols:
      http:
        enabled: true
        port: 8080
        base_path: "/api"
      mqtt:
        enabled: true
        broker:
          host: "mqtt-broker.default.svc.cluster.local"
          port: 1883
      grpc:
        enabled: true
        port: 50051
    reasoning:
      type: "llm"  # Can be: rule-based, bdi, llm, kr-symbolic, kr-graph, kr-probabilistic, hybrid
      config:
        model: "example-model"
        parameters:
          temperature: 0.7
    # Additional configuration sections as needed
```

## Orchestration Strategies

### Stateless vs. Stateful Agents

For stateless agents, use standard Kubernetes Deployments. For stateful agents requiring persistent data:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: openmas-stateful-agent
spec:
  serviceName: "openmas-stateful-service"
  replicas: 3
  selector:
    matchLabels:
      app: openmas-stateful-agent
  template:
    metadata:
      labels:
        app: openmas-stateful-agent
    spec:
      containers:
      - name: agent-container
        image: openmas/agent:latest
        volumeMounts:
        - name: agent-storage
          mountPath: /data
  volumeClaimTemplates:
  - metadata:
      name: agent-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
```

### Protocol Isolation with Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: protocol-isolation
spec:
  podSelector:
    matchLabels:
      app: openmas-agent
  ingress:
  - from:
    - podSelector:
        matchLabels:
          role: api-client
    ports:
    - protocol: TCP
      port: 8080  # HTTP protocol
  - from:
    - podSelector:
        matchLabels:
          role: mqtt-client
    ports:
    - protocol: TCP
      port: 1883  # MQTT protocol
```

### Reasoning Engine Resource Allocation

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openmas-llm-agent
spec:
  replicas: 1
  selector:
    matchLabels:
      app: openmas-llm-agent
  template:
    metadata:
      labels:
        app: openmas-llm-agent
    spec:
      containers:
      - name: agent-container
        image: openmas/agent:latest
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
            nvidia.com/gpu: 1  # For GPU-accelerated LLM reasoning
          requests:
            cpu: "1"
            memory: "2Gi"
```

## Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: openmas-agent-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: openmas-agent-deployment
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Communication Between Agents

### Service Mesh Integration

OpenMAS agents can leverage service mesh technologies (e.g., Istio) for advanced traffic management, security, and observability:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: openmas-agent-routing
spec:
  hosts:
  - openmas-http-service
  http:
  - route:
    - destination:
        host: openmas-http-service
        subset: v1
      weight: 90
    - destination:
        host: openmas-http-service
        subset: v2
      weight: 10
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: openmas-agent-versions
spec:
  host: openmas-http-service
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

## Managing Multi-Protocol Configurations

### Protocol-Specific ConfigMaps

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: http-protocol-config
data:
  http-config.yaml: |
    protocols:
      http:
        enabled: true
        port: 8080
        base_path: "/api"
        middleware:
          cors:
            enabled: true
            allowed_origins: ["*"]
          authentication:
            enabled: true
            provider: "jwt"
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: mqtt-protocol-config
data:
  mqtt-config.yaml: |
    protocols:
      mqtt:
        enabled: true
        broker:
          host: "mqtt-broker.default.svc.cluster.local"
          port: 1883
        client_id: "${OPENMAS_AGENT_ID}"
        qos: 1
```

## Reasoning-Specific Deployments

Different reasoning engines may require specialized Kubernetes configurations:

### LLM-Based Reasoning

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openmas-llm-reasoning
spec:
  replicas: 1
  selector:
    matchLabels:
      app: openmas-llm-agent
  template:
    metadata:
      labels:
        app: openmas-llm-agent
    spec:
      containers:
      - name: llm-container
        image: openmas/llm-agent:latest
        resources:
          limits:
            nvidia.com/gpu: 1
```

### Knowledge Graph Reasoning

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: openmas-knowledge-graph
spec:
  serviceName: "kg-service"
  replicas: 1
  selector:
    matchLabels:
      app: openmas-kg-agent
  template:
    metadata:
      labels:
        app: openmas-kg-agent
    spec:
      containers:
      - name: kg-container
        image: openmas/kg-agent:latest
        volumeMounts:
        - name: kg-storage
          mountPath: /data/graph
  volumeClaimTemplates:
  - metadata:
      name: kg-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 5Gi
```

## Best Practices

1. **Maintain Body-Brain Separation**: Preserve the separation of communication infrastructure from reasoning engines in your Kubernetes deployment patterns

2. **Protocol-Aware Scaling**: Scale agents based on protocol traffic patterns and reasoning engine resource requirements

3. **Configuration Inheritance**: Use hierarchical ConfigMaps to implement configuration inheritance

4. **Observability**: Implement protocol-specific monitoring and logging with Prometheus and distributed tracing

5. **Security**: Implement protocol-specific security measures, including network policies and authentication providers

6. **State Management**: Use appropriate Kubernetes abstractions (StatefulSets, PVCs) for reasoning engines requiring persistent state

## Related Documentation

- [Kubernetes Manifests](./k8s_manifests.md)
- [OpenMAS Architecture Overview](../../01_architecture/architecture_overview.md)
- [Unified Configuration Schema](../../03_configuration/unified_configuration_schema.md)
- [Local Development](../local/local_development.md)
- [Containerization](../containerization/docker_compose.md)
- [Multi-Protocol Design](../../01_architecture/multi_protocol_design.md)
- [Reasoning Agnostic Design](../../01_architecture/reasoning_agnostic_design.md)

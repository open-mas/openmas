# Kubernetes Manifests

This document provides reference Kubernetes manifests for deploying OpenMAS agents and systems on Kubernetes clusters.

## Overview

Kubernetes manifests provide declarative definitions of Kubernetes resources required to deploy OpenMAS agents. These manifests maintain OpenMAS's reasoning-agnostic architecture while leveraging Kubernetes features for orchestration, scaling, and resilience.

## Basic Agent Deployment

### Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: openmas
  labels:
    name: openmas
```

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: agent-config
  namespace: openmas
data:
  config.yaml: |
    agent:
      id: "agent1"
      name: "Example Agent"
      description: "An example OpenMAS agent"
      capabilities:
        core:
          - "text-generation"
          - "function-calling"
        protocol_mapping:
          a2a:
            text-generation: "a2a-completion"
            function-calling: "a2a-function-calling"
          mcp:
            text-generation: "mcp-completion"
            function-calling: "mcp-function-calling"
      
    communication:
      protocol: "a2a"
      endpoint: "http://0.0.0.0:8080"
      
    reasoning:
      type: "llm"
      settings:
        model: "gpt-4"
        temperature: 0.7
        max_tokens: 1024
    
    observability:
      logging:
        level: "info"
        format: "json"
      metrics:
        enabled: true
        endpoint: "/metrics"
```

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: agent-secrets
  namespace: openmas
type: Opaque
data:
  openai-api-key: "c2stZXhhbXBsZWtleQ=="  # base64 encoded (fake key)
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent1
  namespace: openmas
  labels:
    app: agent1
spec:
  replicas: 1
  selector:
    matchLabels:
      app: agent1
  template:
    metadata:
      labels:
        app: agent1
    spec:
      containers:
      - name: agent
        image: openmas/agent:latest
        imagePullPolicy: Always
        command: ["openmas", "run", "agent", "--config", "/etc/openmas/config.yaml"]
        ports:
        - containerPort: 8080
        env:
        - name: OPENMAS_ENV
          value: "production"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: openai-api-key
        resources:
          requests:
            cpu: "100m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        volumeMounts:
        - name: config-volume
          mountPath: /etc/openmas
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: config-volume
        configMap:
          name: agent-config
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: agent1
  namespace: openmas
spec:
  selector:
    app: agent1
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: agent1-ingress
  namespace: openmas
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  rules:
  - host: agent1.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: agent1
            port:
              number: 80
```

## Multi-Agent Deployment

### StatefulSet

For agents that require stable network identities and persistent storage:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: stateful-agent
  namespace: openmas
spec:
  serviceName: "stateful-agent"
  replicas: 3
  selector:
    matchLabels:
      app: stateful-agent
  template:
    metadata:
      labels:
        app: stateful-agent
    spec:
      containers:
      - name: agent
        image: openmas/agent:latest
        command: ["openmas", "run", "agent", "--config", "/etc/openmas/config.yaml"]
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: OPENMAS_ENV
          value: "production"
        volumeMounts:
        - name: agent-data
          mountPath: /data
        - name: config-volume
          mountPath: /etc/openmas
      volumes:
      - name: config-volume
        configMap:
          name: agent-config
  volumeClaimTemplates:
  - metadata:
      name: agent-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "standard"
      resources:
        requests:
          storage: 1Gi
```

### Headless Service

For StatefulSet peer discovery:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: stateful-agent
  namespace: openmas
  labels:
    app: stateful-agent
spec:
  ports:
  - port: 8080
    name: agent
  clusterIP: None
  selector:
    app: stateful-agent
```

## Protocol-Specific Manifests

### A2A Protocol Agent

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: a2a-agent
  namespace: openmas
spec:
  replicas: 1
  selector:
    matchLabels:
      app: a2a-agent
  template:
    metadata:
      labels:
        app: a2a-agent
    spec:
      containers:
      - name: agent
        image: openmas/agent:latest
        env:
        - name: OPENMAS_PROTOCOL
          value: "a2a"
        - name: OPENMAS_A2A_ENDPOINT
          value: "http://0.0.0.0:8080"
        volumeMounts:
        - name: config-volume
          mountPath: /etc/openmas
      volumes:
      - name: config-volume
        configMap:
          name: a2a-agent-config
```

### MCP Protocol Agent

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-agent
  namespace: openmas
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mcp-agent
  template:
    metadata:
      labels:
        app: mcp-agent
    spec:
      containers:
      - name: agent
        image: openmas/agent:latest
        env:
        - name: OPENMAS_PROTOCOL
          value: "mcp"
        - name: OPENMAS_MCP_ENDPOINT
          value: "http://0.0.0.0:8080"
        - name: OPENMAS_MCP_SERVER_MODE
          value: "server"
        volumeMounts:
        - name: config-volume
          mountPath: /etc/openmas
      volumes:
      - name: config-volume
        configMap:
          name: mcp-agent-config
```

## Reasoning-Specific Manifests

### LLM-based Reasoning Agent

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-agent
  namespace: openmas
spec:
  replicas: 1
  selector:
    matchLabels:
      app: llm-agent
  template:
    metadata:
      labels:
        app: llm-agent
    spec:
      containers:
      - name: agent
        image: openmas/agent:latest
        env:
        - name: OPENMAS_REASONING
          value: "llm"
        - name: OPENMAS_LLM_MODEL
          value: "gpt-4"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: openai-api-key
        volumeMounts:
        - name: config-volume
          mountPath: /etc/openmas
      volumes:
      - name: config-volume
        configMap:
          name: llm-agent-config
```

### Rule-based Reasoning Agent

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rule-agent
  namespace: openmas
spec:
  replicas: 1
  selector:
    matchLabels:
      app: rule-agent
  template:
    metadata:
      labels:
        app: rule-agent
    spec:
      containers:
      - name: agent
        image: openmas/agent:latest
        env:
        - name: OPENMAS_REASONING
          value: "rule-based"
        volumeMounts:
        - name: config-volume
          mountPath: /etc/openmas
        - name: rules-volume
          mountPath: /rules
      volumes:
      - name: config-volume
        configMap:
          name: rule-agent-config
      - name: rules-volume
        configMap:
          name: rule-definitions
```

## Supporting Infrastructure

### Redis for Agent Communication

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: openmas
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:6.2
        ports:
        - containerPort: 6379
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "200m"
            memory: "256Mi"
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: openmas
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
```

### Prometheus for Monitoring

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: openmas-monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:v2.30.0
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: prometheus-config
          mountPath: /etc/prometheus
      volumes:
      - name: prometheus-config
        configMap:
          name: prometheus-config
```

## HorizontalPodAutoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: agent-hpa
  namespace: openmas
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: agent1
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
```

## RBAC Configuration

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: openmas-agent-sa
  namespace: openmas

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: openmas-agent-role
  namespace: openmas
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["get", "list", "watch"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: openmas-agent-rb
  namespace: openmas
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: openmas-agent-role
subjects:
- kind: ServiceAccount
  name: openmas-agent-sa
  namespace: openmas
```

## NetworkPolicy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: agent-network-policy
  namespace: openmas
spec:
  podSelector:
    matchLabels:
      app: agent1
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: agent-client
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  - to:
    - namespaceSelector:
        matchLabels:
          name: default
      podSelector:
        matchLabels:
          app: dns
    ports:
    - protocol: UDP
      port: 53
```

## Kustomize Structure

For managing environment-specific configurations:

```
├── base
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
├── overlays
│   ├── development
│   │   ├── kustomization.yaml
│   │   └── deployment-patch.yaml
│   ├── staging
│   │   ├── kustomization.yaml
│   │   └── deployment-patch.yaml
│   └── production
│       ├── kustomization.yaml
│       └── deployment-patch.yaml
```

Example base kustomization.yaml:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- deployment.yaml
- service.yaml
- configmap.yaml
```

Example overlay kustomization.yaml:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
bases:
- ../../base
patchesStrategicMerge:
- deployment-patch.yaml
configMapGenerator:
- name: agent-config
  behavior: merge
  literals:
  - OPENMAS_ENV=production
```

## Best Practices for Kubernetes Manifests

1. **Use Namespace Isolation**: Deploy agents in dedicated namespaces for isolation
2. **Resource Management**: Always set resource requests and limits
3. **Health Checks**: Implement proper liveness and readiness probes
4. **Configuration Management**: Use ConfigMaps for configuration and Secrets for sensitive data
5. **StatefulSets for Stateful Agents**: Use StatefulSets for agents that require stable identities
6. **Network Policies**: Control inbound and outbound traffic with NetworkPolicies
7. **Service Discovery**: Use headless services for StatefulSets
8. **Anti-Affinity**: Distribute agents across nodes for resilience
9. **Environment Variables**: Use environment variables for configuration
10. **Pod Disruption Budgets**: Ensure availability during maintenance

## See Also

- [Multi-Agent Orchestration](./multi_agent_orchestration.md)
- [Deployment Configuration](../configuration/README.md)
- [Deploy Command](../../13_cli_tools/commands/deploy.md)

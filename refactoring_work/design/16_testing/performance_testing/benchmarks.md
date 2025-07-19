# OpenMAS Performance Benchmarks

## Overview

This document defines the performance benchmarks used to measure OpenMAS components and system performance. These benchmarks are designed to evaluate the performance characteristics while preserving OpenMAS's reasoning-agnostic architecture and multi-protocol support.

## Benchmark Framework

OpenMAS uses a standardized benchmark framework that:

1. Measures performance across all supported protocols
2. Isolates communication infrastructure from reasoning engine performance
3. Provides consistent reporting across different environments
4. Allows comparison between different OpenMAS versions
5. Supports both local development and CI/CD pipeline execution

## Protocol Benchmarks

### A2A Protocol

| Benchmark | Description | Target | Measured |
|-----------|-------------|--------|----------|
| A2A_THROUGHPUT | Messages per second through A2A protocol | 1000 msg/s | - |
| A2A_LATENCY | Average response time for A2A messages | <50ms | - |
| A2A_CONCURRENT | Maximum concurrent A2A connections | 1000 | - |
| A2A_CAPABILITY_LATENCY | Average capability invocation latency | <100ms | - |
| A2A_PAYLOAD_MAX | Maximum efficient payload size | 10MB | - |

### MCP Protocol

| Benchmark | Description | Target | Measured |
|-----------|-------------|--------|----------|
| MCP_THROUGHPUT | Messages per second through MCP protocol | 1000 msg/s | - |
| MCP_LATENCY | Average response time for MCP messages | <50ms | - |
| MCP_CONCURRENT | Maximum concurrent MCP connections | 1000 | - |
| MCP_CAPABILITY_LATENCY | Average capability invocation latency | <100ms | - |
| MCP_PAYLOAD_MAX | Maximum efficient payload size | 10MB | - |

### HTTP Protocol

| Benchmark | Description | Target | Measured |
|-----------|-------------|--------|----------|
| HTTP_THROUGHPUT | Requests per second through HTTP | 5000 req/s | - |
| HTTP_LATENCY | Average response time for HTTP requests | <20ms | - |
| HTTP_CONCURRENT | Maximum concurrent HTTP connections | 10000 | - |
| HTTP_CAPABILITY_LATENCY | Average capability invocation latency | <50ms | - |
| HTTP_PAYLOAD_MAX | Maximum efficient payload size | 50MB | - |

### MQTT Protocol

| Benchmark | Description | Target | Measured |
|-----------|-------------|--------|----------|
| MQTT_THROUGHPUT | Messages per second through MQTT | 10000 msg/s | - |
| MQTT_LATENCY | Average message delivery time | <10ms | - |
| MQTT_CONCURRENT | Maximum concurrent MQTT subscriptions | 10000 | - |
| MQTT_CAPABILITY_LATENCY | Average capability invocation latency | <50ms | - |
| MQTT_PAYLOAD_MAX | Maximum efficient payload size | 1MB | - |

### gRPC Protocol

| Benchmark | Description | Target | Measured |
|-----------|-------------|--------|----------|
| GRPC_THROUGHPUT | Calls per second through gRPC | 10000 calls/s | - |
| GRPC_LATENCY | Average response time for gRPC calls | <10ms | - |
| GRPC_CONCURRENT | Maximum concurrent gRPC streams | 5000 | - |
| GRPC_CAPABILITY_LATENCY | Average capability invocation latency | <30ms | - |
| GRPC_PAYLOAD_MAX | Maximum efficient payload size | 100MB | - |

## Reasoning Engine Benchmarks

### Rule-Based Engine

| Benchmark | Description | Target | Measured |
|-----------|-------------|--------|----------|
| RULE_EVALUATION_RATE | Rules evaluated per second | 100000 rules/s | - |
| RULE_LATENCY | Average rule evaluation time | <1ms | - |
| RULE_MEMORY | Memory usage per 1000 rules | <10MB | - |
| RULE_SCALING | Performance scaling with rule count | Linear | - |

### BDI Engine

| Benchmark | Description | Target | Measured |
|-----------|-------------|--------|----------|
| BDI_BELIEF_UPDATE | Belief updates per second | 10000/s | - |
| BDI_INTENTION_SELECTION | Intention selections per second | 5000/s | - |
| BDI_PLAN_EXECUTION | Plan executions per second | 1000/s | - |
| BDI_MEMORY | Memory usage per agent | <50MB | - |
| BDI_SCALING | Performance scaling with belief count | Linear | - |

### LLM-Based Reasoning

| Benchmark | Description | Target | Measured |
|-----------|-------------|--------|----------|
| LLM_INFERENCE_LATENCY | Average inference time | <500ms | - |
| LLM_TOKEN_THROUGHPUT | Tokens processed per second | 100 tokens/s | - |
| LLM_MEMORY | Memory usage during inference | <2GB | - |
| LLM_SCALING | Performance scaling with context length | Linear | - |
| LLM_BATCHING_EFFICIENCY | Efficiency gain from batching | 5x | - |

### Knowledge Graph Reasoning

| Benchmark | Description | Target | Measured |
|-----------|-------------|--------|----------|
| KG_QUERY_LATENCY | Average query time | <50ms | - |
| KG_QUERY_THROUGHPUT | Queries per second | 1000 q/s | - |
| KG_MEMORY | Memory usage per 10000 nodes | <100MB | - |
| KG_SCALING | Performance scaling with graph size | Log-linear | - |
| KG_UPDATE_RATE | Graph updates per second | 5000/s | - |

## Multi-Agent System Benchmarks

| Benchmark | Description | Target | Measured |
|-----------|-------------|--------|----------|
| AGENT_STARTUP_TIME | Time to start an agent | <500ms | - |
| AGENT_MEMORY | Memory usage per agent | <100MB | - |
| AGENT_CPU | CPU usage per agent under load | <10% | - |
| AGENT_SCALE_HORIZONTAL | Maximum agents per machine | 100 | - |
| AGENT_SCALE_DISTRIBUTED | Maximum agents in distributed setup | 10000 | - |
| COMMUNICATION_THROUGHPUT | Inter-agent messages per second | 10000 msg/s | - |

## Cross-Protocol Performance

| Benchmark | Description | Target | Measured |
|-----------|-------------|--------|----------|
| PROTOCOL_CONVERSION_LATENCY | Time to convert between protocols | <5ms | - |
| PROTOCOL_BRIDGE_THROUGHPUT | Messages per second through bridges | 5000 msg/s | - |
| MULTI_PROTOCOL_OVERHEAD | Performance overhead of multi-protocol support | <10% | - |

## Deployment Benchmarks

### Local Deployment

| Benchmark | Description | Target | Measured |
|-----------|-------------|--------|----------|
| LOCAL_STARTUP_TIME | Time to start local deployment | <2s | - |
| LOCAL_MEMORY | Memory usage of local deployment | <500MB | - |
| LOCAL_AGENT_DENSITY | Maximum agents on local machine | 50 | - |

### Container Deployment

| Benchmark | Description | Target | Measured |
|-----------|-------------|--------|----------|
| CONTAINER_STARTUP_TIME | Time to start containerized deployment | <5s | - |
| CONTAINER_MEMORY | Memory overhead of containerization | <20% | - |
| CONTAINER_SCALE | Scaling performance with containers | Near-linear | - |

### Kubernetes Deployment

| Benchmark | Description | Target | Measured |
|-----------|-------------|--------|----------|
| K8S_STARTUP_TIME | Time to start Kubernetes deployment | <30s | - |
| K8S_MEMORY | Memory overhead of Kubernetes | <30% | - |
| K8S_SCALE | Scaling efficiency in Kubernetes | Near-linear | - |
| K8S_RECOVERY | Time to recover from node failure | <10s | - |

## Benchmark Execution

### Running Benchmarks

Benchmarks can be executed with the following command:

```bash
openmas benchmark run --category [protocol|reasoning|multi-agent|deployment] --output results.json
```

### Continuous Benchmarking

OpenMAS uses continuous benchmarking in the CI/CD pipeline:

1. Each pull request runs a subset of benchmarks
2. Daily runs execute all benchmarks
3. Weekly comparisons detect performance regressions
4. Results are published to the performance dashboard

## Profiling Tools

OpenMAS benchmarks use the following profiling tools:

1. **py-spy**: CPU profiling
2. **memory_profiler**: Memory profiling
3. **Prometheus**: Metrics collection
4. **Jaeger**: Distributed tracing
5. **Flame graphs**: Visual performance analysis

## Performance Budgets

OpenMAS defines performance budgets for critical operations:

1. Agent initialization: <500ms
2. Protocol message handling: <10ms
3. Capability invocation: <100ms
4. Configuration loading: <50ms
5. Command-line operation: <1s

## Related Documentation

- [Performance Testing Overview](./README.md)
- [Integration Testing](../integration_testing/README.md)
- [Multi-Agent Testing](../integration_testing/multi_agent_testing.md)
- [Test Framework](../framework/README.md)
- [Deployment Documentation](../../15_deployment/README.md)

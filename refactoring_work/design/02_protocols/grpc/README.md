# gRPC Protocol Support in OpenMAS

## Overview

gRPC is a modern, high-performance Remote Procedure Call (RPC) framework that can run in any environment. OpenMAS provides comprehensive gRPC support while maintaining its core principle of reasoning agnosticism.

**Detailed documentation**: [gRPC Protocol Documentation](./grpc_protocol.md)

## Protocol Specification

- **Name**: gRPC (Remote Procedure Call)
- **Version**: Based on HTTP/2
- **Purpose**: High-performance, language-agnostic RPC framework
- **Transport**: HTTP/2
- **Reasoning Agnosticism**: Complete separation between gRPC communication layer and agent reasoning approaches

## Key Features

- Protocol Buffer-based service definitions
- Binary serialization for efficient data exchange
- Support for unary, server streaming, client streaming, and bidirectional streaming RPC
- Built-in load balancing, health checking, and authentication
- Cross-language service implementation and client generation

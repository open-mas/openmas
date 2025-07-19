# MQTT Protocol Support in OpenMAS

## Overview

The Message Queuing Telemetry Transport (MQTT) is a lightweight, publish-subscribe messaging protocol designed for constrained devices and low-bandwidth, high-latency, or unreliable networks. OpenMAS provides comprehensive MQTT support while maintaining its core principle of reasoning agnosticism.

**Detailed documentation**: [MQTT Protocol Documentation](./mqtt_protocol.md)

## Protocol Specification

- **Name**: Message Queuing Telemetry Transport (MQTT)
- **Version**: 3.1.1 and 5.0
- **Purpose**: Lightweight publish-subscribe messaging for IoT and distributed agents
- **Transport**: TCP/IP, WebSocket
- **Reasoning Agnosticism**: Complete separation between MQTT communication layer and agent reasoning approaches

## Key Features

- Topic-based publish-subscribe messaging
- Quality of Service levels (QoS)
- Retained messages and Last Will and Testament
- Session persistence for disconnected clients
- Lightweight protocol ideal for constrained environments

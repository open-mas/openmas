# Protocol Configuration Guide

## Overview

This guide provides comprehensive configuration examples for all supported protocols in OpenMAS. Each protocol has specific configuration requirements while maintaining OpenMAS's reasoning agnosticism principles.

## Protocol Configuration Fundamentals

All protocol configurations in OpenMAS share a common structure while having protocol-specific parameters. The configuration is part of the unified schema, adhering to OpenMAS's "Single Source of Truth" principle.

### Common Configuration Structure

```json
{
  "protocols": {
    "PROTOCOL_NAME": {
      "enabled": true,
      "transport": {
        "type": "TRANSPORT_TYPE",
        "config": { ... }
      },
      "security": { ... },
      "protocol_specific_settings": { ... }
    }
  }
}
```

## Protocol-Specific Configurations

### 1. A2A Protocol

The Agent-to-Agent (A2A) protocol enables standardized communication between agents.

#### Basic A2A Configuration

```json
{
  "protocols": {
    "a2a": {
      "enabled": true,
      "transport": {
        "type": "http",
        "config": {
          "port": 8080,
          "host": "0.0.0.0",
          "mode": "server"
        }
      },
      "security": {
        "auth_provider": "basic",
        "auth_config": {
          "username_env": "OPENMAS_A2A_USERNAME",
          "password_env": "OPENMAS_A2A_PASSWORD"
        }
      },
      "capabilities": {
        "registration": true,
        "discovery": true
      },
      "agent_card": {
        "name": "My Agent",
        "description": "My OpenMAS agent using A2A protocol",
        "capabilities": ["weather", "calculator", "translate"],
        "url": "https://myagent.example.com/a2a"
      }
    }
  }
}
```

#### A2A Client Configuration

```json
{
  "protocols": {
    "a2a": {
      "enabled": true,
      "transport": {
        "type": "http",
        "config": {
          "mode": "client",
          "timeout_seconds": 30,
          "retry_config": {
            "max_retries": 3,
            "retry_delay_ms": 500
          }
        }
      },
      "capabilities": {
        "discovery": true
      },
      "directory_services": [
        {
          "url": "https://directory.example.com/a2a",
          "auth": {
            "type": "bearer",
            "token_env": "OPENMAS_A2A_DIRECTORY_TOKEN"
          }
        }
      ]
    }
  }
}
```

#### A2A with WebSockets Transport

```json
{
  "protocols": {
    "a2a": {
      "enabled": true,
      "transport": {
        "type": "websocket",
        "config": {
          "port": 8081,
          "host": "0.0.0.0",
          "path": "/a2a/ws",
          "mode": "server",
          "ping_interval_seconds": 30,
          "max_message_size_bytes": 1048576
        }
      }
    }
  }
}
```

### 2. MCP Protocol

The Model Context Protocol (MCP) enables standardized communication between agents and external AI models.

#### Basic MCP Configuration

```json
{
  "protocols": {
    "mcp": {
      "enabled": true,
      "transport": {
        "type": "sse",
        "config": {
          "port": 8082,
          "host": "0.0.0.0",
          "mode": "server"
        }
      },
      "security": {
        "auth_provider": "jwt",
        "auth_config": {
          "secret_key_env": "OPENMAS_MCP_JWT_SECRET",
          "token_expiry_seconds": 3600
        }
      },
      "capabilities": {
        "streaming": true,
        "function_calling": true
      },
      "tools": [
        {
          "name": "get_weather",
          "description": "Get weather information for a location",
          "parameters": {
            "type": "object",
            "properties": {
              "location": {
                "type": "string",
                "description": "The location to get weather for"
              },
              "units": {
                "type": "string",
                "enum": ["metric", "imperial"],
                "default": "metric",
                "description": "Unit system to use"
              }
            },
            "required": ["location"]
          }
        }
      ]
    }
  }
}
```

#### MCP Client Configuration

```json
{
  "protocols": {
    "mcp": {
      "enabled": true,
      "transport": {
        "type": "sse",
        "config": {
          "mode": "client",
          "timeout_seconds": 60,
          "retry_config": {
            "max_retries": 5,
            "retry_delay_ms": 1000
          }
        }
      },
      "security": {
        "auth_provider": "jwt",
        "auth_config": {
          "token_env": "OPENMAS_MCP_CLIENT_TOKEN"
        }
      },
      "model_endpoints": [
        {
          "name": "default_model",
          "url": "https://model.example.com/mcp",
          "model_capabilities": ["text_generation", "function_calling"]
        }
      ]
    }
  }
}
```

#### MCP with HTTP Transport

```json
{
  "protocols": {
    "mcp": {
      "enabled": true,
      "transport": {
        "type": "http",
        "config": {
          "port": 8083,
          "host": "0.0.0.0",
          "mode": "server",
          "response_format": "streaming"
        }
      }
    }
  }
}
```

### 3. HTTP Protocol

Direct HTTP protocol for RESTful API-based agent communication.

#### Basic HTTP Configuration

```json
{
  "protocols": {
    "http": {
      "enabled": true,
      "transport": {
        "config": {
          "port": 8084,
          "host": "0.0.0.0",
          "cors": {
            "enabled": true,
            "allowed_origins": ["*"],
            "allowed_methods": ["GET", "POST"]
          },
          "compression": true
        }
      },
      "security": {
        "auth_provider": "api_key",
        "auth_config": {
          "header_name": "X-API-Key",
          "api_key_env": "OPENMAS_HTTP_API_KEY"
        }
      },
      "endpoints": [
        {
          "path": "/v1/weather",
          "method": "GET",
          "capability": "weather.get_current",
          "parameter_mapping": {
            "query": {
              "location": "location",
              "units": "units"
            }
          }
        },
        {
          "path": "/v1/translate",
          "method": "POST",
          "capability": "translation.translate_text",
          "parameter_mapping": {
            "body": {
              "text": "text",
              "source_language": "source",
              "target_language": "target"
            }
          }
        }
      ]
    }
  }
}
```

#### HTTP Client Configuration

```json
{
  "protocols": {
    "http": {
      "enabled": true,
      "transport": {
        "config": {
          "mode": "client",
          "timeout_seconds": 30,
          "retry_config": {
            "max_retries": 3,
            "retry_delay_ms": 500
          },
          "default_headers": {
            "User-Agent": "OpenMAS-Agent/1.0"
          }
        }
      },
      "service_endpoints": [
        {
          "name": "weather_service",
          "base_url": "https://weather-api.example.com",
          "auth": {
            "type": "api_key",
            "header_name": "X-API-Key",
            "api_key_env": "WEATHER_API_KEY"
          },
          "endpoints": [
            {
              "name": "get_current",
              "path": "/v1/current",
              "method": "GET",
              "parameter_mapping": {
                "location": "q",
                "units": "units"
              }
            }
          ]
        }
      ]
    }
  }
}
```

### 4. MQTT Protocol

MQTT for lightweight pub/sub communication, ideal for IoT scenarios.

#### Basic MQTT Configuration

```json
{
  "protocols": {
    "mqtt": {
      "enabled": true,
      "transport": {
        "config": {
          "broker_url": "${OPENMAS_MQTT_BROKER_URL}",
          "client_id": "openmas-agent-${OPENMAS_INSTANCE_ID}",
          "clean_session": true,
          "keep_alive_seconds": 60
        }
      },
      "security": {
        "auth_config": {
          "username_env": "OPENMAS_MQTT_USERNAME",
          "password_env": "OPENMAS_MQTT_PASSWORD",
          "use_tls": true,
          "ca_cert_path": "/path/to/ca.crt"
        }
      },
      "topics": {
        "subscriptions": [
          {
            "topic": "sensors/+/data",
            "qos": 1,
            "capability": "sensor_processor.process_data"
          },
          {
            "topic": "commands/${OPENMAS_AGENT_ID}",
            "qos": 2,
            "capability": "command_processor.execute_command"
          }
        ],
        "publications": [
          {
            "capability": "status_reporter.report_status",
            "topic": "agents/${OPENMAS_AGENT_ID}/status",
            "qos": 1,
            "retain": true
          }
        ]
      }
    }
  }
}
```

#### MQTT with Last Will and Testament

```json
{
  "protocols": {
    "mqtt": {
      "enabled": true,
      "transport": {
        "config": {
          "broker_url": "${OPENMAS_MQTT_BROKER_URL}",
          "client_id": "openmas-agent-${OPENMAS_INSTANCE_ID}",
          "clean_session": true,
          "keep_alive_seconds": 60,
          "last_will": {
            "topic": "agents/${OPENMAS_AGENT_ID}/status",
            "message": "{\"status\":\"offline\",\"timestamp\":\"${TIMESTAMP}\"}",
            "qos": 1,
            "retain": true
          }
        }
      }
    }
  }
}
```

### 5. gRPC Protocol

gRPC for high-performance, strongly-typed communications.

#### Basic gRPC Configuration

```json
{
  "protocols": {
    "grpc": {
      "enabled": true,
      "transport": {
        "config": {
          "port": 50051,
          "host": "0.0.0.0",
          "mode": "server",
          "max_concurrent_rpcs": 100,
          "max_message_length_bytes": 4194304
        }
      },
      "security": {
        "auth_provider": "tls",
        "auth_config": {
          "cert_path": "/path/to/server.crt",
          "key_path": "/path/to/server.key",
          "ca_cert_path": "/path/to/ca.crt"
        }
      },
      "service_definitions": [
        {
          "proto_file": "./protos/agent_service.proto",
          "service_name": "AgentService",
          "capability_mapping": {
            "GetWeather": "weather.get_current",
            "TranslateText": "translation.translate_text"
          }
        }
      ]
    }
  }
}
```

#### gRPC Client Configuration

```json
{
  "protocols": {
    "grpc": {
      "enabled": true,
      "transport": {
        "config": {
          "mode": "client",
          "timeout_seconds": 30,
          "retry_config": {
            "max_retries": 3,
            "retry_delay_ms": 500
          }
        }
      },
      "security": {
        "auth_provider": "tls",
        "auth_config": {
          "cert_path": "/path/to/client.crt",
          "key_path": "/path/to/client.key",
          "ca_cert_path": "/path/to/ca.crt"
        }
      },
      "service_endpoints": [
        {
          "name": "agent_service",
          "host": "grpc.example.com",
          "port": 50051,
          "proto_file": "./protos/agent_service.proto",
          "service_name": "AgentService",
          "capability_mapping": {
            "GetWeather": "weather.get_current"
          }
        }
      ]
    }
  }
}
```

## Multi-Protocol Configuration

Agents can support multiple protocols simultaneously:

```json
{
  "protocols": {
    "a2a": {
      "enabled": true,
      "transport": {
        "type": "http",
        "config": {
          "port": 8080,
          "host": "0.0.0.0"
        }
      }
    },
    "mcp": {
      "enabled": true,
      "transport": {
        "type": "sse",
        "config": {
          "port": 8082,
          "host": "0.0.0.0"
        }
      }
    },
    "http": {
      "enabled": true,
      "transport": {
        "config": {
          "port": 8084,
          "host": "0.0.0.0"
        }
      }
    }
  },
  "multi_protocol_capabilities": {
    "core": [
      {
        "name": "weather.get_current",
        "description": "Get current weather for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "Location name"
            },
            "units": {
              "type": "string",
              "enum": ["metric", "imperial"],
              "default": "metric",
              "description": "Units system"
            }
          },
          "required": ["location"]
        }
      }
    ],
    "protocol_mapping": {
      "a2a": {
        "weather.get_current": "getWeather"
      },
      "mcp": {
        "weather.get_current": "get_weather_tool"
      },
      "http": {
        "weather.get_current": "/v1/weather"
      }
    }
  }
}
```

## Protocol Adapter Extensions

Protocol adapters allow communication between agents using different protocols. Example configuration:

```json
{
  "extensions": {
    "protocol_adapters": [
      {
        "name": "a2a_mcp_adapter",
        "enabled": true,
        "class": "openmas.extensions.protocol_adapters.A2AMCPAdapter",
        "config": {
          "mappings": {
            "a2a_to_mcp": {
              "getWeather": "get_weather_tool",
              "calculateExpression": "calculator_tool"
            },
            "mcp_to_a2a": {
              "get_weather_tool": "getWeather",
              "calculator_tool": "calculateExpression"
            }
          }
        }
      }
    ]
  }
}
```

## Environment Variable Substitution

As shown in examples, environment variables can be used for sensitive configuration:

```
${OPENMAS_MQTT_BROKER_URL}
${OPENMAS_INSTANCE_ID}
${OPENMAS_AGENT_ID}
```

See [Environment Variables Guide](/refactoring_work/00b_overview/03_configuration/environment_variables.md) for details.

## Security Configurations

Each protocol should be configured with appropriate security settings:

### Authentication Options

1. **API Key**
```json
"security": {
  "auth_provider": "api_key",
  "auth_config": {
    "header_name": "X-API-Key",
    "api_key_env": "OPENMAS_API_KEY"
  }
}
```

2. **JWT**
```json
"security": {
  "auth_provider": "jwt",
  "auth_config": {
    "secret_key_env": "OPENMAS_JWT_SECRET",
    "token_expiry_seconds": 3600,
    "algorithm": "HS256"
  }
}
```

3. **Basic Auth**
```json
"security": {
  "auth_provider": "basic",
  "auth_config": {
    "username_env": "OPENMAS_USERNAME",
    "password_env": "OPENMAS_PASSWORD"
  }
}
```

4. **TLS/SSL**
```json
"security": {
  "auth_provider": "tls",
  "auth_config": {
    "cert_path": "/path/to/cert.pem",
    "key_path": "/path/to/key.pem",
    "ca_cert_path": "/path/to/ca.pem"
  }
}
```

## Protocol Selection Guidelines

When deciding which protocol to use:

1. **A2A** - For standardized agent-to-agent communication with capability discovery
2. **MCP** - For AI model integration and function calling
3. **HTTP** - For RESTful API compatibility and web integration
4. **MQTT** - For IoT scenarios and lightweight pub/sub messaging
5. **gRPC** - For high-performance, strongly-typed service communications

## Reasoning Agnostic Protocol Configuration

Remember that OpenMAS separates the communication layer (protocols) from the reasoning layer. This means your protocol configuration should focus on communication concerns only, without assumptions about the reasoning approach used.

Each protocol configuration defines how messages are transmitted and formatted, while the unified capability schema defines what operations are available, keeping these concepts separate and adhering to OpenMAS's reasoning agnostic principles.

## References

- [Unified Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
- [Environment Variables Guide](/refactoring_work/00b_overview/03_configuration/environment_variables.md)
- [A2A Protocol Specification](/refactoring_work/00b_overview/02_protocols/a2a/a2a_specification.md)
- [MCP Protocol Specification](/refactoring_work/00b_overview/02_protocols/mcp/mcp_specification.md)

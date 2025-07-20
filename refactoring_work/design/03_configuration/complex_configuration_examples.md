# Complex Configuration Examples

## Overview

This document provides detailed examples of complex OpenMAS configuration scenarios. These examples demonstrate how to leverage the unified configuration schema for advanced use cases while maintaining OpenMAS's core principles of reasoning agnosticism and protocol independence.

## Multi-Protocol, Multi-Reasoning Agent System

This example shows a complete configuration for a system with multiple agents using different reasoning approaches, communicating through multiple protocols.

```yaml
name: "Travel Booking System"
version: "1.0.0"
description: "Multi-agent system for travel booking with various reasoning approaches"

defaults:
  common:
    log_level: "info"

  security:
    authentication:
      enabled: true
      providers:
        api_key:
          enabled: true
          api_keys:
            - name: "system_default"
              key: "${SYSTEM_API_KEY}"
              roles: ["system"]

  observability:
    logging:
      enabled: true
      format: "json"
      level: "info"
    metrics:
      enabled: true
      export:
        prometheus:
          enabled: true
          port: 9090

agents:
  # LLM-based coordinator agent
  travel_coordinator:
    class: "agents.travel.TravelCoordinatorAgent"
    type: "llm"
    description: "Coordinates overall travel planning"

    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8000/agents"
          agent_id: "travel_coordinator"
      - type: "mcp-sse"
        enabled: true
        options:
          server_mode: true
          port: 3000

    capabilities:
      multi_protocol_capabilities:
        core:
          - id: "search_flights"
            name: "Search Flights"
            description: "Search for available flights"
            parameters:
              type: "object"
              properties:
                origin:
                  type: "string"
                  description: "Origin airport code"
                destination:
                  type: "string"
                  description: "Destination airport code"
                date:
                  type: "string"
                  description: "Date of travel (YYYY-MM-DD)"
            returns:
              type: "array"
              items:
                type: "object"
                properties:
                  flight_id:
                    type: "string"
                  airline:
                    type: "string"
                  departure:
                    type: "string"
                  arrival:
                    type: "string"
                  price:
                    type: "number"
        protocol_mapping:
          a2a-http:
            search_flights: "search_flights"
          mcp-sse:
            search_flights: "search_flights_tool"

    reasoning:
      type: "llm"
      llm_config:
        model: "gpt-4"
        temperature: 0.2
        system_prompt: "${COORDINATOR_PROMPT}"

  # Rule-based flight search agent
  flight_search:
    class: "agents.travel.FlightSearchAgent"
    type: "rule_based"
    description: "Searches flight databases using rule-based approach"

    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8000/agents"
          agent_id: "flight_search"
      - type: "grpc"
        enabled: true
        options:
          host: "0.0.0.0"
          port: 50051

    capabilities:
      multi_protocol_capabilities:
        core:
          - id: "search_airline_database"
            name: "Search Airline Database"
            description: "Search airline database for flights"
            parameters:
              type: "object"
              properties:
                origin:
                  type: "string"
                destination:
                  type: "string"
                date:
                  type: "string"
                airline_code:
                  type: "string"
                  description: "Optional airline code filter"
                  required: false
            returns:
              type: "array"
              items:
                type: "object"
        protocol_mapping:
          a2a-http:
            search_airline_database: "search_airline_database"
          grpc:
            search_airline_database: "SearchAirlineDatabase"

    reasoning:
      type: "rule_based"
      rules:
        - name: "domestic_flight_search"
          condition: "origin.country == destination.country"
          action: "search_domestic_database"
        - name: "international_flight_search"
          condition: "origin.country != destination.country"
          action: "search_international_database"

  # BDI-based booking agent
  booking_agent:
    class: "agents.travel.BookingAgent"
    type: "bdi"
    description: "Handles booking process using BDI approach"

    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8000/agents"
          agent_id: "booking_agent"
      - type: "mqtt"
        enabled: true
        options:
          broker_host: "localhost"
          broker_port: 1883
          topics:
            - name: "booking/requests"
              role: "subscribe"
            - name: "booking/confirmations"
              role: "publish"

    capabilities:
      multi_protocol_capabilities:
        core:
          - id: "book_flight"
            name: "Book Flight"
            description: "Book a flight"
            parameters:
              type: "object"
              properties:
                flight_id:
                  type: "string"
                passenger_details:
                  type: "object"
                payment_details:
                  type: "object"
            returns:
              type: "object"
              properties:
                booking_id:
                  type: "string"
                status:
                  type: "string"
        protocol_mapping:
          a2a-http:
            book_flight: "book_flight"
          mqtt:
            book_flight: "booking/requests"

    reasoning:
      type: "bdi"
      beliefs:
        - name: "available_airlines"
          type: "list"
          initial_value: ["AA", "UA", "DL", "BA"]
        - name: "payment_methods"
          type: "list"
          initial_value: ["credit_card", "paypal", "bank_transfer"]
      desires:
        - name: "maximize_booking_success"
          priority: 1
        - name: "minimize_booking_cost"
          priority: 2
      intentions:
        - name: "process_booking_request"
          trigger: "receive_booking_request"
          plan: ["validate_payment", "confirm_availability", "create_booking", "send_confirmation"]

# Topology configuration
defaults:
  topology:
    pattern: "hierarchical"
    roles:
      - name: "coordinator"
        description: "Coordinates the overall process"
      - name: "service_provider"
        description: "Provides specific services"
      - name: "booking_processor"
        description: "Processes bookings"
    relationships:
      - name: "coordinates"
        source_role: "coordinator"
        target_role: "service_provider"
        communication_pattern: "request_response"
      - name: "books"
        source_role: "coordinator"
        target_role: "booking_processor"
        communication_pattern: "request_response"

# Agent topology mapping
agents:
  travel_coordinator:
    topology:
      role: "coordinator"
      relationships:
        - agent_id: "flight_search"
          relationship_type: "coordinates"
        - agent_id: "booking_agent"
          relationship_type: "books"
  flight_search:
    topology:
      role: "service_provider"
      relationships:
        - agent_id: "travel_coordinator"
          relationship_type: "coordinates"
          direction: "incoming"
  booking_agent:
    topology:
      role: "booking_processor"
      relationships:
        - agent_id: "travel_coordinator"
          relationship_type: "books"
          direction: "incoming"

# Environment-specific configuration
environments:
  production:
    common:
      log_level: "warning"
    agents:
      travel_coordinator:
        protocols:
          - type: "a2a-http"
            options:
              base_url: "${PROD_A2A_BASE_URL}"
          - type: "mcp-sse"
            options:
              port: "${PROD_MCP_PORT}"
      flight_search:
        protocols:
          - type: "a2a-http"
            options:
              base_url: "${PROD_A2A_BASE_URL}"
          - type: "grpc"
            options:
              host: "${PROD_GRPC_HOST}"
              port: "${PROD_GRPC_PORT}"

  development:
    common:
      log_level: "debug"
    security:
      authentication:
        enabled: false
```

## Hybrid Reasoning Agent with Multi-Protocol Support

This example demonstrates a hybrid agent that combines multiple reasoning approaches while supporting various protocols.

```yaml
agents:
  customer_service:
    class: "agents.hybrid.CustomerServiceAgent"
    type: "hybrid"
    description: "Customer service agent with hybrid reasoning"

    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8000/agents"
          agent_id: "customer_service"
      - type: "mcp-sse"
        enabled: true
        options:
          server_mode: true
          port: 3001
      - type: "websocket"
        enabled: true
        options:
          host: "0.0.0.0"
          port: 8080
          path: "/customer-service"

    capabilities:
      multi_protocol_capabilities:
        core:
          - id: "answer_faq"
            name: "Answer FAQ"
            description: "Answer frequently asked questions"
            parameters:
              type: "object"
              properties:
                question:
                  type: "string"
            returns:
              type: "object"
              properties:
                answer:
                  type: "string"
                confidence:
                  type: "number"
          - id: "escalate_issue"
            name: "Escalate Issue"
            description: "Escalate customer issue to human agent"
            parameters:
              type: "object"
              properties:
                issue_description:
                  type: "string"
                priority:
                  type: "string"
                  enum: ["low", "medium", "high", "critical"]
            returns:
              type: "object"
              properties:
                ticket_id:
                  type: "string"
                estimated_response_time:
                  type: "string"
        protocol_mapping:
          a2a-http:
            answer_faq: "answer_faq"
            escalate_issue: "escalate_issue"
          mcp-sse:
            answer_faq: "answer_faq_tool"
            escalate_issue: "escalate_issue_tool"
          websocket:
            answer_faq: "answer_faq"
            escalate_issue: "escalate_issue"

    reasoning:
      type: "hybrid"
      components:
        - type: "rule_based"
          priority: 1
          rules:
            - name: "simple_faq"
              condition: "question_type == 'faq' AND confidence > 0.9"
              action: "answer_from_faq_database"
            - name: "critical_issue"
              condition: "issue_priority == 'critical'"
              action: "immediate_escalation"

        - type: "llm"
          priority: 2
          llm_config:
            model: "gpt-4"
            temperature: 0.3
            system_prompt: "${CUSTOMER_SERVICE_PROMPT}"

        - type: "symbolic"
          priority: 3
          knowledge_base: "customer_service_kb"
          inference_engine: "prolog"

      fallback: "llm"  # If no component can handle the request

    knowledge:
      representation_type: "hybrid"
      storage:
        type: "vector_store"
        connection_string: "${VECTOR_DB_CONNECTION}"
      sources:
        - name: "faq_database"
          type: "structured"
          connection: "${FAQ_DB_CONNECTION}"
        - name: "product_documentation"
          type: "unstructured"
          path: "/data/product_docs"

    asset_management:
      enabled: true
      asset_types:
        - type: "customer_data"
          storage: "encrypted_db"
          access_control:
            roles: ["customer_service", "admin"]
        - type: "product_images"
          storage: "cdn"
          cache_policy: "public"

    security:
      authentication:
        providers:
          api_key:
            api_key: "${CS_AGENT_API_KEY}"
          oauth2:
            client_id: "${OAUTH_CLIENT_ID}"
            client_secret: "${OAUTH_CLIENT_SECRET}"
            auth_url: "https://auth.example.com/oauth2/authorize"
            token_url: "https://auth.example.com/oauth2/token"

      authorization:
        roles:
          - name: "customer"
            permissions: ["view_faq", "create_ticket"]
          - name: "agent"
            permissions: ["view_faq", "create_ticket", "view_customer_data"]
          - name: "admin"
            permissions: ["*"]

    sessions:
      enabled: true
      storage:
        type: "redis"
        connection_string: "${REDIS_CONNECTION}"
      ttl: 3600  # Session timeout in seconds

    observability:
      logging:
        level: "info"
        sensitive_fields: ["customer_email", "payment_details"]
      metrics:
        enabled: true
        export:
          prometheus:
            enabled: true
```

## Complex Multi-Agent System with External Integrations

This example shows a system that integrates with external services while maintaining protocol independence.

```yaml
name: "Intelligent Marketing System"
version: "1.0.0"
description: "Multi-agent marketing system with external integrations"

# External integrations definition
integrations:
  crm_system:
    type: "api"
    description: "Customer Relationship Management System"
    enabled: true
    config:
      base_url: "${CRM_API_URL}"
      auth:
        type: "api_key"
        api_key_env: "CRM_API_KEY"
        header_name: "X-API-Key"
      retry:
        max_attempts: 3
        backoff_factor: 2

  email_service:
    type: "api"
    description: "Email Marketing Service"
    enabled: true
    config:
      base_url: "${EMAIL_API_URL}"
      auth:
        type: "oauth2"
        client_id_env: "EMAIL_CLIENT_ID"
        client_secret_env: "EMAIL_CLIENT_SECRET"
        scopes: ["email.send", "email.read"]
      rate_limit:
        max_requests: 100
        time_window: 60  # seconds

  analytics_platform:
    type: "api"
    description: "Marketing Analytics Platform"
    enabled: true
    config:
      base_url: "${ANALYTICS_API_URL}"
      auth:
        type: "api_key"
        api_key_env: "ANALYTICS_API_KEY"
        header_name: "Authorization"
        prefix: "Bearer "
      format: "json"

# Agent definitions that use the integrations
agents:
  campaign_manager:
    class: "agents.marketing.CampaignManagerAgent"
    type: "llm"
    description: "Manages marketing campaigns"

    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8000/agents"
          agent_id: "campaign_manager"
      - type: "mcp-sse"
        enabled: true
        options:
          server_mode: true
          port: 3010

    capabilities:
      multi_protocol_capabilities:
        core:
          - id: "create_campaign"
            name: "Create Campaign"
            description: "Create a new marketing campaign"
            parameters:
              type: "object"
              properties:
                name:
                  type: "string"
                target_audience:
                  type: "object"
                content:
                  type: "object"
                schedule:
                  type: "object"
            returns:
              type: "object"
              properties:
                campaign_id:
                  type: "string"
                status:
                  type: "string"
          - id: "analyze_results"
            name: "Analyze Campaign Results"
            description: "Analyze the results of a marketing campaign"
            parameters:
              type: "object"
              properties:
                campaign_id:
                  type: "string"
                metrics:
                  type: "array"
                  items:
                    type: "string"
            returns:
              type: "object"
              properties:
                insights:
                  type: "array"
                  items:
                    type: "object"
        protocol_mapping:
          a2a-http:
            create_campaign: "create_campaign"
            analyze_results: "analyze_results"
          mcp-sse:
            create_campaign: "create_campaign_tool"
            analyze_results: "analyze_results_tool"

    # Integration references in agent configuration
    integrations:
      - integration_id: "crm_system"
        capabilities:
          - id: "get_customer_segments"
            mapping: "get_audience_from_crm"
      - integration_id: "email_service"
        capabilities:
          - id: "send_campaign"
            mapping: "execute_email_campaign"
      - integration_id: "analytics_platform"
        capabilities:
          - id: "get_campaign_metrics"
            mapping: "fetch_campaign_analytics"

    reasoning:
      type: "llm"
      llm_config:
        model: "gpt-4"
        temperature: 0.3
        system_prompt: "${CAMPAIGN_MANAGER_PROMPT}"

  audience_analyzer:
    class: "agents.marketing.AudienceAnalyzerAgent"
    type: "hybrid"
    description: "Analyzes and segments the audience"

    protocols:
      - type: "a2a-http"
        enabled: true
        options:
          base_url: "http://localhost:8000/agents"
          agent_id: "audience_analyzer"
      - type: "grpc"
        enabled: true
        options:
          host: "0.0.0.0"
          port: 50055

    # Integration references in agent configuration
    integrations:
      - integration_id: "crm_system"
        capabilities:
          - id: "get_customer_data"
            mapping: "fetch_customer_profiles"
      - integration_id: "analytics_platform"
        capabilities:
          - id: "get_audience_insights"
            mapping: "analyze_audience_behavior"

    reasoning:
      type: "hybrid"
      components:
        - type: "rule_based"
          priority: 1
          rules:
            - name: "basic_segmentation"
              condition: "customer_data.complete == true"
              action: "apply_segmentation_rules"
        - type: "llm"
          priority: 2
          llm_config:
            model: "gpt-4"
            temperature: 0.2
      fallback: "llm"

# Communication patterns configuration
defaults:
  communication_patterns:
    request_response:
      timeout: 30
      retry:
        enabled: true
        max_attempts: 3
    publish_subscribe:
      topics:
        - name: "campaign_updates"
          description: "Updates about campaign status"
        - name: "audience_insights"
          description: "New audience insights"
    event_based:
      events:
        - name: "campaign_created"
          schema:
            type: "object"
            properties:
              campaign_id:
                type: "string"
        - name: "segment_updated"
          schema:
            type: "object"
            properties:
              segment_id:
                type: "string"
              changes:
                type: "object"

# Environment-specific integration configuration
environments:
  production:
    integrations:
      crm_system:
        config:
          base_url: "${PROD_CRM_API_URL}"
          timeout: 10
      email_service:
        config:
          base_url: "${PROD_EMAIL_API_URL}"
          rate_limit:
            max_requests: 500
            time_window: 60

  staging:
    integrations:
      crm_system:
        config:
          base_url: "${STAGING_CRM_API_URL}"
          timeout: 30
      email_service:
        config:
          base_url: "${STAGING_EMAIL_API_URL}"
          rate_limit:
            max_requests: 200
            time_window: 60
```

## Multi-Protocol System Security Configuration

This example demonstrates comprehensive security configuration across all protocols.

```yaml
defaults:
  security:
    authentication:
      enabled: true
      default_provider: "api_key"
      providers:
        api_key:
          enabled: true
          header_name: "X-API-Key"
          query_param: "api_key"
          api_keys:
            - name: "system_default"
              key: "${SYSTEM_API_KEY}"
              roles: ["system"]
            - name: "admin"
              key: "${ADMIN_API_KEY}"
              roles: ["admin"]

        jwt:
          enabled: true
          issuer: "openmas-auth"
          audience: "openmas-services"
          public_key_path: "/keys/jwt_public.pem"
          private_key_path: "/keys/jwt_private.pem"
          private_key_password: "${JWT_KEY_PASSWORD}"
          expiration: 3600  # seconds

        oauth2:
          enabled: true
          client_id: "${OAUTH_CLIENT_ID}"
          client_secret: "${OAUTH_CLIENT_SECRET}"
          auth_url: "https://auth.example.com/oauth2/authorize"
          token_url: "https://auth.example.com/oauth2/token"
          scopes: ["openid", "profile", "agents:read", "agents:write"]
          redirect_uri: "https://api.example.com/oauth2/callback"

    authorization:
      enabled: true
      default_policy: "deny"
      roles:
        - name: "anonymous"
          permissions: ["agents:discover"]
        - name: "user"
          permissions: ["agents:discover", "agents:invoke:public"]
        - name: "admin"
          permissions: ["agents:*"]
        - name: "system"
          permissions: ["*"]

      resources:
        - name: "agents"
          actions: ["discover", "invoke", "manage"]
        - name: "capabilities"
          actions: ["discover", "invoke"]
        - name: "system"
          actions: ["monitor", "configure"]

      policies:
        - name: "public_access"
          resources: ["agents"]
          actions: ["discover"]
          effect: "allow"
          subjects: ["anonymous", "user", "admin", "system"]

        - name: "capability_access"
          resources: ["capabilities"]
          actions: ["invoke"]
          effect: "allow"
          subjects: ["user", "admin", "system"]
          conditions:
            - "capability.access_level == 'public' OR subject.role IN capability.allowed_roles"

    # Protocol-specific security configurations
    protocols:
      a2a:
        authentication:
          enabled: true
          providers: ["api_key", "jwt"]
        authorization:
          enabled: true
        agent_cards:
          signature_verification: true
          public_key_directory: "/keys/agent_cards/"

      mcp:
        authentication:
          enabled: true
          providers: ["api_key", "oauth2"]
        authorization:
          enabled: true
        tool_authorization:
          enabled: true

      http:
        authentication:
          enabled: true
          providers: ["api_key", "jwt", "oauth2"]
        authorization:
          enabled: true
        cors:
          enabled: true
          allowed_origins: ["https://example.com", "https://admin.example.com"]
          allowed_methods: ["GET", "POST", "PUT", "DELETE"]
          allowed_headers: ["Content-Type", "Authorization", "X-API-Key"]
          expose_headers: ["Content-Length", "Content-Type"]
          max_age: 3600

      grpc:
        authentication:
          enabled: true
          providers: ["api_key", "jwt"]
        authorization:
          enabled: true
        tls:
          enabled: true
          cert_file: "/certs/grpc.crt"
          key_file: "/certs/grpc.key"
          ca_file: "/certs/ca.crt"

      mqtt:
        authentication:
          enabled: true
          providers: ["api_key", "jwt"]
        authorization:
          enabled: true
        tls:
          enabled: true
          cert_file: "/certs/mqtt.crt"
          key_file: "/certs/mqtt.key"
          ca_file: "/certs/ca.crt"
        topic_authorization:
          enabled: true
          # Define which roles can publish/subscribe to which topics
          rules:
            - topic: "agents/+/status"
              operations: ["subscribe"]
              roles: ["user", "admin", "system"]
            - topic: "agents/+/command"
              operations: ["publish"]
              roles: ["admin", "system"]
```

These examples demonstrate the flexibility and expressiveness of the OpenMAS configuration schema for complex real-world scenarios, while maintaining the core architectural principles of reasoning agnosticism and protocol independence.

For the complete schema definition, refer to the [Unified Configuration Schema](/03_configuration/schema/unified_schema_overview.md).

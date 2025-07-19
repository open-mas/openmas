# Basic Communication Pattern Examples

## Overview

This document provides practical examples of how to use OpenMAS communication patterns in typical agent scenarios. These examples demonstrate pattern configuration, integration with agent topologies, and protocol adaptation.

## Request-Response Pattern Example

### Configuration

```yaml
# Project configuration
communication_patterns:
  request_response:
    options:
      timeout: 30000
      retry:
        attempts: 3
      security:
        require_authentication: true

# Agent configuration
agents:
  travel_coordinator:
    communicator_type: "a2a"
    patterns:
      request_response:
        options:
          timeout: 15000  # Override global timeout
    topology:
      role: "orchestrator"
      relationships:
        - agent_id: "flight_search"
          relationship_type: "orchestrator_to_worker"
          communication_pattern: "request_response"
```

### Usage Example

```python
class TravelCoordinator(Agent):
    async def setup(self):
        # Set up patterns from configuration
        await self.pattern_manager.setup()
        
        # Set up topology from configuration
        await self.topology_manager.setup()
        
    async def search_flights(self, search_params):
        """Search for flights using the flight search agent."""
        try:
            # Get the request-response pattern
            pattern = await self.pattern_manager.get_pattern("request_response")
            
            # Send request to flight search agent
            response = await pattern.send_request(
                content={
                    "action": "search_flights",
                    "parameters": search_params
                },
                target_agent_id="flight_search"
            )
            
            # Process response
            if response.get("status") == "success":
                return response.get("content", {}).get("flights", [])
            else:
                self.logger.error(f"Flight search failed: {response.get('error')}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error in flight search: {e}")
            return []
```

## Publish-Subscribe Pattern Example

### Configuration

```yaml
# Project configuration
communication_patterns:
  publish_subscribe:
    options:
      delivery_guarantee: "at_least_once"
      
# Agent configuration
agents:
  status_monitor:
    communicator_type: "mqtt"
    patterns:
      publish_subscribe:
        options:
          topic_prefix: "system/status"
    topology:
      role: "monitor"
      relationships:
        - agent_id: "service_1"
          relationship_type: "monitor_to_service"
          communication_pattern: "publish_subscribe"
        - agent_id: "service_2"
          relationship_type: "monitor_to_service"
          communication_pattern: "publish_subscribe"
```

### Usage Example

```python
class StatusMonitor(Agent):
    async def setup(self):
        # Set up patterns from configuration
        await self.pattern_manager.setup()
        
        # Get the publish-subscribe pattern
        self.pubsub = await self.pattern_manager.get_pattern("publish_subscribe")
        
        # Subscribe to status topics
        await self.pubsub.subscribe("system/status/#")
        
        # Register message handler
        self.pubsub.on_message(self.handle_status_update)
        
    async def handle_status_update(self, message):
        """Handle a status update message."""
        topic = message.get("topic")
        content = message.get("content")
        
        self.logger.info(f"Status update on {topic}: {content}")
        
        # Process the status update
        service_id = topic.split("/")[-1]
        status = content.get("status")
        
        if status == "error":
            await self.alert_service_error(service_id, content)
            
    async def broadcast_system_alert(self, alert_level, message):
        """Broadcast a system alert to all services."""
        await self.pubsub.publish(
            topic="system/alerts",
            content={
                "level": alert_level,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        )
```

## Event-Based Pattern Example

### Configuration

```yaml
# Project configuration
communication_patterns:
  event_based:
    options:
      event_structure:
        include_metadata: true
      event_handling:
        ordering: "timestamp"
        
# Agent configuration
agents:
  workflow_engine:
    communicator_type: "a2a"
    patterns:
      event_based:
        options:
          filtering:
            enabled: true
    topology:
      role: "coordinator"
      relationships:
        - agent_id: "task_processor"
          relationship_type: "coordinator_to_processor"
          communication_pattern: "event_based"
```

### Usage Example

```python
class WorkflowEngine(Agent):
    async def setup(self):
        # Set up patterns from configuration
        await self.pattern_manager.setup()
        
        # Get the event-based pattern
        self.events = await self.pattern_manager.get_pattern("event_based")
        
        # Register event handlers
        self.events.on_event("task_completed", self.handle_task_completed)
        self.events.on_event("task_failed", self.handle_task_failed)
        
        # Initialize workflow state
        self.active_workflows = {}
        
    async def start_workflow(self, workflow_id, workflow_definition):
        """Start a new workflow."""
        # Initialize workflow state
        self.active_workflows[workflow_id] = {
            "definition": workflow_definition,
            "current_step": 0,
            "status": "running",
            "started_at": datetime.now().isoformat()
        }
        
        # Emit workflow started event
        await self.events.emit_event(
            event_type="workflow_started",
            content={
                "workflow_id": workflow_id,
                "definition": workflow_definition
            }
        )
        
        # Start the first task
        await self.execute_next_task(workflow_id)
        
    async def handle_task_completed(self, event):
        """Handle a task completed event."""
        workflow_id = event.get("content", {}).get("workflow_id")
        task_id = event.get("content", {}).get("task_id")
        
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow["current_step"] += 1
            
            # Check if workflow is complete
            if workflow["current_step"] >= len(workflow["definition"]["steps"]):
                workflow["status"] = "completed"
                
                # Emit workflow completed event
                await self.events.emit_event(
                    event_type="workflow_completed",
                    content={
                        "workflow_id": workflow_id,
                        "summary": self._generate_summary(workflow)
                    }
                )
            else:
                # Execute next task
                await self.execute_next_task(workflow_id)
```

## Streaming Pattern Example

### Configuration

```yaml
# Project configuration
communication_patterns:
  streaming:
    options:
      flow_control:
        buffer_size: 1000
        batch_size: 100
      
# Agent configuration
agents:
  data_processor:
    communicator_type: "grpc"
    patterns:
      streaming:
        options:
          stream_lifecycle:
            idle_timeout: 300000
    topology:
      role: "processor"
      relationships:
        - agent_id: "data_source"
          relationship_type: "processor_to_source"
          communication_pattern: "streaming"
```

### Usage Example

```python
class DataProcessor(Agent):
    async def setup(self):
        # Set up patterns from configuration
        await self.pattern_manager.setup()
        
        # Get the streaming pattern
        self.streaming = await self.pattern_manager.get_pattern("streaming")
        
    async def process_data_stream(self, stream_params):
        """Process a data stream from a data source."""
        # Start a stream
        stream = await self.streaming.start_stream(
            source_agent_id="data_source",
            params=stream_params
        )
        
        # Process the stream
        async for chunk in stream:
            # Process each chunk
            processed_data = await self._process_chunk(chunk)
            
            # Send processed data to output
            await stream.send_result(processed_data)
            
        # Stream complete
        await stream.complete()
        
    async def _process_chunk(self, chunk):
        """Process a data chunk."""
        # Implementation-specific processing
        return {
            "processed_items": len(chunk.get("items", [])),
            "results": [self._transform_item(item) for item in chunk.get("items", [])]
        }
```

## Multi-Pattern Integration Example

This example shows how to use multiple patterns together in a single agent:

```python
class SmartAssistant(Agent):
    async def setup(self):
        # Set up patterns
        await self.pattern_manager.setup()
        
        # Get patterns
        self.request_response = await self.pattern_manager.get_pattern("request_response")
        self.events = await self.pattern_manager.get_pattern("event_based")
        self.pubsub = await self.pattern_manager.get_pattern("publish_subscribe")
        
        # Subscribe to user activity
        await self.pubsub.subscribe("user/activity/#")
        
        # Register event handlers
        self.events.on_event("task_assigned", self.handle_task_assigned)
        
    async def handle_user_query(self, query):
        """Handle a user query using request-response pattern."""
        # Determine which service can handle this query
        service = self._determine_service(query)
        
        # Send request to appropriate service
        response = await self.request_response.send_request(
            content={
                "query": query.get("text"),
                "context": query.get("context", {})
            },
            target_agent_id=service
        )
        
        # Process response
        if response.get("status") == "success":
            # Publish user response event
            await self.pubsub.publish(
                topic=f"user/responses/{query.get('user_id')}",
                content={
                    "query_id": query.get("id"),
                    "response": response.get("content"),
                    "service": service
                }
            )
            
            return response.get("content")
        else:
            # Emit error event
            await self.events.emit_event(
                event_type="query_failed",
                content={
                    "query_id": query.get("id"),
                    "error": response.get("error"),
                    "service": service
                }
            )
            
            return {
                "error": "Could not process your query",
                "details": response.get("error", {}).get("message")
            }
```

## Cross-Protocol Pattern Example

This example shows communication across different protocols:

```yaml
# Two agents using different protocols
agents:
  frontend_agent:
    communicator_type: "http"
    patterns:
      request_response:
        protocol_adaptations:
          http:
            method: "POST"
            path: "/api/requests"
    topology:
      role: "client"
      relationships:
        - agent_id: "backend_agent"
          relationship_type: "client_to_server"
          communication_pattern: "request_response"
  
  backend_agent:
    communicator_type: "a2a"
    patterns:
      request_response:
        protocol_adaptations:
          a2a:
            use_tasks: true
            task_type: "request_response"
    topology:
      role: "server"
      relationships:
        - agent_id: "frontend_agent"
          relationship_type: "server_to_client"
          communication_pattern: "request_response"
```

### Implementation

```python
# This works seamlessly despite different protocols
# The frontend agent sends an HTTP request
# The pattern system adapts it to A2A for the backend
# The backend processes it using A2A
# The response returns as HTTP to the frontend

# Frontend code (HTTP)
response = await request_response_pattern.send_request(
    content={"action": "get_data", "id": "12345"},
    target_agent_id="backend_agent"
)

# Backend code (A2A)
def handle_request(self, request):
    # Process the request (converted from HTTP to A2A)
    action = request.get("content", {}).get("action")
    if action == "get_data":
        data_id = request.get("content", {}).get("id")
        return {"data": self._get_data(data_id)}
```

## Session Integration Example

This example shows how patterns integrate with session management:

```python
class ConversationalAgent(Agent):
    async def setup(self):
        # Set up patterns
        await self.pattern_manager.setup()
        
        # Get the request-response pattern
        self.request_response = await self.pattern_manager.get_pattern("request_response")
        
        # Initialize session manager
        self.session_manager = SessionManager(self.config.get("sessions", {}))
        
    async def handle_message(self, message):
        """Handle a conversational message."""
        user_id = message.get("user_id")
        content = message.get("content")
        
        # Get or create session
        session = await self.session_manager.get_session(user_id)
        if not session:
            session = await self.session_manager.create_session(user_id)
            
        # Update session with new message
        session.add_message("user", content)
        
        # Use request-response pattern to get response from reasoning agent
        response = await self.request_response.send_request(
            content={
                "messages": session.get_messages(),
                "user_id": user_id
            },
            target_agent_id="reasoning_agent"
        )
        
        # Process response
        if response.get("status") == "success":
            agent_response = response.get("content", {}).get("response")
            
            # Update session with agent response
            session.add_message("assistant", agent_response)
            
            # Save session
            await self.session_manager.update_session(user_id, session)
            
            return agent_response
        else:
            return "I'm sorry, I couldn't process your message."
```

## Reasoning-Agnostic Example

This example shows how patterns work with different reasoning approaches:

```yaml
# Configuration for two agents with different reasoning
agents:
  # Rule-based agent
  rule_agent:
    class: "agents.rule_based.RuleAgent"
    reasoning:
      type: "rule_based"
    patterns:
      request_response:
        options:
          timeout: 5000  # Fast response expected
          
  # LLM-based agent
  llm_agent:
    class: "agents.llm.LLMAgent"
    reasoning:
      type: "llm"
      model: "gpt-4"
    patterns:
      request_response:
        options:
          timeout: 30000  # Longer timeout for LLM processing
```

### Implementation

```python
# Both agents use the same pattern interface regardless of reasoning
# The pattern system abstracts away the reasoning implementation

# Rule-based agent (fast, deterministic)
class RuleAgent(Agent):
    async def handle_request(self, request):
        # Extract parameters
        params = request.get("content", {})
        
        # Apply rules to determine response
        response = self.rule_engine.apply_rules(params)
        
        return response

# LLM-based agent (more complex reasoning)
class LLMAgent(Agent):
    async def handle_request(self, request):
        # Extract parameters
        params = request.get("content", {})
        
        # Prepare prompt for LLM
        prompt = self._create_prompt(params)
        
        # Get response from LLM
        llm_response = await self.llm_service.complete(prompt)
        
        # Process and format response
        response = self._process_llm_response(llm_response)
        
        return response
```

## Conclusion

These examples demonstrate how to use OpenMAS communication patterns in various scenarios. The patterns provide a consistent, protocol-agnostic way for agents to communicate, regardless of their underlying implementation or reasoning approach.

Key benefits illustrated by these examples:

1. **Configuration-Driven**: Patterns are defined through configuration rather than code
2. **Protocol Independence**: The same patterns work across different protocols
3. **Reasoning Agnosticism**: Patterns work with any reasoning approach
4. **Topology Integration**: Patterns align with agent organizational structures
5. **Flexibility**: Patterns can be combined and adapted to various needs

# A2A Implementation in OpenMAS

## Overview

This document outlines the technical implementation of the Agent-to-Agent (A2A) protocol in OpenMAS, focusing on the core components, integration with the framework, and best practices for developers.

## Implementation Architecture

OpenMAS implements A2A support through specialized communicator components that handle the protocol-specific messaging while maintaining reasoning agnosticism.

```
┌───────────────────────────────────────────────┐
│                OpenMAS Agent                  │
└───────────────┬───────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────┐
│               A2A Communicator                │
│                                               │
│  ┌───────────────┐      ┌──────────────────┐  │
│  │ A2AHttpCommunicator│ │ A2AWsCommunicator│  │
│  └───────────────┘      └──────────────────┘  │
└───────────────┬───────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────┐
│                Other A2A Agents               │
└───────────────────────────────────────────────┘
```

## Core Components

### A2A Communicator

```python
class A2AHttpCommunicator(BaseCommunicator):
    """A2A communicator over HTTP transport."""

    async def setup(self) -> None:
        """Initialize the communicator."""
        await super().setup()

        # Set up A2A components
        self.agent_card = self._generate_agent_card()
        self.message_factory = A2AMessageFactory()
        self.task_manager = A2ATaskManager()

        # Set up HTTP server
        self.app = web.Application()
        self._setup_routes()
        host = self.config.options.get("host", "localhost")
        port = self.config.options.get("port", 8080)
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = web.TCPSite(self.runner, host, port)
        await self.site.start()

        self.logger.info(f"A2A HTTP server running on http://{host}:{port}")

    def _setup_routes(self) -> None:
        """Set up HTTP routes."""
        self.app.router.add_get("/.well-known/agent.json", self._handle_agent_card)
        self.app.router.add_get("/a2a/capabilities", self._handle_list_capabilities)
        self.app.router.add_post("/a2a/tasks", self._handle_task_request)
        self.app.router.add_get("/a2a/tasks/{task_id}", self._handle_task_status)
```

### A2A Client

```python
class A2AClient:
    """Client for interacting with other A2A agents."""

    async def setup(self):
        """Set up the A2A client."""
        self.session = aiohttp.ClientSession()
        self.agent_id = str(uuid.uuid4())

    async def submit_task(self, agent_url: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a task to an agent."""
        if not self.session:
            await self.setup()

        async with self.session.post(
            f"{agent_url}/a2a/tasks",
            headers={"X-A2A-Agent-ID": self.agent_id},
            json=task_data
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to submit task: {response.status}")

    async def get_agent_card(self, agent_url: str) -> Dict[str, Any]:
        """Get agent card from an agent."""
        if not self.session:
            await self.setup()

        async with self.session.get(
            f"{agent_url}/.well-known/agent.json"
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Failed to get agent card: {response.status}")
```

## Agent Card Implementation

```python
class AgentCardGenerator:
    """Generator for A2A agent cards."""

    def __init__(self, agent):
        self.agent = agent

    def generate(self) -> Dict[str, Any]:
        """Generate an agent card."""
        return {
            "name": self.agent.name,
            "description": self.agent.description,
            "version": self.agent.version,
            "contact": {
                "name": self.agent.config.get("contact_name", ""),
                "email": self.agent.config.get("contact_email", "")
            },
            "capabilities": self._generate_capabilities(),
            "features": self._generate_features(),
            "authentication": self._generate_authentication_info()
        }

    def _generate_capabilities(self) -> List[Dict[str, Any]]:
        """Generate capability definitions."""
        capabilities = []
        for cap_name, cap_info in self.agent.capabilities.items():
            capability = {
                "name": cap_name,
                "description": cap_info.get("description", ""),
                "parameters": cap_info.get("parameters", {}),
                "returns": cap_info.get("returns", {}),
                "examples": cap_info.get("examples", [])
            }
            capabilities.append(capability)
        return capabilities

    def _generate_features(self) -> Dict[str, bool]:
        """Generate feature support information."""
        return {
            "streaming": self.agent.config.get("supports_streaming", False),
            "push_notifications": self.agent.config.get("supports_push", False),
            "binary_data": self.agent.config.get("supports_binary", True),
            "rate_limiting": self.agent.config.get("rate_limiting_enabled", True)
        }

    def _generate_authentication_info(self) -> Dict[str, Any]:
        """Generate authentication information."""
        auth_config = self.agent.config.get("authentication", {})
        auth_info = {
            "required": auth_config.get("required", False),
            "types": auth_config.get("types", ["bearer"])
        }
        if auth_config.get("oauth_endpoint"):
            auth_info["oauth_endpoint"] = auth_config["oauth_endpoint"]
        return auth_info
```

## Task Management

```python
class A2ATaskManager:
    """Manager for A2A tasks."""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.tasks = {}
        self.storage_type = self.config.get("storage", "memory")

        if self.storage_type == "memory":
            self.storage = InMemoryTaskStorage()
        elif self.storage_type == "redis":
            self.storage = RedisTaskStorage(self.config.get("redis_url"))
        else:
            raise ValueError(f"Unknown storage type: {self.storage_type}")

    async def create_task(self, task_data: Dict[str, Any]) -> str:
        """Create a new task."""
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "data": task_data,
            "result": None,
            "error": None
        }

        await self.storage.save_task(task_id, task)
        return task_id

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID."""
        return await self.storage.get_task(task_id)

    async def update_task(self, task_id: str, updates: Dict[str, Any]) -> None:
        """Update a task."""
        task = await self.storage.get_task(task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")

        task.update(updates)
        task["updated_at"] = datetime.now().isoformat()
        await self.storage.save_task(task_id, task)

    async def complete_task(self, task_id: str, result: Any) -> None:
        """Mark a task as completed with a result."""
        await self.update_task(task_id, {"status": "completed", "result": result})

    async def fail_task(self, task_id: str, error: str) -> None:
        """Mark a task as failed with an error."""
        await self.update_task(task_id, {"status": "failed", "error": error})
```

## Message Handling

```python
class A2AMessageHandler:
    """Handler for A2A messages."""

    def __init__(self, agent, task_manager: A2ATaskManager):
        self.agent = agent
        self.task_manager = task_manager

    async def handle_task_request(self, request: web.Request) -> web.Response:
        """Handle a task request."""
        try:
            data = await request.json()

            # Validate the request
            if not self._validate_task_request(data):
                return web.json_response(
                    {"error": "Invalid task request"},
                    status=400
                )

            # Create the task
            task_id = await self.task_manager.create_task(data)

            # Process the task asynchronously
            asyncio.create_task(self._process_task(task_id, data))

            return web.json_response({
                "task_id": task_id,
                "status": "accepted"
            })
        except Exception as e:
            return web.json_response(
                {"error": str(e)},
                status=500
            )

    async def _process_task(self, task_id: str, data: Dict[str, Any]) -> None:
        """Process a task asynchronously."""
        try:
            # Extract task information
            capability = data.get("capability")
            input_data = data.get("input_data", {})

            # Check if the agent supports the capability
            if capability not in self.agent.capabilities:
                await self.task_manager.fail_task(
                    task_id,
                    f"Capability not supported: {capability}"
                )
                return

            # Execute the capability
            result = await self.agent.execute_capability(capability, input_data)

            # Complete the task
            await self.task_manager.complete_task(task_id, result)
        except Exception as e:
            # Fail the task on error
            await self.task_manager.fail_task(task_id, str(e))
```

## Capability Definition

```python
def a2a_capability(description=None, parameters=None, returns=None, examples=None):
    """Decorator to define an A2A capability."""
    def decorator(func):
        # Extract parameter information from function signature
        sig = inspect.signature(func)
        param_schema = parameters or {}

        # If no parameter schema was provided, generate one from the function signature
        if not param_schema:
            for name, param in sig.parameters.items():
                if name == 'self':
                    continue

                param_type = param.annotation
                if param_type is inspect.Parameter.empty:
                    param_type = "string"
                else:
                    param_type = _map_python_type_to_json_schema(param_type)

                param_schema[name] = {
                    "type": param_type,
                    "required": param.default is inspect.Parameter.empty
                }

        # Extract return type information
        return_schema = returns or {}
        if not return_schema and func.__annotations__.get('return'):
            return_type = func.__annotations__['return']
            return_schema = _map_python_type_to_json_schema_object(return_type)

        # Build the capability metadata
        capability_meta = {
            "description": description or func.__doc__ or "",
            "parameters": param_schema,
            "returns": return_schema,
            "examples": examples or []
        }

        # Attach metadata to the function
        func.__a2a_capability__ = capability_meta

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
```

## Integrating with OpenMAS Agents

```python
class A2AAgentMixin:
    """Mixin to add A2A protocol capabilities to an agent."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.capabilities = {}
        self.a2a_client = None

    async def setup(self):
        """Set up the A2A agent."""
        if hasattr(super(), 'setup'):
            await super().setup()

        # Initialize A2A client
        self.a2a_client = A2AClient()
        await self.a2a_client.setup()

        # Register capabilities from methods with @a2a_capability decorator
        for name, method in inspect.getmembers(self, inspect.ismethod):
            if hasattr(method, '__a2a_capability__'):
                self.capabilities[name] = method.__a2a_capability__

    async def execute_capability(self, capability_name, input_data):
        """Execute a capability by name."""
        if capability_name not in self.capabilities:
            raise ValueError(f"Capability not found: {capability_name}")

        method = getattr(self, capability_name)
        return await method(**input_data)

    async def delegate_task(self, agent_url, capability, input_data):
        """Delegate a task to another agent."""
        task_data = {
            "name": f"Task for {capability}",
            "description": f"Task delegated from {self.agent_id}",
            "input_data": input_data,
            "requesting_agent": self.agent_id,
            "capability": capability
        }

        result = await self.a2a_client.submit_task(agent_url, task_data)
        return result["task_id"]

    async def wait_for_task_completion(self, agent_url, task_id, timeout=None):
        """Wait for a task to complete."""
        start_time = time.time()
        while timeout is None or (time.time() - start_time) < timeout:
            task_status = await self.a2a_client.get_task_status(agent_url, task_id)

            if task_status["status"] in ["completed", "failed"]:
                return task_status

            await asyncio.sleep(1)

        raise TimeoutError(f"Task timed out: {task_id}")
```

## Configuration Example

> **Note**: This example is for illustration purposes only. For the complete and definitive schema, please refer to the [unified configuration schema](/03_configuration/unified_configuration_schema.md) document.

```yaml
# A2A agent configuration example
agent:
  name: "assistant_agent"
  type: "a2a"
  description: "An assistant agent with A2A capabilities"
  version: "1.0.0"
  contact:
    name: "OpenMAS Team"
    email: "info@openmas.org"

  capabilities:
    - name: "answer_question"
      description: "Answer a question using the agent's knowledge"
    - name: "search_web"
      description: "Search the web for information"

  communication:
    protocol: "a2a"
    transport: "http"
    host: "0.0.0.0"
    port: 8080

  authentication:
    required: true
    types: ["bearer", "basic"]

  features:
    streaming: true
    push_notifications: false
    binary_data: true
```

## Usage Example

```python
class TravelPlannerAgent(BaseAgent, A2AAgentMixin):

    @a2a_capability(
        description="Plan a travel itinerary",
        examples=[{"input": {"destination": "Paris"}, "output": {"days": 3}}]
    )
    async def plan_itinerary(self, destination: str, days: int = 3) -> Dict[str, Any]:
        """Plan a travel itinerary for the specified destination."""
        # Implementation
        return {"destination": destination, "days": days, "plan": [...]}

    async def plan_trip(self, user_query):
        """Plan a trip by coordinating with other agents."""
        # Get weather forecasts from a weather agent
        weather_agent_url = "http://weather-agent.example.com"
        weather_task_id = await self.delegate_task(
            weather_agent_url,
            "get_weather_forecast",
            {"location": user_query["destination"]}
        )

        # Get flight information from a travel agent
        travel_agent_url = "http://travel-agent.example.com"
        flight_task_id = await self.delegate_task(
            travel_agent_url,
            "find_flights",
            {"from": user_query["departure"], "to": user_query["destination"]}
        )

        # Wait for both tasks to complete
        weather_result = await self.wait_for_task_completion(weather_agent_url, weather_task_id)
        flight_result = await self.wait_for_task_completion(travel_agent_url, flight_task_id)

        # Combine the results
        return {
            "weather": weather_result["result"],
            "flights": flight_result["result"],
            "itinerary": await self.plan_itinerary(
                user_query["destination"],
                user_query.get("days", 3)
            )
        }
```

## Performance Considerations

OpenMAS implements these performance optimizations for A2A:

1. **Asynchronous Processing**: Tasks are processed asynchronously
2. **Connection Pooling**: HTTP connections are pooled for better performance
3. **Task Batching**: Multiple related tasks can be batched for efficiency
4. **Distributed Task Processing**: Tasks can be distributed across a cluster
5. **Caching**: Common resources and results are cached

## Security Considerations

The A2A implementation in OpenMAS includes these security features:

1. **Authentication**: Support for multiple authentication methods
2. **Authorization**: Capability-level access control
3. **Input Validation**: All inputs are validated against schemas
4. **Rate Limiting**: Protection against excessive requests
5. **CORS Protection**: Security headers for web-based access

## References

- [A2A Protocol Documentation](/refactoring_work/00b_overview/02_protocols/a2a/a2a_protocol.md)
- [Protocol Integration Guide](/refactoring_work/00b_overview/02_protocols/protocol_integration_guide.md)
- [Unified Configuration Schema](/03_configuration/unified_configuration_schema.md)
- [Agent Architecture](/refactoring_work/00b_overview/04_agents/architecture.md)
- [Multi-Protocol Support](/refactoring_work/00b_overview/02_protocols/multi_protocol_support.md)

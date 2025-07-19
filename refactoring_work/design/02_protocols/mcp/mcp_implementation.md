# MCP Implementation in OpenMAS

This document details the specific implementation of the Model Context Protocol (MCP) within OpenMAS, focusing on the internal architecture and integration points.

## Implementation Architecture

OpenMAS implements MCP support through specialized communicator components that handle the protocol-specific messaging while maintaining reasoning agnosticism.

### Communicator Components

```
┌───────────────────────────────────────────────┐
│                OpenMAS Agent                  │
└───────────────┬───────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────┐
│              McpCommunicator                  │
│                                               │
│  ┌───────────────┐      ┌──────────────────┐  │
│  │McpSseCommunicator│   │McpStdioCommunicator│ │
│  └───────────────┘      └──────────────────┘  │
└───────────────┬───────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────┐
│            External MCP Environment            │
└───────────────────────────────────────────────┘
```

#### MCP Base Communicator

```python
class McpCommunicator(BaseCommunicator):
    """Base class for MCP communicators in OpenMAS."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.tools_registry = ToolsRegistry()
        self.resources_registry = ResourcesRegistry()
        self.session_manager = SessionManager()
    
    async def setup(self) -> None:
        """Set up the MCP communicator."""
        # Register standard tools
        await self._register_standard_tools()
        
        # Set up resource providers
        await self._setup_resource_providers()
    
    async def _register_standard_tools(self) -> None:
        """Register standard MCP tools."""
        # Implementation details for standard tool registration
        pass
    
    async def _setup_resource_providers(self) -> None:
        """Set up resource providers for MCP resources."""
        # Implementation details for resource provider setup
        pass
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process an MCP message."""
        # Implementation details for MCP message processing
        pass
```

#### Server-Sent Events (SSE) Communicator

```python
class McpSseCommunicator(McpCommunicator):
    """MCP communicator over Server-Sent Events."""
    
    async def setup(self) -> None:
        """Initialize the SSE communicator."""
        await super().setup()
        self.sse_client = SseClient(self.config.get("sse_url"))
        
    async def start(self) -> None:
        """Start the SSE communicator."""
        await self.sse_client.connect()
        self.sse_client.on_message(self._handle_sse_message)
        
    async def _handle_sse_message(self, message: str) -> None:
        """Handle an incoming SSE message."""
        parsed_message = json.loads(message)
        response = await self.process_message(parsed_message)
        await self.sse_client.send(json.dumps(response))
```

#### Standard I/O Communicator

```python
class McpStdioCommunicator(McpCommunicator):
    """MCP communicator over Standard I/O."""
    
    async def setup(self) -> None:
        """Initialize the STDIO communicator."""
        await super().setup()
        self.stdin_reader = asyncio.StreamReader()
        self.stdout_writer = None  # Set during start()
        
    async def start(self) -> None:
        """Start the STDIO communicator."""
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        
        w_transport, w_protocol = await loop.connect_write_pipe(
            asyncio.streams.FlowControlMixin, sys.stdout
        )
        self.stdout_writer = asyncio.StreamWriter(w_transport, w_protocol, None, loop)
        
        # Start listening for messages
        self._listen_task = asyncio.create_task(self._listen_for_messages(reader))
        
    async def _listen_for_messages(self, reader: asyncio.StreamReader) -> None:
        """Listen for messages on stdin."""
        while True:
            line = await reader.readline()
            if not line:  # EOF
                break
                
            try:
                message = json.loads(line.decode('utf-8'))
                response = await self.process_message(message)
                await self._send_response(response)
            except json.JSONDecodeError:
                # Log error and continue
                logging.error(f"Failed to decode message: {line}")
                
    async def _send_response(self, response: Dict[str, Any]) -> None:
        """Send a response to stdout."""
        response_json = json.dumps(response)
        self.stdout_writer.write(f"{response_json}\n".encode('utf-8'))
        await self.stdout_writer.drain()
```

## Resource Management

OpenMAS implements MCP resources as first-class entities that can be referenced and processed by tools and agents.

### Resource Base Class

```python
class McpResource:
    """Base class for MCP resources in OpenMAS."""
    
    def __init__(self, resource_id: str, metadata: Dict[str, Any] = None):
        self.resource_id = resource_id
        self.metadata = metadata or {}
    
    async def get_content(self) -> Any:
        """Get the content of the resource."""
        raise NotImplementedError("Subclasses must implement this method.")
    
    def to_mcp_resource(self) -> Dict[str, Any]:
        """Convert to MCP resource format."""
        return {
            "id": self.resource_id,
            "type": self.get_resource_type(),
            "metadata": self.metadata
        }
    
    def get_resource_type(self) -> str:
        """Get the MCP resource type."""
        raise NotImplementedError("Subclasses must implement this method.")
```

### Resource Types

OpenMAS implements these specific resource types:

```python
class TextResource(McpResource):
    """Text resource in MCP."""
    
    def __init__(self, resource_id: str, text: str, metadata: Dict[str, Any] = None):
        super().__init__(resource_id, metadata)
        self._text = text
    
    async def get_content(self) -> str:
        """Get the text content."""
        return self._text
    
    def get_resource_type(self) -> str:
        """Get the MCP resource type."""
        return "text"


class FileResource(McpResource):
    """File resource in MCP."""
    
    def __init__(self, resource_id: str, path: str, metadata: Dict[str, Any] = None):
        super().__init__(resource_id, metadata)
        self._path = path
    
    async def get_content(self) -> bytes:
        """Get the file content."""
        async with aiofiles.open(self._path, "rb") as f:
            return await f.read()
    
    def get_resource_type(self) -> str:
        """Get the MCP resource type."""
        return "file"


class UrlResource(McpResource):
    """URL resource in MCP."""
    
    def __init__(self, resource_id: str, url: str, metadata: Dict[str, Any] = None):
        super().__init__(resource_id, metadata)
        self._url = url
        self._client = httpx.AsyncClient()
    
    async def get_content(self) -> str:
        """Get the URL content."""
        response = await self._client.get(self._url)
        response.raise_for_status()
        return response.text
    
    def get_resource_type(self) -> str:
        """Get the MCP resource type."""
        return "url"
```

## Tool Management

OpenMAS implements MCP tools as modular, self-contained components that can be registered with an agent.

### Tool Registration

```python
class ToolsRegistry:
    """Registry for MCP tools."""
    
    def __init__(self):
        self.tools = {}
        self.categories = defaultdict(list)
    
    def register_tool(self, tool: Tool) -> None:
        """Register a tool with the registry."""
        self.tools[tool.name] = tool
        
        # Add to categories
        for category in tool.categories:
            self.categories[category].append(tool.name)
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Get all tools in a category."""
        tool_names = self.categories.get(category, [])
        return [self.tools[name] for name in tool_names]
    
    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools."""
        return list(self.tools.values())
    
    def get_tool_schema(self) -> Dict[str, Any]:
        """Get the schema for all registered tools."""
        tool_schemas = []
        for tool in self.tools.values():
            tool_schemas.append(tool.to_schema())
        return {"tools": tool_schemas}
```

### Tool Base Class

```python
class Tool:
    """Base class for MCP tools."""
    
    def __init__(self, name: str, description: str, categories: List[str] = None):
        self.name = name
        self.description = description
        self.categories = categories or ["default"]
        self.parameters_schema = {}
        self.returns_schema = {}
    
    def set_parameters_schema(self, schema: Dict[str, Any]) -> None:
        """Set the parameters schema for the tool."""
        self.parameters_schema = schema
    
    def set_returns_schema(self, schema: Dict[str, Any]) -> None:
        """Set the returns schema for the tool."""
        self.returns_schema = schema
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with the given parameters."""
        raise NotImplementedError("Subclasses must implement this method.")
    
    def to_schema(self) -> Dict[str, Any]:
        """Convert the tool to a schema representation."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema,
            "returns": self.returns_schema,
            "categories": self.categories
        }
```

## Session Management

OpenMAS implements session management for MCP to maintain state across interactions.

```python
class SessionManager:
    """Manager for MCP sessions."""
    
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, session_id: str = None) -> str:
        """Create a new session."""
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "created_at": datetime.now().isoformat(),
            "state": {},
            "last_activity": datetime.now().isoformat()
        }
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID."""
        session = self.sessions.get(session_id)
        if session:
            # Update last activity
            session["last_activity"] = datetime.now().isoformat()
        return session
    
    def update_session_state(self, session_id: str, state_updates: Dict[str, Any]) -> None:
        """Update the state of a session."""
        session = self.get_session(session_id)
        if session:
            session["state"].update(state_updates)
            session["last_activity"] = datetime.now().isoformat()
    
    def end_session(self, session_id: str) -> None:
        """End a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
```

## Message Processing Pipeline

OpenMAS implements a structured pipeline for processing MCP messages:

```
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│ Receive   │    │ Validate  │    │ Deserialize│    │ Route to  │
│ Message   │───►│ Message   │───►│ Message    │───►│ Handler   │
└───────────┘    └───────────┘    └───────────┘    └───────────┘
                                                         │
                                                         ▼
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│ Send      │    │ Serialize │    │ Transform │    │ Process   │
│ Response  │◄───│ Response  │◄───│ Result    │◄───│ Request   │
└───────────┘    └───────────┘    └───────────┘    └───────────┘
```

### Message Handler

```python
class McpMessageHandler:
    """Handler for MCP messages."""
    
    def __init__(self, tools_registry: ToolsRegistry, resources_registry: ResourcesRegistry,
                 session_manager: SessionManager):
        self.tools_registry = tools_registry
        self.resources_registry = resources_registry
        self.session_manager = session_manager
        
        # Register message type handlers
        self.handlers = {
            "tool_call": self._handle_tool_call,
            "resource_request": self._handle_resource_request,
            "session_command": self._handle_session_command,
            "schema_request": self._handle_schema_request
        }
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP message."""
        # Validate message
        if not self._validate_message(message):
            return {"error": "Invalid message format"}
            
        # Extract message type and data
        message_type = message.get("type")
        message_data = message.get("data", {})
        
        # Get session
        session_id = message.get("session_id")
        if not session_id:
            session_id = self.session_manager.create_session()
        elif not self.session_manager.get_session(session_id):
            # Create the session if it doesn't exist
            self.session_manager.create_session(session_id)
            
        # Handle the message with the appropriate handler
        handler = self.handlers.get(message_type)
        if handler:
            response = await handler(message_data, session_id)
        else:
            response = {"error": f"Unknown message type: {message_type}"}
            
        # Add session ID to response
        response["session_id"] = session_id
        
        return response
    
    def _validate_message(self, message: Dict[str, Any]) -> bool:
        """Validate an MCP message."""
        # Minimum validation: the message must be a dict with a 'type' field
        return isinstance(message, dict) and "type" in message
    
    async def _handle_tool_call(self, data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle a tool call message."""
        tool_name = data.get("tool")
        tool_params = data.get("parameters", {})
        
        tool = self.tools_registry.get_tool(tool_name)
        if not tool:
            return {"error": f"Unknown tool: {tool_name}"}
            
        try:
            result = await tool.execute(tool_params)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_resource_request(self, data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle a resource request message."""
        resource_id = data.get("resource_id")
        resource = self.resources_registry.get_resource(resource_id)
        
        if not resource:
            return {"error": f"Unknown resource: {resource_id}"}
            
        try:
            content = await resource.get_content()
            return {"resource": resource.to_mcp_resource(), "content": content}
        except Exception as e:
            return {"error": str(e)}
    
    async def _handle_session_command(self, data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle a session command message."""
        command = data.get("command")
        
        if command == "start":
            # Session already started during message handling
            return {"status": "session_started"}
        elif command == "end":
            self.session_manager.end_session(session_id)
            return {"status": "session_ended"}
        elif command == "update_state":
            state_updates = data.get("state", {})
            self.session_manager.update_session_state(session_id, state_updates)
            return {"status": "state_updated"}
        else:
            return {"error": f"Unknown session command: {command}"}
    
    async def _handle_schema_request(self, data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle a schema request message."""
        schema_type = data.get("schema_type")
        
        if schema_type == "tools":
            return {"schema": self.tools_registry.get_tool_schema()}
        elif schema_type == "resources":
            return {"schema": self.resources_registry.get_resource_schema()}
        else:
            return {"error": f"Unknown schema type: {schema_type}"}
```

## Integration with OpenMAS Architecture

The MCP implementation in OpenMAS follows the reasoning agnostic design principles:

1. **Clean Separation** - MCP communicators handle protocol-specific details while providing a reasoning-agnostic interface to agent cores
2. **Protocol Independence** - The agent core interacts with the MCP communicator through the standardized OpenMAS communicator interface
3. **Multi-Protocol Support** - MCP can be used alongside other protocols in the same agent instance

### Agent Integration Example

> **Note**: This example is for illustration purposes only. For the complete and definitive schema, please refer to the [unified configuration schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md) document.

```python
class LLMAgent(Agent):
    async def setup(self):
        # Register MCP communicator with appropriate configuration
        mcp_config = {
            "protocol": "mcp",
            "transport": "sse",
            "sse_url": "http://localhost:8080/mcp",
            "tools": ["weather", "calculator", "web_search"]
        }
        
        self.mcp_communicator = await self.register_communicator(
            "mcp", 
            McpSseCommunicator, 
            mcp_config
        )
        
        # The agent can now receive and send MCP messages
        self.mcp_communicator.on_message(self.handle_mcp_message)
        
    async def handle_mcp_message(self, message):
        # Process MCP message according to the agent's reasoning approach
        # This implementation will vary based on the agent's reasoning type
        response = await self.reasoning_engine.process_message(message)
        await self.mcp_communicator.send_message(response)
```

## Performance Optimizations

OpenMAS implements these performance optimizations for MCP:

1. **Request Batching** - Multiple tool calls can be batched when appropriate
2. **Resource Caching** - Common resources are cached to avoid redundant access
3. **Connection Pooling** - HTTP connections are pooled for URL resources
4. **Streaming Support** - Large resources or responses are streamed to avoid memory issues
5. **Asynchronous Processing** - All operations are asynchronous for optimal performance

## Security Considerations

The MCP implementation in OpenMAS includes these security features:

1. **Input Validation** - All inputs are validated against schemas
2. **Resource Isolation** - Resources are isolated with proper access controls
3. **Tool Authorization** - Tools can define authorization requirements
4. **Rate Limiting** - Protection against excessive tool usage
5. **Secure Defaults** - Secure defaults for all configurations

## References

- [MCP Protocol Documentation](/refactoring_work/00b_overview/02_protocols/mcp/mcp_protocol.md)
- [Protocol Integration Guide](/refactoring_work/00b_overview/02_protocols/protocol_integration_guide.md)
- [Unified Configuration Schema](/refactoring_work/00b_overview/03_configuration/unified_configuration_schema.md)
- [Agent Architecture](/refactoring_work/00b_overview/04_agents/architecture.md)
- [Multi-Protocol Support](/refactoring_work/00b_overview/02_protocols/multi_protocol_support.md)

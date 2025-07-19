# Extension System Documentation Standard

## Extension Point Definition
- **Name**: [Extension Point Name]
- **Purpose**: [Brief description of extension point's purpose]
- **Component**: [Parent component]
- **Type**: [Type of extension: communicator, agent, asset, prompt, etc.]
- **Community Usage**: [How this extension point serves the community]
- **Protocol Compatibility**: [List of protocols the extension supports: MCP, A2A, etc.]

## Extension Schema
```yaml
# Standardized extension configuration schema
type: object
properties:
  # Extension-specific properties
  extension_type:
    type: string
    description: "The type of extension to use"
    enum: [
      "communicator", 
      "agent", 
      "asset", 
      "prompt", 
      "llm", 
      "reasoning", 
      "protocol", 
      "protocol_adapter",
      "tool"
    ]
  
  # Extension metadata
  metadata:
    type: object
    description: "Extension metadata"
    properties:
      name:
        type: string
        description: "Name of the extension"
      description:
        type: string
        description: "Description of the extension"
      version:
        type: string
        description: "Version of the extension"
      author:
        type: string
        description: "Author of the extension"
      license:
        type: string
        description: "License of the extension"
      tags:
        type: array
        description: "Tags for the extension"
        items:
          type: string
      homepage:
        type: string
        description: "Homepage URL for the extension"
      repository:
        type: string
        description: "Repository URL for the extension"
      documentation:
        type: string
        description: "Documentation URL for the extension"
  
  # Extension configuration
  config:
    type: object
    description: "Configuration for the extension"
    # Extension-specific configuration properties

  # Protocol-specific configuration
  protocols:
    type: object
    description: "Protocol-specific extension configuration"
    properties:
      a2a:
        type: object
        description: "A2A protocol configuration"
        properties:
          enabled:
            type: boolean
            description: "Whether this extension is enabled for A2A protocol"
            default: true
          # A2A-specific extension configuration
      
      mcp:
        type: object
        description: "MCP protocol configuration"
        properties:
          enabled:
            type: boolean
            description: "Whether this extension is enabled for MCP protocol"
            default: true
          # MCP-specific extension configuration

  # Extension interfaces definition
  interfaces:
    type: object
    description: "Interfaces implemented by the extension"
    properties:
      # Protocol-specific interfaces
      protocol_interfaces:
        type: array
        description: "Protocol interfaces implemented by the extension"
        items:
          type: object
          properties:
            protocol:
              type: string
              description: "Protocol name"
              enum: ["mcp", "a2a", "grpc", "mqtt"]
            interface:
              type: string
              description: "Interface name"

  # Extension dependencies
  dependencies:
    type: array
    description: "Extension dependencies"
    items:
      type: object
      properties:
        name:
          type: string
          description: "Name of the dependency"
        version:
          type: string
          description: "Version constraint for the dependency"
        optional:
          type: boolean
          description: "Whether this dependency is optional"
          default: false
      required:
        - name
  
  # Extension requirements
  requirements:
    type: object
    description: "Requirements for using the extension"
    properties:
      openmas_version:
        type: string
        description: "Required OpenMAS version"
      python_version:
        type: string
        description: "Required Python version"
      system_dependencies:
        type: array
        description: "System dependencies"
        items:
          type: string

required:
  - extension_type
  - metadata
```

## Extension Lifecycle
- **Registration**: [How extensions are registered]
- **Discovery**: [How extensions are discovered]
- **Loading**: [How extensions are loaded]
- **Configuration**: [How extensions are configured]
- **Initialization**: [How extensions are initialized]
- **Usage**: [How extensions are used]
- **Deactivation**: [How extensions are deactivated]
- **Unregistration**: [How extensions are unregistered]

## Extension Security
- **Verification**: [How extensions are verified for security]
- **Isolation**: [How extensions are isolated]
- **Permissions**: [How extensions are given permissions]
- **Code Signing**: [How extension code signing works]
- **Vulnerability Scanning**: [How extensions are scanned for vulnerabilities]

## Extension Integration
- **Interface Definition**:
  ```python
  # Interface definition code
  from abc import ABC, abstractmethod
  from typing import Dict, Any, Optional, List
  
  class CommunicatorExtension(ABC):
      """Interface for communicator extensions."""
      
      @abstractmethod
      def setup(self, config: Dict[str, Any]) -> None:
          """Set up the communicator extension.
          
          Args:
              config: Extension configuration
          """
          pass
      
      @abstractmethod
      def shutdown(self) -> None:
          """Clean up resources when shutting down."""
          pass
  ```

## Extension Implementation
- **Example Implementation**:
  ```python
  from typing import Dict, Any, Optional, List
  from openmas.extensions import CommunicatorExtension
  
  class CustomProtocolCommunicator(CommunicatorExtension):
      """A custom protocol communicator extension."""
      
      def __init__(self) -> None:
          self.connection: Optional[Any] = None
      
      def setup(self, config: Dict[str, Any]) -> None:
          """Set up the custom protocol communicator.
          
          Args:
              config: Configuration dictionary
          """
          host: str = config.get('host', 'localhost')
          port: int = config.get('port', 8080)
          timeout: int = config.get('timeout', 30)
          self.connection = self._create_connection(host, port, timeout)
          
          # Register protocol interfaces based on configuration
          if config.get('protocols', {}).get('a2a', {}).get('enabled', False):
              self.register_protocol_interface('a2a', A2AProtocolAdapter(self.connection))
              
          if config.get('protocols', {}).get('mcp', {}).get('enabled', False):
              self.register_protocol_interface('mcp', MCPProtocolAdapter(self.connection))
      
      def shutdown(self) -> None:
          """Clean up resources when shutting down."""
          if self.connection:
              self.connection.close()
              self.connection = None
      
      def _create_connection(self, host: str, port: int, timeout: int) -> Any:
          """Create a connection to the custom protocol server.
          
          Args:
              host: Server hostname
              port: Server port
              timeout: Connection timeout
              
          Returns:
              Connection object
          """
          # Implementation details
          return CustomConnection(host, port, timeout)
  ```

## Protocol-Specific Extension Development

Extensions can support multiple protocols through one of the following approaches:

### 1. Protocol-Agnostic Extensions

Extensions that are protocol-agnostic work with any protocol by:
- Implementing a core interface that can be exposed through multiple protocols
- Using the unified asset/resource mapping system for content handling
- Maintaining separation between functionality and communication

```python
from typing import Dict, Any, List, Optional, Union
from openmas.extensions import extension, Extension

@extension(
    name="data_analyzer",
    protocols=["mcp", "a2a"]
)
class DataAnalyzer(Extension):
    """Analyzes data regardless of protocol."""
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Core functionality exposed through multiple protocols.
        
        Args:
            data: The data to analyze
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        # Implementation not tied to any specific protocol
        results: Dict[str, Any] = {}
        # ... analysis logic ...
        return results
```

### 2. Protocol-Specific Extensions

Extensions that are protocol-specific:
- Implement functionality for a specific protocol
- Register only with compatible communicators
- Can be bridged to other protocols using protocol adapters

```python
from typing import Dict, Any, List, Optional, Union, cast
from openmas.extensions import extension, Extension
from openmas.protocols.mcp import McpResource, McpResourceProvider

@extension(
    name="mcp_resource_provider",
    protocols=["mcp"]
)
class McpResourceProvider(Extension, McpResourceProvider):
    """Provides MCP-specific resources."""
    
    def get_resource(self, resource_id: str) -> Optional[McpResource]:
        """MCP-specific implementation.
        
        Args:
            resource_id: ID of the resource to retrieve
            
        Returns:
            Optional[McpResource]: The resource if found
        """
        # Implementation uses MCP-specific concepts
        return self._resource_store.get(resource_id)
```

### 3. Multi-Protocol Adapters

Extension adapters that enable protocol compatibility:
- Translate between different protocol interfaces
- Handle protocol-specific configuration
- Map capabilities between protocol formats

```python
from typing import Dict, Any, List, Optional, Union, cast
from openmas.extensions import extension, Extension
from openmas.protocols.mqtt import MqttMessage
from openmas.protocols.mcp import McpMessage, McpContentType

@extension(
    name="mqtt_to_mcp_adapter",
    type="protocol_adapter",
    source_protocol="mqtt",
    target_protocol="mcp"
)
class MqttToMcpAdapter(Extension):
    """Adapts MQTT messages to MCP format."""
    
    def adapt(self, mqtt_message: MqttMessage) -> McpMessage:
        """Convert MQTT message to MCP format.
        
        Args:
            mqtt_message: The MQTT message to convert
            
        Returns:
            McpMessage: Converted MCP message
        """
        # Implementation of protocol adaptation
        content_type: McpContentType = self._determine_content_type(mqtt_message)
        return McpMessage(
            content=mqtt_message.payload,
            content_type=content_type,
            metadata={
                "mqtt_topic": mqtt_message.topic,
                "mqtt_qos": mqtt_message.qos
            }
        )
        
    def _determine_content_type(self, mqtt_message: MqttMessage) -> McpContentType:
        """Determine MCP content type from MQTT message.
        
        Args:
            mqtt_message: MQTT message
            
        Returns:
            McpContentType: Appropriate content type
        """
        # Logic to determine content type
        if mqtt_message.content_type == "application/json":
            return McpContentType.JSON
        return McpContentType.TEXT
```

### 4. Protocol Discovery and Dynamic Adaptation

Extensions can discover available protocols at runtime and adapt accordingly:

```python
from typing import Dict, Any, List, Optional, cast
from openmas.extensions import extension, Extension
from openmas.protocols import ProtocolRegistry, Protocol

@extension(
    name="adaptive_extension"
)
class AdaptiveExtension(Extension):
    """Extension that adapts to available protocols."""
    
    def __init__(self) -> None:
        self.protocol_registry = ProtocolRegistry()
        self.supported_protocols: List[str] = []
        
    async def setup(self) -> None:
        """Discover available protocols and adapt."""
        # Discover available protocols
        available_protocols: List[Protocol] = await self.protocol_registry.discover_protocols()
        
        for protocol in available_protocols:
            if self._supports_protocol(protocol.name):
                self.supported_protocols.append(protocol.name)
                adapter = self._create_adapter_for_protocol(protocol)
                self.register_protocol_adapter(protocol.name, adapter)
                
    def _supports_protocol(self, protocol_name: str) -> bool:
        """Check if this extension supports a protocol.
        
        Args:
            protocol_name: Name of the protocol
            
        Returns:
            bool: True if supported
        """
        # Implementation to check protocol support
        return protocol_name in ["mcp", "a2a", "mqtt"]
```

### 5. Extension Composition

Extensions can be composed together to provide capabilities across different protocols:

```python
from typing import Dict, Any, List, Optional, cast
from openmas.extensions import extension, Extension, ExtensionComposition

@extension(
    name="composite_extension"
)
class CompositeExtension(ExtensionComposition):
    """Combines multiple extensions across protocols."""
    
    def __init__(self) -> None:
        super().__init__()
        # Add child extensions
        self.add_extension("data_analyzer", DataAnalyzer())
        self.add_extension("mcp_resource_provider", McpResourceProvider())
        
    async def process_request(self, protocol: str, request: Any) -> Any:
        """Process a request using the appropriate extension.
        
        Args:
            protocol: Protocol name
            request: The request object
            
        Returns:
            Any: Response from the appropriate extension
        """
        # Route to appropriate extension based on protocol
        if protocol == "mcp" and isinstance(request, dict) and "resource_id" in request:
            extension = self.get_extension("mcp_resource_provider")
            return await extension.get_resource(request["resource_id"])
        
        # Default to data analyzer for other requests
        extension = self.get_extension("data_analyzer")
        return await extension.analyze(request)
```

### 6. Default Implementations

The framework provides default implementations for common patterns:

```python
from openmas.extensions.defaults import (
    DefaultProtocolAdapter,
    DefaultMultiProtocolExtension,
    DefaultResourceProvider
)
from typing import Dict, Any

class MyExtension(DefaultMultiProtocolExtension):
    """Extension using default implementations."""
    
    def __init__(self) -> None:
        super().__init__()
        # Default implementations handle most protocol interactions
        # Just override specific methods as needed
        
    async def handle_request(self, protocol: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a request from any protocol.
        
        Args:
            protocol: Protocol name
            request: The request data
            
        Returns:
            Dict[str, Any]: Response data
        """
        # Custom logic here
        return {"status": "success"}
```

## Extension Testing Across Protocols

When testing extensions that support multiple protocols:

1. **Unit Tests**:
   - Test core functionality independent of protocol
   - Mock protocol-specific interfaces

```python
import pytest
from unittest.mock import MagicMock
from typing import Dict, Any

def test_data_analyzer_core_functionality():
    """Test the core functionality without protocol dependencies."""
    analyzer = DataAnalyzer()
    result = analyzer.analyze({"data": [1, 2, 3]})
    assert "mean" in result
    assert result["mean"] == 2.0
```

2. **Integration Tests**:
   - Test with each supported protocol separately
   - Verify consistent behavior across protocols
   - Test protocol-specific edge cases

```python
import pytest
from openmas.protocols.mcp import McpClient
from openmas.protocols.a2a import A2AClient

@pytest.mark.integration
@pytest.mark.parametrize("protocol,client_cls", [
    ("mcp", McpClient),
    ("a2a", A2AClient),
])
async def test_extension_with_real_protocols(protocol: str, client_cls: Any):
    """Test extension with real protocol implementations."""
    client = client_cls()
    await client.connect()
    
    # Same request through different protocol clients should yield equivalent results
    result = await client.invoke_extension(
        "data_analyzer",
        "analyze",
        {"data": [1, 2, 3]}
    )
    
    assert "mean" in result
    assert result["mean"] == 2.0
    
    await client.disconnect()
```

3. **Extension Registration Tests**:
   - Verify extension properly registers with appropriate communicators
   - Test capability exposure for each protocol

```python
import pytest
from openmas.extensions import ExtensionRegistry

async def test_extension_registration():
    """Test that extension registers properly with protocols."""
    registry = ExtensionRegistry()
    extension = DataAnalyzer()
    
    await registry.register(extension)
    
    # Check registration with each protocol
    assert registry.is_registered_with_protocol("data_analyzer", "mcp")
    assert registry.is_registered_with_protocol("data_analyzer", "a2a")
    
    # Check capability exposure
    mcp_capabilities = registry.get_capabilities("data_analyzer", "mcp")
    assert "analyze" in [cap["name"] for cap in mcp_capabilities]
    
    a2a_capabilities = registry.get_capabilities("data_analyzer", "a2a")
    assert "analyze" in [cap["name"] for cap in a2a_capabilities]
```

## Extension Packaging and Publishing

- **Package Structure**:
  ```
  my-extension/
  ├── pyproject.toml
  ├── README.md
  ├── LICENSE
  ├── src/
  │   └── openmas_ext_myextension/
  │       ├── __init__.py
  │       ├── extension.py
  │       └── protocols/
  │           ├── __init__.py
  │           ├── a2a.py
  │           └── mcp.py
  └── tests/
      ├── __init__.py
      ├── test_extension.py
      └── test_protocols/
          ├── __init__.py
          ├── test_a2a.py
          └── test_mcp.py
  ```

- **Registration Manifest**:
  ```yaml
  name: my-extension
  version: 1.0.0
  description: My custom OpenMAS extension
  author: Your Name
  license: MIT
  extension_points:
    - name: my_extension
      type: protocol_adapter
      protocols: ["a2a", "mcp"]
      entry_point: openmas_ext_myextension.extension:MyExtension
  ```

- **Extension Commands**:
  ```bash
  # Search for extensions
  openmas ext search "protocol bridge"

  # Publish an extension
  openmas ext publish ./my-extension

  # Validate an extension
  openmas ext validate ./my-extension
  ```

# Streaming Pattern

## Overview

The Streaming pattern enables continuous, efficient data flow between agents. Unlike request-response or event-based patterns that typically involve discrete messages, streaming allows for high-throughput, real-time data transfer that may be unbounded in size or duration.

## Pattern Characteristics

- **Synchronicity**: Typically asynchronous, continuous
- **Cardinality**: One-to-one (1:1) or one-to-many (1:N)
- **Flow Control**: Push-based or pull-based streaming
- **Back Pressure**: Support for handling consumption rate differences
- **Chunking**: Data transferred in manageable chunks

## Core Capabilities

The Streaming pattern provides these key capabilities:

1. **Continuous Data Flow** - Ongoing transfer of data between agents
2. **Flow Control** - Managing data rate between producer and consumer
3. **Back Pressure** - Handling when consumer is slower than producer
4. **Stream Lifecycle** - Establishing, maintaining, and closing streams
5. **Error Recovery** - Resuming streams after interruptions
6. **Batching** - Grouping data for efficient transfer

## Sequence Diagram

```
┌────────────┐                         ┌────────────┐
│            │                         │            │
│  Producer  │                         │  Consumer  │
│            │                         │            │
└────────────┘                         └────────────┘
      │                                      │
      │  1. Stream Initialization            │
      │ ─────────────────────────────────────>
      │                                      │
      │  2. Stream Acknowledgment            │
      │ <─────────────────────────────────────
      │                                      │
      │  3. Data Chunk 1                     │
      │ ─────────────────────────────────────>
      │                                      │
      │  4. Process Chunk                    │
      │                                      │
      │  5. Data Chunk 2                     │
      │ ─────────────────────────────────────>
      │                                      │
      │  6. Process Chunk                    │
      │                                      │
      │  7. Back Pressure (Slow Down)        │
      │ <─────────────────────────────────────
      │                                      │
      │  8. Adjust Rate                      │
      │                                      │
      │  9. Data Chunk 3                     │
      │ ─────────────────────────────────────>
      │                                      │
      │  10. Stream Completion               │
      │ ─────────────────────────────────────>
      │                                      │
```

## Message Format

### Stream Initialization

```yaml
{
  "id": "stream-123",
  "type": "stream_init",
  "stream_id": "data-stream-456",
  "content": {
    "stream_type": "data_export",
    "expected_size": 10485760,  # Optional size hint (10MB)
    "metadata": {
      "format": "json",
      "compression": "gzip"
    }
  },
  "metadata": {
    "pattern": "streaming",
    "timestamp": "2025-05-18T10:32:45Z",
    "producer_id": "data_service",
    "timeout_ms": 300000
  }
}
```

### Stream Data Chunk

```yaml
{
  "id": "chunk-789",
  "type": "stream_data",
  "stream_id": "data-stream-456",
  "sequence": 1,  # Sequence number for ordering
  "content": {
    # Chunk data (may be binary or structured)
    "data": "base64-encoded-or-json-data"
  },
  "metadata": {
    "pattern": "streaming",
    "timestamp": "2025-05-18T10:32:46Z",
    "chunk_size": 4096,
    "is_last": false
  }
}
```

### Stream Control

```yaml
{
  "id": "control-321",
  "type": "stream_control",
  "stream_id": "data-stream-456",
  "control_type": "back_pressure",
  "content": {
    "requested_rate": 2048,  # Bytes per second
    "reason": "processing_overload"
  },
  "metadata": {
    "pattern": "streaming",
    "timestamp": "2025-05-18T10:32:50Z",
    "consumer_id": "data_processor"
  }
}
```

## Configuration Options

The Streaming pattern has these configuration options:

```yaml
streaming:
  options:
    flow_control:
      buffer_size: 1000  # Number of chunks to buffer
      batch_size: 100    # Chunks per batch
      back_pressure: true
      rate_limits:
        max_bytes_per_second: 1048576  # 1MB/s
        max_items_per_second: 1000
    stream_lifecycle:
      idle_timeout: 300000  # 5 minutes in milliseconds
      max_duration: 3600000  # 1 hour in milliseconds
      keepalive_interval: 30000  # 30 seconds
    error_handling:
      resume_on_error: true
      max_retries: 3
      notification_threshold: 10
    chunking:
      size: 4096  # Bytes per chunk
      content_type: "application/octet-stream"
    security:
      require_authentication: true
      authorization_profile: "default"
      encrypt_payload: false
    observability:
      metrics_enabled: true
      log_level: "info"
      tracing_enabled: true
```

## Implementation

### Pattern Class

```python
class StreamingPattern(Pattern):
    """Implementation of the Streaming pattern."""
    
    def __init__(self, options, agent_context):
        """Initialize the pattern."""
        super().__init__(options, agent_context)
        self.flow_control = options.get("flow_control", {})
        self.stream_lifecycle = options.get("stream_lifecycle", {})
        self.error_handling = options.get("error_handling", {})
        self.chunking = options.get("chunking", {})
        
        # Initialize stream tracking
        self.active_streams = {}
        self.stream_buffers = {}
        
    async def start_stream(self, target_agent_id, stream_type, metadata=None):
        """Start a new stream to a target agent."""
        # Create stream ID
        stream_id = str(uuid.uuid4())
        
        # Create stream initialization message
        init_message = {
            "id": str(uuid.uuid4()),
            "type": "stream_init",
            "stream_id": stream_id,
            "content": {
                "stream_type": stream_type,
                "metadata": metadata or {}
            },
            "metadata": {
                "pattern": "streaming",
                "timestamp": datetime.now().isoformat(),
                "producer_id": self.agent_context.agent_id,
                "timeout_ms": self.stream_lifecycle.get("idle_timeout", 300000)
            }
        }
        
        # Get protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)
        
        # Prepare outgoing message
        prepared_init = await adapter.prepare_outgoing(init_message, self)
        
        # Track the stream
        self.active_streams[stream_id] = {
            "target_agent_id": target_agent_id,
            "stream_type": stream_type,
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "sequence": 0,
            "status": "initializing"
        }
        
        # Send initialization message
        await self.agent_context.communicator.send_message(
            prepared_init, target_agent_id=target_agent_id)
            
        # Create a stream object for the caller
        stream = Stream(self, stream_id, target_agent_id)
        
        return stream
        
    async def receive_stream(self, init_message):
        """Receive a new stream from another agent."""
        stream_id = init_message.get("stream_id")
        content = init_message.get("content", {})
        metadata = init_message.get("metadata", {})
        producer_id = metadata.get("producer_id")
        
        # Track the stream
        self.active_streams[stream_id] = {
            "producer_id": producer_id,
            "stream_type": content.get("stream_type"),
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "sequence": 0,
            "status": "active",
            "buffer": []
        }
        
        # Set up buffer for this stream
        buffer_size = self.flow_control.get("buffer_size", 1000)
        self.stream_buffers[stream_id] = asyncio.Queue(maxsize=buffer_size)
        
        # Create a stream object for the caller
        stream = Stream(self, stream_id, producer_id, is_producer=False)
        
        return stream
        
    async def send_chunk(self, stream_id, data, metadata=None, is_last=False):
        """Send a data chunk to a stream."""
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream not found: {stream_id}")
            
        stream_info = self.active_streams[stream_id]
        target_agent_id = stream_info["target_agent_id"]
        
        # Increment sequence
        sequence = stream_info["sequence"] + 1
        stream_info["sequence"] = sequence
        stream_info["last_activity"] = datetime.now()
        
        # Create chunk message
        chunk_message = {
            "id": str(uuid.uuid4()),
            "type": "stream_data",
            "stream_id": stream_id,
            "sequence": sequence,
            "content": {
                "data": data
            },
            "metadata": metadata or {}
        }
        
        # Add pattern metadata
        chunk_message["metadata"].update({
            "pattern": "streaming",
            "timestamp": datetime.now().isoformat(),
            "chunk_size": len(str(data)) if not isinstance(data, bytes) else len(data),
            "is_last": is_last
        })
        
        # Get protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)
        
        # Prepare outgoing message
        prepared_chunk = await adapter.prepare_outgoing(chunk_message, self)
        
        # Send chunk message
        await self.agent_context.communicator.send_message(
            prepared_chunk, target_agent_id=target_agent_id)
            
        # Update status if this is the last chunk
        if is_last:
            stream_info["status"] = "completed"
            
        return sequence
        
    async def receive_chunk(self, chunk_message):
        """Receive a data chunk from a stream."""
        stream_id = chunk_message.get("stream_id")
        sequence = chunk_message.get("sequence")
        content = chunk_message.get("content", {})
        metadata = chunk_message.get("metadata", {})
        is_last = metadata.get("is_last", False)
        
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream not found: {stream_id}")
            
        stream_info = self.active_streams[stream_id]
        stream_info["last_activity"] = datetime.now()
        
        # Check sequence (basic flow control)
        expected_sequence = stream_info["sequence"] + 1
        if sequence != expected_sequence:
            # Out of order, may need to handle
            pass
            
        stream_info["sequence"] = sequence
        
        # Add to buffer
        if stream_id in self.stream_buffers:
            await self.stream_buffers[stream_id].put({
                "sequence": sequence,
                "data": content.get("data"),
                "metadata": metadata,
                "is_last": is_last
            })
            
        # Update status if this is the last chunk
        if is_last:
            stream_info["status"] = "completed"
            
        return sequence
        
    async def send_control(self, stream_id, control_type, content):
        """Send a control message for a stream."""
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream not found: {stream_id}")
            
        stream_info = self.active_streams[stream_id]
        
        # Determine target based on role (producer or consumer)
        target_agent_id = None
        if "target_agent_id" in stream_info:
            # We are the producer
            target_agent_id = stream_info["target_agent_id"]
        elif "producer_id" in stream_info:
            # We are the consumer
            target_agent_id = stream_info["producer_id"]
            
        if not target_agent_id:
            raise ValueError("Cannot determine target for control message")
            
        # Create control message
        control_message = {
            "id": str(uuid.uuid4()),
            "type": "stream_control",
            "stream_id": stream_id,
            "control_type": control_type,
            "content": content,
            "metadata": {
                "pattern": "streaming",
                "timestamp": datetime.now().isoformat(),
                "agent_id": self.agent_context.agent_id
            }
        }
        
        # Get protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)
        
        # Prepare outgoing message
        prepared_control = await adapter.prepare_outgoing(control_message, self)
        
        # Send control message
        await self.agent_context.communicator.send_message(
            prepared_control, target_agent_id=target_agent_id)
            
        return control_message["id"]
        
    async def close_stream(self, stream_id):
        """Close a stream."""
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream not found: {stream_id}")
            
        stream_info = self.active_streams[stream_id]
        
        # Send final control message
        await self.send_control(
            stream_id=stream_id,
            control_type="close",
            content={
                "reason": "completed"
            }
        )
        
        # Update status
        stream_info["status"] = "closed"
        
        # Clean up
        if stream_id in self.stream_buffers:
            # Indicate end of stream to consumers
            await self.stream_buffers[stream_id].put(None)
            
        # Remove after a delay to allow final messages
        async def delayed_cleanup():
            await asyncio.sleep(5)
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
            if stream_id in self.stream_buffers:
                del self.stream_buffers[stream_id]
                
        asyncio.create_task(delayed_cleanup())
        
        return True
        
    async def process_incoming(self, message, protocol):
        """Process an incoming message."""
        adapter = self.get_protocol_adapter(protocol)
        transformed = await adapter.process_incoming(message, self)
        
        msg_type = transformed.get("type")
        stream_id = transformed.get("stream_id")
        
        if msg_type == "stream_init":
            # Handle stream initialization
            stream = await self.receive_stream(transformed)
            # Notify agent of new stream
            await self.agent_context.handle_new_stream(stream)
            
        elif msg_type == "stream_data" and stream_id in self.active_streams:
            # Handle data chunk
            await self.receive_chunk(transformed)
            
        elif msg_type == "stream_control" and stream_id in self.active_streams:
            # Handle control message
            control_type = transformed.get("control_type")
            content = transformed.get("content", {})
            
            if control_type == "back_pressure":
                # Adjust rate if we're the producer
                if "target_agent_id" in self.active_streams[stream_id]:
                    requested_rate = content.get("requested_rate")
                    # Apply rate limiting
                    
            elif control_type == "close":
                # Close the stream
                await self.close_stream(stream_id)
                
        return transformed
        
    async def iterate_stream(self, stream_id):
        """Iterate over chunks in a stream."""
        if stream_id not in self.active_streams or stream_id not in self.stream_buffers:
            raise ValueError(f"Stream not found or not readable: {stream_id}")
            
        buffer = self.stream_buffers[stream_id]
        
        while True:
            # Get next chunk from buffer
            chunk = await buffer.get()
            
            # None indicates end of stream
            if chunk is None:
                break
                
            yield chunk["data"]
            
            # Mark as done to support back pressure
            buffer.task_done()
            
            # If this was the last chunk, we're done
            if chunk.get("is_last", False):
                break
```

### Stream Class

```python
class Stream:
    """Represents a stream for the caller."""
    
    def __init__(self, pattern, stream_id, peer_agent_id, is_producer=True):
        """Initialize the stream."""
        self.pattern = pattern
        self.stream_id = stream_id
        self.peer_agent_id = peer_agent_id
        self.is_producer = is_producer
        self.is_closed = False
        
    async def send(self, data, metadata=None, is_last=False):
        """Send data to the stream."""
        if self.is_closed:
            raise ValueError("Stream is closed")
            
        if not self.is_producer:
            raise ValueError("Cannot send on a consumer stream")
            
        sequence = await self.pattern.send_chunk(
            self.stream_id, data, metadata, is_last)
            
        if is_last:
            self.is_closed = True
            
        return sequence
        
    async def close(self):
        """Close the stream."""
        if self.is_closed:
            return
            
        await self.pattern.close_stream(self.stream_id)
        self.is_closed = True
        
    def __aiter__(self):
        """Make the stream iterable (for consumers)."""
        if self.is_producer:
            raise ValueError("Cannot iterate on a producer stream")
            
        return self.pattern.iterate_stream(self.stream_id)
        
    async def apply_back_pressure(self, requested_rate):
        """Apply back pressure to slow down the producer."""
        if self.is_producer:
            raise ValueError("Cannot apply back pressure as producer")
            
        await self.pattern.send_control(
            self.stream_id,
            "back_pressure",
            {
                "requested_rate": requested_rate,
                "reason": "processing_overload"
            }
        )
```

## Protocol Adaptations

### A2A Protocol Adaptation

A2A protocol adapts the Streaming pattern using streaming features:

```yaml
streaming:
  protocol_adaptations:
    a2a:
      use_streaming: true
      chunk_size: 4096
      stream_id_field: "stream_id"
```

**Adapter Implementation:**

```python
class A2AStreamingAdapter(ProtocolAdapter):
    """Adapts the Streaming pattern to A2A protocol."""
    
    async def process_incoming(self, message, pattern):
        """Process an incoming A2A message."""
        if message.get("type") == "stream_chunk":
            # Extract chunk data
            metadata = message.get("metadata", {})
            stream_id = metadata.get(pattern.config.get("stream_id_field", "stream_id"))
            
            return {
                "id": message.get("id"),
                "type": "stream_data",
                "stream_id": stream_id,
                "sequence": metadata.get("sequence", 0),
                "content": {
                    "data": message.get("chunk")
                },
                "metadata": metadata
            }
            
        return message
        
    async def prepare_outgoing(self, message, pattern):
        """Prepare an outgoing A2A message."""
        if message.get("type") == "stream_data":
            # Create an A2A stream chunk
            chunk = {
                "type": "stream_chunk",
                "chunk": message.get("content", {}).get("data"),
                "metadata": message.get("metadata", {})
            }
            
            # Ensure stream_id is in metadata
            chunk["metadata"][pattern.config.get("stream_id_field", "stream_id")] = message.get("stream_id")
            chunk["metadata"]["sequence"] = message.get("sequence", 0)
            
            return chunk
        
        return message
```

### gRPC Protocol Adaptation

gRPC provides native streaming support:

```yaml
streaming:
  protocol_adaptations:
    grpc:
      service_name: "StreamService"
      method_name: "StreamData"
      stream_type: "bidirectional"
```

## Integration with Topologies

The Streaming pattern is commonly used in these topology relationships:

1. **Peer-to-Peer**: Continuous data flows between peers
2. **Pipeline**: Stages in a data processing pipeline
3. **Hierarchical**: Data aggregation up the hierarchy
4. **Mesh**: High-throughput data distribution

**Example Configuration:**

```yaml
topology:
  pattern: "peer_to_peer"
  roles:
    types:
      - name: "data_source"
      - name: "data_processor"
  relationships:
    types:
      - name: "source_to_processor"
        communication_patterns:
          primary: "streaming"
```

## Use Cases

### 1. Data Export

Streaming large datasets between agents:

```python
# Data service exporting data
async def export_data(self, query_params, target_agent_id):
    # Start a stream
    stream = await streaming_pattern.start_stream(
        target_agent_id=target_agent_id,
        stream_type="data_export",
        metadata={
            "format": "json",
            "query": query_params
        }
    )
    
    # Fetch data in batches
    data_source = self.data_service.query(query_params)
    batch = []
    batch_size = 100
    
    async for item in data_source:
        batch.append(item)
        
        if len(batch) >= batch_size:
            # Send batch as chunk
            await stream.send(batch)
            batch = []
            
    # Send any remaining items
    if batch:
        await stream.send(batch)
        
    # Close the stream
    await stream.send([], is_last=True)
    
# Data processor receiving exported data
async def handle_new_stream(self, stream):
    if stream.stream_id.metadata.get("stream_type") == "data_export":
        # Process the incoming data stream
        imported_count = 0
        
        async for data_batch in stream:
            # Process each batch
            for item in data_batch:
                await self.process_item(item)
                imported_count += 1
                
                # Apply back pressure if needed
                if self.is_overloaded():
                    await stream.apply_back_pressure(1024)  # Slow down
                    
        # Report completion
        self.logger.info(f"Imported {imported_count} items")
```

### 2. Real-Time Analytics

Streaming analytics processing:

```yaml
# Real-time analytics configuration
agents:
  data_collector:
    class: "agents.analytics.DataCollector"
    patterns:
      streaming:
        options:
          flow_control:
            buffer_size: 10000
            batch_size: 500
    topology:
      role: "data_source"
      relationships:
        - agent_id: "analytics_processor"
          relationship_type: "source_to_processor"
          communication_pattern: "streaming"
```

### 3. Media Streaming

Streaming media content:

```python
# Media streaming service
async def stream_media(self, media_id, target_agent_id):
    # Start a stream
    stream = await streaming_pattern.start_stream(
        target_agent_id=target_agent_id,
        stream_type="media_stream",
        metadata={
            "media_id": media_id,
            "format": "mp4",
            "encoding": "h264"
        }
    )
    
    # Open media file
    media_file = await self.media_store.open(media_id)
    chunk_size = 65536  # 64KB chunks
    
    # Stream in chunks
    while True:
        chunk = await media_file.read(chunk_size)
        if not chunk:
            break
            
        await stream.send(
            chunk,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "chunk_size": len(chunk)
            }
        )
        
    # Close the stream
    await stream.send(b"", is_last=True)
    
# Media player receiving stream
async def handle_new_stream(self, stream):
    if stream.metadata.get("stream_type") == "media_stream":
        # Set up media player
        player = self.create_player(
            format=stream.metadata.get("format"),
            encoding=stream.metadata.get("encoding")
        )
        
        # Play the incoming stream
        async for chunk in stream:
            await player.feed(chunk)
            
            # Apply back pressure if buffer is filling up
            if player.buffer_level() > 0.8:  # 80% full
                await stream.apply_back_pressure(32768)  # 32KB/s
```

## Security Considerations

The Streaming pattern includes these security features:

1. **Stream Authorization**: Permissions for initiating and receiving streams
2. **Content Validation**: Validate chunk data for safety
3. **Rate Limiting**: Prevent bandwidth abuse
4. **Encryption**: Payload encryption for sensitive data
5. **Access Control**: Stream type-based access control

**Security Configuration:**

```yaml
streaming:
  options:
    security:
      require_authentication: true
      stream_type_permissions:
        - stream_type: "data_export"
          roles: ["data_admin", "analyst"]
        - stream_type: "media_stream"
          roles: ["media_service", "player"]
      content_validation: true
      encrypt_payload: true
```

## Observability

The Streaming pattern supports observability:

1. **Throughput Metrics**: Bytes/items per second
2. **Stream Lifecycle**: Duration, status
3. **Buffer Metrics**: Utilization, overflow events
4. **Back Pressure Events**: Frequency, duration

**Metrics Example:**

```
stream_throughput_bytes_per_second{agent="data_service",stream_type="data_export"} 1048576
stream_active_count{agent="data_service"} 5
stream_buffer_utilization{agent="data_processor",stream_id="data-stream-456"} 0.75
stream_back_pressure_events{agent="data_processor"} 12
```

## Protocol Independence

The Streaming pattern works consistently across protocols:

- **A2A**: Using streaming chunk features
- **gRPC**: Using bidirectional streaming
- **WebSockets**: Using continuous message flow
- **HTTP**: Using chunked transfer encoding
- **MQTT**: Using sequential message publication

This protocol independence enables agents to stream data using the same pattern regardless of the underlying protocol implementation.

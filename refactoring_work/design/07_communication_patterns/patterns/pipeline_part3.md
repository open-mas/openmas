# Pipeline Pattern (continued)

## Protocol Adaptations

The Pipeline pattern adapts to different protocols while maintaining consistent semantics. This aligns with OpenMAS's protocol independence and ensures that pipelines work consistently regardless of the underlying protocol implementation.

### A2A Protocol Adaptation

A2A protocol adapts the Pipeline pattern using tasks:

```yaml
pipeline:
  protocol_adaptations:
    a2a:
      use_tasks: true
      task_type: "pipeline"
      stage_metadata_field: "stage"
```

**Adapter Implementation:**

```python
class A2APipelineAdapter(ProtocolAdapter):
    """Adapts the Pipeline pattern to A2A protocol."""

    async def process_incoming(self, message, pattern):
        """Process an incoming A2A message."""
        if message.get("type") == pattern.config.get("task_type", "pipeline"):
            # Extract metadata
            metadata = message.get("metadata", {})

            # Determine message type
            if "stage_id" in metadata:
                # This is a stage execution or result
                if "output" in message:
                    # This is a stage result
                    return {
                        "id": message.get("id"),
                        "type": "stage_result",
                        "pipeline_id": metadata.get("pipeline_id"),
                        "stage_id": metadata.get("stage_id"),
                        "content": {
                            "status": "success" if not message.get("error") else "failed",
                            "output": message.get("output"),
                            "error": message.get("error")
                        },
                        "metadata": metadata
                    }
                else:
                    # This is a stage execution
                    return {
                        "id": message.get("id"),
                        "type": "stage_exec",
                        "pipeline_id": metadata.get("pipeline_id"),
                        "stage_id": metadata.get("stage_id"),
                        "content": {
                            "input": message.get("input"),
                            "config": metadata.get("config", {})
                        },
                        "metadata": metadata
                    }
            elif "final_status" in metadata:
                # This is a pipeline completion
                return {
                    "id": message.get("id"),
                    "type": "pipeline_completion",
                    "pipeline_id": metadata.get("pipeline_id"),
                    "content": {
                        "status": metadata.get("final_status"),
                        "final_output": message.get("output")
                    },
                    "metadata": metadata
                }
            else:
                # This is a pipeline initialization
                return {
                    "id": message.get("id"),
                    "type": "pipeline_init",
                    "pipeline_id": metadata.get("pipeline_id"),
                    "content": {
                        "pipeline_type": metadata.get("pipeline_type"),
                        "stages": metadata.get("stages", []),
                        "input": message.get("input")
                    },
                    "metadata": metadata
                }

        return message

    async def prepare_outgoing(self, message, pattern):
        """Prepare an outgoing A2A message."""
        if message.get("type") == "pipeline_init":
            # Prepare pipeline initialization
            task = {
                "type": pattern.config.get("task_type", "pipeline"),
                "input": message.get("content", {}).get("input"),
                "metadata": {
                    "pipeline_id": message.get("pipeline_id"),
                    "pipeline_type": message.get("content", {}).get("pipeline_type"),
                    "stages": message.get("content", {}).get("stages", []),
                    "timestamp": message.get("metadata", {}).get("timestamp"),
                    "initiator_id": message.get("metadata", {}).get("initiator_id")
                }
            }
            return task

        elif message.get("type") == "stage_exec":
            # Prepare stage execution
            task = {
                "type": pattern.config.get("task_type", "pipeline"),
                "input": message.get("content", {}).get("input"),
                "metadata": {
                    "pipeline_id": message.get("pipeline_id"),
                    "stage_id": message.get("stage_id"),
                    "config": message.get("content", {}).get("config", {}),
                    "previous_stage": message.get("metadata", {}).get("previous_stage"),
                    "next_stage": message.get("metadata", {}).get("next_stage"),
                    "timestamp": message.get("metadata", {}).get("timestamp"),
                    "executor_id": message.get("metadata", {}).get("executor_id")
                }
            }
            return task

        elif message.get("type") == "stage_result":
            # Prepare stage result
            task = {
                "type": pattern.config.get("task_type", "pipeline"),
                "output": message.get("content", {}).get("output"),
                "error": message.get("content", {}).get("status") == "failed" and message.get("content", {}).get("error"),
                "metadata": {
                    "pipeline_id": message.get("pipeline_id"),
                    "stage_id": message.get("stage_id"),
                    "timestamp": message.get("metadata", {}).get("timestamp"),
                    "execution_time_ms": message.get("metadata", {}).get("execution_time_ms"),
                    "next_stage": message.get("metadata", {}).get("next_stage")
                }
            }
            return task

        elif message.get("type") == "pipeline_completion":
            # Prepare pipeline completion
            task = {
                "type": pattern.config.get("task_type", "pipeline"),
                "output": message.get("content", {}).get("final_output"),
                "metadata": {
                    "pipeline_id": message.get("pipeline_id"),
                    "final_status": message.get("content", {}).get("status"),
                    "timestamp": message.get("metadata", {}).get("timestamp"),
                    "total_execution_time_ms": message.get("metadata", {}).get("total_execution_time_ms"),
                    "initiator_id": message.get("metadata", {}).get("initiator_id")
                }
            }
            return task

        return message
```

### MCP Protocol Adaptation

MCP protocol adapts the Pipeline pattern using function calls:

```yaml
pipeline:
  protocol_adaptations:
    mcp:
      use_function_calls: true
      stage_function_prefix: "pipeline_stage_"
      init_function: "start_pipeline"
      completion_function: "complete_pipeline"
```

**Adapter Implementation:**

```python
class MCPPipelineAdapter(ProtocolAdapter):
    """Adapts the Pipeline pattern to MCP protocol."""

    async def process_incoming(self, message, pattern):
        """Process an incoming MCP message."""
        if message.get("type") == "function_call":
            function_name = message.get("name", "")
            stage_prefix = pattern.config.get("stage_function_prefix", "pipeline_stage_")

            if function_name.startswith(stage_prefix):
                # This is a stage execution
                stage_id = function_name[len(stage_prefix):]
                args = message.get("arguments", {})

                return {
                    "id": message.get("id"),
                    "type": "stage_exec",
                    "pipeline_id": args.get("pipeline_id"),
                    "stage_id": stage_id,
                    "content": {
                        "input": args.get("input"),
                        "config": args.get("config", {})
                    },
                    "metadata": {
                        "previous_stage": args.get("previous_stage"),
                        "next_stage": args.get("next_stage"),
                        "executor_id": args.get("executor_id"),
                        "timestamp": datetime.now().isoformat()
                    }
                }

            elif function_name == pattern.config.get("init_function", "start_pipeline"):
                # This is a pipeline initialization
                args = message.get("arguments", {})

                return {
                    "id": message.get("id"),
                    "type": "pipeline_init",
                    "pipeline_id": args.get("pipeline_id") or str(uuid.uuid4()),
                    "content": {
                        "pipeline_type": args.get("pipeline_type"),
                        "stages": args.get("stages", []),
                        "input": args.get("input")
                    },
                    "metadata": {
                        "initiator_id": args.get("initiator_id"),
                        "timestamp": datetime.now().isoformat(),
                        "timeout_ms": args.get("timeout_ms", 300000)
                    }
                }

            elif function_name == pattern.config.get("completion_function", "complete_pipeline"):
                # This is a pipeline completion
                args = message.get("arguments", {})

                return {
                    "id": message.get("id"),
                    "type": "pipeline_completion",
                    "pipeline_id": args.get("pipeline_id"),
                    "content": {
                        "status": args.get("status"),
                        "final_output": args.get("final_output")
                    },
                    "metadata": {
                        "timestamp": datetime.now().isoformat(),
                        "total_execution_time_ms": args.get("total_execution_time_ms"),
                        "initiator_id": args.get("initiator_id")
                    }
                }

        elif message.get("type") == "function_result":
            # This is a stage result
            result = message.get("result", {})

            return {
                "id": message.get("id"),
                "type": "stage_result",
                "pipeline_id": result.get("pipeline_id"),
                "stage_id": result.get("stage_id"),
                "content": {
                    "status": "success" if not message.get("error") else "failed",
                    "output": result.get("output"),
                    "error": message.get("error")
                },
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "execution_time_ms": result.get("execution_time_ms"),
                    "next_stage": result.get("next_stage")
                }
            }

        return message

    async def prepare_outgoing(self, message, pattern):
        """Prepare an outgoing MCP message."""
        if message.get("type") == "pipeline_init":
            # Prepare pipeline initialization
            function_call = {
                "type": "function_call",
                "name": pattern.config.get("init_function", "start_pipeline"),
                "arguments": {
                    "pipeline_id": message.get("pipeline_id"),
                    "pipeline_type": message.get("content", {}).get("pipeline_type"),
                    "stages": message.get("content", {}).get("stages", []),
                    "input": message.get("content", {}).get("input"),
                    "initiator_id": message.get("metadata", {}).get("initiator_id"),
                    "timeout_ms": message.get("metadata", {}).get("timeout_ms")
                }
            }
            return function_call

        elif message.get("type") == "stage_exec":
            # Prepare stage execution
            stage_prefix = pattern.config.get("stage_function_prefix", "pipeline_stage_")
            function_call = {
                "type": "function_call",
                "name": f"{stage_prefix}{message.get('stage_id')}",
                "arguments": {
                    "pipeline_id": message.get("pipeline_id"),
                    "input": message.get("content", {}).get("input"),
                    "config": message.get("content", {}).get("config", {}),
                    "previous_stage": message.get("metadata", {}).get("previous_stage"),
                    "next_stage": message.get("metadata", {}).get("next_stage"),
                    "executor_id": message.get("metadata", {}).get("executor_id")
                }
            }
            return function_call

        elif message.get("type") == "stage_result":
            # Prepare stage result
            function_result = {
                "type": "function_result",
                "result": {
                    "pipeline_id": message.get("pipeline_id"),
                    "stage_id": message.get("stage_id"),
                    "output": message.get("content", {}).get("output"),
                    "execution_time_ms": message.get("metadata", {}).get("execution_time_ms"),
                    "next_stage": message.get("metadata", {}).get("next_stage")
                },
                "error": message.get("content", {}).get("status") == "failed" and message.get("content", {}).get("error")
            }
            return function_result

        elif message.get("type") == "pipeline_completion":
            # Prepare pipeline completion
            function_call = {
                "type": "function_call",
                "name": pattern.config.get("completion_function", "complete_pipeline"),
                "arguments": {
                    "pipeline_id": message.get("pipeline_id"),
                    "status": message.get("content", {}).get("status"),
                    "final_output": message.get("content", {}).get("final_output"),
                    "total_execution_time_ms": message.get("metadata", {}).get("total_execution_time_ms"),
                    "initiator_id": message.get("metadata", {}).get("initiator_id")
                }
            }
            return function_call

        return message
```

## Integration with Topologies

The Pipeline pattern is commonly used in these topology relationships:

1. **Hierarchical**: Sequential processing through hierarchy
2. **Centralized**: Orchestrator coordinating workflow stages
3. **Pipeline**: Core pattern for pipeline topologies
4. **Workflow**: Structured business processes

**Example Configuration:**

```yaml
topology:
  pattern: "pipeline"
  roles:
    types:
      - name: "initiator"
      - name: "processor"
  relationships:
    types:
      - name: "initiator_to_processor"
        communication_patterns:
          primary: "pipeline"
      - name: "processor_to_processor"
        communication_patterns:
          primary: "pipeline"
```

## Use Cases

### 1. Data Processing Pipeline

Sequential processing of data through multiple stages:

```python
# Data orchestrator initiating a data processing pipeline
async def process_data(self, data_source, parameters):
    # Define the pipeline stages
    stages = [
        {
            "id": "extract",
            "executor": "data_extractor",
            "timeout": 60000,
            "config": {
                "source": data_source,
                "batch_size": parameters.get("batch_size", 1000)
            }
        },
        {
            "id": "transform",
            "executor": "data_transformer",
            "timeout": 120000,
            "config": {
                "transformations": parameters.get("transformations", [])
            }
        },
        {
            "id": "load",
            "executor": "data_loader",
            "timeout": 180000,
            "config": {
                "target": parameters.get("target"),
                "mode": parameters.get("load_mode", "append")
            }
        }
    ]

    # Start the pipeline
    pipeline = await pipeline_pattern.start_pipeline(
        pipeline_type="data_processing",
        stages=stages,
        input_data={
            "source": data_source,
            "parameters": parameters
        }
    )

    # Wait for completion
    result = await pipeline.wait_for_completion()

    # Return the result
    return {
        "status": result.get("status"),
        "processed_records": result.get("output", {}).get("processed_records", 0),
        "errors": result.get("output", {}).get("errors", [])
    }

# Data extractor implementing a pipeline stage
async def handle_pipeline_stage_extract(self, message):
    pipeline_id = message.get("pipeline_id")
    stage_id = message.get("stage_id")
    input_data = message.get("content", {}).get("input", {})
    config = message.get("content", {}).get("config", {})

    # Extract data from source
    source = config.get("source")
    batch_size = config.get("batch_size", 1000)

    try:
        # Perform extraction
        start_time = time.time()
        extracted_data = await self.extraction_service.extract(
            source=source,
            batch_size=batch_size,
            parameters=input_data.get("parameters", {})
        )
        execution_time = int((time.time() - start_time) * 1000)

        # Return success result
        return {
            "id": str(uuid.uuid4()),
            "type": "stage_result",
            "pipeline_id": pipeline_id,
            "stage_id": stage_id,
            "content": {
                "status": "success",
                "output": {
                    "records": extracted_data,
                    "record_count": len(extracted_data),
                    "source": source
                }
            },
            "metadata": {
                "execution_time_ms": execution_time,
                "next_stage": "transform"
            }
        }
    except Exception as e:
        # Return failure result
        return {
            "id": str(uuid.uuid4()),
            "type": "stage_result",
            "pipeline_id": pipeline_id,
            "stage_id": stage_id,
            "content": {
                "status": "failed",
                "error": {
                    "message": str(e),
                    "type": type(e).__name__
                }
            },
            "metadata": {
                "execution_time_ms": int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
            }
        }
```

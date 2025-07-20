# Pipeline Pattern (continued)

## Configuration Options

The Pipeline pattern has these configuration options:

```yaml
pipeline:
  options:
    stages:
      - id: "stage1"
        executor: "agent1"
        timeout: 30000
      - id: "stage2"
        executor: "agent2"
        timeout: 45000
      - id: "stage3"
        executor: "agent3"
        timeout: 60000
    flow_control:
      parallel_stages: false
      continue_on_error: false
      retry_failed_stages: true
      max_retries: 3
    monitoring:
      track_stage_metrics: true
      stage_timeout_action: "skip"  # fail, skip, retry
    error_handling:
      on_stage_failure: "abort"  # abort, continue, retry
      failure_notification: "immediate"
    security:
      require_authentication: true
      authorization_profile: "default"
    observability:
      metrics_enabled: true
      log_level: "info"
      tracing_enabled: true
```

## Implementation

### Pattern Class

```python
class PipelinePattern(Pattern):
    """Implementation of the Pipeline pattern."""

    def __init__(self, options, agent_context):
        """Initialize the pattern."""
        super().__init__(options, agent_context)
        self.stages_config = options.get("stages", [])
        self.flow_control = options.get("flow_control", {})
        self.monitoring = options.get("monitoring", {})
        self.error_handling = options.get("error_handling", {})

        # Initialize pipeline tracking
        self.active_pipelines = {}

    async def start_pipeline(self, pipeline_type, stages=None, input_data=None, metadata=None):
        """Start a new pipeline."""
        # Create pipeline ID
        pipeline_id = str(uuid.uuid4())

        # Use configured stages or provided stages
        effective_stages = stages or self.stages_config
        if not effective_stages:
            raise ValueError("No stages defined for pipeline")

        # Create pipeline initialization message
        init_message = {
            "id": str(uuid.uuid4()),
            "type": "pipeline_init",
            "pipeline_id": pipeline_id,
            "content": {
                "pipeline_type": pipeline_type,
                "stages": effective_stages,
                "input": input_data or {}
            },
            "metadata": metadata or {}
        }

        # Add pattern metadata
        init_message["metadata"].update({
            "pattern": "pipeline",
            "timestamp": datetime.now().isoformat(),
            "initiator_id": self.agent_context.agent_id,
            "timeout_ms": sum(stage.get("timeout", 30000) for stage in effective_stages)
        })

        # Track the pipeline
        self.active_pipelines[pipeline_id] = {
            "id": pipeline_id,
            "type": pipeline_type,
            "stages": effective_stages,
            "current_stage_index": -1,
            "stage_results": {},
            "status": "initializing",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Execute the first stage
        first_stage = effective_stages[0]
        await self._execute_stage(
            pipeline_id=pipeline_id,
            stage_id=first_stage["id"],
            stage_config=first_stage,
            input_data=input_data
        )

        # Create a pipeline object for the caller
        pipeline = Pipeline(self, pipeline_id)

        return pipeline

    async def _execute_stage(self, pipeline_id, stage_id, stage_config, input_data):
        """Execute a pipeline stage."""
        if pipeline_id not in self.active_pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")

        pipeline = self.active_pipelines[pipeline_id]

        # Find stage index
        stage_index = None
        for i, stage in enumerate(pipeline["stages"]):
            if stage["id"] == stage_id:
                stage_index = i
                break

        if stage_index is None:
            raise ValueError(f"Stage not found in pipeline: {stage_id}")

        pipeline["current_stage_index"] = stage_index
        pipeline["updated_at"] = datetime.now().isoformat()

        # Get executor agent ID
        executor_id = stage_config["executor"]

        # Determine previous and next stages
        previous_stage = None if stage_index == 0 else pipeline["stages"][stage_index - 1]["id"]
        next_stage = None if stage_index == len(pipeline["stages"]) - 1 else pipeline["stages"][stage_index + 1]["id"]

        # Create stage execution message
        exec_message = {
            "id": str(uuid.uuid4()),
            "type": "stage_exec",
            "pipeline_id": pipeline_id,
            "stage_id": stage_id,
            "content": {
                "input": input_data,
                "config": stage_config.get("config", {})
            },
            "metadata": {
                "pattern": "pipeline",
                "timestamp": datetime.now().isoformat(),
                "previous_stage": previous_stage,
                "next_stage": next_stage,
                "executor_id": executor_id
            }
        }

        # Get protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)

        # Prepare outgoing message
        prepared_exec = await adapter.prepare_outgoing(exec_message, self)

        # Send to executor agent
        await self.agent_context.communicator.send_message(
            prepared_exec, target_agent_id=executor_id)

        return exec_message["id"]

    async def handle_stage_result(self, result):
        """Handle a stage execution result."""
        pipeline_id = result.get("pipeline_id")
        stage_id = result.get("stage_id")
        content = result.get("content", {})
        status = content.get("status")
        output = content.get("output", {})
        metadata = result.get("metadata", {})

        if pipeline_id not in self.active_pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")

        pipeline = self.active_pipelines[pipeline_id]

        # Store the stage result
        pipeline["stage_results"][stage_id] = {
            "status": status,
            "output": output,
            "timestamp": metadata.get("timestamp"),
            "execution_time_ms": metadata.get("execution_time_ms")
        }

        pipeline["updated_at"] = datetime.now().isoformat()

        # Check if this is the last stage
        current_index = pipeline["current_stage_index"]
        is_last_stage = current_index == len(pipeline["stages"]) - 1

        # Handle stage failure
        if status != "success":
            on_failure = self.error_handling.get("on_stage_failure", "abort")

            if on_failure == "abort":
                # Abort the pipeline
                await self._complete_pipeline(
                    pipeline_id=pipeline_id,
                    status="failed",
                    final_output={
                        "error": f"Stage {stage_id} failed",
                        "stage_results": pipeline["stage_results"]
                    }
                )
                return
            elif on_failure == "retry":
                # Retry the stage if possible
                retries = pipeline.get("retries", {}).get(stage_id, 0)
                max_retries = self.error_handling.get("max_retries", 3)

                if retries < max_retries:
                    # Update retry count
                    if "retries" not in pipeline:
                        pipeline["retries"] = {}
                    pipeline["retries"][stage_id] = retries + 1

                    # Retry the stage
                    previous_stage_id = pipeline["stages"][current_index - 1]["id"] if current_index > 0 else None
                    previous_output = pipeline["stage_results"].get(previous_stage_id, {}).get("output", {}) if previous_stage_id else pipeline.get("input", {})

                    await self._execute_stage(
                        pipeline_id=pipeline_id,
                        stage_id=stage_id,
                        stage_config=pipeline["stages"][current_index],
                        input_data=previous_output
                    )
                    return

            # If we get here, either on_failure is "continue" or we've exceeded retry attempts

        # If this is the last stage or we're not continuing after failure
        if is_last_stage or (status != "success" and not self.flow_control.get("continue_on_error", False)):
            # Complete the pipeline
            final_status = "success" if all(r.get("status") == "success" for r in pipeline["stage_results"].values()) else "partial" if status != "success" else "failed"

            await self._complete_pipeline(
                pipeline_id=pipeline_id,
                status=final_status,
                final_output=self._generate_final_output(pipeline)
            )
        else:
            # Move to the next stage
            next_index = current_index + 1
            next_stage = pipeline["stages"][next_index]

            await self._execute_stage(
                pipeline_id=pipeline_id,
                stage_id=next_stage["id"],
                stage_config=next_stage,
                input_data=output
            )

    async def _complete_pipeline(self, pipeline_id, status, final_output):
        """Complete a pipeline execution."""
        if pipeline_id not in self.active_pipelines:
            raise ValueError(f"Pipeline not found: {pipeline_id}")

        pipeline = self.active_pipelines[pipeline_id]

        # Update pipeline status
        pipeline["status"] = status
        pipeline["updated_at"] = datetime.now().isoformat()
        pipeline["completed_at"] = datetime.now().isoformat()

        # Calculate total execution time
        start_time = datetime.fromisoformat(pipeline["created_at"])
        end_time = datetime.fromisoformat(pipeline["updated_at"])
        total_time_ms = (end_time - start_time).total_seconds() * 1000

        # Create pipeline completion message
        completion_message = {
            "id": str(uuid.uuid4()),
            "type": "pipeline_completion",
            "pipeline_id": pipeline_id,
            "content": {
                "status": status,
                "final_output": final_output
            },
            "metadata": {
                "pattern": "pipeline",
                "timestamp": datetime.now().isoformat(),
                "total_execution_time_ms": int(total_time_ms),
                "initiator_id": pipeline.get("initiator_id", self.agent_context.agent_id)
            }
        }

        # Get protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)

        # Prepare outgoing message
        prepared_completion = await adapter.prepare_outgoing(completion_message, self)

        # Send to initiator (if not ourselves)
        initiator_id = pipeline.get("initiator_id")
        if initiator_id and initiator_id != self.agent_context.agent_id:
            await self.agent_context.communicator.send_message(
                prepared_completion, target_agent_id=initiator_id)

        # If we're the initiator, notify via callback
        else:
            pipeline_obj = Pipeline(self, pipeline_id)
            await self.agent_context.handle_pipeline_completion(pipeline_obj, status, final_output)

        return completion_message["id"]

    def _generate_final_output(self, pipeline):
        """Generate the final pipeline output."""
        # Collect outputs from all stages
        stage_outputs = {
            stage_id: result.get("output", {})
            for stage_id, result in pipeline.get("stage_results", {}).items()
        }

        # Get the last successful stage result
        last_stage_id = None
        for stage in reversed(pipeline["stages"]):
            stage_id = stage["id"]
            if stage_id in pipeline.get("stage_results", {}) and pipeline["stage_results"][stage_id].get("status") == "success":
                last_stage_id = stage_id
                break

        # Use the last successful stage output as the final output
        final_output = stage_outputs.get(last_stage_id, {}) if last_stage_id else {}

        # Add summary information
        final_output["summary"] = {
            "pipeline_id": pipeline["id"],
            "pipeline_type": pipeline["type"],
            "status": pipeline["status"],
            "stage_results": {
                stage_id: {
                    "status": result.get("status"),
                    "execution_time_ms": result.get("execution_time_ms")
                }
                for stage_id, result in pipeline.get("stage_results", {}).items()
            }
        }

        return final_output

    async def get_pipeline_status(self, pipeline_id):
        """Get the status of a pipeline."""
        if pipeline_id not in self.active_pipelines:
            return None

        pipeline = self.active_pipelines[pipeline_id]

        return {
            "id": pipeline["id"],
            "type": pipeline["type"],
            "status": pipeline["status"],
            "current_stage": pipeline["stages"][pipeline["current_stage_index"]]["id"] if pipeline["current_stage_index"] >= 0 else None,
            "completed_stages": [
                stage_id for stage_id in pipeline.get("stage_results", {}).keys()
                if pipeline["stage_results"][stage_id].get("status") == "success"
            ],
            "created_at": pipeline["created_at"],
            "updated_at": pipeline["updated_at"],
            "completed_at": pipeline.get("completed_at")
        }

    async def process_incoming(self, message, protocol):
        """Process an incoming message."""
        adapter = self.get_protocol_adapter(protocol)
        transformed = await adapter.process_incoming(message, self)

        msg_type = transformed.get("type")

        if msg_type == "stage_result":
            # Handle stage result
            await self.handle_stage_result(transformed)

        elif msg_type == "pipeline_completion" and transformed.get("pipeline_id") in self.active_pipelines:
            # Handle pipeline completion notification
            pipeline_id = transformed.get("pipeline_id")
            content = transformed.get("content", {})

            # Update our pipeline status
            pipeline = self.active_pipelines[pipeline_id]
            pipeline["status"] = content.get("status", "completed")
            pipeline["updated_at"] = datetime.now().isoformat()
            pipeline["completed_at"] = datetime.now().isoformat()

            # Notify agent
            pipeline_obj = Pipeline(self, pipeline_id)
            await self.agent_context.handle_pipeline_completion(
                pipeline_obj, content.get("status"), content.get("final_output"))

        return transformed

    async def prepare_outgoing(self, message, protocol):
        """Prepare an outgoing message."""
        adapter = self.get_protocol_adapter(protocol)
        return await adapter.prepare_outgoing(message, self)
```

### Pipeline Class

```python
class Pipeline:
    """Represents a pipeline for the caller."""

    def __init__(self, pattern, pipeline_id):
        """Initialize the pipeline."""
        self.pattern = pattern
        self.pipeline_id = pipeline_id

    async def get_status(self):
        """Get the status of the pipeline."""
        return await self.pattern.get_pipeline_status(self.pipeline_id)

    async def get_stage_result(self, stage_id):
        """Get the result of a specific stage."""
        pipeline = self.pattern.active_pipelines.get(self.pipeline_id)
        if not pipeline:
            return None

        stage_results = pipeline.get("stage_results", {})
        return stage_results.get(stage_id)

    async def wait_for_completion(self, timeout=None):
        """Wait for the pipeline to complete."""
        start_time = time.time()

        while True:
            status = await self.get_status()

            if not status:
                return None

            if status["status"] in ["success", "failed", "partial", "aborted"]:
                # Get final output
                pipeline = self.pattern.active_pipelines.get(self.pipeline_id)
                if not pipeline:
                    return None

                return {
                    "status": status["status"],
                    "output": self.pattern._generate_final_output(pipeline)
                }

            # Check timeout
            if timeout and (time.time() - start_time > timeout):
                return {
                    "status": "timeout",
                    "output": None
                }

            # Wait a bit before checking again
            await asyncio.sleep(0.5)
```

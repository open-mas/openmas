# Advanced Communication Pattern Integration

This document demonstrates advanced usage of OpenMAS communication patterns, focusing on how patterns can be combined and integrated to solve complex multi-agent scenarios.

## 1. Multi-Pattern Workflow Orchestration

This example demonstrates how to integrate multiple patterns to create a sophisticated workflow:

![Multi-Pattern Workflow](../assets/multi_pattern_workflow.png)

### Key Pattern Integration:
- **Delegation** for task distribution
- **Pipeline** for sequential processing
- **Event-Based** for status updates
- **Streaming** for continuous data transfer
- **Request-Response** for synchronous operations

### Example Implementation:

```python
class WorkflowOrchestrator:
    """Orchestrator agent that integrates multiple communication patterns."""

    def __init__(self, agent_id, config):
        self.agent_id = agent_id
        self.config = config

        # Initialize patterns
        self.delegation_pattern = None
        self.pipeline_pattern = None
        self.event_pattern = None
        self.streaming_pattern = None
        self.request_response_pattern = None

        # Workflow state
        self.active_workflows = {}

    async def initialize_patterns(self, context):
        """Initialize communication patterns."""
        # Load patterns from registry
        pattern_registry = context.get_pattern_registry()

        self.delegation_pattern = await pattern_registry.get_pattern("delegation", self.config.get("patterns", {}).get("delegation"))
        self.pipeline_pattern = await pattern_registry.get_pattern("pipeline", self.config.get("patterns", {}).get("pipeline"))
        self.event_pattern = await pattern_registry.get_pattern("event_based", self.config.get("patterns", {}).get("event_based"))
        self.streaming_pattern = await pattern_registry.get_pattern("streaming", self.config.get("patterns", {}).get("streaming"))
        self.request_response_pattern = await pattern_registry.get_pattern("request_response", self.config.get("patterns", {}).get("request_response"))

        # Subscribe to workflow events
        await self.event_pattern.subscribe("workflow_status", self.handle_workflow_event)

    async def start_workflow(self, workflow_type, input_data):
        """Start a new multi-pattern workflow."""
        # Create workflow ID
        workflow_id = str(uuid.uuid4())

        # Initialize workflow state
        self.active_workflows[workflow_id] = {
            "id": workflow_id,
            "type": workflow_type,
            "status": "initializing",
            "created_at": datetime.now().isoformat(),
            "stages": [],
            "delegations": [],
            "results": {}
        }

        try:
            # Step 1: Use Request-Response for initial validation
            validation_result = await self.request_response_pattern.send_request(
                target_agent_id="validator",
                request_type="workflow_validation",
                content={
                    "workflow_type": workflow_type,
                    "input_data": input_data
                }
            )

            if not validation_result.get("is_valid", False):
                self.active_workflows[workflow_id]["status"] = "validation_failed"
                self.active_workflows[workflow_id]["error"] = validation_result.get("errors")
                return {"status": "error", "workflow_id": workflow_id, "message": "Validation failed"}

            # Step 2: Use Event-Based to notify workflow start
            await self.event_pattern.emit_event(
                event_type="workflow_started",
                content={
                    "workflow_id": workflow_id,
                    "workflow_type": workflow_type,
                    "initiator_id": self.agent_id
                }
            )

            # Step 3: Use Delegation to delegate data preparation
            data_preparation = await self.delegation_pattern.delegate_task(
                task_type="data_preparation",
                task_data={
                    "workflow_id": workflow_id,
                    "input_data": input_data,
                    "workflow_type": workflow_type
                },
                policy="high_priority"
            )

            # Track the delegation
            self.active_workflows[workflow_id]["delegations"].append({
                "id": data_preparation.delegation_id,
                "type": "data_preparation",
                "status": "pending"
            })

            # Wait for data preparation to complete
            preparation_result = await data_preparation.wait_for_completion()

            if preparation_result["status"] != "completed":
                self.active_workflows[workflow_id]["status"] = "preparation_failed"
                return {"status": "error", "workflow_id": workflow_id, "message": "Data preparation failed"}

            # Update workflow state
            prepared_data = preparation_result.get("output", {}).get("prepared_data", {})
            self.active_workflows[workflow_id]["prepared_data"] = prepared_data

            # Step 4: Use Pipeline for main processing
            processing_pipeline = await self.pipeline_pattern.start_pipeline(
                pipeline_type="workflow_processing",
                stages=[
                    {
                        "id": "analysis",
                        "executor": "analyzer",
                        "timeout": 60000
                    },
                    {
                        "id": "enrichment",
                        "executor": "enricher",
                        "timeout": 90000
                    },
                    {
                        "id": "summarization",
                        "executor": "summarizer",
                        "timeout": 30000
                    }
                ],
                input_data=prepared_data
            )

            # Track the pipeline
            self.active_workflows[workflow_id]["pipeline_id"] = processing_pipeline.pipeline_id

            # Step 5: Use Streaming for real-time monitoring
            monitor_stream = await self.streaming_pattern.start_stream(
                target_agent_id="workflow_monitor",
                stream_type="workflow_status",
                metadata={
                    "workflow_id": workflow_id,
                    "workflow_type": workflow_type
                }
            )

            # Store the stream for later use
            self.active_workflows[workflow_id]["monitor_stream"] = monitor_stream.stream_id

            # Step 6: Send initial status update through the stream
            await self.streaming_pattern.send_to_stream(
                stream_id=monitor_stream.stream_id,
                content={
                    "status": "processing",
                    "progress": 0,
                    "message": "Pipeline processing started"
                }
            )

            # Wait for pipeline to complete while streaming updates
            pipeline_status = None
            prev_stage = ""
            progress = 0

            while True:
                # Get current pipeline status
                status = await processing_pipeline.get_status()

                if not status:
                    break

                # Calculate progress
                if status["status"] in ["success", "failed", "partial", "aborted"]:
                    # Pipeline completed
                    pipeline_status = status
                    progress = 100
                    break

                # Update progress based on current stage
                current_stage = status.get("current_stage", "")
                if current_stage != prev_stage:
                    # Stage changed, update progress
                    stage_index = 0
                    for i, stage in enumerate(status.get("stages", [])):
                        if stage["id"] == current_stage:
                            stage_index = i
                            break

                    progress = int((stage_index / len(status.get("stages", []))) * 90)
                    prev_stage = current_stage

                    # Send progress update via stream
                    await self.streaming_pattern.send_to_stream(
                        stream_id=monitor_stream.stream_id,
                        content={
                            "status": "processing",
                            "current_stage": current_stage,
                            "progress": progress,
                            "message": f"Processing stage: {current_stage}"
                        }
                    )

                # Wait before checking again
                await asyncio.sleep(1)

            # Get pipeline result
            if pipeline_status:
                pipeline_result = await processing_pipeline.wait_for_completion()
                final_output = pipeline_result.get("output", {})

                # Step 7: Final workflow completion
                if pipeline_result.get("status") == "success":
                    self.active_workflows[workflow_id]["status"] = "completed"
                    self.active_workflows[workflow_id]["results"] = final_output

                    # Send final update via stream
                    await self.streaming_pattern.send_to_stream(
                        stream_id=monitor_stream.stream_id,
                        content={
                            "status": "completed",
                            "progress": 100,
                            "message": "Workflow completed successfully",
                            "summary": final_output.get("summary", {})
                        }
                    )

                    # Emit completion event
                    await self.event_pattern.emit_event(
                        event_type="workflow_completed",
                        content={
                            "workflow_id": workflow_id,
                            "workflow_type": workflow_type,
                            "status": "success",
                            "summary": final_output.get("summary", {})
                        }
                    )

                    # Close the monitoring stream
                    await self.streaming_pattern.close_stream(monitor_stream.stream_id)

                    return {
                        "status": "success",
                        "workflow_id": workflow_id,
                        "results": final_output
                    }
                else:
                    # Pipeline failed
                    self.active_workflows[workflow_id]["status"] = "processing_failed"
                    self.active_workflows[workflow_id]["error"] = f"Pipeline failed with status: {pipeline_result.get('status')}"

                    # Send failure update via stream
                    await self.streaming_pattern.send_to_stream(
                        stream_id=monitor_stream.stream_id,
                        content={
                            "status": "failed",
                            "progress": progress,
                            "message": "Workflow processing failed",
                            "error": self.active_workflows[workflow_id]["error"]
                        }
                    )

                    # Emit failure event
                    await self.event_pattern.emit_event(
                        event_type="workflow_failed",
                        content={
                            "workflow_id": workflow_id,
                            "workflow_type": workflow_type,
                            "error": self.active_workflows[workflow_id]["error"]
                        }
                    )

                    # Close the monitoring stream
                    await self.streaming_pattern.close_stream(monitor_stream.stream_id)

                    return {
                        "status": "error",
                        "workflow_id": workflow_id,
                        "message": self.active_workflows[workflow_id]["error"]
                    }

        except Exception as e:
            # Handle any exceptions
            error_message = f"Workflow execution failed: {str(e)}"
            self.active_workflows[workflow_id]["status"] = "failed"
            self.active_workflows[workflow_id]["error"] = error_message

            # Try to emit failure event
            try:
                await self.event_pattern.emit_event(
                    event_type="workflow_failed",
                    content={
                        "workflow_id": workflow_id,
                        "workflow_type": workflow_type,
                        "error": error_message
                    }
                )
            except:
                pass

            return {
                "status": "error",
                "workflow_id": workflow_id,
                "message": error_message
            }
```

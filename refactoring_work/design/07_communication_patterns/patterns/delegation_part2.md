# Delegation Pattern (continued)

## Protocol Adaptations

The Delegation pattern adapts to different protocols while maintaining consistent semantics. This ensures protocol independence in alignment with OpenMAS architecture.

### A2A Protocol Adaptation

A2A protocol adapts the Delegation pattern using tasks:

```yaml
delegation:
  protocol_adaptations:
    a2a:
      use_tasks: true
      task_type: "delegation"
      result_handling: "callback"
```

**Adapter Implementation:**

```python
class A2ADelegationAdapter(ProtocolAdapter):
    """Adapts the Delegation pattern to A2A protocol."""
    
    async def process_incoming(self, message, pattern):
        """Process an incoming A2A message."""
        if message.get("type") == pattern.config.get("task_type", "delegation"):
            # Extract metadata
            metadata = message.get("metadata", {})
            
            # Determine message type from function
            function_type = metadata.get("function", "")
            delegation_id = metadata.get("delegation_id")
            
            if function_type == "request":
                # This is a delegation request
                return {
                    "id": message.get("id"),
                    "type": "delegation_request",
                    "delegation_id": delegation_id or str(uuid.uuid4()),
                    "content": {
                        "task_type": metadata.get("task_type"),
                        "task_data": message.get("input"),
                        "policy": metadata.get("policy")
                    },
                    "metadata": metadata
                }
                
            elif function_type == "acceptance":
                # This is a delegation acceptance
                return {
                    "id": message.get("id"),
                    "type": "delegation_acceptance",
                    "delegation_id": delegation_id,
                    "content": {
                        "status": "accepted"
                    },
                    "metadata": metadata
                }
                
            elif function_type == "rejection":
                # This is a delegation rejection
                return {
                    "id": message.get("id"),
                    "type": "delegation_rejection",
                    "delegation_id": delegation_id,
                    "content": {
                        "status": "rejected",
                        "reason": metadata.get("reason")
                    },
                    "metadata": metadata
                }
                
            elif function_type == "progress":
                # This is a progress update
                return {
                    "id": message.get("id"),
                    "type": "delegation_progress",
                    "delegation_id": delegation_id,
                    "content": {
                        "progress_percentage": metadata.get("progress"),
                        "status_message": metadata.get("status_message")
                    },
                    "metadata": metadata
                }
                
            elif function_type == "completion":
                # This is a delegation completion
                return {
                    "id": message.get("id"),
                    "type": "delegation_completion",
                    "delegation_id": delegation_id,
                    "content": {
                        "status": "completed",
                        "result": message.get("output")
                    },
                    "metadata": metadata
                }
                
            elif function_type == "failure":
                # This is a delegation failure
                return {
                    "id": message.get("id"),
                    "type": "delegation_failure",
                    "delegation_id": delegation_id,
                    "content": {
                        "status": "failed",
                        "error": message.get("error")
                    },
                    "metadata": metadata
                }
                
        return message
        
    async def prepare_outgoing(self, message, pattern):
        """Prepare an outgoing A2A message."""
        msg_type = message.get("type")
        delegation_id = message.get("delegation_id")
        
        if msg_type == "delegation_request":
            # Prepare delegation request
            task = {
                "type": pattern.config.get("task_type", "delegation"),
                "input": message.get("content", {}).get("task_data"),
                "metadata": {
                    "function": "request",
                    "delegation_id": delegation_id,
                    "task_type": message.get("content", {}).get("task_type"),
                    "policy": message.get("content", {}).get("policy"),
                    "delegator_id": message.get("metadata", {}).get("delegator_id"),
                    "delegate_id": message.get("metadata", {}).get("delegate_id"),
                    "priority": message.get("metadata", {}).get("priority"),
                    "timestamp": message.get("metadata", {}).get("timestamp")
                }
            }
            return task
            
        elif msg_type == "delegation_acceptance":
            # Prepare delegation acceptance
            task = {
                "type": pattern.config.get("task_type", "delegation"),
                "metadata": {
                    "function": "acceptance",
                    "delegation_id": delegation_id,
                    "delegate_id": message.get("metadata", {}).get("delegate_id"),
                    "timestamp": message.get("metadata", {}).get("timestamp")
                }
            }
            return task
            
        elif msg_type == "delegation_rejection":
            # Prepare delegation rejection
            task = {
                "type": pattern.config.get("task_type", "delegation"),
                "metadata": {
                    "function": "rejection",
                    "delegation_id": delegation_id,
                    "reason": message.get("content", {}).get("reason"),
                    "delegate_id": message.get("metadata", {}).get("delegate_id"),
                    "timestamp": message.get("metadata", {}).get("timestamp")
                }
            }
            return task
            
        elif msg_type == "delegation_progress":
            # Prepare progress update
            task = {
                "type": pattern.config.get("task_type", "delegation"),
                "metadata": {
                    "function": "progress",
                    "delegation_id": delegation_id,
                    "progress": message.get("content", {}).get("progress_percentage"),
                    "status_message": message.get("content", {}).get("status_message"),
                    "delegate_id": message.get("metadata", {}).get("delegate_id"),
                    "timestamp": message.get("metadata", {}).get("timestamp")
                }
            }
            return task
            
        elif msg_type == "delegation_completion":
            # Prepare delegation completion
            task = {
                "type": pattern.config.get("task_type", "delegation"),
                "output": message.get("content", {}).get("result"),
                "metadata": {
                    "function": "completion",
                    "delegation_id": delegation_id,
                    "delegate_id": message.get("metadata", {}).get("delegate_id"),
                    "timestamp": message.get("metadata", {}).get("timestamp")
                }
            }
            return task
            
        elif msg_type == "delegation_failure":
            # Prepare delegation failure
            task = {
                "type": pattern.config.get("task_type", "delegation"),
                "error": message.get("content", {}).get("error"),
                "metadata": {
                    "function": "failure",
                    "delegation_id": delegation_id,
                    "delegate_id": message.get("metadata", {}).get("delegate_id"),
                    "timestamp": message.get("metadata", {}).get("timestamp")
                }
            }
            return task
            
        return message
```

### MCP Protocol Adaptation

MCP protocol adapts the Delegation pattern using function calls:

```yaml
delegation:
  protocol_adaptations:
    mcp:
      use_function_calls: true
      request_function: "delegate_task"
      acceptance_function: "accept_delegation"
      rejection_function: "reject_delegation"
      progress_function: "report_progress"
      completion_function: "complete_delegation"
      failure_function: "fail_delegation"
```

**Adapter Implementation:**

```python
class MCPDelegationAdapter(ProtocolAdapter):
    """Adapts the Delegation pattern to MCP protocol."""
    
    async def process_incoming(self, message, pattern):
        """Process an incoming MCP message."""
        if message.get("type") == "function_call":
            function_name = message.get("name", "")
            args = message.get("arguments", {})
            
            if function_name == pattern.config.get("request_function", "delegate_task"):
                # This is a delegation request
                return {
                    "id": message.get("id"),
                    "type": "delegation_request",
                    "delegation_id": args.get("delegation_id") or str(uuid.uuid4()),
                    "content": {
                        "task_type": args.get("task_type"),
                        "task_data": args.get("task_data"),
                        "policy": args.get("policy")
                    },
                    "metadata": {
                        "delegator_id": args.get("delegator_id"),
                        "delegate_id": args.get("delegate_id"),
                        "priority": args.get("priority", "normal"),
                        "timestamp": datetime.now().isoformat(),
                        "timeout_ms": args.get("timeout_ms", 60000)
                    }
                }
                
            elif function_name == pattern.config.get("acceptance_function", "accept_delegation"):
                # This is a delegation acceptance
                return {
                    "id": message.get("id"),
                    "type": "delegation_acceptance",
                    "delegation_id": args.get("delegation_id"),
                    "content": {
                        "status": "accepted"
                    },
                    "metadata": {
                        "delegate_id": args.get("delegate_id"),
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
            elif function_name == pattern.config.get("rejection_function", "reject_delegation"):
                # This is a delegation rejection
                return {
                    "id": message.get("id"),
                    "type": "delegation_rejection",
                    "delegation_id": args.get("delegation_id"),
                    "content": {
                        "status": "rejected",
                        "reason": args.get("reason")
                    },
                    "metadata": {
                        "delegate_id": args.get("delegate_id"),
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
            elif function_name == pattern.config.get("progress_function", "report_progress"):
                # This is a progress update
                return {
                    "id": message.get("id"),
                    "type": "delegation_progress",
                    "delegation_id": args.get("delegation_id"),
                    "content": {
                        "progress_percentage": args.get("progress"),
                        "status_message": args.get("status_message")
                    },
                    "metadata": {
                        "delegate_id": args.get("delegate_id"),
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
            elif function_name == pattern.config.get("completion_function", "complete_delegation"):
                # This is a delegation completion
                return {
                    "id": message.get("id"),
                    "type": "delegation_completion",
                    "delegation_id": args.get("delegation_id"),
                    "content": {
                        "status": "completed",
                        "result": args.get("result")
                    },
                    "metadata": {
                        "delegate_id": args.get("delegate_id"),
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
            elif function_name == pattern.config.get("failure_function", "fail_delegation"):
                # This is a delegation failure
                return {
                    "id": message.get("id"),
                    "type": "delegation_failure",
                    "delegation_id": args.get("delegation_id"),
                    "content": {
                        "status": "failed",
                        "error": args.get("error")
                    },
                    "metadata": {
                        "delegate_id": args.get("delegate_id"),
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
        elif message.get("type") == "function_result":
            # This could be a result of a delegation request
            result = message.get("result", {})
            
            if "delegation_id" in result:
                return {
                    "id": message.get("id"),
                    "type": "delegation_request_response",
                    "delegation_id": result.get("delegation_id"),
                    "content": {
                        "status": "accepted" if not message.get("error") else "rejected",
                        "error": message.get("error")
                    }
                }
                
        return message
        
    async def prepare_outgoing(self, message, pattern):
        """Prepare an outgoing MCP message."""
        msg_type = message.get("type")
        
        if msg_type == "delegation_request":
            # Prepare delegation request
            function_call = {
                "type": "function_call",
                "name": pattern.config.get("request_function", "delegate_task"),
                "arguments": {
                    "delegation_id": message.get("delegation_id"),
                    "task_type": message.get("content", {}).get("task_type"),
                    "task_data": message.get("content", {}).get("task_data"),
                    "policy": message.get("content", {}).get("policy"),
                    "delegator_id": message.get("metadata", {}).get("delegator_id"),
                    "delegate_id": message.get("metadata", {}).get("delegate_id"),
                    "priority": message.get("metadata", {}).get("priority"),
                    "timeout_ms": message.get("metadata", {}).get("timeout_ms")
                }
            }
            return function_call
            
        elif msg_type == "delegation_acceptance":
            # Prepare delegation acceptance
            function_call = {
                "type": "function_call",
                "name": pattern.config.get("acceptance_function", "accept_delegation"),
                "arguments": {
                    "delegation_id": message.get("delegation_id"),
                    "delegate_id": message.get("metadata", {}).get("delegate_id")
                }
            }
            return function_call
            
        elif msg_type == "delegation_rejection":
            # Prepare delegation rejection
            function_call = {
                "type": "function_call",
                "name": pattern.config.get("rejection_function", "reject_delegation"),
                "arguments": {
                    "delegation_id": message.get("delegation_id"),
                    "reason": message.get("content", {}).get("reason"),
                    "delegate_id": message.get("metadata", {}).get("delegate_id")
                }
            }
            return function_call
            
        elif msg_type == "delegation_progress":
            # Prepare progress update
            function_call = {
                "type": "function_call",
                "name": pattern.config.get("progress_function", "report_progress"),
                "arguments": {
                    "delegation_id": message.get("delegation_id"),
                    "progress": message.get("content", {}).get("progress_percentage"),
                    "status_message": message.get("content", {}).get("status_message"),
                    "delegate_id": message.get("metadata", {}).get("delegate_id")
                }
            }
            return function_call
            
        elif msg_type == "delegation_completion":
            # Prepare delegation completion
            function_call = {
                "type": "function_call",
                "name": pattern.config.get("completion_function", "complete_delegation"),
                "arguments": {
                    "delegation_id": message.get("delegation_id"),
                    "result": message.get("content", {}).get("result"),
                    "delegate_id": message.get("metadata", {}).get("delegate_id")
                }
            }
            return function_call
            
        elif msg_type == "delegation_failure":
            # Prepare delegation failure
            function_call = {
                "type": "function_call",
                "name": pattern.config.get("failure_function", "fail_delegation"),
                "arguments": {
                    "delegation_id": message.get("delegation_id"),
                    "error": message.get("content", {}).get("error"),
                    "delegate_id": message.get("metadata", {}).get("delegate_id")
                }
            }
            return function_call
            
        elif msg_type == "delegation_request_response":
            # Prepare response to a delegation request
            function_result = {
                "type": "function_result",
                "result": {
                    "delegation_id": message.get("delegation_id"),
                    "status": message.get("content", {}).get("status")
                },
                "error": message.get("content", {}).get("status") == "rejected" and message.get("content", {}).get("error")
            }
            return function_result
            
        return message
```

## Integration with Topologies

The Delegation pattern is commonly used in these topology relationships:

1. **Hierarchical**: Managers delegating to workers
2. **Centralized**: Coordinator delegating to team members
3. **Mesh**: Peers delegating based on specialization
4. **Market**: Task allocation through bidding/delegation

**Example Configuration:**

```yaml
topology:
  pattern: "hierarchical"
  roles:
    types:
      - name: "manager"
      - name: "worker"
  relationships:
    types:
      - name: "manager_to_worker"
        communication_patterns:
          primary: "delegation"
      - name: "worker_to_worker"
        communication_patterns:
          secondary: "delegation"
```

## Security Considerations

The Delegation pattern includes these security features:

1. **Task Authorization**: Permissions for delegating and accepting tasks
2. **Capability Verification**: Ensuring delegates have required capabilities
3. **Delegator Authentication**: Verifying the identity of delegators
4. **Delegation Scope Control**: Limiting the scope of delegated tasks
5. **Audit Logging**: Tracking of delegation for compliance

**Security Configuration:**

```yaml
delegation:
  options:
    security:
      require_authentication: true
      authorization:
        delegator_roles: ["manager", "coordinator"]
        delegate_roles:
          data_processing: ["data_processor"]
          information_retrieval: ["information_retriever"]
      capability_verification:
        enabled: true
        verification_method: "capability_registry"
      delegation_scope:
        enabled: true
        scope_enforcement: "policy_based"
```

## Observability

The Delegation pattern supports observability:

1. **Delegation Metrics**: Delegation volume, acceptance rate, completion rate
2. **Task Performance**: Execution time, success rate by task type
3. **Delegation Tracing**: End-to-end tracing from delegation to completion
4. **Status Logging**: Detailed logging of delegation lifecycle
5. **Delegation Visualization**: Visual representation of delegation relationships

**Metrics Example:**

```
delegations_created_total{task_type="data_processing"} 458
delegations_accepted_total{task_type="data_processing"} 432
delegations_rejected_total{task_type="data_processing"} 26
delegation_completion_rate{task_type="data_processing"} 0.94
delegation_execution_time_ms{task_type="data_processing"} 12586
active_delegations{agent="coordinator"} 12
```

## Unified Configuration Schema Integration

The Delegation pattern integrates with OpenMAS's unified configuration schema:

```yaml
# Delegation pattern in the unified configuration schema
communication_patterns:
  delegation:
    options:
      task_types:
        - name: "data_processing"
          schema: "data_processing_schema"
        - name: "information_retrieval"
          schema: "retrieval_schema"
      delegation_policies:
        - name: "time_sensitive"
          timeout: 60000
          priority: "high"
      delegate_selection:
        strategy: "capability_match"
    protocol_adaptations:
      a2a:
        use_tasks: true
        task_type: "delegation"
      mcp:
        use_function_calls: true
        request_function: "delegate_task"
```

## Reasoning Agnosticism

The Delegation pattern maintains OpenMAS's distinctive reasoning agnosticism by:

1. **Task-Oriented Interface**: Defining tasks in terms of inputs and outputs without mandating how the reasoning is performed
2. **Body-Brain Separation**: Delegation connects agents' communication interfaces (body) but makes no assumptions about their reasoning approaches (brain)
3. **Implementation Neutrality**: Both delegator and delegate can use any reasoning approach
4. **Metadata Separation**: Delegation metadata is separated from reasoning-specific data

This enables effective delegation between agents with different reasoning approaches:

- Rule-based agents for well-defined procedural tasks
- BDI agents for goal-oriented problem solving
- LLM-based agents for complex language tasks
- Knowledge Representation and Reasoning (KR&R) agents for inference tasks
- Hybrid approaches that combine multiple reasoning paradigms

For example, a manager agent with BDI reasoning might delegate a complex text analysis task to an LLM-based agent, which then delegates structured data processing to a rule-based agent.

## Protocol Independence

The Delegation pattern works consistently across protocols:

- **A2A**: Using task-based delegation
- **MCP**: Using function-based delegation
- **HTTP**: Using REST endpoints for delegation operations
- **gRPC**: Using service method calls for delegation
- **MQTT**: Using topic-based delegation messaging

This protocol independence enables agents to delegate tasks using the same pattern regardless of the underlying protocol implementation.

## Best Practices

1. **Well-Defined Tasks**: Define tasks with clear inputs, outputs, and success criteria
2. **Appropriate Delegation Policies**: Select policies based on task requirements
3. **Effective Delegate Selection**: Choose delegates based on capabilities and availability
4. **Proper Error Handling**: Handle rejections and failures gracefully
5. **Progress Monitoring**: For long-running tasks, implement progress reporting
6. **Resource Awareness**: Consider delegate capacity and workload
7. **Timeout Management**: Set appropriate timeouts for different task types

## Anti-Patterns

1. **Micromanagement**: Over-specifying how delegates should perform tasks
2. **Delegation Chains**: Creating long chains of delegations without oversight
3. **Capability Mismatch**: Delegating to agents without necessary capabilities
4. **Ignoring Context**: Failing to provide necessary context with the task
5. **Task Ambiguity**: Poorly defined tasks leading to misinterpretation
6. **Overly Complex Tasks**: Delegating tasks that should be broken down

## Use Cases

### 1. Information Retrieval

A personal assistant agent delegating information retrieval:

```python
# Personal assistant delegating information retrieval
async def handle_user_query(self, query):
    # Identify the query type
    query_type = self.classify_query(query)
    
    if query_type == "information_retrieval":
        # Delegate to a specialized information retrieval agent
        delegation = await self.delegation_pattern.delegate_task(
            task_type="information_retrieval",
            task_data={
                "query": query,
                "sources": ["web", "knowledge_base"],
                "max_results": 5
            },
            policy="standard"
        )
        
        # Wait for the results
        result = await delegation.wait_for_completion(timeout=30)
        
        if result and result["status"] == "completed":
            # Process and present the information
            return self.format_information(result["output"])
        else:
            # Handle failure
            return "I couldn't find that information right now."
    else:
        # Handle other query types
        pass

# Information retrieval agent handling delegation
async def handle_delegation_request(self, delegation_id, task_type, task_data, policy, metadata):
    if task_type == "information_retrieval":
        # Accept the delegation
        await self.delegation_pattern.accept_delegation(delegation_id)
        
        # Extract query parameters
        query = task_data.get("query")
        sources = task_data.get("sources", ["knowledge_base"])
        max_results = task_data.get("max_results", 5)
        
        try:
            # Report starting
            await self.delegation_pattern.report_progress(
                delegation_id=delegation_id,
                progress=0,
                status_message="Starting information retrieval"
            )
            
            # Gather information from sources
            results = []
            
            # Report progress for each source
            for i, source in enumerate(sources):
                progress = int((i / len(sources)) * 100)
                await self.delegation_pattern.report_progress(
                    delegation_id=delegation_id,
                    progress=progress,
                    status_message=f"Searching {source}"
                )
                
                # Get information from the source
                source_results = await self.information_service.search(
                    query=query,
                    source=source,
                    max_results=max_results
                )
                
                results.extend(source_results)
                
            # Limit to max results
            results = results[:max_results]
            
            # Complete the delegation with results
            await self.delegation_pattern.complete_delegation(
                delegation_id=delegation_id,
                result={
                    "query": query,
                    "results": results,
                    "sources": sources,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            # Report failure
            await self.delegation_pattern.fail_delegation(
                delegation_id=delegation_id,
                error={
                    "message": str(e),
                    "type": type(e).__name__
                }
            )
```

### 2. Task Decomposition and Delegation

A workflow agent decomposing and delegating tasks:

```python
# Workflow coordinator decomposing tasks
async def process_workflow_item(self, workflow_item):
    # Decompose the workflow item into subtasks
    subtasks = self.decompose_workflow_item(workflow_item)
    
    # Track delegations
    delegations = []
    
    # Delegate each subtask
    for subtask in subtasks:
        # Find appropriate delegate based on subtask type
        delegate_id = await self.find_delegate_for_subtask(subtask["type"])
        
        if delegate_id:
            # Create delegation
            delegation = await self.delegation_pattern.delegate_task(
                task_type=subtask["type"],
                task_data=subtask["data"],
                policy=subtask.get("priority", "standard"),
                delegates=[delegate_id]
            )
            
            delegations.append({
                "subtask_id": subtask["id"],
                "delegation": delegation
            })
        else:
            # Handle no delegate found
            self.logger.warning(f"No delegate found for subtask: {subtask['id']}")
            
    # Wait for all delegations to complete
    results = {}
    for delegation_info in delegations:
        subtask_id = delegation_info["subtask_id"]
        delegation = delegation_info["delegation"]
        
        # Wait for completion
        result = await delegation.wait_for_completion()
        
        if result and result["status"] == "completed":
            results[subtask_id] = result["output"]
        else:
            # Handle delegation failure
            self.logger.error(f"Delegation failed for subtask: {subtask_id}")
            
    # Integrate results
    integrated_result = self.integrate_results(results)
    
    return integrated_result
```

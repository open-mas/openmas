# Delegation Pattern

The Delegation pattern enables an agent to delegate tasks or responsibilities to other agents, enabling distributed task execution and specialization of roles.

## Overview

Delegation allows an agent (the delegator) to transfer a task to another agent (the delegate) for execution, optionally monitoring progress and receiving results. This pattern is essential for distributed workflows, load balancing, and specialization.

![Delegation Pattern](../assets/delegation_pattern.png)

## Key Components

1. **Delegator**: The agent delegating a task
2. **Delegate**: The agent accepting and executing the delegated task
3. **Task**: The work unit being delegated
4. **Task Context**: Information needed to execute the task
5. **Delegation Policy**: Rules and constraints governing the delegation
6. **Result Handling**: How results are returned to the delegator

## Pattern Sequence

1. **Task Preparation**: The delegator defines the task and required context
2. **Delegate Selection**: Identifying an appropriate delegate agent
3. **Delegation Request**: Requesting task execution from the delegate
4. **Acceptance/Rejection**: The delegate's response to the delegation
5. **Task Execution**: The delegate performing the delegated task
6. **Progress Reporting**: Optional updates from delegate to delegator
7. **Result Delivery**: Returning outcomes to the delegator
8. **Task Verification**: Delegator verifying the completed task

## Configuration Options

The Delegation pattern has these configuration options:

```yaml
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
      - name: "background"
        timeout: 300000
        priority: "low"
    delegate_selection:
      strategy: "capability_match"  # capability_match, round_robin, load_balanced
      fallback_strategy: "round_robin"
    monitoring:
      progress_updates: true
      update_interval_ms: 5000
    result_handling:
      delivery_mode: "push"  # push, pull
      callback_endpoint: "handle_delegation_result"
    error_handling:
      on_rejection: "fallback"  # fallback, retry, fail
      on_failure: "retry"  # retry, fail, reassign
      max_retries: 3
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
class DelegationPattern(Pattern):
    """Implementation of the Delegation pattern."""
    
    def __init__(self, options, agent_context):
        """Initialize the pattern."""
        super().__init__(options, agent_context)
        self.task_types = options.get("task_types", [])
        self.delegation_policies = options.get("delegation_policies", [])
        self.delegate_selection = options.get("delegate_selection", {})
        self.monitoring = options.get("monitoring", {})
        self.result_handling = options.get("result_handling", {})
        self.error_handling = options.get("error_handling", {})
        
        # Initialize delegation tracking
        self.active_delegations = {}
        self.delegate_capacity = {}
        
    async def delegate_task(self, task_type, task_data, policy=None, delegates=None, metadata=None):
        """Delegate a task to another agent."""
        # Create delegation ID
        delegation_id = str(uuid.uuid4())
        
        # Validate task type
        valid_task_types = [tt["name"] for tt in self.task_types]
        if task_type not in valid_task_types:
            raise ValueError(f"Invalid task type: {task_type}. Must be one of {valid_task_types}")
            
        # Get task schema
        task_schema = None
        for tt in self.task_types:
            if tt["name"] == task_type:
                task_schema = tt.get("schema")
                break
                
        # Validate task data against schema if needed
        if task_schema:
            # Schema validation would happen here
            pass
            
        # Get delegation policy
        policy_config = None
        if policy:
            for p in self.delegation_policies:
                if p["name"] == policy:
                    policy_config = p
                    break
                    
            if not policy_config:
                raise ValueError(f"Invalid policy: {policy}")
        else:
            # Use default policy if available
            policy_config = self.delegation_policies[0] if self.delegation_policies else {}
            
        # Select delegate if not specified
        delegate_id = None
        if delegates:
            # Use provided delegates
            strategy = self.delegate_selection.get("strategy", "capability_match")
            delegate_id = await self._select_delegate(delegates, task_type, strategy)
        else:
            # Find appropriate delegates
            suitable_delegates = await self._find_suitable_delegates(task_type)
            if not suitable_delegates:
                # Handle no suitable delegates
                if self.error_handling.get("on_rejection") == "fail":
                    raise ValueError(f"No suitable delegates found for task type: {task_type}")
                return None
                
            # Select from suitable delegates
            strategy = self.delegate_selection.get("strategy", "capability_match")
            delegate_id = await self._select_delegate(suitable_delegates, task_type, strategy)
            
        if not delegate_id:
            # Handle delegate selection failure
            if self.error_handling.get("on_rejection") == "fail":
                raise ValueError("Failed to select a delegate")
            return None
            
        # Create delegation request message
        request_message = {
            "id": str(uuid.uuid4()),
            "type": "delegation_request",
            "delegation_id": delegation_id,
            "content": {
                "task_type": task_type,
                "task_data": task_data,
                "policy": policy_config
            },
            "metadata": metadata or {}
        }
        
        # Add pattern metadata
        request_message["metadata"].update({
            "pattern": "delegation",
            "timestamp": datetime.now().isoformat(),
            "delegator_id": self.agent_context.agent_id,
            "delegate_id": delegate_id,
            "priority": policy_config.get("priority", "normal") if policy_config else "normal",
            "timeout_ms": policy_config.get("timeout", 60000) if policy_config else 60000
        })
        
        # Track the delegation
        self.active_delegations[delegation_id] = {
            "id": delegation_id,
            "task_type": task_type,
            "delegate_id": delegate_id,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "policy": policy_config,
            "retries": 0
        }
        
        # Get protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)
        
        # Prepare outgoing message
        prepared_request = await adapter.prepare_outgoing(request_message, self)
        
        # Send to delegate
        await self.agent_context.communicator.send_message(
            prepared_request, target_agent_id=delegate_id)
            
        # Create a delegation object for the caller
        delegation = Delegation(self, delegation_id)
        
        return delegation
        
    async def _select_delegate(self, delegates, task_type, strategy):
        """Select a delegate using the specified strategy."""
        if not delegates:
            return None
            
        if strategy == "capability_match":
            # Select by capability match (first available with matching capability)
            for delegate_id in delegates:
                # Check capabilities (simplified)
                return delegate_id
                
        elif strategy == "round_robin":
            # Simple round robin
            return delegates[0]
            
        elif strategy == "load_balanced":
            # Select by load
            min_load = float('inf')
            selected = None
            
            for delegate_id in delegates:
                load = self.delegate_capacity.get(delegate_id, 0)
                if load < min_load:
                    min_load = load
                    selected = delegate_id
                    
            return selected
            
        # Default: just take the first one
        return delegates[0]
        
    async def _find_suitable_delegates(self, task_type):
        """Find suitable delegates for a task type."""
        # This would typically query a directory service or registry
        # Simplified implementation returning a list of agents
        # In a real implementation, this would check agent capabilities
        return ["agent1", "agent2", "agent3"]
        
    async def accept_delegation(self, delegation_id, metadata=None):
        """Accept a delegation request."""
        # Create acceptance message
        acceptance_message = {
            "id": str(uuid.uuid4()),
            "type": "delegation_acceptance",
            "delegation_id": delegation_id,
            "content": {
                "status": "accepted"
            },
            "metadata": metadata or {}
        }
        
        # Add pattern metadata
        acceptance_message["metadata"].update({
            "pattern": "delegation",
            "timestamp": datetime.now().isoformat(),
            "delegate_id": self.agent_context.agent_id
        })
        
        # Get delegator from request metadata
        delegator_id = None
        request = self.agent_context.incoming_messages.get(delegation_id)
        if request:
            delegator_id = request.get("metadata", {}).get("delegator_id")
            
        if not delegator_id:
            raise ValueError(f"Could not determine delegator for delegation: {delegation_id}")
            
        # Get protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)
        
        # Prepare outgoing message
        prepared_acceptance = await adapter.prepare_outgoing(acceptance_message, self)
        
        # Send to delegator
        await self.agent_context.communicator.send_message(
            prepared_acceptance, target_agent_id=delegator_id)
            
        return acceptance_message["id"]
        
    async def reject_delegation(self, delegation_id, reason=None, metadata=None):
        """Reject a delegation request."""
        # Create rejection message
        rejection_message = {
            "id": str(uuid.uuid4()),
            "type": "delegation_rejection",
            "delegation_id": delegation_id,
            "content": {
                "status": "rejected",
                "reason": reason or "unavailable"
            },
            "metadata": metadata or {}
        }
        
        # Add pattern metadata
        rejection_message["metadata"].update({
            "pattern": "delegation",
            "timestamp": datetime.now().isoformat(),
            "delegate_id": self.agent_context.agent_id
        })
        
        # Get delegator from request metadata
        delegator_id = None
        request = self.agent_context.incoming_messages.get(delegation_id)
        if request:
            delegator_id = request.get("metadata", {}).get("delegator_id")
            
        if not delegator_id:
            raise ValueError(f"Could not determine delegator for delegation: {delegation_id}")
            
        # Get protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)
        
        # Prepare outgoing message
        prepared_rejection = await adapter.prepare_outgoing(rejection_message, self)
        
        # Send to delegator
        await self.agent_context.communicator.send_message(
            prepared_rejection, target_agent_id=delegator_id)
            
        return rejection_message["id"]
        
    async def report_progress(self, delegation_id, progress, status_message=None, metadata=None):
        """Report progress on a delegated task."""
        # Create progress message
        progress_message = {
            "id": str(uuid.uuid4()),
            "type": "delegation_progress",
            "delegation_id": delegation_id,
            "content": {
                "progress_percentage": progress,
                "status_message": status_message or ""
            },
            "metadata": metadata or {}
        }
        
        # Add pattern metadata
        progress_message["metadata"].update({
            "pattern": "delegation",
            "timestamp": datetime.now().isoformat(),
            "delegate_id": self.agent_context.agent_id
        })
        
        # Get delegator from request metadata
        delegator_id = None
        request = self.agent_context.incoming_messages.get(delegation_id)
        if request:
            delegator_id = request.get("metadata", {}).get("delegator_id")
            
        if not delegator_id:
            raise ValueError(f"Could not determine delegator for delegation: {delegation_id}")
            
        # Get protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)
        
        # Prepare outgoing message
        prepared_progress = await adapter.prepare_outgoing(progress_message, self)
        
        # Send to delegator
        await self.agent_context.communicator.send_message(
            prepared_progress, target_agent_id=delegator_id)
            
        return progress_message["id"]
        
    async def complete_delegation(self, delegation_id, result, metadata=None):
        """Complete a delegated task."""
        # Create completion message
        completion_message = {
            "id": str(uuid.uuid4()),
            "type": "delegation_completion",
            "delegation_id": delegation_id,
            "content": {
                "status": "completed",
                "result": result
            },
            "metadata": metadata or {}
        }
        
        # Add pattern metadata
        completion_message["metadata"].update({
            "pattern": "delegation",
            "timestamp": datetime.now().isoformat(),
            "delegate_id": self.agent_context.agent_id
        })
        
        # Get delegator from request metadata
        delegator_id = None
        request = self.agent_context.incoming_messages.get(delegation_id)
        if request:
            delegator_id = request.get("metadata", {}).get("delegator_id")
            
        if not delegator_id:
            raise ValueError(f"Could not determine delegator for delegation: {delegation_id}")
            
        # Get protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)
        
        # Prepare outgoing message
        prepared_completion = await adapter.prepare_outgoing(completion_message, self)
        
        # Send to delegator
        await self.agent_context.communicator.send_message(
            prepared_completion, target_agent_id=delegator_id)
            
        return completion_message["id"]
        
    async def fail_delegation(self, delegation_id, error, metadata=None):
        """Report failure of a delegated task."""
        # Create failure message
        failure_message = {
            "id": str(uuid.uuid4()),
            "type": "delegation_failure",
            "delegation_id": delegation_id,
            "content": {
                "status": "failed",
                "error": error
            },
            "metadata": metadata or {}
        }
        
        # Add pattern metadata
        failure_message["metadata"].update({
            "pattern": "delegation",
            "timestamp": datetime.now().isoformat(),
            "delegate_id": self.agent_context.agent_id
        })
        
        # Get delegator from request metadata
        delegator_id = None
        request = self.agent_context.incoming_messages.get(delegation_id)
        if request:
            delegator_id = request.get("metadata", {}).get("delegator_id")
            
        if not delegator_id:
            raise ValueError(f"Could not determine delegator for delegation: {delegation_id}")
            
        # Get protocol adapter
        protocol = self.agent_context.communicator.protocol
        adapter = self.get_protocol_adapter(protocol)
        
        # Prepare outgoing message
        prepared_failure = await adapter.prepare_outgoing(failure_message, self)
        
        # Send to delegator
        await self.agent_context.communicator.send_message(
            prepared_failure, target_agent_id=delegator_id)
            
        return failure_message["id"]
        
    async def get_delegation_status(self, delegation_id):
        """Get the status of a delegation."""
        if delegation_id not in self.active_delegations:
            return None
            
        delegation = self.active_delegations[delegation_id]
        
        return {
            "id": delegation["id"],
            "task_type": delegation["task_type"],
            "delegate_id": delegation["delegate_id"],
            "status": delegation["status"],
            "created_at": delegation["created_at"],
            "updated_at": delegation["updated_at"],
            "completed_at": delegation.get("completed_at")
        }
        
    async def process_incoming(self, message, protocol):
        """Process an incoming message."""
        adapter = self.get_protocol_adapter(protocol)
        transformed = await adapter.process_incoming(message, self)
        
        msg_type = transformed.get("type")
        delegation_id = transformed.get("delegation_id")
        
        if msg_type == "delegation_request":
            # Handle delegation request
            content = transformed.get("content", {})
            task_type = content.get("task_type")
            task_data = content.get("task_data")
            policy = content.get("policy")
            metadata = transformed.get("metadata", {})
            
            # Notify agent
            await self.agent_context.handle_delegation_request(
                delegation_id, task_type, task_data, policy, metadata)
                
        elif msg_type == "delegation_acceptance" and delegation_id in self.active_delegations:
            # Handle delegation acceptance
            delegation = self.active_delegations[delegation_id]
            delegation["status"] = "accepted"
            delegation["updated_at"] = datetime.now().isoformat()
            
            # Notify agent
            delegation_obj = Delegation(self, delegation_id)
            await self.agent_context.handle_delegation_acceptance(delegation_obj)
            
        elif msg_type == "delegation_rejection" and delegation_id in self.active_delegations:
            # Handle delegation rejection
            delegation = self.active_delegations[delegation_id]
            delegation["status"] = "rejected"
            delegation["updated_at"] = datetime.now().isoformat()
            rejection_reason = transformed.get("content", {}).get("reason")
            
            # Handle according to policy
            on_rejection = self.error_handling.get("on_rejection", "fail")
            
            if on_rejection == "retry" and delegation["retries"] < self.error_handling.get("max_retries", 3):
                # Retry delegation
                delegation["retries"] += 1
                delegation["status"] = "retrying"
                
                # Find a new delegate
                delegates = await self._find_suitable_delegates(delegation["task_type"])
                if delegates:
                    # Exclude the current delegate
                    delegates = [d for d in delegates if d != delegation["delegate_id"]]
                    
                    if delegates:
                        # Select new delegate
                        strategy = self.delegate_selection.get("strategy", "capability_match")
                        new_delegate = await self._select_delegate(delegates, delegation["task_type"], strategy)
                        
                        if new_delegate:
                            # Update delegation
                            delegation["delegate_id"] = new_delegate
                            
                            # Re-create delegation request
                            # (simplified - in a real implementation, this would reuse the original task data)
                            task_data = {}  # placeholder
                            await self.delegate_task(
                                task_type=delegation["task_type"],
                                task_data=task_data,
                                policy=delegation.get("policy", {}).get("name"),
                                delegates=[new_delegate]
                            )
                            return
            
            # If we get here, either the policy is "fail" or we've exhausted retries
            # Notify agent
            delegation_obj = Delegation(self, delegation_id)
            await self.agent_context.handle_delegation_rejection(
                delegation_obj, rejection_reason)
                
        elif msg_type == "delegation_progress" and delegation_id in self.active_delegations:
            # Handle progress update
            delegation = self.active_delegations[delegation_id]
            content = transformed.get("content", {})
            progress = content.get("progress_percentage", 0)
            status_message = content.get("status_message", "")
            
            # Update delegation
            delegation["progress"] = progress
            delegation["status_message"] = status_message
            delegation["updated_at"] = datetime.now().isoformat()
            
            # Notify agent
            delegation_obj = Delegation(self, delegation_id)
            await self.agent_context.handle_delegation_progress(
                delegation_obj, progress, status_message)
                
        elif msg_type == "delegation_completion" and delegation_id in self.active_delegations:
            # Handle completion
            delegation = self.active_delegations[delegation_id]
            content = transformed.get("content", {})
            result = content.get("result")
            
            # Update delegation
            delegation["status"] = "completed"
            delegation["updated_at"] = datetime.now().isoformat()
            delegation["completed_at"] = datetime.now().isoformat()
            
            # Notify agent
            delegation_obj = Delegation(self, delegation_id)
            await self.agent_context.handle_delegation_completion(
                delegation_obj, result)
                
        elif msg_type == "delegation_failure" and delegation_id in self.active_delegations:
            # Handle failure
            delegation = self.active_delegations[delegation_id]
            content = transformed.get("content", {})
            error = content.get("error")
            
            # Update delegation
            delegation["status"] = "failed"
            delegation["error"] = error
            delegation["updated_at"] = datetime.now().isoformat()
            
            # Handle according to policy
            on_failure = self.error_handling.get("on_failure", "fail")
            
            if on_failure == "retry" and delegation["retries"] < self.error_handling.get("max_retries", 3):
                # Retry delegation with same delegate
                delegation["retries"] += 1
                delegation["status"] = "retrying"
                
                # Re-create delegation request
                # (simplified - in a real implementation, this would reuse the original task data)
                task_data = {}  # placeholder
                await self.delegate_task(
                    task_type=delegation["task_type"],
                    task_data=task_data,
                    policy=delegation.get("policy", {}).get("name"),
                    delegates=[delegation["delegate_id"]]
                )
                return
                
            elif on_failure == "reassign":
                # Reassign to a different delegate
                delegation["retries"] += 1
                delegation["status"] = "reassigning"
                
                # Find a new delegate
                delegates = await self._find_suitable_delegates(delegation["task_type"])
                if delegates:
                    # Exclude the current delegate
                    delegates = [d for d in delegates if d != delegation["delegate_id"]]
                    
                    if delegates:
                        # Select new delegate
                        strategy = self.delegate_selection.get("strategy", "capability_match")
                        new_delegate = await self._select_delegate(delegates, delegation["task_type"], strategy)
                        
                        if new_delegate:
                            # Update delegation
                            delegation["delegate_id"] = new_delegate
                            
                            # Re-create delegation request
                            # (simplified - in a real implementation, this would reuse the original task data)
                            task_data = {}  # placeholder
                            await self.delegate_task(
                                task_type=delegation["task_type"],
                                task_data=task_data,
                                policy=delegation.get("policy", {}).get("name"),
                                delegates=[new_delegate]
                            )
                            return
            
            # If we get here, either the policy is "fail" or we've exhausted retries
            # Notify agent
            delegation_obj = Delegation(self, delegation_id)
            await self.agent_context.handle_delegation_failure(
                delegation_obj, error)
                
        return transformed
        
    async def prepare_outgoing(self, message, protocol):
        """Prepare an outgoing message."""
        adapter = self.get_protocol_adapter(protocol)
        return await adapter.prepare_outgoing(message, self)
```

### Delegation Class

```python
class Delegation:
    """Represents a delegation for the caller."""
    
    def __init__(self, pattern, delegation_id):
        """Initialize the delegation."""
        self.pattern = pattern
        self.delegation_id = delegation_id
        
    async def get_status(self):
        """Get the status of the delegation."""
        return await self.pattern.get_delegation_status(self.delegation_id)
        
    async def wait_for_completion(self, timeout=None):
        """Wait for the delegation to complete."""
        start_time = time.time()
        
        while True:
            status = await self.get_status()
            
            if not status:
                return None
                
            if status["status"] in ["completed", "failed", "rejected"]:
                return status
                
            # Check timeout
            if timeout and (time.time() - start_time > timeout):
                return {
                    "id": self.delegation_id,
                    "status": "timeout"
                }
                
            # Wait a bit before checking again
            await asyncio.sleep(0.5)
            
    async def cancel(self):
        """Cancel the delegation if possible."""
        # Create cancellation message
        cancellation_message = {
            "id": str(uuid.uuid4()),
            "type": "delegation_cancellation",
            "delegation_id": self.delegation_id,
            "content": {
                "reason": "cancelled_by_delegator"
            },
            "metadata": {
                "pattern": "delegation",
                "timestamp": datetime.now().isoformat(),
                "delegator_id": self.pattern.agent_context.agent_id
            }
        }
        
        # Get delegation
        delegation = self.pattern.active_delegations.get(self.delegation_id)
        if not delegation:
            return False
            
        # Ensure delegation is in a cancellable state
        if delegation["status"] in ["completed", "failed", "rejected"]:
            return False
            
        # Get delegate ID
        delegate_id = delegation["delegate_id"]
        
        # Get protocol adapter
        protocol = self.pattern.agent_context.communicator.protocol
        adapter = self.pattern.get_protocol_adapter(protocol)
        
        # Prepare outgoing message
        prepared_cancellation = await adapter.prepare_outgoing(cancellation_message, self.pattern)
        
        # Send to delegate
        await self.pattern.agent_context.communicator.send_message(
            prepared_cancellation, target_agent_id=delegate_id)
            
        # Update delegation status
        delegation["status"] = "cancelled"
        delegation["updated_at"] = datetime.now().isoformat()
        
        return True
```

# Context Management

## Overview

The OpenMAS Context Management system provides sophisticated handling of conversation history and context within sessions. It ensures that agents maintain appropriate context across interactions while optimizing for token efficiency and relevance.

## Core Capabilities

The Context Management system provides these key capabilities:

1. **History Tracking** - Recording and organizing conversation history
2. **Context Window Management** - Managing context size within model limits
3. **Intelligent Pruning** - Strategies for removing less relevant content
4. **Context Prioritization** - Identifying and preserving important context elements
5. **Protocol-Agnostic Design** - Consistent context handling across all protocols
6. **Reasoning-Agnostic Implementation** - Independence from specific reasoning approaches

## Configuration

Context management is configured through the unified configuration schema:

```yaml
sessions:
  context:
    max_history_items: 50
    max_tokens: 4000
    pruning_strategy: "selective"
    pruning_config:
      preserve_system_messages: true
      preserve_last_n_exchanges: 5
      summarization_prompt: "summarize_context"
```

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `max_history_items` | Maximum number of history items to store | 50 |
| `max_tokens` | Maximum number of tokens in context | 4000 |
| `pruning_strategy` | Strategy for pruning context when exceeding limits | "selective" |
| `preserve_system_messages` | Whether to always preserve system messages | true |
| `preserve_last_n_exchanges` | Number of recent exchanges to always preserve | 5 |
| `summarization_prompt` | Prompt template for context summarization | "summarize_context" |

## Pruning Strategies

The Context Management system supports multiple pruning strategies:

### 1. Truncation Strategy

Truncation simply removes the oldest messages when limits are reached:

```yaml
sessions:
  context:
    pruning_strategy: "truncate"
```

This is the simplest approach but may lose important context.

#### Implementation

```python
def _truncate_history(self, history):
    """Truncate history to max_history_items by removing oldest items."""
    if len(history) <= self.max_history_items:
        return history
        
    return history[-self.max_history_items:]
```

### 2. Summarization Strategy

Summarization replaces older parts of the conversation with concise summaries:

```yaml
sessions:
  context:
    pruning_strategy: "summarize"
    pruning_config:
      summarization_prompt: "summarize_conversation"
      summarization_window: 10
      preserve_last_n_exchanges: 5
```

This preserves more semantic content while reducing token usage.

#### Implementation

```python
async def _summarize_history(self, history):
    """Summarize older parts of history."""
    if len(history) <= self.max_history_items:
        return history
    
    # Always preserve the most recent exchanges
    preserve_count = self.pruning_config.get("preserve_last_n_exchanges", 5)
    recent_history = history[-preserve_count:] if preserve_count > 0 else []
    
    # Determine what to summarize
    to_summarize = history[:-preserve_count] if preserve_count > 0 else history
    
    # Nothing to summarize
    if not to_summarize:
        return history
    
    # Get the summarization prompt
    prompt_name = self.pruning_config.get("summarization_prompt", "summarize_context")
    
    # Summarize using the prompt management system
    prompt_manager = self._get_prompt_manager()
    summary = await prompt_manager.render_template(
        prompt_name,
        {"history": to_summarize}
    )
    
    # Create a summary message
    summary_message = {
        "role": "system",
        "content": f"Previous conversation summary: {summary}",
        "metadata": {
            "is_summary": True,
            "summarized_messages": len(to_summarize),
            "summary_time": datetime.now().isoformat()
        }
    }
    
    # Return the summary followed by recent history
    return [summary_message] + recent_history
```

### 3. Selective Strategy

Selective pruning intelligently selects which messages to preserve based on relevance:

```yaml
sessions:
  context:
    pruning_strategy: "selective"
    pruning_config:
      preserve_system_messages: true
      preserve_user_questions: true
      preserve_last_n_exchanges: 5
      importance_threshold: 0.7
```

This optimizes context quality by preserving the most important messages.

#### Implementation

```python
async def _selective_prune(self, history):
    """Selectively prune less important messages."""
    if len(history) <= self.max_history_items:
        return history
    
    # Always preserve system messages if configured
    preserve_system = self.pruning_config.get("preserve_system_messages", True)
    
    # Always preserve the most recent exchanges
    preserve_count = self.pruning_config.get("preserve_last_n_exchanges", 5)
    recent_indices = set(range(len(history) - preserve_count, len(history))) if preserve_count > 0 else set()
    
    # Score messages by importance
    scores = await self._score_message_importance(history)
    
    # Determine importance threshold
    threshold = self.pruning_config.get("importance_threshold", 0.7)
    
    # Select which messages to keep
    keep_indices = set()
    
    # Always keep recent messages
    keep_indices.update(recent_indices)
    
    # Add important messages
    for i, (message, score) in enumerate(zip(history, scores)):
        # Always keep system messages if configured
        if preserve_system and message.get("role") == "system":
            keep_indices.add(i)
        # Keep important messages
        elif score >= threshold:
            keep_indices.add(i)
    
    # If we're still over the limit, sort by importance and take the top N
    if len(keep_indices) > self.max_history_items:
        scored_indices = [(i, scores[i]) for i in keep_indices if i not in recent_indices]
        sorted_indices = sorted(scored_indices, key=lambda x: x[1], reverse=True)
        
        # Keep only the most important ones, plus the recent ones
        available_slots = self.max_history_items - len(recent_indices)
        important_indices = {idx for idx, _ in sorted_indices[:available_slots]}
        
        keep_indices = recent_indices.union(important_indices)
    
    # Build the pruned history
    pruned_history = [history[i] for i in sorted(keep_indices)]
    
    return pruned_history

async def _score_message_importance(self, history):
    """Score each message by importance."""
    # Implement relevance scoring logic
    # This could use simple heuristics or more sophisticated models
    scores = []
    
    for message in history:
        score = 0.0
        
        # Higher score for system messages
        if message.get("role") == "system":
            score += 0.3
        
        # Higher score for user messages
        if message.get("role") == "user":
            score += 0.2
        
        # Higher score for questions
        content = message.get("content", "")
        if "?" in content:
            score += 0.2
        
        # Higher score for longer messages (more content)
        content_length = len(content)
        score += min(0.2, content_length / 500)
        
        # Adjust for recency (older messages get lower scores)
        time_str = message.get("timestamp", "")
        if time_str:
            try:
                timestamp = datetime.fromisoformat(time_str)
                now = datetime.now()
                age_hours = (now - timestamp).total_seconds() / 3600
                recency_score = max(0, 0.3 - (age_hours / 24) * 0.1)
                score += recency_score
            except:
                pass
        
        scores.append(min(1.0, score))
    
    return scores
```

## Token Management

The Context Management system includes token counting to manage context size:

```python
async def get_token_count(self, history):
    """Estimate token count for history."""
    # Use the token counting utility
    from openmas.util.tokens import count_tokens
    
    total_tokens = 0
    
    for message in history:
        content = message.get("content", "")
        role = message.get("role", "")
        
        # Count tokens in the message
        message_tokens = count_tokens(f"{role}: {content}")
        total_tokens += message_tokens
        
        # Count tokens in function calls if present
        function_calls = message.get("function_calls", [])
        for call in function_calls:
            function_tokens = count_tokens(str(call))
            total_tokens += function_tokens
    
    return total_tokens
```

## Context Adapters

The Context Management system adapts context for different protocols:

### A2A Context Adaptation

A2A context is adapted to the A2A task protocol:

```python
async def adapt_for_a2a(self, context):
    """Adapt context for A2A protocol."""
    # Convert internal context format to A2A message parts
    parts = []
    
    for message in context:
        role = message.get("role", "")
        content = message.get("content", "")
        
        # Create appropriate part based on role
        if role == "user":
            parts.append({
                "type": "text",
                "content": content,
                "metadata": {"role": "user"}
            })
        elif role == "assistant":
            parts.append({
                "type": "text",
                "content": content,
                "metadata": {"role": "assistant"}
            })
        elif role == "system":
            parts.append({
                "type": "text",
                "content": content,
                "metadata": {"role": "system"}
            })
    
    return parts
```

### MCP Context Adaptation

MCP context is adapted to the MCP protocol:

```python
async def adapt_for_mcp(self, context):
    """Adapt context for MCP protocol."""
    # Convert internal context format to MCP messages
    messages = []
    
    for message in context:
        role = message.get("role", "")
        content = message.get("content", "")
        
        # Create MCP message
        mcp_message = {
            "role": role,
            "content": content
        }
        
        # Add function calls if present
        function_calls = message.get("function_calls", [])
        if function_calls:
            mcp_message["function_calls"] = function_calls
        
        messages.append(mcp_message)
    
    return messages
```

## Multi-Agent Context Sharing

The Context Management system supports sharing context across multiple agents:

```yaml
sessions:
  multi_agent:
    enabled: true
    context_sharing:
      strategy: "shared_db"
      scoped_by_conversation: true
```

This enables collaborative agent scenarios with shared context.

### Implementation

```python
class MultiAgentContextManager:
    """Manages context sharing across multiple agents."""
    
    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.enabled = config.get("enabled", False)
        self.sharing_config = config.get("context_sharing", {})
        self.strategy = self.sharing_config.get("strategy", "shared_db")
        self.scoped_by_conversation = self.sharing_config.get("scoped_by_conversation", True)
        
        # Set up appropriate storage based on strategy
        self.storage = self._create_storage()
    
    def _create_storage(self):
        """Create appropriate storage for the selected strategy."""
        if self.strategy == "shared_db":
            # Use database for shared context
            return SharedDatabaseContextStorage(self.sharing_config)
        elif self.strategy == "message_passing":
            # Use message passing for context sharing
            return MessagePassingContextStorage(self.sharing_config)
        else:
            # Default to in-memory storage
            return InMemoryContextStorage(self.sharing_config)
    
    async def share_context(self, agent_id, conversation_id, context):
        """Share context from an agent."""
        if not self.enabled:
            return
            
        # Get the context key
        context_key = self._get_context_key(agent_id, conversation_id)
        
        # Store in shared storage
        await self.storage.set(context_key, {
            "agent_id": agent_id,
            "conversation_id": conversation_id,
            "context": context,
            "updated_at": datetime.now().isoformat()
        })
    
    async def get_shared_context(self, agent_id, conversation_id):
        """Get shared context for an agent and conversation."""
        if not self.enabled:
            return []
            
        shared_context = []
        
        if self.scoped_by_conversation:
            # Get all contexts for this conversation
            context_keys = await self.storage.list_by_conversation(conversation_id)
            
            for key in context_keys:
                if key != self._get_context_key(agent_id, conversation_id):  # Skip own context
                    context_data = await self.storage.get(key)
                    if context_data:
                        shared_context.append(context_data)
        else:
            # Get all contexts (not scoped by conversation)
            context_keys = await self.storage.list_all()
            
            for key in context_keys:
                if not key.startswith(f"{agent_id}:"):  # Skip own contexts
                    context_data = await self.storage.get(key)
                    if context_data:
                        shared_context.append(context_data)
        
        return shared_context
    
    def _get_context_key(self, agent_id, conversation_id):
        """Get the storage key for a context."""
        if self.scoped_by_conversation:
            return f"{agent_id}:{conversation_id}"
        else:
            return f"{agent_id}"
```

## Reasoning Agnosticism

The Context Management system maintains OpenMAS's reasoning agnosticism by:

1. **Content Neutrality** - Managing context without assumptions about reasoning content
2. **Abstracted Message Format** - Using a neutral format that works with any reasoning approach
3. **Protocol Independence** - Supporting all protocols with the same core implementation
4. **Configurable Strategies** - Allowing tuning for different reasoning needs

This ensures that agents with different reasoning approaches (rule-based, BDI, LLM-based, hybrid) can use the same context management infrastructure without modification.

## Protocol Independence

The Context Management system ensures protocol independence by:

1. **Protocol Adapters** - Adapting context for different protocol requirements
2. **Common Internal Format** - Using a standardized internal representation
3. **Unified Configuration** - Consistent configuration across protocols

This allows context to be managed consistently whether using A2A, MCP, or other protocols.

## Integration with Other Components

The Context Management system integrates with several other OpenMAS components:

1. **Session Management** - Providing context as part of session state
2. **Prompt Management** - Using prompts for context summarization
3. **Agent System** - Supporting agent-specific context needs
4. **Unified Configuration** - Using the schema-based configuration system

"""Integration tests for MCP prompt functionality."""

import inspect

import pytest
import pytest_asyncio
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts.base import Prompt as McpPrompt

from openmas.prompt import PromptManager, get_prompt_manager
from openmas.prompt.providers.mcp import HAS_MCP, McpPromptManager

# Skip these tests if MCP is not installed
pytestmark = pytest.mark.skipif(not HAS_MCP, reason="MCP is not installed")

# Check if our code successfully detected MCP
if not HAS_MCP:
    pytest.skip("HAS_MCP is False despite MCP being installed", allow_module_level=True)


# Create the fixtures outside the test class using pytest_asyncio
@pytest_asyncio.fixture
async def prompt_manager():
    """Create a prompt manager with test prompts."""
    manager = PromptManager()

    # Create two test prompts for more comprehensive testing
    await manager.create_prompt(
        name="test_system_prompt",
        description="A test system prompt",
        system="You are a helpful assistant. Your name is TestBot.",
        template="The user asked: {{query}}",
    )

    await manager.create_prompt(
        name="test_complex_prompt",
        description="A more complex test prompt",
        system="You are a specialized assistant for {{domain}} tasks.",
        template="Please help with this {{domain}} question: {{question}}",
    )

    return manager


@pytest_asyncio.fixture
async def mcp_server():
    """Create a real MCP FastMCP instance for testing."""
    # Create a FastMCP instance with some configuration
    server = FastMCP(name="TestMcpServer", instructions="This is a test MCP server")

    # Verify this is using the actual MCP FastMCP implementation
    assert "mcp.server.fastmcp.server" in str(type(server).__module__), "Not using real MCP FastMCP"

    try:
        yield server
    finally:
        # No cleanup needed for this test fixture, but included for completeness
        pass


@pytest.mark.asyncio
async def test_mcp_server_capabilities():
    """Test that the MCP server has the expected capabilities for MCP 1.7+."""
    # Create a real FastMCP instance
    server = FastMCP()

    # Verify this is the actual MCP implementation
    assert "mcp.server.fastmcp.server" in str(type(server).__module__), "Not using real MCP FastMCP"

    # Verify critical methods exist and are callable
    assert hasattr(server, "add_prompt"), "MCP server missing add_prompt method"
    assert callable(server.add_prompt), "add_prompt should be callable"

    # Verify prompt manager exists
    assert hasattr(server, "_prompt_manager"), "MCP server missing prompt manager"

    # Verify prompt manager has expected methods
    assert hasattr(server._prompt_manager, "add_prompt"), "Prompt manager missing add_prompt method"
    assert hasattr(server._prompt_manager, "list_prompts"), "Prompt manager missing list_prompts method"
    assert callable(server._prompt_manager.list_prompts), "list_prompts should be callable"


@pytest.mark.asyncio
async def test_register_prompt_with_mcp(prompt_manager, mcp_server):
    """Test registering prompts with the MCP server using the real 1.7+ API."""
    # Create the McpPromptManager with our prompt manager - direct instantiation for clarity
    mcp_prompt_manager = McpPromptManager(prompt_manager)

    # Verify server is properly initialized (real MCP implementation)
    assert hasattr(mcp_server, "_prompt_manager"), "MCP server should have a prompt manager"
    initial_prompt_count = len(mcp_server._prompt_manager.list_prompts())

    # Register the prompts with the MCP server
    registered_names = await mcp_prompt_manager.register_all_prompts_with_server(mcp_server)

    # Verify we got the expected result
    assert isinstance(registered_names, list), "Expected a list to be returned"
    assert len(registered_names) == 2, "Expected 2 registered prompts"
    assert "test_system_prompt" in registered_names, "Expected test_system_prompt to be registered"
    assert "test_complex_prompt" in registered_names, "Expected test_complex_prompt to be registered"

    # Verify the prompts were actually registered with the real MCP server
    mcp_prompts = mcp_server._prompt_manager.list_prompts()
    assert len(mcp_prompts) == initial_prompt_count + 2, f"Expected {initial_prompt_count + 2} prompts in server"

    # Check each prompt was properly registered with the right properties
    prompt_names = [p.name for p in mcp_prompts]
    assert "test_system_prompt" in prompt_names, "test_system_prompt not found in registered prompts"
    assert "test_complex_prompt" in prompt_names, "test_complex_prompt not found in registered prompts"

    # Verify registered prompts are instances of the real MCP Prompt class
    for prompt in mcp_prompts:
        assert "mcp.server.fastmcp.prompts.base" in str(type(prompt).__module__), "Not using real MCP Prompt class"


@pytest.mark.asyncio
async def test_factory_integration(prompt_manager, mcp_server):
    """Test that the factory function creates a working MCP prompt manager."""
    # Create the prompt manager via the factory function - direct instantiation for clarity
    mcp_prompt_manager = get_prompt_manager(provider="mcp", prompt_manager=prompt_manager)

    # Verify the manager is the right type
    assert isinstance(mcp_prompt_manager, McpPromptManager), "Factory didn't return a McpPromptManager instance"

    # Register the prompts with the MCP server
    registered_names = await mcp_prompt_manager.register_all_prompts_with_server(mcp_server)

    # Verify we got the expected result
    assert isinstance(registered_names, list), "Expected a list to be returned"
    assert len(registered_names) == 2, "Expected 2 registered prompts"

    # Create a prompt handler for the test prompt
    handler = await mcp_prompt_manager.create_prompt_handler("test_system_prompt")

    # Verify we got a callable handler
    assert handler is not None, "Failed to create prompt handler"
    assert callable(handler), "Handler is not callable"

    # Call the handler
    result = await handler({"query": "What is your factory name?"})

    # Verify the result
    assert "The user asked: What is your factory name?" in result, "Factory prompt handler didn't work correctly"


@pytest.mark.asyncio
async def test_mcp_prompt_function_integration(prompt_manager, mcp_server):
    """Test the integration between our prompt function and MCP's prompt renderer."""
    # Create the McpPromptManager with our prompt manager - direct instantiation for clarity
    mcp_prompt_manager = McpPromptManager(prompt_manager)

    # Create a prompt function for the test prompt
    prompt_fn = await mcp_prompt_manager._create_prompt_function("test_complex_prompt")

    # Verify it's callable and is an async function
    assert prompt_fn is not None, "Failed to create prompt function"
    assert callable(prompt_fn), "Function is not callable"
    assert inspect.iscoroutinefunction(prompt_fn), "Function should be async"

    # Now create an MCP Prompt using this function
    mcp_prompt = McpPrompt.from_function(
        fn=prompt_fn,
        name="test_complex_prompt",
        description="A more complex test prompt",
    )

    # Verify this is a real MCP Prompt instance
    assert "mcp.server.fastmcp.prompts.base" in str(type(mcp_prompt).__module__), "Not using real MCP Prompt class"

    # Register it with the MCP server directly (testing the actual MCP add_prompt method)
    mcp_server.add_prompt(mcp_prompt)

    # Verify it was properly registered
    mcp_prompts = mcp_server._prompt_manager.list_prompts()
    found = False
    for p in mcp_prompts:
        if p.name == "test_complex_prompt":
            found = True
            break
    assert found, "Prompt was not properly registered with MCP server"

    # Now render the prompt with arguments using the real MCP prompt renderer
    result = await mcp_prompt.render({"domain": "finance", "question": "How do I budget?"})

    # Verify the result from the real MCP prompt renderer
    assert isinstance(result, list), "Expected a list of messages"
    assert len(result) > 0, "Expected at least one message"

    # Check the rendered content contains our template variables
    all_content = ""
    for msg in result:
        assert isinstance(msg, object), "Message should be an object"
        assert hasattr(msg, "content"), "Message should have content attribute"
        content = msg.content
        if hasattr(content, "text"):
            all_content += content.text + " "

    # Verify the template variables were properly rendered
    assert "finance" in all_content, "Domain variable not rendered in prompt"
    assert "How do I budget?" in all_content, "Question variable not rendered in prompt"


@pytest.mark.asyncio
async def test_create_prompt_handler(prompt_manager):
    """Test creating a prompt handler function for MCP."""
    # Create the McpPromptManager with our prompt manager - direct instantiation for clarity
    mcp_prompt_manager = McpPromptManager(prompt_manager)

    # Create a prompt handler for the test prompt
    handler = await mcp_prompt_manager.create_prompt_handler("test_system_prompt")

    # Verify we got a callable handler
    assert handler is not None, "Failed to create prompt handler"
    assert callable(handler), "Handler is not callable"
    assert inspect.iscoroutinefunction(handler), "Handler should be async"

    # Create a context with the structure for MCP 1.7+
    context = {"query": "What is your name?"}

    # Call the handler with the context
    result = await handler(context)

    # Verify the result includes both the system prompt and the rendered template
    assert "You are a helpful assistant" in result, "System prompt not in result"
    assert "The user asked: What is your name?" in result, "Rendered template not in result"


@pytest.mark.asyncio
async def test_prompt_handler_with_custom_object(prompt_manager):
    """Test the prompt handler with a non-dict context as a fallback case."""
    # Create the McpPromptManager with our prompt manager - direct instantiation for clarity
    mcp_prompt_manager = McpPromptManager(prompt_manager)

    # Create a prompt handler
    handler = await mcp_prompt_manager.create_prompt_handler("test_system_prompt")

    # Create a simple object with attributes (not the standard MCP 1.7+ format but as fallback)
    class CustomContext:
        def __init__(self):
            self.query = "What is your custom name?"

    context = CustomContext()

    # Call the handler with the custom object context
    result = await handler(context)

    # Verify it correctly extracts and uses the context attributes
    assert "You are a helpful assistant" in result, "System prompt not in result"
    assert "The user asked: What is your custom name?" in result, "Rendered template not in result"


@pytest.mark.asyncio
async def test_error_handling_invalid_prompt_name(prompt_manager, mcp_server):
    """Test error handling when using an invalid prompt name."""
    # Create the McpPromptManager with our prompt manager - direct instantiation for clarity
    mcp_prompt_manager = McpPromptManager(prompt_manager)

    # Try to create a handler for a non-existent prompt
    handler = await mcp_prompt_manager.create_prompt_handler("non_existent_prompt")

    # Should still return a handler (for error handling)
    assert handler is not None, "Should return a handler even for invalid prompt names"
    assert callable(handler), "Handler should be callable"

    # Call the handler
    result = await handler({"query": "test"})

    # Should contain error message
    assert "Prompt not found" in result, "Error message should indicate prompt not found"

    # Similarly, create a prompt function for a non-existent prompt
    prompt_fn = await mcp_prompt_manager._create_prompt_function("non_existent_prompt")

    # Should return None since this is an internal method
    assert prompt_fn is None, "Should return None for invalid prompt names"

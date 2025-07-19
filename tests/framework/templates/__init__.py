"""
OpenMAS Test Framework Templates

This module provides TDD-ready test framework templates for the core OpenMAS
interfaces, designed to prevent AI hallucination and ensure compatibility
with real protocol implementations.

The templates use real protocol data and comprehensive test patterns to
validate actual behavior rather than assumed behavior.
"""

from .protocol_adapter_tests import (
    IProtocolAdapterTestTemplate,
    create_protocol_adapter_test_suite,
    real_protocol_message_fixtures,
)

from .pattern_engine_tests import (
    IPatternEngineTestTemplate,
    create_pattern_engine_test_suite,
    pattern_execution_fixtures,
)

from .extension_registry_tests import (
    IExtensionRegistryTestTemplate,
    create_extension_registry_test_suite,
    extension_definition_fixtures,
)

from .common_fixtures import (
    simf_message_fixtures,
    real_mcp_messages,
    real_a2a_messages,
    real_http_messages,
    create_test_agent_config,
    create_test_protocol_config,
)

__all__ = [
    # Protocol Adapter Tests
    "IProtocolAdapterTestTemplate",
    "create_protocol_adapter_test_suite",
    "real_protocol_message_fixtures",
    
    # Pattern Engine Tests
    "IPatternEngineTestTemplate", 
    "create_pattern_engine_test_suite",
    "pattern_execution_fixtures",
    
    # Extension Registry Tests
    "IExtensionRegistryTestTemplate",
    "create_extension_registry_test_suite", 
    "extension_definition_fixtures",
    
    # Common Fixtures
    "simf_message_fixtures",
    "real_mcp_messages",
    "real_a2a_messages", 
    "real_http_messages",
    "create_test_agent_config",
    "create_test_protocol_config",
] 
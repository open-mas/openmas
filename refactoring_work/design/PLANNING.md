# PLANNING.MD - OpenMAS 0.3.0 Documentation Refinement

This document outlines the necessary refinements to the OpenMAS 0.3.0 design documentation to ensure implementation readiness.

## 1. Implementation Readiness Refinements

### 1.1 Agent Framework Enhancements

#### 1.1.1 Underspecified Message Handling Interfaces
    * **Problem**: Lack of explicit method signatures (parameter names, types, return types) for how an agent receives, processes, and sends messages in a protocol-agnostic way.
    * **Architectural Implication/Impact**: Medium to High. Developers would need to define these core interfaces, potentially leading to inconsistencies.
    * **Proposed Design Decision & Strategy for Resolution**: Define a clear `IMessageHandler` interface with methods like `receive_message(message_object)`, `process_incoming(internal_message)`, and `prepare_outgoing(internal_message) -> platform_specific_message`. Specify the structure of `message_object` and `internal_message` (potentially linking to `internal_message_format_standard.md`).
    * **Relevant Documents to be Updated**:
        * `00b_overview/04_agents/agent_framework_overview.md`
        * `00b_overview/01_architecture/internal_message_format_standard.md`
        * Relevant interaction documents (e.g., `agent_framework_protocol_layer.md`)

#### 1.1.2 Vague Capability Registration Mechanism
    * **Problem**: The specific API for capability registration (e.g., method signatures, structure of handler functions, schemas for input/output) is not detailed.
    * **Architectural Implication/Impact**: Medium. Difficulty in implementing a consistent way for agents to expose and for the framework to manage capabilities.
    * **Proposed Design Decision & Strategy for Resolution**: Define a `CapabilityManager` interface or methods within the Agent Framework like `register_capability(name: str, handler_function: Callable, input_schema: PydanticModel, output_schema: PydanticModel)`. Specify how `handler_function` should be structured.
    * **Relevant Documents to be Updated**:
        * `00b_overview/04_agents/agent_capabilities.md`
        * `00b_overview/04_agents/agent_framework_overview.md`

#### 1.1.3 Unclear State Management API
    * **Problem**: Specific methods for an agent to save, load, or subscribe to state changes are not clearly defined with data types.
    * **Architectural Implication/Impact**: Medium. Agents cannot reliably persist and retrieve their state, hindering long-running operations or recovery.
    * **Proposed Design Decision & Strategy for Resolution**: Define an `IAgentState` interface with methods like `save_state(key: str, value: Any, is_shared: bool = False)`, `load_state(key: str) -> Any`, `delete_state(key: str)`. Clarify serialization and deserialization mechanisms, and how "Any" is handled (e.g., JSON-serializable).
    * **Relevant Documents to be Updated**:
        * `00b_overview/04_agents/agent_framework_overview.md`
        * Potentially a new `00b_overview/04_agents/state_management_api.md`

### 1.2 Knowledge Representation & Reasoning (KR&R) System Enhancements

#### 1.2.1 Abstract `IKnowledgeBase` Interface Definition
    * **Problem**: `IKnowledgeBase` methods may be too abstract if the structure of `fact_data`, `query_structure`, etc., isn't concretely defined for each supported knowledge representation type.
    * **Architectural Implication/Impact**: High. Implementing both the KR&R system and Reasoning Engines will be difficult and prone to integration issues.
    * **Proposed Design Decision & Strategy for Resolution**: For each method in `IKnowledgeBase` (e.g., `add_fact`, `query_knowledge`), provide explicit Pydantic models or clearly defined schemas for all parameters and return types, with specific variants or union types to handle different knowledge representations (symbolic, graph, vector).
    * **Relevant Documents to be Updated**:
        * `00b_overview/09_knowledge_representation/knowledge_access_interfaces/interfaces.md`
        * `00b_overview/09_knowledge_representation/architecture.md`

#### 1.2.2 Undefined Knowledge Base Registry Access
    * **Problem**: The API for reasoning engines to discover or request specific knowledge bases from the central registry is unclear.
    * **Architectural Implication/Impact**: Medium. Reasoning engines cannot dynamically discover or select knowledge sources.
    * **Proposed Design Decision & Strategy for Resolution**: Define an `IKnowledgeBaseRegistry` interface with methods like `list_knowledge_bases(filter_criteria: Optional[dict]) -> List[KBInfo]`, `get_knowledge_base_accessor(name: str) -> IKnowledgeBase`. Define the `KBInfo` structure.
    * **Relevant Documents to be Updated**:
        * `00b_overview/09_knowledge_representation/architecture.md`
        * `00b_overview/09_knowledge_representation/knowledge_access_interfaces/interfaces.md` (or a new registry interface file)

### 1.3 Reasoning Engines Enhancements

#### 1.3.1 Ambiguous Standardized Invocation Interface
    * **Problem**: Unclear if a common way exists for the Agent Framework to initiate reasoning or pass goals/data, or if it's purely implementation-specific per engine type.
    * **Architectural Implication/Impact**: Medium. Integrating diverse reasoning engines might require more custom adapter code within the Agent Framework than anticipated if no common pattern is defined.
    * **Proposed Design Decision & Strategy for Resolution**: Define a minimal, standardized `IReasoningEngine` interface with a method like `execute_cycle(input_data: PydanticModel, knowledge_accessor: IKnowledgeBase, session_manager: ISessionManager) -> OutputDataModel`. Allow `input_data` and `OutputDataModel` to be generic but require them to be Pydantic models for clarity. Explicitly state this is the entry point the Agent Framework expects.
    * **Relevant Documents to be Updated**:
        * `00b_overview/01_architecture/reasoning_agnostic_design.md`
        * `00b_overview/09_knowledge_representation/reasoning/interfaces.md`
        * `00b_overview/04_agents/reasoning/README.md`

### 1.4 Protocol Layer Enhancements

#### 1.4.1 Undefined `IProtocolAdapter` Interface
    * **Problem**: Lack of explicit definition for the `IProtocolAdapter` interface that all protocol implementations must adhere to, including methods for sending/receiving, connection handling, etc.
    * **Architectural Implication/Impact**: High. Impossible to implement new protocols consistently, undermining multi-protocol support.
    * **Proposed Design Decision & Strategy for Resolution**: Define `IProtocolAdapter` with explicit methods like `connect(config: ProtocolConfig)`, `disconnect()`, `send(internal_message: InternalMessageFormat)`, `register_receive_callback(callback: Callable[[InternalMessageFormat], None])`, `get_status() -> ProtocolStatus`. Define associated data structures like `ProtocolConfig` (linking to unified schema) and `ProtocolStatus`.
    * **Relevant Documents to be Updated**:
        * `00b_overview/01_architecture/multi_protocol_design.md`
        * `00b_overview/02_protocols/protocol_integration_guide.md`
        * A new `00b_overview/02_protocols/iprotocol_adapter_interface.md`

#### 1.4.2 Unclear Message Pre/Post-processing Hook Integration
    * **Problem**: How pre/post-processing hooks or format adapters for protocol-specific message formats are registered or invoked is not detailed.
    * **Architectural Implication/Impact**: Medium. Difficulty in managing protocol-specific transformations cleanly.
    * **Proposed Design Decision & Strategy for Resolution**: Define interfaces for `IMessagePreprocessor` and `IMessagePostprocessor` (e.g., `process(data: Any, context: dict) -> Any`). Specify how these are registered with and invoked by the `Protocol Interface Factory` or `IProtocolAdapter` instances, possibly through configuration.
    * **Relevant Documents to be Updated**:
        * `00b_overview/01_architecture/multi_protocol_design.md`
        * `00b_overview/02_protocols/protocol_integration_guide.md`

#### 1.4.3 Insufficient Specificity in Internal Message Format
    * **Problem**: The `internal_message_format_standard.md` may lack detailed structure for all common data types, headers, and payload definitions.
    * **Architectural Implication/Impact**: High. Ambiguity in the core message format hinders reliable conversion to/from protocol-specific formats.
    * **Proposed Design Decision & Strategy for Resolution**: Augment `internal_message_format_standard.md` with a Pydantic model or detailed JSON schema defining all mandatory and optional fields, including header structure, payload type indicators, and metadata fields (e.g., message ID, timestamp, sender/receiver IDs, trace context).
    * **Relevant Documents to be Updated**:
        * `00b_overview/01_architecture/internal_message_format_standard.md`

### 1.5 Topology Management Enhancements

#### 1.5.1 Missing Topology Query API
    * **Problem**: Lack of a clear API for agents/framework to query topology information (roles, relationships, other agents).
    * **Architectural Implication/Impact**: Medium. Agents cannot easily understand their context or discover peers within the topology.
    * **Proposed Design Decision & Strategy for Resolution**: Define an `ITopologyManager` interface with methods like `get_agent_role(agent_id: str) -> str`, `get_agents_by_role(role_name: str) -> List[AgentInfo]`, `get_agent_relationships(agent_id: str, relationship_type: Optional[str]) -> List[RelationshipInfo]`. Define `AgentInfo` and `RelationshipInfo` structures.
    * **Relevant Documents to be Updated**:
        * `00b_overview/08_topology/architecture.md`
        * `00b_overview/04_agents/topologies/design_topology_system.md`

#### 1.5.2 Unclear Topology Pattern Management Interface
    * **Problem**: How topology patterns (Centralized, P2P, etc.) are programmatically or configuratively applied and managed beyond conceptual descriptions is unclear.
    * **Architectural Implication/Impact**: Medium. Difficulty in dynamically setting up or modifying agent network structures.
    * **Proposed Design Decision & Strategy for Resolution**: Detail how the `ITopologyManager` or a related configuration mechanism allows instantiation and parameterization of specific topology patterns. Clarify how configuration in `unified_configuration_schema.md` maps to these patterns and their runtime management.
    * **Relevant Documents to be Updated**:
        * `00b_overview/08_topology/architecture.md`
        * `00b_overview/04_agents/topologies/design_topology_system.md`
        * Relevant sections in `00b_overview/03_configuration/schema/agents.md` (or topology-specific schema file).

### 1.6 Communication Pattern Engine Enhancements

#### 1.6.1 Undefined Pattern Invocation API for Agents
    * **Problem**: Actual methods and signatures for an agent to *use* communication patterns (Request-Response, Pub-Sub) are not clearly specified.
    * **Architectural Implication/Impact**: High. Core to agent interaction; ambiguity hinders agent development.
    * **Proposed Design Decision & Strategy for Resolution**: Define a `CommunicationManager` (or similar) accessible to agents, with explicit methods for each supported pattern, e.g., `async request(target_agent_id: str, payload: PydanticModel, timeout_sec: float = 30.0) -> PydanticModel`, `publish(topic: str, payload: PydanticModel)`. Define schemas for payloads.
    * **Relevant Documents to be Updated**:
        * `00b_overview/01_architecture/communication_patterns_design.md`
        * `00b_overview/07_communication_patterns/README.md`
        * Specific pattern files in `00b_overview/07_communication_patterns/patterns/`

#### 1.6.2 Vague Pattern Adaptation Configuration Mechanism
    * **Problem**: How protocol-specific implementations of patterns are managed and configured, and how this is abstracted from the agent, is unclear.
    * **Architectural Implication/Impact**: Medium. Complexity in ensuring patterns work consistently across different transport protocols.
    * **Proposed Design Decision & Strategy for Resolution**: Detail in `00b_overview/07_communication_patterns/protocol_adaptations.md` how the `Communication Pattern Engine` interacts with the `Protocol Layer` to select and configure the correct underlying transport mechanism for a chosen pattern, based on agent configuration and target agent capabilities/protocol.
    * **Relevant Documents to be Updated**:
        * `00b_overview/07_communication_patterns/protocol_adaptations.md`
        * `00b_overview/01_architecture/communication_patterns_design.md`

### 1.7 Asset Management Enhancements

#### 1.7.1 Missing Asset Access & Interaction API
    * **Problem**: Lack of a clear API for retrieving and interacting with assets (e.g., model files, embeddings).
    * **Architectural Implication/Impact**: Medium to High. Components relying on dynamic asset loading (like LLM engines) will be blocked or require ad-hoc solutions.
    * **Proposed Design Decision & Strategy for Resolution**: Define an `IAssetManager` interface with methods like `get_asset_stream(asset_id: str, version: Optional[str] = None) -> StreamingResponse`, `get_asset_local_path(asset_id: str, version: Optional[str] = None) -> Path`, `get_asset_metadata(asset_id: str, version: Optional[str] = None) -> AssetMetadata`. Define `AssetMetadata` Pydantic model.
    * **Relevant Documents to be Updated**:
        * `00b_overview/10_asset_management/architecture.md`
        * `00b_overview/05_extensions/assets/design_asset_management.md`

#### 1.7.2 Undefined Asset-to-Protocol Transformation Mechanism
    * **Problem**: The mechanism and interfaces for asset-to-protocol format conversion (e.g., mapping assets to A2A message parts or MCP resources) are not detailed.
    * **Architectural Implication/Impact**: Medium. Difficulty in seamlessly using assets in multi-protocol communications.
    * **Proposed Design Decision & Strategy for Resolution**: Specify how the `Asset Management` system interacts with `Protocol Adapters` or a new set of `AssetFormatters` to transform assets into protocol-specific representations. Define an `IAssetFormatter` interface if applicable.
    * **Relevant Documents to be Updated**:
        * `00b_overview/10_asset_management/architecture.md`
        * `00b_overview/05_extensions/asset_resource_mapping.md`

#### 1.7.3 Unclear Asset Handling Strategy Specification
    * **Problem**: How a component specifies or queries which asset handling strategy (inline, reference, hybrid) is in use for a given asset or protocol is unclear.
    * **Architectural Implication/Impact**: Low to Medium. Could lead to inefficient asset handling or larger message sizes if not managed.
    * **Proposed Design Decision & Strategy for Resolution**: Clarify in `Asset Management` documentation how strategies are configured (globally, per asset type, per protocol) and if/how components can query this or express preferences. This primarily involves detailing relevant configuration schema sections.
    * **Relevant Documents to be Updated**:
        * `00b_overview/10_asset_management/architecture.md`
        * Relevant sections in `00b_overview/03_configuration/unified_configuration_schema.md`

### 1.8 Prompt Management Enhancements

#### 1.8.1 Undefined Prompt Retrieval & Formatting API
    * **Problem**: Specific API calls to fetch prompt templates and render them with context are not defined.
    * **Architectural Implication/Impact**: Medium. LLM-based components cannot easily or consistently access and utilize managed prompts.
    * **Proposed Design Decision & Strategy for Resolution**: Define an `IPromptManager` interface with methods like `get_formatted_prompt(template_name: str, version: Optional[str] = None, context_data: dict) -> str`, `get_prompt_template(template_name: str, version: Optional[str] = None) -> PromptTemplate`. Define `PromptTemplate` structure (e.g., template string, variable schema).
    * **Relevant Documents to be Updated**:
        * `00b_overview/11_prompt_management/architecture.md`
        * `00b_overview/05_extensions/prompts/design_prompt_management.md`

#### 1.8.2 Vague Prompt Validation Process/API
    * **Problem**: How "Validation of prompts against schema" is invoked or integrated into a workflow is unclear.
    * **Architectural Implication/Impact**: Low to Medium. Risk of runtime errors if prompt templates or context data do not match expectations.
    * **Proposed Design Decision & Strategy for Resolution**: Clarify if validation is primarily a CLI/authoring-time check or if there's a runtime validation API. If runtime, specify methods in `IPromptManager` like `validate_prompt_template(template_name: str, version: Optional[str] = None)` or `validate_context_for_template(template_name: str, context_data: dict)`.
    * **Relevant Documents to be Updated**:
        * `00b_overview/11_prompt_management/architecture.md`
        * `00b_overview/13_cli_tools/commands/validate.md` (if related to CLI)

### 1.9 Session Management Enhancements

#### 1.9.1 Missing Session Data Access API
    * **Problem**: Core API methods for session data access (CRUD, history) are not explicitly defined with signatures.
    * **Architectural Implication/Impact**: Medium to High. Essential for agents maintaining conversational context or persistent state.
    * **Proposed Design Decision & Strategy for Resolution**: Define an `ISessionManager` interface with methods like `set_data(key: str, value: Any)`, `get_data(key: str) -> Any`, `append_history(turn: ConversationTurn)`, `get_history(limit: Optional[int] = None) -> List[ConversationTurn]`. Define `ConversationTurn` structure.
    * **Relevant Documents to be Updated**:
        * `00b_overview/04_agents/sessions/design_session_management.md`
        * `00b_overview/04_agents/session_management.md`

#### 1.9.2 Undefined Multi-Agent Session Coordination Interfaces
    * **Problem**: Mechanisms and interfaces for how context is shared or managed in "Multi-Agent Sessions" are not sufficiently detailed.
    * **Architectural Implication/Impact**: Medium. Limits the development of sophisticated collaborative multi-agent scenarios.
    * **Proposed Design Decision & Strategy for Resolution**: Detail strategies for multi-agent session coordination (e.g., shared distributed cache, message-based state synchronization). If direct APIs are involved, define them within `ISessionManager` or a specialized `IMultiAgentSessionCoordinator` interface.
    * **Relevant Documents to be Updated**:
        * `00b_overview/04_agents/sessions/design_session_management.md`
        * `00b_overview/04_agents/sessions/multi_agent_sessions.md`

### 1.10 Extension System Enhancements

#### 1.10.1 Abstract Extension Point Interfaces
    * **Problem**: The specific, concrete interfaces (Abstract Base Classes, required methods/properties) for each type of extension point (Communicator, Agent, LLM, Tool, etc.) are likely not defined with enough precision.
    * **Architectural Implication/Impact**: High. Impossible to develop or integrate extensions in a standardized way, undermining the system's extensibility.
    * **Proposed Design Decision & Strategy for Resolution**: For each extension type listed in `00b_overview/05_extensions/extension_points/README.md`, create a dedicated markdown file defining its Python ABC or Protocol, including all required methods with full signatures (parameters, types, return types) and expected behaviors.
    * **Relevant Documents to be Updated**:
        * `00b_overview/05_extensions/extension_points/README.md` (and new files per extension type within this directory)
        * `00b_overview/05_extensions/design/design_extension_system.md`
        * Individual files in `00b_overview/05_extensions/extension_types/`

### 1.11 Observability System Enhancements

#### 1.11.1 Missing Telemetry Emission API
    * **Problem**: Lack of clear API calls for components to interact with the logging, metrics, and tracing subsystems.
    * **Architectural Implication/Impact**: Medium. Inconsistent observability if developers use disparate libraries or ad-hoc methods.
    * **Proposed Design Decision & Strategy for Resolution**: Define an `IObservabilityManager` or provide clear instructions on accessing pre-configured logger instances (e.g., `logging.getLogger(__name__)`), and define simple wrappers/APIs for metric emission (e.g., `metrics.increment_counter(name, tags)`) and trace span creation (`tracer.start_span(name)`).
    * **Relevant Documents to be Updated**:
        * `00b_overview/12_observability/architecture.md`
        * `00b_overview/12_observability/logging/README.md`
        * `00b_overview/12_observability/metrics/README.md`
        * `00b_overview/12_observability/tracing/README.md`

#### 1.11.2 Undefined Protocol-Specific Monitoring Hook Interfaces
    * **Problem**: How specialized monitoring for each protocol is implemented and what interfaces/callbacks the protocol layer needs to invoke in the observability system are unclear.
    * **Architectural Implication/Impact**: Low to Medium. May lead to incomplete or inconsistent monitoring data for specific protocols.
    * **Proposed Design Decision & Strategy for Resolution**: Define specific hook functions or event types that protocol adapters should emit to the observability system (e.g., `observability.log_protocol_event(protocol_name, event_type, data)`). Detail these in the `IProtocolAdapter` interface or related interaction documents.
    * **Relevant Documents to be Updated**:
        * `00b_overview/12_observability/architecture.md`
        * `00b_overview/01_architecture/component_interoperability/interactions/protocol_layer_observability.md`
        * `iprotocol_adapter_interface.md` (proposed new doc)

### 1.12 Deployment Management & CLI Tools Enhancements

#### 1.12.1 Insufficient Clarity in CLI Commands and Deployment Configurations
    * **Problem**: CLI command parameters, expected behaviors, and the schema for deployment-specific configuration files may be underspecified.
    * **Architectural Implication/Impact**: Medium. Developers may struggle to build, deploy, and manage OpenMAS instances efficiently.
    * **Proposed Design Decision & Strategy for Resolution**: For each CLI command in `00b_overview/13_cli_tools/commands/`, ensure all arguments and options are explicitly defined with their types and purposes. For deployment configurations (Docker, K8s, Cloud in `00b_overview/15_deployment/`), provide complete example manifest/configuration files and clearly document the schema for all customizable parameters, linking back to the `unified_configuration_schema.md` where applicable.
    * **Relevant Documents to be Updated**:
        * All files within `00b_overview/13_cli_tools/commands/`
        * All files within `00b_overview/15_deployment/` (especially in `containerization`, `kubernetes`, `cloud` subdirectories)
        * `00b_overview/03_configuration/unified_configuration_schema.md` (to ensure it covers all deployment params)
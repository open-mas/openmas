TASK: Define Agent Framework Message Handling API
Objective: To clearly define the interfaces and data structures for protocol-agnostic message handling within the Agent Framework, ensuring consistent message processing across different communication protocols.

Related Finding from PLANNING.MD: 1.1.1 Underspecified Message Handling Interfaces

Key Deliverables:

A clearly defined IMessageHandler (or equivalent) interface within the Agent Framework documentation.

Precise Pydantic models or schema definitions for InternalMessageFormat (referenced or detailed from internal_message_format_standard.md [cite: uploaded:00b_overview/01_architecture/internal_message_format_standard.md]) and any intermediate message objects used by the IMessageHandler.

Updated sequence diagrams or interaction descriptions illustrating the flow of a message through these new interfaces.

Detailed Sub-Tasks/Actions:

Review Existing Documentation:

Thoroughly review 00b_overview/04_agents/agent_framework_overview.md.

Analyze 00b_overview/01_architecture/internal_message_format_standard.md [cite: uploaded:00b_overview/01_architecture/internal_message_format_standard.md] for its current level of detail and suitability.

Examine relevant interaction documents, particularly 00b_overview/01_architecture/component_interoperability/interactions/agent_framework_protocol_layer.md [cite: uploaded:00b_overview/01_architecture/component_interoperability/interactions/agent_framework_protocol_layer.md].

Define InternalMessageFormat Pydantic Model:

Based on internal_message_format_standard.md [cite: uploaded:00b_overview/01_architecture/internal_message_format_standard.md], create a precise Pydantic model for the InternalMessageFormat.

Ensure it includes fields for:

message_id: str

sender_agent_id: Optional[str]

recipient_agent_id: Optional[str] (or topic: Optional[str])

protocol_name: str (source protocol)

timestamp: datetime

payload_type: str (e.g., 'text', 'json', 'binary', custom type identifier)

payload: Any (with clear guidance on serialization/deserialization or use of BaseModel for structured payloads)

metadata: Dict[str, Any] (for protocol-specific headers, trace context, etc.)

communication_pattern: Optional[str] (e.g., 'request-response', 'publish-subscribe')

Document this model clearly within or alongside internal_message_format_standard.md [cite: uploaded:00b_overview/01_architecture/internal_message_format_standard.md].

Design and Define IMessageHandler Interface:

Propose an interface (e.g., an Abstract Base Class in Python terms) named IMessageHandler or similar.

Define core methods, for example:

async def handle_incoming_message(self, raw_message_data: Any, source_protocol_adapter: IProtocolAdapter) -> None:

raw_message_data: The data as received from the protocol adapter.

source_protocol_adapter: Instance of the adapter that received the message.

This method would be responsible for converting raw_message_data (potentially using the source_protocol_adapter or a formatter) into the InternalMessageFormat.

It would then route the InternalMessageFormat object to the appropriate agent logic or capability.

async def prepare_outgoing_message(self, internal_message: InternalMessageFormat, target_protocol_adapter: IProtocolAdapter) -> Any:

internal_message: The message in the agent's standard internal format.

target_protocol_adapter: The protocol adapter that will send the message.

This method converts the InternalMessageFormat into the raw_message_data format expected by the target_protocol_adapter.

Returns the platform-specific message object.

Specify parameter types (using type hints, referencing the InternalMessageFormat Pydantic model and the IProtocolAdapter interface).

Specify return types.

Define Supporting Data Structures/Enums (if any):

For example, MessageProcessingStatus (e.g., RECEIVED, PROCESSING, ROUTED, FAILED).

Update Documentation:

In 00b_overview/04_agents/agent_framework_overview.md:

Add a new section detailing the IMessageHandler interface and its methods.

Explain how it supports protocol-agnostic message processing.

Clearly reference the InternalMessageFormat definition.

In 00b_overview/01_architecture/component_interoperability/interactions/agent_framework_protocol_layer.md [cite: uploaded:00b_overview/01_architecture/component_interoperability/interactions/agent_framework_protocol_layer.md]:

Update interaction descriptions and/or diagrams to reflect the use of IMessageHandler.

Show the sequence: Protocol Adapter receives -> calls IMessageHandler.handle_incoming_message -> InternalMessageFormat created -> Agent logic -> IMessageHandler.prepare_outgoing_message called -> Protocol Adapter sends.

Ensure internal_message_format_standard.md [cite: uploaded:00b_overview/01_architecture/internal_message_format_standard.md] is updated or clearly hosts the Pydantic model for InternalMessageFormat.

Provide Examples (Conceptual):

Include a brief conceptual example in the documentation showing how a message might be received, converted to InternalMessageFormat, processed, and then prepared for sending over a different protocol, highlighting the role of IMessageHandler.

Cross-references to be checked/updated:

00b_overview/01_architecture/multi_protocol_design.md [cite: uploaded:00b_overview/01_architecture/multi_protocol_design.md] (to ensure alignment with IProtocolAdapter interactions)

00b_overview/02_protocols/iprotocol_adapter_interface.md (once defined)

Any component documentation that describes sending or receiving messages at a high level.

Verification:

Are all method signatures in IMessageHandler explicit (parameters, types, return types)?

Is the InternalMessageFormat structure concretely defined and sufficient for various payload types and metadata?

Is the flow of message handling from protocol reception to agent logic and back to protocol transmission clear?

Progress Notes:

- Sub-task 1: Review Existing Documentation - **COMPLETED**
  - Thoroughly reviewed agent_framework_overview.md and found it provides a good high-level overview but lacks specific message handling interfaces
  - Analyzed internal_message_format_standard.md and found it contains comprehensive details about the message format structure but lacks Pydantic model definitions
  - Examined agent_framework_protocol_layer.md and identified the need to update it to reference the new message handling interface

- Sub-task 2: Define InternalMessageFormat Pydantic Model - **COMPLETED**
  - Created a comprehensive Pydantic model in `/01_architecture/models/internal_message_format.md` that directly corresponds to the specification in internal_message_format_standard.md
  - Implemented all required fields: message_id, session_id, timestamps, agent IDs, payload types, etc.
  - Structured the model with proper type hints, docstrings, and validation using Pydantic's Field class
  - Created payload models for all the specified payload types (text, structured data, assets, etc.)
  - Added usage examples to demonstrate how to create different types of messages

- Sub-task 3: Design and Define IMessageHandler Interface - **COMPLETED**
  - Created the IMessageHandler interface in `/04_agents/interfaces/message_handler_interface.md`
  - Defined core methods with explicit parameter types and return types:
    - handle_incoming_message(raw_message_data, source_protocol_adapter)
    - prepare_outgoing_message(internal_message, target_protocol_adapter, protocol_specific_options)
    - route_internal_message(internal_message)
    - create_internal_message(message_type, payload, target_agent_id, etc.)
  - Added detailed docstrings explaining each method's purpose, parameters, return values, and exceptions
  - Included a message flow sequence diagram illustrating message processing flow

- Sub-task 4: Define Supporting Data Structures - **COMPLETED**
  - Created MessageProcessingStatus enum in `/04_agents/models/message_processing.md`
  - Defined MessageProcessingResult class to capture message processing outcomes
  - Added MessageProcessingError hierarchy for standardized error handling
  - Implemented IMessageConverter interface for protocol adapters
  - Added usage examples to demonstrate practical application

- Sub-task 5: Update Documentation - **COMPLETED**
  - Added a new Message Handling section to agent_framework_overview.md
  - Updated the Core Components section to reference standardized message handling
  - Updated agent_framework_protocol_layer.md to reference the new IMessageHandler interface
  - Ensured all new components link back to relevant existing documentation

- Sub-task 6: Verification - **COMPLETED**
  - ✅ Method signatures in IMessageHandler are explicit with parameters, types, and return types
  - ✅ InternalMessageFormat structure is concretely defined and sufficient for various payload types and metadata
  - ✅ Flow of message handling from protocol reception to agent logic and back is clearly documented in sequence diagrams and text descriptions
  - ✅ All cross-references between documents are maintained and updated

- Decision Note: The IMessageHandler interface was designed to be fully asynchronous (using async/await) to support high-throughput, non-blocking message processing, which is critical for scalable agent systems dealing with multiple protocols simultaneously.

- Decision Note: Adopted a Pydantic-based approach for both the internal message format and processing results to leverage built-in validation and ensure type safety throughout the message handling pipeline.
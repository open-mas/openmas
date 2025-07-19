TASK: Specify Agent Framework Capability Registration API
Objective: To define a clear and specific API within the Agent Framework for agents to register their capabilities, including method signatures, the structure of handler functions, and schemas for inputs and outputs.

Related Finding from PLANNING.MD: 1.1.2 Vague Capability Registration Mechanism

Key Deliverables:

A defined ICapabilityManager interface or a set of clearly defined methods within the Agent Framework's core API for capability registration and discovery.

Specification of the expected signature and behavior for capability handler functions.

Clear guidelines on using Pydantic models for defining input and output schemas for capabilities.

Updated documentation reflecting these API definitions and usage examples.

Detailed Sub-Tasks/Actions:

Review Existing Documentation:

Thoroughly review 00b_overview/04_agents/agent_capabilities.md [cite: uploaded:00b_overview/04_agents/agent_capabilities.md] to understand the current conceptual framework.

Review 00b_overview/04_agents/agent_framework_overview.md [cite: uploaded:00b_overview/04_agents/agent_framework_overview.md] for any existing mentions or stubs related to capability management.

Design the Capability Registration API:

Option A: ICapabilityManager Interface:

Define an interface (e.g., Python ABC) ICapabilityManager.

Specify methods like:

async def register_capability(self, name: str, handler_function: Callable, input_schema: Type[BaseModel], output_schema: Type[BaseModel], description: Optional[str] = None, version: str = "1.0") -> None:

async def unregister_capability(self, name: str) -> None:

async def list_capabilities(self) -> List[CapabilityInfo]:

async def get_capability_details(self, name: str) -> Optional[CapabilityInfo]:

async def invoke_capability(self, name: str, input_data: BaseModel) -> BaseModel: (or the framework handles invocation directly based on incoming messages mapped to capabilities).

Option B: Direct Agent Framework Methods:

If a central manager is too heavy, define these methods directly on the agent's core object or a provided context object.

Define the CapabilityInfo Pydantic model:

name: str

description: Optional[str]

version: str

input_schema_definition: dict (JSON schema representation of the Pydantic model)

output_schema_definition: dict (JSON schema representation of the Pydantic model)

Potentially handler_function_name: str (for introspection)

Specify Capability Handler Function Signature:

Define the expected signature for functions that implement a capability. For example:

async def my_capability_handler(input_data: MyInputModel, agent_context: AgentContext) -> MyOutputModel:

input_data: An instance of the Pydantic model defined in input_schema.

agent_context: An object providing access to agent-specific resources (e.g., logger, state, communication manager). This needs to be defined.

Returns an instance of the Pydantic model defined in output_schema.

Clarify if handlers should be synchronous or asynchronous. (Asynchronous is preferred for non-blocking operations).

Define AgentContext (if used in handlers):

Specify the attributes and methods available on the AgentContext object passed to capability handlers (e.g., context.log, context.state_manager, context.communication_manager, context.get_config()).

Integrate with Message Handling (Conceptual):

Briefly describe how incoming messages (after being processed by IMessageHandler into InternalMessageFormat) might be routed to invoke a registered capability based on message content or metadata (e.g., a 'command' field in the payload, or a specific topic). This links to TASK_define_agent_framework_message_handling_api.md.

Update Documentation:

In 00b_overview/04_agents/agent_capabilities.md [cite: uploaded:00b_overview/04_agents/agent_capabilities.md]:

Add a new section detailing the capability registration API (ICapabilityManager or direct methods).

Provide the definition of CapabilityInfo.

Specify the required signature for capability handler functions.

Explain the role and structure of AgentContext if applicable.

Include clear examples of registering a capability, defining its Pydantic input/output models, and writing a handler function.

Update 00b_overview/04_agents/agent_framework_overview.md [cite: uploaded:00b_overview/04_agents/agent_framework_overview.md] to reference the new detailed capability registration API.

Ensure unified_configuration_schema.md [cite: uploaded:00b_overview/03_configuration/unified_configuration_schema.md] includes sections for agents to declare their capabilities if static declaration is also supported alongside programmatic registration.

Provide Examples:

A complete, albeit simple, example of:

Defining input and output Pydantic models for a capability.

Writing the capability handler function.

Registering the capability with the framework during agent initialization.

(Conceptual) How an incoming message might trigger this capability.

Cross-references to be checked/updated:

00b_overview/03_configuration/schema/agents.md [cite: uploaded:00b_overview/03_configuration/schema/agents.md] (if capabilities can be statically defined in config).

TASK_define_agent_framework_message_handling_api.md (for how messages trigger capabilities).

Reasoning Engine documentation (if reasoning engines expose themselves as capabilities).

Verification:

Is the API for registering, unregistering, and listing capabilities clear and unambiguous?

Is the expected structure and signature of a capability handler function well-defined?

Is the use of Pydantic models for input/output schemas clearly mandated and explained?

Are there sufficient examples for a developer to implement and register a new capability?

Progress Notes:

- **Sub-task 1: Review Existing Documentation** ✅ COMPLETED
  - Reviewed agent_capabilities.md to understand the current conceptual framework for capabilities
  - Reviewed agent_framework_overview.md to see how capabilities fit into the broader agent framework
  - Examined unified_configuration_schema.md to understand how capabilities are currently defined in configuration
  - Analyzed agents.md to see component-specific schema documentation for capabilities

- **Sub-task 2: Design the Capability Registration API** ✅ COMPLETED
  - Decision: Implemented Option A (ICapabilityManager Interface) as it provides a clean, centralized approach to capability management
  - Created a comprehensive interface definition with detailed method signatures, docstrings, and type hints
  - Ensured all methods are async to support non-blocking operations throughout the agent framework
  - Added a load_capabilities_from_config method to bridge between declarative (config) and programmatic registration

- **Sub-task 3: Define the CapabilityInfo Pydantic model** ✅ COMPLETED
  - Created a comprehensive CapabilityInfo model that includes all required fields
  - Added JSON schema representation fields to facilitate protocol adaptations
  - Included protocol_specific_names mapping to support multi-protocol capabilities
  - Added examples field to improve discoverability and documentation

- **Sub-task 4: Specify Capability Handler Function Signature** ✅ COMPLETED
  - Defined clear async function signature with input_data and context parameters
  - Ensured type hints indicate that input_data is a Pydantic model specific to the capability
  - Specified that the return value must conform to the output schema Pydantic model
  - Chose async function signature to ensure non-blocking operations

- **Sub-task 5: Define AgentContext** ✅ COMPLETED
  - Created a comprehensive AgentContext class with properties for all agent resources
  - Included access to logger, state_manager, communication_manager, etc.
  - Added specific methods for accessing configuration and session context
  - Ensured properties have clear return type annotations

- **Sub-task 6: Conceptual Integration with Message Handling** ✅ COMPLETED
  - Described the flow from protocol-specific message to capability invocation
  - Outlined how the capability system maintains separation between communication and reasoning
  - Detailed the four key steps in the message-to-capability process

- **Sub-task 7: Update Documentation** ✅ COMPLETED
  - Added Capability Registration API section to agent_capabilities.md
  - Enhanced Capability System section in agent_framework_overview.md
  - Added comprehensive example demonstrating all aspects of capability registration and usage
  - Ensured clear cross-references between documents

- **Verification Checks** ✅ ALL PASSED
  - ✅ API for registering, unregistering, and listing capabilities is clear and unambiguous
  - ✅ Structure and signature of capability handler functions is well-defined
  - ✅ Use of Pydantic models for input/output schemas is clearly mandated and explained
  - ✅ Comprehensive examples provided for implementing and registering capabilities

- **Key Design Decisions**:
  - Used a dedicated interface (ICapabilityManager) rather than embedding methods directly in the agent
  - Made all methods async to support non-blocking operations throughout the agent framework
  - Required Pydantic models for input/output schemas to ensure strong validation and schema generation
  - Added protocol_specific_names mapping to support OpenMAS's multi-protocol design
  - Created a comprehensive AgentContext to provide capability handlers with access to agent resources
  - Added explicit load_capabilities_from_config method to bridge declarative and programmatic approaches
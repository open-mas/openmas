TASK: Detail Agent Framework State Management API
Objective: To define a clear and specific API within the Agent Framework that allows agents to persistently save, load, and manage their internal state, including data types and serialization mechanisms.

Related Finding from PLANNING.MD: 1.1.3 Unclear State Management API

Key Deliverables:

A defined IAgentStateManager interface (or equivalent set of methods on an agent context object).

Clear specification of methods for creating, reading, updating, and deleting state entries.

Guidelines on data types that can be stored and the underlying serialization/deserialization mechanisms (e.g., JSON for Pydantic models, or support for raw bytes).

Consideration for state scopes (e.g., private to agent, shared within a session).

Updated documentation reflecting these API definitions and usage examples.

Detailed Sub-Tasks/Actions:

Review Existing Documentation:

Analyze 00b_overview/04_agents/agent_framework_overview.md [cite: uploaded:00b_overview/04_agents/agent_framework_overview.md] for current concepts of state management.

Review 00b_overview/04_agents/sessions/session_storage.md [cite: uploaded:00b_overview/04_agents/sessions/session_storage.md] and 00b_overview/04_agents/session_management.md [cite: uploaded:00b_overview/04_agents/session_management.md] for overlaps or distinctions between agent state and session state. This task focuses on general agent state that might live beyond a single session or be independent of it.

Design the IAgentStateManager Interface:

Define an interface, e.g., IAgentStateManager.

Specify core methods:

async def set_state(self, key: str, value: Any, scope: AgentStateScope = AgentStateScope.PRIVATE_PERSISTENT) -> None:

key: A string identifier for the state entry.

value: The data to be stored. Must be serializable (see point 3).

scope: An enum indicating the visibility/lifetime of the state (e.g., PRIVATE_PERSISTENT, SESSION_SCOPED, SHARED_GROUP - needs definition).

async def get_state(self, key: str, scope: AgentStateScope = AgentStateScope.PRIVATE_PERSISTENT) -> Optional[Any]:

Returns the deserialized state value, or None if not found.

async def delete_state(self, key: str, scope: AgentStateScope = AgentStateScope.PRIVATE_PERSISTENT) -> bool:

Returns True if deletion was successful or key didn't exist, False on failure.

async def has_state(self, key: str, scope: AgentStateScope = AgentStateScope.PRIVATE_PERSISTENT) -> bool:

async def list_state_keys(self, scope: AgentStateScope = AgentStateScope.PRIVATE_PERSISTENT, prefix: Optional[str] = None) -> List[str]:

Allows discovery of stored state keys.

Define the AgentStateScope enum (e.g., PRIVATE_PERSISTENT, SESSION_SPECIFIC_PERSISTENT, IN_MEMORY_SESSION_ONLY).

Specify Data Serialization and Supported Types:

Clearly state the default serialization mechanism (e.g., JSON).

If Pydantic models are passed as value, they should be automatically serialized to dict/JSON and deserialized back to model instances.

Specify support for primitive types: str, int, float, bool, list, dict.

Consider if raw bytes storage is needed for custom binary data.

Document any limitations (e.g., maximum size per entry if applicable, depending on the backend).

Define State Scopes and Lifetime:

Detail each AgentStateScope:

PRIVATE_PERSISTENT: State private to the agent, persists across agent restarts.

SESSION_SPECIFIC_PERSISTENT: State associated with a particular session ID, persists across restarts if the session can be resumed. (Requires integration with Session Management).

IN_MEMORY_SESSION_ONLY: State tied to the current active session, lost when session ends or agent restarts.

Explain how the backend storage mechanism might differ or be tagged based on scope.

Consider Advanced Features (Optional for first pass, but document as future):

State change notifications/subscriptions: async def subscribe_to_state_change(self, key: str, callback: Callable[[str, Any], None], scope: AgentStateScope).

Transactional updates for multiple keys.

Update Documentation:

Create a new document, e.g., 00b_overview/04_agents/agent_state_management_api.md, or add a major section to 00b_overview/04_agents/agent_framework_overview.md [cite: uploaded:00b_overview/04_agents/agent_framework_overview.md].

Detail the IAgentStateManager interface, its methods, and the AgentStateScope enum.

Clearly explain serialization, supported data types, and how Pydantic models are handled.

Provide examples of an agent saving its configuration, a counter, or a user preference.

Explain how developers can access the IAgentStateManager (e.g., via agent_context.state_manager).

Clarify the relationship and distinction between this general IAgentStateManager and the more specific ISessionManager (from TASK_define_session_management_data_access_api.md). They might use the same underlying storage but offer different semantics or scopes.

Configuration:

Specify how the underlying storage for agent state is configured (e.g., local file, database connection string) in the unified_configuration_schema.md [cite: uploaded:00b_overview/03_configuration/unified_configuration_schema.md].

Cross-references to be checked/updated:

00b_overview/04_agents/session_management.md [cite: uploaded:00b_overview/04_agents/session_management.md] (to clarify distinctions and potential integrations).

00b_overview/03_configuration/schema/agents.md [cite: uploaded:00b_overview/03_configuration/schema/agents.md] (for state backend configuration).

AgentContext definition (from TASK_specify_agent_framework_capability_registration_api.md).

Verification:

Is the API for CRUD operations on agent state clear and unambiguous?

Are supported data types and serialization methods explicitly stated?

Are state scopes and their implications well-defined?

Is it clear how an agent developer would use this API?

Is the configuration of the state backend clear?

Progress Notes:

### Completed Sub-tasks

* **Sub-task 1.1: Review Existing Documentation** - COMPLETED
  * Reviewed agent_framework_overview.md, session_management.md, and session_storage.md
  * Identified that state management is mentioned but not well-defined in the existing documentation
  * Noted the session storage interface which uses a similar pattern but is specific to sessions

* **Sub-task 1.2: Design the IAgentStateManager Interface** - COMPLETED
  * Designed a comprehensive interface with all required methods
  * Created the AgentStateScope enum with four well-defined scopes (PRIVATE_PERSISTENT, SESSION_SPECIFIC_PERSISTENT, IN_MEMORY_SESSION_ONLY, SHARED)
  * Added get_state_as_model() to provide direct Pydantic model integration
  * Added clear_scope() method for complete scope management

* **Sub-task 1.3: Specify Data Serialization and Supported Types** - COMPLETED
  * Defined support for JSON-serializable primitives (str, int, float, bool, list, dict)
  * Specified automatic handling of Pydantic models with serialization/deserialization
  * Added support for bytes storage for binary data
  * Documented serialization mechanisms and their limitations

* **Sub-task 1.4: Define State Scopes and Lifetime** - COMPLETED
  * Created detailed definitions for each state scope with clear implications
  * Documented how scopes affect persistence, visibility, and integration with sessions
  * Specified how namespacing works to prevent key collisions between scopes

* **Sub-task 1.5: Update Documentation** - COMPLETED
  * Created new comprehensive document at 04_agents/agent_state_management_api.md
  * Included detailed interface definition, usage examples, and implementation considerations
  * Added cross-references to related documentation

* **Sub-task 1.6: Configuration** - COMPLETED
  * Updated unified_configuration_schema.md with state management configuration
  * Added storage backend options (memory, file, database, Redis)
  * Defined expiration settings for different state scopes
  * Added serialization configuration options
  * Updated agents.md schema documentation to reference state management

### Key Decisions Made

* **Decision 1**: Created four distinct state scopes to address different persistence and visibility needs
  * Rationale: Different agents have varying state requirements, from ephemeral session-specific data to long-lived configuration

* **Decision 2**: Designed for async-first operation with all methods being asynchronous
  * Rationale: Aligns with OpenMAS's async architecture and enables efficient concurrent access

* **Decision 3**: Added specific Pydantic model support via get_state_as_model() method
  * Rationale: Simplifies working with structured data and aligns with OpenMAS's use of Pydantic throughout the codebase

* **Decision 4**: Implemented automatic namespacing to prevent key collisions
  * Rationale: Simplifies API usage by hiding the complexity of ensuring unique keys across agents and sessions

* **Decision 5**: Supported multiple storage backends with consistent API
  * Rationale: Provides flexibility for different deployment scenarios while maintaining a consistent developer experience

### Verification

* ✅ **API for CRUD operations is clear and unambiguous**
  * All methods have precise signatures with type hints and docstrings
  * Method behavior is clearly specified including return values and exceptions

* ✅ **Supported data types and serialization methods are explicitly stated**
  * Documented primitive types, Pydantic models, and bytes support
  * Specified serialization mechanisms and formats

* ✅ **State scopes and their implications are well-defined**
  * Each scope has a clear definition with persistence and visibility implications
  * Documentation explains when to use each scope

* ✅ **Usage examples demonstrate how an agent developer would use the API**
  * Provided examples for basic operations, session-specific state, and Pydantic models
  * Illustrated proper error handling and key management

* ✅ **Configuration of the state backend is clearly specified**
  * Updated unified configuration schema with complete configuration options
  * Documented all configuration parameters with descriptions and defaults

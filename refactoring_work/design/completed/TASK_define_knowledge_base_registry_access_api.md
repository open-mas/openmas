TASK: Define Knowledge Base Registry Access API
Objective: To define a clear API that allows Reasoning Engines or other authorized components to discover, list, and obtain accessors for available Knowledge Bases managed by the KR&R System.

Related Finding from PLANNING.MD: 1.2.2 Undefined Knowledge Base Registry Access

Key Deliverables:

A defined IKnowledgeBaseRegistry interface (e.g., Python ABC).

Precise Pydantic models for data structures used by this interface (e.g., KnowledgeBaseInfo to describe a registered KB).

Clear method signatures for listing available KBs and retrieving an IKnowledgeBase accessor for a specific KB.

Updated documentation in 00b_overview/09_knowledge_representation/architecture.md [cite: uploaded:00b_overview/09_knowledge_representation/architecture.md] and potentially a new file for this interface definition.

## Progress Notes & Completion Summary

**Sub-tasks Completed:**
- Reviewed all relevant documentation (architecture, interfaces, component summary) for context and requirements
- Designed and documented the `IKnowledgeBaseRegistry` interface as a Python ABC, following OpenMAS conventions
- Defined supporting Pydantic models: `KnowledgeBaseInfo` and `KnowledgeBaseFilterCriteria`, with full field-level docstrings and type hints
- Updated the canonical interface documentation in `09_knowledge_representation/knowledge_access_interfaces/interfaces.md` to include the new registry API, methods, and usage example
- Updated `09_knowledge_representation/architecture.md` to reference the new registry interface and clarify its role in knowledge base discovery and access

**Key Design Decisions:**
- Registry API is async, type-safe, and extensible; filtering is supported via Pydantic criteria
- Registry returns metadata and accessors for KBs, not direct knowledge items
- Registry is the canonical entry point for all KB discovery in the KR&R system

**Verification:**
- All deliverables defined in the task are complete
- Documentation is consistent, precise, and cross-referenced
- No ambiguities or unresolved review flags

**Task Status:**

✅ **COMPLETE** — The Knowledge Base Registry Access API is now fully specified and documented. See the updated interface and architecture docs for details.

description: Optional[str]

supported_representations: List[KnowledgeRepresentationType] (Enum from IKnowledgeBase task)

supported_query_types: List[KnowledgeQueryType] (Enum from IKnowledgeBase task)

metadata: Dict[str, Any] (e.g., creation date, owner, access control info if applicable)

tags: Optional[List[str]]

storage_backend_type: Optional[str] (e.g., "PostgreSQL", "VectorDB-Chroma", "InMemory")

is_read_only: bool = False

KnowledgeBaseFilterCriteria(BaseModel):

name_pattern: Optional[str]

requires_representation: Optional[KnowledgeRepresentationType]

requires_all_representations: Optional[List[KnowledgeRepresentationType]]

tags_include_any: Optional[List[str]]

tags_include_all: Optional[List[str]]

metadata_matches: Optional[Dict[str, Any]]

KnowledgeBaseConfig(BaseModel) (if including registration methods):

kb_name: str

description: Optional[str]

storage_type: str (e.g., "sql", "vector", "graph_db")

connection_params: Dict[str, Any] (references secure configuration)

schema_definition: Optional[Dict[str, Any]] (e.g., for SQL tables, graph schema)

initial_representations: Optional[List[KnowledgeRepresentationType]]

Clarify Access and Configuration:

How does a Reasoning Engine (or other component) get an instance of IKnowledgeBaseRegistry? (e.g., dependency injection, provided in AgentContext).

How are knowledge bases themselves configured and loaded into the KR&R system to be discoverable by this registry? This should link to the unified_configuration_schema.md [cite: uploaded:00b_overview/03_configuration/unified_configuration_schema.md].

Update Documentation:

In 00b_overview/09_knowledge_representation/architecture.md [cite: uploaded:00b_overview/09_knowledge_representation/architecture.md]:

Add a new section detailing the IKnowledgeBaseRegistry interface, its methods, and supporting Pydantic models (KnowledgeBaseInfo, KnowledgeBaseFilterCriteria).

Explain the workflow: Component gets registry -> lists KBs -> requests an accessor for a specific KB -> uses the returned IKnowledgeBase instance.

If a new file is created (e.g., 00b_overview/09_knowledge_representation/knowledge_access_interfaces/registry_interface.md), ensure it's linked from the main architecture and interface documents.

Provide examples of:

Listing all available knowledge bases.

Filtering for knowledge bases that support vector embeddings.

Getting an accessor for a specific knowledge base by name.

In 00b_overview/03_configuration/schema/knowledge_representation.md (or a new schema file under 03_configuration/schema/), detail the configuration parameters for defining individual knowledge bases that the KR&R system will load and register.

Cross-references to be checked/updated:

IKnowledgeBase interface document (00b_overview/09_knowledge_representation/knowledge_access_interfaces/interfaces.md [cite: uploaded:00b_overview/09_knowledge_representation/knowledge_access_interfaces/interfaces.md]) - as this is what the registry returns.

00b_overview/09_knowledge_representation/reasoning/interfaces.md [cite: uploaded:00b_overview/09_knowledge_representation/reasoning/interfaces.md] (to show how reasoning engines might use the registry).

unified_configuration_schema.md [cite: uploaded:00b_overview/03_configuration/unified_configuration_schema.md] (for KB definition and KR&R system config).

AgentContext definition (if the registry is accessed via it).

Verification:

Are all methods in IKnowledgeBaseRegistry explicitly defined with typed parameters and return values?

Is the KnowledgeBaseInfo structure comprehensive enough to describe a KB for discovery?

Is the filtering mechanism for listing KBs clear and flexible?

Is the process for obtaining an IKnowledgeBase accessor straightforward?

Is it clear how KBs are configured in the system to become available via the registry?

Progress Notes:

(AI Agent: Please update this section as you complete sub-tasks, make decisions, or encounter issues. Use bullet points for clarity.)

Sub-task X.Y.Z: [Status/Decision/Notes]

...

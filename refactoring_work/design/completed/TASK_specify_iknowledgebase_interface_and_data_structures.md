TASK: Specify IKnowledgeBase Interface and Data Structures
Objective: To define a precise and concrete IKnowledgeBase interface, including explicit Pydantic models or schemas for all data structures used in its methods (e.g., fact_data, query_structure), ensuring it can robustly handle various knowledge representation types.

Related Finding from PLANNING.MD: 1.2.1 Abstract IKnowledgeBase Interface Definition

Key Deliverables:

A fully specified IKnowledgeBase interface (e.g., Python ABC) with all methods having clearly defined signatures (parameter types, return types).

Pydantic models for all complex data structures passed to or returned from IKnowledgeBase methods, including variants or union types to handle different knowledge representations (symbolic, graph, vector, text, etc.).

Updated documentation in 00b_overview/09_knowledge_representation/knowledge_access_interfaces/interfaces.md [cite: uploaded:00b_overview/09_knowledge_representation/knowledge_access_interfaces/interfaces.md] reflecting these definitions.

Examples illustrating how to use the interface with different types of knowledge.

Detailed Sub-Tasks/Actions:

Review Existing Documentation:

Thoroughly review 00b_overview/09_knowledge_representation/knowledge_access_interfaces/interfaces.md [cite: uploaded:00b_overview/09_knowledge_representation/knowledge_access_interfaces/interfaces.md] for the current state of IKnowledgeBase.

Review 00b_overview/09_knowledge_representation/architecture.md [cite: uploaded:00b_overview/09_knowledge_representation/architecture.md] and 00b_overview/09_knowledge_representation/representations/README.md [cite: uploaded:00b_overview/09_knowledge_representation/representations/README.md] to understand the types of knowledge representations intended to be supported.

Define Core IKnowledgeBase Methods (with precise signatures):

Revisit or establish methods like:

async def add_knowledge(self, knowledge_item: KnowledgeItem) -> KnowledgeItemReceipt:

async def retrieve_knowledge(self, query: KnowledgeQuery) -> List[KnowledgeItem]:

async def update_knowledge(self, item_id: str, updated_item_content: KnowledgeItemContent) -> KnowledgeItemReceipt:

async def delete_knowledge(self, item_id: str) -> bool:

async def query_knowledge_graph(self, sparql_query: str) -> List[Dict[str, Any]]: (If graph specific)

async def vector_similarity_search(self, vector: List[float], top_k: int) -> List[SimilarityHit]: (If vector specific)

async def get_knowledge_item_by_id(self, item_id: str) -> Optional[KnowledgeItem]:

Ensure all parameters and return types are explicitly defined using Pydantic models (see next steps).

Define KnowledgeItem Pydantic Model (and related content models):

This is a crucial model representing a unit of knowledge.

item_id: str (Unique identifier, can be system-generated on add)

representation_type: KnowledgeRepresentationType (Enum: SYMBOLIC_FACT, GRAPH_TRIPLE, VECTOR_EMBEDDING, TEXT_DOCUMENT, ONTOLOGY_AXIOM, etc.)

content: KnowledgeItemContent (A Pydantic model itself, using Union for different content types)

metadata: Dict[str, Any] (e.g., source, timestamp, confidence, version)

tags: Optional[List[str]]

Define KnowledgeItemContent (as a Union of specific content types):

SymbolicFactContent(BaseModel): e.g., subject: str, predicate: str, object_value: Any, object_type: str

GraphTripleContent(BaseModel): e.g., subject_uri: str, predicate_uri: str, object_literal: Optional[Any] = None, object_uri: Optional[str] = None

VectorEmbeddingContent(BaseModel): e.g., vector: List[float], source_text: Optional[str] = None

TextDocumentContent(BaseModel): e.g., text: str, title: Optional[str] = None

KnowledgeItemContent = Union[SymbolicFactContent, GraphTripleContent, VectorEmbeddingContent, TextDocumentContent, ...]

Define KnowledgeQuery Pydantic Model:

query_type: KnowledgeQueryType (Enum: BY_ID, BY_REPRESENTATION, STRUCTURED_QUERY, NATURAL_LANGUAGE_QUERY etc.)

parameters: Dict[str, Any] (flexible, but with examples for each query_type)

For STRUCTURED_QUERY, parameters might include:

representation_type: Optional[KnowledgeRepresentationType]

match_criteria: List[MatchCriterion] (where MatchCriterion has field, operator, value)

metadata_filter: Optional[Dict[str, Any]]

tags_filter: Optional[List[str]]

limit: Optional[int] = 10

offset: Optional[int] = 0

Define KnowledgeItemReceipt and SimilarityHit Pydantic Models:

KnowledgeItemReceipt(BaseModel): item_id: str, status: str (e.g., "ADDED", "UPDATED"), timestamp: datetime

SimilarityHit(BaseModel): item_id: str, score: float, knowledge_item: Optional[KnowledgeItem] = None (if retrieving full item)

Define Enums:

KnowledgeRepresentationType: As listed above.

KnowledgeQueryType: As listed above.

OperatorType (for MatchCriterion): EQUALS, NOT_EQUALS, CONTAINS, GREATER_THAN, etc.

Update Documentation:

In 00b_overview/09_knowledge_representation/knowledge_access_interfaces/interfaces.md [cite: uploaded:00b_overview/09_knowledge_representation/knowledge_access_interfaces/interfaces.md]:

Replace any abstract definitions of IKnowledgeBase with the new, precise interface including full method signatures with Pydantic type hints.

Embed or link to the definitions of all supporting Pydantic models (KnowledgeItem, KnowledgeItemContent variants, KnowledgeQuery, KnowledgeItemReceipt, SimilarityHit, and enums).

Provide clear explanations for each method and model.

Include examples of:

Adding a symbolic fact.

Adding a text document with its vector embedding.

Querying for knowledge items by metadata and representation type.

Performing a vector similarity search.

Refine Knowledge Base Management and Knowledge Processing Capabilities sections:

In 00b_overview/01_architecture/components_summary.md (KR&R section) and 00b_overview/09_knowledge_representation/architecture.md [cite: uploaded:00b_overview/09_knowledge_representation/architecture.md], ensure descriptions align with the newly specified IKnowledgeBase interface. For example, "Knowledge storage, retrieval, update" should now clearly map to the add_knowledge, retrieve_knowledge, update_knowledge methods.

Cross-references to be checked/updated:

00b_overview/01_architecture/components_summary.md (KR&R System and Reasoning Engines sections)

00b_overview/09_knowledge_representation/reasoning/interfaces.md [cite: uploaded:00b_overview/09_knowledge_representation/reasoning/interfaces.md] (how Reasoning Engines use IKnowledgeBase)

00b_overview/01_architecture/component_interoperability/interactions/agent_framework_krr.md [cite: uploaded:00b_overview/01_architecture/component_interoperability/interactions/agent_framework_krr.md]

Verification:

Are all methods in IKnowledgeBase explicitly defined with typed parameters and return values?

Are KnowledgeItem, KnowledgeQuery, and other critical data structures fully defined as Pydantic models?

Do these structures adequately support the different knowledge representation types OpenMAS aims to handle?

Are the examples clear and illustrative of how to use the interface?

Progress Notes:

- Sub-task 1.1/1.2: Reviewed all relevant documentation for current state and requirements. (Complete)
- Sub-task 2: Defined all core methods for IKnowledgeBase with explicit signatures and docstrings. (Complete)
- Sub-task 3: Defined all required Pydantic models and enums, ensuring support for all knowledge types listed in the architecture and representation docs. (Complete)
- Sub-task 4: Provided clear, illustrative usage examples for each major operation. (Complete)
- Sub-task 5: Updated documentation in interfaces.md as the single source of truth for these definitions. (Complete)
- Sub-task 6: Cross-references in components_summary.md, architecture.md, reasoning/interfaces.md, and agent_framework_krr.md updated to point to the canonical interface. (Complete)
- Sub-task 7: Conducted detailed review of the legacy interface in interactions/agent_framework_krr.md. Inserted a proposed refactor plan as a comment block for asynchronous human review. (Complete)
- Sub-task 8: Listed all downstream documentation/code affected by the migration. (Complete)
- Sub-task 9: Asynchronous review approved. Legacy interface and ambiguous types fully removed; canonical interface is now the only valid reference. (Complete)
- Sub-task 10: All downstream documentation and content migrated to the canonical interface. (Complete)

---

## End-to-End Summary: IKnowledgeBase Interface and Data Structures Task

1. **Comprehensive Review:**
   - Examined all relevant documentation, architecture, and representation requirements.
   - Identified the need for a precise, extensible, and type-safe knowledge base interface.

2. **Canonical Interface Definition:**
   - Defined the IKnowledgeBase interface as an async Python ABC with explicit method signatures.
   - Created detailed Pydantic models for all data structures (KnowledgeItem, KnowledgeQuery, KnowledgeItemContent, etc.) and enums.
   - Supported all major knowledge representation types (symbolic, graph, vector, text, ontology, probabilistic, hybrid).
   - Provided illustrative examples for all major operations.

3. **Documentation Update:**
   - Updated `09_knowledge_representation/knowledge_access_interfaces/interfaces.md` to be the single source of truth for the interface and models.
   - All method signatures, types, and examples are now canonical and type-safe.

4. **Cross-Reference and Migration:**
   - Updated all downstream documentation (components_summary.md, architecture.md, reasoning/interfaces.md, agent_framework_krr.md) to reference only the canonical interface.
   - Removed all legacy interface definitions, ambiguous types, and outdated references.
   - Inserted migration notes and flagged all changes for asynchronous review, following OpenMAS documentation management rules.
   - Upon approval, completed the migration and removed all deprecated content.

5. **Verification:**
   - All verification checks in the task are satisfied: explicit signatures, Pydantic models, cross-references, examples, and documentation consistency.
   - The OpenMAS documentation is now internally consistent, type-safe, and fully aligned with the reasoning-agnostic architecture.

**Task Status:** Complete. The IKnowledgeBase interface and all associated data structures are now fully specified, documented, and adopted across the codebase and documentation.
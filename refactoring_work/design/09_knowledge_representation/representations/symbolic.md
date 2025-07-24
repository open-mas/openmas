# Symbolic Representations

Symbolic representations are a cornerstone of classical AI, encoding knowledge using discrete symbols, logical rules, and structured facts. In OpenMAS, this formalism is essential for agents that require precise, verifiable, and explainable reasoning processes.

## 1. Core Concepts

-   **Facts**: Atomic pieces of information, often represented as logical predicates (e.g., `is_a(robot, agent)`), tuples, or key-value pairs.
-   **Rules**: Conditional statements that define logical implications (e.g., `IF condition THEN conclusion`). These are fundamental for inference engines.
-   **Logic-Based Formalisms**: The system is designed to accommodate various logical systems, such as first-order logic, description logic, or Prolog-style clauses.

## 2. Use Cases in OpenMAS

Symbolic knowledge bases are ideal for:

-   **Rule-Based Reasoning**: Executing `if-then` rule sets to make decisions.
-   **Planning**: Representing world states and operator schemas for automated planning systems.
-   **Formal Verification**: Storing system models and specifications that can be formally verified.
-   **Ontological Reasoning**: Managing explicit class hierarchies and properties where logical consistency is paramount.

## 3. Interaction via `IKnowledgeBase`

Reasoning engines interact with a symbolic knowledge base through the standard `IKnowledgeBase` interface:

-   `assert_fact(fact)`: Adds a new symbolic fact (e.g., a logical predicate) to the store.
-   `retract_fact(fact)`: Removes a symbolic fact.
-   `query(query)`: Executes a logical query against the fact store. The `query.query_content` would typically contain a logical formula or a query pattern to be matched.

## 4. Configuration Example

An agent configures a symbolic knowledge base in its `knowledge_management_config` section. The `type` field specifies that the KB should use a symbolic representation.

```yaml
agents:
  example_planner_agent:
    reasoning:
      approach: "planning_engine"

    knowledge_management_config:
      enabled: true
      knowledge_bases:
        - kb_id: "world_state_kb"
          type: "symbolic_facts" # Specifies a symbolic representation
          # Implementation-specific config could go here
          # e.g., persistence_path: "/data/world_state.db"
        - kb_id: "domain_rules_kb"
          type: "symbolic_rules"
          # e.g., source_file: "/assets/planning_rules.pl"
```

This configuration allows the `planning_engine` to connect to two distinct symbolic knowledge bases: one for storing dynamic world state facts and another for static domain rules.

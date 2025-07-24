# OpenMAS Knowledge Representation & Reasoning (KR&R) System

## 1. Overview

The Knowledge Representation and Reasoning (KR&R) System is a core component of the OpenMAS framework, designed to provide agents with sophisticated capabilities for knowledge management and access. It serves as a centralized service that separates the storage and management of knowledge from an agent's primary decision-making logic (i.e., its Reasoning Engine).

This architectural separation is crucial to OpenMAS's design, enabling agents to leverage diverse knowledge sources through a standardized set of interfaces without coupling their reasoning logic to any specific knowledge representation.

## 2. Documentation Structure

This section provides a comprehensive guide to the KR&R system's architecture, design principles, and formal interfaces.

*   **[Architecture](./architecture.md)**
    *   Describes the high-level structure of the KR&R system, its key components, and how it interacts with other parts of the OpenMAS framework, particularly Reasoning Engines.

*   **[Design Principles](./design_principles.md)**
    *   Outlines the fundamental principles that guide the design of the KR&R system, such as representation agnosticism, scalability, and the separation of knowledge from reasoning.

*   **[Knowledge Access Interfaces](./knowledge_access_interfaces/README.md)**
    *   Provides the formal definitions for the interfaces used to interact with the KR&R system, including the `IKnowledgeBase` for querying knowledge and the `IKnowledgeBaseRegistry` for discovering available knowledge bases.

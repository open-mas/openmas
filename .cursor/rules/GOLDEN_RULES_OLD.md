### API Design Standards
- **Pydantic models for everything** - all interfaces use Pydantic for type safety
- **Async by default** - all method signatures should be async unless impossible
- **Explicit type hints** - every parameter and return type must be clearly defined
- **Protocol agnostic** - no protocol-specific logic in shared interfaces
- **SIMF integration** - ensure all protocol adapters translate to/from SIMF correctly

### Documentation Quality
- **Reference existing patterns** from completed TASK files for consistency
- **Include usage examples** for every interface and major method
- **Update cross-references** when adding new interfaces
- **Maintain architectural constraints** defined in the master plan

## 🧱 Code Structure & Modularity
- **Never create a file longer than 500 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into protocol-specific modules** while maintaining a clean separation between communication layers and reasoning approaches.
- **Use clear, consistent imports** (prefer relative imports within packages).
- **Maintain clean separation** between protocol implementations (A2A, MCP, HTTP, MQTT, gRPC) while preserving shared abstractions.

## 🧯 Testing & Reliability
- **Always create Pytest unit tests for new features** (functions, classes, protocols, etc).
- **After updating any protocol implementation**, check whether existing protocol tests need to be updated.
- **Tests should live in a `/tests` folder** mirroring the main package structure.
  - Include at least:
    - 1 test for expected use
    - 1 edge case
    - 1 failure case
- **Create protocol-specific integration tests** that verify proper message handling.
- **Maintain test coverage of at least 70%** across all components (higher coverage for MCP components).
- **Use proper test markers** (unit, integration, example, mcp, grpc, mqtt, sync, async) for all test files.
- **ALWAYS test against real libraries in integration tests**:
  - Inspect the actual library API using `pip show`, `dir()`, and file inspection
  - Document API findings before implementing adapters
  - NEVER speculate or hallucinate library APIs
- **Design code for testability**:
  - Use dependency injection for all external dependencies
  - Create interfaces for all dependencies to enable proper mocking
  - Follow inversion of control principles
  - Keep adapter implementations minimal and focused

## 📎 Style & Conventions
- **Use Python 3.10+** as the baseline language version.
- **Follow strict formatting rules using:**
  - Black with line length of 88
  - isort with Black profile and line length of 88
  - flake8 with standard configurations (ignoring E203, W503)
- **Use strict type annotations** for all production code:
  - All functions must have complete type annotations
  - Use Pydantic for data validation
  - Follow mypy strict mode guidelines
- **Keep optional protocol implementations separate** as defined in the extras.
- **Follow naming conventions:**
  ```python
  # Variables and functions: snake_case
  my_variable = "value"
  def my_function():
      pass

  # Classes: PascalCase
  class MyClass:
      pass

  # Constants: UPPER_CASE
  MY_CONSTANT = "value"
  ```
- Write **Google-style docstrings** for every function:
  ```python
  def example():
      """
      Brief summary.

      Args:
          param1 (type): Description.

      Returns:
          type: Description.
      """
  ```

## 📚 Documentation & Explainability

### Documentation Structure
- **Follow hierarchical documentation organization** with the established sections:
  - Core Concepts: design philosophy, architecture, project structure
  - Guides: step-by-step instructions for specific features
  - Examples & Use Cases: working demonstrations
  - CLI Reference: command line tool documentation
  - API Reference: detailed technical documentation
- **Create new guides** for any significant feature or protocol implementation
- **Include diagrams and visuals** for complex concepts and architectures
- **Use a consistent tone** that's technical but approachable for mid-level developers

### Markdown Documentation
- **Place all documentation** in the `docs/` directory following the existing hierarchy
- **Use proper Markdown formatting** with consistent headers, lists, and code blocks
- **Include code examples** in all guides and reference materials
- **Link related documentation sections** to create a cohesive navigation experience
- **Add screenshots or diagrams** for UI-related features or complex architectures
- **Structure tutorials** with clear prerequisites, steps, and expected outcomes
- **Document protocol-specific details** comprehensively, including message formats and patterns

### Code Documentation
- **Write Google-style docstrings** for all modules, classes, methods, and properties:
  ```python
  """Brief summary.

  Detailed explanation.

  Args:
      param1 (type): Description.

  Returns:
      type: Description.

  Raises:
      Exception: Description.
  """
  ```
- **Document all public APIs** with complete parameter and return type information
- **Include usage examples** in docstrings for complex or commonly used functions
- **Comment non-obvious code** with inline explanations
- **Use `# Reason:` comments** to explain complex algorithms or design decisions
- **Document protocol-specific implementation details** thoroughly

### Documentation Tools & Workflows
- **Use MkDocs with Material theme** for generating documentation website
- **Preview documentation locally** before committing changes
- **Keep API reference up-to-date** when adding or modifying code
- **Verify all code examples** in documentation actually work
- **Run documentation builds** in CI/CD to catch formatting errors

## 🔐 Protocol Implementation Rules
- **Ensure all protocol implementations support the unified configuration schema**.
- **Maintain reasoning agnosticism** in all protocol implementations.
- **Properly separate communication monitoring** from reasoning monitoring.
- **Follow security best practices** for each protocol, including proper authentication and authorization mechanisms.
- **Design for observability** with protocol-specific monitoring capabilities.

## 🛠️ Development Workflow
- **Use pre-commit hooks** for consistent code quality:
  - trailing-whitespace
  - end-of-file-fixer
  - check-yaml/check-toml
  - black, isort, flake8, mypy
- **Run tox environments** for testing different components:
  - Use `tox -e lint` for linting
  - Use `tox -e unit` for unit tests
  - Use `tox -e integration-mock` for integration tests with mocks
  - Use protocol-specific test environments as needed
- **Use poetry for dependency management**, maintaining clear separation of optional dependencies.

## 🧠 AI Behavior Rules
- **Never assume missing context. Ask questions if uncertain about protocol-specific requirements.**
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing protocol implementations** unless explicitly instructed to.
- **Respect the separation between "body" and "brain"** components in all code changes.


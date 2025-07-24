# Directory Structure for OpenMAS 0.3.0

## Task Overview
Create the directory structure for OpenMAS 0.3.0 while preserving the 0.2.0 codebase for reference.

## Tasks

✅ ~~1. Create new branch for version 0.3.0 development~~ (Completed)
   - ~~Create and checkout branch named '030'~~

✅ ~~2. Move existing files to 0.2.0 subdirectory~~ (Completed)
   - ~~All files except refactoring_work have been moved to the 0.2.0 directory~~

3. Create new root project structure
   - Recreate essential project configuration files in the root
   - Setup GitHub workflows
   - Create documentation structure

4. Setup new src/openmas module directory structure
   - Create all module directories based on the unified schema
   - Ensure proper `__init__.py` files for each module

## Directory Structure for OpenMAS 0.3.0

```
openmas/
├── .github/                    # GitHub workflows and configuration
├── .flake8                     # Flake8 configuration
├── .gitignore                  # Git ignore file
├── .pre-commit-config.yaml     # Pre-commit hooks configuration
├── mypy.ini                    # MyPy configuration
├── pyproject.toml              # Project metadata and dependencies
├── pytest.ini                  # PyTest configuration
├── tox.ini                     # Tox configuration
├── README.md                   # Project documentation
├── CHANGELOG.md                # Version changelog
├── LICENSE                     # License file
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
├── src/
│   └── openmas/                # Main package
│       ├── __init__.py         # Package initialization
│       ├── agent/              # Agent subsystem
│       │   ├── __init__.py
│       │   ├── capabilities/   # Agent capabilities
│       │   └── lifecycle/      # Agent lifecycle management
│       ├── assets/             # Asset management
│       │   ├── __init__.py
│       │   ├── loaders/        # Asset loading mechanisms
│       │   └── resources/      # Resource mapping and handling
│       ├── cli/                # Command-line interface
│       │   └── __init__.py
│       ├── protocols/          # Protocol implementations (aligned with design)
│       │   ├── __init__.py
│       │   ├── a2a/            # A2A protocol
│       │   ├── mcp/            # MCP protocol
│       │   ├── http/           # HTTP protocol
│       │   ├── mqtt/           # MQTT protocol
│       │   └── grpc/           # gRPC protocol
│       ├── communication_patterns/ # Communication patterns (aligned with design)
│       │   ├── __init__.py
│       │   ├── request_response/ # Request-response pattern
│       │   ├── publish_subscribe/ # Publish-subscribe pattern
│       │   └── event_based/    # Event-based pattern
│       ├── config/             # Configuration management
│       │   ├── __init__.py
│       │   ├── schema/         # Schema definitions
│       │   ├── validation/     # Configuration validation
│       │   └── loaders/        # Configuration loading
│       ├── deployment/         # Deployment utilities
│       │   └── __init__.py
│       ├── exceptions.py       # Exception definitions
│       ├── extensions/         # Extension system
│       │   ├── __init__.py
│       │   ├── registration/   # Extension registration
│       │   └── discovery/      # Extension discovery
│       ├── integrations/       # Third-party integrations
│       │   └── __init__.py
│       ├── observability/      # Observability framework
│       │   ├── __init__.py
│       │   ├── logging/        # Logging system
│       │   ├── metrics/        # Metrics collection
│       │   └── tracing/        # Distributed tracing
│       ├── prompt_management/  # Prompt management (aligned with design)
│       │   ├── __init__.py
│       │   ├── templates/      # Prompt templates
│       │   ├── variables/      # Template variables
│       │   └── validation/     # Prompt validation
│       ├── security/           # Security components
│       │   ├── __init__.py
│       │   ├── authentication/ # Authentication mechanisms
│       │   └── authorization/  # Authorization controls
│       ├── session_management/ # Session management (aligned with design)
│       │   ├── __init__.py
│       │   ├── persistence/    # Session persistence
│       │   └── coordination/   # Multi-agent coordination
│       ├── topology/           # Agent topologies (aligned with design)
│       │   ├── __init__.py
│       │   ├── centralized/    # Centralized topologies
│       │   ├── decentralized/  # Decentralized topologies
│       │   └── hybrid/         # Hybrid topologies
│       ├── knowledge_representation/ # KR&R System (missing component)
│       │   ├── __init__.py
│       │   ├── knowledge_bases/ # Knowledge base implementations
│       │   ├── interfaces/     # Knowledge access interfaces
│       │   └── reasoning/      # Reasoning engine support
│       ├── asset_management/   # Asset management (missing component)
│       │   ├── __init__.py
│       │   ├── loaders/        # Asset loading mechanisms
│       │   └── versioning/     # Asset versioning
│       └── cli_tools/          # CLI tools (missing component)
│           ├── __init__.py
│           ├── commands/       # CLI commands
│           └── scaffolding/    # Project scaffolding
├── tests/                      # Test directory
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── fixtures/               # Test fixtures
└── 0.2.0/                      # Previous version (for reference)
    └── ... (all existing files)
```

## Success Criteria
- Complete directory structure created
- All configuration files properly placed
- Module hierarchy follows the unified schema design
- `__init__.py` files created for all Python packages

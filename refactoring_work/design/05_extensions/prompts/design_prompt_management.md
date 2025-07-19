# Prompt Management System Design

## Overview

The OpenMAS Prompt Management system provides standardized templates, versioning, and contextual adaptation for prompts across all protocols and reasoning approaches. It ensures consistent prompt handling, efficient template management, and supports the framework's key architectural principles of reasoning agnosticism and multi-protocol support.

## Core Principles

1. **Reasoning Agnosticism**: Prompts are managed independently of the reasoning approach
2. **Protocol Independence**: Prompt templates work consistently across all protocols (MCP, A2A, etc.)
3. **Contextual Adaptation**: Templates adjust based on execution context
4. **Version Control**: Support for prompt versioning and governance
5. **Templating Flexibility**: Multiple template engines and formats
6. **Schema Validation**: Strict schema validation for prompt structures

## Prompt Types

OpenMAS supports these standard prompt types:

1. **System Prompts** - Define system behavior and context
2. **User Prompts** - Represent user inputs with variables
3. **Assistant Prompts** - Template assistant responses
4. **Function Prompts** - Define function calls and parameters
5. **Few-Shot Prompts** - Example-based templates for reasoning
6. **Chain Prompts** - Connected sequences of prompts
7. **Conditional Prompts** - Context-dependent prompt selection

## Architecture Implementation

### PromptManager Class

The `PromptManager` coordinates all prompt operations:

```python
class PromptManager:
    """Central manager for prompts across the system."""
    
    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.templates = {}
        self.engines = {}
        self.repositories = {}
        
        # Initialize template engines
        self._initialize_engines()
        
        # Initialize prompt repositories
        self._initialize_repositories()
        
        # Load prompt templates
        self._load_templates()
    
    def _initialize_engines(self):
        """Initialize template engines from configuration."""
        engines_config = self.config.get("engines", {})
        
        # Initialize built-in engines
        self.engines["text"] = PlainTextEngine()
        self.engines["jinja2"] = Jinja2Engine()
        self.engines["handlebars"] = HandlebarsEngine()
        
        # Initialize custom engines
        custom_engines = engines_config.get("custom", [])
        for engine_config in custom_engines:
            engine_type = engine_config["type"]
            engine_name = engine_config["name"]
            engine = self._create_engine(engine_type, engine_config)
            self.engines[engine_name] = engine
    
    def _initialize_repositories(self):
        """Initialize prompt repositories."""
        repos_config = self.config.get("repositories", [])
        for repo_config in repos_config:
            repo_type = repo_config["type"]
            repo_name = repo_config["name"]
            repo = self._create_repository(repo_type, repo_config)
            self.repositories[repo_name] = repo
    
    def _create_engine(self, engine_type, config):
        """Create a template engine of the specified type."""
        # Implementation for creating custom engines
        pass
    
    def _create_repository(self, repo_type, config):
        """Create a prompt repository of the specified type."""
        if repo_type == "file_system":
            return FileSystemRepository(config)
        elif repo_type == "database":
            return DatabaseRepository(config)
        elif repo_type == "git":
            return GitRepository(config)
        else:
            # Use extension system to find repository
            return self._get_extension_repository(repo_type, config)
    
    def _get_extension_repository(self, repo_type, config):
        """Get repository from extension system."""
        # Implementation for finding repository in extensions
        pass
    
    def _load_templates(self):
        """Load prompt templates from all repositories."""
        for repo_name, repo in self.repositories.items():
            templates = repo.list_templates()
            for template_id, template in templates.items():
                # Register with source repository
                full_id = f"{repo_name}:{template_id}"
                self.templates[full_id] = template
    
    async def get_template(self, template_id, version=None):
        """Get a prompt template by ID and optional version."""
        # Parse template ID to get repository and local ID
        repo_name, local_id = self._parse_template_id(template_id)
        
        # If repository specified, get from that repository
        if repo_name:
            if repo_name not in self.repositories:
                raise ValueError(f"Unknown repository: {repo_name}")
            
            repo = self.repositories[repo_name]
            return await repo.get_template(local_id, version)
        
        # Otherwise, search in all repositories
        for repo_name, repo in self.repositories.items():
            try:
                template = await repo.get_template(local_id, version)
                return template
            except:
                # Not found in this repository
                pass
        
        raise ValueError(f"Template not found: {template_id}")
    
    def _parse_template_id(self, template_id):
        """Parse a template ID into repository and local ID."""
        # Format: [repository:]local_id
        parts = template_id.split(":", 1)
        if len(parts) == 1:
            return None, template_id
        
        return parts[0], parts[1]
    
    async def render_template(self, template_id, context, version=None):
        """Render a template with context."""
        # Get the template
        template = await self.get_template(template_id, version)
        
        # Get template format
        template_format = template.get("format", "text")
        
        # Get appropriate engine
        if template_format not in self.engines:
            raise ValueError(f"Unsupported template format: {template_format}")
        
        engine = self.engines[template_format]
        
        # Render the template
        return await engine.render(template, context)
    
    async def validate_template(self, template):
        """Validate a template against schema."""
        # Implementation for schema validation
        pass
    
    async def register_template(self, template, repository=None):
        """Register a new template."""
        # Validate the template
        await self.validate_template(template)
        
        # Use default repository if none specified
        if not repository:
            repository = self.config.get("default_repository", "local")
        
        if repository not in self.repositories:
            raise ValueError(f"Unknown repository: {repository}")
        
        # Register with repository
        repo = self.repositories[repository]
        template_id = await repo.register_template(template)
        
        # Register in local cache
        full_id = f"{repository}:{template_id}"
        self.templates[full_id] = template
        
        return full_id
```

### Template Engine Interface

Template engines implement a common interface for rendering templates:

```python
class TemplateEngine:
    """Base class for template engines."""
    
    def __init__(self, config=None):
        """Initialize with optional configuration."""
        self.config = config or {}
    
    async def render(self, template, context):
        """Render a template with context."""
        raise NotImplementedError("Subclasses must implement render")
    
    async def validate(self, template):
        """Validate a template structure."""
        raise NotImplementedError("Subclasses must implement validate")
    
    async def parse(self, template_string):
        """Parse a template string into a template object."""
        raise NotImplementedError("Subclasses must implement parse")
```

### Jinja2 Template Engine Implementation

Example implementation for Jinja2 templates:

```python
class Jinja2Engine(TemplateEngine):
    """Template engine for Jinja2 templates."""
    
    def __init__(self, config=None):
        """Initialize Jinja2 environment."""
        super().__init__(config)
        
        # Create Jinja2 environment
        self.env = jinja2.Environment(
            loader=jinja2.BaseLoader(),
            autoescape=self.config.get("autoescape", True),
            trim_blocks=self.config.get("trim_blocks", True),
            lstrip_blocks=self.config.get("lstrip_blocks", True)
        )
        
        # Register custom filters
        self._register_filters()
    
    def _register_filters(self):
        """Register custom filters with Jinja2."""
        # Register standard filters
        self.env.filters["to_json"] = json.dumps
        
        # Register custom filters from configuration
        custom_filters = self.config.get("filters", {})
        for name, func_path in custom_filters.items():
            filter_func = self._import_filter(func_path)
            self.env.filters[name] = filter_func
    
    def _import_filter(self, func_path):
        """Import a filter function from path."""
        module_path, func_name = func_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return getattr(module, func_name)
    
    async def render(self, template, context):
        """Render a Jinja2 template with context."""
        # Get template content
        content = template["content"]["template"]
        
        # Create Jinja2 template
        jinja_template = self.env.from_string(content)
        
        # Render with context
        return jinja_template.render(**context)
    
    async def validate(self, template):
        """Validate a Jinja2 template structure."""
        # Check required fields
        if "content" not in template or "template" not in template["content"]:
            raise ValueError("Template must have content.template field")
        
        # Try parsing to validate syntax
        try:
            self.env.parse(template["content"]["template"])
        except jinja2.exceptions.TemplateSyntaxError as e:
            raise ValueError(f"Invalid Jinja2 syntax: {e}")
        
        return True
    
    async def parse(self, template_string):
        """Parse a template string into a template object."""
        # Check valid syntax
        try:
            self.env.parse(template_string)
        except jinja2.exceptions.TemplateSyntaxError as e:
            raise ValueError(f"Invalid Jinja2 syntax: {e}")
        
        # Create template object
        return {
            "type": "user",  # Default type
            "format": "jinja2",
            "content": {
                "template": template_string
            }
        }
```

### Prompt Repository Interface

Repositories provide storage and retrieval of prompt templates:

```python
class PromptRepository:
    """Base class for prompt repositories."""
    
    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
    
    async def get_template(self, template_id, version=None):
        """Get a template by ID and optional version."""
        raise NotImplementedError("Subclasses must implement get_template")
    
    async def register_template(self, template):
        """Register a new template and return its ID."""
        raise NotImplementedError("Subclasses must implement register_template")
    
    async def update_template(self, template_id, template, create_version=True):
        """Update an existing template, optionally creating a new version."""
        raise NotImplementedError("Subclasses must implement update_template")
    
    async def list_templates(self, filter=None):
        """List templates, optionally filtered."""
        raise NotImplementedError("Subclasses must implement list_templates")
    
    async def list_versions(self, template_id):
        """List versions of a template."""
        raise NotImplementedError("Subclasses must implement list_versions")
```

### File System Repository Implementation

Example implementation for file-based prompt storage:

```python
class FileSystemRepository(PromptRepository):
    """Repository that stores templates in the file system."""
    
    def __init__(self, config):
        """Initialize with configuration."""
        super().__init__(config)
        
        # Get base path
        self.base_path = self.config.get("base_path", "./prompts")
        
        # Ensure directory exists
        os.makedirs(self.base_path, exist_ok=True)
        
        # Version control
        self.versioning = self.config.get("versioning", True)
        
        # Templates cache
        self.templates = {}
    
    async def get_template(self, template_id, version=None):
        """Get a template by ID and optional version."""
        # Normalize template ID
        template_id = self._normalize_id(template_id)
        
        # Get template path
        template_path = self._get_template_path(template_id)
        
        # Check if template exists
        if not os.path.exists(template_path):
            raise ValueError(f"Template not found: {template_id}")
        
        # Load template metadata
        metadata_path = os.path.join(template_path, "metadata.json")
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        # Determine version to load
        if version is None:
            # Use latest version
            version = metadata.get("latest_version", "1.0.0")
        
        # Load specific version
        version_path = os.path.join(template_path, "versions", version)
        if not os.path.exists(version_path):
            raise ValueError(f"Version not found: {version}")
        
        with open(version_path, "r") as f:
            template = json.load(f)
        
        # Add metadata
        template["metadata"] = metadata
        template["version"] = version
        
        return template
    
    async def register_template(self, template):
        """Register a new template and return its ID."""
        # Generate ID if not provided
        template_id = template.get("id")
        if not template_id:
            template_id = self._generate_id(template)
        
        # Normalize template ID
        template_id = self._normalize_id(template_id)
        
        # Get template path
        template_path = self._get_template_path(template_id)
        
        # Check if template already exists
        if os.path.exists(template_path):
            raise ValueError(f"Template already exists: {template_id}")
        
        # Create template directory
        os.makedirs(os.path.join(template_path, "versions"), exist_ok=True)
        
        # Create initial version
        version = "1.0.0"
        version_path = os.path.join(template_path, "versions", version)
        
        # Strip metadata for version storage
        template_version = template.copy()
        metadata = template_version.pop("metadata", {})
        
        # Add creation timestamp to metadata
        metadata["created_at"] = datetime.datetime.now().isoformat()
        metadata["latest_version"] = version
        
        # Write version file
        with open(version_path, "w") as f:
            json.dump(template_version, f, indent=2)
        
        # Write metadata file
        metadata_path = os.path.join(template_path, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return template_id
    
    def _normalize_id(self, template_id):
        """Normalize a template ID for file system use."""
        # Replace invalid characters
        return re.sub(r'[^\w\-\.]', '_', template_id)
    
    def _get_template_path(self, template_id):
        """Get the file system path for a template."""
        return os.path.join(self.base_path, template_id)
    
    def _generate_id(self, template):
        """Generate an ID for a template."""
        # Use name if available
        if "name" in template:
            return self._normalize_id(template["name"].lower())
        
        # Otherwise use a UUID
        return str(uuid.uuid4())
```

## Protocol Support

### MCP Prompt Integration

Integration with the Model Context Protocol:

```python
class MCPPromptAdapter:
    """Adapts OpenMAS prompts to MCP messages."""
    
    def __init__(self, prompt_manager):
        """Initialize with prompt manager."""
        self.prompt_manager = prompt_manager
    
    async def create_system_message(self, prompt_id, context=None):
        """Create an MCP system message from a prompt."""
        # Get the prompt template
        template = await self.prompt_manager.get_template(prompt_id)
        
        # Render the template
        content = await self.prompt_manager.render_template(prompt_id, context or {})
        
        # Create MCP system message
        return {
            "role": "system",
            "content": content
        }
    
    async def create_user_message(self, prompt_id, context=None):
        """Create an MCP user message from a prompt."""
        # Get the prompt template
        template = await self.prompt_manager.get_template(prompt_id)
        
        # Render the template
        content = await self.prompt_manager.render_template(prompt_id, context or {})
        
        # Check for resources
        resources = []
        if "resources" in context:
            for resource in context["resources"]:
                # Convert to MCP resource format
                resources.append(self._convert_to_mcp_resource(resource))
        
        # Create MCP user message
        message = {
            "role": "user",
            "content": content
        }
        
        # Add resources if any
        if resources:
            message["resources"] = resources
        
        return message
    
    def _convert_to_mcp_resource(self, resource):
        """Convert a resource to MCP format."""
        # Implementation for resource conversion
        pass
```

### A2A Prompt Integration

Integration with the Agent-to-Agent Protocol:

```python
class A2APromptAdapter:
    """Adapts OpenMAS prompts to A2A messages."""
    
    def __init__(self, prompt_manager):
        """Initialize with prompt manager."""
        self.prompt_manager = prompt_manager
    
    async def create_a2a_message(self, prompt_id, context=None):
        """Create an A2A message from a prompt."""
        # Get the prompt template
        template = await self.prompt_manager.get_template(prompt_id)
        
        # Render the template
        content = await self.prompt_manager.render_template(prompt_id, context or {})
        
        # Create A2A message with parts
        message = {
            "parts": [
                {
                    "type": "text",
                    "content": content
                }
            ]
        }
        
        # Add additional parts from context
        if "parts" in context:
            for part in context["parts"]:
                # Convert to A2A part format
                message["parts"].append(self._convert_to_a2a_part(part))
        
        # Add metadata if any
        if "metadata" in context:
            message["metadata"] = context["metadata"]
        
        return message
    
    def _convert_to_a2a_part(self, part):
        """Convert a part to A2A format."""
        # Implementation for part conversion
        pass
```

## Configuration Example

```yaml
# Global prompt management configuration
prompts:
  # Template engines configuration
  engines:
    template_format: "jinja2"  # Default format
    custom:
      - type: "custom_engine"
        name: "mustache"
        class: "my_package.MustacheEngine"
        config:
          option1: "value1"
  
  # Prompt repositories
  repositories:
    - type: "file_system"
      name: "local"
      config:
        base_path: "./prompts"
        versioning: true
    
    - type: "database"
      name: "shared"
      config:
        connection_string: "postgresql://user:pass@localhost/prompts"
        table_prefix: "prompt_"
    
    - type: "git"
      name: "version_controlled"
      config:
        repo_url: "https://github.com/org/prompt-templates.git"
        branch: "main"
        path: "templates"
  
  # Default repository for new prompts
  default_repository: "local"
  
  # Prompt validation
  validation:
    schema_validation: true
    syntax_validation: true
  
  # Version control
  versioning:
    enabled: true
    auto_version: true
    naming_scheme: "semver"  # semantic versioning
```

## Template Example

```yaml
# Example prompt template
id: "travel_assistant"
type: "system"
format: "jinja2"

content:
  template: |
    You are a travel assistant helping to plan a trip to {{ destination }}.
    {% if budget %}
    The user has a budget of {{ budget }} for this trip.
    {% endif %}
    {% if duration %}
    The trip will last for {{ duration }} days.
    {% endif %}
    Your job is to provide helpful travel information and recommendations.

  variables:
    destination:
      type: "string"
      description: "Travel destination"
      required: true
    budget:
      type: "number"
      description: "Travel budget"
      required: false
    duration:
      type: "number"
      description: "Trip duration in days"
      required: false

metadata:
  name: "Travel Assistant Prompt"
  description: "System prompt for travel planning assistant"
  author: "OpenMAS Team"
  tags: ["travel", "planning", "assistant"]
  version: "1.0.0"
  created_at: "2025-05-01T12:00:00Z"
```

## Multi-Protocol Support

The prompt management system ensures compatibility across protocols by:

1. **Protocol-Agnostic Templates**: Templates are designed independently of protocols
2. **Protocol-Specific Adapters**: Adapters convert templates to protocol-specific formats
3. **Resource Integration**: Support for including protocol-appropriate resources
4. **Message Format Conversion**: Templates adapt to different message structures
5. **Context Mapping**: Context variables map to protocol-specific fields

## Reasoning Agnosticism

The prompt management system maintains OpenMAS's reasoning agnosticism by:

1. **Reasoning-Independent Templates**: Templates are designed independently of reasoning approaches
2. **Flexible Content Structures**: Templates work with any reasoning paradigm
3. **Separation of Concerns**: Template management is distinct from reasoning implementation
4. **Adaptation to Reasoning**: Templates can adapt to reasoning approach via context

This prompt management design provides a flexible foundation for generating, managing, and adapting prompts across all OpenMAS protocols and reasoning approaches, ensuring consistency while preserving the framework's key architectural principles.

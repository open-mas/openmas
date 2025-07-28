# Deployment System Setup

## Task Overview
Setup the Deployment Management system for OpenMAS 0.3.0, which provides enterprise-ready deployment options while maintaining OpenMAS's reasoning-agnostic architecture and multi-protocol capabilities.

## Design Alignment
**Reference**: `/refactoring_work/design/01_architecture/components_summary.md` sections 172-193 and `/refactoring_work/design/documentation_structure.md` section `15_deployment/`
**Architecture**: Deployment management provides local, containerized, Kubernetes, and cloud deployment options with multi-protocol support and reasoning-agnostic configurations.

## Tasks

1. Create Deployment Directory Structure
   - Setup local deployment utilities
   - Create containerization support
   - Configure cloud deployment options

2. Implement Container Support
   - Docker image generation
   - Multi-protocol container configurations
   - Reasoning-specific container setups
   - Container orchestration utilities

3. Setup Cloud Deployment
   - AWS, Azure, GCP deployment configurations
   - Kubernetes manifests and operators
   - Environment management
   - Security controls across deployments

4. Configure Deployment Management
   - Deployment lifecycle management
   - Configuration templating
   - Monitoring and health checks
   - Rollback and update mechanisms

## Directory Structure

```
src/openmas/deployment/
├── __init__.py                     # Deployment module initialization
├── local/                          # Local deployment utilities
│   ├── __init__.py
│   ├── supervisor.py              # Local agent supervision
│   ├── process_manager.py         # Process management
│   ├── development_server.py      # Development server
│   └── local_registry.py          # Local service registry
├── containers/                     # Container deployment
│   ├── __init__.py
│   ├── docker/                    # Docker support
│   │   ├── __init__.py
│   │   ├── image_builder.py       # Docker image building
│   │   ├── compose_generator.py   # Docker Compose generation
│   │   ├── multi_protocol_config.py # Multi-protocol container config
│   │   └── reasoning_config.py    # Reasoning-specific config
│   ├── kubernetes/                # Kubernetes support
│   │   ├── __init__.py
│   │   ├── manifest_generator.py  # K8s manifest generation
│   │   ├── operator.py            # OpenMAS K8s operator
│   │   ├── helm_charts/           # Helm chart templates
│   │   └── ingress_config.py      # Ingress configuration
│   └── podman/                    # Podman support
│       ├── __init__.py
│       └── podman_config.py       # Podman-specific configuration
├── cloud/                          # Cloud deployment
│   ├── __init__.py
│   ├── aws/                       # AWS deployment
│   │   ├── __init__.py
│   │   ├── ecs_deployment.py      # ECS deployment
│   │   ├── lambda_deployment.py   # Lambda deployment
│   │   ├── ec2_deployment.py      # EC2 deployment
│   │   └── cloudformation/        # CloudFormation templates
│   ├── azure/                     # Azure deployment
│   │   ├── __init__.py
│   │   ├── container_instances.py # Azure Container Instances
│   │   ├── functions_deployment.py # Azure Functions
│   │   ├── vm_deployment.py       # Virtual Machine deployment
│   │   └── arm_templates/         # ARM templates
│   ├── gcp/                       # Google Cloud deployment
│   │   ├── __init__.py
│   │   ├── cloud_run.py           # Cloud Run deployment
│   │   ├── functions_deployment.py # Cloud Functions
│   │   ├── gce_deployment.py      # Compute Engine deployment
│   │   └── deployment_manager/    # Deployment Manager templates
│   └── multi_cloud/               # Multi-cloud deployment
│       ├── __init__.py
│       ├── terraform/             # Terraform configurations
│       └── pulumi/                # Pulumi configurations
├── management/                     # Deployment management
│   ├── __init__.py
│   ├── lifecycle_manager.py       # Deployment lifecycle
│   ├── config_templating.py       # Configuration templating
│   ├── environment_manager.py     # Environment management
│   ├── health_monitor.py          # Deployment health monitoring
│   ├── rollback_manager.py        # Rollback capabilities
│   └── update_manager.py          # Update management
├── security/                       # Deployment security
│   ├── __init__.py
│   ├── secrets_manager.py         # Secrets management
│   ├── certificate_manager.py     # Certificate management
│   ├── network_security.py        # Network security configuration
│   └── access_control.py          # Access control configuration
└── utilities/                      # Deployment utilities
    ├── __init__.py
    ├── validation/                 # Deployment validation
    │   ├── __init__.py
    │   ├── config_validator.py     # Configuration validation
    │   ├── resource_validator.py   # Resource validation
    │   └── security_validator.py   # Security validation
    ├── monitoring/                 # Deployment monitoring
    │   ├── __init__.py
    │   ├── metrics_collector.py    # Metrics collection
    │   ├── log_aggregator.py       # Log aggregation
    │   └── alert_manager.py        # Alert management
    └── testing/                    # Deployment testing
        ├── __init__.py
        ├── integration_tester.py   # Integration testing
        ├── load_tester.py          # Load testing
        └── smoke_tester.py         # Smoke testing
```

## Key Implementation Files

### 1. Deployment Manager (`__init__.py`)

```python
"""
OpenMAS Deployment System - Enterprise-ready deployment management.

Provides local, containerized, Kubernetes, and cloud deployment options
while maintaining OpenMAS's reasoning-agnostic architecture and multi-protocol capabilities.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import asyncio

from .management.lifecycle_manager import LifecycleManager
from .management.environment_manager import EnvironmentManager
from .management.health_monitor import DeploymentHealthMonitor

class DeploymentType(Enum):
    """Types of deployments supported."""
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    MULTI_CLOUD = "multi_cloud"

@dataclass
class DeploymentConfig:
    """Configuration for a deployment."""
    name: str
    deployment_type: DeploymentType
    environment: str
    protocols: List[str]
    reasoning_engines: List[str]
    resources: Dict[str, Any]
    security_config: Dict[str, Any]
    monitoring_config: Dict[str, Any]

class DeploymentManager:
    """Central manager for all deployment operations."""

    def __init__(self):
        self._deployments: Dict[str, Any] = {}
        self._lifecycle_manager = LifecycleManager()
        self._environment_manager = EnvironmentManager()
        self._health_monitor = DeploymentHealthMonitor()

    async def create_deployment(self, config: DeploymentConfig) -> bool:
        """Create a new deployment."""
        try:
            # Validate configuration
            if not await self._validate_deployment_config(config):
                return False

            # Create deployment based on type
            deployment = await self._create_deployment_instance(config)

            # Initialize deployment
            if await deployment.initialize():
                self._deployments[config.name] = deployment

                # Start health monitoring
                await self._health_monitor.add_deployment(config.name, deployment)

                return True
            else:
                return False

        except Exception as e:
            print(f"Failed to create deployment {config.name}: {e}")
            return False

    async def deploy(self, deployment_name: str) -> bool:
        """Deploy an application."""
        deployment = self._deployments.get(deployment_name)
        if not deployment:
            return False

        return await self._lifecycle_manager.deploy(deployment)

    async def update_deployment(self, deployment_name: str, new_config: DeploymentConfig) -> bool:
        """Update an existing deployment."""
        deployment = self._deployments.get(deployment_name)
        if not deployment:
            return False

        return await self._lifecycle_manager.update(deployment, new_config)

    async def rollback_deployment(self, deployment_name: str, version: Optional[str] = None) -> bool:
        """Rollback a deployment to a previous version."""
        deployment = self._deployments.get(deployment_name)
        if not deployment:
            return False

        return await self._lifecycle_manager.rollback(deployment, version)

    async def delete_deployment(self, deployment_name: str) -> bool:
        """Delete a deployment."""
        deployment = self._deployments.get(deployment_name)
        if not deployment:
            return False

        success = await self._lifecycle_manager.delete(deployment)
        if success:
            await self._health_monitor.remove_deployment(deployment_name)
            del self._deployments[deployment_name]

        return success

    async def get_deployment_status(self, deployment_name: str) -> Dict[str, Any]:
        """Get deployment status."""
        deployment = self._deployments.get(deployment_name)
        if not deployment:
            return {"status": "not_found"}

        return await deployment.get_status()

    async def list_deployments(self) -> List[str]:
        """List all deployments."""
        return list(self._deployments.keys())

    async def _validate_deployment_config(self, config: DeploymentConfig) -> bool:
        """Validate deployment configuration."""
        # Validate protocols
        supported_protocols = ['a2a', 'mcp', 'http', 'mqtt', 'grpc']
        for protocol in config.protocols:
            if protocol not in supported_protocols:
                return False

        # Validate reasoning engines
        supported_reasoning = ['rule_based', 'bdi', 'llm', 'hybrid', 'symbolic']
        for engine in config.reasoning_engines:
            if engine not in supported_reasoning:
                return False

        return True

    async def _create_deployment_instance(self, config: DeploymentConfig) -> Any:
        """Create deployment instance based on type."""
        if config.deployment_type == DeploymentType.LOCAL:
            from .local.supervisor import LocalDeployment
            return LocalDeployment(config)
        elif config.deployment_type == DeploymentType.DOCKER:
            from .containers.docker.image_builder import DockerDeployment
            return DockerDeployment(config)
        elif config.deployment_type == DeploymentType.KUBERNETES:
            from .containers.kubernetes.manifest_generator import KubernetesDeployment
            return KubernetesDeployment(config)
        elif config.deployment_type == DeploymentType.AWS:
            from .cloud.aws.ecs_deployment import AWSDeployment
            return AWSDeployment(config)
        # Add other deployment types...
        else:
            raise ValueError(f"Unsupported deployment type: {config.deployment_type}")

# Global deployment manager instance
deployment_manager = DeploymentManager()
```

### 2. Docker Image Builder (`containers/docker/image_builder.py`)

```python
"""
Docker image builder for OpenMAS deployments.

Builds Docker images with multi-protocol support and reasoning-agnostic configurations.
"""

import os
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path
import docker
from jinja2 import Template

from ...management.config_templating import ConfigTemplating

class DockerImageBuilder:
    """Builder for OpenMAS Docker images."""

    def __init__(self):
        self.docker_client = docker.from_env()
        self.config_templating = ConfigTemplating()

    async def build_image(self, config: Dict[str, Any]) -> str:
        """Build Docker image for OpenMAS deployment."""

        # Create temporary build context
        with tempfile.TemporaryDirectory() as build_dir:
            build_path = Path(build_dir)

            # Generate Dockerfile
            dockerfile_content = self._generate_dockerfile(config)
            (build_path / "Dockerfile").write_text(dockerfile_content)

            # Generate application configuration
            app_config = self._generate_app_config(config)
            config_dir = build_path / "config"
            config_dir.mkdir()
            (config_dir / "openmas.yaml").write_text(app_config)

            # Generate entrypoint script
            entrypoint_script = self._generate_entrypoint(config)
            (build_path / "entrypoint.sh").write_text(entrypoint_script)
            (build_path / "entrypoint.sh").chmod(0o755)

            # Build image
            image_tag = f"openmas/{config['name']}:{config.get('version', 'latest')}"

            try:
                image, build_logs = self.docker_client.images.build(
                    path=str(build_path),
                    tag=image_tag,
                    rm=True,
                    forcerm=True
                )

                return image_tag

            except docker.errors.BuildError as e:
                print(f"Docker build failed: {e}")
                raise

    def _generate_dockerfile(self, config: Dict[str, Any]) -> str:
        """Generate Dockerfile content."""

        dockerfile_template = Template("""
# OpenMAS Multi-Protocol, Reasoning-Agnostic Agent Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install OpenMAS
RUN pip install openmas=={{ version }}

# Copy application configuration
COPY config/ /app/config/

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Create non-root user
RUN useradd -m -u 1000 openmas
USER openmas

# Expose ports for protocols
{% for protocol in protocols %}
{% if protocol == 'http' %}
EXPOSE 8080
{% elif protocol == 'grpc' %}
EXPOSE 50051
{% elif protocol == 'mqtt' %}
EXPOSE 1883
{% endif %}
{% endfor %}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/health || exit 1

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
""")

        return dockerfile_template.render(
            version=config.get('openmas_version', '0.3.0'),
            protocols=config.get('protocols', ['a2a']),
            reasoning_engines=config.get('reasoning_engines', ['rule_based'])
        )

    def _generate_app_config(self, config: Dict[str, Any]) -> str:
        """Generate application configuration."""

        app_config = {
            'agent': {
                'name': config['name'],
                'protocols': config.get('protocols', ['a2a']),
                'reasoning': {
                    'primary_engine': config.get('reasoning_engines', ['rule_based'])[0],
                    'fallback_engines': config.get('reasoning_engines', ['rule_based'])[1:]
                }
            },
            'protocols': self._generate_protocol_config(config),
            'observability': {
                'logging': {
                    'level': config.get('log_level', 'INFO'),
                    'format': 'json'
                },
                'metrics': {
                    'enabled': True,
                    'port': 9090
                }
            },
            'security': config.get('security_config', {})
        }

        import yaml
        return yaml.dump(app_config, default_flow_style=False)

    def _generate_protocol_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate protocol-specific configuration."""
        protocol_config = {}

        for protocol in config.get('protocols', ['a2a']):
            if protocol == 'a2a':
                protocol_config['a2a'] = {
                    'agent_card': {
                        'name': config['name'],
                        'capabilities': config.get('capabilities', []),
                        'protocols': ['a2a']
                    }
                }
            elif protocol == 'mcp':
                protocol_config['mcp'] = {
                    'server_mode': True,
                    'resources': config.get('mcp_resources', []),
                    'tools': config.get('mcp_tools', [])
                }
            elif protocol == 'http':
                protocol_config['http'] = {
                    'port': 8080,
                    'host': '0.0.0.0',
                    'cors_enabled': True
                }

        return protocol_config

    def _generate_entrypoint(self, config: Dict[str, Any]) -> str:
        """Generate entrypoint script."""

        return """#!/bin/bash
set -e

# Wait for dependencies
echo "Waiting for dependencies..."
sleep 5

# Start OpenMAS agent
echo "Starting OpenMAS agent..."
exec python -m openmas.cli_tools.commands.agent.deploy \\
    --config /app/config/openmas.yaml \\
    --log-level ${LOG_LEVEL:-INFO}
"""

class DockerDeployment:
    """Docker deployment implementation."""

    def __init__(self, config):
        self.config = config
        self.image_builder = DockerImageBuilder()
        self.docker_client = docker.from_env()
        self.container = None

    async def initialize(self) -> bool:
        """Initialize Docker deployment."""
        try:
            # Build image
            self.image_tag = await self.image_builder.build_image(self.config.__dict__)
            return True
        except Exception as e:
            print(f"Failed to initialize Docker deployment: {e}")
            return False

    async def deploy(self) -> bool:
        """Deploy container."""
        try:
            # Run container
            self.container = self.docker_client.containers.run(
                self.image_tag,
                name=self.config.name,
                detach=True,
                ports=self._get_port_mapping(),
                environment=self._get_environment_vars(),
                restart_policy={"Name": "unless-stopped"}
            )

            return True

        except Exception as e:
            print(f"Failed to deploy container: {e}")
            return False

    def _get_port_mapping(self) -> Dict[str, int]:
        """Get port mapping for protocols."""
        port_mapping = {}

        for protocol in self.config.protocols:
            if protocol == 'http':
                port_mapping['8080/tcp'] = 8080
            elif protocol == 'grpc':
                port_mapping['50051/tcp'] = 50051
            elif protocol == 'mqtt':
                port_mapping['1883/tcp'] = 1883

        return port_mapping

    def _get_environment_vars(self) -> Dict[str, str]:
        """Get environment variables for container."""
        return {
            'OPENMAS_ENV': self.config.environment,
            'LOG_LEVEL': 'INFO'
        }

    async def get_status(self) -> Dict[str, Any]:
        """Get deployment status."""
        if not self.container:
            return {"status": "not_deployed"}

        self.container.reload()
        return {
            "status": self.container.status,
            "ports": self.container.ports,
            "image": self.container.image.tags[0] if self.container.image.tags else "unknown"
        }
```

## Integration with Other Components

### 1. Configuration System Integration

Deployment integrates with configuration through:

- **Environment-Specific Configs**: Different configurations per deployment environment
- **Template Generation**: Dynamic configuration generation for deployments
- **Validation**: Pre-deployment configuration validation
- **Secrets Management**: Secure handling of sensitive configuration data

### 2. Observability Integration

Deployment integrates with observability through:

- **Health Monitoring**: Deployment health checks and monitoring
- **Metrics Collection**: Deployment and runtime metrics
- **Log Aggregation**: Centralized logging across deployments
- **Alerting**: Deployment-specific alerts and notifications

## Configuration Integration

Deployment should be configured through the unified configuration schema:

```yaml
deployment:
  environments:
    development:
      type: "local"
      protocols: ["a2a", "http"]
      reasoning_engines: ["rule_based"]
      monitoring:
        enabled: true
        metrics_port: 9090
    production:
      type: "kubernetes"
      protocols: ["a2a", "mcp", "http"]
      reasoning_engines: ["llm", "rule_based"]
      replicas: 3
      resources:
        cpu: "500m"
        memory: "1Gi"
      security:
        tls_enabled: true
        authentication_required: true
  docker:
    base_image: "python:3.11-slim"
    registry: "registry.example.com"
    build_args:
      OPENMAS_VERSION: "0.3.0"
  kubernetes:
    namespace: "openmas"
    ingress:
      enabled: true
      host: "agents.example.com"
  cloud:
    aws:
      region: "us-west-2"
      ecs_cluster: "openmas-cluster"
    azure:
      resource_group: "openmas-rg"
      location: "West US 2"
    gcp:
      project: "openmas-project"
      region: "us-central1"
```

## Success Criteria
- Complete Deployment directory structure created
- Local deployment supervisor functional
- Docker image building and container deployment working
- Kubernetes manifest generation and deployment operational
- Cloud deployment configurations for AWS, Azure, GCP implemented
- Multi-protocol and reasoning-agnostic deployment support verified
- Security controls and environment management functional
- Health monitoring and rollback capabilities working
- Configuration schema alignment maintained

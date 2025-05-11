# Asset Management in OpenMAS

OpenMAS provides a robust Asset Management system to help developers manage, download, verify, and access external assets required by their agents. This guide explains how to configure and use this feature.

## Overview

The Asset Management feature allows you to:

- Declaratively define external assets required by your agents in your project configuration
- Automatically download and cache assets as needed
- Verify asset integrity with checksums
- Support various source types: HTTP, Hugging Face Hub, and local files
- Secure access to gated resources with authentication
- Configure download retries, progress reporting, and archive unpacking
- Access assets programmatically from your agents

## Configuring Assets

Assets are defined in your `openmas_project.yml` file in two main sections:

1. The global `assets` list defines all assets available to your project
2. Each agent's `required_assets` list specifies which assets that agent needs

### Global Assets Configuration

```yaml
# openmas_project.yml
name: "my_project"
version: "0.1.0"

# Define all assets used in the project
assets:
  - name: "llama3-8b"
    version: "1.0"
    asset_type: "model"
    description: "Llama 3 8B model weights"
    source:
      type: "hf"
      repo_id: "meta-llama/Llama-3-8B"
      filename: "model.safetensors"
      revision: "main"
    checksum: "sha256:a1b2c3d4e5f6..."
    # Authentication for gated models
    authentication:
      strategy: "env_token"
      hf:
        token_env_var: "HUGGING_FACE_HUB_TOKEN"
    # Download retry configuration
    retries: 3
    retry_delay_seconds: 10
    # Progress reporting
    progress_report: true

  - name: "prompt-templates"
    version: "latest"
    asset_type: "template"
    description: "Collection of prompt templates"
    source:
      type: "http"
      url: "https://example.com/assets/prompt-templates.zip"
    checksum: "sha256:f6e5d4c3b2a1..."
    # Unpacking configuration
    unpack: true
    unpack_format: "zip"
    # Authentication for HTTP
    authentication:
      strategy: "env_token"
      http:
        token_env_var: "MY_API_KEY"
        scheme: "Bearer"
        header_name: "Authorization"
    # Progress reporting
    progress_report: true
    progress_report_interval_mb: 10

  - name: "knowledge-index"
    version: "2023-06"
    asset_type: "index"
    description: "Vector index of knowledge base"
    source:
      type: "local"
      path: "/opt/shared-assets/knowledge-index.bin"
    checksum: "sha256:1a2b3c4d5e6f..."

# Settings for asset management
settings:
  assets:
    cache_dir: "/app/data/asset-cache"  # Optional, defaults to ~/.openmas/assets/
```

### Agent Asset Requirements

```yaml
# openmas_project.yml (continued)
agents:
  rag_agent:
    module: "agents.rag_agent"
    class: "RAGAgent"
    required_assets:
      - "llama3-8b"
      - "knowledge-index"

  template_agent:
    module: "agents.template_agent"
    class: "TemplateAgent"
    required_assets:
      - "prompt-templates"
```

## Asset Configuration Options

### Asset Configuration

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `name` | string | Unique name for the asset | Yes |
| `version` | string | Asset version | No (defaults to "latest") |
| `asset_type` | string | Type of asset (e.g., "model", "data", "template") | No (defaults to "model") |
| `source` | object | Source configuration (see below) | Yes |
| `checksum` | string | SHA256 checksum for verification (format: "sha256:<hex_digest>") | No |
| `unpack` | boolean | Whether to unpack an archive file | No (defaults to false) |
| `unpack_format` | string | Archive format ("zip", "tar", "tar.gz", "tar.bz2") | Yes if `unpack` is true |
| `unpack_destination_is_file` | boolean | If true and unpack is set, the unpacked content is expected to be a single file, and the path returned will be to this file directly | No (defaults to false) |
| `description` | string | Human-readable description | No |
| `authentication` | object | Authentication configuration (see below) | No |
| `retries` | integer | Number of times to retry download on failure | No (defaults to 0) |
| `retry_delay_seconds` | float | Seconds to wait between retries | No (defaults to 5.0) |
| `progress_report` | boolean | Enable progress reporting for this asset during download | No (defaults to true) |
| `progress_report_interval_mb` | float | For HttpDownloader, report progress approximately every X MB downloaded | No (defaults to 5.0) |

### Authentication Configuration

The `authentication` field allows you to configure secure access to gated assets:

```yaml
authentication:
  strategy: "env_token"  # Currently the only supported strategy

  # For Hugging Face Hub assets:
  hf:
    token_env_var: "HUGGING_FACE_HUB_TOKEN"  # Name of env var containing the token

  # For HTTP/HTTPS assets:
  http:
    token_env_var: "MY_API_KEY"  # Name of env var containing the token
    scheme: "Bearer"             # Auth scheme (e.g., "Bearer", "Token", "Basic", or "" for none)
    header_name: "Authorization" # HTTP header name (e.g., "Authorization", "X-API-Key")
```

The `token_env_var` specifies which environment variable contains the actual authentication token. This approach keeps sensitive tokens out of your configuration files and allows different developers or environments to use different tokens without changing the configuration.

For Hugging Face Hub, the default environment variable is `HUGGING_FACE_HUB_TOKEN` if no `hf` block is provided.

### Source Configurations

#### HTTP Source

```yaml
source:
  type: "http"
  url: "https://example.com/path/to/asset.file"
```

#### Hugging Face Hub Source

```yaml
source:
  type: "hf"
  repo_id: "organization/model-name"
  filename: "model.safetensors"  # File within the repo
  revision: "main"  # Optional: branch, tag, or commit hash
```

#### Local File Source

```yaml
source:
  type: "local"
  path: "/path/to/local/file.bin"  # Absolute path or relative to project root
```

## Download Progress Reporting

OpenMAS provides flexible progress reporting during asset downloads:

1. **HTTP Downloads**: Shows progress in two ways:
   - In terminal environments: Uses tqdm progress bars for a rich interactive experience
   - In non-terminal environments: Logs progress at regular intervals (configurable with `progress_report_interval_mb`)

2. **Hugging Face Downloads**: Uses Hugging Face's native progress display system
   - Can be disabled by setting `progress_report: false`

Configure progress reporting in your asset configuration:

```yaml
assets:
  - name: "large-model"
    # ... other config ...
    progress_report: true                 # Enable/disable progress reporting
    progress_report_interval_mb: 10.0     # Report every 10 MB (for HTTP sources)
```

## Retry Mechanism

For handling transient network issues or temporary server errors, configure download retries:

```yaml
assets:
  - name: "large-model"
    # ... other config ...
    retries: 3                 # Number of retry attempts after initial download failure
    retry_delay_seconds: 10.0  # Seconds to wait between retry attempts
```

The asset manager will:
1. Attempt the download
2. If it fails, wait for the specified delay
3. Retry up to the specified number of times
4. Report detailed error information if all attempts fail

## Asset Cache

By default, assets are cached in `~/.openmas/assets/`. This location follows this structure:

```
~/.openmas/assets/
  ├── model/                         # asset_type
  │   └── llama3-8b/                 # asset name
  │       └── 1.0/                   # asset version
  │           ├── model.safetensors  # the actual asset
  │           └── .asset_info.json   # metadata
  └── .locks/                        # lock files for concurrent access
```

You can override the cache location in three ways (in order of precedence):

1. Environment variable: `OPENMAS_ASSETS_DIR=/path/to/cache`
2. Project config: `settings.assets.cache_dir: "/path/to/cache"` in `openmas_project.yml`
3. Default: `~/.openmas/assets/`

## Using Assets in Agents

Agents can access their configured assets programmatically using the `asset_manager` provided by OpenMAS:

```python
from openmas.agent import BaseAgent
from pathlib import Path

class MyAgent(BaseAgent):
    async def setup(self):
        # Get path to a required asset
        model_path: Path = await self.asset_manager.get_asset_path("llama3-8b")
        self.model = load_model(model_path)

        # Force re-download an asset if needed
        model_path = await self.asset_manager.get_asset_path("llama3-8b", force_download=True)

        # The asset_manager handles:
        # - Checking if the asset exists in cache
        # - Downloading if needed (with locking for concurrent access)
        # - Verifying integrity via checksum
        # - Unpacking archives if configured
        # - Implementing retries and progress reporting
        # - Managing authentication for gated assets
        # - Returning the final path
```

The `get_asset_path()` method is asynchronous and will:

1. Look up the asset configuration by name
2. Check if it exists in the cache and is valid
3. Download it if necessary (with proper locking to prevent race conditions)
4. Verify its checksum (if provided)
5. Unpack it (if configured)
6. Return the path to the asset

## CLI Commands

OpenMAS provides CLI commands to manage assets:

```bash
# List all configured assets and their status
openmas assets list

# Download a specific asset
openmas assets download llama3-8b
openmas assets download llama3-8b --force  # Force re-download even if cached

# Verify asset integrity
openmas assets verify llama3-8b
openmas assets verify  # Verify all cached assets

# Clear asset cache
openmas assets clear-cache --asset llama3-8b  # Clear specific asset
openmas assets clear-cache --all  # Clear entire cache (with confirmation)
```

See the [Assets CLI documentation](../cli/assets.md) for more details.

## Concurrency and Locking

OpenMAS uses file-based locking to ensure that multiple processes can safely access the asset cache without conflicts. This is particularly important when:

- Multiple agents request the same asset simultaneously
- Multiple instances of the same agent are running across different processes
- Assets are being downloaded while others are trying to use them

The locking system is transparent to the agent code and is handled automatically by the asset manager.

## Handling Secrets for Asset Authentication

For assets that require authentication (like gated Hugging Face models), use environment variables to store tokens:

1. Add your tokens to your `.env` file (which is automatically loaded by OpenMAS):
   ```
   HUGGING_FACE_HUB_TOKEN=hf_abcdefghijklmnopqrstuvwxyz
   MY_CUSTOM_API_KEY=api_123456789abcdef
   ```

2. Reference these environment variables in your asset configuration:
   ```yaml
   authentication:
     strategy: "env_token"
     hf:
       token_env_var: "HUGGING_FACE_HUB_TOKEN"
   ```

3. Make sure to include `.env` in your `.gitignore` to avoid committing sensitive tokens.

The asset downloader will automatically use the appropriate token from your environment when accessing protected resources.

## Best Practices

- **Always provide checksums** for important assets to ensure integrity
- **Configure appropriate retries** for large files or unreliable networks
- **Use authentication blocks** for gated resources
- **Enable progress reporting** for large downloads
- **Consider unpacking large archives** directly in the cache to avoid duplicating storage
- **Use version tags** for assets to manage updates and ensure reproducibility
- **Add `.env` to your `.gitignore** to prevent exposing secrets
- **Set appropriate cache locations** based on your deployment environment:
  - Development: Use default or local directory
  - Docker: Mount a volume for the cache to persist between container restarts
  - Production: Consider a shared network volume for clusters

# Hugging Face Asset Management in OpenMAS

OpenMAS provides robust support for downloading and managing assets from the Hugging Face Hub, including both single files and entire model repositories (sharded models).

## Prerequisites

To use Hugging Face Hub assets, you need to install the `huggingface_hub` package:

```bash
pip install huggingface_hub
```

Or if you're using Poetry:

```bash
poetry add huggingface_hub
```

## Configuring Hugging Face Assets

### Single File Download

For downloading a specific file from a Hugging Face repository:

```yaml
# In openmas_project.yml
assets:
  - name: llama-tokenizer
    version: "1.0"
    asset_type: "tokenizer"
    source:
      type: "hf"
      repo_id: "meta-llama/Llama-3-8B"
      filename: "tokenizer.model"  # Specify the filename to download a single file
      revision: "main"  # Optional, defaults to "main"
```

### Sharded Model Download (Entire Repository)

For downloading an entire repository or multiple files based on patterns:

```yaml
# In openmas_project.yml
assets:
  - name: llama-3-8b
    version: "1.0"
    asset_type: "model"
    source:
      type: "hf"
      repo_id: "meta-llama/Llama-3-8B"
      # No filename means download the whole repository
      # Optional: Filter which files to download
      allow_patterns: ["*.safetensors", "*.json", "*.model"]
      # Optional: Exclude certain files
      ignore_patterns: ["*.md", "examples/*"]
```

The `allow_patterns` and `ignore_patterns` fields accept either a single string or a list of glob patterns.

## Authentication

For accessing private repositories, you can configure authentication:

```yaml
# In openmas_project.yml
assets:
  - name: private-model
    version: "1.0"
    asset_type: "model"
    source:
      type: "hf"
      repo_id: "my-org/private-model"
      # For a single file:
      filename: "model.bin"
      # Or for a sharded model:
      # allow_patterns: ["*.bin", "*.json"]
      authentication:
        strategy: "env_token"
        hf:
          token_env_var: "HUGGINGFACE_TOKEN"  # Name of the environment variable holding your HF token
```

You can set the environment variable in various ways:

1. In your shell:
   ```bash
   export HUGGINGFACE_TOKEN=hf_your_token_here
   ```

2. In a `.env` file (OpenMAS automatically loads this):
   ```
   HUGGINGFACE_TOKEN=hf_your_token_here
   ```

3. Programmatically:
   ```python
   import os
   os.environ["HUGGINGFACE_TOKEN"] = "hf_your_token_here"
   ```

To get a Hugging Face token, visit your [Hugging Face account settings](https://huggingface.co/settings/tokens).

## Downloading Assets

You can download assets using the CLI:

```bash
# Download a single file asset
openmas assets download llama-tokenizer

# Download a sharded model
openmas assets download llama-3-8b
```

Or programmatically:

```python
import asyncio
from openmas.assets import AssetManager
from openmas.cli.utils import load_project_config

async def download_asset():
    project_config = load_project_config()
    asset_manager = AssetManager(project_config)

    # Download and get path to the asset
    asset_path = await asset_manager.get_asset_path("llama-3-8b", force_download=False)
    print(f"Asset downloaded to: {asset_path}")

# Run the async function
asyncio.run(download_asset())
```

## Best Practices

1. **Cache Management**: Assets are cached at `~/.openmas/assets/` by default. You can customize this location with the `OPENMAS_ASSETS_DIR` environment variable.

2. **Checksums**: For production use, include checksums to verify asset integrity:
   ```yaml
   assets:
     - name: llama-3-8b
       # ...
       checksum: "sha256:0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
   ```

3. **Version Control**: Always specify asset versions to ensure reproducibility.

4. **Download Patterns**: For sharded models with many files:
   - Use `allow_patterns` to include only necessary files (saves bandwidth and disk space)
   - Common patterns: `["*.safetensors", "*.json", "*.model", "config.json"]`

5. **Progress Reporting**: Control progress display with:
   ```yaml
   source:
     type: "hf"
     # ...
     progress_report: true  # Enable/disable progress reporting
     progress_report_interval_mb: 10.0  # Report progress every 10MB
   ```

## Troubleshooting

### Common Issues

1. **Missing Dependencies**:
   ```
   Error: Missing dependency 'huggingface_hub'
   ```
   Install the package: `pip install huggingface_hub`

2. **Authentication Errors**:
   ```
   Authentication error accessing Hugging Face Hub resource
   ```
   Check that your token is valid and correctly set in the environment variable.

3. **Not Found Errors**:
   ```
   Resource not found on Hugging Face Hub
   ```
   Verify the `repo_id`, `filename`, and `revision` are correct.

### Manually Downloading Models

If automatic downloading isn't working, you can download models manually and configure them as local assets:

```bash
# Download using git-lfs
git lfs install
git clone https://huggingface.co/meta-llama/Llama-3-8B /path/to/models/llama-3-8b
```

Then configure in `openmas_project.yml`:
```yaml
assets:
  - name: llama-3-8b
    version: "1.0"
    asset_type: "model"
    source:
      type: "local"
      path: "/path/to/models/llama-3-8b"
```

## API Reference

For more details, see the OpenMAS API reference for:

- `AssetSourceConfig` - Configuration for asset sources
- `AssetConfig` - Full asset configuration
- `AssetManager` - For programmatic asset management
- `HfDownloader` - The Hugging Face Hub downloader implementation

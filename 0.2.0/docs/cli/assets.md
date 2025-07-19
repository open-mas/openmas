# Assets CLI Commands

OpenMAS provides a set of CLI commands to manage assets defined in your project.

## Overview

The `openmas assets` command group helps you:

- List all assets defined in your project and their current status
- Download assets on-demand, with options to force re-download
- Verify the integrity of downloaded assets
- Clear the asset cache when needed

## Commands

### List Assets

```bash
openmas assets list
```

Lists all assets defined in your project configuration (`openmas_project.yml`) along with their current status.

**Output example:**

```
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name            ┃ Version ┃ Type       ┃ Source               ┃ Status                               ┃ Cache Path                  ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ llama3-8b       │ 1.0     │ model      │ hf:meta-llama/...    │ ✅ Downloaded and verified           │ ~/.openmas/assets/model/... │
│ prompt-templates│ latest  │ template   │ http://example.com/..│ ❌ Not found                         │ -                           │
│ knowledge-index │ 2023-06 │ index      │ local:/opt/shared/.. │ ⚠️ Downloaded but checksum mismatch │ ~/.openmas/assets/index/... │
└─────────────────┴─────────┴────────────┴─────────────────────┴─────────────────────────────────────┴────────────────────────────┘
```

The status column shows:
- ✅ Downloaded and verified: Asset is downloaded and checksum verified (if provided)
- ⚠️ Downloaded but checksum mismatch: Asset is downloaded but checksum doesn't match
- ❌ Not found: Asset is not in cache

### Download Asset

```bash
openmas assets download <asset_name> [--force]
```

Downloads a specific asset to the cache.

**Purpose:**
The `download` command fetches assets specified in your `openmas_project.yml` configuration from their defined sources and stores them in the OpenMAS asset cache. This command ensures that models, templates, and other resources are available for your agents to use.

**Arguments:**
- `asset_name` (Required): The unique name of the asset as specified in the `assets` list in your `openmas_project.yml`.

**Options:**
- `--force`, `-f`: Boolean flag. If set, the asset will be re-downloaded even if it already exists in the cache and appears verified.

**Prerequisites for Specific Asset Types:**
- **Hugging Face Assets (type: 'hf'):** Requires the `huggingface_hub` Python library. If not installed, the command will detect this and instruct you to install it with:
  ```bash
  pip install huggingface_hub
  ```

- **HTTP Assets (type: 'http'):** No additional dependencies required.

- **Local Assets (type: 'local'):** No download occurs; the command simply verifies the file exists at the specified path.

**Running the Command:**
The command should be run from within an OpenMAS project directory (or a subdirectory), where `openmas_project.yml` can be found. This ensures the command has access to your asset definitions.

**Environment Setup:**
- Ensure `openmas` and any necessary underlying libraries (like `huggingface_hub` for 'hf' assets) are installed in your active Python environment.
- If using Poetry for your project, run as `poetry run openmas assets download ...`.
- If using a virtual environment, activate it first.

**Asset Caching:**
Downloaded assets are stored in the OpenMAS asset cache:
- Default location: `~/.openmas/assets/`
- This can be overridden with the `OPENMAS_ASSETS_DIR` environment variable
- Assets are organized by type, name, and version: `~/.openmas/assets/<asset_type>/<asset_name>/<asset_version>/`

**Examples:**

Download a model from Hugging Face:
```bash
openmas assets download llama-tokenizer
```

```
Downloading asset "llama-tokenizer" (version 1.0)...
Source: Hugging Face Hub (meta-llama/Llama-3-8B/tokenizer.model)
Progress: ████████████████████████████████ 100%
Verifying checksum... OK
Asset downloaded to: /home/user/.openmas/assets/tokenizer/llama-tokenizer/1.0/tokenizer.model
```

Force re-download of an asset that already exists in cache:
```bash
openmas assets download prompt-templates --force
```

```
Downloading asset "prompt-templates" (version latest)...
Source: HTTP (https://example.com/templates.zip)
Progress: ████████████████████████████████ 100%
Unpacking archive... OK
Verifying checksum... OK
Asset downloaded to: /home/user/.openmas/assets/template/prompt-templates/latest/
```

Download a sharded model (multiple files) from Hugging Face:
```bash
openmas assets download llama-3-8b
```

```
Downloading asset "llama-3-8b" (version 1.0)...
Source: Hugging Face Hub Repository (meta-llama/Llama-3-8B)
Progress managed by Hugging Face Hub...
Verifying integrity... OK
Asset downloaded to: /home/user/.openmas/assets/model/llama-3-8b/1.0/
```

If using Poetry:
```bash
poetry run openmas assets download llama-3-8b
```

### Verify Asset

```bash
openmas assets verify [asset_name]
```

Verifies the integrity of one or all cached assets.

**Arguments:**

| Argument | Description |
|----------|-------------|
| `asset_name` | (Optional) Name of the asset to verify. If omitted, all cached assets are verified. |

**Examples:**

Verify a specific asset:
```bash
openmas assets verify llama3-8b
```

Output:
```
Verifying asset "llama3-8b" (version 1.0)...
Expected checksum: sha256:a1b2c3d4e5f6...
Calculated checksum: sha256:a1b2c3d4e5f6...
Result: ✅ Verification successful
```

Verify all assets:
```bash
openmas assets verify
```

Output:
```
Verifying all cached assets...

llama3-8b (version 1.0):
  Expected checksum: sha256:a1b2c3d4e5f6...
  Calculated checksum: sha256:a1b2c3d4e5f6...
  Result: ✅ Verification successful

knowledge-index (version 2023-06):
  Expected checksum: sha256:1a2b3c4d5e6f...
  Calculated checksum: sha256:9z8y7x6w5v4...
  Result: ❌ Verification failed

Summary:
  Total assets: 2
  Passed: 1
  Failed: 1
```

### Clear Cache

```bash
openmas assets clear-cache [--asset ASSET_NAME] [--all]
```

Clears the asset cache, either for a specific asset or the entire cache.

**Options:**

| Option | Description |
|--------|-------------|
| `--asset`, `-a` | Name of the asset to clear from cache |
| `--all` | Clear the entire asset cache (will prompt for confirmation) |

**Examples:**

Clear a specific asset:
```bash
openmas assets clear-cache --asset llama3-8b
```

Output:
```
Clearing asset "llama3-8b" (version 1.0) from cache...
Cache location: /home/user/.openmas/assets/model/llama3-8b/1.0
Are you sure you want to clear the cache for asset 'llama3-8b'? [y/N]: y
Asset cache successfully cleared.
```

Clear all assets:
```bash
openmas assets clear-cache --all
```

Output:
```
This will clear the entire asset cache at:
/home/user/.openmas/assets/

Are you sure you want to clear the entire asset cache? [y/N]: y
Successfully cleared entire assets cache.
```

## Environment Variables

The asset CLI commands respect the same environment variables as the core asset management system:

| Environment Variable | Description | Default |
|----------------------|-------------|---------|
| `OPENMAS_ASSETS_DIR` | Override the default asset cache directory | `~/.openmas/assets/` |
| `OPENMAS_ENV` | Environment name for loading configuration | `local` |

In addition, asset authentication can use environment variables like:

| Environment Variable | Description |
|----------------------|-------------|
| `HUGGINGFACE_TOKEN` | Default token for Hugging Face Hub authentication |
| Custom variables | Any custom variable referenced in `authentication.*.token_env_var` |

## Using .env for Authentication

When using the asset commands, OpenMAS automatically loads environment variables from a `.env` file in your project root. This is especially useful for storing authentication tokens for gated assets:

```
# .env file
HUGGINGFACE_TOKEN=hf_abcdefghijklmnopqrstuvwxyz
MY_CUSTOM_API_KEY=api_123456789abcdef
```

Make sure to add `.env` to your `.gitignore` to prevent accidentally committing sensitive tokens.

## Examples

**Download all assets defined in your project:**

```bash
# List all assets
openmas assets list | grep "Not found" | awk '{print $1}' > missing_assets.txt

# Download each missing asset
while read asset; do
  openmas assets download $asset
done < missing_assets.txt
```

**Verify and re-download corrupted assets:**

```bash
# Verify all assets and capture results
openmas assets verify > verification_results.txt

# Extract failed assets
grep "failed" verification_results.txt | awk '{print $1}' > failed_assets.txt

# Re-download failed assets
while read asset; do
  openmas assets clear-cache --asset $asset
  openmas assets download $asset --force
done < failed_assets.txt
```

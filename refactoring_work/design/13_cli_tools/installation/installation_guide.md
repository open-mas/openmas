# OpenMAS CLI Installation Guide

This guide provides detailed instructions for installing and setting up the OpenMAS command-line interface (CLI) tools.

## Prerequisites

Before installing the OpenMAS CLI, ensure you have the following prerequisites:

- Python 3.8 or later
- pip (Python package manager)
- Git (for development installations)

## Installation Methods

### Method 1: PyPI Installation (Recommended)

```bash
pip install openmas-cli
```

### Method 2: Development Installation

For contributors and developers who want to modify the CLI:

```bash
git clone https://github.com/openmas-ai/openmas.git
cd openmas
pip install -e .[cli]
```

## Verification

To verify the installation was successful:

```bash
openmas --version
```

You should see the version number of the installed OpenMAS CLI.

## Configuration

After installation, you can configure the CLI with your preferred settings:

```bash
openmas config init
```

This will create a default configuration file that you can customize.

## Platform-Specific Instructions

### Windows

For Windows users, ensure you have Python in your PATH environment variable. You may need to use `py -m pip` instead of `pip` in some environments.

### macOS

macOS users may need to use `pip3` instead of `pip` if both Python 2 and 3 are installed.

### Linux

Linux installations may require `sudo` privileges for global installation:

```bash
sudo pip install openmas-cli
```

Alternatively, you can install for the current user only:

```bash
pip install --user openmas-cli
```

## Troubleshooting

If you encounter issues during installation:

1. Ensure you have the latest pip version: `pip install --upgrade pip`
2. Check for dependency conflicts: `pip check`
3. Try installing in a virtual environment:
   ```bash
   python -m venv openmas-env
   source openmas-env/bin/activate  # On Windows: openmas-env\Scripts\activate
   pip install openmas-cli
   ```

## Next Steps

After installation, refer to the [Command Reference](../commands/README.md) for information on available commands and their usage.

# OpenMAS Project Setup Guide

This guide explains how to set up an OpenMAS project using your preferred Python environment management approach.

## Prerequisites

- Python 3.9 or higher
- Your preferred package manager (pip, Poetry, or Conda)

## Creating a New OpenMAS Project

### 1. Install OpenMAS

**Using pip:**
```bash
pip install openmas
```

**Using Poetry:**
```bash
poetry add openmas
```

**Using Conda:**
```bash
conda create -n openmas-env python=3.9
conda activate openmas-env
pip install openmas
```

### 2. Initialize Your Project

```bash
mkdir my_openmas_project
cd my_openmas_project
openmas init .
```

With Poetry:
```bash
openmas init . --poetry
```

### 3. Project Structure

```
my_openmas_project/
├── README.md
├── agents/                # Your agents go here
├── assets/                # Local assets
├── openmas_project.yml    # Project configuration
└── requirements.txt       # Dependencies (or pyproject.toml)
```

## Setting Up Your Environment

### Option A: Using venv and pip

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

### Option B: Using Poetry

```bash
poetry install
poetry shell
# Or run commands without activating:
poetry run openmas --help
```

### Option C: Using Conda

```bash
conda create -n my_project_env python=3.9
conda activate my_project_env
pip install -r requirements.txt
```

## Configuring Your Project

Edit `openmas_project.yml` to define your agents:

```yaml
project:
  name: my_openmas_project
  description: My OpenMAS project

agents:
  - name: example_agent
    class: agents.example.ExampleAgent
    config:
      param1: value1
```

## Creating Your First Agent

1. Create directories:
```bash
mkdir -p agents/example
```

2. Create `agents/example/agent.py`:
```python
from openmas.agent import Agent
from openmas.logging import get_logger

logger = get_logger(__name__)

class ExampleAgent(Agent):
    async def setup(self):
        logger.info(f"Setting up {self.name}")

    async def run(self):
        logger.info(f"Running {self.name}")
        param1 = self.config.get("param1", "default")
        logger.info(f"Param1: {param1}")

    async def cleanup(self):
        logger.info(f"Cleaning up {self.name}")
```

## Running Your Agent

**With venv or conda (after activating):**
```bash
openmas run example_agent
```

**With Poetry:**
```bash
poetry run openmas run example_agent
```

## Testing

**With pytest:**
```bash
# Using venv (activated)
pytest tests/

# Using Poetry
poetry run pytest tests/

# Using tox
tox -e unit
```

## Additional Resources

- [Your First OpenMAS Application](./first_application.md)
- [Asset Management Guide](../asset_management.md)
- [OpenMAS CLI Documentation](../../cli/index.md)

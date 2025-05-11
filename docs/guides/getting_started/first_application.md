# Your First OpenMAS Application: A Step-by-Step Guide

This guide will walk you through creating your first OpenMAS application from scratch. We'll cover project setup, environment configuration, agent creation, and execution - all in a way that works with your preferred Python environment management approach.

## Prerequisites

Before starting, ensure you have:

- Python 3.9 or higher installed
- Basic familiarity with Python and terminal/command line usage

## Project Initialization

Let's start by creating a new OpenMAS project:

```bash
# Install OpenMAS if you haven't already
# Choose the appropriate command for your environment:
pip install openmas       # Standard pip
# OR
poetry add openmas        # If using Poetry
# OR
conda install openmas     # If using Conda

# Create a new project
openmas init my_first_app
cd my_first_app
```

This will generate the basic structure for your OpenMAS project:

```
my_first_app/
├── README.md              # Project documentation
├── agents/                # Directory for your agents
├── assets/                # Local assets directory
├── openmas_project.yml    # OpenMAS project configuration
└── requirements.txt       # Python dependencies
```

Let's look at the generated project configuration:

```yaml
# openmas_project.yml
project:
  name: my_first_app
  description: My first OpenMAS application

agents:
  # No agents defined yet

assets:
  # No assets defined yet
```

## Setting Up Your Python Environment

OpenMAS works with any standard Python environment management tool. Choose **one** of the following methods based on your preference:

### Method A: Using `venv` and `pip`

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Method B: Using Poetry

```bash
# If you created the project with openmas init . --poetry
poetry install

# Activate the Poetry environment
poetry shell
```

### Method C: Using Conda

```bash
# Create a conda environment
conda create -n my_openmas_env python=3.9
conda activate my_openmas_env

# Install dependencies
pip install -r requirements.txt
```

## Creating Your First Agent

Now let's create a simple agent that logs a greeting message:

1. Create a directory for your agent:

```bash
mkdir -p agents/hello_agent
```

2. Create a file `agents/hello_agent/agent.py` with the following content:

```python
from openmas.agent import Agent
from openmas.logging import get_logger

logger = get_logger(__name__)

class HelloAgent(Agent):
    """A simple agent that says hello."""

    async def setup(self):
        """Initialize the agent."""
        logger.info(f"Setting up {self.name}")

    async def run(self):
        """Run the agent."""
        logger.info(f"Hello from {self.name}! I'm running!")

        # Access agent configuration if provided
        message = self.config.get("message", "No custom message provided")
        logger.info(f"Custom message: {message}")

        # You can also create tasks that run periodically
        # await self.create_task(self.periodic_task())

    async def periodic_task(self):
        """Example of a periodic task."""
        import asyncio
        while True:
            logger.info("This is a periodic task")
            await asyncio.sleep(5)  # Sleep for 5 seconds

    async def cleanup(self):
        """Clean up resources when agent stops."""
        logger.info(f"Cleaning up {self.name}")
```

3. Update your `openmas_project.yml` to include the agent:

```yaml
project:
  name: my_first_app
  description: My first OpenMAS application

agents:
  - name: hello_agent
    class: hello_agent.agent.HelloAgent
    config:
      message: "Welcome to OpenMAS!"

assets:
  # No assets defined yet
```

## Running Your Agent

Now let's run the agent. Use the appropriate command for your environment setup:

```bash
# If using venv or conda (make sure your environment is activated):
openmas run hello_agent

# If using Poetry and you prefer not to activate the environment:
poetry run openmas run hello_agent
```

You should see output similar to:

```
INFO     hello_agent.agent:agent.py:12 - Setting up hello_agent
INFO     hello_agent.agent:agent.py:16 - Hello from hello_agent! I'm running!
INFO     hello_agent.agent:agent.py:19 - Custom message: Welcome to OpenMAS!
...
^C  # Press Ctrl+C to stop the agent
INFO     hello_agent.agent:agent.py:32 - Cleaning up hello_agent
```

## Adding Multiple Agents

Let's add a second agent to demonstrate how multiple agents can work together:

1. Create a new agent directory:

```bash
mkdir -p agents/timer_agent
```

2. Create `agents/timer_agent/agent.py`:

```python
import asyncio
from datetime import datetime
from openmas.agent import Agent
from openmas.logging import get_logger

logger = get_logger(__name__)

class TimerAgent(Agent):
    """An agent that periodically announces the time."""

    async def setup(self):
        """Initialize the agent."""
        logger.info(f"Setting up {self.name}")
        self.interval = self.config.get("interval", 10)  # Default to 10 seconds

    async def run(self):
        """Run the agent."""
        logger.info(f"{self.name} is running with interval of {self.interval} seconds")

        # Create a periodic task
        await self.create_task(self.announce_time())

    async def announce_time(self):
        """Periodically announce the current time."""
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            logger.info(f"Current time is: {current_time}")
            await asyncio.sleep(self.interval)

    async def cleanup(self):
        """Clean up resources when agent stops."""
        logger.info(f"Cleaning up {self.name}")
```

3. Update `openmas_project.yml` to include both agents:

```yaml
project:
  name: my_first_app
  description: My first OpenMAS application

agents:
  - name: hello_agent
    class: hello_agent.agent.HelloAgent
    config:
      message: "Welcome to OpenMAS!"

  - name: timer_agent
    class: timer_agent.agent.TimerAgent
    config:
      interval: 5  # Announce time every 5 seconds

assets:
  # No assets defined yet
```

4. Run both agents simultaneously (using the appropriate command for your environment):

```bash
# With venv or conda (activated environment):
openmas run hello_agent timer_agent

# With Poetry (without activating):
poetry run openmas run hello_agent timer_agent
```

## Next Steps

Congratulations! You've created your first OpenMAS application with multiple agents. Here are some suggestions for what to explore next:

1. **Agent Communication**: Learn how to set up communication between agents using the various communication methods provided by OpenMAS.

2. **Assets Management**: Add model assets to your project and learn how to use them in your agents.

3. **LLM Integration**: Connect your agents to language models for more intelligent behavior.

4. **Deployment**: Learn how to deploy your agents in different environments.

5. **Patterns**: Explore agent design patterns like chaining, parallel processing, and more.

For detailed information on these topics, check the respective guides in the OpenMAS documentation.

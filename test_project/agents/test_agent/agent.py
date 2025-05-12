"""Test agent for MCP port configuration issue."""

import asyncio
import json

from openmas.agent import BaseAgent


class Agent(BaseAgent):
    """Test agent for MCP port configuration issue."""

    async def setup(self):
        """Set up the agent and print configuration."""
        # Print communicator type
        comm_type = self.communicator.__class__.__name__
        print(f"COMM_TYPE:{comm_type}")

        # Print communicator configuration
        if hasattr(self.config, "communicator_type"):
            print(f"CONFIG_COMM_TYPE:{self.config.communicator_type}")

        if hasattr(self.config, "communicator_options"):
            # Print as JSON for easy parsing
            print(f"COMM_OPTIONS:{json.dumps(self.config.communicator_options)}")

        # Print the actual port used by the MCP/SSE communicator
        if hasattr(self.communicator, "http_port"):
            print(f"MCP_SSE_PORT:{self.communicator.http_port}")

        # Print the port passed to FastMCP, which is the actual server port
        if hasattr(self.communicator, "fastmcp_server"):
            if hasattr(self.communicator.fastmcp_server, "port"):
                print(f"FASTMCP_PORT:{self.communicator.fastmcp_server.port}")

    async def run(self):
        """Run the agent briefly for testing."""
        print("AGENT_STARTED")
        await asyncio.sleep(1)
        print("AGENT_COMPLETED")
        return

    async def shutdown(self):
        """Shut down the agent."""
        print("AGENT_SHUTDOWN")

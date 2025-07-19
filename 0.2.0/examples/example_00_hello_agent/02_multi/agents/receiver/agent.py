"""Receiver agent implementation for real multi-agent hello world example."""

import asyncio
from openmas.agent import BaseAgent


class Agent(BaseAgent):
    """A receiver agent that receives and responds to messages from the sender agent."""

    def __init__(self, shutdown_event: asyncio.Event = None, **kwargs):
        super().__init__(**kwargs)
        self.shutdown_event = shutdown_event or asyncio.Event()
        self.message_received = False

    async def setup(self) -> None:
        """Initialize the agent."""
        self.logger.info("Setting up the Receiver Agent")
        
        # Register message handlers
        await self.communicator.register_handler("handle_message", self.handle_message)
        await self.communicator.register_handler("ping", self.ping)

    async def ping(self, params: dict) -> dict:
        """Simple ping handler to check if the agent is online.
        
        Args:
            params: Empty dictionary
            
        Returns:
            A response indicating the agent is online
        """
        self.logger.debug("Received ping request")
        return {"status": "online"}

    async def handle_message(self, payload: dict) -> dict:
        """Handle incoming messages from the sender agent.
        
        Args:
            payload: The message payload, expected to contain a greeting
            
        Returns:
            A response message acknowledging receipt
        """
        self.logger.info(f"📨 Received message: {payload}")
        
        # Extract greeting if present
        greeting = payload.get("greeting", "no greeting provided")
        
        # Set flag to indicate we received a message (useful for testing)
        self.message_received = True
        
        # Log the receipt
        self.logger.info(f"Successfully received greeting: '{greeting}'")
        
        # Return a response
        return {"status": "received", "message": "Hello received and acknowledged!"}

    async def run(self) -> None:
        """Run the agent. This agent just waits for incoming messages."""
        self.logger.info("Receiver agent is running, waiting for messages")
        try:
            # This agent is passive and just waits for messages,
            # so we'll just keep it alive until shutdown is requested
            while not self.shutdown_event.is_set():
                await asyncio.sleep(1)
                
                # Display periodic heartbeat messages to show the agent is still alive
                if not self.message_received:
                    self.logger.debug("Waiting for messages...")
        except asyncio.CancelledError:
            self.logger.info("Run loop cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Agent encountered an error: {e}")
            raise

    async def shutdown(self) -> None:
        """Shut down the agent gracefully."""
        self.logger.info("Shutting down the Receiver agent")
        self.shutdown_event.set()

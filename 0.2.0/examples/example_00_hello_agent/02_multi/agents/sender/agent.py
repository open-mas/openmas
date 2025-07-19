"""Sender agent implementation for real multi-agent hello world example."""

import asyncio
from openmas.agent import BaseAgent


class Agent(BaseAgent):
    """A sender agent that sends a greeting message to the receiver agent using real HTTP communication."""

    def __init__(self, shutdown_event: asyncio.Event = None, **kwargs):
        super().__init__(**kwargs)
        self.shutdown_event = shutdown_event or asyncio.Event()
        self.message_sent = False
        self.receiver_available = False

    async def setup(self) -> None:
        """Initialize the agent."""
        self.logger.info("Setting up the Sender Agent")
        # Create a background task to check for receiver availability
        self.create_background_task(self._wait_for_receiver())

    async def _wait_for_receiver(self) -> None:
        """Wait for the receiver agent to come online."""
        self.logger.info("Waiting for receiver agent to be available...")
        retries = 0
        
        while not self.receiver_available and not self.shutdown_event.is_set():
            try:
                # Simple ping to check if receiver is available
                await self.communicator.send_request(
                    target_service="receiver", 
                    method="ping", 
                    params={}, 
                    timeout=1.0
                )
                self.receiver_available = True
                self.logger.info("✅ Receiver agent is now available!")
                
                # Once receiver is available, send the message
                await self._send_greeting()
            except Exception:
                retries += 1
                self.logger.debug(f"Receiver agent not available yet (attempt {retries}), waiting...")
                await asyncio.sleep(2)  # Retry after 2 seconds

    async def _send_greeting(self) -> None:
        """Send a greeting message to the receiver agent."""
        self.logger.info("Sending greeting to receiver agent")
        
        # Send message to receiver
        message = {"greeting": "Hello from a real agent!"}
        try:
            result = await self.communicator.send_request(
                target_service="receiver", 
                method="handle_message", 
                params=message
            )
            self.message_sent = True
            self.logger.info(f"Received response from receiver: {result}")
            
            # Start countdown and finish
            await self._run_countdown()
            
            # Auto-terminate for demonstration purposes
            self.logger.info("Example complete - agent terminating")
            await self.stop()
            
        except Exception as e:
            self.logger.error(f"Error sending message to receiver: {e}")

    async def _run_countdown(self) -> None:
        """Run a countdown after successful message exchange."""
        self.logger.info("Starting countdown (message exchange successful)...")
        
        # Countdown from 5 to 1
        for count in range(5, 0, -1):
            self.logger.info(f"Countdown: {count}...")
            await asyncio.sleep(1)
            
        # Finish with KABOOM!
        self.logger.info("🔥 KABOOM! 💥")
        await asyncio.sleep(0.5)

    async def run(self) -> None:
        """Run the agent main loop."""
        self.logger.info("Sender agent is running")
        try:
            # Keep running until shutdown is requested
            while not self.shutdown_event.is_set():
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.logger.info("Run loop cancelled")
            raise
        except Exception as e:
            self.logger.error(f"Agent encountered an error: {e}")
            raise

    async def shutdown(self) -> None:
        """Shut down the agent gracefully."""
        self.logger.info("Shutting down the Sender agent")
        self.shutdown_event.set()

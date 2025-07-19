"""Integration test for the real multi-agent hello world example.

This test demonstrates how to run multiple real agents programmatically
for testing purposes without requiring separate terminals.
"""

import asyncio
import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path
import pytest


async def run_agent_process(agent_name, log_file_path):
    """Run an agent in a separate process with output redirection.
    
    Args:
        agent_name: Name of the agent to run
        log_file_path: Path to the log file where agent output will be written
    
    Returns:
        The subprocess.Popen object representing the running agent process
    """
    # Get the current directory which should be the project root
    project_dir = Path(__file__).parent.absolute()
    
    # Open log file for writing
    log_file = open(log_file_path, "w")
    
    # Start the agent process with output redirection
    process = subprocess.Popen(
        ["openmas", "run", agent_name],
        stdout=log_file,
        stderr=subprocess.STDOUT,
        cwd=project_dir,
        # Ensure process doesn't receive keyboard interrupts from parent
        preexec_fn=os.setpgrp
    )
    
    return process


def kill_process_gracefully(process):
    """Attempt to kill a process gracefully.
    
    First sends SIGTERM to allow for clean shutdown, then SIGKILL if needed.
    
    Args:
        process: The subprocess.Popen object to terminate
    """
    if process.poll() is None:  # Check if process is still running
        try:
            # Try to terminate gracefully first (equivalent to Ctrl+C)
            process.send_signal(signal.SIGTERM)
            
            # Give it some time to shut down gracefully
            for _ in range(5):  # Try for 5 seconds
                if process.poll() is not None:
                    break  # Process has terminated
                time.sleep(1)
                
            # If still running, force kill
            if process.poll() is None:
                process.kill()  # SIGKILL
                process.wait()
        except Exception as e:
            print(f"Error terminating process: {e}")


def check_logs_for_success(log_file_path, success_markers):
    """Check if the agent logs contain the success markers.
    
    Args:
        log_file_path: Path to the log file to check
        success_markers: List of strings that should be present in logs for success
        
    Returns:
        bool: True if all success markers were found
    """
    with open(log_file_path, "r") as f:
        log_content = f.read()
        
    # Check if all success markers are present in the logs
    return all(marker in log_content for marker in success_markers)


@pytest.mark.asyncio
async def test_multi_agent_communication():
    """Test the communication between receiver and sender agents."""
    # Create temporary log files
    receiver_log = tempfile.NamedTemporaryFile(delete=False, suffix=".log").name
    sender_log = tempfile.NamedTemporaryFile(delete=False, suffix=".log").name
    
    try:
        # Start the receiver agent first
        print("Starting receiver agent...")
        receiver_process = await run_agent_process("receiver", receiver_log)
        
        # Wait a bit for the receiver to initialize
        await asyncio.sleep(3)
        
        # Start the sender agent
        print("Starting sender agent...")
        sender_process = await run_agent_process("sender", sender_log)
        
        # Give the agents time to communicate
        max_wait_time = 30  # Maximum wait time in seconds
        wait_interval = 2   # Check interval in seconds
        
        print(f"Waiting for agents to communicate (max {max_wait_time} seconds)...")
        
        # Monitor logs to detect success
        sender_success = False
        for _ in range(max_wait_time // wait_interval):
            # Check if the sender has successfully sent a message and completed
            sender_success = check_logs_for_success(
                sender_log, 
                ["Received response from receiver", "🔥 KABOOM! 💥", "Example complete"]
            )
            
            # Check if the receiver has received and processed a message
            receiver_success = check_logs_for_success(
                receiver_log,
                ["📨 Received message", "Successfully received greeting"]
            )
            
            if sender_success and receiver_success:
                print("✅ Communication successful!")
                break
                
            await asyncio.sleep(wait_interval)
        
        # Assert that communication was successful
        assert sender_success, "Sender did not successfully complete the communication"
        
        # Output the logs for debugging
        print("\n=== RECEIVER LOG ===")
        with open(receiver_log, "r") as f:
            print(f.read())
            
        print("\n=== SENDER LOG ===")
        with open(sender_log, "r") as f:
            print(f.read())
            
    finally:
        # Clean up processes and log files
        print("Cleaning up processes...")
        kill_process_gracefully(sender_process)
        kill_process_gracefully(receiver_process)
        
        # Clean up log files after the test
        if os.path.exists(receiver_log):
            os.unlink(receiver_log)
        if os.path.exists(sender_log):
            os.unlink(sender_log)


if __name__ == "__main__":
    # For manual running of the test
    asyncio.run(test_multi_agent_communication())

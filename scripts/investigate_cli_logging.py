#!/usr/bin/env python3
"""
Investigation script for analyzing logging behavior in the OpenMAS CLI.

This script helps identify why debug and info logs appear in the output of
commands like `openmas --version` where clean output is preferred.
"""

import importlib
import inspect
import os
import sys
import logging
from pathlib import Path

# Add the project to the path so we can import modules from it
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import key OpenMAS modules
import openmas
from openmas.logging import get_logger
import openmas.cli
import openmas.cli.main
from openmas.cli.main import cli, version_callback
import openmas.communication

# Utility functions for the investigation
def find_logger_calls(module_name):
    """Find all logger calls in a module."""
    try:
        module = sys.modules[module_name]
        source = inspect.getsource(module)
        result = []
        for i, line in enumerate(source.splitlines()):
            if "logger." in line and ("debug" in line or "info" in line):
                result.append((i + 1, line.strip()))
        return result
    except Exception as e:
        return [(-1, f"Error: {e}")]

def analyze_module_structure(module_name):
    """Analyze module structure to see when imports happen."""
    print(f"\n{'-'*80}")
    print(f"Module structure for: {module_name}")
    print(f"{'-'*80}")
    
    try:
        module = sys.modules[module_name]
        # Check for global imports and module-level code
        source = inspect.getsource(module)
        print("First 10 imports:")
        imports = [line.strip() for line in source.splitlines() if line.strip().startswith(("import ", "from "))]
        for imp in imports[:10]:
            print(f"  {imp}")
        
        print("\nGlobal variable initializations:")
        module_vars = vars(module)
        for name, value in list(module_vars.items())[:10]:
            if not name.startswith("__") and not inspect.isfunction(value) and not inspect.isclass(value):
                print(f"  {name} = {repr(value)[:60]}")
    except Exception as e:
        print(f"Error analyzing module structure: {e}")

def analyze_logging_setup():
    """Analyze how logging is set up in OpenMAS."""
    print(f"\n{'-'*80}")
    print(f"Analysis of OpenMAS logging setup")
    print(f"{'-'*80}")
    
    # Import and analyze the logging module
    import openmas.logging
    print(f"Logging module location: {openmas.logging.__file__}")
    
    # Show the implementation of get_logger
    try:
        print("\nImplementation of get_logger:")
        get_logger_source = inspect.getsource(openmas.logging.get_logger)
        print(get_logger_source)
    except Exception as e:
        print(f"Error getting get_logger source: {e}")
    
    # Check for log level configuration
    print("\nLog level configuration:")
    try:
        # Try to determine the default log level
        logger = get_logger("test.logger")
        print(f"Default log level: {logger.level}")
        print(f"Is debug enabled: {logger.isEnabledFor(logging.DEBUG)}")
        print(f"Logger handlers: {logger.handlers}")
        
        # Check for any environment variables that might affect logging
        print("\nEnvironment variables affecting logging:")
        for env_var, value in os.environ.items():
            if "log" in env_var.lower() or "debug" in env_var.lower():
                print(f"  {env_var}={value}")
    except Exception as e:
        print(f"Error checking log configuration: {e}")

def main():
    """Main investigation function."""
    print(f"\n{'='*80}")
    print(f"INVESTIGATION OF CLI LOGGING BEHAVIOR IN OPENMAS")
    print(f"{'='*80}")
    
    print("\nFocus: Why does 'openmas --version' display debug/info log messages?")
    
    # Analyze the main CLI module
    print(f"\n{'-'*80}")
    print(f"1. Analysis of CLI entry points and logging calls")
    print(f"{'-'*80}")
    print(f"CLI package location: {openmas.cli.__file__}")
    
    # Find all logger calls in the main CLI module
    logger_calls = find_logger_calls("openmas.cli.main")
    print(f"\nFound {len(logger_calls)} logger calls in CLI main module:")
    for line_no, call in logger_calls[:10]:  # Show first 10
        print(f"  Line {line_no}: {call}")
    
    # Check version_callback for any logging
    print(f"\nAnalysis of version_callback function:")
    try:
        version_source = inspect.getsource(version_callback)
        print(f"version_callback has any logging calls: {'logger.' in version_source}")
        if 'logger.' in version_source:
            for line in version_source.splitlines():
                if 'logger.' in line:
                    print(f"  {line.strip()}")
    except Exception as e:
        print(f"Error analyzing version_callback: {e}")
    
    # Find where the problematic logs are coming from
    print(f"\n{'-'*80}")
    print(f"2. Tracking sources of specific log messages")
    print(f"{'-'*80}")
    
    # Look for 'Registered communicator' logs
    print("Searching for 'Registered communicator' log sources:")
    for module_name in ['openmas.communication', 'openmas.communication.base', 'openmas.communication.http']:
        try:
            module = importlib.import_module(module_name)
            source = inspect.getsource(module)
            if "Registered communicator" in source:
                print(f"  Found in {module_name}")
                # Find the specific line
                for line in source.splitlines():
                    if "Registered communicator" in line:
                        print(f"    {line.strip()}")
        except Exception as e:
            print(f"  Error checking {module_name}: {e}")
    
    # Look for 'MCP SDK' logs
    print("\nSearching for 'MCP SDK' log sources:")
    for module_name in ['openmas.prompt', 'openmas.prompt.providers.mcp', 'openmas.integrations.mcp']:
        try:
            module = importlib.import_module(module_name)
            source = inspect.getsource(module)
            if "MCP SDK" in source:
                print(f"  Found in {module_name}")
                # Find the specific line
                for line in source.splitlines():
                    if "MCP SDK" in line:
                        print(f"    {line.strip()}")
        except Exception as e:
            print(f"  Error checking {module_name}: {e}")
    
    # Analyze module loading order and structure
    analyze_module_structure("openmas.cli.main")
    
    # Analyze logging setup
    analyze_logging_setup()
    
    # Investigate Click's handling of callback functions
    print(f"\n{'-'*80}")
    print(f"3. Analysis of Click's command handling")
    print(f"{'-'*80}")
    print("Checking how Click handles command callbacks:")
    
    import click
    version_opt = None
    for param in cli.params:
        if param.name == 'version':
            version_opt = param
            break
    
    if version_opt:
        print(f"Version option found in CLI:")
        print(f"  Name: {version_opt.name}")
        print(f"  Callback: {version_opt.callback}")
        print(f"  Is eager: {version_opt.is_eager}")
    else:
        print("Version option not found in CLI params")
    
    # Recommendations
    print(f"\n{'-'*80}")
    print(f"4. RECOMMENDATIONS")
    print(f"{'-'*80}")
    print("""
1. ROOT CAUSE:
   The debug/info logs are likely emitted during module imports, before the 
   version callback even runs. This happens because importing modules can trigger
   code execution that registers components and logs status.

2. POTENTIAL SOLUTIONS:
   a) Implement log silencing for specific commands:
      - Add a custom log filter for the --version/info commands
      - Temporarily change log level before running these commands
   
   b) Lazy-load components:
      - Ensure communication modules are only loaded when actually needed
      - Move non-essential imports into functions
   
   c) Add CLI option to control log verbosity:
      - Add --quiet flag globally to silence all logs
      - Check if a similar mechanism exists in the codebase already
    """)

if __name__ == "__main__":
    main() 
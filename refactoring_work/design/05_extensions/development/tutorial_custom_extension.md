# Building a Custom OpenMAS Extension: Step-by-Step Tutorial

## Overview

This tutorial walks through the complete process of creating a custom OpenMAS extension from initial setup to deployment. We'll build a "Weather Service" extension that allows agents to retrieve weather information regardless of which reasoning approach or protocol they use, demonstrating OpenMAS's reasoning agnosticism and protocol independence principles.

> **IMPORTANT**: Before starting this tutorial, please review the detailed documentation for the specific extension type you're interested in developing. Each extension type has its own interface requirements and integration patterns:
> 
> - [Agent Extensions](../extension_types/agent_extensions.md) - Enhance agent capabilities and behaviors
> - [Communicator Extensions](../extension_types/communicator_extensions.md) - Add support for new communication protocols
> - [Asset Extensions](../extension_types/assets.md) - Handle various types of assets and resources
> - [Prompt Extensions](../extension_types/prompts.md) - Manage and customize prompts
> - [LLM Extensions](../extension_types/llm_extensions.md) - Integrate with language models
> - [Reasoning Extensions](../extension_types/reasoning_extensions.md) - Implement custom reasoning approaches
> - [Protocol Adapter Extensions](../extension_types/protocol_adapters.md) - Enable communication between protocols
> - [Tool Extensions](../extension_types/tool_extensions.md) - Add new tool capabilities to agents
>
> This tutorial implements a Tool Extension, but the general principles apply to all extension types.

## Prerequisites

Before starting, ensure you have:

1. OpenMAS 0.3.0 or later installed
2. Python 3.9+ environment
3. Access to a weather API (we'll use a mock for demonstration)
4. Basic understanding of OpenMAS concepts and architecture
5. Familiarity with the [Extension Development Guide](./guide.md)

## Step 1: Setting Up the Extension Package

Create a directory structure for your extension:

```bash
mkdir -p weather_extension/openmas_weather
cd weather_extension
```

Create the package files:

```bash
touch openmas_weather/__init__.py
touch openmas_weather/extension.py
touch openmas_weather/config.py
touch openmas_weather/client.py
touch setup.py
touch README.md
```

Set up `setup.py` for your extension:

```python
from setuptools import setup, find_namespace_packages

setup(
    name="openmas-weather-extension",
    version="0.1.0",
    description="Weather service extension for OpenMAS",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_namespace_packages(),
    install_requires=[
        "openmas>=0.3.0",
        "requests>=2.25.0",
    ],
    entry_points={
        "openmas.extensions": [
            "weather_service=openmas_weather.extension:WeatherServiceExtension",
        ],
    },
)
```

## Step 2: Define Extension Configuration

Create the configuration schema in `config.py`:

```python
from pydantic import BaseModel, Field, AnyHttpUrl
from typing import Optional, List, Dict, Any

class WeatherApiConfig(BaseModel):
    """Configuration for the weather API service."""
    api_key_env: str = Field(
        "WEATHER_API_KEY", 
        description="Environment variable containing the API key"
    )
    base_url: AnyHttpUrl = Field(
        "https://api.weatherservice.example", 
        description="Base URL for the weather API"
    )
    timeout: int = Field(
        10, 
        description="Timeout in seconds for API requests"
    )
    units: str = Field(
        "metric", 
        description="Unit system (metric/imperial)"
    )
    cache_ttl: int = Field(
        300, 
        description="Cache time-to-live in seconds"
    )

class WeatherServiceConfig(BaseModel):
    """Configuration schema for the Weather Service extension."""
    enabled: bool = Field(
        True, 
        description="Whether the weather service is enabled"
    )
    api: WeatherApiConfig = Field(
        default_factory=WeatherApiConfig,
        description="API configuration"
    )
    default_location: Optional[str] = Field(
        None, 
        description="Default location for weather queries"
    )
    capabilities: List[str] = Field(
        ["current_weather", "forecast", "alerts"],
        description="Enabled capabilities"
    )
    protocol_mapping: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Protocol-specific capability name mapping"
    )
```

## Step 3: Implement API Client

Create a client for the weather API in `client.py`:

```python
import os
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WeatherClient:
    """Client for the weather service API."""
    
    def __init__(self, config):
        """Initialize the weather client with configuration."""
        self.config = config
        self.api_key = os.environ.get(config.api_key_env)
        if not self.api_key:
            logger.warning(f"API key not found in environment variable {config.api_key_env}")
        
        self.base_url = str(config.base_url)
        self.timeout = config.timeout
        self.units = config.units
        
        # Simple in-memory cache
        self._cache = {}
    
    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate a cache key from endpoint and parameters."""
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{endpoint}?{param_str}"
    
    def _is_cache_valid(self, cache_entry) -> bool:
        """Check if a cache entry is still valid."""
        if not cache_entry:
            return False
        timestamp, _ = cache_entry
        return datetime.now() < timestamp + timedelta(seconds=self.config.cache_ttl)
    
    def _request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make an API request with caching."""
        # Check cache first
        cache_key = self._get_cache_key(endpoint, params)
        cache_entry = self._cache.get(cache_key)
        
        if self._is_cache_valid(cache_entry):
            logger.debug(f"Cache hit for {cache_key}")
            _, data = cache_entry
            return data
        
        # Prepare request
        url = f"{self.base_url}/{endpoint}"
        request_params = {
            "key": self.api_key,
            "units": self.units,
            **params
        }
        
        # Make request
        try:
            response = requests.get(
                url, 
                params=request_params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # Cache response
            self._cache[cache_key] = (datetime.now(), data)
            return data
            
        except requests.RequestException as e:
            logger.error(f"Weather API request failed: {e}")
            raise
    
    def get_current_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather for a location."""
        return self._request("current", {"location": location})
    
    def get_forecast(self, location: str, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for a location."""
        return self._request("forecast", {"location": location, "days": days})
    
    def get_alerts(self, location: str) -> Dict[str, Any]:
        """Get weather alerts for a location."""
        return self._request("alerts", {"location": location})
    
    # For demonstration, we'll add a mock implementation that doesn't require an actual API
    def mock_implementation(self) -> bool:
        """Set up mock data instead of real API calls."""
        logger.info("Using mock weather data")
        
        # Create mock methods that override the real ones
        def mock_current(location):
            return {
                "location": location,
                "temperature": 22.5,
                "condition": "Partly cloudy",
                "humidity": 65,
                "wind_speed": 10,
                "wind_direction": "NW",
                "updated": datetime.now().isoformat()
            }
        
        def mock_forecast(location, days=5):
            return {
                "location": location,
                "days": [
                    {
                        "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                        "min_temp": 18 + i,
                        "max_temp": 25 + i,
                        "condition": "Sunny" if i % 2 == 0 else "Cloudy",
                        "precipitation": 0 if i % 2 == 0 else 15
                    }
                    for i in range(days)
                ]
            }
        
        def mock_alerts(location):
            return {
                "location": location,
                "alerts": []  # No alerts by default
            }
        
        # Replace real methods with mocks
        self.get_current_weather = mock_current
        self.get_forecast = mock_forecast
        self.get_alerts = mock_alerts
        
        return True
```

## Step 4: Implement the Extension Class

Create the main extension class in `extension.py`:

```python
from openmas.extensions import BaseExtension
from openmas.extensions.registry import ExtensionRegistry
from typing import Dict, Any, Optional, List
import logging
import os

from .config import WeatherServiceConfig
from .client import WeatherClient

logger = logging.getLogger(__name__)

class WeatherServiceExtension(BaseExtension):
    """
    Weather Service Extension for OpenMAS.
    
    This extension enables agents to retrieve weather information,
    demonstrating OpenMAS's reasoning agnosticism and protocol independence.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the extension with configuration."""
        super().__init__(config)
        self.config = WeatherServiceConfig(**config)
        self.client = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the extension and set up the weather client."""
        if self._initialized:
            return True
        
        if not self.config.enabled:
            logger.info("Weather service extension is disabled")
            return False
        
        # Create and initialize the weather client
        self.client = WeatherClient(self.config.api)
        
        # For demonstration purposes, use mock implementation
        # In production, you would use the real API
        if os.environ.get("OPENMAS_EXTENSIONS_MOCK", "").lower() == "true":
            self.client.mock_implementation()
        
        # Register capabilities with the extension registry
        registry = ExtensionRegistry.get_instance()
        
        if "current_weather" in self.config.capabilities:
            registry.register_capability(
                "current_weather",
                self.get_current_weather,
                {
                    "description": "Get the current weather for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "Location name, city, or coordinates"
                            }
                        },
                        "required": ["location"]
                    },
                    "returns": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "temperature": {"type": "number"},
                            "condition": {"type": "string"},
                            "humidity": {"type": "number"},
                            "wind_speed": {"type": "number"},
                            "wind_direction": {"type": "string"},
                            "updated": {"type": "string"}
                        }
                    }
                },
                protocol_mapping=self.config.protocol_mapping.get("current_weather", {})
            )
        
        if "forecast" in self.config.capabilities:
            registry.register_capability(
                "forecast",
                self.get_forecast,
                {
                    "description": "Get a weather forecast for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "Location name, city, or coordinates"
                            },
                            "days": {
                                "type": "integer",
                                "description": "Number of days to forecast",
                                "default": 5,
                                "minimum": 1,
                                "maximum": 10
                            }
                        },
                        "required": ["location"]
                    },
                    "returns": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "days": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "date": {"type": "string"},
                                        "min_temp": {"type": "number"},
                                        "max_temp": {"type": "number"},
                                        "condition": {"type": "string"},
                                        "precipitation": {"type": "number"}
                                    }
                                }
                            }
                        }
                    }
                },
                protocol_mapping=self.config.protocol_mapping.get("forecast", {})
            )
        
        if "alerts" in self.config.capabilities:
            registry.register_capability(
                "alerts",
                self.get_alerts,
                {
                    "description": "Get weather alerts for a location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "Location name, city, or coordinates"
                            }
                        },
                        "required": ["location"]
                    },
                    "returns": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "alerts": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "severity": {"type": "string"},
                                        "description": {"type": "string"},
                                        "start": {"type": "string"},
                                        "end": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                },
                protocol_mapping=self.config.protocol_mapping.get("alerts", {})
            )
        
        self._initialized = True
        logger.info("Weather service extension initialized successfully")
        return True
    
    async def get_current_weather(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get current weather for a location."""
        if not self._initialized:
            raise RuntimeError("Extension not initialized")
        
        location = location or self.config.default_location
        if not location:
            raise ValueError("Location is required")
        
        return self.client.get_current_weather(location)
    
    async def get_forecast(self, location: Optional[str] = None, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for a location."""
        if not self._initialized:
            raise RuntimeError("Extension not initialized")
        
        location = location or self.config.default_location
        if not location:
            raise ValueError("Location is required")
        
        return self.client.get_forecast(location, days)
    
    async def get_alerts(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get weather alerts for a location."""
        if not self._initialized:
            raise RuntimeError("Extension not initialized")
        
        location = location or self.config.default_location
        if not location:
            raise ValueError("Location is required")
        
        return self.client.get_alerts(location)
    
    async def shutdown(self) -> bool:
        """Clean up resources and shut down the extension."""
        logger.info("Shutting down weather service extension")
        self._initialized = False
        return True
```

## Step 5: Set Up Package Discovery

Update `__init__.py` to expose the extension class:

```python
"""Weather service extension for OpenMAS."""

from .extension import WeatherServiceExtension

__version__ = "0.1.0"
__all__ = ["WeatherServiceExtension"]
```

Create a README.md for your extension:

```markdown
# OpenMAS Weather Service Extension

This extension enables OpenMAS agents to retrieve weather information for any location, demonstrating OpenMAS's reasoning agnosticism and protocol independence principles.

## Features

- Current weather information
- Multi-day forecasts
- Weather alerts
- Location-based queries
- Protocol-independent operation
- Works with any agent reasoning approach

## Installation

```bash
pip install openmas-weather-extension
```

## Configuration

In your OpenMAS project configuration:

```yaml
extensions:
  weather_service:
    enabled: true
    api:
      api_key_env: "WEATHER_API_KEY"
      base_url: "https://api.weatherservice.example"
      timeout: 10
      units: "metric"
      cache_ttl: 300
    default_location: "New York"
    capabilities: ["current_weather", "forecast", "alerts"]
    protocol_mapping:
      a2a-http:
        current_weather: "getCurrentWeather"
        forecast: "getWeatherForecast"
        alerts: "getWeatherAlerts"
      mcp-sse:
        current_weather: "get_current_weather_tool"
        forecast: "get_weather_forecast_tool"
        alerts: "get_weather_alerts_tool"
```

## Usage

After installing and configuring the extension, agents can use the weather capabilities through any supported protocol:

### LLM-Based Agent (through MCP):

```yaml
agents:
  travel_planner:
    class: "agents.travel.TravelPlannerAgent"
    type: "llm"
    protocols:
      - type: "mcp-sse"
        enabled: true
    capabilities:
      multi_protocol_capabilities:
        core:
          - id: "plan_itinerary"
            # ...
    reasoning:
      type: "llm"
      llm_config:
        system_prompt: |
          You are a travel planning assistant.
          Use the weather information tools to suggest activities.
```

### Rule-Based Agent (through A2A):

```yaml
agents:
  activity_recommender:
    class: "agents.activities.ActivityRecommenderAgent"
    type: "rule_based"
    protocols:
      - type: "a2a-http"
        enabled: true
    capabilities:
      multi_protocol_capabilities:
        core:
          - id: "recommend_activities"
            # ...
    reasoning:
      type: "rule_based"
      rules:
        - name: "outdoor_activity"
          condition: "current_weather.condition == 'Sunny' AND current_weather.temperature > 20"
          action: "recommend_outdoor_activities"
```

## License

MIT
```

## Step 6: Build and Install the Extension

Build and install your extension locally:

```bash
pip install -e .
```

## Step 7: Configure in OpenMAS Project

Add the extension to your OpenMAS project configuration:

```yaml
# config.yaml
name: "My OpenMAS Project"
version: "1.0.0"

defaults:
  # ... other default configuration ...

  extensions:
    weather_service:
      enabled: true
      api:
        api_key_env: "WEATHER_API_KEY"
        base_url: "https://api.weatherservice.example"
        timeout: 10
        units: "metric"
        cache_ttl: 300
      default_location: "San Francisco"
      capabilities: ["current_weather", "forecast", "alerts"]
      protocol_mapping:
        a2a-http:
          current_weather: "getCurrentWeather"
          forecast: "getWeatherForecast"
          alerts: "getWeatherAlerts"
        mcp-sse:
          current_weather: "get_current_weather_tool"
          forecast: "get_weather_forecast_tool"
          alerts: "get_weather_alerts_tool"

# ... agent configuration ...
```

Set the environment variable for testing:

```bash
export WEATHER_API_KEY=your_api_key_here
# For testing with mock data
export OPENMAS_EXTENSIONS_MOCK=true
```

## Step 8: Use the Extension in Agents

### With LLM-Based Agents

LLM-based agents can use the weather service through the MCP protocol as tools:

```yaml
agents:
  travel_assistant:
    class: "agents.travel.TravelAssistantAgent"
    type: "llm"
    protocols:
      - type: "mcp-sse"
        enabled: true
    reasoning:
      type: "llm"
      llm_config:
        model: "gpt-4"
        temperature: 0.2
        system_prompt: |
          You are a travel assistant that helps plan trips.
          
          Use the weather tools to check conditions and provide
          appropriate recommendations based on the forecast.
          
          For sunny days, suggest outdoor activities.
          For rainy days, suggest indoor activities.
```

Example LLM-based agent code:

```python
from openmas.agents import LLMAgent
from openmas.reasoning import LLMReasoning

class TravelAssistantAgent(LLMAgent):
    async def setup(self):
        await super().setup()
        # Extension capabilities are automatically available through the registry
```

### With Rule-Based Agents

Rule-based agents can define rules using the weather capabilities:

```yaml
agents:
  activity_recommender:
    class: "agents.activities.ActivityRecommenderAgent"
    type: "rule_based"
    protocols:
      - type: "a2a-http"
        enabled: true
    reasoning:
      type: "rule_based"
      rules:
        - name: "sunny_day_activities"
          condition: "current_weather.temperature > 22 AND current_weather.condition == 'Sunny'"
          action: "recommend_outdoor_activities"
        - name: "rainy_day_activities"
          condition: "current_weather.condition == 'Rainy'"
          action: "recommend_indoor_activities"
```

Example rule-based agent code:

```python
from openmas.agents import RuleBasedAgent
from openmas.reasoning import RuleBasedReasoning
from openmas.extensions.registry import ExtensionRegistry

class ActivityRecommenderAgent(RuleBasedAgent):
    async def setup(self):
        await super().setup()
        self.registry = ExtensionRegistry.get_instance()
    
    async def recommend_outdoor_activities(self, context):
        location = context.get("location", self.config.get("default_location"))
        return {
            "activities": [
                "Hiking",
                "Beach visit",
                "Outdoor dining",
                "Sightseeing",
                "City tour"
            ],
            "weather": await self.registry.invoke_capability("current_weather", {"location": location})
        }
    
    async def recommend_indoor_activities(self, context):
        location = context.get("location", self.config.get("default_location"))
        return {
            "activities": [
                "Museum visit",
                "Shopping",
                "Indoor dining",
                "Spa day",
                "Movie theater"
            ],
            "weather": await self.registry.invoke_capability("current_weather", {"location": location})
        }
```

## Step 9: Protocol Independence Demonstration

The extension works seamlessly across different protocols:

### A2A Protocol

```python
# Making an A2A request to the agent
import requests

response = requests.post(
    "http://localhost:8000/agents/activity_recommender/capabilities/getCurrentWeather",
    json={"location": "London"}
)
weather_data = response.json()
print(f"Current weather in London: {weather_data['temperature']}°C, {weather_data['condition']}")
```

### MCP Protocol

```python
# MCP tool call in an LLM prompt
prompt = """
I'm planning a trip to Tokyo tomorrow. What's the weather forecast?
"""

# The LLM can use the get_weather_forecast_tool capability
```

## Step 10: Testing the Extension

Create unit tests for your extension to ensure it works correctly:

```python
# test_weather_extension.py
import pytest
import os
from openmas_weather.extension import WeatherServiceExtension
from openmas_weather.client import WeatherClient

@pytest.fixture
def mock_config():
    return {
        "enabled": True,
        "api": {
            "api_key_env": "TEST_WEATHER_API_KEY",
            "base_url": "https://api.example.com",
            "timeout": 5,
            "units": "metric",
            "cache_ttl": 10
        },
        "default_location": "Test City",
        "capabilities": ["current_weather", "forecast", "alerts"],
        "protocol_mapping": {}
    }

@pytest.fixture
def weather_client(mock_config):
    client = WeatherClient(mock_config["api"])
    client.mock_implementation()
    return client

@pytest.fixture
async def weather_extension(mock_config):
    # Set environment variable for mock mode
    os.environ["OPENMAS_EXTENSIONS_MOCK"] = "true"
    # Create extension
    extension = WeatherServiceExtension(mock_config)
    await extension.initialize()
    yield extension
    await extension.shutdown()

async def test_current_weather(weather_extension):
    result = await weather_extension.get_current_weather("Berlin")
    assert result["location"] == "Berlin"
    assert "temperature" in result
    assert "condition" in result
    
async def test_forecast(weather_extension):
    result = await weather_extension.get_forecast("Paris", days=3)
    assert result["location"] == "Paris"
    assert len(result["days"]) == 3
    
async def test_alerts(weather_extension):
    result = await weather_extension.get_alerts("Tokyo")
    assert result["location"] == "Tokyo"
    assert "alerts" in result
```

Run the tests:

```bash
pytest -xvs test_weather_extension.py
```

## Conclusion

You have successfully created a custom weather service extension for OpenMAS that:

1. Follows the Single Source of Truth principle with a clear configuration schema
2. Maintains Reasoning Agnosticism by working with any agent reasoning approach
3. Ensures Protocol Independence through protocol-specific mappings
4. Provides standardized capabilities with clear schemas
5. Includes proper error handling and validation

This extension demonstrates how OpenMAS extensions can provide new capabilities while adhering to the core architectural principles of the framework.

## Next Steps

1. Implement validation tests for different protocols
2. Add more complex weather data processing capabilities
3. Develop a richer agent example that combines the weather extension with other extensions
4. Publish your extension to PyPI for wider use

For more information on extension development, see the [Extension Development Guide](/05_extensions/development/README.md) and [Extension System Overview](/05_extensions/README.md).

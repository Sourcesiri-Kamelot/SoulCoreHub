"""
Weather tool for AirTrain.

This module provides a tool for fetching weather data.
For demonstration purposes, this returns mock data regardless of the location.
"""

import random
from typing import Dict, Any
from datetime import datetime
from loguru import logger

from .registry import StatelessTool, register_tool


@register_tool("weather")
class WeatherTool(StatelessTool):
    """Tool for retrieving weather information for a location."""

    def __init__(self):
        self.name = "weather"
        self.description = "Get current weather information for a location"
        self.parameters = {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City and country (e.g., 'New York, USA', 'Paris, France')",
                }
            },
            "required": ["location"],
            "additionalProperties": False,
        }

    def __call__(self, location: str) -> Dict[str, Any]:
        """
        Execute the weather tool to get mock weather data.

        Args:
            location: The city and country to get weather for

        Returns:
            A dictionary containing mock weather data
        """
        logger.info(f"Weather tool called with location: {location}")

        # For demonstration purposes, return mock data regardless of input
        temp_celsius = random.uniform(15.0, 30.0)
        temp_fahrenheit = (temp_celsius * 9 / 5) + 32

        conditions = random.choice(
            ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain", "Thunderstorms", "Clear"]
        )

        humidity = random.randint(30, 90)
        wind_speed = random.uniform(0, 20)

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        weather_data = {
            "status": "success",
            "location": location,
            "timestamp": current_time,
            "weather": {
                "temperature": {
                    "celsius": round(temp_celsius, 1),
                    "fahrenheit": round(temp_fahrenheit, 1),
                },
                "conditions": conditions,
                "humidity": humidity,
                "wind_speed": round(wind_speed, 1),
                "forecast": "This is mock data for demonstration purposes",
            },
        }

        logger.info(f"Returning mock weather data for {location}")
        return weather_data

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary format for LLM function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

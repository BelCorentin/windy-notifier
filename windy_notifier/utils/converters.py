#!/usr/bin/env python3
"""
Converter Utilities

This module provides utility functions for converting between different units
of measurement and parsing values from text.
"""

import re
import logging

# Configure module logger
logger = logging.getLogger(__name__)


def convert_to_knots(value, unit="mph"):
    """
    Convert wind speed from different units to knots.
    
    Args:
        value (float): The wind speed value
        unit (str): The unit of the wind speed (knots, km/h, mph, m/s)
        
    Returns:
        float: The wind speed in knots
    """
    unit = unit.lower()
    
    if unit in ["knots", "kts", "kt"]:
        return value
    elif unit in ["km/h", "kph"]:
        # 1 km/h = 0.539957 knots
        return value * 0.539957
    elif unit in ["mph"]:
        # 1 mph = 0.868976 knots
        return value * 0.868976
    elif unit in ["m/s"]:
        # 1 m/s = 1.94384 knots
        return value * 1.94384
    else:
        logger.warning(f"Unknown wind speed unit: {unit}, assuming knots")
        return value


def parse_wind_data(wind_text):
    """
    Parse wind data from text, handling different numeric formats and units.
    
    Args:
        wind_text (str): Text containing wind speed information
        
    Returns:
        tuple: (value in float, unit as string) or (None, None) if parsing fails
    """
    if not wind_text:
        return None, None
        
    # Extract numeric value and unit
    match = re.search(r'(\d+(?:[,.]\d+)?)\s*(mph|km/h|kts|knots)?', wind_text, re.IGNORECASE)
    if match:
        # Replace comma with period for proper float conversion
        value_str = match.group(1).replace(',', '.')
        value = float(value_str)
        unit = match.group(2).lower() if match.group(2) else "mph"  # Default to mph if no unit specified
        return value, unit
    else:
        logger.warning(f"Could not extract numeric wind speed from: {wind_text}")
        return None, None


def format_wind_speed(speed, unit="knots", precision=1):
    """
    Format wind speed with the specified unit and precision.
    
    Args:
        speed (float): Wind speed value
        unit (str): Unit to display
        precision (int): Number of decimal places
        
    Returns:
        str: Formatted wind speed string
    """
    if speed is None:
        return "N/A"
        
    format_str = f"{{:.{precision}f}} {unit}"
    return format_str.format(speed)


def get_wind_description(speed_knots):
    """
    Get a text description of wind conditions based on the Beaufort scale.
    
    Args:
        speed_knots (float): Wind speed in knots
        
    Returns:
        tuple: (beaufort_number, description)
    """
    # Beaufort scale (knots)
    beaufort_scale = [
        (0, 1, "Calm"),
        (1, 3, "Light air"),
        (4, 6, "Light breeze"),
        (7, 10, "Gentle breeze"),
        (11, 16, "Moderate breeze"),
        (17, 21, "Fresh breeze"),
        (22, 27, "Strong breeze"),
        (28, 33, "Near gale"),
        (34, 40, "Gale"),
        (41, 47, "Strong gale"),
        (48, 55, "Storm"),
        (56, 63, "Violent storm"),
        (64, float('inf'), "Hurricane force")
    ]
    
    if speed_knots is None:
        return 0, "Unknown"
        
    for i, (lower, upper, description) in enumerate(beaufort_scale):
        if lower <= speed_knots <= upper:
            return i, description
            
    return 12, "Hurricane force"  # Default for very high values 
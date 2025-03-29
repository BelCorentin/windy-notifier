#!/usr/bin/env python3
"""
Test Scraper Module

This module tests the extraction of wind data from the WeatherLink page.
It verifies that Selenium is configured correctly and can extract wind data.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from windy_notifier.scraper.weatherlink import get_weather_data
from windy_notifier.utils.converters import parse_wind_data, convert_to_knots, get_wind_description

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def test_wind_data_extraction():
    """
    Test the extraction of wind data from WeatherLink.
    
    Returns:
        bool: True if the test succeeds
    """
    print("\n===== Testing Wind Data Extraction =====")
    print("This will test if the Selenium scraper can extract wind data from WeatherLink.")
    
    # Create debug directory if it doesn't exist
    Path("debug").mkdir(exist_ok=True)
    
    try:
        # Get weather data
        print("Accessing WeatherLink page...")
        weather_data = get_weather_data()
        
        # Show all extracted data
        print("\nExtracted Weather Data:")
        for key, value in weather_data.items():
            print(f"  - {key}: {value}")
        
        # Process wind speed
        wind_speed = None
        if 'wind_speed' in weather_data:
            raw_value, unit = parse_wind_data(weather_data['wind_speed'])
            if raw_value is not None:
                wind_speed = convert_to_knots(raw_value, unit)
                print(f"\nWind Speed: {raw_value} {unit} ({wind_speed:.2f} knots)")
                
                # Get wind description
                beaufort_num, wind_desc = get_wind_description(wind_speed)
                print(f"Wind Conditions: {wind_desc} (Beaufort {beaufort_num})")
        else:
            print("\n❌ Failed to extract wind speed")
        
        # Process wind gust
        wind_gust = None
        if 'gust_speed' in weather_data:
            raw_value, unit = parse_wind_data(weather_data['gust_speed'])
            if raw_value is not None:
                wind_gust = convert_to_knots(raw_value, unit)
                print(f"Wind Gust: {raw_value} {unit} ({wind_gust:.2f} knots)")
        else:
            print("Note: No wind gust data found")
        
        # Show other data
        if 'wind_direction' in weather_data:
            print(f"Wind Direction: {weather_data['wind_direction']}")
        
        if 'temperature' in weather_data:
            print(f"Temperature: {weather_data['temperature']}")
        
        success = wind_speed is not None
        
        if success:
            print("\n✅ Successfully extracted wind data!")
        else:
            print("\n❌ Failed to extract wind data")
            print("Check debug/weatherlink_debug.png and debug/last_weatherlink_page.html for more information")
        
        return success
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        logger.exception("Error during scraper test")
        return False


def main():
    """Main function to run the scraper test."""
    success = test_wind_data_extraction()
    
    print("\n===== Troubleshooting Tips =====")
    print("If the test failed, check the following:")
    print("1. Make sure Google Chrome is installed")
    print("2. Verify your internet connection is working")
    print("3. Check if the WeatherLink page structure has changed")
    print("4. Look at debug files in the debug directory")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 
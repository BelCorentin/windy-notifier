#!/usr/bin/env python3
"""
Windy Notifier Main Module

This is the main entry point for the Windy Notifier application that 
monitors wind speed at Saint-Raphaël port and sends notifications when
the wind exceeds a specified threshold.
"""

import os
import time
import json
import logging
import traceback
from pathlib import Path
from datetime import datetime

import schedule
from dotenv import load_dotenv

from windy_notifier.scraper.weatherlink import get_weather_data
from windy_notifier.utils.converters import parse_wind_data, convert_to_knots, get_wind_description
from windy_notifier.notifiers.email_notifier import send_email_notification
from windy_notifier.notifiers.telegram_notifier import send_telegram_notification

# Load environment variables
load_dotenv()

# Create debug directory if it doesn't exist
Path("debug").mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug/windy_notifier.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("windy_notifier")

# Constants
WIND_THRESHOLD = int(os.getenv("WIND_THRESHOLD", "15"))  # Wind speed threshold in knots
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "30"))  # How often to check
NOTIFICATION_METHOD = os.getenv("NOTIFICATION_METHOD", "email").lower()  # email, telegram, or both


def get_wind_data():
    """
    Extract wind data from WeatherLink.
    
    Returns:
        tuple: (wind_speed, wind_gust) in knots, or (None, None) if not available
    """
    try:
        # Get weather data using the scraper module
        weather_data = get_weather_data()
        logger.info(f"Weather data: {weather_data}")
        
        # Extract wind speed
        wind_speed = None
        if 'wind_speed' in weather_data:
            # Parse wind speed
            raw_value, unit = parse_wind_data(weather_data['wind_speed'])
            if raw_value is not None:
                wind_speed = convert_to_knots(raw_value, unit)
                logger.info(f"Wind speed: {raw_value} {unit} ({wind_speed:.2f} knots)")
        
        # Extract wind gust
        wind_gust = None
        if 'gust_speed' in weather_data:
            # Parse gust speed
            raw_value, unit = parse_wind_data(weather_data['gust_speed'])
            if raw_value is not None:
                wind_gust = convert_to_knots(raw_value, unit)
                logger.info(f"Wind gust: {raw_value} {unit} ({wind_gust:.2f} knots)")
        
        return wind_speed, wind_gust
        
    except Exception as e:
        logger.error(f"Error getting wind data: {e}")
        logger.error(traceback.format_exc())
        return None, None


def send_notification(wind_speed, wind_gust=None):
    """
    Send a notification using the configured method(s).
    
    Args:
        wind_speed (float): Current wind speed in knots
        wind_gust (float, optional): Wind gust speed in knots
        
    Returns:
        bool: True if at least one notification method succeeded
    """
    threshold = WIND_THRESHOLD
    notification_sent = False
    
    if NOTIFICATION_METHOD == "telegram":
        # Only use Telegram
        logger.info("Using Telegram for notification")
        notification_sent = send_telegram_notification(wind_speed, wind_gust, threshold)
    
    elif NOTIFICATION_METHOD == "email":
        # Use the simple SMTP notifier
        try:
            # Import simple SMTP notifier
            from windy_notifier.notifiers.simple_smtp_notifier import send_simple_smtp_notification
            logger.info("Using simple SMTP notification")
            notification_sent = send_simple_smtp_notification(wind_speed, wind_gust, threshold)
        except ImportError:
            # Fall back to regular email if simple SMTP is not available
            logger.info("Simple SMTP notifier not available, using standard email notification")
            notification_sent = send_email_notification(wind_speed, wind_gust, threshold)
    
    elif NOTIFICATION_METHOD == "both":
        # Try both methods
        logger.info("Using both email and Telegram for notification")
        
        # Try simple SMTP first
        try:
            from windy_notifier.notifiers.simple_smtp_notifier import send_simple_smtp_notification
            email_success = send_simple_smtp_notification(wind_speed, wind_gust, threshold)
        except ImportError:
            # Fall back to regular email
            email_success = send_email_notification(wind_speed, wind_gust, threshold)
            
        telegram_success = send_telegram_notification(wind_speed, wind_gust, threshold)
        notification_sent = email_success or telegram_success
    
    else:
        # Default to email
        logger.warning(f"Unknown notification method: {NOTIFICATION_METHOD}, defaulting to email")
        notification_sent = send_email_notification(wind_speed, wind_gust, threshold)
    
    return notification_sent


def check_wind():
    """Check wind speed and send notification if it exceeds the threshold."""
    try:
        logger.info("Checking wind speed...")
        wind_speed, wind_gust = get_wind_data()
        
        if wind_speed is not None:
            # Get wind description
            beaufort_num, wind_desc = get_wind_description(wind_speed)
            logger.info(f"Wind conditions: {wind_desc} (Beaufort {beaufort_num})")
            
            if wind_speed >= WIND_THRESHOLD:
                logger.info(f"Wind speed ({wind_speed:.1f} knots) exceeds threshold ({WIND_THRESHOLD} knots)")
                send_notification(wind_speed, wind_gust)
            else:
                logger.info(f"Wind speed ({wind_speed:.1f} knots) is below threshold ({WIND_THRESHOLD} knots)")
                
            # Save the last check result
            save_last_check(wind_speed, wind_gust)
        else:
            logger.warning("Could not determine wind speed during this check")
            
    except Exception as e:
        logger.error(f"Error during wind check: {e}")
        logger.error(traceback.format_exc())


def save_last_check(wind_speed, wind_gust=None):
    """
    Save the result of the last check to a file.
    
    Args:
        wind_speed (float): The wind speed in knots
        wind_gust (float, optional): The wind gust speed in knots
    """
    try:
        beaufort_num, wind_desc = get_wind_description(wind_speed)
        
        data = {
            "timestamp": time.time(),
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "wind_speed": wind_speed,
            "wind_gust": wind_gust,
            "wind_description": wind_desc,
            "beaufort_scale": beaufort_num,
            "threshold": WIND_THRESHOLD,
            "above_threshold": wind_speed >= WIND_THRESHOLD
        }
        
        with open("debug/last_check.json", "w") as f:
            json.dump(data, f, indent=2)
            
        logger.debug("Saved last check data")
    except Exception as e:
        logger.error(f"Error saving last check data: {e}")


def run():
    """Run the wind checking schedule."""
    logger.info("Starting Windy Notifier")
    logger.info(f"Will check for winds exceeding {WIND_THRESHOLD} knots every {CHECK_INTERVAL_MINUTES} minutes")
    logger.info(f"Notification method: {NOTIFICATION_METHOD}")
    
    # Run once at startup
    check_wind()
    
    # Schedule regular checks
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(check_wind)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Windy Notifier stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    run() 
#!/usr/bin/env python3
"""
Telegram Notifier for Windy Notifier

This module provides Telegram notification functionality for wind alerts,
including enhanced formatting and wind gust information.
"""

import os
import logging
import requests
from ..utils.converters import get_wind_description, format_wind_speed

# Configure module logger
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram notification handler for wind alerts."""
    
    def __init__(self, config=None):
        """
        Initialize the Telegram notifier with configuration.
        
        Args:
            config (dict, optional): Configuration dictionary. If None, loads from env vars.
        """
        self.config = config or {}
        
        # Load config from environment variables if not provided
        self.bot_token = self.config.get('bot_token', os.getenv("TELEGRAM_BOT_TOKEN"))
        
        # Handle multiple chat IDs
        chat_id_str = self.config.get('chat_id', os.getenv("TELEGRAM_CHAT_ID", ""))
        self.chat_ids = []
        
        # Parse chat IDs (comma-separated list)
        if chat_id_str:
            self.chat_ids = [cid.strip() for cid in chat_id_str.split(',') if cid.strip()]
            
        # Website URL for reference in notifications
        self.website_url = self.config.get(
            'website_url', 
            os.getenv("PORT_WEBSITE_URL", 
                      "https://www.ville-saintraphael.fr/utile/la-regie-des-ports-raphaelois")
        )
        
        # Check if configuration is valid
        self.is_configured = bool(self.bot_token and self.chat_ids)
    
    def is_valid(self):
        """Check if the Telegram configuration is valid."""
        return self.is_configured
    
    def create_message(self, wind_speed, wind_gust=None, threshold=15, location="Saint-Raphaël port"):
        """
        Create a Markdown-formatted message for Telegram.
        
        Args:
            wind_speed (float): Current wind speed in knots
            wind_gust (float, optional): Wind gust speed in knots
            threshold (int): Wind speed threshold that triggered the notification
            location (str): Name of the location being monitored
            
        Returns:
            str: Markdown-formatted message
        """
        # Get wind description
        beaufort_num, wind_desc = get_wind_description(wind_speed)
        
        # Format wind speeds
        wind_formatted = format_wind_speed(wind_speed)
        gust_formatted = format_wind_speed(wind_gust) if wind_gust else "N/A"
        
        # Create emoji based on Beaufort scale
        wind_emoji = "🌬️"
        if beaufort_num <= 3:
            wind_emoji = "🌬️"  # Light air/breeze
        elif beaufort_num <= 5:
            wind_emoji = "💨"   # Moderate to fresh breeze
        elif beaufort_num <= 7:
            wind_emoji = "🌪️"  # Strong breeze to near gale
        else:
            wind_emoji = "⚠️🌪️" # Gale or stronger
        
        message = f"""{wind_emoji} *High Wind Alert* {wind_emoji}

*Location:* {location}

*Current Wind Speed:* {wind_formatted}
*Wind Conditions:* {wind_desc}
*Wind Gusts:* {gust_formatted}
*Alert Threshold:* {threshold} knots

Click [here]({self.website_url}) to check the port website.

_Sent by Windy Notifier_"""
        
        return message
    
    def send_notification(self, wind_speed, wind_gust=None, threshold=15, location="Saint-Raphaël port"):
        """
        Send a Telegram notification about high wind speed.
        
        Args:
            wind_speed (float): The current wind speed in knots
            wind_gust (float, optional): Wind gust speed in knots
            threshold (int): The threshold value that triggered the alert
            location (str): Name of the location being monitored
        
        Returns:
            bool: True if notification was sent successfully to all recipients, False otherwise
        """
        if not self.is_configured:
            logger.error("Telegram configuration is incomplete (missing bot token or chat ID)")
            return False
        
        message = self.create_message(wind_speed, wind_gust, threshold, location)
        
        success = True
        for chat_id in self.chat_ids:
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False
                }
                
                response = requests.post(url, data=payload, timeout=10)
                response.raise_for_status()
                
                result = response.json()
                if result.get("ok"):
                    logger.info(f"Telegram notification sent successfully to chat ID {chat_id}")
                else:
                    logger.error(f"Failed to send Telegram notification: {result.get('description')}")
                    success = False
                    
            except Exception as e:
                logger.error(f"Error sending Telegram notification to {chat_id}: {e}")
                success = False
                
        return success


def send_telegram_notification(wind_speed, wind_gust=None, threshold=15, config=None):
    """
    Convenience function to send a Telegram notification.
    
    Args:
        wind_speed (float): Wind speed in knots
        wind_gust (float, optional): Wind gust speed in knots
        threshold (int): Threshold that triggered the notification
        config (dict, optional): Telegram configuration
        
    Returns:
        bool: Success status
    """
    notifier = TelegramNotifier(config)
    if notifier.is_valid():
        return notifier.send_notification(wind_speed, wind_gust, threshold)
    return False


def setup_telegram():
    """
    Interactive setup guide for Telegram notifications.
    
    Returns:
        bool: True if setup was successful
    """
    print("""
=== Telegram Bot Setup Guide ===

To use Telegram notifications with Windy Notifier:

1. Talk to BotFather on Telegram (@BotFather) to create a new bot:
   - Send /newbot to BotFather
   - Choose a name for your bot
   - Choose a username ending with 'bot'
   - BotFather will give you an API token - save this for step 4

2. Start a conversation with your new bot:
   - Search for your bot by username
   - Start a conversation by clicking Start

3. Get your chat ID:
   - Talk to @userinfobot on Telegram
   - It will reply with your chat ID

4. Add these values to your .env file:
   TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
   TELEGRAM_CHAT_ID=your_chat_id_from_userinfobot

5. You can also specify multiple chat IDs separated by commas:
   TELEGRAM_CHAT_ID=id1,id2,id3

6. Now the Windy Notifier will be able to send you Telegram notifications!
""")
    
    # Check if current configuration is valid
    notifier = TelegramNotifier()
    if notifier.is_valid():
        print("✅ Current Telegram configuration appears to be valid.")
        print(f"Bot token: {'*' * (len(notifier.bot_token) - 4)}{notifier.bot_token[-4:]}")
        print(f"Chat IDs: {', '.join(notifier.chat_ids)}")
        return True
    else:
        print("❌ Current Telegram configuration is incomplete or invalid.")
        return False


def test_telegram_notification():
    """
    Test the Telegram notification functionality with a test message.
    
    Returns:
        bool: True if test was successful
    """
    print("Testing Telegram notification...")
    
    notifier = TelegramNotifier()
    if not notifier.is_valid():
        print("❌ Telegram configuration is incomplete")
        print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in your .env file")
        setup_telegram()
        return False
    
    print(f"Sending test notifications to {len(notifier.chat_ids)} chat ID(s)...")
    
    test_wind = 18.5
    test_gust = 24.2
    threshold = 15
    
    print(f"Test data: wind speed: {test_wind} knots, gust: {test_gust} knots")
    result = notifier.send_notification(test_wind, test_gust, threshold)
    
    if result:
        print("✅ Test notification sent successfully!")
    else:
        print("❌ Failed to send test notification")
    
    return result


if __name__ == "__main__":
    # Set up logging when run directly
    logging.basicConfig(level=logging.INFO, 
                      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run setup and test
    setup_telegram()
    
    print("\nWould you like to send a test notification to verify your setup?")
    answer = input("Enter 'y' to send a test or any other key to exit: ")
    
    if answer.lower() == 'y':
        test_telegram_notification() 
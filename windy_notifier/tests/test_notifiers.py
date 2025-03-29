#!/usr/bin/env python3
"""
Test Notifiers Module

This module provides test functions for the notification system.
It can be used to test email, Telegram, or both notification methods.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from windy_notifier.notifiers.email_notifier import EmailNotifier
from windy_notifier.notifiers.telegram_notifier import TelegramNotifier
from windy_notifier.utils.converters import get_wind_description

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def test_email_notification(wind_speed=18.5, wind_gust=25.3, html=True):
    """
    Test email notification functionality.
    
    Args:
        wind_speed (float): Test wind speed in knots
        wind_gust (float): Test wind gust speed in knots
        html (bool): Whether to send HTML-formatted email
        
    Returns:
        bool: True if the test succeeds
    """
    print("\n===== Testing Email Notification =====")
    
    # Create an email notifier
    notifier = EmailNotifier()
    
    # Validate configuration
    if not notifier.is_valid():
        print("❌ Email configuration is incomplete")
        print("Please check the following environment variables:")
        print("  - SMTP_SERVER")
        print("  - SMTP_PORT")
        print("  - SMTP_USERNAME")
        print("  - SMTP_PASSWORD")
        print("  - SENDER_EMAIL")
        print("  - RECIPIENT_EMAIL (can be comma-separated for multiple recipients)")
        return False
    
    # Show configuration details
    print(f"SMTP Server: {notifier.smtp_server}")
    print(f"SMTP Port: {notifier.smtp_port}")
    print(f"Sender: {notifier.sender_email}")
    recipient_list = ", ".join(notifier.recipients)
    print(f"Recipients: {recipient_list}")
    
    # Get wind description
    _, wind_desc = get_wind_description(wind_speed)
    
    # Send test notification
    print(f"\nSending test email notification:")
    print(f"  - Wind Speed: {wind_speed} knots ({wind_desc})")
    print(f"  - Wind Gust: {wind_gust} knots")
    print(f"  - Format: {'HTML' if html else 'Plain text'}")
    
    # Send notification
    result = notifier.send_notification(
        wind_speed=wind_speed,
        wind_gust=wind_gust,
        threshold=15,
        location="Saint-Raphaël port",
        html=html
    )
    
    if result:
        print("✅ Test email sent successfully!")
    else:
        print("❌ Failed to send test email")
    
    return result


def test_telegram_notification(wind_speed=18.5, wind_gust=25.3):
    """
    Test Telegram notification functionality.
    
    Args:
        wind_speed (float): Test wind speed in knots
        wind_gust (float): Test wind gust speed in knots
        
    Returns:
        bool: True if the test succeeds
    """
    print("\n===== Testing Telegram Notification =====")
    
    # Create a Telegram notifier
    notifier = TelegramNotifier()
    
    # Validate configuration
    if not notifier.is_valid():
        print("❌ Telegram configuration is incomplete")
        print("Please check the following environment variables:")
        print("  - TELEGRAM_BOT_TOKEN")
        print("  - TELEGRAM_CHAT_ID (can be comma-separated for multiple chat IDs)")
        return False
    
    # Show configuration details
    print(f"Bot Token: {'*' * (len(notifier.bot_token) - 4)}{notifier.bot_token[-4:]}")
    chat_id_list = ", ".join(notifier.chat_ids)
    print(f"Chat IDs: {chat_id_list}")
    
    # Get wind description
    beaufort_num, wind_desc = get_wind_description(wind_speed)
    
    # Send test notification
    print(f"\nSending test Telegram notification:")
    print(f"  - Wind Speed: {wind_speed} knots ({wind_desc})")
    print(f"  - Wind Gust: {wind_gust} knots")
    print(f"  - Beaufort Scale: {beaufort_num}")
    
    # Send notification
    result = notifier.send_notification(
        wind_speed=wind_speed,
        wind_gust=wind_gust,
        threshold=15,
        location="Saint-Raphaël port"
    )
    
    if result:
        print("✅ Test message sent successfully!")
    else:
        print("❌ Failed to send test message")
    
    return result


def main():
    """Main function to run notification tests based on command line arguments."""
    parser = argparse.ArgumentParser(description='Test Windy Notifier notification system.')
    parser.add_argument('--method', choices=['email', 'telegram', 'both'], default='both',
                      help='Notification method to test')
    parser.add_argument('--wind-speed', type=float, default=18.5,
                      help='Wind speed in knots for test notification')
    parser.add_argument('--wind-gust', type=float, default=25.3,
                      help='Wind gust in knots for test notification')
    parser.add_argument('--plain-text', action='store_true',
                      help='Use plain text email instead of HTML (email only)')
    
    args = parser.parse_args()
    success = True
    
    # Test selected method(s)
    if args.method in ['email', 'both']:
        email_success = test_email_notification(
            wind_speed=args.wind_speed,
            wind_gust=args.wind_gust,
            html=not args.plain_text
        )
        success = success and email_success
    
    if args.method in ['telegram', 'both']:
        telegram_success = test_telegram_notification(
            wind_speed=args.wind_speed,
            wind_gust=args.wind_gust
        )
        success = success and telegram_success
    
    # Print summary
    print("\n===== Test Summary =====")
    if success:
        print("✅ All tests passed successfully!")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main()) 
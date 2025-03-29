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
try:
    from windy_notifier.notifiers.simple_smtp_notifier import SimpleSmtpNotifier
    simple_smtp_available = True
except ImportError:
    simple_smtp_available = False
    
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


def test_email_notification(wind_speed=18.5, wind_gust=25.3, html=True, use_simple=True):
    """
    Test email notification functionality.
    
    Args:
        wind_speed (float): Test wind speed in knots
        wind_gust (float): Test wind gust speed in knots
        html (bool): Whether to send HTML-formatted email
        use_simple (bool): Whether to use the simple SMTP notifier
        
    Returns:
        bool: True if the test succeeds
    """
    print("\n===== Testing Email Notification =====")
    
    # Choose which notifier to use
    if use_simple and simple_smtp_available:
        print("Using Simple SMTP Notifier (standard library only)")
        notifier = SimpleSmtpNotifier()
    else:
        print("Using Standard Email Notifier")
        notifier = EmailNotifier()
    
    # Validate configuration
    if not notifier.is_valid():
        print("❌ Email configuration is incomplete")
        print("Please check your .env file for the following settings:")
        
        if use_simple and simple_smtp_available:
            print("  - SMTP_SERVER")
            print("  - SMTP_PORT")
            print("  - SMTP_USERNAME")
            print("  - SMTP_PASSWORD")
            print("  - RECIPIENT_EMAIL (can be comma-separated for multiple recipients)")
        else:
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
        print("\nFor Gmail users:")
        print("1. Make sure you're using an App Password if 2FA is enabled")
        print("2. Check for security alerts in your Gmail account")
        print("3. Enable 'Less secure app access' if not using 2FA")
    
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
    parser.add_argument('--simple', action='store_true', default=True,
                      help='Use the simple SMTP implementation (default: True)')
    parser.add_argument('--standard', action='store_true',
                      help='Use the standard email implementation instead of simple SMTP')
    
    args = parser.parse_args()
    success = True
    
    # Determine whether to use simple SMTP (defaults to True unless --standard is specified)
    use_simple = args.simple and not args.standard
    
    # Test selected method(s)
    if args.method in ['email', 'both']:
        print(f"Testing {'simple SMTP' if use_simple else 'standard email'} notification")
        email_success = test_email_notification(
            wind_speed=args.wind_speed,
            wind_gust=args.wind_gust,
            html=not args.plain_text,
            use_simple=use_simple
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
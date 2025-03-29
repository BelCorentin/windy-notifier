#!/usr/bin/env python3
"""
Email Notifier Module

This module provides functionality to send wind notifications via email,
supporting both plain text and HTML formatting.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..utils.converters import get_wind_description, format_wind_speed

# Configure module logger
logger = logging.getLogger(__name__)


class EmailNotifier:
    """Email notification handler for wind alerts."""
    
    def __init__(self, config=None):
        """
        Initialize the email notifier with configuration.
        
        Args:
            config (dict, optional): Configuration dictionary. If None, loads from env vars.
        """
        self.config = config or {}
        
        # Load config from environment variables if not provided
        self.smtp_server = self.config.get('smtp_server', os.getenv("SMTP_SERVER"))
        self.smtp_port = int(self.config.get('smtp_port', os.getenv("SMTP_PORT", "587")))
        self.smtp_username = self.config.get('smtp_username', os.getenv("SMTP_USERNAME"))
        self.smtp_password = self.config.get('smtp_password', os.getenv("SMTP_PASSWORD"))
        self.sender_email = self.config.get('sender_email', os.getenv("SENDER_EMAIL"))
        
        # Default recipient or list from environment
        default_recipient = os.getenv("RECIPIENT_EMAIL", "")
        self.recipients = self.config.get('recipients', 
                                          [r.strip() for r in default_recipient.split(',')])
        
        # Make sure recipients is always a list
        if isinstance(self.recipients, str):
            self.recipients = [self.recipients]
            
        # Website URL for reference in notifications
        self.website_url = self.config.get(
            'website_url', 
            os.getenv("PORT_WEBSITE_URL", 
                      "https://www.ville-saintraphael.fr/utile/la-regie-des-ports-raphaelois")
        )
        
        # Check if configuration is valid
        self.is_configured = all([
            self.smtp_server, 
            self.smtp_username, 
            self.smtp_password, 
            self.sender_email, 
            self.recipients
        ])
    
    def is_valid(self):
        """Check if the email configuration is valid."""
        return self.is_configured
    
    def create_html_message(self, wind_speed, wind_gust=None, threshold=15, location="Saint-Raphaël port"):
        """
        Create an HTML-formatted email message about wind conditions.
        
        Args:
            wind_speed (float): Current wind speed in knots
            wind_gust (float, optional): Wind gust speed in knots
            threshold (int): Wind speed threshold that triggered the notification
            location (str): Name of the location being monitored
            
        Returns:
            str: HTML-formatted message
        """
        # Get wind description
        _, wind_desc = get_wind_description(wind_speed)
        
        # Format wind speeds
        wind_formatted = format_wind_speed(wind_speed)
        gust_formatted = format_wind_speed(wind_gust) if wind_gust else "N/A"
        
        # HTML message with styled content
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                h1 {{
                    color: #e74c3c;
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                }}
                .data-row {{
                    display: flex;
                    margin-bottom: 10px;
                }}
                .label {{
                    font-weight: bold;
                    width: 180px;
                }}
                .highlight {{
                    color: #e74c3c;
                    font-weight: bold;
                }}
                .footer {{
                    margin-top: 30px;
                    font-size: 0.8em;
                    color: #777;
                    border-top: 1px solid #eee;
                    padding-top: 10px;
                }}
                .button {{
                    display: inline-block;
                    background-color: #3498db;
                    color: white;
                    padding: 10px 15px;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-top: 15px;
                }}
                .button:hover {{
                    background-color: #2980b9;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🌬️ High Wind Alert 🌬️</h1>
                <p>High wind conditions have been detected at <strong>{location}</strong>!</p>
                
                <div class="data-row">
                    <div class="label">Current wind speed:</div>
                    <div class="value highlight">{wind_formatted}</div>
                </div>
                
                <div class="data-row">
                    <div class="label">Wind conditions:</div>
                    <div class="value">{wind_desc}</div>
                </div>
                
                <div class="data-row">
                    <div class="label">Wind gusts:</div>
                    <div class="value">{gust_formatted}</div>
                </div>
                
                <div class="data-row">
                    <div class="label">Alert threshold:</div>
                    <div class="value">{threshold} knots</div>
                </div>
                
                <p>
                    <a href="{self.website_url}" class="button">View Port Website</a>
                </p>
                
                <div class="footer">
                    This is an automated message from Windy Notifier.<br>
                    Time: {os.popen('date').read().strip()}
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def create_text_message(self, wind_speed, wind_gust=None, threshold=15, location="Saint-Raphaël port"):
        """
        Create a plain text email message about wind conditions.
        
        Args:
            wind_speed (float): Current wind speed in knots
            wind_gust (float, optional): Wind gust speed in knots
            threshold (int): Wind speed threshold that triggered the notification
            location (str): Name of the location being monitored
            
        Returns:
            str: Plain text message
        """
        # Get wind description
        _, wind_desc = get_wind_description(wind_speed)
        
        # Format wind speeds
        wind_formatted = format_wind_speed(wind_speed)
        gust_formatted = format_wind_speed(wind_gust) if wind_gust else "N/A"
        
        text = f"""
        🌬️ High Wind Alert 🌬️
        
        High wind conditions have been detected at {location}!
        
        Current wind speed: {wind_formatted}
        Wind conditions: {wind_desc}
        Wind gusts: {gust_formatted}
        Alert threshold: {threshold} knots
        
        Check the website for more details: {self.website_url}
        
        This is an automated message from Windy Notifier.
        Time: {os.popen('date').read().strip()}
        """
        return text
    
    def send_notification(self, wind_speed, wind_gust=None, threshold=15, location="Saint-Raphaël port", html=True):
        """
        Send an email notification about high wind speed.
        
        Args:
            wind_speed (float): The current wind speed in knots
            wind_gust (float, optional): Wind gust speed in knots
            threshold (int): The threshold value that triggered the alert
            location (str): Name of the location being monitored
            html (bool): Whether to send HTML-formatted email
        
        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        if not self.is_configured:
            logger.error("Email configuration is incomplete, notification not sent")
            logger.error(f"SMTP Server: {self.smtp_server}")
            logger.error(f"SMTP Port: {self.smtp_port}")
            logger.error(f"SMTP Username: {'✓ Set' if self.smtp_username else '✗ Missing'}")
            logger.error(f"SMTP Password: {'✓ Set' if self.smtp_password else '✗ Missing'}")
            logger.error(f"Sender Email: {self.sender_email}")
            logger.error(f"Recipients: {', '.join(self.recipients) if self.recipients else '✗ Missing'}")
            return False
        
        subject = f"High Wind Alert: {format_wind_speed(wind_speed)}"
        
        # Create a multipart message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.sender_email
        
        # Always add a plain text version
        text_content = self.create_text_message(wind_speed, wind_gust, threshold, location)
        message.attach(MIMEText(text_content, "plain"))
        
        # Add HTML version if requested
        if html:
            html_content = self.create_html_message(wind_speed, wind_gust, threshold, location)
            message.attach(MIMEText(html_content, "html"))
        
        success = True
        try:
            logger.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                logger.info("Connected to SMTP server, starting TLS...")
                server.starttls()
                logger.info(f"TLS started, attempting to login with username: {self.smtp_username}...")
                server.login(self.smtp_username, self.smtp_password)
                logger.info("Login successful!")
                
                # Send to all recipients
                for recipient in self.recipients:
                    try:
                        logger.info(f"Sending email to {recipient}...")
                        message["To"] = recipient
                        server.sendmail(self.sender_email, recipient, message.as_string())
                        logger.info(f"Email notification sent to {recipient}")
                    except Exception as e:
                        logger.error(f"Failed to send email notification to {recipient}: {e}")
                        success = False
            
            return success
        
        except Exception as e:
            logger.error(f"Failed to send email notifications: {e}")
            if "authentication" in str(e).lower():
                logger.error("This appears to be an authentication issue. Please check your SMTP username and password.")
                logger.error("For Gmail, make sure you're using an App Password if 2FA is enabled.")
                logger.error("For ProtonMail, ensure you're using the Bridge password and Bridge is running.")
            return False


def send_email_notification(wind_speed, wind_gust=None, threshold=15, config=None):
    """
    Convenience function to send an email notification.
    
    Args:
        wind_speed (float): Wind speed in knots
        wind_gust (float, optional): Wind gust speed in knots
        threshold (int): Threshold that triggered the notification
        config (dict, optional): Email configuration
        
    Returns:
        bool: Success status
    """
    notifier = EmailNotifier(config)
    if notifier.is_valid():
        return notifier.send_notification(wind_speed, wind_gust, threshold)
    return False


# Simple test function for this module
def test_email_notification():
    """Test the email notification functionality."""
    print("Testing email notification...")
    
    notifier = EmailNotifier()
    if not notifier.is_valid():
        print("❌ Email configuration is incomplete")
        print("Please check your .env file for email settings:")
        print(f"  - SMTP_SERVER: {notifier.smtp_server or 'Not set'}")
        print(f"  - SMTP_PORT: {notifier.smtp_port}")
        print(f"  - SMTP_USERNAME: {'Set' if notifier.smtp_username else 'Not set'}")
        print(f"  - SMTP_PASSWORD: {'Set' if notifier.smtp_password else 'Not set'}")
        print(f"  - SENDER_EMAIL: {notifier.sender_email or 'Not set'}")
        print(f"  - RECIPIENT_EMAIL: {', '.join(notifier.recipients) if notifier.recipients else 'Not set'}")
        
        print("\nCommon email issues:")
        print("1. For Gmail:")
        print("   - You need to use an App Password if 2FA is enabled")
        print("   - Enable 'Less secure app access' for older apps")
        print("2. For ProtonMail:")
        print("   - You need to use Bridge and the Bridge password")
        print("   - Make sure Bridge is running")
        print("3. For all providers:")
        print("   - Check for typos in email addresses")
        print("   - Ensure the SMTP port is allowed in your firewall")
        
        return False
    
    test_wind = 18.5
    test_gust = 24.2
    threshold = 15
    
    print(f"Sending test email for wind speed: {test_wind} knots, gust: {test_gust} knots")
    print(f"Using SMTP server: {notifier.smtp_server}:{notifier.smtp_port}")
    print(f"Sender email: {notifier.sender_email}")
    print(f"Recipients: {', '.join(notifier.recipients)}")
    
    result = notifier.send_notification(test_wind, test_gust, threshold)
    
    if result:
        print("✅ Test email sent successfully!")
    else:
        print("❌ Failed to send test email")
        print("\nTroubleshooting steps:")
        print("1. Check your email provider's security settings")
        print("2. Try using a different email provider (Gmail, Outlook, etc.)")
        print("3. Verify that your .env file has the correct credentials")
        print("4. Look at the logs above for specific error messages")
    
    return result


if __name__ == "__main__":
    # Set up logging when run directly
    logging.basicConfig(level=logging.INFO, 
                      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run test
    test_email_notification() 
#!/usr/bin/env python3
"""
Simple SMTP Email Notifier

This module provides a simpler approach to sending email notifications using only
the standard smtplib library without any third-party dependencies.
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from ..utils.converters import get_wind_description, format_wind_speed

# Configure module logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class SimpleSmtpNotifier:
    """Simple email notification handler using standard smtplib."""
    
    def __init__(self, config=None):
        """
        Initialize the simple SMTP notifier with configuration.
        
        Args:
            config (dict, optional): Configuration dictionary. If None, loads from env vars.
        """
        self.config = config or {}
        
        # Load config from environment variables if not provided
        self.smtp_server = self.config.get('smtp_server', os.getenv("SMTP_SERVER", "smtp.gmail.com"))
        self.smtp_port = int(self.config.get('smtp_port', os.getenv("SMTP_PORT", "587")))
        self.smtp_username = self.config.get('smtp_username', os.getenv("SMTP_USERNAME"))
        self.smtp_password = self.config.get('smtp_password', os.getenv("SMTP_PASSWORD"))
        self.sender_email = self.config.get('sender_email', os.getenv("SENDER_EMAIL"))
        
        # If sender email is not set, use username
        if not self.sender_email and self.smtp_username:
            self.sender_email = self.smtp_username
            
        # Default recipient or list from environment
        default_recipient = os.getenv("RECIPIENT_EMAIL", "")
        self.recipients = self.config.get('recipients', 
                                        [r.strip() for r in default_recipient.split(',')] if default_recipient else [])
        
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
        Create HTML-formatted message content.
        
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
        
        # Simple HTML message - no complex CSS that might be stripped by email clients
        html = f"""
        <html>
        <body>
            <h1>High Wind Alert!</h1>
            <p>High wind conditions have been detected at <strong>{location}</strong>!</p>
            
            <p><strong>Current wind speed:</strong> {wind_formatted}</p>
            <p><strong>Wind conditions:</strong> {wind_desc}</p>
            <p><strong>Wind gusts:</strong> {gust_formatted}</p>
            <p><strong>Alert threshold:</strong> {threshold} knots</p>
            
            <p><a href="{self.website_url}">View Port Website</a></p>
            
            <p style="color: #777; font-size: 0.8em;">
                This is an automated message from Windy Notifier.<br>
                Time: {os.popen('date').read().strip()}
            </p>
        </body>
        </html>
        """
        return html
    
    def create_text_message(self, wind_speed, wind_gust=None, threshold=15, location="Saint-Raphaël port"):
        """
        Create a plain text message about wind conditions.
        
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
        High Wind Alert!
        
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
        Send an email notification about high wind speed using standard smtplib.
        
        Args:
            wind_speed (float): The current wind speed in knots
            wind_gust (float, optional): Wind gust speed in knots
            threshold (int): The threshold value that triggered the alert
            location (str): Name of the location being monitored
            html (bool): Whether to include HTML content
        
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
        
        # Create subject
        subject = f"High Wind Alert: {format_wind_speed(wind_speed)}"
        
        # Create a multipart message for both text and HTML (if requested)
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.sender_email
        
        # Always add text content first (as fallback)
        text_content = self.create_text_message(wind_speed, wind_gust, threshold, location)
        message.attach(MIMEText(text_content, "plain"))
        
        # Add HTML content if requested
        if html:
            html_content = self.create_html_message(wind_speed, wind_gust, threshold, location)
            message.attach(MIMEText(html_content, "html"))
        
        success = True
        try:
            logger.info(f"Connecting to SMTP server {self.smtp_server}:{self.smtp_port}...")
            
            # Create SMTP connection
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                logger.info("Connected to SMTP server, starting TLS...")
                server.starttls()  # Secure the connection
                
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
            logger.error(f"Failed to send email notification: {e}")
            if "authentication" in str(e).lower():
                logger.error("This appears to be an authentication issue.")
                logger.error("Make sure your username and password are correct.")
                logger.error("For Gmail with 2FA, you need to use an App Password.")
            elif "ssl" in str(e).lower() or "tls" in str(e).lower():
                logger.error("This appears to be an SSL/TLS issue.")
                logger.error(f"Make sure your SMTP port ({self.smtp_port}) is correct.")
            return False


def send_simple_smtp_notification(wind_speed, wind_gust=None, threshold=15, config=None):
    """
    Convenience function to send an email notification using standard smtplib.
    
    Args:
        wind_speed (float): Wind speed in knots
        wind_gust (float, optional): Wind gust speed in knots
        threshold (int): Threshold that triggered the notification
        config (dict, optional): Email configuration
        
    Returns:
        bool: Success status
    """
    notifier = SimpleSmtpNotifier(config)
    if notifier.is_valid():
        return notifier.send_notification(wind_speed, wind_gust, threshold)
    return False


# Simple test function for this module
def test_simple_smtp_notification():
    """Test the simple SMTP notification functionality."""
    print("Testing simple SMTP notification...")
    
    notifier = SimpleSmtpNotifier()
    if not notifier.is_valid():
        print("❌ Email configuration is incomplete")
        print("Please check your .env file for email settings:")
        print(f"  - SMTP_SERVER: {notifier.smtp_server}")
        print(f"  - SMTP_PORT: {notifier.smtp_port}")
        print(f"  - SMTP_USERNAME: {'Set' if notifier.smtp_username else 'Not set'}")
        print(f"  - SMTP_PASSWORD: {'Set' if notifier.smtp_password else 'Not set'}")
        print(f"  - SENDER_EMAIL: {notifier.sender_email or 'Not set (will use username if available)'}")
        print(f"  - RECIPIENT_EMAIL: {', '.join(notifier.recipients) if notifier.recipients else 'Not set'}")
        
        print("\nMinimum required setup in .env:")
        print("SMTP_USERNAME=your_email@example.com")
        print("SMTP_PASSWORD=your_email_password")
        print("RECIPIENT_EMAIL=destination@example.com")
        
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
        print("\nFor Gmail users:")
        print("1. Make sure you're using an App Password if 2FA is enabled")
        print("2. Check for security alerts in your Gmail account")
        print("3. Enable 'Less secure app access' if not using 2FA")
        print("4. Visit https://accounts.google.com/DisplayUnlockCaptcha if needed")
    
    return result


if __name__ == "__main__":
    # Set up logging when run directly
    logging.basicConfig(level=logging.INFO, 
                      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run test
    test_simple_smtp_notification() 
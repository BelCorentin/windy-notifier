# Standard SMTP Email Guide

## Overview

This guide explains how to set up email notifications in Windy Notifier using the standard `smtplib` library.

We've simplified the email notification system to use only Python's built-in libraries, which means:
- No third-party dependencies required
- Simpler installation and maintenance
- Standard SMTP protocol supported by all email providers

## Setting Up Email Notifications

### 1. Configure Your .env File

Add these settings to your `.env` file:

```
# For Gmail:
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient@example.com
```

### 2. For Gmail with 2FA (Recommended)

If you have 2-Factor Authentication enabled on your Gmail account (recommended), you need to generate an App Password:

1. Go to your Google Account: https://myaccount.google.com/
2. Go to Security → App passwords
3. At the bottom, select "Mail" and "Other (Custom name)"
4. Enter "Windy Notifier" as the name
5. Click "Generate"
6. Use the 16-character password that appears in your .env file
7. Click "Done"

### 3. For Gmail without 2FA

If you're not using 2FA (not recommended), you'll need to:

1. Go to https://myaccount.google.com/security
2. Scroll down to "Less secure app access"
3. Turn on "Allow less secure apps"

### 4. For Other Email Providers

For other email providers, you'll need:

1. SMTP server address (e.g., smtp.example.com)
2. SMTP port (usually 587 for TLS or 465 for SSL)
3. Your email username
4. Your email password
5. Recipient email address(es)

For example, for Outlook/Hotmail:
```
SMTP_SERVER=smtp.office365.com
SMTP_PORT=587
SMTP_USERNAME=your_email@outlook.com
SMTP_PASSWORD=your_password
RECIPIENT_EMAIL=recipient@example.com
```

### 5. Testing Your Configuration

Run the simple SMTP notifier test:

```bash
python -m windy_notifier.notifiers.simple_smtp_notifier
```

Or use the test module:

```bash
python -m windy_notifier.tests.test_notifiers --method email
```

## Troubleshooting

### Authentication Issues

1. **Incorrect Password**: Double-check that your password is correct.
2. **Using Regular Password with 2FA**: You must use an App Password if 2FA is enabled on Gmail.
3. **Account Security Alert**: Check your email for security alerts that might be blocking the login.
4. **Captcha Required**: Visit https://accounts.google.com/DisplayUnlockCaptcha to authorize the application.

### Connection Issues

1. **Network Restrictions**: Some networks block outgoing SMTP traffic.
2. **Firewall Settings**: Check if your firewall is blocking the connection.
3. **Incorrect Server/Port**: Verify the SMTP server address and port.
4. **TLS/SSL Issues**: Make sure you're using the correct port for TLS (587) or SSL (465).

## Benefits of Standard smtplib

1. **No Dependencies**: No need to install additional packages.
2. **Reliability**: Uses standard protocols that work with all email providers.
3. **Simplicity**: Straightforward configuration with minimal settings.
4. **Compatibility**: Works out of the box with Python's standard library.

## Customizing Email Content

You can customize the email content by editing the templates in `simple_smtp_notifier.py`:

1. `create_html_message()`: For HTML-formatted emails
2. `create_text_message()`: For plain text emails

Both templates support:
- Wind speed and direction
- Gust speed
- Wind conditions description
- Customizable threshold
- Location information 
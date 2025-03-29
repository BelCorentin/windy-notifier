# Windy Notifier

A Python application that monitors wind speed at Saint-Raphaël port and sends notifications when the wind exceeds a specified threshold.

## Features

- Reliably extracts wind data from JavaScript-rendered content using Selenium:
  - Wind speed
  - Wind direction
  - Wind gust speed (NEW!)
  - Temperature
- Multiple notification methods supported:
  - Email (Gmail or other SMTP providers)
    - Now supports HTML-formatted emails
    - Multiple recipients
  - Telegram
    - Enhanced formatting with Beaufort scale indicators
    - Multiple chat IDs
  - Or both simultaneously
- Beaufort scale wind descriptions
- Comprehensive logging and debugging
- Detailed test suite
- Modular code organization

## Requirements

- Python 3.7 or higher
- Google Chrome browser (for Selenium)
- Email account for notifications and/or Telegram account

## Project Structure

```
windy-notifier/
├── debug/                    # Debug artifacts directory
├── windy_notifier/           # Main package
│   ├── __init__.py
│   ├── main.py               # Main application module
│   ├── scraper/              # Data extraction modules
│   │   ├── __init__.py
│   │   └── weatherlink.py    # WeatherLink scraper
│   ├── notifiers/            # Notification modules
│   │   ├── __init__.py
│   │   ├── email_notifier.py # Email notifications
│   │   └── telegram_notifier.py # Telegram notifications
│   ├── utils/                # Utility modules
│   │   ├── __init__.py
│   │   └── converters.py     # Unit conversion utilities
│   └── tests/                # Test modules
│       ├── __init__.py
│       ├── test_scraper.py   # Tests for data extraction
│       └── test_notifiers.py # Tests for notifications
├── .env.example              # Example configuration file
├── requirements.txt          # Dependencies
├── run.py                    # Main entry point
└── test.py                   # Test launcher
```

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/windy-notifier.git
   cd windy-notifier
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your configuration:
   ```
   cp .env.example .env
   ```
   
4. Edit the `.env` file with your preferred notification settings

## Configuration

The `.env` file contains all the configuration options:

### Wind Settings
- `WIND_THRESHOLD`: The wind speed threshold in knots (default: 15)
- `CHECK_INTERVAL_MINUTES`: How often to check the wind speed (default: 30 minutes)

### Notification Method
- `NOTIFICATION_METHOD`: Choose from `email`, `telegram`, or `both`

### Email Notifications
- For Gmail, you'll need to [create an app password](https://support.google.com/accounts/answer/185833)
- `SMTP_SERVER`: SMTP server address (e.g., smtp.gmail.com)
- `SMTP_PORT`: SMTP port (typically 587 for TLS)
- `SMTP_USERNAME`: Your email username
- `SMTP_PASSWORD`: Your email password or app password
- `SENDER_EMAIL`: The email address to send from (usually the same as username)
- `RECIPIENT_EMAIL`: Comma-separated list of recipient email addresses

### Telegram Notifications
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from BotFather
- `TELEGRAM_CHAT_ID`: Comma-separated list of chat IDs

## Usage

### Running the Application

Start the monitoring service:

```
python run.py
```

The application will:
1. Check the wind speed immediately
2. Schedule regular checks according to the interval setting
3. Send notifications when the wind exceeds the threshold

### Running Tests

To run all tests:

```
python test.py
```

To run specific tests:

```
python test.py scraper         # Test the scraper functionality
python test.py email           # Test email notifications
python test.py telegram        # Test Telegram notifications
python test.py notifiers       # Test both notification methods
```

### Setting Up Telegram

To set up Telegram notifications:

```
python -m windy_notifier.notifiers.telegram_notifier
```

This will guide you through the process of creating a Telegram bot and getting your chat ID.

### Setting Up Email

To test your email configuration:

```
python -m windy_notifier.notifiers.email_notifier
```

## Running as a Service

### Using systemd (Linux)

1. Create a systemd service file:
   ```
   sudo nano /etc/systemd/system/windy-notifier.service
   ```

2. Add the following content (adjust paths as needed):
   ```
   [Unit]
   Description=Windy Notifier Service
   After=network.target

   [Service]
   User=yourusername
   WorkingDirectory=/path/to/windy-notifier
   ExecStart=/usr/bin/python3 /path/to/windy-notifier/run.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```
   sudo systemctl enable windy-notifier.service
   sudo systemctl start windy-notifier.service
   ```

4. Check the status:
   ```
   sudo systemctl status windy-notifier.service
   ```

## Troubleshooting

Check the log files in the `debug` directory for detailed information about the application's operation.

Common issues:

- Email/Telegram authentication problems: Verify your credentials and settings
- Chrome browser errors: Make sure Chrome is installed and compatible with the Selenium version
- Wind data extraction issues: Check `debug/weatherlink_debug.png` and `debug/last_weatherlink_page.html`

## License

MIT 
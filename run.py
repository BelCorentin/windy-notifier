#!/usr/bin/env python3
"""
Windy Notifier

A script that monitors wind speed at Saint-Raphaël port and sends notifications
when the wind exceeds a specified threshold.

Run this script to start the application.
"""

import sys
import os
import logging
from pathlib import Path

# Create debug directory if it doesn't exist
Path("debug").mkdir(exist_ok=True)

# Configure basic logging for the startup process
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug/startup.log"),
        logging.StreamHandler()
    ]
)

# Add the current directory to the Python path if needed
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    logging.info(f"Added {current_dir} to Python path")

try:
    from windy_notifier.main import run
    logging.info("Successfully imported main module")
    
    if __name__ == "__main__":
        run()
except ImportError as e:
    logging.error(f"Error importing main module: {e}")
    logging.error(f"Python path: {sys.path}")
    logging.error("Please make sure the windy_notifier package is properly installed.")
    sys.exit(1)
except Exception as e:
    logging.error(f"Unexpected error: {e}")
    import traceback
    logging.error(traceback.format_exc())
    sys.exit(1) 
#!/usr/bin/env python3
"""
WeatherLink Scraper Module

This module handles extracting weather data from the WeatherLink website using Selenium.
It focuses on extracting wind speed, wind direction, gust speed, and temperature.
"""

import re
import time
import logging
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Configure module logger
logger = logging.getLogger(__name__)

# Default URL for Saint-Raphaël port weather
DEFAULT_URL = "https://www.weatherlink.com/embeddablePage/show/d8f389c51427467eb5c4f266caaf78a9/summary"


def get_weather_data(url=DEFAULT_URL, save_debug_files=True):
    """
    Extract weather data from WeatherLink using Selenium.
    
    Args:
        url (str): URL of the WeatherLink page to scrape
        save_debug_files (bool): Whether to save debug files (screenshot, HTML)
        
    Returns:
        dict: Dictionary containing extracted weather data (wind_speed, wind_direction, 
              gust_speed, temperature)
    """
    logger.info(f"Accessing {url} with Selenium")
    
    # Configure Chrome options with more realistic browser appearance
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome driver initialized")
        
        # Set page load timeout
        driver.set_page_load_timeout(30)
        
        # Navigate to URL
        driver.get(url)
        logger.info("URL loaded")
        
        # Wait for content to load
        wait = WebDriverWait(driver, 20)
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            logger.info("Body tag found, page has loaded")
        except Exception as e:
            logger.warning(f"Waiting for body tag failed: {str(e)}")
        
        # Wait for JavaScript to execute
        time.sleep(8)
        
        # Save screenshot for debugging if requested
        if save_debug_files:
            try:
                driver.save_screenshot("debug/weatherlink_debug.png")
                logger.debug("Screenshot saved for debugging")
            except Exception as e:
                logger.warning(f"Could not save screenshot: {str(e)}")
        
        # Initialize weather data dictionary
        weather_data = {}
        
        # DIRECT TARGETING: Try to find wind elements by specific selectors first
        try:
            # Current Wind Speed
            extract_element_by_label(driver, weather_data, 'wind_speed', 
                                    ["Wind Speed", "Current Wind", "Wind"], 
                                    r'(\d+(?:[,.]\d+)?)\s*(mph|km/h|kts|knots)')
            
            # Wind Gust Speed (added as requested)
            extract_element_by_label(driver, weather_data, 'gust_speed',
                                    ["Wind Gust", "Gust Speed", "Gust"],
                                    r'(\d+(?:[,.]\d+)?)\s*(mph|km/h|kts|knots)')
            
            # Wind Direction
            wind_dir_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Wind Direction')]//following::*[1]")
            if wind_dir_elements:
                for elem in wind_dir_elements:
                    text = elem.text.strip()
                    if text:
                        weather_data['wind_direction'] = text
                        logger.info(f"Found wind direction: {text}")
                        break
            
            # Temperature
            temp_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Temperature')]//following::*[1]")
            if temp_elements:
                for elem in temp_elements:
                    text = elem.text.strip()
                    if text and re.search(r'(\d+(?:[,.]\d+)?)\s*[°]?[CF]', text, re.I):
                        weather_data['temperature'] = text
                        logger.info(f"Found temperature: {text}")
                        break
                        
        except Exception as e:
            logger.warning(f"Error finding elements directly: {str(e)}")
            
        # If direct targeting failed, use BeautifulSoup as fallback
        if 'wind_speed' not in weather_data or 'gust_speed' not in weather_data:
            fallback_extraction(driver, weather_data, save_debug_files)
        
        return weather_data
        
    except Exception as e:
        logger.error(f"Error accessing website with Selenium: {str(e)}")
        logger.error(traceback.format_exc())
        return {}
    
    finally:
        # Always close the driver
        if 'driver' in locals():
            driver.quit()
            logger.info("Selenium driver closed")


def extract_element_by_label(driver, data_dict, key, labels, pattern):
    """
    Helper function to extract element by its label and pattern.
    
    Args:
        driver: Selenium WebDriver instance
        data_dict: Dictionary to store the extracted data
        key: Key to use in the data dictionary
        labels: List of possible labels to look for
        pattern: Regex pattern to validate the value
    """
    for label in labels:
        xpath = f"//*[contains(text(), '{label}')]//following::*[1]"
        elements = driver.find_elements(By.XPATH, xpath)
        
        if elements:
            for elem in elements:
                text = elem.text.strip()
                if text and re.search(pattern, text, re.I):
                    data_dict[key] = text
                    logger.info(f"Found {key}: {text}")
                    return True
    
    # If not found by label, try to find by value format
    value_pattern = pattern.replace('(', '').replace(')', '')
    value_xpath = f"//*[matches(text(), '{value_pattern}')]"
    try:
        value_elements = driver.find_elements(By.XPATH, value_xpath)
        for elem in value_elements:
            text = elem.text.strip()
            if text and re.search(pattern, text, re.I):
                # Make sure this actually contains wind-related terms
                parent = elem.find_element(By.XPATH, "./..")
                parent_text = parent.text.lower()
                if any(label.lower() in parent_text for label in labels):
                    data_dict[key] = text
                    logger.info(f"Found {key} by value: {text}")
                    return True
    except:
        pass  # XPath with matches() might not be supported
    
    return False


def fallback_extraction(driver, weather_data, save_debug_files):
    """
    Fallback extraction method using BeautifulSoup when direct targeting fails.
    
    Args:
        driver: Selenium WebDriver instance
        weather_data: Dictionary to store weather data
        save_debug_files: Whether to save debug files
    """
    logger.info("Direct targeting failed, using BeautifulSoup fallback")
    page_source = driver.page_source
    
    # Save the HTML only if direct targeting failed and debug files are enabled
    if save_debug_files:
        with open("debug/last_weatherlink_page.html", 'w', encoding='utf-8') as f:
            f.write(page_source)
    
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Look for wind speed if not already found
    if 'wind_speed' not in weather_data:
        wind_elements = soup.find_all(string=re.compile(r'(?:wind\s+speed|mph|km/h|kts|knots)', re.I))
        extract_from_elements(wind_elements, weather_data, 'wind_speed', r'(\d+(?:[,.]\d+)?)\s*(mph|km/h|kts|knots)')
    
    # Look for gust speed if not already found
    if 'gust_speed' not in weather_data:
        gust_elements = soup.find_all(string=re.compile(r'(?:gust|rafale|mph|km/h|kts|knots)', re.I))
        extract_from_elements(gust_elements, weather_data, 'gust_speed', r'(\d+(?:[,.]\d+)?)\s*(mph|km/h|kts|knots)')
    
    # Last resort: extract from all text
    all_text = soup.get_text(separator='\n', strip=True)
    
    # Wind speed
    if 'wind_speed' not in weather_data:
        extract_from_text(all_text, weather_data, 'wind_speed', r'wind\s+speed.*?(\d+(?:[,.]\d+)?)\s*(mph|km/h|kts|knots)', 
                         r'(\d+(?:[,.]\d+)?)\s*(mph|km/h|kts|knots)')
    
    # Gust speed
    if 'gust_speed' not in weather_data:
        extract_from_text(all_text, weather_data, 'gust_speed', r'gust.*?(\d+(?:[,.]\d+)?)\s*(mph|km/h|kts|knots)',
                         r'(\d+(?:[,.]\d+)?)\s*(mph|km/h|kts|knots)')
    
    # Wind direction if not already found
    if 'wind_direction' not in weather_data:
        dir_match = re.search(r'(?:wind|from)\s+([NESW]{1,3}|North|South|East|West|Nord|Sud|Est|Ouest)', all_text, re.I)
        if dir_match:
            weather_data['wind_direction'] = dir_match.group(1)
            logger.info(f"Extracted wind direction: {weather_data['wind_direction']}")


def extract_from_elements(elements, data_dict, key, pattern):
    """
    Extract data from a list of elements using a pattern.
    
    Args:
        elements: List of BeautifulSoup elements
        data_dict: Dictionary to store the extracted data
        key: Key to use in the data dictionary
        pattern: Regex pattern to match
    """
    if elements:
        for elem in elements:
            text = elem.strip()
            match = re.search(pattern, text, re.I)
            if match:
                data_dict[key] = match.group(0)
                logger.info(f"Extracted {key} from text: {data_dict[key]}")
                return True
    return False


def extract_from_text(text, data_dict, key, context_pattern, fallback_pattern):
    """
    Extract data from text using patterns.
    
    Args:
        text: Text to search in
        data_dict: Dictionary to store the extracted data
        key: Key to use in the data dictionary
        context_pattern: Pattern with context
        fallback_pattern: Pattern without context
    """
    # Try with context first
    context_match = re.search(context_pattern, text, re.I)
    if context_match:
        # Replace comma with period for consistent decimal parsing
        value = context_match.group(1).replace(',', '.')
        unit = context_match.group(2)
        data_dict[key] = f"{value} {unit}"
        logger.info(f"Extracted {key} with context: {data_dict[key]}")
        return True
    
    # Fallback to just finding any matching pattern
    fallback_match = re.search(fallback_pattern, text, re.I)
    if fallback_match:
        # Replace comma with period for consistent decimal parsing
        value = fallback_match.group(1).replace(',', '.')
        unit = fallback_match.group(2)
        data_dict[key] = f"{value} {unit}"
        logger.info(f"Extracted {key} from all text: {data_dict[key]}")
        return True
        
    return False 
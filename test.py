#!/usr/bin/env python3
"""
Windy Notifier Test Launcher

This script provides a simple way to run the various test modules
in the Windy Notifier project. It can run all tests or specific ones.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Define test modules
TEST_MODULES = {
    "scraper": "windy_notifier/tests/test_scraper.py",
    "email": "windy_notifier/tests/test_notifiers.py --method email",
    "telegram": "windy_notifier/tests/test_notifiers.py --method telegram",
    "notifiers": "windy_notifier/tests/test_notifiers.py --method both"
}


def run_test(test_name, extra_args=None):
    """
    Run a specific test module.
    
    Args:
        test_name (str): Name of the test to run
        extra_args (list, optional): Extra arguments to pass to the test
        
    Returns:
        int: Exit code from the test
    """
    if test_name not in TEST_MODULES:
        print(f"❌ Unknown test: {test_name}")
        return 1
    
    command = f"python {TEST_MODULES[test_name]}"
    if extra_args:
        command += f" {' '.join(extra_args)}"
    
    print(f"\n==== Running {test_name} tests ====")
    print(f"Command: {command}\n")
    
    result = subprocess.run(command, shell=True)
    return result.returncode


def main():
    """Main function to parse arguments and run tests."""
    parser = argparse.ArgumentParser(description='Run Windy Notifier tests.')
    parser.add_argument('tests', nargs='*', choices=['all'] + list(TEST_MODULES.keys()),
                      default=['all'], help='Tests to run')
    parser.add_argument('--args', nargs=argparse.REMAINDER,
                      help='Additional arguments to pass to the test script')
    
    args = parser.parse_args()
    
    # Create debug directory if it doesn't exist
    Path("debug").mkdir(exist_ok=True)
    
    exit_code = 0
    if 'all' in args.tests:
        print("==== Running all tests ====")
        for test_name in TEST_MODULES:
            result = run_test(test_name, args.args)
            if result != 0:
                exit_code = result
    else:
        for test_name in args.tests:
            result = run_test(test_name, args.args)
            if result != 0:
                exit_code = result
    
    print("\n==== Test Summary ====")
    if exit_code == 0:
        print("✅ All tests completed successfully!")
    else:
        print(f"❌ Some tests failed with exit code {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main()) 
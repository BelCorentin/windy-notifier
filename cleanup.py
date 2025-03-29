#!/usr/bin/env python3
"""
Cleanup Script

This script helps clean up temporary debug files created by the Windy Notifier application.
"""

import os
import glob
import argparse

# Patterns for temp/debug files
TEMP_FILE_PATTERNS = [
    "*.log",
    "*.html",
    "weatherlink_debug.png",
    "last_check.json"
]

def list_files_to_clean():
    """
    List all temporary files that can be safely deleted.
    
    Returns:
        list: Paths of files that can be safely deleted
    """
    all_files = []
    for pattern in TEMP_FILE_PATTERNS:
        all_files.extend(glob.glob(pattern))
    
    # Filter out important files
    important_files = ["README.md", ".env", ".env.example"]
    temp_files = [f for f in all_files if f not in important_files]
    
    return sorted(temp_files)

def main():
    """Main function to list and optionally delete temporary files."""
    parser = argparse.ArgumentParser(description='Clean up temporary debug files.')
    parser.add_argument('--delete', action='store_true', help='Delete files without confirmation prompt')
    args = parser.parse_args()
    
    files_to_clean = list_files_to_clean()
    
    if not files_to_clean:
        print("No temporary files found to clean up.")
        return
    
    print("The following temporary files will be deleted:")
    for file in files_to_clean:
        print(f"  - {file}")
    
    if args.delete or input("\nDelete these files? (y/n): ").lower() == 'y':
        for file in files_to_clean:
            try:
                os.remove(file)
                print(f"Deleted: {file}")
            except Exception as e:
                print(f"Error deleting {file}: {e}")
        
        print("\nCleanup completed.")
    else:
        print("Cleanup cancelled.")

if __name__ == "__main__":
    main() 
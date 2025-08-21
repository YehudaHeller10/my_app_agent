#!/usr/bin/env python3
"""
Android App Generator - Launcher Script

Simple launcher for the Android App Generator application.
This script provides an easy way to start the application.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main application
from main import main

if __name__ == "__main__":
    main()
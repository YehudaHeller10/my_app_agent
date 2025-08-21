#!/usr/bin/env python3
"""
Android App Generator - Main Entry Point

A powerful desktop application that uses local AI models to generate 
complete Android applications from natural language descriptions.

Author: Android App Generator Team
Version: 1.0.0
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import traceback

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from gui.main_window import MainWindow
from core.llm_manager import LLMManager
from core.project_generator import ProjectGenerator


def setup_environment():
    """Setup the application environment"""
    # Create necessary directories
    directories = [
        "models",
        "config",
        "output",
        "templates",
        "logs"
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    # Set up logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )


def check_dependencies():
    """Check if all required dependencies are available"""
    required_packages = [
        'gpt4all',
        'tkinter',
        'json',
        'threading',
        'urllib'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'json':
                import json
            elif package == 'threading':
                import threading
            elif package == 'urllib':
                import urllib
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        error_msg = f"Missing required packages: {', '.join(missing_packages)}\n\n"
        error_msg += "Please install them using:\n"
        error_msg += "pip install -r requirements.txt"
        messagebox.showerror("Missing Dependencies", error_msg)
        return False

    return True


def show_splash_screen():
    """Show a splash screen while the application loads"""
    splash = tk.Tk()
    splash.title("Android App Generator")
    splash.geometry("400x300")
    splash.resizable(False, False)

    # Center the splash window
    splash.eval('tk::PlaceWindow . center')

    # Create splash content
    frame = tk.Frame(splash, bg='#f0f0f0')
    frame.pack(fill='both', expand=True)

    # App icon/logo
    tk.Label(frame, text="🤖", font=('Segoe UI', 48), bg='#f0f0f0').pack(pady=20)

    # App title
    tk.Label(frame, text="Android App Generator",
             font=('Segoe UI', 18, 'bold'), bg='#f0f0f0').pack()

    # Subtitle
    tk.Label(frame, text="AI-Powered Android Development",
             font=('Segoe UI', 12), fg='#666', bg='#f0f0f0').pack(pady=5)

    # Loading message
    loading_label = tk.Label(frame, text="Initializing...",
                             font=('Segoe UI', 10), bg='#f0f0f0')
    loading_label.pack(pady=20)

    # Simple loading indicator instead of progress bar
    loading_indicator = tk.Label(frame, text="⏳", font=('Segoe UI', 24), bg='#f0f0f0')
    loading_indicator.pack(pady=10)

    return splash, loading_label


def main():
    """Main application entry point"""
    try:
        # Setup environment
        setup_environment()

        # Check dependencies
        if not check_dependencies():
            sys.exit(1)

        # Show splash screen
        splash, loading_label = show_splash_screen()
        splash.update()

        # Update loading message
        loading_label.config(text="Checking dependencies...")
        splash.update()

        # Initialize core components
        loading_label.config(text="Initializing AI model...")
        splash.update()

        # Create main window
        loading_label.config(text="Loading user interface...")
        splash.update()

        # Close splash and create main window
        splash.destroy()

        # Create and run main application
        try:
            app = MainWindow()
            app.run()
        except Exception as e:
            error_msg = f"Failed to create main window: {str(e)}"
            print(error_msg)
            messagebox.showerror("Application Error", error_msg)
            raise

    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)

    except Exception as e:
        error_msg = f"Application error: {str(e)}\n\n"
        error_msg += "Please check the logs for more details."

        # Try to show error dialog, fallback to console if tkinter fails
        try:
            messagebox.showerror("Application Error", error_msg)
        except:
            print(error_msg)
            traceback.print_exc()

        sys.exit(1)


if __name__ == "__main__":
    main()
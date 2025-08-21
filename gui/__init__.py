"""
GUI module for Android App Generator

This module contains all the user interface components including:
- MainWindow: The main application window
- ChatPanel: Chat interface for AI interaction
- ProjectPanel: Project management interface
- SettingsPanel: Application settings interface
"""

from .main_window import MainWindow
from .chat_panel import ChatPanel
from .project_panel import ProjectPanel
from .settings_panel import SettingsPanel

__all__ = ['MainWindow', 'ChatPanel', 'ProjectPanel', 'SettingsPanel']
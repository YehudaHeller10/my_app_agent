"""
Core module for Android App Generator

This module contains the core functionality including:
- LLMManager: Manages local AI models
- ProjectGenerator: Generates Android projects
- AndroidTemplates: Provides project templates
"""

from .llm_manager import LLMManager
from .project_generator import ProjectGenerator
from .android_templates import AndroidTemplates

__all__ = ['LLMManager', 'ProjectGenerator', 'AndroidTemplates']
"""
🧠 Open WebUI AI Core

A unified module for all AI capabilities in Open WebUI, integrating various
consciousness systems, model routing, and response generation features.

This module serves as the central point for accessing all AI-related
functionality in the Open WebUI platform.
"""

from .consciousness import EnhancedConsciousness
from .models import ModelManager
from .routing import ModelRouter
from .generation import ResponseGenerator
from .utils import AIUtils

__all__ = [
    'EnhancedConsciousness',
    'ModelManager',
    'ModelRouter',
    'ResponseGenerator',
    'AIUtils'
]

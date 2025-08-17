"""
Test configuration for Open WebUI

This file contains pytest configuration and fixtures for testing Open WebUI components.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Pytest configuration
def pytest_configure(config):
    """Configure pytest for Open WebUI testing."""
    # Register custom markers
    config.addinivalue_line("markers", "unit: mark a test as a unit test")
    config.addinivalue_line("markers", "integration: mark a test as an integration test")
    config.addinivalue_line("markers", "e2e: mark a test as an end-to-end test")
    config.addinivalue_line("markers", "ai_core: mark a test for AI Core components")
    config.addinivalue_line("markers", "backends: mark a test for backend components")
    config.addinivalue_line("markers", "consciousness: mark a test for consciousness components")

# Fixtures
@pytest.fixture
def mock_model_loader():
    """Provide a mock model loader for testing."""
    mock = MagicMock()
    mock.load_model.return_value = MagicMock(name="mock_model")
    return mock

@pytest.fixture
def mock_text_generation():
    """Provide a mock text generation backend for testing."""
    mock = MagicMock()
    mock.generate.return_value = "This is a mock generated response"
    return mock

@pytest.fixture
def mock_consciousness():
    """Provide a mock consciousness system for testing."""
    mock = MagicMock()
    mock.process_input.return_value = {
        "text": "Enhanced response",
        "metadata": {"consciousness_system": "mock"}
    }
    return mock

@pytest.fixture
def test_prompt():
    """Provide a test prompt for generation tests."""
    return "This is a test prompt for AI generation"

@pytest.fixture
def ai_core_config():
    """Provide a test configuration for the AI Core."""
    return {
        "logging_level": "DEBUG",
        "default_model": "test-model",
        "consciousness": {
            "enabled": True,
            "system": "enhanced"
        },
        "models": {
            "load_on_startup": []
        }
    }

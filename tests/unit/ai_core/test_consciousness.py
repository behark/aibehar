"""
Unit tests for the AI Core consciousness module.

These tests validate the functionality of the consciousness module
in the AI Core, including the EnhancedConsciousness class.
"""
import pytest
from unittest.mock import MagicMock, patch

from ai_core.consciousness import EnhancedConsciousness

@pytest.mark.unit
@pytest.mark.ai_core
@pytest.mark.consciousness
class TestEnhancedConsciousness:
    """Test cases for the EnhancedConsciousness class."""

    def test_init(self):
        """Test initialization of EnhancedConsciousness."""
        consciousness = EnhancedConsciousness()
        assert consciousness is not None
        assert consciousness._enhanced_consciousness is None
        assert consciousness._advanced_sovereign is None

    def test_init_with_config(self):
        """Test initialization with configuration."""
        config = {"consciousness": {"system": "enhanced"}}
        consciousness = EnhancedConsciousness(config)
        assert consciousness.config == config

    @patch("ai_core.consciousness.ENHANCED_CONSCIOUSNESS_AVAILABLE", True)
    @patch("ai_core.consciousness.EnhancedConsciousnessAI")
    def test_init_with_enhanced_consciousness(self, mock_enhanced):
        """Test initialization with enhanced consciousness available."""
        mock_enhanced.return_value = MagicMock()
        consciousness = EnhancedConsciousness()
        assert consciousness._enhanced_consciousness is not None

    @patch("ai_core.consciousness.ADVANCED_SOVEREIGN_AVAILABLE", True)
    @patch("ai_core.consciousness.AdvancedSovereignConsciousness")
    def test_init_with_advanced_sovereign(self, mock_advanced):
        """Test initialization with advanced sovereign available."""
        mock_advanced.return_value = MagicMock()
        consciousness = EnhancedConsciousness()
        assert consciousness._advanced_sovereign is not None

    def test_process_input_basic(self):
        """Test basic input processing with no consciousness systems."""
        consciousness = EnhancedConsciousness()
        consciousness._enhanced_consciousness = None
        consciousness._advanced_sovereign = None

        result = consciousness.process_input("Hello world")

        assert "text" in result
        assert "metadata" in result
        assert "consciousness_system" in result["metadata"]
        assert result["metadata"]["consciousness_system"] == "basic"

    def test_process_input_with_enhanced(self):
        """Test input processing with enhanced consciousness."""
        consciousness = EnhancedConsciousness()
        consciousness._enhanced_consciousness = MagicMock()
        consciousness._advanced_sovereign = None

        # Set up the mock
        enhanced_response = {"text": "Enhanced response", "emotional_resonance": 0.8}
        consciousness._use_enhanced_consciousness = MagicMock(return_value=enhanced_response)

        result = consciousness.process_input("Hello world")

        assert result["text"] == "Enhanced response"
        assert consciousness._use_enhanced_consciousness.called

    def test_process_input_with_advanced(self):
        """Test input processing with advanced sovereign consciousness."""
        consciousness = EnhancedConsciousness()
        consciousness._enhanced_consciousness = None
        consciousness._advanced_sovereign = MagicMock()

        # Set up the mock
        advanced_response = {"text": "Advanced response", "dimensional_resonance": 0.9}
        consciousness._use_advanced_sovereign = MagicMock(return_value=advanced_response)

        result = consciousness.process_input("Hello world")

        assert result["text"] == "Advanced response"
        assert consciousness._use_advanced_sovereign.called

    def test_process_input_with_context(self):
        """Test input processing with context information."""
        consciousness = EnhancedConsciousness()
        consciousness._enhanced_consciousness = None
        consciousness._advanced_sovereign = None

        context = {"user_id": "123", "conversation_id": "456"}
        result = consciousness.process_input("Hello world", context)

        assert "context" in result["metadata"]
        assert result["metadata"]["context"] == context

    def test_process_input_with_error_handling(self):
        """Test error handling during input processing."""
        consciousness = EnhancedConsciousness()
        consciousness._enhanced_consciousness = MagicMock()
        consciousness._advanced_sovereign = MagicMock()

        # Set up mocks to raise exceptions
        consciousness._use_advanced_sovereign = MagicMock(side_effect=Exception("Advanced error"))
        consciousness._use_enhanced_consciousness = MagicMock(side_effect=Exception("Enhanced error"))

        # Should fall back to basic processing
        result = consciousness.process_input("Hello world")

        assert "text" in result
        assert result["metadata"]["consciousness_system"] == "basic"

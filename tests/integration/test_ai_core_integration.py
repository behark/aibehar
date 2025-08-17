"""
Integration tests for the AI Core components.

These tests validate that the different AI Core components
work together correctly as an integrated system.
"""
import pytest
from unittest.mock import MagicMock, patch
import asyncio
import os
import sys

# Add project root to path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ai_core import EnhancedConsciousness, ModelManager, ModelRouter, ResponseGenerator
from ai_core_bridge import AICoreBridge

@pytest.mark.integration
@pytest.mark.ai_core
class TestAICoreIntegration:
    """Integration tests for AI Core components."""

    @pytest.mark.asyncio
    @patch("ai_core.consciousness.ENHANCED_CONSCIOUSNESS_AVAILABLE", True)
    @patch("ai_core.consciousness.EnhancedConsciousnessAI")
    @patch("ai_core.models.MODEL_LOADER_AVAILABLE", True)
    @patch("ai_core.models.ModelLoader")
    async def test_end_to_end_query_processing(self, mock_model_loader, mock_consciousness_ai):
        """Test end-to-end query processing through multiple components."""
        # Set up consciousness mock
        mock_consciousness = MagicMock()
        mock_consciousness_ai.return_value = mock_consciousness
        mock_consciousness.process.return_value = "Enhanced test response"

        # Set up model loader mock
        mock_loader = MagicMock()
        mock_model_loader.return_value = mock_loader
        mock_model = MagicMock(name="test_model")
        mock_loader.load_model.return_value = mock_model

        # Create real instances of the core components
        model_manager = ModelManager()
        model_router = ModelRouter()
        response_generator = ResponseGenerator()
        consciousness = EnhancedConsciousness()

        # Configure components for the test
        model_manager._model_loader = mock_loader

        # Load a test model
        model = model_manager.load_model("test-model", "/path/to/model")
        assert model is not None

        # Create a bridge using the real components
        bridge = AICoreBridge()
        bridge.consciousness = consciousness
        bridge.model_manager = model_manager
        bridge.model_router = model_router
        bridge.response_generator = response_generator

        # Configure response generator to return a mock response
        async def mock_generate(*args, **kwargs):
            return {
                "text": "Test generated response",
                "model_id": "test-model",
                "metadata": {"generation_method": "mock"}
            }

        response_generator.generate_response = mock_generate

        # Process a test query through the bridge
        result = await bridge.process_query(
            query="What is the meaning of life?",
            user_id="test-user",
            context={"session_id": "test-session"},
            parameters={"temperature": 0.7}
        )

        # Verify the result contains the expected components
        assert "text" in result
        assert "model_id" in result
        assert "metadata" in result

        # The model manager should have been used to get models
        assert len(model_manager.list_models()) > 0

        # Clean up
        model_manager.unload_model("test-model")

    @pytest.mark.asyncio
    async def test_ai_core_components_isolation(self):
        """Test that AI Core components properly isolate errors."""
        # Create instances with mocks that will raise exceptions
        model_manager = ModelManager()
        model_manager.list_models = MagicMock(side_effect=Exception("Model manager error"))

        model_router = ModelRouter()
        model_router.route_query = MagicMock(side_effect=Exception("Router error"))

        # Create a bridge with the problematic components
        bridge = AICoreBridge()
        bridge.model_manager = model_manager
        bridge.model_router = model_router

        # The bridge should handle the exceptions and return an error response
        result = await bridge.process_query("Test query")

        # Verify error response format
        assert "error" in result
        assert result["error"] is True
        assert "error_message" in result
        assert "error_type" in result

    def test_ai_core_initialization_resilience(self):
        """Test that AI Core initialization is resilient to missing components."""
        # Create a configuration that references non-existent components
        config = {
            "non_existent": {
                "option": "value"
            }
        }

        # Components should initialize without errors despite the bad config
        consciousness = EnhancedConsciousness(config)
        model_manager = ModelManager(config)
        model_router = ModelRouter(config)
        response_generator = ResponseGenerator(config)

        # All components should be created successfully
        assert consciousness is not None
        assert model_manager is not None
        assert model_router is not None
        assert response_generator is not None

        # And they should have the configuration we provided
        assert consciousness.config == config
        assert model_manager.config == config
        assert model_router.config == config
        assert response_generator.config == config

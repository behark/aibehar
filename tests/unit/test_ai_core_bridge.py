"""
Unit tests for the AI Core Bridge.

These tests validate the functionality of the AI Core Bridge,
which provides a simplified interface for the AI core.
"""
import pytest
from unittest.mock import MagicMock, patch
import asyncio

from ai_core_bridge import AICoreBridge

@pytest.mark.unit
@pytest.mark.ai_core
class TestAICoreBridge:
    """Test cases for the AICoreBridge class."""

    @patch("ai_core_bridge.EnhancedConsciousness")
    @patch("ai_core_bridge.ModelManager")
    @patch("ai_core_bridge.ModelRouter")
    @patch("ai_core_bridge.ResponseGenerator")
    def test_init(self, mock_generator, mock_router, mock_manager, mock_consciousness):
        """Test initialization of AICoreBridge."""
        # Set up mocks
        mock_consciousness.return_value = MagicMock()
        mock_manager.return_value = MagicMock()
        mock_router.return_value = MagicMock()
        mock_generator.return_value = MagicMock()

        bridge = AICoreBridge()

        assert bridge is not None
        assert bridge.consciousness is not None
        assert bridge.model_manager is not None
        assert bridge.model_router is not None
        assert bridge.response_generator is not None

    def test_get_instance(self):
        """Test singleton pattern of AICoreBridge."""
        # Reset the instance
        AICoreBridge._instance = None

        # Create instances with patches to avoid actual initialization
        with patch("ai_core_bridge.EnhancedConsciousness"), \
             patch("ai_core_bridge.ModelManager"), \
             patch("ai_core_bridge.ModelRouter"), \
             patch("ai_core_bridge.ResponseGenerator"):

            instance1 = AICoreBridge.get_instance()
            instance2 = AICoreBridge.get_instance()

            assert instance1 is instance2  # Should be the same instance

    @pytest.mark.asyncio
    @patch("ai_core_bridge.AICoreBridge.model_manager")
    @patch("ai_core_bridge.AICoreBridge.model_router")
    @patch("ai_core_bridge.AICoreBridge.response_generator")
    @patch("ai_core_bridge.AICoreBridge.consciousness")
    async def test_process_query(self, mock_consciousness, mock_generator, mock_router, mock_manager):
        """Test processing a query through the AI Core Bridge."""
        # Create a bridge instance with mocked components
        bridge = MagicMock()
        bridge.model_manager = mock_manager
        bridge.model_router = mock_router
        bridge.response_generator = mock_generator
        bridge.consciousness = mock_consciousness

        # Configure mocks
        mock_manager.list_models.return_value = ["model1", "model2"]

        mock_router.route_query.return_value = {
            "model_id": "model1",
            "confidence": 0.9,
            "metadata": {"routing": "test"}
        }

        # Set up async mock for generate_response
        mock_generator.generate_response = MagicMock(return_value=asyncio.Future())
        mock_generator.generate_response.return_value.set_result({
            "text": "Generated response",
            "model_id": "model1",
            "metadata": {"generation": "test"}
        })

        mock_consciousness.process_input.return_value = {
            "text": "Enhanced response",
            "metadata": {"consciousness": "test"}
        }

        # Call the method directly with the mocked instance
        result = await AICoreBridge.process_query(
            bridge,
            query="Test query",
            user_id="user123",
            context={"test": "context"},
            parameters={"temperature": 0.7}
        )

        # Verify the result
        assert result["text"] == "Enhanced response"
        assert result["model_id"] == "model1"
        assert "consciousness" in result["metadata"]

        # Verify interactions with mocked components
        mock_manager.list_models.assert_called_once()
        mock_router.route_query.assert_called_once()
        mock_generator.generate_response.assert_called_once()
        mock_consciousness.process_input.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_query_exception(self):
        """Test exception handling when processing a query."""
        # Create a bridge instance with proper exception handling
        bridge = AICoreBridge()

        # Override the components with mocks that raise exceptions
        bridge.model_manager = MagicMock()
        bridge.model_manager.list_models.side_effect = Exception("Models error")

        # Test that the method handles exceptions and returns an error response
        result = await bridge.process_query("Test query")

        assert result["error"] is True
        assert "error_message" in result
        assert "Failed to process query" in result["error_message"]

    def test_load_model(self):
        """Test loading a model through the AI Core Bridge."""
        bridge = AICoreBridge()
        bridge.model_manager = MagicMock()
        bridge.model_manager.load_model.return_value = MagicMock()

        result = bridge.load_model(
            model_id="test-model",
            model_path="/path/to/model",
            model_type="text"
        )

        assert result is True
        bridge.model_manager.load_model.assert_called_with(
            model_id="test-model",
            model_path="/path/to/model",
            model_type="text"
        )

    def test_load_model_failure(self):
        """Test handling of model loading failure."""
        bridge = AICoreBridge()
        bridge.model_manager = MagicMock()
        bridge.model_manager.load_model.return_value = None

        result = bridge.load_model("test-model")

        assert result is False

    def test_load_model_exception(self):
        """Test exception handling when loading a model."""
        bridge = AICoreBridge()
        bridge.model_manager = MagicMock()
        bridge.model_manager.load_model.side_effect = Exception("Loading error")

        result = bridge.load_model("test-model")

        assert result is False

    def test_get_ai_capabilities(self):
        """Test getting AI capabilities through the AI Core Bridge."""
        bridge = AICoreBridge()

        # Set up mocks
        bridge.consciousness = MagicMock()
        bridge.consciousness._enhanced_consciousness = MagicMock()
        bridge.consciousness._advanced_sovereign = None

        bridge.model_manager = MagicMock()
        bridge.model_manager.list_models.return_value = ["model1", "model2"]
        bridge.model_manager._model_loader = MagicMock()

        bridge.model_router = MagicMock()
        bridge.model_router.get_router_status.return_value = {
            "available": True,
            "type": "advanced"
        }

        bridge.response_generator = MagicMock()
        bridge.response_generator.get_available_models.return_value = [
            {"id": "model1", "source": "text_generation"}
        ]

        capabilities = bridge.get_ai_capabilities()

        assert "consciousness" in capabilities
        assert capabilities["consciousness"]["available"] is True
        assert capabilities["consciousness"]["advanced_available"] is False

        assert "models" in capabilities
        assert capabilities["models"]["available"] == ["model1", "model2"]
        assert capabilities["models"]["loader_available"] is True

        assert "routing" in capabilities
        assert capabilities["routing"]["available"] is True
        assert capabilities["routing"]["type"] == "advanced"

        assert "generation" in capabilities
        assert len(capabilities["generation"]["available_models"]) == 1

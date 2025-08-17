"""
Unit tests for the AI Core routing module.

These tests validate the functionality of the routing module
in the AI Core, including the ModelRouter class.
"""
import pytest
from unittest.mock import MagicMock, patch

from ai_core.routing import ModelRouter

@pytest.mark.unit
@pytest.mark.ai_core
class TestModelRouter:
    """Test cases for the ModelRouter class."""

    def test_init(self):
        """Test initialization of ModelRouter."""
        router = ModelRouter()
        assert router is not None
        assert router._router is None

    def test_init_with_config(self):
        """Test initialization with configuration."""
        config = {"routing": {"strategy": "weighted"}}
        router = ModelRouter(config)
        assert router.config == config

    @patch("ai_core.routing.ROUTER_AVAILABLE", True)
    @patch("ai_core.routing.MultiModelIntelligenceRouter")
    def test_init_router(self, mock_router_class):
        """Test initialization with router available."""
        mock_router = MagicMock()
        mock_router_class.return_value = mock_router

        router = ModelRouter()

        assert router._router is mock_router

    def test_route_query_basic(self):
        """Test basic query routing with no advanced router."""
        router = ModelRouter()
        router._router = None

        available_models = ["model1", "model2", "model3"]
        result = router.route_query("Test query", available_models=available_models)

        assert result["model_id"] == "model1"
        assert result["confidence"] == 1.0
        assert result["metadata"]["method"] == "fallback_routing"

    def test_route_query_no_models(self):
        """Test query routing with no available models."""
        router = ModelRouter()
        router._router = None

        result = router.route_query("Test query", available_models=[])

        assert result["model_id"] is None
        assert result["confidence"] == 0.0
        assert "error" in result["metadata"]

    @patch("ai_core.routing.ROUTER_AVAILABLE", True)
    def test_route_query_advanced(self):
        """Test advanced query routing."""
        router = ModelRouter()
        router._router = MagicMock()

        # Mock the router's route_query method
        router._router.route_query.return_value = MagicMock(
            selected_model="model2",
            confidence=0.85,
            metadata={"reasoning": "Test reasoning"}
        )

        available_models = ["model1", "model2", "model3"]
        result = router.route_query(
            "Test query",
            context={"user_preference": "accuracy"},
            available_models=available_models
        )

        assert result["model_id"] == "model2"
        assert result["confidence"] == 0.85
        assert result["metadata"]["reasoning"] == "Test reasoning"

        # Verify the router was called with correct arguments
        router._router.route_query.assert_called_once()

    @patch("ai_core.routing.ROUTER_AVAILABLE", True)
    def test_route_query_advanced_exception(self):
        """Test exception handling in advanced query routing."""
        router = ModelRouter()
        router._router = MagicMock()

        # Set up the mock to raise an exception
        router._router.route_query.side_effect = Exception("Routing error")

        available_models = ["model1", "model2", "model3"]
        result = router.route_query("Test query", available_models=available_models)

        # Should fall back to basic routing
        assert result["model_id"] == "model1"
        assert result["confidence"] == 1.0
        assert result["metadata"]["method"] == "fallback_routing"

    def test_get_router_status_not_available(self):
        """Test getting router status when not available."""
        router = ModelRouter()
        router._router = None

        status = router.get_router_status()

        assert status["available"] is False
        assert status["type"] == "fallback"
        assert status["status"] == "limited_functionality"

    @patch("ai_core.routing.ROUTER_AVAILABLE", True)
    def test_get_router_status_available(self):
        """Test getting router status when available."""
        router = ModelRouter()
        router._router = MagicMock()

        status = router.get_router_status()

        assert status["available"] is True
        assert status["type"] == "advanced"
        assert status["status"] == "operational"

    @patch("ai_core.routing.ROUTER_AVAILABLE", True)
    def test_get_router_status_exception(self):
        """Test exception handling when getting router status."""
        router = ModelRouter()
        router._router = MagicMock()

        # Set up the property to raise an exception
        type(router._router).status = MagicMock(side_effect=Exception("Status error"))

        status = router.get_router_status()

        assert status["available"] is False
        assert status["type"] == "fallback"
        assert status["status"] == "limited_functionality"

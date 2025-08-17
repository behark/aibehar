"""
Unit tests for the AI Core models module.

These tests validate the functionality of the models module
in the AI Core, including the ModelManager class.
"""
import pytest
from unittest.mock import MagicMock, patch
import os

from ai_core.models import ModelManager

@pytest.mark.unit
@pytest.mark.ai_core
class TestModelManager:
    """Test cases for the ModelManager class."""

    def test_init(self):
        """Test initialization of ModelManager."""
        manager = ModelManager()
        assert manager is not None
        assert manager.loaded_models == {}

    def test_init_with_config(self):
        """Test initialization with configuration."""
        config = {"models": {"load_on_startup": ["model1", "model2"]}}
        manager = ModelManager(config)
        assert manager.config == config

    @patch("ai_core.models.MODEL_LOADER_AVAILABLE", True)
    @patch("ai_core.models.ModelLoader")
    def test_init_model_loader(self, mock_loader):
        """Test initialization with model loader available."""
        mock_loader.return_value = MagicMock()
        manager = ModelManager()
        assert manager._model_loader is not None

    def test_load_model_already_loaded(self):
        """Test loading a model that's already loaded."""
        manager = ModelManager()
        mock_model = MagicMock()
        manager.loaded_models["test-model"] = mock_model

        result = manager.load_model("test-model")

        assert result is mock_model

    @patch("ai_core.models.MODEL_LOADER_AVAILABLE", True)
    def test_load_model_with_loader(self):
        """Test loading a model using the model loader."""
        manager = ModelManager()
        manager._model_loader = MagicMock()
        mock_model = MagicMock()
        manager._model_loader.load_model.return_value = mock_model

        result = manager.load_model("test-model", "/path/to/model")

        assert result is mock_model
        assert manager.loaded_models["test-model"] is mock_model
        manager._model_loader.load_model.assert_called_once_with("/path/to/model")

    @patch("ai_core.models.MODEL_LOADER_AVAILABLE", True)
    def test_load_model_failure(self):
        """Test handling of model loading failure."""
        manager = ModelManager()
        manager._model_loader = MagicMock()
        manager._model_loader.load_model.return_value = None

        result = manager.load_model("test-model", "/path/to/model")

        assert result is None
        assert "test-model" not in manager.loaded_models

    @patch("ai_core.models.MODEL_LOADER_AVAILABLE", True)
    def test_load_model_exception(self):
        """Test handling of exceptions during model loading."""
        manager = ModelManager()
        manager._model_loader = MagicMock()
        manager._model_loader.load_model.side_effect = Exception("Loading error")

        result = manager.load_model("test-model", "/path/to/model")

        assert result is None
        assert "test-model" not in manager.loaded_models

    def test_unload_model_success(self):
        """Test successful model unloading."""
        manager = ModelManager()
        mock_model = MagicMock()
        manager.loaded_models["test-model"] = mock_model

        result = manager.unload_model("test-model")

        assert result is True
        assert "test-model" not in manager.loaded_models

    def test_unload_model_not_loaded(self):
        """Test unloading a model that's not loaded."""
        manager = ModelManager()

        result = manager.unload_model("test-model")

        assert result is False

    def test_unload_model_exception(self):
        """Test handling of exceptions during model unloading."""
        manager = ModelManager()
        mock_model = MagicMock()
        manager.loaded_models["test-model"] = mock_model

        # Set up a side effect when deleting the model
        delattr_mock = MagicMock(side_effect=Exception("Unloading error"))
        manager.loaded_models.__delitem__ = delattr_mock

        result = manager.unload_model("test-model")

        assert result is False

    def test_get_model(self):
        """Test getting a loaded model."""
        manager = ModelManager()
        mock_model = MagicMock()
        manager.loaded_models["test-model"] = mock_model

        result = manager.get_model("test-model")

        assert result is mock_model

    def test_get_model_not_found(self):
        """Test getting a model that's not loaded."""
        manager = ModelManager()

        result = manager.get_model("test-model")

        assert result is None

    def test_list_models(self):
        """Test listing loaded models."""
        manager = ModelManager()
        manager.loaded_models = {
            "model1": MagicMock(),
            "model2": MagicMock(),
            "model3": MagicMock()
        }

        result = manager.list_models()

        assert set(result) == {"model1", "model2", "model3"}

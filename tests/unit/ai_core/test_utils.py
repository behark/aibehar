"""
Unit tests for the AI Core utils module.

These tests validate the functionality of the utils module
in the AI Core, including the AIUtils class.
"""
import pytest
from unittest.mock import MagicMock, patch, mock_open
import os
import json
from pathlib import Path

from ai_core.utils import AIUtils

@pytest.mark.unit
@pytest.mark.ai_core
class TestAIUtils:
    """Test cases for the AIUtils class."""

    def test_format_error_response(self):
        """Test formatting of error responses."""
        response = AIUtils.format_error_response(
            error_message="Test error",
            error_type="test_error",
            context={"test": "context"}
        )

        assert response["error"] is True
        assert response["error_type"] == "test_error"
        assert response["error_message"] == "Test error"
        assert response["context"] == {"test": "context"}

    def test_format_error_response_default_values(self):
        """Test formatting of error responses with default values."""
        response = AIUtils.format_error_response("Test error")

        assert response["error"] is True
        assert response["error_type"] == "processing_error"
        assert response["error_message"] == "Test error"
        assert response["context"] == {}

    def test_validate_model_config_valid(self):
        """Test validation of a valid model configuration."""
        config = {
            "id": "test-model",
            "name": "Test Model",
            "type": "text"
        }

        errors = AIUtils.validate_model_config(config)

        assert errors == []

    def test_validate_model_config_missing_fields(self):
        """Test validation of a model configuration with missing fields."""
        config = {
            "id": "test-model",
            "name": "Test Model"
            # Missing "type" field
        }

        errors = AIUtils.validate_model_config(config)

        assert len(errors) == 1
        assert "Missing required field: type" in errors

    def test_validate_model_config_invalid_type(self):
        """Test validation of a model configuration with an invalid type."""
        config = {
            "id": "test-model",
            "name": "Test Model",
            "type": "invalid_type"  # Not a valid type
        }

        errors = AIUtils.validate_model_config(config)

        assert len(errors) == 1
        assert "Invalid model type: invalid_type" in errors

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_model_metadata(self, mock_json_dump, mock_file_open, mock_makedirs):
        """Test saving model metadata."""
        metadata = {
            "name": "Test Model",
            "description": "A test model",
            "parameters": 1000000
        }

        result = AIUtils.save_model_metadata("test-model", metadata)

        assert result is True
        mock_makedirs.assert_called_once()
        mock_file_open.assert_called_once()
        mock_json_dump.assert_called_once_with(metadata, mock_file_open(), indent=2)

    @patch("os.makedirs")
    @patch("builtins.open", side_effect=Exception("File error"))
    def test_save_model_metadata_exception(self, mock_file_open, mock_makedirs):
        """Test exception handling when saving model metadata."""
        metadata = {"name": "Test Model"}

        result = AIUtils.save_model_metadata("test-model", metadata)

        assert result is False

    @patch("builtins.open", new_callable=mock_open, read_data='{"name": "Test Model"}')
    @patch("pathlib.Path.exists", return_value=True)
    @patch("json.load", return_value={"name": "Test Model"})
    def test_load_model_metadata(self, mock_json_load, mock_path_exists, mock_file_open):
        """Test loading model metadata."""
        metadata = AIUtils.load_model_metadata("test-model")

        assert metadata == {"name": "Test Model"}
        mock_path_exists.assert_called_once()
        mock_file_open.assert_called_once()
        mock_json_load.assert_called_once_with(mock_file_open())

    @patch("pathlib.Path.exists", return_value=False)
    def test_load_model_metadata_not_found(self, mock_path_exists):
        """Test loading model metadata when the file doesn't exist."""
        metadata = AIUtils.load_model_metadata("test-model")

        assert metadata is None
        mock_path_exists.assert_called_once()

    @patch("builtins.open", side_effect=Exception("File error"))
    @patch("pathlib.Path.exists", return_value=True)
    def test_load_model_metadata_exception(self, mock_path_exists, mock_file_open):
        """Test exception handling when loading model metadata."""
        metadata = AIUtils.load_model_metadata("test-model")

        assert metadata is None

"""
Unit tests for the AI Core generation module.

These tests validate the functionality of the generation module
in the AI Core, including the ResponseGenerator class.
"""
import pytest
from unittest.mock import MagicMock, patch
import asyncio

from ai_core.generation import ResponseGenerator

@pytest.mark.unit
@pytest.mark.ai_core
class TestResponseGenerator:
    """Test cases for the ResponseGenerator class."""

    def test_init(self):
        """Test initialization of ResponseGenerator."""
        generator = ResponseGenerator()
        assert generator is not None
        assert generator._text_generation is None
        assert generator._professional_engine is None

    def test_init_with_config(self):
        """Test initialization with configuration."""
        config = {"generation": {"default_parameters": {"temperature": 0.7}}}
        generator = ResponseGenerator(config)
        assert generator.config == config

    @patch("ai_core.generation.TEXT_GENERATION_AVAILABLE", True)
    @patch("ai_core.generation.TextGenerationBackend")
    def test_init_text_generation(self, mock_text_gen):
        """Test initialization with text generation available."""
        mock_text_gen.return_value = MagicMock()
        generator = ResponseGenerator()
        assert generator._text_generation is not None

    @patch("ai_core.generation.PROFESSIONAL_ENGINE_AVAILABLE", True)
    @patch("ai_core.generation.ProfessionalResponseEngine")
    def test_init_professional_engine(self, mock_engine):
        """Test initialization with professional engine available."""
        mock_engine.return_value = MagicMock()
        generator = ResponseGenerator()
        assert generator._professional_engine is not None

    @pytest.mark.asyncio
    async def test_generate_response_fallback(self):
        """Test fallback response generation."""
        generator = ResponseGenerator()
        generator._text_generation = None
        generator._professional_engine = None

        response = await generator.generate_response("Test prompt")

        assert "text" in response
        assert "model_id" in response
        assert "metadata" in response
        assert response["metadata"]["generation_method"] == "fallback"

    @pytest.mark.asyncio
    @patch("ai_core.generation.TEXT_GENERATION_AVAILABLE", True)
    async def test_generate_response_with_text_generation(self):
        """Test response generation with text generation backend."""
        generator = ResponseGenerator()
        generator._text_generation = MagicMock()
        generator._professional_engine = None

        # Set up the mock to return a response
        mock_response = MagicMock()
        mock_response.text = "Generated text"
        generator._text_generation.generate = MagicMock(return_value=asyncio.Future())
        generator._text_generation.generate.return_value.set_result(mock_response)

        response = await generator.generate_response(
            prompt="Test prompt",
            model_id="test-model",
            parameters={"temperature": 0.7}
        )

        assert response["text"] == "Generated text"
        assert response["model_id"] == "test-model"
        assert response["metadata"]["generation_method"] == "text_generation"

        # Verify the text generation was called with correct arguments
        generator._text_generation.generate.assert_called_with(
            prompt="Test prompt",
            model="test-model",
            temperature=0.7
        )

    @pytest.mark.asyncio
    @patch("ai_core.generation.TEXT_GENERATION_AVAILABLE", True)
    async def test_generate_response_with_exception(self):
        """Test exception handling during response generation."""
        generator = ResponseGenerator()
        generator._text_generation = MagicMock()
        generator._professional_engine = None

        # Set up the mock to raise an exception
        future = asyncio.Future()
        future.set_exception(Exception("Generation error"))
        generator._text_generation.generate = MagicMock(return_value=future)

        response = await generator.generate_response("Test prompt")

        # Should still return a response with the fallback method
        assert "text" in response
        assert "model_id" in response
        assert response["metadata"]["generation_method"] == "fallback"

    @pytest.mark.asyncio
    @patch("ai_core.generation.TEXT_GENERATION_AVAILABLE", True)
    @patch("ai_core.generation.PROFESSIONAL_ENGINE_AVAILABLE", True)
    async def test_generate_response_with_transformation(self):
        """Test response generation with professional transformation."""
        generator = ResponseGenerator()
        generator._text_generation = MagicMock()
        generator._professional_engine = MagicMock()

        # Set up the text generation mock
        mock_response = MagicMock()
        mock_response.text = "Generated text"
        generator._text_generation.generate = MagicMock(return_value=asyncio.Future())
        generator._text_generation.generate.return_value.set_result(mock_response)

        # Set up the professional engine mock
        transformed_response = MagicMock()
        transformed_response.text = "Professionally transformed text"
        generator._professional_engine.transform_response.return_value = transformed_response

        response = await generator.generate_response(
            prompt="Test prompt",
            model_id="test-model",
            context={"user_expertise": "beginner"},
            parameters={"tone": "formal", "style": "educational"}
        )

        assert response["text"] == "Professionally transformed text"
        assert "transformation_applied" in response["metadata"]
        assert response["metadata"]["transformation_applied"] is True

        # Verify the professional engine was called with correct arguments
        generator._professional_engine.transform_response.assert_called_once()

    def test_get_available_models_empty(self):
        """Test getting available models when none are available."""
        generator = ResponseGenerator()
        generator._text_generation = None

        models = generator.get_available_models()

        assert models == []

    @patch("ai_core.generation.TEXT_GENERATION_AVAILABLE", True)
    def test_get_available_models(self):
        """Test getting available models."""
        generator = ResponseGenerator()
        generator._text_generation = MagicMock()
        generator._text_generation.list_models.return_value = ["model1", "model2"]

        models = generator.get_available_models()

        assert len(models) == 2
        assert models[0]["id"] == "model1"
        assert models[0]["source"] == "text_generation"
        assert models[1]["id"] == "model2"
        assert models[1]["source"] == "text_generation"

    @patch("ai_core.generation.TEXT_GENERATION_AVAILABLE", True)
    def test_get_available_models_exception(self):
        """Test exception handling when getting available models."""
        generator = ResponseGenerator()
        generator._text_generation = MagicMock()
        generator._text_generation.list_models.side_effect = Exception("Listing error")

        models = generator.get_available_models()

        assert models == []

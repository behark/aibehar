"""
✨ Generation Module

This module provides a unified interface for generating responses using
various AI models and response transformation capabilities.
"""

import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

# Import existing response engines if available
try:
    from ..text_generation import TextGenerationBackend
    TEXT_GENERATION_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Text generation backend not available: {e}")
    TEXT_GENERATION_AVAILABLE = False

try:
    from ..advanced_sovereign.professional_response_engine import (
        ProfessionalResponseEngine,
        ResponseTone,
        PresentationStyle,
        ResponseContext
    )
    PROFESSIONAL_ENGINE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Professional response engine not available: {e}")
    PROFESSIONAL_ENGINE_AVAILABLE = False

class ResponseGenerator:
    """
    Unified response generation system for Open WebUI.

    This class provides a consistent interface for generating responses using
    various AI models and response transformation capabilities. It integrates
    with existing text generation and response engines if available.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the response generator with the specified configuration.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._text_generation = None
        self._professional_engine = None

        # Initialize generation components
        self._init_generation_components()

    def _init_generation_components(self):
        """Initialize available generation components."""
        if TEXT_GENERATION_AVAILABLE:
            try:
                self._text_generation = TextGenerationBackend()
                logger.info("Text generation backend initialized")
            except Exception as e:
                logger.error(f"Failed to initialize text generation backend: {e}")

        if PROFESSIONAL_ENGINE_AVAILABLE:
            try:
                self._professional_engine = ProfessionalResponseEngine()
                logger.info("Professional response engine initialized")
            except Exception as e:
                logger.error(f"Failed to initialize professional response engine: {e}")

    async def generate_response(self, prompt: str, model_id: Optional[str] = None,
                          context: Optional[Dict[str, Any]] = None,
                          parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response for the given prompt using the appropriate model.

        Args:
            prompt: The prompt text
            model_id: Optional model ID to use
            context: Optional context information
            parameters: Optional generation parameters

        Returns:
            A dictionary containing the generated response and metadata
        """
        context = context or {}
        parameters = parameters or {}

        # Basic response in case no generators are available
        response_data = {
            "text": f"Response to: {prompt[:50]}...",
            "model_id": model_id,
            "metadata": {"generation_method": "fallback"}
        }

        # Use text generation backend if available
        if self._text_generation is not None:
            try:
                # Adapt to the text generation backend's interface
                raw_response = await self._text_generation.generate(
                    prompt=prompt,
                    model=model_id,
                    **parameters
                )

                response_data = {
                    "text": raw_response.text if hasattr(raw_response, 'text') else str(raw_response),
                    "model_id": model_id,
                    "metadata": {"generation_method": "text_generation"}
                }
            except Exception as e:
                logger.error(f"Text generation failed: {e}")

        # Apply professional response transformations if available
        if self._professional_engine is not None and response_data.get("text"):
            try:
                # Create response context
                response_context = ResponseContext(
                    original_prompt=prompt,
                    original_response=response_data["text"],
                    user_context=context
                )

                # Apply professional transformations
                transformed_response = self._professional_engine.transform_response(
                    response_context,
                    tone=parameters.get("tone"),
                    style=parameters.get("style")
                )

                response_data["text"] = transformed_response.text
                response_data["metadata"]["transformation_applied"] = True
            except Exception as e:
                logger.error(f"Professional transformation failed: {e}")

        return response_data

    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available models for response generation.

        Returns:
            A list of dictionaries containing model information
        """
        models = []

        # Get models from text generation backend if available
        if self._text_generation is not None:
            try:
                backend_models = self._text_generation.list_models()
                models.extend([
                    {"id": model_id, "source": "text_generation"}
                    for model_id in backend_models
                ])
            except Exception as e:
                logger.error(f"Failed to list text generation models: {e}")

        return models

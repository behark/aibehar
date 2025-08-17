"""
🚀 Models Module

This module provides a unified interface for managing and loading
different types of AI models in Open WebUI.
"""

import logging
import os
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

# Import existing model loader if available
try:
    from ..model_loader import ModelLoader
    MODEL_LOADER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Model loader not available: {e}")
    MODEL_LOADER_AVAILABLE = False

class ModelManager:
    """
    Unified model management system for Open WebUI.

    This class provides a consistent interface for loading and managing
    different types of AI models, regardless of the underlying implementation.
    It integrates with the existing ModelLoader if available.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the model manager with the specified configuration.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._model_loader = None
        self.loaded_models = {}

        # Initialize model loader if available
        self._init_model_loader()

    def _init_model_loader(self):
        """Initialize the model loader if available."""
        if MODEL_LOADER_AVAILABLE:
            try:
                self._model_loader = ModelLoader()
                logger.info("Model loader initialized")
            except Exception as e:
                logger.error(f"Failed to initialize model loader: {e}")

    def load_model(self, model_id: str, model_path: Optional[str] = None,
                   model_type: Optional[str] = None, **kwargs) -> Any:
        """
        Load a model with the specified ID and parameters.

        Args:
            model_id: The unique identifier for the model
            model_path: Optional path to the model file
            model_type: Optional type of the model
            **kwargs: Additional model-specific parameters

        Returns:
            The loaded model or None if loading fails
        """
        # Check if model is already loaded
        if model_id in self.loaded_models:
            logger.info(f"Model '{model_id}' already loaded")
            return self.loaded_models[model_id]

        # Use model loader if available
        if self._model_loader is not None:
            try:
                if model_path:
                    model = self._model_loader.load_model(model_path, **kwargs)
                    if model:
                        self.loaded_models[model_id] = model
                        logger.info(f"Model '{model_id}' loaded successfully")
                        return model
            except Exception as e:
                logger.error(f"Failed to load model '{model_id}': {e}")

        logger.warning(f"Model '{model_id}' could not be loaded")
        return None

    def unload_model(self, model_id: str) -> bool:
        """
        Unload a model with the specified ID.

        Args:
            model_id: The unique identifier for the model

        Returns:
            True if the model was unloaded successfully, False otherwise
        """
        if model_id in self.loaded_models:
            try:
                # Model-specific cleanup if needed
                del self.loaded_models[model_id]
                logger.info(f"Model '{model_id}' unloaded successfully")
                return True
            except Exception as e:
                logger.error(f"Failed to unload model '{model_id}': {e}")

        return False

    def get_model(self, model_id: str) -> Optional[Any]:
        """
        Get a loaded model by ID.

        Args:
            model_id: The unique identifier for the model

        Returns:
            The loaded model or None if not found
        """
        return self.loaded_models.get(model_id)

    def list_models(self) -> List[str]:
        """
        List all loaded models.

        Returns:
            A list of model IDs
        """
        return list(self.loaded_models.keys())

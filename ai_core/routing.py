"""
🚀 Routing Module

This module provides a unified interface for routing requests to the
appropriate AI models based on query context and model capabilities.
"""

import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

# Import existing router if available
try:
    from ..advanced_sovereign.multi_model_router import (
        MultiModelIntelligenceRouter,
        ModelCapability,
        QueryContext,
        ModelResponse
    )
    ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Multi-model router not available: {e}")
    ROUTER_AVAILABLE = False

class ModelRouter:
    """
    Unified model routing system for Open WebUI.

    This class provides a consistent interface for routing requests to the
    appropriate AI models based on the query context and model capabilities.
    It integrates with the existing MultiModelIntelligenceRouter if available.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the model router with the specified configuration.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self._router = None

        # Initialize router if available
        self._init_router()

    def _init_router(self):
        """Initialize the multi-model router if available."""
        if ROUTER_AVAILABLE:
            try:
                self._router = MultiModelIntelligenceRouter()
                logger.info("Multi-model router initialized")
            except Exception as e:
                logger.error(f"Failed to initialize multi-model router: {e}")

    def route_query(self, query: str, context: Optional[Dict[str, Any]] = None,
                   available_models: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Route a query to the appropriate model based on the context.

        Args:
            query: The query text
            context: Optional context information
            available_models: Optional list of available model IDs

        Returns:
            A dictionary containing the selected model ID and routing metadata
        """
        context = context or {}
        available_models = available_models or []

        # Use advanced router if available
        if self._router is not None:
            try:
                # Prepare the query context for the router
                query_context = QueryContext(
                    query=query,
                    metadata=context
                )

                # Route the query
                result = self._router.route_query(query_context, available_models)

                return {
                    "model_id": result.selected_model,
                    "confidence": result.confidence,
                    "metadata": result.metadata
                }
            except Exception as e:
                logger.error(f"Advanced routing failed: {e}")

        # Simple fallback routing if advanced router is not available
        if available_models:
            # Simple selection of the first available model
            return {
                "model_id": available_models[0],
                "confidence": 1.0,
                "metadata": {"method": "fallback_routing"}
            }

        return {
            "model_id": None,
            "confidence": 0.0,
            "metadata": {"method": "fallback_routing", "error": "No available models"}
        }

    def get_router_status(self) -> Dict[str, Any]:
        """
        Get the current status of the router.

        Returns:
            A dictionary containing the router status
        """
        if self._router is not None:
            try:
                # Get status from advanced router
                return {
                    "available": True,
                    "type": "advanced",
                    "status": "operational"
                }
            except Exception as e:
                logger.error(f"Failed to get router status: {e}")

        return {
            "available": False,
            "type": "fallback",
            "status": "limited_functionality"
        }

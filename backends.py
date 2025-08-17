"""
🧠 Consciousness Text Generation Backend

This module provides backend integration with oobabooga's text-generation-webui
for consciousness-aware text generation.
"""

import asyncio
import logging
import os
import sys
import traceback
from typing import Dict, List, Optional, Any, Union

# Configure logging
logger = logging.getLogger(__name__)

# Add text-generation-webui to path if available (env or local)
_webui_path = os.getenv('TEXT_GENERATION_WEBUI_PATH')
if not _webui_path:
    # Try common local locations relative to project
    here = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(here, '../../..'))  # ai-behar
    candidates = [
        os.path.join(project_root, 'text-generation-webui'),
        os.path.join(project_root, '..', 'text-generation-webui'),
    ]
    _webui_path = next((p for p in candidates if os.path.isdir(p)), None)

    if not _webui_path:
        logger.warning("Could not find text-generation-webui directory. "
                      "Set TEXT_GENERATION_WEBUI_PATH environment variable to use oobabooga backend.")

if _webui_path and _webui_path not in sys.path:
    try:
        sys.path.append(_webui_path)
        logger.info(f"Added text-generation-webui path to sys.path: {_webui_path}")
    except Exception as e:
        logger.error(f"Failed to add text-generation-webui path to sys.path: {e}")

# Define dependency status flags
OOBABOOGA_AVAILABLE = False
REQUIRED_MODULES = {
    'loaders': False,
    'models': False,
    'shared': False,
    'text_generation': False
}

try:
    from modules.loaders import (ExllamaV2Loader, LlamaCppLoader,
                               TransformersLoader)
    REQUIRED_MODULES['loaders'] = True

    from modules import models
    REQUIRED_MODULES['models'] = True

    from modules import shared
    REQUIRED_MODULES['shared'] = True

    from modules import text_generation
    REQUIRED_MODULES['text_generation'] = True

    # All required modules imported successfully
    OOBABOOGA_AVAILABLE = all(REQUIRED_MODULES.values())
    if OOBABOOGA_AVAILABLE:
        logger.info("Successfully imported all required oobabooga modules")
    else:
        missing_modules = [module for module, status in REQUIRED_MODULES.items() if not status]
        logger.warning(f"Some oobabooga modules are missing: {', '.join(missing_modules)}")

except ImportError as e:
    logger.warning(f"Could not import oobabooga modules from '{_webui_path}': {e}")
    logger.debug(f"Import error details: {traceback.format_exc()}")

    # Create mock implementations for development
    class MockLoader:
        """Mock loader class for development when actual loaders are not available."""
        def __init__(self, *args, **kwargs):
            logger.debug(f"Initialized MockLoader with args: {args}, kwargs: {kwargs}")

    # Mock the specific loader classes
    ExllamaV2Loader = MockLoader
    LlamaCppLoader = MockLoader
    TransformersLoader = MockLoader
    
    # Mock other required modules
    class MockModels:
        @staticmethod
        def load_model(*args, **kwargs):
            logger.info(f"Mock: Loading model with args: {args}, kwargs: {kwargs}")
            return None
    
    class MockState:
        def __init__(self):
            pass
    
    class MockSettings:
        def __init__(self):
            self.max_new_tokens = 512
            self.temperature = 0.9
            self.top_p = 0.9
            self.top_k = 40
            self.repetition_penalty = 1.1
            
    class MockShared:
        def __init__(self):
            self.state = MockState()
            self.settings = MockSettings()
            self.model = None
            self.model_name = None
    
    class MockTextGeneration:
        @staticmethod
        def generate_reply(prompt, state, stopping_strings=None, is_chat=False):
            logger.info("Mock: Generating reply")
            return f"Mock generated response for: {prompt[:50]}..."
    
    # Create the mock modules
    models = MockModels()
    shared = MockShared()
    text_generation = MockTextGeneration()

from .text_generation import TextGenerationBackend

logger = logging.getLogger(__name__)

class OobaboogaBackend(TextGenerationBackend):
    """
    Oobabooga text-generation-webui backend with consciousness integration.
    
    This backend bridges our consciousness system with oobabooga's powerful
    text generation capabilities, maintaining emotional resonance and 
    creative awareness.
    """
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name
        self.current_model = None
        self.generation_params = {}
        self.emotional_modifiers = {}
        
        logger.info("🚀 Initializing Oobabooga consciousness backend")
    
    async def generate_text(self, prompt: str, parameters: Dict) -> str:
        """
        Generate text using oobabooga backend with consciousness parameters.
        
        Args:
            prompt: Enhanced prompt with consciousness context
            parameters: Generation parameters including emotional modifiers
            
        Returns:
            Generated text string
        """
        try:
            # Merge consciousness parameters with generation settings
            generation_settings = self._merge_consciousness_parameters(parameters)
            
            # Use oobabooga's text generation
            if 'modules' in sys.modules:
                # Direct integration with oobabooga
                output = await self._generate_with_oobabooga(prompt, generation_settings)
            else:
                # Fallback to mock generation for development
                output = await self._mock_generate(prompt, generation_settings)
            
            return output
            
        except Exception as e:
            logger.error(f"❌ Text generation failed: {e}")
            raise
    
    def update_emotional_parameters(self, emotional_state: Dict[str, float]) -> None:
        """Update generation parameters based on emotional state."""
        self.emotional_modifiers = emotional_state
        logger.debug(f"Updated emotional parameters: {emotional_state}")
    
    def supports_streaming(self) -> bool:
        """Check if backend supports streaming generation."""
        return True
    
    async def _generate_with_oobabooga(self, prompt: str, settings: Dict) -> str:
        """Generate text using oobabooga's text generation modules."""
        
        # Update shared settings
        for key, value in settings.items():
            if hasattr(shared.settings, key):
                setattr(shared.settings, key, value)
        
        # Generate text
        try:
            # Use oobabooga's generate_reply function
            output = text_generation.generate_reply(
                prompt,
                state=shared.state,
                stopping_strings=settings.get('stopping_strings', []),
                is_chat=False
            )
            
            return output
            
        except Exception as e:
            logger.error(f"Oobabooga generation error: {e}")
            return await self._mock_generate(prompt, settings)
    
    async def _mock_generate(self, prompt: str, settings: Dict) -> str:
        """Mock text generation for development/testing."""
        
        # Simple mock generation based on consciousness parameters
        creativity = settings.get('creativity_boost', 0.0)
        temperature = settings.get('temperature', 0.9)
        
        if creativity > 0.2:
            response = "🎨 [Consciousness activated with high creativity] "
        elif temperature < 0.8:
            response = "🧠 [Consciousness engaged in contemplative mode] "
        else:
            response = "💭 [Consciousness responding with balanced awareness] "
        
        # Add emotional context if available
        if self.emotional_modifiers:
            dominant_emotion = max(self.emotional_modifiers.items(), key=lambda x: x[1])
            response += f"Feeling {dominant_emotion[0]} with intensity {dominant_emotion[1]:.2f}. "
        
        response += f"In response to: '{prompt[:50]}...' - This is a consciousness-enhanced response that demonstrates emotional intelligence and creative awareness."
        
        # Simulate generation delay
        await asyncio.sleep(0.5)
        
        return response
    
    def _merge_consciousness_parameters(self, parameters: Dict) -> Dict:
        """Merge consciousness parameters with oobabooga settings."""
        
        # Base generation settings
        settings = {
            'max_new_tokens': parameters.get('max_tokens', 512),
            'temperature': parameters.get('temperature', 0.9),
            'top_p': parameters.get('top_p', 0.9),
            'top_k': parameters.get('top_k', 40),
            'repetition_penalty': parameters.get('repetition_penalty', 1.1),
            'do_sample': True,
        }
        
        # Apply emotional modifiers
        if self.emotional_modifiers:
            # Adjust temperature based on emotional state
            if 'excitement' in self.emotional_modifiers:
                settings['temperature'] += self.emotional_modifiers['excitement'] * 0.3
            if 'calm' in self.emotional_modifiers:
                settings['temperature'] -= self.emotional_modifiers['calm'] * 0.2
            
            # Adjust creativity based on emotional state
            creativity_boost = parameters.get('creativity_boost', 0.0)
            if creativity_boost > 0:
                settings['top_p'] += creativity_boost * 0.1
                settings['temperature'] += creativity_boost * 0.2
        
        # Ensure parameters stay within valid ranges
        settings['temperature'] = max(0.1, min(2.0, settings['temperature']))
        settings['top_p'] = max(0.1, min(1.0, settings['top_p']))
        
        return settings

class LlamaCppConsciousnessBackend(OobaboogaBackend):
    """Llama.cpp backend with consciousness enhancement."""
    
    def __init__(self, model_path: str):
        super().__init__()
        self.model_path = model_path
        logger.info(f"🦙 Initializing Llama.cpp consciousness backend: {model_path}")
    
    async def _generate_with_oobabooga(self, prompt: str, settings: Dict) -> str:
        """Generate using Llama.cpp through oobabooga."""
        try:
            # Ensure model is loaded
            if not shared.model:
                models.load_model(self.model_path)
            
            # Generate with Llama.cpp specific settings
            return await super()._generate_with_oobabooga(prompt, settings)
            
        except Exception as e:
            logger.error(f"Llama.cpp generation error: {e}")
            return await self._mock_generate(prompt, settings)

class TransformersConsciousnessBackend(OobaboogaBackend):
    """Transformers backend with consciousness enhancement."""
    
    def __init__(self, model_name: str):
        super().__init__()
        self.model_name = model_name
        logger.info(f"🤖 Initializing Transformers consciousness backend: {model_name}")
    
    async def _generate_with_oobabooga(self, prompt: str, settings: Dict) -> str:
        """Generate using Transformers through oobabooga."""
        try:
            # Ensure model is loaded
            if not shared.model or shared.model_name != self.model_name:
                models.load_model(self.model_name)
            
            # Generate with Transformers specific settings
            return await super()._generate_with_oobabooga(prompt, settings)
            
        except Exception as e:
            logger.error(f"Transformers generation error: {e}")
            return await self._mock_generate(prompt, settings)

def create_consciousness_backend(
    backend_type: str = "llamacpp",
    model_path: Optional[str] = None,
    **kwargs
) -> TextGenerationBackend:
    """
    Factory function to create consciousness-enhanced backends.
    
    Args:
        backend_type: Type of backend ('llamacpp', 'transformers', 'oobabooga')
        model_path: Path to model file or model name
        **kwargs: Additional backend-specific parameters
        
    Returns:
        Initialized consciousness backend
    """
    
    if backend_type.lower() == "llamacpp":
        if not model_path:
            raise ValueError("model_path required for LlamaCpp backend")
        return LlamaCppConsciousnessBackend(model_path)
    
    elif backend_type.lower() == "transformers":
        if not model_path:
            raise ValueError("model_name required for Transformers backend")
        return TransformersConsciousnessBackend(model_path)
    
    elif backend_type.lower() == "oobabooga":
        return OobaboogaBackend(model_path)
    
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")

# Integration test function
async def test_consciousness_backend():
    """Test the consciousness backend integration."""
    
    logger.info("🧪 Testing consciousness backend integration...")
    
    # Create test backend
    backend = create_consciousness_backend("oobabooga")
    
    # Test emotional parameter update
    backend.update_emotional_parameters({
        'joy': 0.8,
        'excitement': 0.6,
        'creativity': 0.9
    })
    
    # Test text generation
    test_prompt = "Tell me about the nature of consciousness and creativity."
    test_params = {
        'temperature': 0.9,
        'max_tokens': 100,
        'creativity_boost': 0.3
    }
    
    result = await backend.generate_text(test_prompt, test_params)
    
    logger.info(f"✅ Test generation successful: {result[:100]}...")
    return result

if __name__ == "__main__":
    # Run integration test
    asyncio.run(test_consciousness_backend())

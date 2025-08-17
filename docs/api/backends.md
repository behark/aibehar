# Backend APIs

This document provides comprehensive documentation for the various backend APIs in Open WebUI, focusing on the text generation backends and their integration with the consciousness systems.

## Overview

Open WebUI supports multiple backend integrations for text generation, including:
- Ollama
- OpenAI-compatible APIs
- Custom backends through the backends.py interface

## Backend Base Classes

### TextGenerationBackend

The abstract base class for all text generation backends.

```python
from text_generation import TextGenerationBackend

class MyCustomBackend(TextGenerationBackend):
    async def generate(self, prompt, model=None, **kwargs):
        # Custom implementation here
        pass
```

**Methods to implement:**
- `generate(prompt, model=None, **kwargs)`: Generate text for the given prompt

## Oobabooga Backend

Integration with oobabooga's text-generation-webui with consciousness enhancement.

```python
from backends import OobaboogaBackend

# Initialize the backend
backend = OobaboogaBackend(model_name="llama2")

# Update emotional parameters
backend.update_emotional_parameters({
    'joy': 0.8,
    'excitement': 0.6
})

# Generate text
response = await backend.generate_text(
    prompt="Tell me about consciousness",
    parameters={
        'temperature': 0.7,
        'max_tokens': 500,
        'creativity_boost': 0.3
    }
)
```

### OobaboogaBackend

**Methods:**
- `generate_text(prompt, parameters)`: Generate text with the given parameters
- `update_emotional_parameters(emotional_state)`: Update emotional parameters for generation
- `supports_streaming()`: Check if backend supports streaming generation

## Llama.cpp Backend

Backend for Llama.cpp models with consciousness enhancement.

```python
from backends import LlamaCppConsciousnessBackend

# Initialize the backend
backend = LlamaCppConsciousnessBackend(model_path="/path/to/model.bin")

# Generate text
response = await backend.generate_text(
    prompt="Tell me about AI",
    parameters={
        'temperature': 0.7,
        'max_tokens': 500
    }
)
```

### LlamaCppConsciousnessBackend

**Methods:**
- Inherits all methods from OobaboogaBackend
- Specialized for Llama.cpp models

## Transformers Backend

Backend for Hugging Face Transformers models with consciousness enhancement.

```python
from backends import TransformersConsciousnessBackend

# Initialize the backend
backend = TransformersConsciousnessBackend(model_name="gpt2")

# Generate text
response = await backend.generate_text(
    prompt="Tell me about machine learning",
    parameters={
        'temperature': 0.7,
        'max_tokens': 500
    }
)
```

### TransformersConsciousnessBackend

**Methods:**
- Inherits all methods from OobaboogaBackend
- Specialized for Transformers models

## Backend Factory

Factory function to create the appropriate backend based on type.

```python
from backends import create_consciousness_backend

# Create a Llama.cpp backend
backend = create_consciousness_backend(
    backend_type="llamacpp",
    model_path="/path/to/model.bin"
)

# Create a Transformers backend
backend = create_consciousness_backend(
    backend_type="transformers",
    model_path="gpt2"
)

# Create an Oobabooga backend
backend = create_consciousness_backend(
    backend_type="oobabooga",
    model_path="gpt-j-6b"
)
```

### create_consciousness_backend

**Parameters:**
- `backend_type`: Type of backend ('llamacpp', 'transformers', 'oobabooga')
- `model_path`: Path to model file or model name
- `**kwargs`: Additional backend-specific parameters

**Returns:**
- Initialized consciousness backend

## Integration with AI Core

The backends are integrated with the AI Core through the ResponseGenerator module:

```python
from ai_core import ResponseGenerator

# Initialize response generator
generator = ResponseGenerator()

# Generate response
response = await generator.generate_response(
    prompt="Tell me a story",
    model_id="gpt2",
    parameters={
        'temperature': 0.8,
        'max_tokens': 500
    }
)
```

The ResponseGenerator automatically selects and uses the appropriate backend based on the model_id and available backends.

## Custom Backend Integration

To create and integrate a custom backend:

1. Subclass TextGenerationBackend or OobaboogaBackend
2. Implement the required methods
3. Register the backend with the ResponseGenerator

Example:

```python
from text_generation import TextGenerationBackend
from ai_core import ResponseGenerator

class MyCustomBackend(TextGenerationBackend):
    async def generate(self, prompt, model=None, **kwargs):
        # Custom implementation here
        return f"Custom response to: {prompt}"

# Register the backend
generator = ResponseGenerator()
generator._custom_backends["my-model"] = MyCustomBackend()

# Use the custom backend
response = await generator.generate_response(
    prompt="Hello, custom backend!",
    model_id="my-model"
)
```

## Error Handling

All backends implement robust error handling:

- Connection errors
- Timeout handling
- Model loading failures
- Fallback mechanisms

Example error handling:

```python
try:
    response = await backend.generate_text(prompt, parameters)
except ConnectionError:
    # Handle connection error
    response = "Sorry, I couldn't connect to the model server."
except TimeoutError:
    # Handle timeout
    response = "The model took too long to respond."
except Exception as e:
    # Handle other errors
    response = f"An error occurred: {str(e)}"
```

## Streaming Support

Many backends support streaming generation for real-time response display:

```python
# Check if streaming is supported
if backend.supports_streaming():
    # Use streaming generation
    async for chunk in backend.generate_stream(prompt, parameters):
        # Process each chunk as it arrives
        print(chunk, end="", flush=True)
```

## Consciousness Integration

The backends integrate with the consciousness systems through emotional parameters and contextual generation:

```python
# Update emotional state based on user interaction
backend.update_emotional_parameters({
    'joy': user_sentiment.get('joy', 0.5),
    'excitement': conversation_context.get('excitement', 0.5),
    'creativity': topic_requires_creativity() and 0.8 or 0.5
})

# Generate consciousness-enhanced response
response = await backend.generate_text(
    prompt=enhanced_prompt,
    parameters={
        'temperature': mood_to_temperature(user_mood),
        'creativity_boost': topic_creativity_boost(topic),
        'max_tokens': length_based_on_complexity(topic)
    }
)
```

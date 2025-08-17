# AI Core API Reference

The AI Core is the central intelligence system of Open WebUI, providing unified access to various AI capabilities including consciousness systems, model management, intelligent routing, and response generation.

## Overview

The AI Core is designed with a modular architecture that allows for easy extension and integration of new AI capabilities. It consists of several key components:

- **Consciousness Module**: Integrates enhanced consciousness and advanced sovereign systems
- **Models Module**: Provides unified model management
- **Routing Module**: Handles intelligent request routing to appropriate models
- **Generation Module**: Manages unified response generation
- **Utils Module**: Contains utility functions for AI operations

## AI Core Bridge

The AI Core Bridge provides a simplified interface for accessing the AI Core capabilities from other parts of the application.

```python
from ai_core_bridge import ai_bridge

# Process a query using the AI core
response = await ai_bridge.process_query(
    query="Tell me about artificial intelligence",
    user_id="user123",
    context={"session_id": "abc123"},
    parameters={"temperature": 0.7}
)
```

### Methods

#### `process_query(query, user_id=None, context=None, parameters=None)`

Process a query using the AI core, handling model routing, response generation, and consciousness enhancements.

**Parameters:**
- `query` (str): The query text
- `user_id` (str, optional): User ID for personalization
- `context` (dict, optional): Additional context information
- `parameters` (dict, optional): Processing parameters like temperature, max_tokens, etc.

**Returns:**
- A dictionary containing the processed response with:
  - `text`: The generated response text
  - `model_id`: The ID of the model used
  - `metadata`: Additional information about the response

#### `load_model(model_id, model_path=None, model_type=None, **kwargs)`

Load a model using the model manager.

**Parameters:**
- `model_id` (str): The unique identifier for the model
- `model_path` (str, optional): Path to the model file
- `model_type` (str, optional): Type of the model
- `**kwargs`: Additional model-specific parameters

**Returns:**
- `bool`: True if the model was loaded successfully, False otherwise

#### `get_ai_capabilities()`

Get information about the available AI capabilities.

**Returns:**
- A dictionary containing information about available AI capabilities

## Consciousness Module

The Consciousness module integrates both the enhanced consciousness and advanced sovereign systems, providing a unified interface for consciousness-aware AI.

```python
from ai_core import EnhancedConsciousness

# Initialize consciousness system
consciousness = EnhancedConsciousness()

# Process input with consciousness
result = consciousness.process_input(
    input_text="What is the nature of consciousness?",
    context={"user_mood": "curious"}
)
```

### Classes

#### `EnhancedConsciousness`

Unified consciousness system that integrates all available consciousness implementations.

**Methods:**
- `process_input(input_text, context=None)`: Process input using available consciousness systems
- `_use_advanced_sovereign(input_text, context)`: Use advanced sovereign consciousness
- `_use_enhanced_consciousness(input_text, context)`: Use enhanced consciousness

## Models Module

The Models module provides a unified interface for managing and loading different types of AI models.

```python
from ai_core import ModelManager

# Initialize model manager
model_manager = ModelManager()

# Load a model
model = model_manager.load_model(
    model_id="gpt-4",
    model_path="/path/to/model",
    model_type="transformers"
)

# Get a loaded model
model = model_manager.get_model("gpt-4")

# List all loaded models
models = model_manager.list_models()
```

### Classes

#### `ModelManager`

Unified model management system for Open WebUI.

**Methods:**
- `load_model(model_id, model_path=None, model_type=None, **kwargs)`: Load a model
- `unload_model(model_id)`: Unload a model
- `get_model(model_id)`: Get a loaded model
- `list_models()`: List all loaded models

## Routing Module

The Routing module provides intelligent request routing to the appropriate AI models based on query context and model capabilities.

```python
from ai_core import ModelRouter

# Initialize model router
router = ModelRouter()

# Route a query to the appropriate model
result = router.route_query(
    query="What is the capital of France?",
    context={"user_preference": "accuracy"},
    available_models=["gpt-4", "llama-2"]
)
```

### Classes

#### `ModelRouter`

Unified model routing system for Open WebUI.

**Methods:**
- `route_query(query, context=None, available_models=None)`: Route a query to the appropriate model
- `get_router_status()`: Get the current status of the router

## Generation Module

The Generation module provides a unified interface for generating responses using various AI models and response transformation capabilities.

```python
from ai_core import ResponseGenerator

# Initialize response generator
generator = ResponseGenerator()

# Generate a response
response = await generator.generate_response(
    prompt="Tell me a story about a dragon",
    model_id="gpt-4",
    context={"style": "fantasy"},
    parameters={"temperature": 0.8, "max_tokens": 500}
)
```

### Classes

#### `ResponseGenerator`

Unified response generation system for Open WebUI.

**Methods:**
- `generate_response(prompt, model_id=None, context=None, parameters=None)`: Generate a response
- `get_available_models()`: Get a list of available models for response generation

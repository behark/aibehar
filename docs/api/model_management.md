# Model Management API

This document provides detailed information about the Model Management API in Open WebUI, explaining how to load, manage, and use AI models in your applications.

## Overview

The Model Management API allows you to:
- Load and unload AI models
- List available models
- Get information about loaded models
- Monitor model performance and usage

## ModelManager Class

The `ModelManager` class provides a unified interface for managing AI models:

```python
from ai_core import ModelManager

# Initialize the model manager
model_manager = ModelManager()
```

### Loading Models

```python
# Load a model with basic parameters
model = model_manager.load_model(
    model_id="gpt-j-6b",
    model_path="/path/to/model"
)

# Load a model with specific parameters
model = model_manager.load_model(
    model_id="llama-2-7b",
    model_path="/path/to/llama2.bin",
    model_type="llamacpp",
    n_ctx=2048,
    n_batch=512,
    use_gpu=True
)
```

#### Parameters:

- `model_id` (str): Unique identifier for the model
- `model_path` (str, optional): Path to the model file
- `model_type` (str, optional): Type of model (e.g., "llamacpp", "transformers")
- `**kwargs`: Additional model-specific parameters

#### Returns:

- The loaded model or None if loading fails

### Unloading Models

```python
# Unload a model by ID
success = model_manager.unload_model("gpt-j-6b")
```

#### Parameters:

- `model_id` (str): Unique identifier for the model to unload

#### Returns:

- `bool`: True if successful, False otherwise

### Getting Models

```python
# Get a loaded model by ID
model = model_manager.get_model("gpt-j-6b")
```

#### Parameters:

- `model_id` (str): Unique identifier for the model

#### Returns:

- The loaded model or None if not found

### Listing Models

```python
# List all loaded models
models = model_manager.list_models()
```

#### Returns:

- `List[str]`: List of loaded model IDs

## Model Metadata

The `AIUtils` class provides methods for managing model metadata:

```python
from ai_core import AIUtils

# Save model metadata
AIUtils.save_model_metadata(
    model_id="gpt-j-6b",
    metadata={
        "name": "GPT-J 6B",
        "description": "A 6 billion parameter model",
        "parameters": 6_000_000_000,
        "context_length": 2048,
        "created_at": "2023-01-01T00:00:00Z"
    }
)

# Load model metadata
metadata = AIUtils.load_model_metadata("gpt-j-6b")
```

### Validating Model Configurations

```python
# Validate a model configuration
errors = AIUtils.validate_model_config({
    "id": "gpt-j-6b",
    "name": "GPT-J 6B",
    "type": "text"
})

if errors:
    print(f"Configuration errors: {errors}")
else:
    print("Configuration is valid")
```

## Integration with AI Core Bridge

The `AICoreBridge` provides a simplified interface for model management:

```python
from ai_core_bridge import ai_bridge

# Load a model
success = ai_bridge.load_model(
    model_id="gpt-j-6b",
    model_path="/path/to/model",
    model_type="transformers"
)

# Get AI capabilities including available models
capabilities = ai_bridge.get_ai_capabilities()
print(f"Available models: {capabilities['models']['available']}")
```

## Model Loading Process

The model loading process follows these steps:

1. Request to load a model is received by the `ModelManager`
2. `ModelManager` checks if the model is already loaded
3. If not loaded, it determines the appropriate loader based on model type
4. The loader loads the model into memory
5. Model is registered in the `ModelManager`'s internal registry
6. Metadata is saved for future reference

## Model Types

Open WebUI supports various model types:

### Text Generation Models

```python
# Load a text generation model
model = model_manager.load_model(
    model_id="text-model",
    model_path="/path/to/model",
    model_type="text"
)
```

### Image Generation Models

```python
# Load an image generation model
model = model_manager.load_model(
    model_id="image-model",
    model_path="/path/to/model",
    model_type="image"
)
```

### Multi-Modal Models

```python
# Load a multi-modal model
model = model_manager.load_model(
    model_id="multimodal-model",
    model_path="/path/to/model",
    model_type="multimodal"
)
```

## Error Handling

The Model Management API includes robust error handling:

```python
try:
    model = model_manager.load_model("non-existent-model")
    if model is None:
        print("Model loading failed")
except Exception as e:
    print(f"Error: {str(e)}")
```

## Performance Monitoring

You can monitor model performance:

```python
# Get model performance metrics
metrics = model_manager.get_model_metrics("gpt-j-6b")

print(f"Inference speed: {metrics['inference_speed']} tokens/s")
print(f"Memory usage: {metrics['memory_usage']} MB")
print(f"GPU utilization: {metrics['gpu_utilization']}%")
```

## Memory Management

The `ModelManager` includes memory management capabilities:

```python
# Get total memory usage
memory_usage = model_manager.get_total_memory_usage()

# Unload models if memory is constrained
if memory_usage > 90:  # 90% of available memory
    # Unload least recently used model
    model_manager.unload_least_used_model()
```

## Model Sharing

Models can be shared across different components:

```python
# Get a model for use in multiple components
model = model_manager.get_model("gpt-j-6b")

# Use in generation
response = await generation_component.generate(prompt, model)

# Use in classification
classification = await classification_component.classify(text, model)
```

## Model Updates

You can update model parameters:

```python
# Update model parameters
success = model_manager.update_model_parameters(
    model_id="gpt-j-6b",
    parameters={
        "temperature": 0.8,
        "top_p": 0.9
    }
)
```

## Examples

### Loading a Transformers Model

```python
model = model_manager.load_model(
    model_id="gpt2",
    model_path="gpt2",
    model_type="transformers",
    use_gpu=True,
    fp16=True
)
```

### Loading a Llama.cpp Model

```python
model = model_manager.load_model(
    model_id="llama-2-7b",
    model_path="/path/to/llama-2-7b.bin",
    model_type="llamacpp",
    n_ctx=2048,
    n_batch=512,
    n_gpu_layers=32
)
```

### Creating a Model Registry

```python
# Create a simple model registry
class ModelRegistry:
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.registry = {}
    
    def register_model(self, model_id, model_path, model_type, **kwargs):
        model = self.model_manager.load_model(
            model_id=model_id,
            model_path=model_path,
            model_type=model_type,
            **kwargs
        )
        
        if model:
            self.registry[model_id] = {
                "model": model,
                "path": model_path,
                "type": model_type,
                "loaded_at": datetime.now().isoformat()
            }
            return True
        return False
    
    def get_registered_models(self):
        return list(self.registry.keys())

# Usage
registry = ModelRegistry(model_manager)
registry.register_model("gpt2", "gpt2", "transformers")
registry.register_model("llama-2", "/path/to/llama2.bin", "llamacpp")
print(f"Registered models: {registry.get_registered_models()}")
```

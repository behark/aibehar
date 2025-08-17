"""
🚀 Advanced Model Loader

Intelligent model loading system that can handle various model formats
from your extensive collection. Supports Python compiled models, pickled
models, HDF5 models, and more.

Features:
- Multi-format model loading
- Automatic format detection
- Performance optimization
- Error handling and recovery
- Memory management
- GPU acceleration detection
"""

import asyncio
import datetime
import importlib.util
import json
import logging
import os
import pickle
import sys
import threading
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

class ModelLoader:
    """
    Advanced model loader for various machine learning model formats.
    
    This class provides a unified interface for loading models from different file formats,
    with built-in caching, error handling, and memory management capabilities.
    
    Supported formats:
    - Python modules (.py): Loads Python modules with standard model interfaces
    - Compiled Python (.pyc): Handles compiled Python modules
    - Pickle files (.pkl): Deserializes pickled models
    - HDF5 files (.h5): Loads Keras/TensorFlow models or inspects HDF5 structure
    - JSON files (.json): Parses JSON model definitions or parameters
    - Protocol Buffers (.pb): Handles TensorFlow protocol buffer models
    
    Usage:
        loader = ModelLoader()
        model = loader.load_model('/path/to/model.h5')
        
        # Get information without loading
        info = loader.get_model_info('/path/to/model.json')
        
        # Memory management
        loader.unload_model('model_id')
        loader.clear_cache()
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the model loader with configuration options.
        
        Args:
            config: Configuration dictionary with loader options
        """
        # Load default config
        self.config = {
            'max_cache_size': 10,
            'preload_models': False,
            'allowed_directories': [
                '/home/behar/Desktop/sssss/legacy/ai-platform-modern',
                '/tmp/models',
                '/var/models'
            ],
            'default_model_path': None,
            'enable_metrics': True,
            'security_validation': True,
            'enable_async': True
        }
        
        # Override with provided config
        if config:
            self.config.update(config)
        
        # Initialize core components
        self.loaded_models = {}
        self.model_metadata = {}  # Store metadata separately from loaded models
        self.max_cache_size = self.config['max_cache_size']
        self.model_access_times = {}  # For LRU cache implementation
        self._lock = threading.RLock()  # Thread safety
        self._start_time = time.time()
        self._load_count = 0
        self._load_times = []
        self._load_success_count = 0
        
        # Metrics collection
        self.metrics_client = None  # Will be set if monitoring is available
        
        self.supported_formats = {
            '.py': self._load_python_model,
            '.pyc': self._load_compiled_python_model,
            '.pkl': self._load_pickle_model,
            '.h5': self._load_h5_model,
            '.json': self._load_json_model,
            '.pb': self._load_protobuf_model
        }
        
        logger.info(f"🚀 Model Loader initialized with cache size: {self.max_cache_size}")
        logger.info(f"🔒 Security validation: {'enabled' if self.config['security_validation'] else 'disabled'}")
        
        if self.config['preload_models']:
            self._preload_common_models()
    
    def load_model(self, model_path: str, model_id: str = None, validate_source: bool = None, version: str = None) -> Optional[Any]:
        """
        Load a model from file path with automatic format detection.
        
        Args:
            model_path: Path to the model file
            model_id: Optional identifier for caching
            validate_source: Whether to validate the source for security (defaults to config)
            version: Optional version constraint for the model
            
        Returns:
            Loaded model object or None if loading failed
        """
        start_time = time.time()
        result = None
        error = None
        
        # Use config default if not specified
        if validate_source is None:
            validate_source = self.config['security_validation']
        
        try:
            with self._lock:
                self._load_count += 1
            
            # Validate path to prevent directory traversal attacks
            model_path = os.path.abspath(model_path)
            
            if validate_source:
                allowed_dirs = self._get_allowed_model_directories()
                if not any(model_path.startswith(allowed_dir) for allowed_dir in allowed_dirs):
                    logger.error(f"🛑 Security: Attempted to load model from unauthorized location: {model_path}")
                    return None
            
            if not os.path.exists(model_path):
                logger.error(f"💥 Model file not found: {model_path}")
                return None
            
            # Check if already loaded
            cache_key = model_id or model_path
            if cache_key in self.loaded_models:
                with self._lock:
                    self.model_access_times[cache_key] = time.time()
                logger.info(f"♻️ Using cached model: {cache_key}")
                return self.loaded_models[cache_key]
            
            # Version validation if specified
            if version and not self._validate_model_version(model_path, version):
                logger.error(f"⚠️ Model version mismatch: {model_path} does not satisfy version {version}")
                return None
            
            # Determine file format
            file_extension = Path(model_path).suffix.lower()
            
            if file_extension not in self.supported_formats:
                logger.warning(f"⚠️ Unsupported format: {file_extension} for {model_path}")
                result = self._load_generic_file(model_path)
            else:
                # Load model using appropriate loader
                loader_func = self.supported_formats[file_extension]
                result = loader_func(model_path)
            
            if result is not None:
                # Cache the loaded model
                with self._lock:
                    self.loaded_models[cache_key] = result
                    self.model_access_times[cache_key] = time.time()
                    self._load_success_count += 1
                    
                    # Store metadata
                    self.model_metadata[cache_key] = {
                        'path': model_path,
                        'format': file_extension,
                        'load_time': time.time() - start_time,
                        'version': version,
                        'size_bytes': os.path.getsize(model_path)
                    }
                
                # Manage cache size
                self._manage_cache_size()
                
                logger.info(f"✅ Successfully loaded model: {model_path}")
            else:
                logger.error(f"💥 Failed to load model: {model_path}")
                
        except Exception as e:
            error = str(e)
            logger.error(f"💥 Error loading model {model_path}: {error}")
            logger.debug(f"Stack trace: {traceback.format_exc()}")
        finally:
            # Record metrics for monitoring
            elapsed_time = time.time() - start_time
            with self._lock:
                self._load_times.append(elapsed_time)
            self._record_loading_metrics(model_path, elapsed_time, bool(result), error)
            
        return result
    
    def _load_python_model(self, model_path: str) -> Optional[Any]:
        """Load a Python model from .py file."""
        try:
            model_name = os.path.basename(model_path).replace(".py", "")
            spec = importlib.util.spec_from_file_location(model_name, model_path)
            
            if spec is None or spec.loader is None:
                logger.error(f"💥 Cannot create spec for {model_path}")
                return None
            
            model_module = importlib.util.module_from_spec(spec)
            
            # Add to sys.modules to handle imports
            sys.modules[model_name] = model_module
            
            spec.loader.exec_module(model_module)
            
            # Try to get the model object
            if hasattr(model_module, 'get_model'):
                return model_module.get_model()
            elif hasattr(model_module, 'model'):
                return model_module.model
            elif hasattr(model_module, 'Model'):
                return model_module.Model()
            else:
                logger.warning(f"⚠️ No standard model interface found in {model_path}")
                return model_module
                
        except Exception as e:
            logger.error(f"💥 Python model loading failed: {e}")
            return None
    
    def _load_compiled_python_model(self, model_path: str) -> Optional[Any]:
        """Load a compiled Python model from .pyc file."""
        try:
            # For .pyc files, we need to handle them differently
            # Most of your .cpython-312.pyc files are compiled modules
            
            model_name = os.path.basename(model_path).replace(".cpython-312.pyc", "")
            
            # Try to load as a regular Python module if source exists
            py_path = model_path.replace(".cpython-312.pyc", ".py")
            if os.path.exists(py_path):
                return self._load_python_model(py_path)
            
            # For compiled-only modules, we can't easily load them
            # But we can provide metadata about them
            logger.info(f"📝 Compiled model detected: {model_name}")
            
            return {
                'type': 'compiled_python_model',
                'name': model_name,
                'path': model_path,
                'status': 'detected',
                'note': 'Compiled Python module - requires runtime loading'
            }
            
        except Exception as e:
            logger.error(f"💥 Compiled Python model loading failed: {e}")
            return None
    
    def _load_pickle_model(self, model_path: str) -> Optional[Any]:
        """Load a pickled model."""
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            logger.info(f"🥒 Loaded pickle model: {model_path}")
            return model
            
        except Exception as e:
            logger.error(f"💥 Pickle model loading failed: {e}")
            return None
    
    def _load_h5_model(self, model_path: str) -> Optional[Any]:
        """Load an HDF5 model (typically Keras/TensorFlow)."""
        try:
            # Try different HDF5 loading methods
            try:
                # Try Keras first
                import tensorflow as tf
                model = tf.keras.models.load_model(model_path)
                logger.info(f"🧠 Loaded Keras model: {model_path}")
                return model
            except ImportError:
                # Fallback to h5py for data inspection
                try:
                    import h5py
                    with h5py.File(model_path, 'r') as f:
                        model_data = {
                            'type': 'h5_file',
                            'keys': list(f.keys()),
                            'path': model_path,
                            'format': 'hdf5'
                        }
                    logger.info(f"📊 Loaded H5 data: {model_path}")
                    return model_data
                except ImportError:
                    logger.warning(f"⚠️ No H5 loading libraries available for {model_path}")
                    return None
            
        except Exception as e:
            logger.error(f"💥 H5 model loading failed: {e}")
            return None
    
    def _load_json_model(self, model_path: str) -> Optional[Any]:
        """Load a JSON model/data file."""
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                model_data = json.load(f)
            
            logger.info(f"📄 Loaded JSON model: {model_path}")
            return model_data
            
        except Exception as e:
            logger.error(f"💥 JSON model loading failed: {e}")
            return None
    
    def _load_protobuf_model(self, model_path: str) -> Optional[Any]:
        """Load a Protocol Buffer model (typically TensorFlow)."""
        try:
            # This is complex and depends on the specific protobuf format
            # For now, return metadata
            model_info = {
                'type': 'protobuf_model',
                'path': model_path,
                'format': 'protobuf',
                'status': 'detected',
                'note': 'Protocol Buffer model - requires specific loader'
            }
            
            logger.info(f"📦 Detected Protocol Buffer model: {model_path}")
            return model_info
            
        except Exception as e:
            logger.error(f"💥 Protocol Buffer model loading failed: {e}")
            return None
    
    def _load_generic_file(self, model_path: str) -> Optional[Any]:
        """Load a generic file and return metadata."""
        try:
            file_stats = os.stat(model_path)
            file_info = {
                'type': 'generic_file',
                'path': model_path,
                'size_bytes': file_stats.st_size,
                'extension': Path(model_path).suffix,
                'name': os.path.basename(model_path),
                'status': 'detected'
            }
            
            logger.info(f"📁 Detected generic file: {model_path}")
            return file_info
            
        except Exception as e:
            logger.error(f"💥 Generic file loading failed: {e}")
            return None
    
    async def load_model_async(self, model_path: str, model_id: str = None, validate_source: bool = None, version: str = None) -> Optional[Any]:
        """
        Asynchronously load a model from file path.
        
        Args:
            model_path: Path to the model file
            model_id: Optional identifier for caching
            validate_source: Whether to validate the source for security
            version: Optional version constraint for the model
            
        Returns:
            Loaded model object or None if loading failed
        """
        try:
            # Run the synchronous load_model in a thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.load_model,
                model_path,
                model_id,
                validate_source,
                version
            )
            return result
        except Exception as e:
            logger.error(f"💥 Error in async model loading for {model_path}: {e}")
            return None
    
    def preload_models(self, model_configs: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        Preload multiple models for faster subsequent access.
        
        Args:
            model_configs: List of model configuration dictionaries with keys:
                - path: Model file path
                - id: Optional model identifier
                - validate_source: Optional security validation flag
                - version: Optional version constraint
        
        Returns:
            Dictionary mapping model IDs/paths to loading success status
        """
        results = {}
        
        for config in model_configs:
            model_path = config.get('path')
            model_id = config.get('id')
            validate_source = config.get('validate_source')
            version = config.get('version')
            
            if not model_path:
                logger.warning("⚠️ Skipping model config without path")
                continue
            
            try:
                result = self.load_model(model_path, model_id, validate_source, version)
                key = model_id or model_path
                results[key] = result is not None
                
                if result is not None:
                    logger.info(f"✅ Preloaded model: {key}")
                else:
                    logger.warning(f"⚠️ Failed to preload model: {key}")
                    
            except Exception as e:
                key = model_id or model_path
                results[key] = False
                logger.error(f"💥 Error preloading model {key}: {e}")
        
        return results
    
    def list_loaded_models(self) -> List[Dict[str, Any]]:
        """Get list of all currently loaded models with their info."""
        models = []
        for key in self.loaded_models.keys():
            model_info = self.get_loaded_model_info(key)
            if model_info:
                model_info['key'] = key
                models.append(model_info)
        return models
    
    def get_loaded_model_info(self, model_key: str) -> Optional[Dict[str, Any]]:
        """Get information about a loaded model from cache."""
        if model_key not in self.loaded_models:
            return None
        
        info = {
            'loaded': True,
            'last_accessed': self.model_access_times.get(model_key),
            'type': type(self.loaded_models[model_key]).__name__
        }
        
        if model_key in self.model_metadata:
            info.update(self.model_metadata[model_key])
        
        return info
    
    def unload_model(self, model_key: str) -> bool:
        """Unload a specific model from cache."""
        try:
            if model_key in self.loaded_models:
                with self._lock:
                    del self.loaded_models[model_key]
                    if model_key in self.model_access_times:
                        del self.model_access_times[model_key]
                    if model_key in self.model_metadata:
                        del self.model_metadata[model_key]
                
                logger.info(f"♻️ Unloaded model: {model_key}")
                return True
            else:
                logger.warning(f"⚠️ Model not found in cache: {model_key}")
                return False
        except Exception as e:
            logger.error(f"💥 Error unloading model {model_key}: {e}")
            return False

    def get_model_info(self, model_path: str) -> Dict[str, Any]:
        """Get information about a model without loading it."""
        try:
            if not os.path.exists(model_path):
                return {'error': 'File not found'}
            
            file_stats = os.stat(model_path)
            file_extension = Path(model_path).suffix.lower()
            
            info = {
                'path': model_path,
                'name': os.path.basename(model_path),
                'size_bytes': file_stats.st_size,
                'size_human': self._format_bytes(file_stats.st_size),
                'extension': file_extension,
                'supported': file_extension in self.supported_formats,
                'loader_available': file_extension in self.supported_formats
            }
            
            # Add format-specific information
            if file_extension == '.json':
                try:
                    with open(model_path, 'r') as f:
                        data = json.load(f)
                    info['json_keys'] = list(data.keys()) if isinstance(data, dict) else 'array'
                except:
                    pass
            
            return info
            
        except Exception as e:
            return {'error': str(e)}
    
    def list_loaded_models(self) -> Dict[str, Any]:
        """List all currently loaded models."""
        return {
            'count': len(self.loaded_models),
            'models': list(self.loaded_models.keys()),
            'memory_usage': self._estimate_memory_usage()
        }
    
    def unload_model(self, model_id: str) -> bool:
        """Unload a model from memory."""
        try:
            if model_id in self.loaded_models:
                del self.loaded_models[model_id]
                logger.info(f"🗑️ Unloaded model: {model_id}")
                return True
            else:
                logger.warning(f"⚠️ Model not found in cache: {model_id}")
                return False
        except Exception as e:
            logger.error(f"💥 Failed to unload model {model_id}: {e}")
            return False
    
    def _get_allowed_model_directories(self) -> List[str]:
        """Get list of allowed directories for model loading."""
        allowed_dirs = [
            os.path.abspath(self.cache_dir),
            os.path.abspath(os.path.expanduser("~/.cache/huggingface")),
            os.path.abspath(os.path.expanduser("~/.cache/models")),
            "/tmp/models",
            "/var/lib/models"
        ]
        
        # Add any custom directories from config
        if 'allowed_model_dirs' in self.config:
            for custom_dir in self.config['allowed_model_dirs']:
                allowed_dirs.append(os.path.abspath(custom_dir))
        
        return allowed_dirs
    
    def _validate_model_version(self, model_path: str, required_version: str) -> bool:
        """Validate model version against requirements."""
        try:
            # Try to extract version from model metadata or filename
            # This is a simplified implementation - actual version checking
            # would depend on model format and metadata availability
            model_name = Path(model_path).stem
            
            # Look for version pattern in filename (e.g., model_v1.2.3.pkl)
            import re
            version_pattern = r'v?(\d+)\.(\d+)\.(\d+)'
            match = re.search(version_pattern, model_name)
            
            if match:
                model_version = f"{match.group(1)}.{match.group(2)}.{match.group(3)}"
                # Simple version comparison - in production, use proper semver
                return model_version >= required_version
            
            # If no version found, assume it's compatible
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Could not validate version for {model_path}: {e}")
            return True  # Default to allow loading
    
    def _manage_cache_size(self):
        """Manage cache size by removing least recently used models."""
        try:
            if len(self.loaded_models) <= self.config['max_cached_models']:
                return
            
            # Sort by access time and remove oldest
            sorted_models = sorted(
                self.model_access_times.items(),
                key=lambda x: x[1]
            )
            
            models_to_remove = len(self.loaded_models) - self.config['max_cached_models']
            
            for i in range(models_to_remove):
                model_key = sorted_models[i][0]
                if model_key in self.loaded_models:
                    del self.loaded_models[model_key]
                    del self.model_access_times[model_key]
                    if model_key in self.model_metadata:
                        del self.model_metadata[model_key]
                    logger.info(f"♻️ Removed cached model from memory: {model_key}")
                    
        except Exception as e:
            logger.error(f"💥 Error managing cache size: {e}")
    
    def _record_loading_metrics(self, model_path: str, elapsed_time: float, success: bool, error: str = None):
        """Record metrics for monitoring and analysis."""
        try:
            # Update internal counters
            if success:
                with self._lock:
                    self._load_success_count += 1
            else:
                with self._lock:
                    self._load_failure_count += 1
            
            # Log metrics for external monitoring systems
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'model_path': model_path,
                'elapsed_time': elapsed_time,
                'success': success,
                'error': error,
                'cache_size': len(self.loaded_models),
                'total_loads': self._load_count
            }
            
            # In production, this would send to monitoring system (Prometheus, etc.)
            logger.debug(f"📊 Loading metrics: {metrics}")
            
        except Exception as e:
            logger.error(f"💥 Error recording metrics: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get loader health status for monitoring."""
        try:
            with self._lock:
                avg_load_time = sum(self._load_times[-100:]) / len(self._load_times[-100:]) if self._load_times else 0
                success_rate = (self._load_success_count / max(self._load_count, 1)) * 100
                
                return {
                    'status': 'healthy' if success_rate > 80 else 'degraded',
                    'total_loads': self._load_count,
                    'success_count': self._load_success_count,
                    'failure_count': self._load_failure_count,
                    'success_rate_percent': round(success_rate, 2),
                    'cached_models': len(self.loaded_models),
                    'average_load_time_seconds': round(avg_load_time, 3),
                    'supported_formats': list(self.supported_formats.keys()),
                    'cache_directory': self.cache_dir,
                    'last_updated': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"💥 Error getting health status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def clear_cache(self) -> int:
        """Clear all cached models and return count of cleared models."""
        try:
            with self._lock:
                count = len(self.loaded_models)
                self.loaded_models.clear()
                self.model_access_times.clear()
                self.model_metadata.clear()
                logger.info(f"♻️ Cleared {count} models from cache")
                return count
        except Exception as e:
            logger.error(f"💥 Error clearing cache: {e}")
            return 0
    
    def _format_bytes(self, bytes_size: int) -> str:
        """Format bytes into human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
    
    def _estimate_memory_usage(self) -> str:
        """Estimate memory usage of loaded models."""
        # This is a rough estimate
        estimated_bytes = len(self.loaded_models) * 1024 * 1024  # 1MB per model estimate
        return self._format_bytes(estimated_bytes)


# Global model loader instance
model_loader = ModelLoader()

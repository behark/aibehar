"""Graceful shutdown utilities for Consciousness WebUI"""

import signal
import sys
import atexit
import threading
import time
from typing import List, Callable, Optional
from pathlib import Path

class GracefulShutdown:
    """Handle graceful shutdown of the consciousness platform"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.shutdown_handlers: List[Callable] = []
        self.is_shutting_down = False
        self.shutdown_timeout = 30  # seconds
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Register atexit handler
        atexit.register(self._cleanup)
    
    def register_handler(self, handler: Callable) -> None:
        """Register a cleanup handler"""
        self.shutdown_handlers.append(handler)
        if self.logger:
            self.logger.debug(f"Registered shutdown handler: {handler.__name__}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        signal_names = {
            signal.SIGINT: "SIGINT (Ctrl+C)",
            signal.SIGTERM: "SIGTERM"
        }
        signal_name = signal_names.get(signum, f"Signal {signum}")
        
        if self.logger:
            self.logger.info(f"Received {signal_name}, initiating graceful shutdown...", emoji="🛑")
        else:
            print(f"\n🛑 Received {signal_name}, initiating graceful shutdown...")
        
        self._shutdown()
    
    def _cleanup(self):
        """Cleanup function called on exit"""
        if not self.is_shutting_down:
            self._shutdown()
    
    def _shutdown(self):
        """Perform graceful shutdown"""
        if self.is_shutting_down:
            return
        
        self.is_shutting_down = True
        
        if self.logger:
            self.logger.info("Starting graceful shutdown process...", emoji="🌙")
        else:
            print("🌙 Starting graceful shutdown process...")
        
        # Execute shutdown handlers
        for i, handler in enumerate(self.shutdown_handlers):
            try:
                if self.logger:
                    self.logger.debug(f"Executing shutdown handler {i+1}/{len(self.shutdown_handlers)}: {handler.__name__}")
                
                # Run handler with timeout
                handler_thread = threading.Thread(target=handler)
                handler_thread.daemon = True
                handler_thread.start()
                handler_thread.join(timeout=5)  # 5 second timeout per handler
                
                if handler_thread.is_alive():
                    if self.logger:
                        self.logger.warning(f"Shutdown handler {handler.__name__} timed out")
                    else:
                        print(f"⚠️  Shutdown handler {handler.__name__} timed out")
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error in shutdown handler {handler.__name__}: {e}")
                else:
                    print(f"❌ Error in shutdown handler {handler.__name__}: {e}")
        
        if self.logger:
            self.logger.success("Graceful shutdown completed")
        else:
            print("✅ Graceful shutdown completed")
        
        # Force exit after timeout
        sys.exit(0)

def create_shutdown_manager(logger=None) -> GracefulShutdown:
    """Create and return a graceful shutdown manager"""
    return GracefulShutdown(logger)

# Shutdown handlers for common resources
def shutdown_gradio_interface(interface):
    """Shutdown handler for Gradio interface"""
    try:
        if hasattr(interface, 'close'):
            interface.close()
        print("🌐 Gradio interface closed")
    except Exception as e:
        print(f"❌ Error closing Gradio interface: {e}")

def save_session_data(data, file_path: str):
    """Shutdown handler to save session data"""
    try:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Session data saved to {file_path}")
    except Exception as e:
        print(f"❌ Error saving session data: {e}")

def cleanup_temp_files(temp_dir: str):
    """Shutdown handler to clean up temporary files"""
    try:
        temp_path = Path(temp_dir)
        if temp_path.exists() and temp_path.is_dir():
            import shutil
            shutil.rmtree(temp_path)
            print(f"🗑️  Cleaned up temporary files in {temp_dir}")
    except Exception as e:
        print(f"❌ Error cleaning up temp files: {e}")

def stop_background_tasks(tasks: List):
    """Shutdown handler to stop background tasks"""
    try:
        for task in tasks:
            if hasattr(task, 'cancel'):
                task.cancel()
            elif hasattr(task, 'stop'):
                task.stop()
        print(f"⏹️  Stopped {len(tasks)} background tasks")
    except Exception as e:
        print(f"❌ Error stopping background tasks: {e}")

"""Enhanced logging utilities for Consciousness WebUI"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union
from datetime import datetime

# ANSI color codes for terminal output
COLORS = {
    'RESET': '\033[0m',
    'RED': '\033[91m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'PURPLE': '\033[95m',
    'CYAN': '\033[96m',
    'BOLD': '\033[1m'
}

class ConsciousnessLogger:
    """Enhanced logger with colored console output and file logging"""
    
    def __init__(
        self, 
        name: str = "consciousness", 
        log_level: str = "info",
        log_file: Optional[Union[str, Path]] = None,
        console_output: bool = True
    ):
        self.name = name
        self.logger = logging.getLogger(name)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Set log level
        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }
        self.logger.setLevel(level_map.get(log_level.lower(), logging.INFO))
        
        # Create console handler with color formatting
        if console_output:
            console = logging.StreamHandler(sys.stdout)
            console.setFormatter(ColoredFormatter())
            self.logger.addHandler(console)
        
        # Add file handler if specified
        if log_file:
            file_path = Path(log_file)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(file_handler)
    
    def debug(self, msg: str, emoji: str = "🔍"):
        """Log debug message"""
        self.logger.debug(f"{emoji} {msg}")
        
    def info(self, msg: str, emoji: str = "ℹ️"):
        """Log info message"""
        self.logger.info(f"{emoji} {msg}")
        
    def warning(self, msg: str, emoji: str = "⚠️"):
        """Log warning message"""
        self.logger.warning(f"{emoji} {msg}")
        
    def error(self, msg: str, emoji: str = "❌", exc_info: bool = False):
        """Log error message"""
        self.logger.error(f"{emoji} {msg}", exc_info=exc_info)
        
    def critical(self, msg: str, emoji: str = "🚨", exc_info: bool = False):
        """Log critical message"""
        self.logger.critical(f"{emoji} {msg}", exc_info=exc_info)
        
    def success(self, msg: str, emoji: str = "✅"):
        """Log success message"""
        self.logger.info(f"{emoji} {msg}")
    
    def consciousness(self, msg: str, emoji: str = "🧠"):
        """Log consciousness-specific message"""
        self.logger.info(f"{emoji} {msg}")
    
    def system(self, msg: str, emoji: str = "⚙️"):
        """Log system message"""
        self.logger.info(f"{emoji} {msg}")
    
    def user_action(self, msg: str, emoji: str = "👤"):
        """Log user action"""
        self.logger.info(f"{emoji} {msg}")
    
    def performance(self, msg: str, emoji: str = "📊"):
        """Log performance message"""
        self.logger.info(f"{emoji} {msg}")

class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored console output"""
    
    FORMATS = {
        logging.DEBUG: COLORS['BLUE'] + '%(message)s' + COLORS['RESET'],
        logging.INFO: '%(message)s',
        logging.WARNING: COLORS['YELLOW'] + '%(message)s' + COLORS['RESET'],
        logging.ERROR: COLORS['RED'] + '%(message)s' + COLORS['RESET'],
        logging.CRITICAL: COLORS['RED'] + COLORS['BOLD'] + '%(message)s' + COLORS['RESET'],
    }
    
    def format(self, record):
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_format)
        return formatter.format(record)

# Global logger instance
_global_logger: Optional[ConsciousnessLogger] = None

def get_logger() -> ConsciousnessLogger:
    """Get the global consciousness logger"""
    global _global_logger
    if _global_logger is None:
        _global_logger = ConsciousnessLogger(
            name="consciousness",
            log_level="info",
            log_file="user_data/logs/consciousness.log"
        )
    return _global_logger

def setup_logging(log_level: str = "info", log_file: Optional[str] = None) -> ConsciousnessLogger:
    """Setup global logging configuration"""
    global _global_logger
    _global_logger = ConsciousnessLogger(
        name="consciousness",
        log_level=log_level,
        log_file=log_file or "user_data/logs/consciousness.log"
    )
    return _global_logger

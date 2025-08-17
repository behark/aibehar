"""
Security Logging and Monitoring for Open WebUI

This module implements logging and monitoring for security events:
- Authentication attempts (success/failure)
- Authorization violations
- API access patterns
- Rate limiting events
- System changes
- Security-related errors

Features:
- Structured logging with consistent formats
- Log rotation to prevent file bloat
- Log levels for different environments
- Sensitive data filtering
"""

import datetime
import json
import logging
import os
import re
import socket
import time
import traceback
from functools import wraps
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Any, Dict, List, Optional, Set, Union

# Configure the logger
logger = logging.getLogger("security")

class SecurityLogger:
    """
    Security logging handler for Open WebUI.
    """
    
    # Sensitive fields that should be redacted in logs
    SENSITIVE_FIELDS = {
        'password', 'token', 'secret', 'api_key', 'apikey', 'key', 
        'credentials', 'auth', 'jwt', 'refresh_token', 'access_token',
    }
    
    def __init__(
        self,
        log_dir: str = "logs",
        max_log_size_mb: int = 10,
        backup_count: int = 5,
        log_level: str = "INFO",
        log_to_console: bool = True,
        log_format: str = None,
        hostname: str = None,
    ):
        """
        Initialize the security logger.
        
        Args:
            log_dir: Directory to store log files
            max_log_size_mb: Maximum size of log file in MB before rotation
            backup_count: Number of backup files to keep
            log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_console: Whether to log to console in addition to file
            log_format: Custom log format (or None for default)
            hostname: Hostname to include in logs (or None to detect)
        """
        self.log_dir = log_dir
        self.max_log_size_mb = max_log_size_mb
        self.backup_count = backup_count
        self.log_level_name = log_level
        self.log_level = getattr(logging, log_level)
        self.log_to_console = log_to_console
        self.hostname = hostname or socket.gethostname()
        
        # Ensure log directory exists
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configure logger
        logger.setLevel(self.log_level)
        
        # Set up file handler with rotation
        security_log_path = os.path.join(log_dir, "security.log")
        file_handler = RotatingFileHandler(
            security_log_path, 
            maxBytes=max_log_size_mb * 1024 * 1024,
            backupCount=backup_count,
        )
        
        # Set up formatter - default to JSON format for easier parsing
        if log_format:
            formatter = logging.Formatter(log_format)
        else:
            formatter = logging.Formatter(
                '%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] - %(message)s'
            )
        
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Add console handler if requested
        if log_to_console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
        # Access log for API requests
        access_log_path = os.path.join(log_dir, "access.log")
        self.access_logger = logging.getLogger("access")
        self.access_logger.setLevel(self.log_level)
        
        access_file_handler = TimedRotatingFileHandler(
            access_log_path,
            when="midnight",
            backupCount=backup_count
        )
        access_file_handler.setFormatter(formatter)
        self.access_logger.addHandler(access_file_handler)
        
        if log_to_console:
            self.access_logger.addHandler(console_handler)
            
    @staticmethod
    def _redact_sensitive_data(data: Any) -> Any:
        """
        Redact sensitive data from logs.
        
        Args:
            data: Data to redact
            
        Returns:
            Redacted data
        """
        if isinstance(data, dict):
            return {
                k: "[REDACTED]" if k.lower() in SecurityLogger.SENSITIVE_FIELDS else 
                   SecurityLogger._redact_sensitive_data(v)
                for k, v in data.items()
            }
        elif isinstance(data, list):
            return [SecurityLogger._redact_sensitive_data(item) for item in data]
        else:
            return data
            
    def _format_extra(self, extra: Dict[str, Any]) -> Dict[str, Any]:
        """Format extra data for logging."""
        extra_copy = dict(extra)
        extra_copy["hostname"] = self.hostname
        extra_copy["timestamp"] = datetime.datetime.utcnow().isoformat()
        return self._redact_sensitive_data(extra_copy)
            
    def log_auth_attempt(
        self,
        success: bool,
        username: str,
        source_ip: str,
        auth_type: str = "password",
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log an authentication attempt.
        
        Args:
            success: Whether the attempt was successful
            username: Username used in the attempt
            source_ip: Source IP address
            auth_type: Type of authentication (password, token, etc.)
            details: Additional details
        """
        log_data = {
            "event_type": "authentication",
            "success": success,
            "username": username,
            "source_ip": source_ip,
            "auth_type": auth_type,
        }
        
        if details:
            log_data["details"] = self._redact_sensitive_data(details)
            
        if success:
            logger.info(f"Authentication success: {username}", extra=self._format_extra(log_data))
        else:
            logger.warning(f"Authentication failure: {username}", extra=self._format_extra(log_data))
    
    def log_authorization(
        self,
        success: bool,
        username: str,
        source_ip: str,
        resource: str,
        action: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log an authorization check.
        
        Args:
            success: Whether the authorization was successful
            username: Username of the user
            source_ip: Source IP address
            resource: Resource being accessed
            action: Action being performed (read, write, etc.)
            details: Additional details
        """
        log_data = {
            "event_type": "authorization",
            "success": success,
            "username": username,
            "source_ip": source_ip,
            "resource": resource,
            "action": action,
        }
        
        if details:
            log_data["details"] = self._redact_sensitive_data(details)
            
        if success:
            logger.info(f"Authorization success: {username} - {action} on {resource}", 
                        extra=self._format_extra(log_data))
        else:
            logger.warning(f"Authorization failure: {username} - {action} on {resource}",
                         extra=self._format_extra(log_data))
    
    def log_api_request(
        self,
        method: str,
        path: str,
        source_ip: str,
        status_code: int,
        username: Optional[str] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_time_ms: Optional[float] = None,
        user_agent: Optional[str] = None
    ):
        """
        Log an API request.
        
        Args:
            method: HTTP method
            path: URL path
            source_ip: Source IP address
            status_code: HTTP status code
            username: Username if authenticated
            request_data: Request data
            response_time_ms: Response time in milliseconds
            user_agent: User agent string
        """
        log_data = {
            "event_type": "api_request",
            "method": method,
            "path": path,
            "source_ip": source_ip,
            "status_code": status_code,
        }
        
        if username:
            log_data["username"] = username
        
        if request_data:
            log_data["request_data"] = self._redact_sensitive_data(request_data)
            
        if response_time_ms:
            log_data["response_time_ms"] = response_time_ms
            
        if user_agent:
            log_data["user_agent"] = user_agent
            
        # Use access logger for API requests
        self.access_logger.info(
            f"{method} {path} - {status_code} - {source_ip} - {username or 'anonymous'}",
            extra=self._format_extra(log_data)
        )
        
        # Log 4xx and 5xx status codes as warnings and errors
        if 400 <= status_code < 500:
            logger.warning(
                f"API request error: {method} {path} - {status_code}",
                extra=self._format_extra(log_data)
            )
        elif status_code >= 500:
            logger.error(
                f"API server error: {method} {path} - {status_code}",
                extra=self._format_extra(log_data)
            )
    
    def log_rate_limit(
        self,
        source_ip: str,
        path: str,
        limit: int,
        window_seconds: int,
        username: Optional[str] = None
    ):
        """
        Log a rate limit violation.
        
        Args:
            source_ip: Source IP address
            path: URL path
            limit: Rate limit
            window_seconds: Time window in seconds
            username: Username if authenticated
        """
        log_data = {
            "event_type": "rate_limit",
            "source_ip": source_ip,
            "path": path,
            "limit": limit,
            "window_seconds": window_seconds,
        }
        
        if username:
            log_data["username"] = username
            
        logger.warning(
            f"Rate limit exceeded: {source_ip} - {path}",
            extra=self._format_extra(log_data)
        )
    
    def log_system_change(
        self,
        change_type: str,
        username: str,
        source_ip: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log a system configuration change.
        
        Args:
            change_type: Type of change
            username: Username who made the change
            source_ip: Source IP address
            details: Additional details
        """
        log_data = {
            "event_type": "system_change",
            "change_type": change_type,
            "username": username,
            "source_ip": source_ip,
        }
        
        if details:
            log_data["details"] = self._redact_sensitive_data(details)
            
        logger.info(
            f"System change: {change_type} by {username}",
            extra=self._format_extra(log_data)
        )
    
    def log_security_event(
        self,
        event_type: str,
        severity: str,
        message: str,
        source_ip: Optional[str] = None,
        username: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Log a generic security event.
        
        Args:
            event_type: Type of security event
            severity: Severity (low, medium, high, critical)
            message: Event message
            source_ip: Source IP address
            username: Username involved
            details: Additional details
        """
        log_data = {
            "event_type": "security_event",
            "security_event_type": event_type,
            "severity": severity,
        }
        
        if source_ip:
            log_data["source_ip"] = source_ip
            
        if username:
            log_data["username"] = username
            
        if details:
            log_data["details"] = self._redact_sensitive_data(details)
        
        log_method = {
            "low": logger.info,
            "medium": logger.warning,
            "high": logger.error,
            "critical": logger.critical
        }.get(severity.lower(), logger.warning)
        
        log_method(
            f"Security event: {event_type} - {message}",
            extra=self._format_extra(log_data)
        )
        
    def log_error(
        self,
        error: Exception,
        source_ip: Optional[str] = None,
        username: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Log an error with stack trace.
        
        Args:
            error: The exception to log
            source_ip: Source IP address
            username: Username involved
            context: Additional context
        """
        log_data = {
            "event_type": "error",
            "error_type": error.__class__.__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
        }
        
        if source_ip:
            log_data["source_ip"] = source_ip
            
        if username:
            log_data["username"] = username
            
        if context:
            log_data["context"] = self._redact_sensitive_data(context)
            
        logger.error(
            f"Error: {error.__class__.__name__} - {str(error)}",
            extra=self._format_extra(log_data)
        )


# Create a FastAPI middleware for request logging
def create_request_logging_middleware(security_logger: SecurityLogger):
    """
    Create a FastAPI middleware for logging requests.
    
    Args:
        security_logger: SecurityLogger instance
        
    Returns:
        Middleware class for FastAPI
    """
    from fastapi import Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware
    
    class RequestLoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            start_time = time.time()
            
            # Get client IP
            source_ip = request.client.host if request.client else "unknown"
            
            # Get username from session if available
            username = None
            if hasattr(request.state, "user") and hasattr(request.state.user, "username"):
                username = request.state.user.username
            
            # Get request path and method
            method = request.method
            path = request.url.path
            
            # Get user agent
            user_agent = request.headers.get("user-agent", "unknown")
            
            # Try to get request data (for non-GET requests)
            request_data = None
            if method != "GET":
                try:
                    if request.headers.get("content-type") == "application/json":
                        request_data = await request.json()
                except:
                    # JSON parsing might fail, just continue without request data
                    pass
            
            # Process request
            try:
                response = await call_next(request)
                status_code = response.status_code
            except Exception as e:
                # Log the error
                security_logger.log_error(e, source_ip=source_ip, username=username)
                raise
            
            # Calculate response time
            response_time_ms = (time.time() - start_time) * 1000
            
            # Log the request
            security_logger.log_api_request(
                method=method,
                path=path,
                source_ip=source_ip,
                status_code=status_code,
                username=username,
                request_data=request_data,
                response_time_ms=response_time_ms,
                user_agent=user_agent
            )
            
            # Rate limit exceeded (assuming 429 is rate limit)
            if status_code == 429:
                security_logger.log_rate_limit(
                    source_ip=source_ip,
                    path=path,
                    limit=100,  # Default limit, should be retrieved from config
                    window_seconds=60,  # Default window, should be retrieved from config
                    username=username
                )
            
            return response
    
    return RequestLoggingMiddleware


# Usage example
"""
from fastapi import FastAPI
from .security_logging import SecurityLogger, create_request_logging_middleware

# Initialize security logger
security_logger = SecurityLogger(
    log_dir="logs",
    log_level="INFO",
    log_to_console=True
)

app = FastAPI()

# Add request logging middleware
app.add_middleware(create_request_logging_middleware(security_logger))

# Example usage in an authentication endpoint
@app.post("/api/login")
async def login(username: str, password: str, request: Request):
    # ... authentication logic ...
    
    success = True  # or False if authentication failed
    source_ip = request.client.host
    
    # Log the authentication attempt
    security_logger.log_auth_attempt(
        success=success,
        username=username,
        source_ip=source_ip,
        auth_type="password"
    )
    
    # ... return response ...
"""

#!/usr/bin/env python3
"""
🧠 Enhanced Security Utilities

Security framework for the Consciousness WebUI with support for:
- JWT authentication
- Rate limiting
- CORS protection
- Input validation
- Security audit logging
- XSS and CSRF protection

Author: Dimensional AI
Version: 2.0.0
"""

import hashlib
import ipaddress
import json
import logging
import re
import secrets
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

import jwt

logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
    """Security configuration settings."""
    enable_auth: bool = False
    jwt_secret_key: str = ""
    session_timeout: int = 3600
    allowed_ips: List[str] = field(default_factory=list)
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    enable_cors: bool = True
    cors_allow_origins: List[str] = field(default_factory=list)
    content_security_policy: bool = True
    xss_protection: bool = True
    audit_logging: bool = True

@dataclass
class UserSession:
    """User session data."""
    user_id: str
    username: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    permissions: List[str] = field(default_factory=list)
    session_data: Dict[str, Any] = field(default_factory=dict)

class PasswordValidator:
    """Password validation and security policy enforcement."""
    
    def __init__(self, min_length=12, require_uppercase=True, require_lowercase=True, 
                 require_numbers=True, require_special=True, max_length=128,
                 disallow_common=True):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_numbers = require_numbers
        self.require_special = require_special
        self.max_length = max_length
        self.disallow_common = disallow_common
        
        # Common passwords to disallow (this should be expanded in production)
        self.common_passwords = {
            "password", "123456", "qwerty", "admin", "welcome", 
            "password123", "admin123", "letmein", "welcome1"
        }
    
    def validate(self, password: str) -> tuple[bool, str]:
        """
        Validate a password against security policies.
        
        Args:
            password: The password to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check length
        if not password:
            return False, "Password cannot be empty"
            
        if len(password) < self.min_length:
            return False, f"Password must be at least {self.min_length} characters long"
            
        if len(password) > self.max_length:
            return False, f"Password exceeds maximum length of {self.max_length} characters"
        
        # Check complexity requirements
        if self.require_uppercase and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
            
        if self.require_lowercase and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
            
        if self.require_numbers and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
            
        if self.require_special and not any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/`~" for c in password):
            return False, "Password must contain at least one special character"
        
        # Check for common passwords
        if self.disallow_common and password.lower() in self.common_passwords:
            return False, "Password is too common and easily guessed"
        
        return True, "Password meets security requirements"


class RateLimiter:
    """Rate limiting implementation."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for given identifier."""
        now = time.time()
        user_requests = self.requests[identifier]
        
        # Remove old requests outside the window
        while user_requests and user_requests[0] <= now - self.window_seconds:
            user_requests.popleft()
        
        # Check if under limit
        if len(user_requests) < self.max_requests:
            user_requests.append(now)
            return True
        
        return False
    
    def get_reset_time(self, identifier: str) -> Optional[datetime]:
        """Get when the rate limit resets for identifier."""
        user_requests = self.requests.get(identifier)
        if not user_requests:
            return None
        
        oldest_request = user_requests[0]
        reset_time = oldest_request + self.window_seconds
        return datetime.fromtimestamp(reset_time)

class InputValidator:
    """Input validation utilities."""
    
    # Common patterns
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]{3,32}$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    SAFE_TEXT_PATTERN = re.compile(r'^[a-zA-Z0-9\s\.,!?\-_()]+$')
    
    # XSS patterns to block
    XSS_PATTERNS = [
        re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),
        re.compile(r'<iframe[^>]*>.*?</iframe>', re.IGNORECASE | re.DOTALL),
        re.compile(r'<object[^>]*>.*?</object>', re.IGNORECASE | re.DOTALL),
        re.compile(r'<embed[^>]*>', re.IGNORECASE),
    ]
    
    @classmethod
    def validate_username(cls, username: str) -> bool:
        """Validate username format."""
        return bool(cls.USERNAME_PATTERN.match(username))
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate email format."""
        return bool(cls.EMAIL_PATTERN.match(email))
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: int = 1000) -> str:
        """Sanitize text input by removing dangerous content."""
        if not isinstance(text, str):
            return ""
        
        # Truncate to max length
        text = text[:max_length]
        
        # Remove XSS patterns
        for pattern in cls.XSS_PATTERNS:
            text = pattern.sub('', text)
        
        # Remove null bytes and control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        return text.strip()
    
    @classmethod
    def validate_consciousness_prompt(cls, prompt: str) -> tuple[bool, str]:
        """Validate consciousness prompt for safety."""
        if not prompt or len(prompt.strip()) == 0:
            return False, "Prompt cannot be empty"
        
        if len(prompt) > 5000:
            return False, "Prompt is too long (max 5000 characters)"
        
        # Check for potential injection attempts
        dangerous_patterns = [
            r'system\s*prompt',
            r'ignore\s+previous\s+instructions',
            r'forget\s+everything',
            r'act\s+as\s+if',
            r'pretend\s+to\s+be',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return False, f"Prompt contains potentially dangerous content"
        
        return True, "Valid"

class SecurityAuditLogger:
    """Security audit logging system."""
    
    def __init__(self, log_file: str = "user_data/logs/security_audit.log"):
        self.log_file = log_file
        self.events = deque(maxlen=1000)
        
        # Ensure log directory exists
        from pathlib import Path
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    def log_event(self, event_type: str, user_id: str, ip_address: str, 
                  details: Dict[str, Any], severity: str = "INFO") -> None:
        """Log security event."""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'ip_address': ip_address,
            'severity': severity,
            'details': details
        }
        
        self.events.append(event)
        
        # Write to file
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            logger.error(f"Error writing security audit log: {e}")
        
        # Log to console if high severity
        if severity in ['WARN', 'ERROR', 'CRITICAL']:
            logger.warning(f"SECURITY {severity}: {event_type} from {ip_address} - {details}")
    
    def log_authentication(self, user_id: str, ip_address: str, success: bool, details: Dict[str, Any] = None) -> None:
        """Log authentication attempt."""
        self.log_event(
            'authentication',
            user_id,
            ip_address,
            {
                'success': success,
                'details': details or {}
            },
            'INFO' if success else 'WARN'
        )
    
    def log_rate_limit(self, identifier: str, ip_address: str, endpoint: str) -> None:
        """Log rate limit violation."""
        self.log_event(
            'rate_limit_exceeded',
            identifier,
            ip_address,
            {'endpoint': endpoint},
            'WARN'
        )
    
    def log_input_validation(self, user_id: str, ip_address: str, validation_type: str, content: str) -> None:
        """Log input validation failure."""
        self.log_event(
            'input_validation_failed',
            user_id,
            ip_address,
            {
                'validation_type': validation_type,
                'content_length': len(content),
                'content_preview': content[:100] + '...' if len(content) > 100 else content
            },
            'WARN'
        )

class EnhancedSecurityManager:
    """Main security management system."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.rate_limiter = RateLimiter(
            config.rate_limit_requests,
            config.rate_limit_window
        )
        self.audit_logger = SecurityAuditLogger() if config.audit_logging else None
        self.active_sessions: Dict[str, UserSession] = {}
        self.blocked_ips: set = set()
        
        # Generate JWT secret if not provided
        if config.enable_auth and not config.jwt_secret_key:
            self.config.jwt_secret_key = secrets.token_urlsafe(64)
            logger.warning("⚠️  Generated temporary JWT secret. Set CONSCIOUSNESS_JWT_SECRET for production!")
        
        logger.info("🔒 Enhanced security manager initialized")
    
    def validate_ip_address(self, ip_address: str) -> bool:
        """Validate if IP address is allowed."""
        if ip_address in self.blocked_ips:
            return False
        
        if not self.config.allowed_ips:
            return True
        
        try:
            client_ip = ipaddress.ip_address(ip_address)
            for allowed in self.config.allowed_ips:
                if '/' in allowed:
                    # CIDR notation
                    if client_ip in ipaddress.ip_network(allowed, strict=False):
                        return True
                else:
                    # Single IP
                    if client_ip == ipaddress.ip_address(allowed):
                        return True
            return False
        except Exception:
            logger.warning(f"Invalid IP address format: {ip_address}")
            return False
    
    def check_rate_limit(self, identifier: str, ip_address: str, endpoint: str = "") -> bool:
        """Check rate limit for identifier."""
        allowed = self.rate_limiter.is_allowed(identifier)
        
        if not allowed and self.audit_logger:
            self.audit_logger.log_rate_limit(identifier, ip_address, endpoint)
        
        return allowed
    
    def create_jwt_token(self, user_id: str, username: str, permissions: List[str] = None) -> str:
        """Create JWT token for user."""
        if not self.config.enable_auth:
            raise ValueError("Authentication is not enabled")
        
        payload = {
            'user_id': user_id,
            'username': username,
            'permissions': permissions or [],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=self.config.session_timeout)
        }
        
        token = jwt.encode(payload, self.config.jwt_secret_key, algorithm='HS256')
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload."""
        if not self.config.enable_auth:
            return {'user_id': 'anonymous', 'username': 'anonymous', 'permissions': []}
        
        try:
            payload = jwt.decode(token, self.config.jwt_secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    def create_session(self, user_id: str, username: str, ip_address: str, permissions: List[str] = None) -> str:
        """Create user session."""
        session_id = secrets.token_urlsafe(32)
        
        session = UserSession(
            user_id=user_id,
            username=username,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            ip_address=ip_address,
            permissions=permissions or []
        )
        
        self.active_sessions[session_id] = session
        
        if self.audit_logger:
            self.audit_logger.log_authentication(user_id, ip_address, True)
        
        logger.info(f"🔐 Session created for user {username} from {ip_address}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get user session."""
        session = self.active_sessions.get(session_id)
        
        if session:
            # Check if session expired
            if datetime.now() - session.last_activity > timedelta(seconds=self.config.session_timeout):
                self.invalidate_session(session_id)
                return None
            
            # Update last activity
            session.last_activity = datetime.now()
        
        return session
    
    def invalidate_session(self, session_id: str) -> None:
        """Invalidate user session."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            del self.active_sessions[session_id]
            logger.info(f"🔐 Session invalidated for user {session.username}")
    
    def validate_and_sanitize_input(self, text: str, input_type: str = "general") -> tuple[bool, str]:
        """Validate and sanitize user input."""
        if input_type == "consciousness_prompt":
            is_valid, message = InputValidator.validate_consciousness_prompt(text)
            if not is_valid:
                return False, message
        
        sanitized = InputValidator.sanitize_text(text)
        
        # Check if sanitization changed the content significantly
        if len(sanitized) < len(text) * 0.8:  # More than 20% removed
            if self.audit_logger:
                self.audit_logger.log_input_validation(
                    'anonymous', 
                    'unknown', 
                    input_type, 
                    text
                )
            return False, "Input contains potentially dangerous content"
        
        return True, sanitized
    
    def get_cors_headers(self, origin: str = None) -> Dict[str, str]:
        """Get CORS headers for response."""
        if not self.config.enable_cors:
            return {}
        
        headers = {
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400'
        }
        
        # Check if origin is allowed
        if origin and self.config.cors_allow_origins:
            if origin in self.config.cors_allow_origins or '*' in self.config.cors_allow_origins:
                headers['Access-Control-Allow-Origin'] = origin
        elif not self.config.cors_allow_origins or '*' in self.config.cors_allow_origins:
            headers['Access-Control-Allow-Origin'] = '*'
        
        return headers
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers for response."""
        headers = {}
        
        if self.config.content_security_policy:
            headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: blob:; "
                "connect-src 'self' ws: wss:; "
                "font-src 'self' data:;"
            )
        
        if self.config.xss_protection:
            headers['X-XSS-Protection'] = '1; mode=block'
            headers['X-Content-Type-Options'] = 'nosniff'
            headers['X-Frame-Options'] = 'DENY'
        
        headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return headers
    
    def block_ip(self, ip_address: str, reason: str = "") -> None:
        """Block IP address."""
        self.blocked_ips.add(ip_address)
        
        if self.audit_logger:
            self.audit_logger.log_event(
                'ip_blocked',
                'system',
                ip_address,
                {'reason': reason},
                'WARN'
            )
        
        logger.warning(f"🚫 IP address blocked: {ip_address} - {reason}")
    
    def unblock_ip(self, ip_address: str) -> None:
        """Unblock IP address."""
        self.blocked_ips.discard(ip_address)
        logger.info(f"✅ IP address unblocked: {ip_address}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status."""
        return {
            'authentication_enabled': self.config.enable_auth,
            'active_sessions': len(self.active_sessions),
            'blocked_ips': len(self.blocked_ips),
            'rate_limiting_enabled': True,
            'cors_enabled': self.config.enable_cors,
            'audit_logging_enabled': self.audit_logger is not None,
            'security_headers_enabled': self.config.xss_protection or self.config.content_security_policy
        }

# Decorators for security
def require_auth(security_manager: EnhancedSecurityManager):
    """Decorator to require authentication."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would be integrated with the web framework
            # Implementation depends on Gradio/FastAPI integration
            return func(*args, **kwargs)
        return wrapper
    return decorator

def rate_limit(security_manager: EnhancedSecurityManager, identifier_func: Callable = None):
    """Decorator to apply rate limiting."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This would be integrated with the web framework
            # Implementation depends on Gradio/FastAPI integration
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Global security manager
_security_manager = None

def initialize_security(config: SecurityConfig) -> EnhancedSecurityManager:
    """Initialize global security manager."""
    global _security_manager
    _security_manager = EnhancedSecurityManager(config)
    return _security_manager

def get_security_manager() -> Optional[EnhancedSecurityManager]:
    """Get global security manager."""
    return _security_manager

# Export utilities
__all__ = [
    'EnhancedSecurityManager',
    'SecurityConfig',
    'UserSession',
    'RateLimiter',
    'InputValidator',
    'SecurityAuditLogger',
    'initialize_security',
    'get_security_manager',
    'require_auth',
    'rate_limit'
]

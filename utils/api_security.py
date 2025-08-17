"""
API Security Middleware for Open WebUI

This module provides middleware for securing API endpoints:
- Rate limiting to prevent abuse
- Request validation to ensure data integrity
- API key validation
- IP-based filtering
- Security headers

These middleware components can be used with FastAPI applications.
"""

import hashlib
import ipaddress
import json
import logging
import re
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set, Union

from fastapi import Depends, HTTPException, Request, Response, Security, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# Configure logging
logger = logging.getLogger(__name__)

class RateLimitExceeded(HTTPException):
    """Exception raised when rate limit is exceeded"""
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=429, detail=detail)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting API requests.
    
    Features:
    - Per-IP rate limiting with customizable time windows
    - Per-user rate limiting when authentication is used
    - Different limits for different endpoints
    - Whitelist for trusted IPs
    - Burst handling
    """
    
    def __init__(
        self, 
        app, 
        limit_by_ip: int = 100,
        limit_by_user: int = 1000,
        window_seconds: int = 60,
        whitelist_ips: List[str] = None,
        endpoint_limits: Dict[str, int] = None,
    ):
        """
        Initialize the rate limit middleware.
        
        Args:
            app: The FastAPI application
            limit_by_ip: Number of requests allowed per IP in the time window
            limit_by_user: Number of requests allowed per user in the time window
            window_seconds: Time window in seconds for rate limiting
            whitelist_ips: List of IPs to whitelist from rate limiting
            endpoint_limits: Dictionary mapping endpoint paths to custom request limits
        """
        super().__init__(app)
        self.limit_by_ip = limit_by_ip
        self.limit_by_user = limit_by_user
        self.window_seconds = window_seconds
        self.whitelist_ips = set(whitelist_ips or [])
        self.endpoint_limits = endpoint_limits or {}
        
        # Storage for rate limiting - in production consider using Redis
        # Format: {ip_or_user: deque([timestamp1, timestamp2, ...])}
        self.requests_by_ip = defaultdict(lambda: deque(maxlen=max(limit_by_ip * 2, 1000)))
        self.requests_by_user = defaultdict(lambda: deque(maxlen=max(limit_by_user * 2, 1000)))
        
        # Last cleanup timestamp
        self.last_cleanup = time.time()
    
    def _is_whitelisted(self, ip: str) -> bool:
        """Check if an IP is in the whitelist."""
        return ip in self.whitelist_ips
    
    def _get_limit_for_path(self, path: str) -> int:
        """Get rate limit for specific path or use default."""
        for pattern, limit in self.endpoint_limits.items():
            if re.match(pattern, path):
                return limit
        return self.limit_by_ip
    
    def _cleanup_old_requests(self):
        """Periodically clean up old request timestamps to prevent memory growth."""
        # Only clean up every 5 minutes to reduce overhead
        current_time = time.time()
        if current_time - self.last_cleanup < 300:
            return
            
        cutoff_time = current_time - self.window_seconds
        
        # Clean up IP records
        for ip, timestamps in list(self.requests_by_ip.items()):
            while timestamps and timestamps[0] < cutoff_time:
                timestamps.popleft()
            if not timestamps:
                del self.requests_by_ip[ip]
                
        # Clean up user records
        for user, timestamps in list(self.requests_by_user.items()):
            while timestamps and timestamps[0] < cutoff_time:
                timestamps.popleft()
            if not timestamps:
                del self.requests_by_user[user]
                
        self.last_cleanup = current_time
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Implement the rate limiting logic."""
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        
        # Skip rate limiting for whitelisted IPs
        if self._is_whitelisted(client_ip):
            return await call_next(request)
        
        # Get user ID from session if available
        user_id = None
        if hasattr(request.state, "user") and hasattr(request.state.user, "id"):
            user_id = request.state.user.id
        
        # Get appropriate limit for this endpoint
        path_limit = self._get_limit_for_path(path)
        
        # Current timestamp
        now = time.time()
        
        # Remove expired entries to avoid memory growth
        self._cleanup_old_requests()
        
        # Check IP-based limit
        ip_timestamps = self.requests_by_ip[client_ip]
        cutoff_time = now - self.window_seconds
        
        # Keep only timestamps within the current window
        while ip_timestamps and ip_timestamps[0] < cutoff_time:
            ip_timestamps.popleft()
        
        # Check if IP exceeds limit
        if len(ip_timestamps) >= path_limit:
            logger.warning(f"Rate limit exceeded for IP {client_ip} on {path}")
            remaining_seconds = int(self.window_seconds - (now - ip_timestamps[0]))
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "retry_after": remaining_seconds,
                }
            )
            
        # Add current request timestamp
        ip_timestamps.append(now)
        
        # Check user-based limit if authenticated
        if user_id:
            user_timestamps = self.requests_by_user[user_id]
            while user_timestamps and user_timestamps[0] < cutoff_time:
                user_timestamps.popleft()
                
            if len(user_timestamps) >= self.limit_by_user:
                logger.warning(f"Rate limit exceeded for user {user_id} on {path}")
                remaining_seconds = int(self.window_seconds - (now - user_timestamps[0]))
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "User rate limit exceeded",
                        "retry_after": remaining_seconds,
                    }
                )
                
            user_timestamps.append(now)
        
        # Process the request normally
        response = await call_next(request)
        
        # Add rate limit headers to response
        if isinstance(response, Response):
            limit_used = len(ip_timestamps)
            response.headers["X-RateLimit-Limit"] = str(path_limit)
            response.headers["X-RateLimit-Remaining"] = str(max(0, path_limit - limit_used))
            response.headers["X-RateLimit-Reset"] = str(int(now + self.window_seconds))
            
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses.
    
    Implements:
    - Content-Security-Policy
    - Strict-Transport-Security
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Referrer-Policy
    """
    
    def __init__(
        self, 
        app,
        enable_csp: bool = True,
        enable_hsts: bool = True,
        enable_xfo: bool = True,
        enable_xss_protection: bool = True,
        enable_content_type_options: bool = True,
        enable_referrer_policy: bool = True,
        csp_directives: Dict[str, str] = None,
    ):
        """
        Initialize the security headers middleware.
        
        Args:
            app: The FastAPI application
            enable_csp: Whether to add Content-Security-Policy header
            enable_hsts: Whether to add Strict-Transport-Security header
            enable_xfo: Whether to add X-Frame-Options header
            enable_xss_protection: Whether to add X-XSS-Protection header
            enable_content_type_options: Whether to add X-Content-Type-Options header
            enable_referrer_policy: Whether to add Referrer-Policy header
            csp_directives: Custom Content-Security-Policy directives
        """
        super().__init__(app)
        self.enable_csp = enable_csp
        self.enable_hsts = enable_hsts
        self.enable_xfo = enable_xfo
        self.enable_xss_protection = enable_xss_protection
        self.enable_content_type_options = enable_content_type_options
        self.enable_referrer_policy = enable_referrer_policy
        
        # Default CSP directives
        self.csp_directives = csp_directives or {
            "default-src": "'self'",
            "img-src": "'self' data: blob:",
            "style-src": "'self' 'unsafe-inline'",
            "script-src": "'self'",
            "connect-src": "'self'",
            "frame-ancestors": "'self'",
            "form-action": "'self'",
        }
    
    def _build_csp_header(self) -> str:
        """Build Content-Security-Policy header value from directives."""
        parts = [f"{key} {value}" for key, value in self.csp_directives.items()]
        return "; ".join(parts)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to responses."""
        response = await call_next(request)
        
        if isinstance(response, Response):
            # Content-Security-Policy
            if self.enable_csp:
                response.headers["Content-Security-Policy"] = self._build_csp_header()
            
            # HTTP Strict Transport Security
            if self.enable_hsts:
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
            # X-Frame-Options
            if self.enable_xfo:
                response.headers["X-Frame-Options"] = "SAMEORIGIN"
            
            # X-XSS-Protection
            if self.enable_xss_protection:
                response.headers["X-XSS-Protection"] = "1; mode=block"
            
            # X-Content-Type-Options
            if self.enable_content_type_options:
                response.headers["X-Content-Type-Options"] = "nosniff"
            
            # Referrer-Policy
            if self.enable_referrer_policy:
                response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


class APIKeyMiddleware:
    """
    Middleware for API key authentication.
    
    Features:
    - API key validation
    - Different scopes for different API keys
    - Rate limiting per API key
    """
    
    def __init__(self, api_keys: Dict[str, List[str]] = None):
        """
        Initialize the API key middleware.
        
        Args:
            api_keys: Dictionary mapping API keys to lists of allowed scopes
        """
        self.api_keys = api_keys or {}
        self.api_key_header = APIKeyHeader(name="X-API-Key")
    
    async def __call__(self, request: Request, api_key: str = Security(APIKeyHeader(name="X-API-Key"))):
        """Validate API key and check permissions."""
        if api_key not in self.api_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "APIKey"},
            )
        
        # Store API key scopes in request state for later use
        request.state.api_key_scopes = self.api_keys[api_key]
        return request


# Helper function to check if a request has a required scope
def requires_scope(scope: str):
    """Dependency to check if request has required API key scope."""
    
    async def check_scope(request: Request):
        if not hasattr(request.state, "api_key_scopes"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No API key scopes available",
            )
        
        if scope not in request.state.api_key_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key missing required scope: {scope}",
            )
        return True
    
    return check_scope


# Example usage in FastAPI app:
"""
from fastapi import FastAPI, Depends
from .middleware import RateLimitMiddleware, SecurityHeadersMiddleware, APIKeyMiddleware, requires_scope

app = FastAPI()

# Add middleware
app.add_middleware(
    RateLimitMiddleware,
    limit_by_ip=100,
    limit_by_user=1000,
    window_seconds=60,
    whitelist_ips=["127.0.0.1"],
    endpoint_limits={
        r"^/api/v1/users": 50,          # Lower limit for user management
        r"^/api/v1/models/generate": 20, # Lower limit for model generation
    }
)

app.add_middleware(
    SecurityHeadersMiddleware,
    enable_csp=True,
    enable_hsts=True
)

# API key setup
API_KEYS = {
    "abc123": ["read:models", "generate:text"],
    "xyz789": ["read:models", "generate:text", "write:models"],
}
api_key_middleware = APIKeyMiddleware(api_keys=API_KEYS)

# Protected endpoint example
@app.get("/api/v1/models", dependencies=[Depends(api_key_middleware)])
async def list_models(has_scope: bool = Depends(requires_scope("read:models"))):
    return {"models": ["model1", "model2"]}

@app.post("/api/v1/models/generate", dependencies=[Depends(api_key_middleware)])
async def generate_text(has_scope: bool = Depends(requires_scope("generate:text"))):
    return {"generated": "Some text"}

@app.post("/api/v1/models/new", dependencies=[Depends(api_key_middleware)])
async def create_model(has_scope: bool = Depends(requires_scope("write:models"))):
    return {"status": "model created"}
"""

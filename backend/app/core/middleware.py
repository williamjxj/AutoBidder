"""
Performance Timing Middleware

Tracks request duration and adds timing headers to responses.
Used for measuring API performance against workflow optimization success criteria.
"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class TimingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track and log request processing time.
    
    Adds X-Response-Time header to all responses with duration in milliseconds.
    Logs slow requests (>500ms) for performance monitoring.
    """

    def __init__(self, app: ASGIApp, slow_request_threshold_ms: float = 500.0) -> None:
        """
        Initialize timing middleware.
        
        Args:
            app: ASGI application
            slow_request_threshold_ms: Threshold in ms to log slow requests (default: 500ms)
        """
        super().__init__(app)
        self.slow_request_threshold_ms = slow_request_threshold_ms

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and add timing information.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            Response with X-Response-Time header added
        """
        # Record start time with high precision
        start_time = time.perf_counter()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate duration in milliseconds
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Add timing header to response
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        
        # Log slow requests for monitoring
        if duration_ms > self.slow_request_threshold_ms:
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} "
                f"took {duration_ms:.2f}ms (threshold: {self.slow_request_threshold_ms}ms)"
            )
        
        # Log all requests in debug mode
        logger.debug(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {duration_ms:.2f}ms"
        )
        
        return response


def add_timing_middleware(app: ASGIApp, slow_threshold_ms: float = 500.0) -> None:
    """
    Helper function to add timing middleware to FastAPI app.
    
    Args:
        app: FastAPI application instance
        slow_threshold_ms: Threshold for logging slow requests (default: 500ms)
        
    Example:
        from fastapi import FastAPI
        from app.core.middleware import add_timing_middleware
        
        app = FastAPI()
        add_timing_middleware(app, slow_threshold_ms=500.0)
    """
    app.add_middleware(TimingMiddleware, slow_request_threshold_ms=slow_threshold_ms)
    logger.info(f"Timing middleware added (slow request threshold: {slow_threshold_ms}ms)")

"""
Enhanced error handling and retry mechanisms for ReefShield Backend
"""

import logging
import asyncio
import functools
from typing import Optional, Callable, Any, Type, Tuple, Dict
from datetime import datetime, timedelta
import traceback
import json
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from app.models.schemas import ErrorResponse

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


class ModelExecutionError(Exception):
    """Custom exception for model execution errors"""
    
    def __init__(self, message: str, error_code: str = "MODEL_ERROR", details: Dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()


class DataProcessingError(Exception):
    """Custom exception for data processing errors"""
    
    def __init__(self, message: str, error_code: str = "DATA_ERROR", details: Dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()


class SchedulerError(Exception):
    """Custom exception for scheduler-related errors"""
    
    def __init__(self, message: str, error_code: str = "SCHEDULER_ERROR", details: Dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()


class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self, log_errors_to_file: bool = True):
        self.log_errors_to_file = log_errors_to_file
        self.error_counts = {}
        self.last_errors = {}
        
    def log_error(
        self,
        error: Exception,
        context: str = "unknown",
        additional_data: Dict = None
    ) -> str:
        """Log error with context and return error ID"""
        error_id = f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        error_data = {
            "error_id": error_id,
            "error_type": type(error).__name__,
            "message": str(error),
            "context": context,
            "timestamp": datetime.now().isoformat(),
            "traceback": traceback.format_exc(),
            "additional_data": additional_data or {}
        }
        
        # Add custom error details if available
        if hasattr(error, 'error_code'):
            error_data["error_code"] = error.error_code
        if hasattr(error, 'details'):
            error_data["details"] = error.details
        
        # Log to application logger
        logger.error(f"Error {error_id} in {context}: {str(error)}")
        logger.debug(f"Full error details: {json.dumps(error_data, indent=2)}")
        
        # Update error statistics
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        self.last_errors[context] = error_data
        
        # Log to file if configured
        if self.log_errors_to_file:
            self._log_to_file(error_data)
        
        return error_id
    
    def _log_to_file(self, error_data: Dict) -> None:
        """Log error data to file"""
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{json.dumps(error_data)}\\n")
                
        except Exception as e:
            logger.warning(f"Failed to log error to file: {e}")
    
    def get_error_stats(self) -> Dict:
        """Get error statistics"""
        return {
            "error_counts": self.error_counts.copy(),
            "last_errors": {k: v for k, v in self.last_errors.items()},
            "total_errors": sum(self.error_counts.values())
        }
    
    def create_error_response(
        self,
        error: Exception,
        status_code: int = 500,
        context: str = "unknown"
    ) -> JSONResponse:
        """Create standardized error response"""
        error_id = self.log_error(error, context)
        
        # Determine error message based on error type
        if isinstance(error, ModelExecutionError):
            error_code = error.error_code
            message = error.message
            details = error.details
        elif isinstance(error, DataProcessingError):
            error_code = error.error_code
            message = error.message
            details = error.details
        elif isinstance(error, SchedulerError):
            error_code = error.error_code
            message = error.message
            details = error.details
        elif isinstance(error, HTTPException):
            error_code = "HTTP_ERROR"
            message = error.detail
            details = {"status_code": error.status_code}
        else:
            error_code = "INTERNAL_ERROR"
            message = "An internal server error occurred"
            details = {"error_type": type(error).__name__}
        
        error_response = ErrorResponse(
            error=error_code,
            message=message,
            details={**details, "error_id": error_id},
            timestamp=datetime.now().isoformat() + "Z"
        )
        
        return JSONResponse(
            status_code=status_code,
            content=error_response.dict()
        )


def retry_async(
    config: RetryConfig = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    log_attempts: bool = True
):
    """Decorator for async functions with retry logic"""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    if log_attempts and attempt > 0:
                        logger.info(f"Retrying {func.__name__} (attempt {attempt + 1}/{config.max_attempts})")
                    
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_attempts - 1:
                        # Last attempt failed
                        if log_attempts:
                            logger.error(f"All retry attempts failed for {func.__name__}: {str(e)}")
                        break
                    
                    # Calculate delay for next attempt
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    if config.jitter:
                        import random
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    if log_attempts:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. Retrying in {delay:.2f}s")
                    
                    await asyncio.sleep(delay)
            
            # If we get here, all attempts failed
            raise last_exception
        
        return wrapper
    return decorator


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 60.0,
    expected_exception: Type[Exception] = Exception
):
    """Circuit breaker decorator for async functions"""
    
    class CircuitBreakerState:
        def __init__(self):
            self.failure_count = 0
            self.last_failure_time = None
            self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    state = CircuitBreakerState()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            now = datetime.now()
            
            # Check if we should transition from OPEN to HALF_OPEN
            if (state.state == "OPEN" and 
                state.last_failure_time and 
                (now - state.last_failure_time).total_seconds() >= recovery_timeout):
                state.state = "HALF_OPEN"
                logger.info(f"Circuit breaker for {func.__name__} transitioning to HALF_OPEN")
            
            # If circuit is OPEN, fail fast
            if state.state == "OPEN":
                raise ModelExecutionError(
                    f"Circuit breaker is OPEN for {func.__name__}. Too many recent failures.",
                    error_code="CIRCUIT_BREAKER_OPEN",
                    details={
                        "failure_count": state.failure_count,
                        "last_failure": state.last_failure_time.isoformat() if state.last_failure_time else None
                    }
                )
            
            try:
                result = await func(*args, **kwargs)
                
                # Success - reset failure count and close circuit
                if state.state == "HALF_OPEN":
                    logger.info(f"Circuit breaker for {func.__name__} transitioning to CLOSED")
                
                state.failure_count = 0
                state.state = "CLOSED"
                return result
                
            except expected_exception as e:
                state.failure_count += 1
                state.last_failure_time = now
                
                # Check if we should open the circuit
                if state.failure_count >= failure_threshold:
                    state.state = "OPEN"
                    logger.error(f"Circuit breaker for {func.__name__} transitioning to OPEN after {state.failure_count} failures")
                
                raise e
        
        return wrapper
    return decorator


def timeout_async(seconds: float):
    """Timeout decorator for async functions"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                raise ModelExecutionError(
                    f"Function {func.__name__} timed out after {seconds} seconds",
                    error_code="TIMEOUT_ERROR",
                    details={"timeout_seconds": seconds}
                )
        return wrapper
    return decorator


def safe_async(
    default_return=None,
    log_errors: bool = True,
    suppress_exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Decorator to safely execute async functions with default fallback"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except suppress_exceptions as e:
                if log_errors:
                    logger.warning(f"Safe execution of {func.__name__} failed: {str(e)}")
                return default_return
        return wrapper
    return decorator


# Global error handler instance
error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance"""
    return error_handler
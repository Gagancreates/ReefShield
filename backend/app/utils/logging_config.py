"""
Advanced logging configuration for ReefShield Backend
"""

import logging
import logging.handlers
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import traceback

from config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        # Create base log entry
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add thread/process info if available
        if hasattr(record, 'process'):
            log_entry["process_id"] = record.process
        if hasattr(record, 'thread'):
            log_entry["thread_id"] = record.thread
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_entry["extra"] = record.extra_data
        
        # Add request info if available (for FastAPI logging)
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        if hasattr(record, 'endpoint'):
            log_entry["endpoint"] = record.endpoint
        
        return json.dumps(log_entry, default=str, ensure_ascii=False)


class ReefShieldLogger:
    """Advanced logging manager for ReefShield Backend"""
    
    def __init__(self, logs_dir: str = "logs"):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        self._loggers: Dict[str, logging.Logger] = {}
        self._initialized = False
    
    def setup_logging(self, 
                     level: str = "INFO",
                     enable_console: bool = True,
                     enable_file: bool = True,
                     enable_json: bool = True,
                     max_file_size: int = 10 * 1024 * 1024,  # 10MB
                     backup_count: int = 5) -> None:
        """Setup comprehensive logging configuration"""
        
        if self._initialized:
            return
        
        # Convert level string to logging level
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        # Create root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler with colored output
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level)
            
            # Use simple formatter for console
            console_formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # File handlers
        if enable_file:
            # General application log
            app_handler = logging.handlers.RotatingFileHandler(
                filename=self.logs_dir / "reefshield.log",
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            app_handler.setLevel(log_level)
            
            if enable_json:
                app_handler.setFormatter(JSONFormatter())
            else:
                app_handler.setFormatter(logging.Formatter(
                    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                ))
            
            root_logger.addHandler(app_handler)
            
            # Error-only log
            error_handler = logging.handlers.RotatingFileHandler(
                filename=self.logs_dir / "errors.log",
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            
            if enable_json:
                error_handler.setFormatter(JSONFormatter())
            else:
                error_handler.setFormatter(logging.Formatter(
                    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d',
                    datefmt='%Y-%m-%d %H:%M:%S'
                ))
            
            root_logger.addHandler(error_handler)
            
            # Model execution log
            model_handler = logging.handlers.RotatingFileHandler(
                filename=self.logs_dir / "model_execution.log",
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            model_handler.setLevel(logging.INFO)
            
            # Create filter for model-related logs
            class ModelFilter(logging.Filter):
                def filter(self, record):
                    return any(keyword in record.getMessage().lower() 
                             for keyword in ['model', 'execution', 'finalig', 'prediction'])
            
            model_handler.addFilter(ModelFilter())
            
            if enable_json:
                model_handler.setFormatter(JSONFormatter())
            else:
                model_handler.setFormatter(logging.Formatter(
                    fmt='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                ))
            
            root_logger.addHandler(model_handler)
            
            # API access log
            api_handler = logging.handlers.RotatingFileHandler(
                filename=self.logs_dir / "api_access.log",
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            api_handler.setLevel(logging.INFO)
            
            # Create filter for API-related logs
            class APIFilter(logging.Filter):
                def filter(self, record):
                    return any(keyword in record.name.lower() 
                             for keyword in ['uvicorn', 'fastapi', 'api', 'routes'])
            
            api_handler.addFilter(APIFilter())
            
            if enable_json:
                api_handler.setFormatter(JSONFormatter())
            else:
                api_handler.setFormatter(logging.Formatter(
                    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                ))
            
            root_logger.addHandler(api_handler)
        
        # Configure third-party loggers
        self._configure_third_party_loggers(log_level)
        
        self._initialized = True
        logging.getLogger(__name__).info("Advanced logging system initialized")
    
    def _configure_third_party_loggers(self, level: int) -> None:
        """Configure logging levels for third-party libraries"""
        # Reduce noise from third-party libraries
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.error").setLevel(logging.INFO)
        logging.getLogger("apscheduler").setLevel(logging.INFO)
        
        # Set pandas and numpy to WARNING to reduce noise
        logging.getLogger("pandas").setLevel(logging.WARNING)
        logging.getLogger("numpy").setLevel(logging.WARNING)
        
        # HTTP libraries
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("requests").setLevel(logging.WARNING)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get or create a logger with the given name"""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            self._loggers[name] = logger
        return self._loggers[name]
    
    def log_with_context(self, 
                        logger_name: str,
                        level: str,
                        message: str,
                        **context) -> None:
        """Log message with additional context"""
        logger = self.get_logger(logger_name)
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        # Create log record with extra context
        extra = {"extra_data": context} if context else {}
        logger.log(log_level, message, extra=extra)
    
    def log_api_request(self,
                       method: str,
                       endpoint: str,
                       status_code: int,
                       response_time: float,
                       user_id: Optional[str] = None,
                       request_id: Optional[str] = None) -> None:
        """Log API request with structured data"""
        logger = self.get_logger("api.access")
        
        extra = {
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "response_time_ms": response_time * 1000,
            "user_id": user_id,
            "request_id": request_id
        }
        
        message = f"{method} {endpoint} - {status_code} - {response_time:.3f}s"
        logger.info(message, extra={"extra_data": extra})
    
    def log_model_execution(self,
                          execution_id: str,
                          status: str,
                          duration: Optional[float] = None,
                          error_message: Optional[str] = None) -> None:
        """Log model execution with structured data"""
        logger = self.get_logger("model.execution")
        
        extra = {
            "execution_id": execution_id,
            "status": status,
            "duration_seconds": duration,
            "error_message": error_message
        }
        
        if status == "success":
            message = f"Model execution {execution_id} completed successfully"
            if duration:
                message += f" in {duration:.2f}s"
            logger.info(message, extra={"extra_data": extra})
        else:
            message = f"Model execution {execution_id} failed: {error_message or 'Unknown error'}"
            logger.error(message, extra={"extra_data": extra})
    
    def log_scheduler_event(self,
                          event_type: str,
                          job_id: str,
                          details: Dict[str, Any] = None) -> None:
        """Log scheduler events with structured data"""
        logger = self.get_logger("scheduler")
        
        extra = {
            "event_type": event_type,
            "job_id": job_id,
            "details": details or {}
        }
        
        message = f"Scheduler event: {event_type} for job {job_id}"
        logger.info(message, extra={"extra_data": extra})
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        stats = {
            "logs_directory": str(self.logs_dir),
            "initialized": self._initialized,
            "loggers_count": len(self._loggers),
            "log_files": []
        }
        
        # Get information about log files
        if self.logs_dir.exists():
            for log_file in self.logs_dir.glob("*.log*"):
                try:
                    stat = log_file.stat()
                    file_info = {
                        "name": log_file.name,
                        "size_bytes": stat.st_size,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    }
                    stats["log_files"].append(file_info)
                except Exception as e:
                    stats["log_files"].append({
                        "name": log_file.name,
                        "error": str(e)
                    })
        
        return stats


# Global logging manager instance
logging_manager = ReefShieldLogger()


def setup_logging(level: str = None) -> None:
    """Setup logging with configuration from settings"""
    log_level = level or settings.LOG_LEVEL
    
    logging_manager.setup_logging(
        level=log_level,
        enable_console=True,
        enable_file=True,
        enable_json=settings.ENVIRONMENT == "production"
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging_manager.get_logger(name)


def get_logging_manager() -> ReefShieldLogger:
    """Get the global logging manager"""
    return logging_manager
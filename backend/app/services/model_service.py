"""
Model service for executing and managing the finalig.py coral reef prediction model
"""

import subprocess
import sys
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import json
import uuid

from app.models.schemas import ModelExecutionStatus
from app.utils.error_handling import (
    ModelExecutionError, 
    retry_async, 
    circuit_breaker, 
    timeout_async,
    RetryConfig,
    error_handler
)
from config import settings

logger = logging.getLogger(__name__)


# Note: ModelExecutionError is now imported from error_handling module


class ModelService:
    """Service for managing coral reef prediction model execution with enhanced error handling"""
    
    def __init__(self, models_path: Optional[Path] = None):
        """Initialize ModelService with models directory path"""
        self.models_path = models_path or settings.MODELS_DIR
        self.model_script_path = self.models_path / settings.MODEL_SCRIPT
        
        # Execution tracking
        self._last_execution_time: Optional[datetime] = None
        self._last_execution_status: str = "unknown"
        self._last_error_message: Optional[str] = None
        self._execution_lock = asyncio.Lock()
        self._current_execution_id: Optional[str] = None
        
        # Error handling configuration
        self._retry_config = RetryConfig(
            max_attempts=3,
            base_delay=2.0,
            max_delay=30.0,
            exponential_base=2.0
        )
        
        logger.info(f"ModelService initialized with script: {self.model_script_path}")
    
    def check_model_script_exists(self) -> bool:
        """Check if the model script file exists"""
        exists = self.model_script_path.exists()
        logger.debug(f"Model script exists: {exists}")
        return exists
    
    def check_csv_files_exist(self) -> Dict[str, bool]:
        """Verify that required CSV files exist"""
        files_status = {
            'historical_csv': settings.historical_csv_path.exists(),
            'predictions_csv': settings.predictions_csv_path.exists(),
            'combined_14day_csv': settings.combined_14day_csv_path.exists(),
            'training_csv': settings.training_csv_path.exists(),
        }
        
        logger.debug(f"CSV files status: {files_status}")
        return files_status
    
    def get_execution_status(self) -> ModelExecutionStatus:
        """Get current model execution status"""
        # Check if model is currently running
        is_running = self._current_execution_id is not None
        
        # Format timestamps
        last_run = None
        if self._last_execution_time:
            last_run = self._last_execution_time.isoformat() + "Z"
        
        # Calculate next scheduled run (daily at configured time)
        next_run = None
        try:
            now = datetime.now()
            next_run_time = now.replace(
                hour=settings.MODEL_RUN_HOUR,
                minute=settings.MODEL_RUN_MINUTE,
                second=0,
                microsecond=0
            )
            
            # If today's run time has passed, schedule for tomorrow
            if now > next_run_time:
                next_run_time += timedelta(days=1)
            
            next_run = next_run_time.isoformat() + "Z"
            
        except Exception as e:
            logger.warning(f"Error calculating next run time: {e}")
        
        return ModelExecutionStatus(
            is_running=is_running,
            last_run=last_run,
            last_error=self._last_error_message,
            next_scheduled_run=next_run
        )
    
    @retry_async(
        config=None,  # Will use default RetryConfig
        exceptions=(ModelExecutionError, subprocess.SubprocessError, OSError),
        log_attempts=True
    )
    @circuit_breaker(
        failure_threshold=3,
        recovery_timeout=300.0,  # 5 minutes
        expected_exception=ModelExecutionError
    )
    @timeout_async(600)  # 10 minutes timeout
    async def run_model(self, force: bool = False) -> Tuple[bool, str, Optional[str]]:
        """
        Execute the finalig.py model
        Returns: (success, message, execution_id)
        """
        async with self._execution_lock:
            # Check if model is already running
            if self._current_execution_id and not force:
                return False, "Model is already running", None
            
            # Check if recently executed (within last hour) and not forced
            if (not force and 
                self._last_execution_time and 
                datetime.now() - self._last_execution_time < timedelta(hours=1)):
                return False, "Model executed recently. Use force=True to override.", None
            
            # Generate execution ID
            execution_id = str(uuid.uuid4())
            self._current_execution_id = execution_id
            
            logger.info(f"Starting model execution (ID: {execution_id})")
            
            try:
                # Validate prerequisites
                if not self.check_model_script_exists():
                    raise ModelExecutionError(
                        f"Model script not found: {self.model_script_path}",
                        error_code="SCRIPT_NOT_FOUND",
                        details={"script_path": str(self.model_script_path)}
                    )
                
                # Execute the model
                success, output, error = await self._execute_model_script_with_retry()
                
                if success:
                    self._last_execution_time = datetime.now()
                    self._last_execution_status = "success"
                    self._last_error_message = None
                    
                    logger.info(f"Model execution completed successfully (ID: {execution_id})")
                    return True, f"Model executed successfully. Output files updated.", execution_id
                else:
                    error_message = error or "Unknown error during model execution"
                    self._last_execution_status = "failed"
                    self._last_error_message = error_message
                    
                    # Create detailed error
                    model_error = ModelExecutionError(
                        f"Model execution failed: {error_message}",
                        error_code="EXECUTION_FAILED",
                        details={
                            "stdout": output[:1000] if output else None,  # Limit output size
                            "stderr": error[:1000] if error else None,
                            "execution_id": execution_id
                        }
                    )
                    
                    error_handler.log_error(model_error, "model_execution")
                    logger.error(f"Model execution failed (ID: {execution_id}): {error_message}")
                    return False, f"Model execution failed: {error_message}", execution_id
                
            except ModelExecutionError:
                # Re-raise model execution errors
                raise
            except Exception as e:
                # Wrap other exceptions in ModelExecutionError
                model_error = ModelExecutionError(
                    f"Unexpected error during model execution: {str(e)}",
                    error_code="UNEXPECTED_ERROR",
                    details={
                        "exception_type": type(e).__name__,
                        "execution_id": execution_id
                    }
                )
                
                self._last_execution_status = "error"
                self._last_error_message = str(e)
                
                error_handler.log_error(model_error, "model_execution")
                logger.error(f"Unexpected error during model execution (ID: {execution_id}): {e}")
                
                raise model_error
            
            finally:
                # Clear current execution ID
                self._current_execution_id = None
    
    async def _execute_model_script_with_retry(self) -> Tuple[bool, str, Optional[str]]:
        """Execute model script with built-in retry logic for transient failures"""
        return await self._execute_model_script()
    
    async def _execute_model_script(self) -> Tuple[bool, str, Optional[str]]:
        """
        Execute the finalig.py script using subprocess
        Returns: (success, stdout, stderr)
        """
        try:
            # Change to models directory for execution
            original_cwd = Path.cwd()
            
            logger.debug(f"Executing model script: {self.model_script_path}")
            logger.debug(f"Working directory: {self.models_path}")
            
            # Validate working directory exists and is accessible
            if not self.models_path.exists():
                raise ModelExecutionError(
                    f"Models directory does not exist: {self.models_path}",
                    error_code="MODELS_DIR_NOT_FOUND",
                    details={"models_path": str(self.models_path)}
                )
            
            if not self.models_path.is_dir():
                raise ModelExecutionError(
                    f"Models path is not a directory: {self.models_path}",
                    error_code="MODELS_PATH_INVALID",
                    details={"models_path": str(self.models_path)}
                )
            
            # Execute the Python script
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(self.model_script_path.name),
                cwd=str(self.models_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=1024*1024  # 1MB buffer limit
            )
            
            # Wait for completion with timeout (handled by decorator)
            stdout, stderr = await process.communicate()
            
            # Decode output
            stdout_text = stdout.decode('utf-8', errors='replace') if stdout else ""
            stderr_text = stderr.decode('utf-8', errors='replace') if stderr else ""
            
            # Check return code
            if process.returncode == 0:
                logger.debug("Model script executed successfully")
                logger.debug(f"Script output: {stdout_text[:500]}...")  # Log first 500 chars
                
                # Verify output files were created
                if not self._verify_output_files():
                    raise ModelExecutionError(
                        "Output files were not created or are invalid",
                        error_code="OUTPUT_FILES_MISSING",
                        details={
                            "expected_files": [
                                str(settings.historical_csv_path),
                                str(settings.predictions_csv_path),
                                str(settings.combined_14day_csv_path)
                            ]
                        }
                    )
                
                return True, stdout_text, None
            else:
                logger.error(f"Model script failed with return code: {process.returncode}")
                logger.error(f"Error output: {stderr_text}")
                
                raise ModelExecutionError(
                    f"Model script failed with return code {process.returncode}",
                    error_code="SCRIPT_EXECUTION_FAILED",
                    details={
                        "return_code": process.returncode,
                        "stdout": stdout_text[:1000] if stdout_text else None,
                        "stderr": stderr_text[:1000] if stderr_text else None
                    }
                )
                
        except ModelExecutionError:
            # Re-raise model execution errors
            raise
        except asyncio.TimeoutError:
            raise ModelExecutionError(
                "Model execution timed out",
                error_code="EXECUTION_TIMEOUT",
                details={"timeout_seconds": 600}
            )
        except OSError as e:
            raise ModelExecutionError(
                f"Operating system error during model execution: {str(e)}",
                error_code="OS_ERROR",
                details={
                    "os_error_code": getattr(e, 'errno', None),
                    "os_error_message": str(e)
                }
            )
        except Exception as e:
            logger.error(f"Unexpected exception during model execution: {e}")
            raise ModelExecutionError(
                f"Unexpected error during script execution: {str(e)}",
                error_code="UNEXPECTED_SCRIPT_ERROR",
                details={"exception_type": type(e).__name__}
            )
    
    def _verify_output_files(self) -> bool:
        """Verify that model execution created/updated the expected output files"""
        required_files = [
            settings.historical_csv_path,
            settings.predictions_csv_path,
            settings.combined_14day_csv_path,
        ]
        
        all_exist = True
        for file_path in required_files:
            if not file_path.exists():
                logger.warning(f"Expected output file missing: {file_path}")
                all_exist = False
            else:
                # Check if file was modified recently (within last 5 minutes)
                try:
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if datetime.now() - file_mtime > timedelta(minutes=5):
                        logger.warning(f"Output file not recently updated: {file_path}")
                        # Don't fail verification for this, just warn
                except Exception as e:
                    logger.warning(f"Error checking file modification time for {file_path}: {e}")
        
        return all_exist
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model and its environment"""
        try:
            info = {
                'script_path': str(self.model_script_path),
                'script_exists': self.check_model_script_exists(),
                'models_directory': str(self.models_path),
                'python_executable': sys.executable,
                'csv_files_status': self.check_csv_files_exist(),
                'execution_status': self.get_execution_status().dict(),
            }
            
            # Get script file info if it exists
            if self.model_script_path.exists():
                stat = self.model_script_path.stat()
                info['script_size_bytes'] = stat.st_size
                info['script_modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {'error': str(e)}
    
    def cancel_execution(self) -> bool:
        """Cancel current model execution if running"""
        if self._current_execution_id:
            # Note: This is a simplified implementation
            # In a production system, you'd want to properly terminate the subprocess
            logger.warning("Model execution cancellation requested but not fully implemented")
            self._current_execution_id = None
            return True
        return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on model service"""
        health_status = {
            'service': 'ModelService',
            'status': 'healthy',
            'checks': {}
        }
        
        try:
            # Check if model script exists
            health_status['checks']['script_exists'] = self.check_model_script_exists()
            
            # Check CSV files
            csv_status = self.check_csv_files_exist()
            health_status['checks']['required_files'] = all(csv_status.values())
            health_status['checks']['file_details'] = csv_status
            
            # Check execution status
            exec_status = self.get_execution_status()
            health_status['checks']['not_stuck'] = not exec_status.is_running
            
            # Overall status
            if not all([
                health_status['checks']['script_exists'],
                health_status['checks']['required_files'],
                health_status['checks']['not_stuck']
            ]):
                health_status['status'] = 'degraded'
            
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['error'] = str(e)
        
        return health_status
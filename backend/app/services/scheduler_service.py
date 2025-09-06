"""
Background scheduler service for automated model execution
"""

import logging
import asyncio
from datetime import datetime, time, timedelta
from typing import Optional, Dict, Any, Callable, Tuple
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from app.services.model_service import ModelService
from app.utils.error_handling import (
    SchedulerError,
    safe_async,
    error_handler
)
from config import settings

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing background scheduled tasks"""
    
    def __init__(self, model_service: ModelService):
        """Initialize SchedulerService with ModelService dependency"""
        self.model_service = model_service
        self.scheduler = None
        self._is_running = False
        self._last_job_result: Optional[Dict[str, Any]] = None
        self._job_history = []
        self._max_history = 10
        
        # Configure APScheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': True,  # Combine multiple pending executions into one
            'max_instances': 1,  # Only one instance of the job can run at a time
            'misfire_grace_time': 300  # 5 minutes grace time for missed jobs
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        # Add event listeners
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
        self.scheduler.add_listener(self._job_missed, EVENT_JOB_MISSED)
        
        logger.info("SchedulerService initialized")
    
    async def start(self) -> None:
        """Start the background scheduler"""
        if self._is_running:
            logger.warning("Scheduler is already running")
            return
        
        try:
            self.scheduler.start()
            self._is_running = True
            
            # Schedule the daily model execution
            await self._schedule_daily_model_run()
            
            logger.info("SchedulerService started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start SchedulerService: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the background scheduler"""
        if not self._is_running:
            logger.warning("Scheduler is not running")
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self._is_running = False
            logger.info("SchedulerService stopped successfully")
            
        except Exception as e:
            logger.error(f"Failed to stop SchedulerService: {e}")
            raise
    
    async def _schedule_daily_model_run(self) -> None:
        """Schedule daily model execution at configured time"""
        try:
            # Remove existing job if it exists
            if self.scheduler.get_job('daily_model_run'):
                self.scheduler.remove_job('daily_model_run')
            
            # Create cron trigger for daily execution
            trigger = CronTrigger(
                hour=settings.MODEL_RUN_HOUR,
                minute=settings.MODEL_RUN_MINUTE,
                second=0,
                timezone='UTC'
            )
            
            # Schedule the job
            self.scheduler.add_job(
                func=self._execute_daily_model,
                trigger=trigger,
                id='daily_model_run',
                name='Daily Coral Reef Model Execution',
                replace_existing=True
            )
            
            next_run = self.scheduler.get_job('daily_model_run').next_run_time
            logger.info(f"Daily model execution scheduled for {settings.MODEL_RUN_HOUR:02d}:{settings.MODEL_RUN_MINUTE:02d} UTC")
            logger.info(f"Next scheduled run: {next_run}")
            
        except Exception as e:
            logger.error(f"Failed to schedule daily model run: {e}")
            raise
    
    async def _execute_daily_model(self) -> None:
        """Execute the daily model run (scheduled job function)"""
        job_start_time = datetime.now()
        job_id = f"daily_run_{job_start_time.strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting scheduled model execution (Job ID: {job_id})")
        
        try:
            # Execute the model with enhanced error handling
            success, message, execution_id = await self._safe_model_execution(force=True)
            
            job_result = {
                'job_id': job_id,
                'execution_id': execution_id,
                'start_time': job_start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'success': success,
                'message': message,
                'trigger': 'scheduled'
            }
            
            # Store result
            self._last_job_result = job_result
            self._add_to_history(job_result)
            
            if success:
                logger.info(f"Scheduled model execution completed successfully (Job ID: {job_id})")
            else:
                logger.error(f"Scheduled model execution failed (Job ID: {job_id}): {message}")
                # Log the failure but don't re-raise to avoid breaking the scheduler
                error_handler.log_error(
                    SchedulerError(f"Scheduled execution failed: {message}", "SCHEDULED_EXECUTION_FAILED"),
                    "scheduled_model_execution",
                    {"job_id": job_id, "execution_id": execution_id}
                )
            
        except Exception as e:
            job_result = {
                'job_id': job_id,
                'execution_id': None,
                'start_time': job_start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'success': False,
                'message': f"Exception during scheduled execution: {str(e)}",
                'trigger': 'scheduled'
            }
            
            self._last_job_result = job_result
            self._add_to_history(job_result)
            
            # Log the error but don't re-raise to avoid breaking the scheduler
            error_handler.log_error(e, "scheduled_model_execution", {"job_id": job_id})
            logger.error(f"Exception during scheduled model execution (Job ID: {job_id}): {e}")
    
    @safe_async(default_return=(False, "Safe execution failed", None), log_errors=True)
    async def _safe_model_execution(self, force: bool = False) -> Tuple[bool, str, Optional[str]]:
        """Safely execute model with comprehensive error handling"""
        return await self.model_service.run_model(force=force)
    
    def _job_executed(self, event) -> None:
        """Handle job execution completion events"""
        logger.debug(f"Job {event.job_id} executed successfully")
    
    def _job_error(self, event) -> None:
        """Handle job execution error events"""
        logger.error(f"Job {event.job_id} encountered an error: {event.exception}")
    
    def _job_missed(self, event) -> None:
        """Handle missed job events"""
        logger.warning(f"Job {event.job_id} was missed (scheduled for {event.scheduled_run_time})")
    
    def _add_to_history(self, job_result: Dict[str, Any]) -> None:
        """Add job result to history with size limit"""
        self._job_history.append(job_result)
        
        # Keep only the most recent entries
        if len(self._job_history) > self._max_history:
            self._job_history = self._job_history[-self._max_history:]
    
    async def trigger_immediate_run(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Trigger an immediate model run outside of the schedule"""
        job_start_time = datetime.now()
        job_id = f"manual_run_{job_start_time.strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting manual model execution (Job ID: {job_id}, User: {user_id})")
        
        try:
            success, message, execution_id = await self._safe_model_execution(force=False)
            
            job_result = {
                'job_id': job_id,
                'execution_id': execution_id,
                'start_time': job_start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'success': success,
                'message': message,
                'trigger': 'manual',
                'user_id': user_id
            }
            
            self._add_to_history(job_result)
            
            if success:
                logger.info(f"Manual model execution completed successfully (Job ID: {job_id})")
            else:
                logger.warning(f"Manual model execution failed (Job ID: {job_id}): {message}")
            
            return job_result
            
        except Exception as e:
            job_result = {
                'job_id': job_id,
                'execution_id': None,
                'start_time': job_start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'success': False,
                'message': f"Exception during manual execution: {str(e)}",
                'trigger': 'manual',
                'user_id': user_id
            }
            
            self._add_to_history(job_result)
            error_handler.log_error(e, "manual_model_execution", {"job_id": job_id, "user_id": user_id})
            logger.error(f"Exception during manual model execution (Job ID: {job_id}): {e}")
            
            return job_result
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status and job information"""
        status = {
            'is_running': self._is_running,
            'jobs': [],
            'last_job_result': self._last_job_result,
            'job_history_count': len(self._job_history)
        }
        
        if self.scheduler:
            for job in self.scheduler.get_jobs():
                job_info = {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                }
                status['jobs'].append(job_info)
        
        return status
    
    def get_job_history(self, limit: int = 10) -> list:
        """Get recent job execution history"""
        return self._job_history[-limit:] if self._job_history else []
    
    async def reschedule_daily_run(self, hour: int, minute: int) -> bool:
        """Reschedule the daily model run to a new time"""
        try:
            # Validate time
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                raise ValueError("Invalid time: hour must be 0-23, minute must be 0-59")
            
            # Update settings
            settings.MODEL_RUN_HOUR = hour
            settings.MODEL_RUN_MINUTE = minute
            
            # Reschedule the job
            if self._is_running:
                await self._schedule_daily_model_run()
            
            logger.info(f"Daily model run rescheduled to {hour:02d}:{minute:02d} UTC")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reschedule daily run: {e}")
            return False
    
    async def pause_scheduler(self) -> bool:
        """Pause the scheduler (stop accepting new jobs)"""
        try:
            if self._is_running:
                self.scheduler.pause()
                logger.info("Scheduler paused")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to pause scheduler: {e}")
            return False
    
    async def resume_scheduler(self) -> bool:
        """Resume the paused scheduler"""
        try:
            if self._is_running:
                self.scheduler.resume()
                logger.info("Scheduler resumed")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to resume scheduler: {e}")
            return False
    
    def __del__(self):
        """Cleanup when service is destroyed"""
        if self._is_running and self.scheduler:
            try:
                self.scheduler.shutdown(wait=False)
            except:
                pass
"""
Model execution scheduler for ReefShield Backend
This will be implemented in Phase 5
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from config import settings

logger = logging.getLogger(__name__)

class ModelScheduler:
    """Handles daily execution of the coral reef prediction model"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def daily_model_run(self):
        """Execute model daily - to be implemented in Phase 5"""
        logger.info("Daily model run triggered")
        # Model execution logic will be implemented in Phase 5
        pass
    
    def start_scheduler(self):
        """Start the scheduler"""
        if not self.is_running:
            # Schedule daily model run
            self.scheduler.add_job(
                self.daily_model_run,
                'cron',
                hour=settings.MODEL_RUN_HOUR,
                minute=settings.MODEL_RUN_MINUTE,
                id='daily_model_run'
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info(f"Model scheduler started - will run daily at {settings.MODEL_RUN_HOUR:02d}:{settings.MODEL_RUN_MINUTE:02d}")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Model scheduler stopped")

# Global scheduler instance
scheduler = ModelScheduler()
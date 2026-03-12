"""
Automated Pipeline - Runs Every 5 Minutes
Collects cryptocurrency data continuously
"""
import schedule
import time
from datetime import datetime, timedelta
from loguru import logger
from main import CryptoPipeline

def run_pipeline_job():
    """Job function for scheduled execution"""
    pipeline = CryptoPipeline()
    try:
        pipeline.run_pipeline()
    except Exception as e:
        logger.error(f"❌ Pipeline job failed: {e}")
    finally:
        pipeline.cleanup()

def start_scheduler():
    """Start the automated scheduler"""
    logger.info("=" * 70)
    logger.info("🤖 AUTOMATED PIPELINE SCHEDULER")
    logger.info("=" * 70)
    logger.info("📅 Interval: Every 5 minutes")
    logger.info("🛑 To stop: Press Ctrl+C")
    logger.info("=" * 70 + "\n")
    
    # Schedule pipeline to run every 5 minutes
    # Every 1 minute
schedule.every(1).minutes.do(run_pipeline_job)

# Every 10 minutes
schedule.every(10).minutes.do(run_pipeline_job)

# Every hour
schedule.every().hour.do(run_pipeline_job)

# Every day at 9 AM
schedule.every().day.at("09:00").do(run_pipeline_job)
    
    # Run once immediately
    logger.info("🚀 Running initial pipeline execution...\n")
    run_pipeline_job()
    
    # Show next run time
    next_run = datetime.now() + timedelta(minutes=5)
    logger.info(f"\n⏰ Next run scheduled at: {next_run.strftime('%H:%M:%S')}")
    
    # Keep running
    iteration = 1
    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds
        
        # Update next run time display every iteration
        if iteration % 2 == 0:  # Every minute
            next_run = datetime.now() + timedelta(minutes=5)
            logger.debug(f"⏰ Next run at: {next_run.strftime('%H:%M:%S')}")
        
        iteration += 1

if __name__ == "__main__":
    try:
        start_scheduler()
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 70)
        logger.info("⛔ SCHEDULER STOPPED BY USER")
        logger.info("=" * 70)
        logger.info("👋 Goodbye!\n")
    except Exception as e:
        logger.error(f"\n❌ Scheduler error: {e}")
        logger.info("👋 Goodbye!\n")
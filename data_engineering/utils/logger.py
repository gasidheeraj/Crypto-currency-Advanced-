"""
Logging Configuration
"""
from loguru import logger
import sys
import os
from data_engineering.config.settings import settings

def setup_logger():
    """Configure application logger"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(settings.LOG_FILE_PATH)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Remove default handler
    logger.remove()
    
    # Console handler with colors
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True
    )
    
    # File handler
    logger.add(
        settings.LOG_FILE_PATH,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.LOG_LEVEL
    )
    
    logger.info("✅ Logger initialized")
    return logger

# Initialize logger
app_logger = setup_logger()
"""
Centralized Logging Configuration
=================================

This module provides a centralized logging configuration for the Tibiantis-Bot application.
It sets up logging with appropriate handlers, formatters, and levels.
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Default log levels for different components
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_BOT_LOG_LEVEL = "INFO"
DEFAULT_API_LOG_LEVEL = "INFO"
DEFAULT_DB_LOG_LEVEL = "WARNING"
DEFAULT_SCRAPER_LOG_LEVEL = "INFO"

# Log file configuration
LOG_DIR = "logs"
LOG_FILE = "tibiantis_bot.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3

def setup_logging():
    """
    Set up logging with appropriate handlers, formatters, and levels.
    
    This function configures logging for the entire application, including:
    - Console logging with colored output
    - File logging with rotation
    - Different log levels for different components
    
    Log levels can be configured through environment variables:
    - LOG_LEVEL: Overall log level (default: INFO)
    - BOT_LOG_LEVEL: Log level for bot components (default: INFO)
    - API_LOG_LEVEL: Log level for API components (default: INFO)
    - DB_LOG_LEVEL: Log level for database components (default: WARNING)
    - SCRAPER_LOG_LEVEL: Log level for scraper components (default: INFO)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(exist_ok=True)
    
    # Get log levels from environment variables or use defaults
    log_level = os.getenv("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
    bot_log_level = os.getenv("BOT_LOG_LEVEL", DEFAULT_BOT_LOG_LEVEL).upper()
    api_log_level = os.getenv("API_LOG_LEVEL", DEFAULT_API_LOG_LEVEL).upper()
    db_log_level = os.getenv("DB_LOG_LEVEL", DEFAULT_DB_LOG_LEVEL).upper()
    scraper_log_level = os.getenv("SCRAPER_LOG_LEVEL", DEFAULT_SCRAPER_LOG_LEVEL).upper()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers to avoid duplicate logs
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Create formatters
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler
    file_handler = RotatingFileHandler(
        log_dir / LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    logging.getLogger("app.bot").setLevel(bot_log_level)
    logging.getLogger("app.api").setLevel(api_log_level)
    logging.getLogger("app.db").setLevel(db_log_level)
    logging.getLogger("app.scrapers").setLevel(scraper_log_level)
    
    # Configure third-party loggers
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("sqlalchemy").setLevel(db_log_level)
    
    # Log the configuration
    logging.info("Logging configured with level: %s", log_level)
    logging.info("Bot logging level: %s", bot_log_level)
    logging.info("API logging level: %s", api_log_level)
    logging.info("Database logging level: %s", db_log_level)
    logging.info("Scraper logging level: %s", scraper_log_level)

def get_logger(name):
    """
    Get a logger with the specified name.
    
    Args:
        name (str): The name of the logger.
        
    Returns:
        logging.Logger: A logger instance.
    """
    return logging.getLogger(name)
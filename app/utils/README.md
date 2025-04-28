# Utilities Module

This directory contains utility modules used throughout the Tibiantis-Bot application.

## Logging Module

The `logging.py` module provides a centralized logging configuration for the entire application. It sets up logging with appropriate handlers, formatters, and levels.

### Features

- Console logging with formatted output
- File logging with rotation (logs are stored in the `logs` directory)
- Different log levels for different components
- Environment variable configuration

### Usage

To use the logging module in your code:

```python
import logging
from app.utils.logging import setup_logging

# Initialize logging (should be done at application startup)
setup_logging()

# Get a logger for your module
logger = logging.getLogger(__name__)

# Use the logger
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.exception("Exception message with traceback")
```

### Configuration

Log levels can be configured through environment variables:

- `LOG_LEVEL`: Overall log level (default: INFO)
- `BOT_LOG_LEVEL`: Log level for bot components (default: INFO)
- `API_LOG_LEVEL`: Log level for API components (default: INFO)
- `DB_LOG_LEVEL`: Log level for database components (default: WARNING)
- `SCRAPER_LOG_LEVEL`: Log level for scraper components (default: INFO)

These can be set in the `.env` file or as environment variables.

### Log Levels

The available log levels, in order of increasing severity:

1. DEBUG: Detailed information, typically of interest only when diagnosing problems
2. INFO: Confirmation that things are working as expected
3. WARNING: An indication that something unexpected happened, or may happen in the near future
4. ERROR: Due to a more serious problem, the software has not been able to perform some function
5. CRITICAL: A serious error, indicating that the program itself may be unable to continue running
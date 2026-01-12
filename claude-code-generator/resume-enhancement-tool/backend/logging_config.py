"""
Structured logging configuration for production environments.

Provides JSON-formatted logs for better parsing in log aggregation systems
like CloudWatch, Stackdriver, or ELK Stack.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs log records as JSON.

    This makes it easier to parse logs in production monitoring systems.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            log_data['exception_type'] = record.exc_info[0].__name__ if record.exc_info[0] else None

        # Add extra fields from record
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms

        return json.dumps(log_data)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured root logger instance
    """
    # Convert string to logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler with JSON formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)
    handler.setFormatter(JSONFormatter())

    # Add handler to logger
    logger.addHandler(handler)

    # Configure third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logger.info("Structured logging initialized", extra={
        'log_level': log_level,
        'formatter': 'JSON',
    })

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the logger (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)

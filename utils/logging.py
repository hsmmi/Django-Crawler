"""
Logger Module for Nobitex Trading Bot

This module configures logging with:
- JSON-formatted logs for file storage
- Console logs in a human-readable format
- Rotating file handler to manage log file size

Features:
- Logs messages to `logs/trader.log` with automatic rotation.
- Console logging for real-time debugging.
- Supports structured logging with extra fields.

Usage:
    from src.logger import logger
    logger.info("Fetching order book for BTC/USDT")
    logger.error("Something went wrong", exc_info=True)

Author: Hesoyam
"""

import datetime as dt
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from django.conf import settings

LOCAL_TZ = settings.LOCAL_TZ


class MyJsonFormatter(logging.Formatter):
    """
    Custom JSON Formatter for structured logging.

    Converts log records into JSON format with the following fields:
    - message: Log message
    - timestamp: Log creation time in ISO 8601 format
    - level: Log level (INFO, ERROR, etc.)
    - exception: Exception details (if any)
    - stack: Stack trace (if any)
    - Any extra attributes passed with `logger.info(..., extra={"key": value})`
    """

    def __init__(self, *, fmt_keys: dict[str, str] = None):
        """
        Initializes the JSON formatter.

        Args:
            fmt_keys (dict[str, str]): A mapping of field names to custom keys.
        """
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys else {}

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats the log record as a JSON string.

        Args:
            record (logging.LogRecord): The log record.

        Returns:
            str: The formatted JSON log entry.
        """
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)  # Convert dictionary to JSON string

    def _prepare_log_dict(self, record: logging.LogRecord) -> dict:
        """
        Prepares the log entry dictionary.

        Args:
            record (logging.LogRecord): The log record.

        Returns:
            dict: The structured log entry.
        """
        always_keys = {
            "msg": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(record.created, LOCAL_TZ).strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
            "levelname": record.levelname,
            "filename": record.filename,
            "funcName": record.funcName,
            "lineno": record.lineno,
        }
        if record.exc_info:
            always_keys["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            always_keys["stack"] = self.formatStack(record.stack_info)

        # Format log message with specified key mappings
        message = {
            val: always_keys.pop(key, getattr(record, key, None))
            for key, val in self.fmt_keys.items()
        }
        message.update(always_keys)

        # Include extra fields from log record
        for key, val in record.__dict__.items():
            if key not in message and key not in self.fmt_keys:
                message[key] = val

        return message


def setup_logger() -> logging.Logger:
    """
    Configures the logger with JSON formatting, console logging, and file rotation.

    - Logs messages to `logs/trader.log`
    - Rotates log files when they exceed 5MB (keeps last 3 logs)
    - Prints logs to the console in human-readable format

    Returns
    -------
        logging.Logger: The configured logger instance.
    """
    # Create the logs directory if it doesn't exist
    log_dir = settings.LOG_DIR  # Get log directory from settings.py
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, "django.log")
    warn_log_file = os.path.join(log_dir, "django_warn.log")

    # Define a JSON formatter for file logs
    json_formatter = MyJsonFormatter(
        fmt_keys={
            "levelname": "lvl",
            "msg": "msg",
            "timestamp": "time",
            "filename": "file",
            "module": "module",
            "lineno": "line",
            "funcName": "func",
        }
    )

    # **Rotating File Handler** (max 5MB per log file, keeps 5 backups)
    file_handler = RotatingFileHandler(log_file, maxBytes=5_000_000, backupCount=5)
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(logging.DEBUG)

    # **Rotating Warn File Handler** for warnings and above
    warn_handler = RotatingFileHandler(warn_log_file, maxBytes=5_000_000, backupCount=2)
    warn_handler.setFormatter(json_formatter)
    warn_handler.setLevel(logging.WARNING)

    # **Console Handler** (for human-readable output)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter(
            "[%(levelname)s] %(message)s | %(asctime)s (%(filename)s:%(module)s:%(lineno)d:%(funcName)s)"
            # LOCAL_TZ is the timezone object
            ,
            datefmt="%Y-%m-%d %H:%M:%S %Z",
        )
    )
    console_handler.setLevel(logging.INFO)

    # Configure the main logger
    logger = logging.getLogger("DjangoLogger")
    logger.setLevel(logging.DEBUG)  # Capture all levels (DEBUG, INFO, ERROR, etc.)
    logger.addHandler(file_handler)
    logger.addHandler(warn_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()
# Seprate each run of the program
logger.info("=" * 100)

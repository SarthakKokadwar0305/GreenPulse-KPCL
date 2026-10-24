"""
GreenPulse AI - Enterprise Structured Rotating Logging Configuration
Enterprise logging system adhering to industrial observability standards.
Features:
- ISO 8601 timestamps with millisecond precision
- Console standard output handler
- Rotating file handler writing to backend/logs/greenpulse_ai.log (10 MB max, 5 backups)
- Domain loggers for predictions, alerts, thresholds, and recommendations
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE_PATH = LOGS_DIR / "greenpulse_ai.log"


class EnterpriseLogFormatter(logging.Formatter):
    """Formats logs with ISO timestamp, component name, and severity levels."""
    
    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z")
        level = record.levelname.ljust(7)
        component = f"[{record.name}]".ljust(25)
        message = record.getMessage()
        
        formatted = f"{timestamp} | {level} | {component} | {message}"
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"
        return formatted


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configures structured root logging with stream and rotating file handlers."""
    root_logger = logging.getLogger("greenpulse")
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.handlers.clear()

    formatter = EnterpriseLogFormatter()

    # 1. Console Stream Handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)

    # 2. Rotating File Handler (10MB per file, 5 backup files)
    try:
        file_handler = RotatingFileHandler(
            LOG_FILE_PATH,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not initialize RotatingFileHandler at {LOG_FILE_PATH}: {e}")

    root_logger.propagate = False
    return root_logger


logger = setup_logging()

# Specialized Domain Loggers
prediction_logger = logging.getLogger("greenpulse.predictions")
alert_logger = logging.getLogger("greenpulse.alerts")
threshold_logger = logging.getLogger("greenpulse.thresholds")
recommendation_logger = logging.getLogger("greenpulse.recommendations")
rule_logger = logging.getLogger("greenpulse.rules")

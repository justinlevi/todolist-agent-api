import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from pythonjsonlogger import jsonlogger

from src.config import settings

# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure JSON formatter
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name

# Create logger
logger = logging.getLogger("api")
logger.setLevel(settings.LOG_LEVEL)

# Create JSON formatter
json_formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(json_formatter)
logger.addHandler(console_handler)

# Create rotating file handler
file_handler = RotatingFileHandler(
    log_dir / "api.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(json_formatter)
logger.addHandler(file_handler)

def get_logger():
    return logger

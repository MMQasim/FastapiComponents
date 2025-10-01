import logging
import sys
from logging.handlers import RotatingFileHandler

class AppLogger:
    def __init__(
        self,
        name: str = "Logger",
        level: int = logging.INFO,
        log_file: str = "app.log",
        max_bytes: int = 5 * 1024 * 1024,
        backup_count: int = 5,
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Prevent duplicate handlers if logger is reused
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(console_handler)

            # Rotating file handler
            file_handler = RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
            )
            file_handler.setFormatter(self._get_formatter())
            self.logger.addHandler(file_handler)

    def _get_formatter(self):
        return logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def get_logger(self):
        return self.logger
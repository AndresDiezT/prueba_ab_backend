import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.config import settings


def configure_logging() -> None:
    log_format = "%(asctime)s %(levelname)s %(name)s - %(message)s"
    formatter = logging.Formatter(log_format)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if not any(getattr(handler, "_ab_console", False) for handler in root_logger.handlers):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler._ab_console = True  # type: ignore[attr-defined]
        root_logger.addHandler(console_handler)

    log_path = Path(settings.log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if not any(getattr(handler, "_ab_file", False) for handler in root_logger.handlers):
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler._ab_file = True  # type: ignore[attr-defined]
        root_logger.addHandler(file_handler)

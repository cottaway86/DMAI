import logging
import os
from typing import Any


DEFAULT_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)


class ContextFormatter(logging.Formatter):
    """Append non-standard LogRecord attributes as key=value context."""

    _standard_record_keys = set(logging.makeLogRecord({}).__dict__.keys())
    _standard_record_keys.update({"asctime", "message"})

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)

        context: dict[str, Any] = {}
        for key, value in record.__dict__.items():
            if key in self._standard_record_keys:
                continue
            context[key] = value

        if not context:
            return message

        context_str = " ".join(f"{key}={value!r}" for key, value in sorted(context.items()))
        return f"{message} | {context_str}"


def setup_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(
        ContextFormatter(DEFAULT_LOG_FORMAT, datefmt="%Y-%m-%d %H:%M:%S")
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

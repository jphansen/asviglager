"""Logging module with LogBull integration."""
import time
import threading
from typing import Any, Dict, Optional

from app.core.config import settings


class Logger:
    """Application logger wrapping LogBull with console fallback."""

    _instance: Optional["Logger"] = None
    _lock = threading.Lock()

    def __init__(self):
        self._logbull = None
        if settings.logbull_enabled:
            try:
                from logbull import LogBullLogger
                self._logbull = LogBullLogger(
                    host=settings.logbull_host,
                    project_id=settings.logbull_project_id,
                )
            except ImportError:
                pass

    @classmethod
    def get_logger(cls) -> "Logger":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _log(self, level: str, message: str, fields: Optional[Dict[str, Any]] = None):
        fields = fields or {}
        prefix = {"error": "✗", "warning": "⚠", "info": "✓", "debug": "→"}.get(level, "•")
        print(f"{prefix} {message}")
        if self._logbull:
            try:
                getattr(self._logbull, level)(message, fields=fields)
            except Exception:
                pass

    def info(self, message: str, fields: Optional[Dict[str, Any]] = None):
        self._log("info", message, fields)

    def error(self, message: str, fields: Optional[Dict[str, Any]] = None):
        self._log("error", message, fields)

    def warning(self, message: str, fields: Optional[Dict[str, Any]] = None):
        self._log("warning", message, fields)

    def debug(self, message: str, fields: Optional[Dict[str, Any]] = None):
        self._log("debug", message, fields)

    def with_context(self, context: Dict[str, Any]) -> "Logger":
        if not self._logbull:
            return self
        try:
            session = self._logbull.with_context(context)
        except Exception:
            return self
        wrapped = Logger.__new__(Logger)
        wrapped._logbull = session
        return wrapped

    def flush(self):
        if self._logbull:
            try:
                self._logbull.flush()
            except Exception:
                pass
        time.sleep(1)


logger = Logger.get_logger()

"""JSON log formatter for CI/CD environments.

Emits structured JSON lines to stderr, replacing Rich's human-readable
output when ``--json-logs`` is passed to the root CLI command.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone


class JsonLogFormatter(logging.Formatter):
    """Emit log records as single-line JSON objects.

    Output schema per line::

        {
            "timestamp": "2026-04-24T17:30:00.000Z",
            "level": "INFO",
            "logger": "gemstack.orchestration.executor",
            "message": "Acquired lock: .agent/.gemstack.lock"
        }

    Exception info, if present, is appended to the ``message`` field
    so every record is a single parseable JSON line.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as a JSON line."""
        message = record.getMessage()

        # Append exception info to message if present
        if record.exc_info and record.exc_info[0] is not None:
            exc_text = self.formatException(record.exc_info)
            message = f"{message}\n{exc_text}"

        entry = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": message,
        }
        return json.dumps(entry, ensure_ascii=False)

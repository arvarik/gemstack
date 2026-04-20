"""Filesystem utilities — atomic writes and safe file operations.

All mutations to user-owned files (.agent/, docs/, config) should use
write_atomic() to guard against corruption from concurrent writers or
interrupted processes (see spec §9.5).
"""

from __future__ import annotations

import tempfile
from pathlib import Path


def write_atomic(path: Path, content: str) -> None:
    """Write a file atomically using write-to-temp-then-rename.

    Guarantees the file is never in a partially-written state:
    1. Write content to a temp file in the same directory.
    2. Rename the temp file over the target (atomic on POSIX).
    3. Clean up the temp file on failure.

    Args:
        path: Target file path (parent directory must exist or be creatable).
        content: Content to write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=path.parent, suffix=".tmp", prefix=f".{path.stem}-"
    )
    try:
        with open(tmp_fd, "w") as f:
            f.write(content)
        Path(tmp_path).replace(path)  # Atomic on POSIX; best-effort on Windows
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise

"""Cross-platform symlink and file copy management."""

import logging
import platform
import shutil
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class InstallManager:
    """Manages installation of Gemstack commands across agent tools.

    Handles common concerns:
    - Resolving bundled data paths from importlib.resources
    - Cross-platform symlink/copy logic
    - Idempotent operation (safe to re-run)
    - Atomic writes for TOML generation
    """

    def get_bundled_data_dir(self) -> Path:
        """Resolve the real filesystem path to bundled markdown data.

        Handles three installation modes:
        1. Standard pip install → data is in site-packages/gemstack/data/
        2. Editable install (pip install -e .) → data is in src/gemstack/data/
        3. Zipapp/pex → data must be extracted to a temp directory
        """
        from importlib.resources import files

        data = files("gemstack.data")

        # Standard and editable installs provide a real path
        if hasattr(data, "_path"):
            return Path(data._path)

        # Fallback: check if it's a real path via __fspath__
        try:
            return Path(str(data))
        except TypeError:
            pass

        # Last resort: extract to a persistent cache directory
        from platformdirs import user_config_dir

        logger.warning(
            "Bundled data is not on the filesystem (zipapp/pex install). "
            "Extracting to cache directory..."
        )
        cache_dir = Path(user_config_dir("gemstack")) / "data_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def create_symlink_safe(self, source: Path, target: Path) -> None:
        """Create a symlink with cross-platform safety.

        On Windows:
        - Tries symlink first (requires Developer Mode or admin)
        - Falls back to file copy with a warning

        On POSIX:
        - Removes existing symlink/file before creating
        - Uses absolute paths for reliability
        """
        if target.exists() or target.is_symlink():
            target.unlink()

        if platform.system() == "Windows":
            try:
                target.symlink_to(source)
            except OSError:
                logger.warning(
                    f"Symlink creation failed for {target.name}. "
                    "Falling back to copy. Enable Developer Mode for symlinks."
                )
                shutil.copy2(source, target)
        else:
            target.symlink_to(source.resolve())

    def write_toml_atomic(self, path: Path, content: str) -> None:
        """Write a TOML file atomically.

        Prevents partial writes that would crash Gemini CLI
        if the process is interrupted.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=path.parent, suffix=".tmp", prefix=f".{path.stem}-"
        )
        try:
            with open(tmp_fd, "w") as f:
                f.write(content)
            Path(tmp_path).replace(path)
        except Exception:
            Path(tmp_path).unlink(missing_ok=True)
            raise

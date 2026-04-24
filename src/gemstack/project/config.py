"""Global Gemstack configuration management."""

from pathlib import Path
from typing import Any

from platformdirs import user_config_dir
from pydantic import BaseModel, Field, SecretStr


class GemstackConfig(BaseModel):
    """Global Gemstack configuration.

    Stored at:
    - macOS:   ~/Library/Application Support/gemstack/config.toml
    - Linux:   ~/.config/gemstack/config.toml
    - Windows: %APPDATA%/gemstack/config.toml

    The gemini_api_key uses SecretStr to prevent accidental exposure
    in repr(), model_dump(), logs, and error messages (see spec §9.7).
    """

    gemini_api_key: SecretStr | None = None
    default_model: str = "gemini-3.1-pro-preview"
    default_topology: list[str] | None = None
    custom_templates_dir: str | None = None
    projects: list[str] = Field(default_factory=list)  # For `gemstack matrix`
    copy_mode: bool = False  # Global default for symlink vs copy

    @classmethod
    def config_path(cls) -> Path:
        """Get the platform-appropriate config file path."""
        return Path(user_config_dir("gemstack")) / "config.toml"

    @classmethod
    def load(cls) -> "GemstackConfig":
        """Load config from disk, creating defaults if missing."""
        path = cls.config_path()
        if path.exists():
            import sys

            if sys.version_info >= (3, 11):
                import tomllib
            else:
                import tomli as tomllib
            return cls.model_validate(tomllib.loads(path.read_text()))
        return cls()

    def get_api_key(self) -> str | None:
        """Get the raw API key value, or None if not set.

        This is the ONLY sanctioned way to access the key's plaintext
        value. Using this method makes audit grep easy: search for
        'get_api_key' to find every exposure site.
        """
        if self.gemini_api_key is None:
            return None
        return self.gemini_api_key.get_secret_value()

    def save(self) -> None:
        """Persist config to disk atomically.

        Uses write-to-temp-then-rename pattern to prevent corruption
        if the process is interrupted mid-write.
        """
        import tomli_w

        from gemstack.utils.fileutil import write_atomic

        path = self.config_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        # Serialize with SecretStr values exposed for TOML persistence
        data = self._serializable_dump()
        content = tomli_w.dumps(data)
        write_atomic(path, content)

    def _serializable_dump(self) -> dict[str, Any]:
        """Dump model data with SecretStr values exposed for persistence."""
        data = self.model_dump(exclude_none=True)
        # SecretStr serializes as '**********' by default; expose for TOML
        if self.gemini_api_key is not None:
            data["gemini_api_key"] = self.gemini_api_key.get_secret_value()
        return data

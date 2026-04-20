"""Gemini CLI adapter — TOML wrapper generation (Phase 2)."""

from pathlib import Path

from gemstack.adapters.base import InstallResult


class GeminiCLIAdapter:
    """Generates TOML command wrappers for Gemini CLI.

    Full implementation coming in Phase 2.
    """

    TARGET_DIR = Path.home() / ".gemini" / "commands"

    @property
    def name(self) -> str:
        return "Gemini CLI"

    @property
    def is_available(self) -> bool:
        return self.TARGET_DIR.parent.exists()

    def install(self, data_dir: Path, copy_mode: bool = False) -> InstallResult:
        """Install TOML wrappers (Coming in v0.2.0)."""
        if not self.TARGET_DIR.parent.exists():
            return InstallResult(
                success=False,
                installed_count=0,
                skipped_count=0,
                errors=["Gemini CLI directory not found"],
            )

        self.TARGET_DIR.mkdir(parents=True, exist_ok=True)
        return InstallResult(
            success=True,
            installed_count=0,
            skipped_count=0,
            warnings=["TOML wrapper generation coming in v0.2.0"],
        )

    def uninstall(self) -> InstallResult:
        """Remove TOML wrappers (Coming in v0.2.0)."""
        return InstallResult(
            success=True,
            installed_count=0,
            skipped_count=0,
            warnings=["Gemini CLI TOML cleanup coming in v0.2.0"],
        )

    def verify(self) -> list[str]:
        """Verify Gemini CLI installation integrity."""
        return []

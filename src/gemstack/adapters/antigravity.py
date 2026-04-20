"""Antigravity IDE adapter."""

import platform
import shutil
from pathlib import Path

from gemstack.adapters.base import InstallResult


class AntigravityAdapter:
    """Installs Gemstack commands as Antigravity global workflows."""

    TARGET_DIR = Path.home() / ".gemini" / "antigravity" / "global_workflows"

    @property
    def name(self) -> str:
        return "Antigravity"

    @property
    def is_available(self) -> bool:
        return self.TARGET_DIR.parent.exists()

    def install(self, data_dir: Path, copy_mode: bool = False) -> InstallResult:
        """Symlink (or copy) all .md files into global workflows directory."""
        self.TARGET_DIR.mkdir(parents=True, exist_ok=True)
        errors: list[str] = []
        installed = 0
        skipped = 0

        for subdir in ["roles", "phases", "workflows", "topologies"]:
            source_dir = data_dir / subdir
            if not source_dir.exists():
                continue
            for md_file in sorted(source_dir.glob("*.md")):
                target = self.TARGET_DIR / md_file.name
                try:
                    if copy_mode or (platform.system() == "Windows"):
                        shutil.copy2(md_file, target)
                    else:
                        if target.exists() or target.is_symlink():
                            target.unlink()
                        target.symlink_to(md_file)
                    installed += 1
                except OSError as e:
                    errors.append(f"Failed to link {md_file.name}: {e}")

        return InstallResult(
            success=len(errors) == 0,
            installed_count=installed,
            skipped_count=skipped,
            errors=errors,
            warnings=[],
        )

    def uninstall(self) -> InstallResult:
        """Remove all Gemstack symlinks from Antigravity."""
        if not self.TARGET_DIR.exists():
            return InstallResult(success=True, installed_count=0, skipped_count=0)

        removed = 0
        for link in self.TARGET_DIR.iterdir():
            if link.is_symlink():
                link.unlink()
                removed += 1

        return InstallResult(
            success=True,
            installed_count=removed,
            skipped_count=0,
        )

    def verify(self) -> list[str]:
        """Verify Antigravity installation integrity."""
        issues: list[str] = []
        if not self.TARGET_DIR.exists():
            issues.append("Antigravity global_workflows directory not found")
            return issues

        broken = [
            f.name
            for f in self.TARGET_DIR.iterdir()
            if f.is_symlink() and not f.resolve().exists()
        ]
        if broken:
            issues.append(f"Broken symlinks: {', '.join(broken)}")

        return issues

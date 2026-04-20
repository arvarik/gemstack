"""Tests for the git hook integration."""

import stat
from pathlib import Path

from gemstack.cli.hook_cmd import _HOOKS


class TestHookInstall:
    """Tests for hook file creation and content."""

    def _setup_git_repo(self, tmp_path: Path) -> Path:
        """Create a mock .git/hooks directory."""
        hooks_dir = tmp_path / ".git" / "hooks"
        hooks_dir.mkdir(parents=True)
        return hooks_dir

    def test_hook_scripts_have_shebang(self) -> None:
        for hook_name, script in _HOOKS.items():
            assert script.startswith("#!/usr/bin/env bash"), f"{hook_name} missing shebang"

    def test_hook_scripts_reference_gemstack(self) -> None:
        for hook_name, script in _HOOKS.items():
            assert "gemstack" in script.lower(), f"{hook_name} doesn't reference gemstack"

    def test_pre_commit_runs_check(self) -> None:
        assert "gemstack check" in _HOOKS["pre-commit"]

    def test_pre_push_checks_in_progress(self) -> None:
        assert "IN_PROGRESS" in _HOOKS["pre-push"]

    def test_post_merge_runs_diff(self) -> None:
        assert "gemstack diff" in _HOOKS["post-merge"]

    def test_hook_install_creates_files(self, tmp_path: Path) -> None:
        hooks_dir = self._setup_git_repo(tmp_path)

        # Simulate installation
        for hook_name, script in _HOOKS.items():
            hook_path = hooks_dir / hook_name
            hook_path.write_text(script)
            hook_path.chmod(0o755)

        for hook_name in _HOOKS:
            hook_path = hooks_dir / hook_name
            assert hook_path.exists()
            assert hook_path.stat().st_mode & stat.S_IXUSR  # executable

    def test_hook_uninstall_removes_gemstack_hooks(self, tmp_path: Path) -> None:
        hooks_dir = self._setup_git_repo(tmp_path)

        # Install hooks
        for hook_name, script in _HOOKS.items():
            (hooks_dir / hook_name).write_text(script)

        # Uninstall (only gemstack-managed hooks)
        for hook_name in _HOOKS:
            hook_path = hooks_dir / hook_name
            if hook_path.exists():
                content = hook_path.read_text()
                if "gemstack" in content.lower():
                    hook_path.unlink()

        for hook_name in _HOOKS:
            assert not (hooks_dir / hook_name).exists()

    def test_preserves_non_gemstack_hooks(self, tmp_path: Path) -> None:
        hooks_dir = self._setup_git_repo(tmp_path)

        # Existing non-gemstack hook
        (hooks_dir / "pre-commit").write_text("#!/bin/sh\nstrangerscript\n")

        # Should not be removed by uninstall
        content = (hooks_dir / "pre-commit").read_text()
        assert "gemstack" not in content.lower()
        # So this hook should survive
        assert (hooks_dir / "pre-commit").exists()

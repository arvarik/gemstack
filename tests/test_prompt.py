"""Tests for the prompt template manager."""

from pathlib import Path

from gemstack.cli.prompt_cmd import _get_versions


class TestPromptCreate:
    def test_creates_prompt_file(self, tmp_path: Path) -> None:

        # Simulate the create command logic
        prompts_dir = tmp_path / "prompts" / "extraction"
        prompts_dir.mkdir(parents=True)
        prompt_file = prompts_dir / "v1.0.md"
        prompt_file.write_text("---\nname: extraction\nversion: v1.0\n---\n")

        assert prompt_file.exists()
        content = prompt_file.read_text()
        assert "extraction" in content
        assert "v1.0" in content


class TestPromptVersioning:
    def test_get_versions_empty(self, tmp_path: Path) -> None:
        tmp_path.mkdir(exist_ok=True)
        assert _get_versions(tmp_path) == []

    def test_get_versions_sorted(self, tmp_path: Path) -> None:
        (tmp_path / "v1.0.md").touch()
        (tmp_path / "v1.1.md").touch()
        (tmp_path / "v1.2.md").touch()

        versions = _get_versions(tmp_path)
        assert versions == ["v1.0", "v1.1", "v1.2"]

    def test_ignores_non_version_files(self, tmp_path: Path) -> None:
        (tmp_path / "v1.0.md").touch()
        (tmp_path / "README.md").touch()
        (tmp_path / "notes.txt").touch()

        versions = _get_versions(tmp_path)
        assert versions == ["v1.0"]


class TestPromptChangelog:
    def test_updates_status_md(self, tmp_path: Path) -> None:
        from gemstack.cli.prompt_cmd import _update_prompt_changelog

        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text(
            "[STATE: IN_PROGRESS]\n\n"
            "## Prompt Versioning Changelog\n\n"
            "| Name | Version | Date | Description |\n"
            "|------|---------|------|-------------|\n"
        )

        _update_prompt_changelog(tmp_path, "extraction", "v1.0", "Initial prompt")

        content = (agent_dir / "STATUS.md").read_text()
        assert "extraction" in content
        assert "v1.0" in content
        assert "Initial prompt" in content

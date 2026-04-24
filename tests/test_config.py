"""Tests for the configuration module."""

from pathlib import Path

import pytest

from gemstack.project.config import GemstackConfig


class TestGemstackConfig:
    """Test configuration load/save and defaults."""

    def test_default_values(self) -> None:
        config = GemstackConfig()
        assert config.gemini_api_key is None
        assert config.default_model == "gemini-3.1-pro-preview"
        assert config.default_topology is None
        assert config.custom_templates_dir is None
        assert config.projects == []
        assert config.copy_mode is False

    def test_config_path_is_platform_appropriate(self) -> None:
        path = GemstackConfig.config_path()
        assert "gemstack" in str(path)
        assert path.name == "config.toml"

    def test_load_returns_defaults_when_no_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        # When no config file exists, load should return defaults
        config_path = tmp_path / "nonexistent" / "config.toml"
        monkeypatch.setattr(GemstackConfig, "config_path", classmethod(lambda cls: config_path))
        config = GemstackConfig.load()
        assert config.default_model == "gemini-3.1-pro-preview"

    def test_save_and_load_roundtrip(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Config should survive a save/load roundtrip."""
        config_path = tmp_path / "config.toml"
        monkeypatch.setattr(GemstackConfig, "config_path", classmethod(lambda cls: config_path))

        # Save with custom values
        from pydantic import SecretStr
        config = GemstackConfig(
            gemini_api_key=SecretStr("test-key-123"),
            default_model="gemini-2.5-pro",
            copy_mode=True,
        )
        config.save()

        # Load and verify
        loaded = GemstackConfig.load()
        assert loaded.get_api_key() == "test-key-123"
        assert loaded.default_model == "gemini-2.5-pro"
        assert loaded.copy_mode is True

    def test_save_creates_parent_dirs(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        config_path = tmp_path / "nested" / "dir" / "config.toml"
        monkeypatch.setattr(GemstackConfig, "config_path", classmethod(lambda cls: config_path))

        config = GemstackConfig()
        config.save()
        assert config_path.exists()

    def test_model_dump_excludes_none(self) -> None:
        config = GemstackConfig()
        dumped = config.model_dump(exclude_none=True)
        assert "gemini_api_key" not in dumped
        assert "default_model" in dumped

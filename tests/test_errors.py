"""Tests for the error hierarchy module."""

from gemstack.errors import (
    ConfigurationError,
    GemstackError,
    NetworkError,
    PluginError,
    ProjectError,
    SymlinkError,
    ValidationError,
)


class TestGemstackError:
    """Test the base error class and its subclasses."""

    def test_base_error_has_message(self) -> None:
        err = GemstackError("Something went wrong")
        assert str(err) == "Something went wrong"

    def test_base_error_has_suggestion(self) -> None:
        err = GemstackError("Something went wrong", suggestion="Try this fix")
        assert err.suggestion == "Try this fix"

    def test_base_error_default_empty_suggestion(self) -> None:
        err = GemstackError("Something went wrong")
        assert err.suggestion == ""

    def test_configuration_error_inherits(self) -> None:
        err = ConfigurationError(
            "Gemini API key not configured",
            suggestion="Run `gemstack config set gemini-api-key YOUR_KEY`",
        )
        assert isinstance(err, GemstackError)
        assert "Gemini API key" in str(err)
        assert "gemstack config" in err.suggestion

    def test_project_error_inherits(self) -> None:
        err = ProjectError(
            "No .agent/ directory found",
            suggestion="Run `gemstack init` to initialize this project",
        )
        assert isinstance(err, GemstackError)

    def test_validation_error_inherits(self) -> None:
        err = ValidationError("3 validation errors found")
        assert isinstance(err, GemstackError)

    def test_network_error_inherits(self) -> None:
        err = NetworkError("Failed to connect to Gemini API")
        assert isinstance(err, GemstackError)

    def test_symlink_error_inherits(self) -> None:
        err = SymlinkError(
            "Cannot create symlink",
            suggestion="On Windows, enable Developer Mode or use --copy-mode",
        )
        assert isinstance(err, GemstackError)

    def test_plugin_error_inherits(self) -> None:
        err = PluginError("Plugin crashed")
        assert isinstance(err, GemstackError)

    def test_all_errors_are_catchable_as_base(self) -> None:
        """All error types should be catchable via GemstackError."""
        error_types = [
            ConfigurationError,
            ProjectError,
            ValidationError,
            NetworkError,
            SymlinkError,
            PluginError,
        ]
        for error_cls in error_types:
            try:
                raise error_cls("test")
            except GemstackError:
                pass  # Expected

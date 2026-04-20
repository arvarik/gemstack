"""Structured error hierarchy for Gemstack.

All errors inherit from GemstackError and produce actionable suggestions —
never raw tracebacks for user-facing commands.
"""


class GemstackError(Exception):
    """Base error for all Gemstack operations.

    All subclasses must provide:
    - A human-readable message
    - A suggestion for how to fix the issue
    """

    def __init__(self, message: str, suggestion: str = "") -> None:
        super().__init__(message)
        self.suggestion = suggestion


class ConfigurationError(GemstackError):
    """Configuration is missing or invalid.

    Examples:
        - "Gemini API key not configured"
        - suggestion: "Run `gemstack config set gemini-api-key YOUR_KEY`"
    """


class ProjectError(GemstackError):
    """Project structure is invalid or missing.

    Examples:
        - "No .agent/ directory found"
        - suggestion: "Run `gemstack init` to initialize this project"
    """


class ValidationError(GemstackError):
    """Validation checks failed.

    Examples:
        - "3 validation errors found in .agent/"
        - suggestion: "Run `gemstack check --fix` to auto-fix trivial issues"
    """


class NetworkError(GemstackError):
    """Network operation failed.

    Examples:
        - "Failed to connect to Gemini API"
        - suggestion: "Check your internet connection and API key"
    """


class SymlinkError(GemstackError):
    """Symlink operation failed.

    Examples:
        - "Cannot create symlink (insufficient permissions)"
        - suggestion: "On Windows, enable Developer Mode or use --copy-mode"
    """


class PluginError(GemstackError):
    """A plugin failed to load or execute.

    Examples:
        - "Plugin 'gemstack-topology-mobile' crashed during initialization"
        - suggestion: "Update or uninstall the plugin: pip install --upgrade ..."
    """

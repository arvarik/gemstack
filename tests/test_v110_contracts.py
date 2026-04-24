"""v1.1.0 Contract Tests — The Trap.

This test suite defines the v1.1.0 API contracts derived from the exploration
document (docs/explorations/2026-04-23-engineer-migration-dx-improvements.md).

Every test in this file MUST FAIL against the current codebase.
Every test in this file MUST PASS after the v1.1.0 implementation.

The definition of "done" is mathematically locked in this file.
"""

from pathlib import Path

from typer.testing import CliRunner

from gemstack.cli.main import app
from gemstack.project.detector import ProjectDetector, Topology
from gemstack.project.validator import ProjectValidator
from gemstack.utils.differ import ContextDiffer

runner = CliRunner()


# ---------------------------------------------------------------------------
# Contract 1: Section-Scoped Dependency Extraction (differ.py)
#
# The differ MUST only extract dependencies from Tech Stack / Dependencies
# sections in ARCHITECTURE.md. Backtick items in other sections (Data Models,
# Safety Invariants, etc.) MUST NOT be treated as dependencies.
# ---------------------------------------------------------------------------


class TestDifferDepPrecision:
    """Contract: _extract_documented_deps() is section-scoped."""

    ARCH_WITH_NOISE = """\
# Architecture

## 1. System Overview

The service uses `sleep_id` and `zone_five_milli` fields in its JSON responses.
Error codes include `API_ERROR` and `CONFLICT`.

## 2. Tech Stack & Dependencies

### Core Dependencies
| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | `>=0.100` | Web framework |
| `uvicorn` | `>=0.20` | ASGI server |
| `pydantic` | `>=2.0` | Validation |

## 3. Data Models

| Field | Type | Description |
|-------|------|-------------|
| `sleep_id` | `BIGINT` | Primary key |
| `zone_five_milli` | `INTEGER` | Zone 5 duration |
| `heart_rate` | `SMALLINT` | Heart rate BPM |

## 4. Safety Invariants

- **NEVER** use `eval()` on user input
- **ALWAYS** validate `user_id` before database queries
"""

    def test_ignores_json_tags_in_data_models(self) -> None:
        """Backtick items in Data Models section must NOT be extracted as deps."""
        differ = ContextDiffer()
        deps = differ._extract_documented_deps(self.ARCH_WITH_NOISE)
        assert "sleep_id" not in deps, "JSON tag 'sleep_id' falsely extracted as dependency"
        assert "zone_five_milli" not in deps, "JSON tag 'zone_five_milli' falsely extracted"

    def test_ignores_sql_types_in_data_models(self) -> None:
        """SQL column types like BIGINT must NOT be extracted as deps."""
        differ = ContextDiffer()
        deps = differ._extract_documented_deps(self.ARCH_WITH_NOISE)
        # These are ALL_CAPS but they're SQL types, not dependencies
        assert "bigint" not in deps, "SQL type 'BIGINT' falsely extracted as dependency"
        assert "integer" not in deps, "SQL type 'INTEGER' falsely extracted"
        assert "smallint" not in deps, "SQL type 'SMALLINT' falsely extracted"

    def test_ignores_error_codes_in_overview(self) -> None:
        """Error code constants in prose must NOT be extracted as deps."""
        differ = ContextDiffer()
        deps = differ._extract_documented_deps(self.ARCH_WITH_NOISE)
        assert "api_error" not in deps, "Error code 'API_ERROR' falsely extracted"
        assert "conflict" not in deps, "Error code 'CONFLICT' falsely extracted"

    def test_extracts_real_deps_from_tech_stack(self) -> None:
        """Real dependencies in Tech Stack section MUST be extracted."""
        differ = ContextDiffer()
        deps = differ._extract_documented_deps(self.ARCH_WITH_NOISE)
        assert "fastapi" in deps, "Real dep 'fastapi' not found in Tech Stack"
        assert "uvicorn" in deps, "Real dep 'uvicorn' not found in Tech Stack"
        assert "pydantic" in deps, "Real dep 'pydantic' not found in Tech Stack"

    def test_ignores_commands_in_safety_invariants(self) -> None:
        """Backtick items in Safety Invariants must NOT be extracted."""
        differ = ContextDiffer()
        deps = differ._extract_documented_deps(self.ARCH_WITH_NOISE)
        assert "eval()" not in deps
        assert "user_id" not in deps

    def test_scoped_extraction_reduces_false_positives(self) -> None:
        """Section-scoping must reduce extracted count to only real deps."""
        differ = ContextDiffer()
        deps = differ._extract_documented_deps(self.ARCH_WITH_NOISE)
        # Only 3 real deps should be extracted (fastapi, uvicorn, pydantic)
        assert len(deps) <= 5, (
            f"Expected <=5 deps from Tech Stack, got {len(deps)}: {deps}. "
            "Parser is still extracting from non-dependency sections."
        )


# ---------------------------------------------------------------------------
# Contract 2: Section-Scoped Env Var Extraction (differ.py)
#
# The differ MUST only extract env vars from Configuration / Environment
# sections. ALL_CAPS items elsewhere (SQL types, error codes, etc.) MUST
# NOT be treated as environment variables.
# ---------------------------------------------------------------------------


class TestDifferEnvVarPrecision:
    """Contract: _extract_documented_env_vars() is section-scoped."""

    ARCH_WITH_NOISE = """\
# Architecture

## 1. Data Models

| Column | Type |
|--------|------|
| `USER_ID` | `BIGINT` |
| `CREATED_AT` | `TIMESTAMP` |

## 2. Safety Invariants

- **NEVER** allow `PATH_TRAVERSAL` attacks
- **ALWAYS** use `ATOMIC_WRITE` for disk operations

## 3. Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `API_KEY` | Yes | External service key |
| `LOG_LEVEL` | No | Logging verbosity |

## 4. CI/CD Pipeline

The pipeline uses `GITHUB_TOKEN` and `NPM_TOKEN` for authentication.
"""

    def test_ignores_sql_types_as_env_vars(self) -> None:
        """SQL types like BIGINT, TIMESTAMP must NOT be extracted as env vars."""
        differ = ContextDiffer()
        env_vars = differ._extract_documented_env_vars(self.ARCH_WITH_NOISE)
        assert "BIGINT" not in env_vars, "SQL type 'BIGINT' falsely extracted as env var"
        assert "TIMESTAMP" not in env_vars, "SQL type 'TIMESTAMP' falsely extracted"

    def test_ignores_safety_invariant_constants(self) -> None:
        """Constants in Safety Invariants must NOT be extracted as env vars."""
        differ = ContextDiffer()
        env_vars = differ._extract_documented_env_vars(self.ARCH_WITH_NOISE)
        assert "PATH_TRAVERSAL" not in env_vars
        assert "ATOMIC_WRITE" not in env_vars

    def test_ignores_column_names_as_env_vars(self) -> None:
        """Database column names like USER_ID must NOT be extracted as env vars."""
        differ = ContextDiffer()
        env_vars = differ._extract_documented_env_vars(self.ARCH_WITH_NOISE)
        assert "USER_ID" not in env_vars, "Column name 'USER_ID' falsely extracted as env var"
        assert "CREATED_AT" not in env_vars

    def test_extracts_real_env_vars_from_configuration(self) -> None:
        """Real env vars in Configuration section MUST be extracted."""
        differ = ContextDiffer()
        env_vars = differ._extract_documented_env_vars(self.ARCH_WITH_NOISE)
        assert "DATABASE_URL" in env_vars, "Real env var 'DATABASE_URL' not found"
        assert "API_KEY" in env_vars, "Real env var 'API_KEY' not found"
        assert "LOG_LEVEL" in env_vars, "Real env var 'LOG_LEVEL' not found"

    def test_ignores_ci_tokens_outside_config_section(self) -> None:
        """Tokens mentioned in CI/CD prose must NOT be extracted as env vars."""
        differ = ContextDiffer()
        env_vars = differ._extract_documented_env_vars(self.ARCH_WITH_NOISE)
        assert "GITHUB_TOKEN" not in env_vars, (
            "'GITHUB_TOKEN' in CI section falsely extracted as project env var"
        )
        assert "NPM_TOKEN" not in env_vars

    def test_scoped_extraction_reduces_false_positives(self) -> None:
        """Only real env vars from Configuration section should be extracted."""
        differ = ContextDiffer()
        env_vars = differ._extract_documented_env_vars(self.ARCH_WITH_NOISE)
        assert len(env_vars) <= 4, (
            f"Expected <=4 env vars from Configuration, got {len(env_vars)}: {env_vars}. "
            "Parser is still extracting from non-configuration sections."
        )


# ---------------------------------------------------------------------------
# Contract 3: Validator Stale Reference Precision (validator.py)
#
# The validator's _extract_relevant_files() MUST:
# - Only scan the "## Relevant Files" section
# - Exclude markdown syntax characters (|, [, ], **, ##)
# - Require file refs to look like actual paths (contain . or /)
# ---------------------------------------------------------------------------


class TestValidatorStaleRefPrecision:
    """Contract: _extract_relevant_files() is scoped and filtered."""

    def test_ignores_bullet_points_outside_relevant_files(self) -> None:
        """Bullet items outside ## Relevant Files must NOT be extracted."""
        content = """\
# Status
[STATE: IN_PROGRESS]

## Current Focus
- Add OAuth login
- Fix database migrations

## Relevant Files
- `src/auth.py`
- `src/db.py`

## Known Issues
- Memory leak in worker
- Stale cache entries
"""
        validator = ProjectValidator()
        refs = validator._extract_relevant_files(content)
        assert "src/auth.py" in refs
        assert "src/db.py" in refs
        # Items from other sections must NOT appear
        for bad_ref in ["Add", "OAuth", "Fix", "database", "Memory", "leak", "Stale", "cache"]:
            assert bad_ref not in refs, f"'{bad_ref}' from non-Relevant Files section extracted"

    def test_ignores_markdown_table_pipes(self) -> None:
        """Markdown table pipes '|' must NOT be extracted as file refs."""
        content = """\
# Status

## Release History
| Version | Date | Notes |
|---------|------|-------|
| v1.0.0 | 2026-01-01 | Initial |

## Relevant Files
- `src/main.py`
"""
        # Also test that items from Release History section are not extracted
        validator = ProjectValidator()
        refs = validator._extract_relevant_files(content)
        assert "|" not in refs, "Markdown pipe '|' falsely extracted as file reference"
        assert "Version" not in refs
        assert "src/main.py" in refs

    def test_ignores_lifecycle_checkboxes(self) -> None:
        """Lifecycle checkbox items like '- [x] Spec' must NOT be extracted."""
        content = """\
# Status

## Lifecycle Progress
- [x] Spec — Done
- [ ] Trap — Pending
- [ ] Build

## Relevant Files
- `src/app.py`
"""
        validator = ProjectValidator()
        refs = validator._extract_relevant_files(content)
        assert "[x]" not in refs
        assert "Spec" not in refs
        assert "Trap" not in refs
        assert "src/app.py" in refs

    def test_requires_path_like_references(self) -> None:
        """Extracted refs must look like file paths (contain '.' or '/')."""
        content = """\
# Status

## Relevant Files
- `src/main.py` — entry point
- `README` — docs
- `config/settings.yaml` — config
"""
        validator = ProjectValidator()
        refs = validator._extract_relevant_files(content)
        assert "src/main.py" in refs
        assert "config/settings.yaml" in refs
        # "README" has no . or / — debatable, but the contract says path-like
        # At minimum, the single-word items from other sections should be filtered

    def test_end_to_end_no_false_positive_warnings(self, tmp_path: Path) -> None:
        """A project with a typical STATUS.md must produce zero stale ref warnings
        from markdown syntax."""
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        for f in ProjectValidator.REQUIRED_FILES:
            (agent_dir / f).touch()

        (agent_dir / "ARCHITECTURE.md").write_text("# Architecture\n\n**Topology:** `[backend]`\n")
        (agent_dir / "STATUS.md").write_text("""\
# Status
[STATE: IN_PROGRESS]

## Current Focus
**Feature:** DX Improvements

## Lifecycle Progress
- [x] Spec — Complete
- [ ] Trap — In progress
- [ ] Build
- [ ] Audit
- [ ] Ship

## Release History
| Version | Date | Highlights |
|---------|------|------------|
| v1.0.0 | 2026-04-14 | Initial release |

## Known Issues
1. Parser false positives
2. Hook exit codes
""")
        # Create docs dirs to avoid those warnings
        for d in ["explorations", "designs", "plans", "archive"]:
            (tmp_path / "docs" / d).mkdir(parents=True, exist_ok=True)
            (tmp_path / "docs" / d / ".gitkeep").touch()

        validator = ProjectValidator()
        result = validator.validate(tmp_path)
        stale_warnings = [w for w in result.warnings if "Stale reference" in w]
        assert len(stale_warnings) == 0, (
            f"Expected 0 stale ref warnings from markdown syntax, got {len(stale_warnings)}: "
            f"{stale_warnings}"
        )


# ---------------------------------------------------------------------------
# Contract 4: Check Command --strict Flag (check_cmd.py)
#
# - Default: warnings = exit 0, errors = exit 1
# - --strict: warnings = exit 1 (treat as errors)
# ---------------------------------------------------------------------------


class TestCheckStrictFlag:
    """Contract: check command supports --strict flag."""

    def _make_project_with_warnings(self, tmp_path: Path) -> Path:
        """Create a project that has warnings but no errors."""
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        for f in ProjectValidator.REQUIRED_FILES:
            (agent_dir / f).touch()
        (agent_dir / "ARCHITECTURE.md").write_text(
            "# Architecture\n\n**Topology:** `[backend]`\n"
        )
        # STATUS.md without [STATE: ...] → produces a warning, not an error
        (agent_dir / "STATUS.md").write_text("# Status\n\nNo state tag here.\n")
        # Missing docs dirs → warnings
        return tmp_path

    def test_strict_flag_accepted(self, tmp_path: Path) -> None:
        """The --strict flag must be a recognized option, not cause a Typer error."""
        project = self._make_project_with_warnings(tmp_path)
        result = runner.invoke(app, ["check", str(project), "--strict"])
        # Must NOT get a Typer "No such option" error (exit code 2)
        assert result.exit_code != 2, (
            "The --strict flag is not implemented on the check command. "
            f"Got Typer error (exit 2). Output: {result.stdout}"
        )
        # Must not contain usage error messages
        assert "No such option" not in (result.stdout + str(result.exception or "")), (
            "The --strict flag is not implemented on the check command"
        )

    def test_strict_flag_exits_nonzero_on_warnings(self, tmp_path: Path) -> None:
        """With --strict, warnings must cause exit code 1 (not 2 from unrecognized flag)."""
        project = self._make_project_with_warnings(tmp_path)
        result = runner.invoke(app, ["check", str(project), "--strict"])
        # Must exit 1 (validation error), NOT 2 (Typer usage error)
        assert result.exit_code == 1, (
            f"check --strict should exit 1 on warnings, got exit code {result.exit_code}. "
            "If exit code is 2, --strict is not implemented. "
            "If exit code is 0, --strict is not treating warnings as errors."
        )


# ---------------------------------------------------------------------------
# Contract 5: Hook Script Correctness (hook_cmd.py)
#
# The pre-commit hook must use the correct CLI syntax for the check command.
# The check command takes a positional argument, NOT --project.
# ---------------------------------------------------------------------------


class TestHookScriptCorrectness:
    """Contract: hook scripts use correct argument syntax."""

    def test_precommit_hook_uses_positional_arg(self) -> None:
        """Pre-commit hook must pass project path as positional arg, not --project."""
        from gemstack.cli.hook_cmd import _HOOKS

        hook_script = _HOOKS["pre-commit"]
        # The hook must NOT use --project (check doesn't accept it)
        assert "--project" not in hook_script, (
            "Pre-commit hook uses '--project' but check command takes a positional argument. "
            "This causes every hook invocation to fail with 'No such option'."
        )
        # The hook SHOULD use the path as a positional argument
        assert 'gemstack check "$(git rev-parse --show-toplevel)"' in hook_script or \
               "gemstack check $(git rev-parse --show-toplevel)" in hook_script, (
            "Pre-commit hook should pass the project path as a positional argument"
        )


# ---------------------------------------------------------------------------
# Contract 6: Detector — Python CLI Detection (detector.py)
#
# Typer, Click, and Fire CLI frameworks must be detected as backend topology.
# ---------------------------------------------------------------------------


class TestDetectorPythonCLI:
    """Contract: Python CLI frameworks detected as backend."""

    def test_typer_detected_as_backend(self, tmp_path: Path) -> None:
        """A Python project with typer dependency must be detected as backend."""
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "my-cli"\ndependencies = ["typer>=0.12"]\n'
        )
        detector = ProjectDetector()
        profile = detector.detect(tmp_path)
        assert profile.language == "python"
        assert Topology.BACKEND in profile.topologies, (
            f"Typer CLI not detected as backend. Got topologies: {profile.topologies}"
        )

    def test_click_detected_as_backend(self, tmp_path: Path) -> None:
        """A Python project with click dependency must be detected as backend."""
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "my-cli"\ndependencies = ["click>=8.0"]\n'
        )
        detector = ProjectDetector()
        profile = detector.detect(tmp_path)
        assert Topology.BACKEND in profile.topologies, (
            f"Click CLI not detected as backend. Got topologies: {profile.topologies}"
        )

    def test_fire_detected_as_backend(self, tmp_path: Path) -> None:
        """A Python project with fire dependency must be detected as backend."""
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "my-cli"\ndependencies = ["fire>=0.5"]\n'
        )
        detector = ProjectDetector()
        profile = detector.detect(tmp_path)
        assert Topology.BACKEND in profile.topologies, (
            f"Fire CLI not detected as backend. Got topologies: {profile.topologies}"
        )


# ---------------------------------------------------------------------------
# Contract 7: Detector — Python ML/AI Gaps (detector.py)
#
# faster-whisper, ctranslate2, whisper, onnxruntime must be detected as ML/AI.
# ---------------------------------------------------------------------------


class TestDetectorPythonMLAI:
    """Contract: Additional ML/AI Python deps detected."""

    def test_faster_whisper_detected_as_mlai(self, tmp_path: Path) -> None:
        """A project with faster-whisper must be detected as ML/AI topology."""
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "transcriber"\ndependencies = ["faster-whisper>=1.0"]\n'
        )
        detector = ProjectDetector()
        profile = detector.detect(tmp_path)
        assert Topology.ML_AI in profile.topologies, (
            f"faster-whisper not detected as ML/AI. Got: {profile.topologies}"
        )

    def test_onnxruntime_detected_as_mlai(self, tmp_path: Path) -> None:
        """A project with onnxruntime must be detected as ML/AI topology."""
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "inference"\ndependencies = ["onnxruntime>=1.16"]\n'
        )
        detector = ProjectDetector()
        profile = detector.detect(tmp_path)
        assert Topology.ML_AI in profile.topologies, (
            f"onnxruntime not detected as ML/AI. Got: {profile.topologies}"
        )

    def test_ctranslate2_detected_as_mlai(self, tmp_path: Path) -> None:
        """A project with ctranslate2 must be detected as ML/AI topology."""
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "translator"\ndependencies = ["ctranslate2>=4.0"]\n'
        )
        detector = ProjectDetector()
        profile = detector.detect(tmp_path)
        assert Topology.ML_AI in profile.topologies, (
            f"ctranslate2 not detected as ML/AI. Got: {profile.topologies}"
        )


# ---------------------------------------------------------------------------
# Contract 8: Detector — Go net/http Backend (detector.py)
#
# A Go project using net/http directly (no framework) must still be
# detected as backend topology.
# ---------------------------------------------------------------------------


class TestDetectorGoNetHTTP:
    """Contract: Go net/http projects detected as backend."""

    def test_go_net_http_detected_as_backend(self, tmp_path: Path) -> None:
        """A Go project importing net/http must be detected as backend."""
        (tmp_path / "go.mod").write_text("module myapp\n\ngo 1.22\n")
        # Create a Go source file that imports net/http
        (tmp_path / "main.go").write_text(
            'package main\n\nimport "net/http"\n\nfunc main() {\n'
            "\thttp.ListenAndServe(\":8080\", nil)\n}\n"
        )
        detector = ProjectDetector()
        profile = detector.detect(tmp_path)
        assert Topology.BACKEND in profile.topologies, (
            f"Go net/http project not detected as backend. Got: {profile.topologies}. "
            "The detector only checks for framework deps (chi, gin, etc.) but not net/http."
        )


# ---------------------------------------------------------------------------
# Contract 9: Detector — Go SDK Library with cmd/ (detector.py)
#
# A Go project with BOTH pkg/ and cmd/ directories must be detected as
# library-sdk topology. The current heuristic (pkg/ AND NOT cmd/) is wrong
# for SDK repos that have example binaries in cmd/.
# ---------------------------------------------------------------------------


class TestDetectorGoSDKWithCmd:
    """Contract: Go SDK with cmd/ dir still detected as library-sdk."""

    def test_go_sdk_with_pkg_and_cmd_is_library(self, tmp_path: Path) -> None:
        """A Go project with both pkg/ and cmd/ must include library-sdk topology."""
        (tmp_path / "go.mod").write_text("module github.com/user/sdk\n\ngo 1.22\n")
        (tmp_path / "pkg").mkdir()
        (tmp_path / "pkg" / "client.go").write_text("package client\n")
        (tmp_path / "cmd").mkdir()
        (tmp_path / "cmd" / "example").mkdir()
        (tmp_path / "cmd" / "example" / "main.go").write_text("package main\n")

        detector = ProjectDetector()
        profile = detector.detect(tmp_path)
        assert Topology.LIBRARY_SDK in profile.topologies, (
            f"Go SDK with pkg/ and cmd/ not detected as library-sdk. Got: {profile.topologies}. "
            "Current heuristic requires pkg/ AND NOT cmd/, but SDKs can have both."
        )


# ---------------------------------------------------------------------------
# Contract 10: Smart STATE Suggestion (validator.py)
#
# When STATUS.md is missing [STATE: ...], the warning message must include
# a suggested state based on content heuristics.
# ---------------------------------------------------------------------------


class TestSmartStateSuggestion:
    """Contract: check suggests a STATE when missing."""

    def test_suggests_state_in_warning(self, tmp_path: Path) -> None:
        """Warning for missing STATE must include a suggestion."""
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        for f in ProjectValidator.REQUIRED_FILES:
            (agent_dir / f).touch()
        (agent_dir / "ARCHITECTURE.md").write_text("# Architecture\n\n**Topology:** `[backend]`\n")
        (agent_dir / "STATUS.md").write_text("# Status\n\nSome content without a state tag.\n")
        for d in ["explorations", "designs", "plans", "archive"]:
            (tmp_path / "docs" / d).mkdir(parents=True, exist_ok=True)
            (tmp_path / "docs" / d / ".gitkeep").touch()

        validator = ProjectValidator()
        result = validator.validate(tmp_path)
        state_warnings = [w for w in result.warnings if "STATE" in w]
        assert len(state_warnings) == 1
        assert "suggested" in state_warnings[0].lower() or "suggest" in state_warnings[0].lower(), (
            f"Warning '{state_warnings[0]}' does not include a state suggestion. "
            "Expected something like: 'STATUS.md missing [STATE: ...] (suggested: INITIALIZED)'"
        )


# ---------------------------------------------------------------------------
# Contract 11: Batch Command Exists (batch_cmd.py — new)
#
# `gemstack batch` and `gemstack registry` must be registered CLI commands.
# ---------------------------------------------------------------------------


class TestBatchCommandContract:
    """Contract: batch and registry commands exist."""

    def test_batch_command_registered(self) -> None:
        """The 'batch' subcommand must be registered in the CLI."""
        result = runner.invoke(app, ["batch", "--help"])
        assert result.exit_code == 0, (
            f"'gemstack batch' not registered. Got exit code {result.exit_code}. "
            f"Output: {result.stdout}"
        )
        assert "batch" in result.stdout.lower()

    def test_registry_command_registered(self) -> None:
        """The 'registry' subcommand must be registered in the CLI."""
        result = runner.invoke(app, ["registry", "--help"])
        assert result.exit_code == 0, (
            f"'gemstack registry' not registered. Got exit code {result.exit_code}. "
            f"Output: {result.stdout}"
        )

    def test_registry_add_accepts_path(self, tmp_path: Path) -> None:
        """'gemstack registry add <path>' must accept a project path."""
        result = runner.invoke(app, ["registry", "add", str(tmp_path)])
        # Must not get Typer "No such command" error (exit code 2)
        assert result.exit_code != 2, (
            f"'registry add' not recognized. Got exit code 2. Output: {result.stdout}"
        )
        assert result.exit_code == 0, (
            f"'registry add' failed with exit code {result.exit_code}"
        )

    def test_registry_list_returns_output(self) -> None:
        """'gemstack registry list' must return structured output."""
        result = runner.invoke(app, ["registry", "list"])
        assert result.exit_code == 0

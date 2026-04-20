"""Tests for the ProjectDetector module."""

from pathlib import Path

from gemstack.project.detector import ProjectDetector, Topology


class TestNodeDetection:
    """Test Node.js project detection from package.json."""

    def test_detects_nextjs(self, nextjs_app: Path) -> None:
        detector = ProjectDetector()
        profile = detector.detect(nextjs_app)

        assert profile.language == "typescript"
        assert profile.framework == "next"
        assert profile.runtime == "node"
        assert Topology.FRONTEND in profile.topologies
        assert profile.manifest_file is not None
        assert profile.manifest_file.name == "package.json"

    def test_detects_npm_as_default_manager(self, nextjs_app: Path) -> None:
        detector = ProjectDetector()
        profile = detector.detect(nextjs_app)
        assert profile.package_manager == "npm"

    def test_detects_pnpm(self, nextjs_app: Path) -> None:
        (nextjs_app / "pnpm-lock.yaml").touch()
        detector = ProjectDetector()
        profile = detector.detect(nextjs_app)
        assert profile.package_manager == "pnpm"

    def test_infers_commands_from_scripts(self, nextjs_app: Path) -> None:
        import json

        pkg = json.loads((nextjs_app / "package.json").read_text())
        pkg["scripts"] = {"dev": "next dev", "build": "next build", "lint": "next lint"}
        (nextjs_app / "package.json").write_text(json.dumps(pkg))

        detector = ProjectDetector()
        profile = detector.detect(nextjs_app)
        assert profile.dev_command is not None
        assert "dev" in profile.dev_command


class TestPythonDetection:
    """Test Python project detection from pyproject.toml."""

    def test_detects_fastapi(self, python_fastapi: Path) -> None:
        detector = ProjectDetector()
        profile = detector.detect(python_fastapi)

        assert profile.language == "python"
        assert profile.runtime == "cpython"
        assert Topology.BACKEND in profile.topologies
        assert profile.manifest_file is not None

    def test_detects_fastapi_framework(self, python_fastapi: Path) -> None:
        detector = ProjectDetector()
        profile = detector.detect(python_fastapi)
        assert profile.framework == "fastapi"


class TestGoDetection:
    """Test Go project detection from go.mod."""

    def test_detects_go_chi(self, go_chi: Path) -> None:
        detector = ProjectDetector()
        profile = detector.detect(go_chi)

        assert profile.language == "go"
        assert profile.runtime == "go"
        assert Topology.BACKEND in profile.topologies
        assert profile.manifest_file is not None
        assert profile.manifest_file.name == "go.mod"

    def test_infers_go_test_command(self, go_chi: Path) -> None:
        detector = ProjectDetector()
        profile = detector.detect(go_chi)
        assert profile.test_command == "go test -race ./..."


class TestEmptyProject:
    """Test behavior on empty/minimal projects."""

    def test_empty_returns_unknown(self, empty_project: Path) -> None:
        detector = ProjectDetector()
        profile = detector.detect(empty_project)

        assert profile.language == "unknown"
        assert profile.topologies == []
        assert profile.manifest_file is None

    def test_name_is_directory_name(self, empty_project: Path) -> None:
        detector = ProjectDetector()
        profile = detector.detect(empty_project)
        assert profile.name == "empty-project"


class TestBootstrappedProject:
    """Test detection of already-bootstrapped projects."""

    def test_detects_existing_agent_dir(self, bootstrapped_project: Path) -> None:
        detector = ProjectDetector()
        profile = detector.detect(bootstrapped_project)
        assert profile.existing_agent_dir is True

    def test_empty_has_no_agent_dir(self, empty_project: Path) -> None:
        detector = ProjectDetector()
        profile = detector.detect(empty_project)
        assert profile.existing_agent_dir is False


class TestLegacyDetection:
    """Test detection of legacy context files."""

    def test_detects_cursorrules(self, empty_project: Path) -> None:
        (empty_project / ".cursorrules").write_text("rules")
        detector = ProjectDetector()
        profile = detector.detect(empty_project)
        assert len(profile.legacy_files) == 1
        assert profile.legacy_files[0].name == ".cursorrules"

    def test_detects_gemini_md(self, empty_project: Path) -> None:
        (empty_project / "GEMINI.md").write_text("context")
        detector = ProjectDetector()
        profile = detector.detect(empty_project)
        assert any(p.name == "GEMINI.md" for p in profile.legacy_files)

    def test_detects_claude_md(self, empty_project: Path) -> None:
        (empty_project / "CLAUDE.md").write_text("context")
        detector = ProjectDetector()
        profile = detector.detect(empty_project)
        assert any(p.name == "CLAUDE.md" for p in profile.legacy_files)


class TestRobustness:
    """Test that the detector handles malformed inputs gracefully."""

    def test_malformed_package_json(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text("{invalid json")
        detector = ProjectDetector()
        profile = detector.detect(tmp_path)
        # Should not crash — still detects as Node.js-ish
        assert profile.language == "typescript" or profile.manifest_file is not None

    def test_empty_package_json(self, tmp_path: Path) -> None:
        (tmp_path / "package.json").write_text("{}")
        detector = ProjectDetector()
        profile = detector.detect(tmp_path)
        assert profile.language in ("javascript", "typescript")

    def test_malformed_pyproject_toml(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("this is not toml ][")
        detector = ProjectDetector()
        profile = detector.detect(tmp_path)
        assert profile.language == "python"


class TestMiscDetection:
    """Test misc detection features."""

    def test_detects_env_example(self, python_fastapi: Path) -> None:
        detector = ProjectDetector()
        profile = detector.detect(python_fastapi)
        assert profile.env_file is not None

    def test_detects_tests_dir(self, python_fastapi: Path) -> None:
        detector = ProjectDetector()
        profile = detector.detect(python_fastapi)
        assert profile.has_tests is True

    def test_detects_source_dirs(self, python_fastapi: Path) -> None:
        detector = ProjectDetector()
        profile = detector.detect(python_fastapi)
        assert any(d.name == "src" for d in profile.source_dirs)

"""Tests for the CI config generation command."""

from pathlib import Path

from gemstack.cli.ci_cmd import _GITHUB_ACTIONS_TEMPLATE, _GITLAB_CI_TEMPLATE


class TestGitHubActionsTemplate:
    """Tests for the GitHub Actions CI template."""

    def test_template_valid_yaml_structure(self) -> None:
        assert "name: Gemstack Check" in _GITHUB_ACTIONS_TEMPLATE
        assert "on:" in _GITHUB_ACTIONS_TEMPLATE
        assert "pull_request:" in _GITHUB_ACTIONS_TEMPLATE

    def test_template_runs_gemstack_check(self) -> None:
        assert "gemstack check" in _GITHUB_ACTIONS_TEMPLATE

    def test_template_checks_for_stubs(self) -> None:
        assert "TODO: remove stub" in _GITHUB_ACTIONS_TEMPLATE

    def test_template_checks_audit_findings(self) -> None:
        assert "AUDIT_FINDINGS.md" in _GITHUB_ACTIONS_TEMPLATE

    def test_writes_file(self, tmp_path: Path) -> None:
        output = tmp_path / ".github" / "workflows" / "gemstack.yml"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(_GITHUB_ACTIONS_TEMPLATE)

        assert output.exists()
        assert "gemstack check" in output.read_text()


class TestGitLabCITemplate:
    """Tests for the GitLab CI template."""

    def test_template_has_stage(self) -> None:
        assert "stage: test" in _GITLAB_CI_TEMPLATE

    def test_template_runs_gemstack_check(self) -> None:
        assert "gemstack check" in _GITLAB_CI_TEMPLATE

    def test_template_merge_requests_only(self) -> None:
        assert "merge_requests" in _GITLAB_CI_TEMPLATE

"""Tests for the PhaseRouter module."""

from pathlib import Path

from gemstack.core.router import PhaseRouter, RoutingAction


class TestRouterRules:
    """Test all 8 routing rules from the spec."""

    def test_missing_status_returns_blocked(self, tmp_path: Path) -> None:
        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.BLOCKED
        assert "gemstack init" in decision.next_command
        assert "Missing .agent/ directory" in decision.blockers

    def test_audit_findings_reroute_to_build(self, bootstrapped_project: Path) -> None:
        # Create AUDIT_FINDINGS.md with content
        audit_path = bootstrapped_project / ".agent" / "AUDIT_FINDINGS.md"
        audit_path.write_text("## Findings\n- SQL injection in login route\n")

        router = PhaseRouter()
        decision = router.route(bootstrapped_project)

        assert decision.action == RoutingAction.REROUTE_TO_BUILD
        assert decision.next_command == "/step3-build"
        assert "Audit findings" in decision.reason

    def test_initialized_state_continues_to_spec(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text(
            "# Status\n\n[STATE: INITIALIZED]\n\n"
            "## Feature Lifecycle\n- [ ] Spec\n- [ ] Build\n"
        )

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.CONTINUE
        assert decision.next_command == "/step1-spec"

    def test_ready_for_build_continues(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text("[STATE: READY_FOR_BUILD]\n")

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.CONTINUE
        assert decision.next_command == "/step3-build"

    def test_ready_for_audit_continues(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text("[STATE: READY_FOR_AUDIT]\n")

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.CONTINUE
        assert decision.next_command == "/step4-audit"

    def test_ready_for_ship_no_findings(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text("[STATE: READY_FOR_SHIP]\n")

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.READY_TO_SHIP
        assert decision.next_command == "/step5-ship"

    def test_shipped_state_blocked(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text("[STATE: SHIPPED]\n")

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.BLOCKED
        assert "gemstack start" in decision.next_command

    def test_unknown_state_blocked(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text("[STATE: SOMETHING_WEIRD]\n")

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.BLOCKED


class TestInProgressRouting:
    """Test IN_PROGRESS state with lifecycle inference."""

    def test_in_progress_spec_incomplete(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text(
            "[STATE: IN_PROGRESS]\n\n## Feature Lifecycle\n"
            "- [ ] Spec\n- [ ] Trap\n- [ ] Build\n- [ ] Audit\n- [ ] Ship\n"
        )

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.CONTINUE
        assert decision.next_command == "/step1-spec"

    def test_in_progress_spec_done_trap_next(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text(
            "[STATE: IN_PROGRESS]\n\n## Feature Lifecycle\n"
            "- [x] Spec\n- [ ] Trap\n- [ ] Build\n"
        )

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.CONTINUE
        assert decision.next_command == "/step2-trap"

    def test_in_progress_build_next(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text(
            "[STATE: IN_PROGRESS]\n\n## Feature Lifecycle\n"
            "- [x] Spec\n- [x] Trap\n- [ ] Build\n- [ ] Audit\n- [ ] Ship\n"
        )

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.CONTINUE
        assert decision.next_command == "/step3-build"


class TestStateParsing:
    """Test internal state parsing helpers."""

    def test_parse_state_extracts_enum(self, tmp_path: Path) -> None:
        path = tmp_path / "STATUS.md"
        path.write_text("[STATE: READY_FOR_BUILD]")

        router = PhaseRouter()
        assert router._parse_state(path) == "READY_FOR_BUILD"

    def test_parse_state_handles_whitespace(self, tmp_path: Path) -> None:
        path = tmp_path / "STATUS.md"
        path.write_text("[STATE:  IN_PROGRESS]")

        router = PhaseRouter()
        state = router._parse_state(path)
        assert state == "IN_PROGRESS"

    def test_parse_state_missing_returns_unknown(self, tmp_path: Path) -> None:
        path = tmp_path / "STATUS.md"
        path.write_text("No state here")

        router = PhaseRouter()
        assert router._parse_state(path) == "UNKNOWN"

    def test_parse_lifecycle(self, tmp_path: Path) -> None:
        path = tmp_path / "STATUS.md"
        path.write_text(
            "- [x] Spec\n- [x] Trap\n- [ ] Build\n- [ ] Audit\n- [ ] Ship\n"
        )

        router = PhaseRouter()
        lifecycle = router._parse_lifecycle(path)

        assert lifecycle["Spec"] is True
        assert lifecycle["Trap"] is True
        assert lifecycle["Build"] is False
        assert lifecycle["Ship"] is False


class TestEmptyAuditFindings:
    """Test that empty AUDIT_FINDINGS.md behaves correctly."""

    def test_empty_file_not_treated_as_findings(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text("[STATE: READY_FOR_SHIP]\n")
        (agent_dir / "AUDIT_FINDINGS.md").write_text("")  # Empty

        router = PhaseRouter()
        decision = router.route(tmp_path)

        # Empty file should NOT trigger reroute
        assert decision.action == RoutingAction.READY_TO_SHIP

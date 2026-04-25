"""Tests for the PhaseRouter module."""

from pathlib import Path

from gemstack.orchestration.router import PhaseRouter, RoutingAction


class TestRouterRules:
    """Test routing rules."""

    def test_missing_status_returns_blocked(self, tmp_path: Path) -> None:
        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.BLOCKED
        assert "gemstack init" in decision.next_command
        assert "Missing .agent/ directory" in decision.blockers

    def test_audit_findings_reroute_to_build(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text(
            "- [x] Step 1: Spec\n"
            "- [x] Step 2: Trap\n"
            "- [x] Step 3: Build\n"
            "- [ ] Step 4: Audit\n"
        )
        
        audit_path = agent_dir / "AUDIT_FINDINGS.md"
        audit_path.write_text("## Findings\n- SQL injection in login route\n")

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.REROUTE_TO_BUILD
        assert decision.next_command == "/step3-build"
        assert "Audit findings" in decision.reason

    def test_initialized_state_continues_to_spec(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text(
            
            "## 5. Lifecycle Tracker\n"
            "- [ ] Step 1: Spec\n"
            "- [ ] Step 2: Trap\n"
            "- [ ] Step 3: Build\n"
            "- [ ] Step 4: Audit\n"
            "- [ ] Step 5: Ship\n"
        
        )

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.CONTINUE
        assert decision.next_command == "/step1-spec"

    def test_ready_for_build_continues(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text(
            
            "- [x] Step 1: Spec\n"
            "- [x] Step 2: Trap\n"
            "- [ ] Step 3: Build\n"
        
        )

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.CONTINUE
        assert decision.next_command == "/step3-build"

    def test_ready_for_audit_continues(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text(
            
            "- [x] Step 1: Spec\n"
            "- [x] Step 2: Trap\n"
            "- [x] Step 3: Build\n"
            "- [ ] Step 4: Audit\n"
        
        )

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.CONTINUE
        assert decision.next_command == "/step4-audit"

    def test_ready_for_ship_no_findings(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text(
            
            "- [x] Step 1: Spec\n"
            "- [x] Step 2: Trap\n"
            "- [x] Step 3: Build\n"
            "- [x] Step 4: Audit\n"
            "- [ ] Step 5: Ship\n"
        
        )

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.READY_TO_SHIP
        assert decision.next_command == "/step5-ship"

    def test_shipped_state_blocked(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text(
            
            "- [x] Step 1: Spec\n"
            "- [x] Step 2: Trap\n"
            "- [x] Step 3: Build\n"
            "- [x] Step 4: Audit\n"
            "- [x] Step 5: Ship\n"
        
        )

        router = PhaseRouter()
        decision = router.route(tmp_path)

        assert decision.action == RoutingAction.BLOCKED
        assert "gemstack start" in decision.next_command


class TestAuditStateParsing:
    """Test parsing of AUDIT_FINDINGS.md"""

    def test_empty_audit_file(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text(
            "- [x] Step 1: Spec\n"
            "- [x] Step 2: Trap\n"
            "- [x] Step 3: Build\n"
            "- [ ] Step 4: Audit\n"
        )
        (agent_dir / "AUDIT_FINDINGS.md").write_text("")
        
        router = PhaseRouter()
        decision = router.route(tmp_path)
        
        # Should continue to audit
        assert decision.action == RoutingAction.CONTINUE
        assert decision.next_command == "/step4-audit"

    def test_resolved_audit_file(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        (agent_dir / "STATUS.md").write_text(
            "- [x] Step 1: Spec\n"
            "- [x] Step 2: Trap\n"
            "- [x] Step 3: Build\n"
            "- [ ] Step 4: Audit\n"
        )
        (agent_dir / "AUDIT_FINDINGS.md").write_text("ALL ISSUES RESOLVED")
        
        router = PhaseRouter()
        decision = router.route(tmp_path)
        
        # Should continue to audit for re-verification
        assert decision.action == RoutingAction.CONTINUE
        assert decision.next_command == "/step4-audit"
        
    def test_pass_audit_file(self, tmp_path: Path) -> None:
        agent_dir = tmp_path / ".agent"
        agent_dir.mkdir()
        # Even if Audit checkbox isn't checked, if file says PASS it skips to ship
        (agent_dir / "STATUS.md").write_text(
            "- [x] Step 1: Spec\n"
            "- [x] Step 2: Trap\n"
            "- [x] Step 3: Build\n"
            "- [ ] Step 4: Audit\n"
            "- [ ] Step 5: Ship\n"
        )
        (agent_dir / "AUDIT_FINDINGS.md").write_text("PASS")
        
        router = PhaseRouter()
        decision = router.route(tmp_path)
        
        assert decision.action == RoutingAction.READY_TO_SHIP
        assert decision.next_command == "/step5-ship"


class TestLifecycleParsing:
    """Test parsing of STATUS.md checkboxes."""

    def test_parse_lifecycle_old_format(self, tmp_path: Path) -> None:
        path = tmp_path / "STATUS.md"
        path.write_text("- [x] Spec\n- [x] Trap\n- [ ] Build\n- [ ] Audit\n- [ ] Ship\n")

        router = PhaseRouter()
        lifecycle = router._parse_lifecycle(path)

        assert lifecycle["Spec"] is True
        assert lifecycle["Trap"] is True
        assert lifecycle["Build"] is False
        assert lifecycle["Ship"] is False

    def test_parse_lifecycle_new_format(self, tmp_path: Path) -> None:
        path = tmp_path / "STATUS.md"
        path.write_text(
            "- [x] Step 1: Spec\n"
            "- [x] Step 2: Trap\n"
            "- [ ] Step 3: Build\n"
            "- [ ] Step 4: Audit\n"
            "- [ ] Step 5: Ship\n"
        )

        router = PhaseRouter()
        lifecycle = router._parse_lifecycle(path)

        assert lifecycle["Spec"] is True
        assert lifecycle["Trap"] is True
        assert lifecycle["Build"] is False
        assert lifecycle["Ship"] is False

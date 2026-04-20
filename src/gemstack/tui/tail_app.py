"""Gemstack Tail — Live session monitor TUI.

A Textual application that watches .agent/STATUS.md for changes and
displays a real-time dashboard of the project's workflow state.

Requires the `gemstack[tail]` optional dependency (textual + watchdog).
"""

from __future__ import annotations

import re
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Footer, Header, Static
from watchdog.events import FileModifiedEvent, FileSystemEventHandler
from watchdog.observers import Observer


class StatusFileChanged(Message):
    """Message posted when STATUS.md changes on disk."""


class _StatusWatcher(FileSystemEventHandler):
    """Watchdog handler that posts a Textual message on file change."""

    def __init__(self, app: GemstackTailApp, watch_file: str) -> None:
        self._app = app
        self._watch_file = watch_file

    def on_modified(self, event: FileModifiedEvent) -> None:  # type: ignore[override]
        if event.src_path and str(event.src_path).endswith(self._watch_file):
            self._app.post_message(StatusFileChanged())


class PhaseProgress(Static):
    """Displays the 5-step workflow as a visual pipeline."""

    DEFAULT_CSS = """
    PhaseProgress {
        height: 3;
        padding: 0 1;
    }
    """

    def render_phase_bar(self, lifecycle: dict[str, bool], state: str) -> str:
        """Render a visual pipeline of the 5 phases."""
        steps = ["Spec", "Trap", "Build", "Audit", "Ship"]
        parts: list[str] = []

        for step_name in steps:
            completed = lifecycle.get(step_name, False)
            if completed:
                parts.append(f"[green]✅ {step_name}[/green]")
            elif state == "IN_PROGRESS":
                # Mark the first uncompleted as active
                if not any(lifecycle.get(s, False) for s in steps[steps.index(step_name):]):
                    parts.append(f"[yellow]▶ {step_name}[/yellow]")
                else:
                    parts.append(f"[dim]○ {step_name}[/dim]")
            else:
                parts.append(f"[dim]○ {step_name}[/dim]")

        return " → ".join(parts)


class StatusPanel(Static):
    """Displays the current STATUS.md content with syntax highlighting."""

    DEFAULT_CSS = """
    StatusPanel {
        height: 100%;
        border: round $primary;
        padding: 1;
        overflow-y: scroll;
    }
    """


class RouterPanel(Static):
    """Displays the current routing decision."""

    DEFAULT_CSS = """
    RouterPanel {
        height: auto;
        max-height: 8;
        border: round $accent;
        padding: 1;
    }
    """


class GemstackTailApp(App[None]):
    """Live session monitor TUI for Gemstack projects.

    Watches .agent/STATUS.md for filesystem changes and updates
    the dashboard in real-time.
    """

    TITLE = "Gemstack Tail — Live Session Monitor"

    CSS = """
    Screen {
        layout: vertical;
    }

    #progress-bar {
        dock: top;
        height: 3;
        padding: 0 1;
        background: $surface;
    }

    #main-layout {
        height: 1fr;
    }

    #status-panel {
        width: 2fr;
    }

    #side-panel {
        width: 1fr;
    }
    """

    status_content: reactive[str] = reactive("")

    def __init__(self, project_root: Path) -> None:
        super().__init__()
        self.project_root = project_root
        self._observer: Observer | None = None  # type: ignore[valid-type]

    def compose(self) -> ComposeResult:
        yield Header()
        yield PhaseProgress(id="progress-bar")
        with Horizontal(id="main-layout"):
            with Vertical(id="status-panel"):
                yield StatusPanel("Loading STATUS.md...", id="status-content")
            with Vertical(id="side-panel"):
                yield RouterPanel("Computing route...", id="router-content")
        yield Footer()

    def on_mount(self) -> None:
        """Start watching STATUS.md when the app mounts."""
        self._refresh_dashboard()

        # Start filesystem watcher
        agent_dir = self.project_root / ".agent"
        if agent_dir.exists():
            self._observer = Observer()
            handler = _StatusWatcher(self, "STATUS.md")
            self._observer.schedule(handler, str(agent_dir), recursive=False)
            self._observer.start()

    def on_unmount(self) -> None:
        """Stop the filesystem watcher when the app unmounts."""
        if self._observer:
            self._observer.stop()  # type: ignore[attr-defined]
            self._observer.join(timeout=2)  # type: ignore[attr-defined]

    def on_status_file_changed(self, _message: StatusFileChanged) -> None:
        """Handle STATUS.md file change notification."""
        self.call_from_thread(self._refresh_dashboard)

    def _refresh_dashboard(self) -> None:
        """Reload STATUS.md and update all panels."""
        status_path = self.project_root / ".agent" / "STATUS.md"
        if not status_path.exists():
            self.query_one("#status-content", StatusPanel).update(
                "[red]No .agent/STATUS.md found[/red]"
            )
            return

        content = status_path.read_text()

        # Update status panel
        self.query_one("#status-content", StatusPanel).update(content)

        # Update phase progress
        state = self._parse_state(content)
        lifecycle = self._parse_lifecycle(content)
        progress = self.query_one("#progress-bar", PhaseProgress)
        progress.update(progress.render_phase_bar(lifecycle, state))

        # Update router panel
        self._refresh_router()

    def _refresh_router(self) -> None:
        """Refresh the routing decision panel."""
        try:
            from gemstack.core.router import PhaseRouter

            router = PhaseRouter()
            decision = router.route(self.project_root)

            emoji = {
                "continue": "🟢",
                "reroute_to_build": "🟠",
                "ready_to_ship": "🚀",
                "blocked": "🛑",
            }.get(decision.action.value, "❓")

            self.query_one("#router-content", RouterPanel).update(
                f"{emoji} [bold]{decision.action.value.upper()}[/bold]\n"
                f"{decision.reason}\n"
                f"Next: [cyan]{decision.next_command}[/cyan]"
            )
        except Exception as e:
            self.query_one("#router-content", RouterPanel).update(
                f"[red]Router error: {e}[/red]"
            )

    @staticmethod
    def _parse_state(content: str) -> str:
        """Extract [STATE: ...] from STATUS.md content."""
        match = re.search(r"\[STATE:\s*(\w+)\]", content)
        return match.group(1) if match else "UNKNOWN"

    @staticmethod
    def _parse_lifecycle(content: str) -> dict[str, bool]:
        """Extract lifecycle checkboxes from STATUS.md content."""
        lifecycle: dict[str, bool] = {}
        for match in re.finditer(r"-\s*\[([ xX])\]\s*(\w+)", content):
            lifecycle[match.group(2)] = match.group(1).lower() == "x"
        return lifecycle

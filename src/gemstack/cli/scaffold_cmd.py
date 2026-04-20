"""gemstack scaffold — Smart boilerplate generation.

Generates context-aware scaffolding that respects the project's
topology and style guide.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from gemstack.core.fileutil import write_atomic

console = Console()

scaffold_app = typer.Typer(name="scaffold", help="Smart boilerplate generation")


@scaffold_app.command()
def route(
    path: str = typer.Argument(..., help="Route path (e.g., /api/v1/notifications)"),
    project_root: Path = typer.Option(
        ".", "--project", "-p", help="Project root directory"
    ),
) -> None:
    """Scaffold a backend route and its test file."""
    project_root = project_root.resolve()
    lang = _detect_language(project_root)

    if lang == "python":
        _scaffold_python_route(project_root, path)
    elif lang in ("typescript", "javascript"):
        _scaffold_ts_route(project_root, path)
    elif lang == "go":
        _scaffold_go_route(project_root, path)
    else:
        console.print(
            f"[yellow]⚠️  Language '{lang}' not yet supported "
            f"for route scaffolding.[/yellow]"
        )


@scaffold_app.command()
def component(
    name: str = typer.Argument(..., help="Component name (e.g., NotificationBell)"),
    project_root: Path = typer.Option(
        ".", "--project", "-p", help="Project root directory"
    ),
) -> None:
    """Scaffold a frontend component with all 5 states."""
    project_root = project_root.resolve()
    lang = _detect_language(project_root)

    if lang in ("typescript", "javascript"):
        _scaffold_react_component(project_root, name)
    else:
        console.print(
            f"[yellow]⚠️  Language '{lang}' not yet supported "
            f"for component scaffolding.[/yellow]"
        )


@scaffold_app.command("test")
def scaffold_test(
    name: str = typer.Argument(..., help="Test suite name"),
    project_root: Path = typer.Option(
        ".", "--project", "-p", help="Project root directory"
    ),
) -> None:
    """Scaffold a test file matching project conventions."""
    project_root = project_root.resolve()
    lang = _detect_language(project_root)

    if lang == "python":
        _scaffold_python_test(project_root, name)
    elif lang in ("typescript", "javascript"):
        _scaffold_ts_test(project_root, name)
    else:
        console.print(
            f"[yellow]⚠️  Language '{lang}' not yet supported "
            f"for test scaffolding.[/yellow]"
        )


# ── Scaffolding implementations ────────────────────────────────────


def _scaffold_python_route(root: Path, route_path: str) -> None:
    name = route_path.strip("/").replace("/", "_").replace("-", "_")
    src_dir = root / "src" / "routes"
    src_dir.mkdir(parents=True, exist_ok=True)

    route_file = src_dir / f"{name}.py"
    write_atomic(
        route_file,
        f'"""Route handler for {route_path}."""\n\n'
        f"# TODO: Implement {route_path} endpoint\n\n\n"
        f"async def handle_{name}():\n"
        f'    """Handle {route_path} requests."""\n'
        f'    return {{"status": "ok"}}\n',
    )
    console.print(f"  [green]✔[/green] Created {route_file.relative_to(root)}")

    test_dir = root / "tests"
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / f"test_{name}.py"
    write_atomic(
        test_file,
        f'"""Tests for {route_path} route."""\n\n\n'
        f"class TestRoute{name.title().replace('_', '')}:\n"
        f'    def test_returns_ok(self) -> None:\n'
        f'        """Verify route returns 200."""\n'
        f"        assert True  # TODO: implement\n",
    )
    console.print(f"  [green]✔[/green] Created {test_file.relative_to(root)}")
    console.print("[green]✅ Route scaffolded![/green]")


def _scaffold_ts_route(root: Path, route_path: str) -> None:
    name = route_path.strip("/").replace("/", "-")
    src_dir = root / "src" / "routes"
    src_dir.mkdir(parents=True, exist_ok=True)

    route_file = src_dir / f"{name}.ts"
    write_atomic(
        route_file,
        f"// Route handler for {route_path}\n\n"
        f"export async function handle(req: Request): Promise<Response> {{\n"
        f'  // TODO: Implement {route_path}\n'
        f'  return new Response(JSON.stringify({{ status: "ok" }}));\n'
        f"}}\n",
    )
    console.print(f"  [green]✔[/green] Created {route_file.relative_to(root)}")
    console.print("[green]✅ Route scaffolded![/green]")


def _scaffold_go_route(root: Path, route_path: str) -> None:
    name = route_path.strip("/").replace("/", "_").replace("-", "_")
    handler_dir = root / "handlers"
    handler_dir.mkdir(parents=True, exist_ok=True)

    handler_file = handler_dir / f"{name}.go"
    write_atomic(
        handler_file,
        f"package handlers\n\n"
        f"import (\n\t\"net/http\"\n)\n\n"
        f"// Handle{name.title().replace('_', '')} handles {route_path}\n"
        f"func Handle{name.title().replace('_', '')}(w http.ResponseWriter, r *http.Request) {{\n"
        f'\t// TODO: Implement {route_path}\n'
        f'\tw.WriteHeader(http.StatusOK)\n'
        f"}}\n",
    )
    console.print(f"  [green]✔[/green] Created {handler_file.relative_to(root)}")
    console.print("[green]✅ Route scaffolded![/green]")


def _scaffold_react_component(root: Path, name: str) -> None:
    comp_dir = root / "src" / "components"
    comp_dir.mkdir(parents=True, exist_ok=True)

    comp_file = comp_dir / f"{name}.tsx"
    write_atomic(
        comp_file,
        f'import React from "react";\n\n'
        f"interface {name}Props {{\n"
        f"  // TODO: Define props\n"
        f"}}\n\n"
        f"export function {name}({{ }}: {name}Props) {{\n"
        f"  // States: Loading, Empty, Error, Populated, Offline\n"
        f"  const [loading, setLoading] = React.useState(true);\n"
        f"  const [error, setError] = React.useState<Error | null>(null);\n\n"
        f"  if (loading) return <div>Loading...</div>;\n"
        f"  if (error) return <div>Error: {{error.message}}</div>;\n\n"
        f"  return (\n"
        f"    <div>\n"
        f"      {{/* TODO: Implement {name} */}}\n"
        f"    </div>\n"
        f"  );\n"
        f"}}\n",
    )
    console.print(f"  [green]✔[/green] Created {comp_file.relative_to(root)}")
    console.print("[green]✅ Component scaffolded with 5-state skeleton![/green]")


def _scaffold_python_test(root: Path, name: str) -> None:
    test_dir = root / "tests"
    test_dir.mkdir(parents=True, exist_ok=True)

    test_file = test_dir / f"test_{name}.py"
    write_atomic(
        test_file,
        f'"""Tests for {name}."""\n\n'
        f"import pytest\n\n\n"
        f"class Test{name.title().replace('_', '')}:\n"
        f'    """Test suite for {name}."""\n\n'
        f"    def test_placeholder(self) -> None:\n"
        f'        """TODO: Implement tests."""\n'
        f"        assert True\n",
    )
    console.print(f"  [green]✔[/green] Created {test_file.relative_to(root)}")
    console.print("[green]✅ Test suite scaffolded![/green]")


def _scaffold_ts_test(root: Path, name: str) -> None:
    test_dir = root / "tests"
    test_dir.mkdir(parents=True, exist_ok=True)

    test_file = test_dir / f"{name}.test.ts"
    write_atomic(
        test_file,
        f'import {{ describe, it, expect }} from "vitest";\n\n'
        f'describe("{name}", () => {{\n'
        f'  it("should work", () => {{\n'
        f"    // TODO: implement\n"
        f"    expect(true).toBe(true);\n"
        f"  }});\n"
        f"}});\n",
    )
    console.print(f"  [green]✔[/green] Created {test_file.relative_to(root)}")
    console.print("[green]✅ Test suite scaffolded![/green]")


# ── Helpers ────────────────────────────────────────────────────────


def _detect_language(root: Path) -> str:
    """Quick language detection based on manifest files."""
    if (root / "pyproject.toml").exists() or (root / "setup.py").exists():
        return "python"
    if (root / "package.json").exists():
        has_ts = (root / "tsconfig.json").exists()
        if not has_ts and (root / "src").exists():
            has_ts = any((root / "src").rglob("*.tsx"))
        if has_ts:
            return "typescript"
        return "javascript"
    if (root / "go.mod").exists():
        return "go"
    return "unknown"

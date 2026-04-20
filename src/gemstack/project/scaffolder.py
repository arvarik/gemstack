"""Scaffolding logic for generating project boilerplate."""

from pathlib import Path

from gemstack.errors import ProjectError
from gemstack.utils.fileutil import write_atomic


class Scaffolder:
    """Generates context-aware scaffolding based on project topology."""

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()

    def _detect_language(self) -> str:
        """Quick language detection based on manifest files."""
        if (self.project_root / "pyproject.toml").exists() or (
            self.project_root / "setup.py"
        ).exists():
            return "python"
        if (self.project_root / "package.json").exists():
            has_ts = (self.project_root / "tsconfig.json").exists()
            if not has_ts and (self.project_root / "src").exists():
                has_ts = any((self.project_root / "src").rglob("*.tsx"))
            if has_ts:
                return "typescript"
            return "javascript"
        if (self.project_root / "go.mod").exists():
            return "go"
        return "unknown"

    def scaffold_route(self, route_path: str) -> Path:
        """Scaffold a route and its test file."""
        lang = self._detect_language()

        if lang == "python":
            return self._scaffold_python_route(route_path)
        elif lang in ("typescript", "javascript"):
            return self._scaffold_ts_route(route_path)
        elif lang == "go":
            return self._scaffold_go_route(route_path)
        else:
            raise ProjectError(
                f"Language '{lang}' not yet supported for route scaffolding.",
                suggestion="Currently supported: python, typescript/javascript, go.",
            )

    def scaffold_component(self, name: str) -> Path:
        """Scaffold a frontend component with all 5 states."""
        lang = self._detect_language()

        if lang in ("typescript", "javascript"):
            return self._scaffold_react_component(name)
        else:
            raise ProjectError(
                f"Language '{lang}' not yet supported for component scaffolding.",
                suggestion="React/TS component scaffolding is currently supported.",
            )

    def scaffold_test(self, name: str) -> Path:
        """Scaffold a test file matching project conventions."""
        lang = self._detect_language()

        if lang == "python":
            return self._scaffold_python_test(name)
        elif lang in ("typescript", "javascript"):
            return self._scaffold_ts_test(name)
        else:
            raise ProjectError(
                f"Language '{lang}' not yet supported for test scaffolding.",
                suggestion="Currently supported: python, typescript/javascript.",
            )

    # ── Scaffolding implementations ────────────────────────────────────

    def _scaffold_python_route(self, route_path: str) -> Path:
        name = route_path.strip("/").replace("/", "_").replace("-", "_")
        src_dir = self.project_root / "src" / "routes"
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

        test_dir = self.project_root / "tests"
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file = test_dir / f"test_{name}.py"
        write_atomic(
            test_file,
            f'"""Tests for {route_path} route."""\n\n\n'
            f"class TestRoute{name.title().replace('_', '')}:\n"
            f"    def test_returns_ok(self) -> None:\n"
            f'        """Verify route returns 200."""\n'
            f"        assert True  # TODO: implement\n",
        )
        return route_file

    def _scaffold_ts_route(self, route_path: str) -> Path:
        name = route_path.strip("/").replace("/", "-")
        src_dir = self.project_root / "src" / "routes"
        src_dir.mkdir(parents=True, exist_ok=True)

        route_file = src_dir / f"{name}.ts"
        write_atomic(
            route_file,
            f"// Route handler for {route_path}\n\n"
            f"export async function handle(req: Request): Promise<Response> {{\n"
            f"  // TODO: Implement {route_path}\n"
            f'  return new Response(JSON.stringify({{ status: "ok" }}));\n'
            f"}}\n",
        )
        return route_file

    def _scaffold_go_route(self, route_path: str) -> Path:
        name = route_path.strip("/").replace("/", "_").replace("-", "_")
        handler_dir = self.project_root / "handlers"
        handler_dir.mkdir(parents=True, exist_ok=True)

        handler_file = handler_dir / f"{name}.go"
        write_atomic(
            handler_file,
            f"package handlers\n\n"
            f'import (\n\t"net/http"\n)\n\n'
            f"// Handle{name.title().replace('_', '')} handles {route_path}\n"
            f"func Handle{name.title().replace('_', '')}"
            f"(w http.ResponseWriter, r *http.Request) {{\n"
            f"\t// TODO: Implement {route_path}\n"
            f"\tw.WriteHeader(http.StatusOK)\n"
            f"}}\n",
        )
        return handler_file

    def _scaffold_react_component(self, name: str) -> Path:
        comp_dir = self.project_root / "src" / "components"
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
        return comp_file

    def _scaffold_python_test(self, name: str) -> Path:
        test_dir = self.project_root / "tests"
        test_dir.mkdir(parents=True, exist_ok=True)

        test_file = test_dir / f"test_{name}.py"
        write_atomic(
            test_file,
            f'"""Tests for {name}."""\n\n'
            f"import pytest\n\n\n"
            f"class Test{name.title().replace('_', '')}:\n"
            f'"""Test suite for {name}."""\n\n'
            f"    def test_placeholder(self) -> None:\n"
            f'        """TODO: Implement tests."""\n'
            f"        assert True\n",
        )
        return test_file

    def _scaffold_ts_test(self, name: str) -> Path:
        test_dir = self.project_root / "tests"
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
        return test_file

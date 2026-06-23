"""Tests for TypeScript scaffolding."""

from pathlib import Path
from gemstack.project.scaffolder import Scaffolder

class TestTypeScriptScaffolding:
    def test_scaffold_route_creates_files(self, tmp_path: Path) -> None:
        route_path = "/api/v1/users"
        Scaffolder(tmp_path)._scaffold_ts_route(route_path)

        route_file = tmp_path / "src" / "routes" / "api-v1-users.ts"
        assert route_file.exists()
        content = route_file.read_text()
        assert "export async function handle(req: Request): Promise<Response>" in content
        assert f'return Response.json({{ status: "ok", path: "{route_path}" }});' in content
        assert "TODO" not in content

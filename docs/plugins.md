# Building Gemstack Plugins

Gemstack uses `pluggy` for deep extensibility. You can add custom Topologies, Roles, or intercept compilation events.

## Example Plugin

Ensure you have `gemstack[plugins]` installed. Provide the hooks within a Python package via your entry points:

```python
# my_plugin.py
from gemstack.plugins.hooks import hookimpl

class MyPlugin:
    @hookimpl
    def gemstack_post_init(self, project_root, profile):
        """Add custom files after gemstack init."""
        (project_root / ".agent" / "CUSTOM.md").write_text("# Custom Context")

    @hookimpl
    def gemstack_register_topologies(self):
        return [{"name": "mobile", "description": "iOS/Android", "content": "..."}]
```

Register this inside your package's `pyproject.toml`:
```toml
[project.entry-points."gemstack"]
my_plugin = "my_plugin:MyPlugin"
```

*The Plugin API guarantees backward compatibility across the 1.x release pipeline.*

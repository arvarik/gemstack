# The `.agent/` Context System

Every Gemstack project stores its essential instructions for the agent within five markdown files located in the `.agent/` directory.

These files act as the **single source of truth** that all AI agents read before modifying your code.

| File | What It Contains |
|------|-----------------|
| **ARCHITECTURE.md** | Topology declaration, tech stack with versions, API contracts, database schemas, environment variables, dev/build/test commands |
| **STYLE.md** | Design system tokens, code naming conventions, file organization patterns, **FORBIDDEN** anti-patterns |
| **TESTING.md** | Test commands per topology, scenario tables, coverage matrices (route coverage, component state, eval thresholds) |
| **PHILOSOPHY.md** | Product soul, core user beliefs, anti-goals, decision principles |
| **STATUS.md** | Current state (`[STATE: READY_FOR_BUILD]`), active feature, lifecycle checkboxes, blocking issues |

### Context Compilation

During execution, Gemstack securely compiles the relevant `.agent/` files into a single, optimized prompt payload:

```bash
gemstack compile step3-build   # View the compiled output payload
gemstack compile step3-build --token-budget 100000  # Specify token limits
```

The compiler applies truncation priorities automatically. For example, `STATUS.md` (which tracks state) is never truncated, while source file listings are clipped first if you exceed your configured context window.

# The 5-Step Lifecycle

Gemstack prevents AI hallucination through **separation of concerns** and **terminal-verified execution**. Each step runs in a fresh context window, forcing the agent to verify its work against tests rather than just writing code blindly.

```text
Step 1        Step 2        Step 3        Step 4        Step 5
 Spec    →     Trap    →    Build    →    Audit    →    Ship
Define it   Write tests   Implement    Verify it   Merge & deploy
             that fail    until pass    (fresh eyes)
                             ↑              │
                             └──── fix ←────┘
                            (if issues found)
```

| Step | Command | What Happens | Roles |
|------|---------|-------------|-------|
| **Spec** | `gemstack run step1-spec` | Define the feature, design UX, lock API contracts | Product Visionary, UX Designer, Architect |
| **Trap** | `gemstack run step2-trap` | Write the task plan and failing test suite | Planner, SDET |
| **Build** | `gemstack run step3-build` | Implement code, loop against terminal until Exit Code 0 | Principal Engineer |
| **Audit** | `gemstack run step4-audit` | Fresh-context security review, SAST, edge case testing | Security Engineer, SDET |
| **Ship** | `gemstack run step5-ship` | Integrate, merge, deploy, archive, reset STATUS.md | DevOps Engineer |

### Why "New Chat" Airgaps?
Every single step starts entirely fresh. The Auditing AI agent cannot be influenced by the Builder AI's justifications. Tests are written before code. This is how you guarantee your code verifies and doesn't just rest on LLM rationalization.

Run `gemstack route` anytime to figure out exactly what step you are currently on.

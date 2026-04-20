# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.x     | ✅ Active support   |
| < 1.0   | ❌ No support       |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, please report vulnerabilities by emailing:

📧 **arvind.arikatla@gmail.com**

Include the following in your report:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### What to Expect

- **Acknowledgment** within 48 hours
- **Initial assessment** within 5 business days
- **Fix timeline** communicated within 10 business days
- **Credit** in the security advisory (unless you prefer anonymity)

## Scope

The following areas are in scope for security reports:

- Path traversal in file read/write operations
- Arbitrary code execution via MCP tools or autonomous execution
- API key exposure or credential leakage
- Prompt injection via `.agent/` file content
- Denial of service via resource exhaustion (unbounded file walks, token budgets)
- Plugin system sandbox escapes

## Security Design

Gemstack implements the following security controls:

- **Path traversal protection** — all file writes are validated against the project root; MCP resource reads are confined to `.agent/`
- **Atomic file writes** — temp-file-then-rename pattern prevents partial writes on crash
- **API key handling** — stored using Pydantic `SecretStr`, masked in all display output
- **Subprocess safety** — no shell expansion; all subprocess calls use explicit argument lists
- **Non-root Docker** — the container image runs as an unprivileged user

## Known Limitations

- **Clipboard content** — `gemstack compile --clipboard` pipes compiled context (which may include user-authored `.agent/` file content) to platform clipboard commands (`pbcopy`, `xclip`, `clip`) without sanitization. This is by design — the content is the user's own project context — but users should be aware that `.agent/` file content is passed through these commands unmodified.
- **Concurrency lock (POSIX-only)** — the `gemstack run` lockfile mechanism uses `fcntl.flock`, which is only available on POSIX systems (macOS, Linux). On native Windows (outside WSL), concurrent execution guards will not function. WSL environments support `fcntl.flock` normally.

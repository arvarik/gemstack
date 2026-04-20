# Multi-stage build for Gemstack CLI
#
# Usage:
#   docker build -t arvarik/gemstack .
#   docker run -v $(pwd):/workspace arvarik/gemstack status
#   docker run -v $(pwd):/workspace -e GEMINI_API_KEY arvarik/gemstack run step1-spec --feature "..."
#
# The image installs gemstack from PyPI (not from source) to ensure
# the published package is what runs in containers.

FROM python:3.12-slim AS base

LABEL org.opencontainers.image.title="Gemstack"
LABEL org.opencontainers.image.description="Opinionated AI agent orchestration framework for Gemini CLI and Antigravity"
LABEL org.opencontainers.image.source="https://github.com/arvarik/gemstack"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.authors="Arvind Arikatla <arvind.arikatla@gmail.com>"

# Prevent .pyc files and enable unbuffered output for clean logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install gemstack with all runtime extras (no dev deps)
# Pin to the version matching the tag via build arg, defaulting to latest
ARG GEMSTACK_VERSION=""
RUN if [ -n "$GEMSTACK_VERSION" ]; then \
      pip install --no-cache-dir "gemstack[ai,mcp,plugins]==$GEMSTACK_VERSION"; \
    else \
      pip install --no-cache-dir "gemstack[ai,mcp,plugins]"; \
    fi

# Create non-root user (UID 1000 matches most host users for volume mounts)
RUN groupadd --gid 1000 gemstack && \
    useradd --uid 1000 --gid gemstack --create-home gemstack

USER gemstack

# Mount your project here
WORKDIR /workspace

# Health check — verify the binary is functional
HEALTHCHECK --interval=30s --timeout=5s --retries=1 \
    CMD ["gemstack", "--version"]

ENTRYPOINT ["gemstack"]
CMD ["--help"]

# Multi-stage build for Gemstack CLI
# No hardcoded versions — pulls from hatch-vcs / PyPI

FROM python:3.12-slim AS base

LABEL maintainer="Arvind Varik"
LABEL description="Gemstack — Opinionated AI agent orchestration framework"

# Prevent Python from writing .pyc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install gemstack with runtime extras only (no dev dependencies)
RUN pip install --no-cache-dir gemstack[ai,mcp,tail,plugins]

# Create non-root user for security
RUN groupadd --gid 1000 gemstack && \
    useradd --uid 1000 --gid gemstack --create-home gemstack

USER gemstack

# Default working directory for project mounting
WORKDIR /workspace

ENTRYPOINT ["gemstack"]
CMD ["--help"]

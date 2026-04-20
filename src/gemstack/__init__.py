"""Gemstack — Opinionated AI agent orchestration framework."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gemstack")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

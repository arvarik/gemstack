"""Shared test fixtures for Gemstack."""

import shutil
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def python_fastapi(tmp_path: Path) -> Path:
    """Create a temporary Python FastAPI project fixture."""
    fixture = FIXTURES_DIR / "python-fastapi"
    dest = tmp_path / "python-fastapi"
    shutil.copytree(fixture, dest)
    return dest


@pytest.fixture
def nextjs_app(tmp_path: Path) -> Path:
    """Create a temporary Next.js project fixture."""
    fixture = FIXTURES_DIR / "nextjs-app"
    dest = tmp_path / "nextjs-app"
    shutil.copytree(fixture, dest)
    return dest


@pytest.fixture
def go_chi(tmp_path: Path) -> Path:
    """Create a temporary Go chi project fixture."""
    fixture = FIXTURES_DIR / "go-chi"
    dest = tmp_path / "go-chi"
    shutil.copytree(fixture, dest)
    return dest


@pytest.fixture
def empty_project(tmp_path: Path) -> Path:
    """Create an empty project fixture."""
    fixture = FIXTURES_DIR / "empty-project"
    dest = tmp_path / "empty-project"
    shutil.copytree(fixture, dest)
    return dest


@pytest.fixture
def bootstrapped_project(tmp_path: Path) -> Path:
    """Create a pre-bootstrapped project fixture."""
    fixture = FIXTURES_DIR / "bootstrapped-project"
    dest = tmp_path / "bootstrapped-project"
    shutil.copytree(fixture, dest)
    return dest

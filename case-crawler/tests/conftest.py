"""Shared test fixtures."""

import os
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add backend to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

# Use a temp DB for tests so we don't pollute real data
os.environ["DB_PATH"] = str(Path(tempfile.mkdtemp()) / "test.db")

from app import app, _load_game_data, _scenarios  # noqa: E402
from database import Base, engine  # noqa: E402


@pytest.fixture(autouse=True, scope="session")
def setup():
    """Load game data and create DB tables before any tests run."""
    _load_game_data()
    Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def scenario():
    """The non-compete scenario data (including scoring)."""
    return _scenarios["non-compete"]

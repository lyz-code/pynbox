"""Store the classes and fixtures used throughout the tests."""

import os
from pathlib import Path
from typing import Generator

import pytest
from repository_orm import FakeRepository

from pynbox.config import Config


@pytest.fixture(name="config")
def fixture_config(tmp_path: Path) -> Config:
    """Configure the Config object for the tests."""
    tinydb_file_path = str(tmp_path / "tinydb.db")
    os.environ["DATABASE_URL"] = f"tinydb:///{tinydb_file_path}"

    config = Config()
    config.load("tests/assets/config.yaml")

    return config


@pytest.fixture(name="repo")
def repo_() -> Generator[FakeRepository, None, None]:
    """Configure a FakeRepository instance."""
    repo = FakeRepository()

    yield repo

    repo.close()

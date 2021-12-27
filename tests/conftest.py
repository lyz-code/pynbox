"""Store the classes and fixtures used throughout the tests."""

import os

import pytest
from py._path.local import LocalPath
from repository_orm import FakeRepository

from pynbox.config import Config
from pynbox.model import Element


@pytest.fixture(name="config")
def fixture_config(tmpdir: LocalPath) -> Config:
    """Configure the Config object for the tests."""
    tinydb_file_path = str(tmpdir.join("tinydb.db"))  # type: ignore
    os.environ["DATABASE_URL"] = f"tinydb:///{tinydb_file_path}"

    config = Config()
    config.load("tests/assets/config.yaml")

    return config


@pytest.fixture(name="repo")
def repo_() -> FakeRepository:
    """Configure a FakeRepository instance."""
    return FakeRepository([Element])

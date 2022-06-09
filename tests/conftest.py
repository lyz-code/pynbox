"""Store the classes and fixtures used throughout the tests."""

import os
from typing import Generator

import pytest
from py._path.local import LocalPath
from repository_orm import FakeRepository

from pynbox.config import Config


@pytest.fixture(name="config")
def fixture_config(tmpdir: LocalPath) -> Config:
    """Configure the Config object for the tests."""
    tinydb_file_path = str(tmpdir.join("tinydb.db"))  # type: ignore
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

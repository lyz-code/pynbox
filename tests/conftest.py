"""Store the classes and fixtures used throughout the tests."""

from shutil import copyfile

import pytest
from _pytest.tmpdir import TempdirFactory
from repository_orm import FakeRepository

from pynbox.config import Config
from pynbox.model import Element


@pytest.fixture(name="config")
def fixture_config(tmpdir_factory: TempdirFactory) -> Config:
    """Configure the Config object for the tests."""
    data = tmpdir_factory.mktemp("data")
    config_file = str(data.join("config.yaml"))
    copyfile("tests/assets/config.yaml", config_file)
    config = Config(config_file)
    config["database_url"] = f"tinydb://{data}/database.tinydb"
    config.save()

    return config


@pytest.fixture(name="repo")
def repo_() -> FakeRepository:
    """Configure a FakeRepository instance."""
    return FakeRepository([Element])

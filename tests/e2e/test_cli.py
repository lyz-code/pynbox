"""Test the command line interface."""

import logging
import re
from typing import List

import pytest
from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner
from py._path.local import LocalPath
from repository_orm import load_repository

from pynbox.config import Config
from pynbox.entrypoints.cli import cli
from pynbox.model import Element
from pynbox.version import __version__

log = logging.getLogger(__name__)


@pytest.fixture(name="runner")
def fixture_runner(config: Config) -> CliRunner:
    """Configure the Click cli test runner."""
    return CliRunner(mix_stderr=False, env={"PYNBOX_CONFIG_PATH": config.config_path})


def test_version(runner: CliRunner) -> None:
    """Prints program version when called with --version."""
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert re.match(
        fr" *pynbox version: {__version__}\n" r" *python version: .*\n *platform: .*",
        result.stdout,
    )


def test_load_config_handles_configerror_exceptions(
    runner: CliRunner, tmpdir: LocalPath, caplog: LogCaptureFixture
) -> None:
    """
    Given: A wrong configuration file.
    When: CLI is initialized
    Then: The ConfigError exception is gracefully handled.
    """
    config_file = tmpdir.join("config.yaml")  # type: ignore
    config_file.write("[ invalid yaml")

    result = runner.invoke(cli, ["-c", str(config_file), "null"])

    assert result.exit_code == 1
    assert (
        "pynbox.entrypoints",
        logging.ERROR,
        f'Configuration Error: while parsing a flow sequence\n  in "{config_file}", '
        "line 1, column 1\nexpected ',' or ']', but got '<stream end>'\n  in"
        f' "{config_file}", line 1, column 15',
    ) in caplog.record_tuples


def test_parse_stores_elements(
    runner: CliRunner, config: Config, tmpdir: LocalPath
) -> None:
    """
    Given: A configured program and a file to parse
    When: parse command line is used
    Then: the element is stored in the repository, and the file is pruned
    """
    parse_file = f"{tmpdir}/parse.pynbox"
    with open(parse_file, "w+") as file_descriptor:
        file_descriptor.write("t. Task title")

    result = runner.invoke(cli, ["parse", parse_file])

    assert result.exit_code == 0
    repo = load_repository(models=[Element], database_url=config["database_url"])
    elements: List[Element] = repo.all()
    assert len(elements) == 1
    assert elements[0].type_ == "task"
    assert elements[0].description == "Task title"
    with open(parse_file, "r") as file_descriptor:
        assert file_descriptor.read() == ""

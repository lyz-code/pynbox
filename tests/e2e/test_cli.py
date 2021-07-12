"""Test the command line interface."""

import logging
import re

import pytest
from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner
from py._path.local import LocalPath
from pynbox.config import Config
from pynbox.entrypoints.cli import cli
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

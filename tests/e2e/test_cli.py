"""Test the command line interface."""

import logging
import os
import re
import subprocess
import sys
import time
from typing import Any, Generator

import pexpect
import pytest
from _pytest.capture import CaptureFixture
from _pytest.logging import LogCaptureFixture
from click.testing import CliRunner
from py._path.local import LocalPath
from repository_orm import Repository, load_repository

from pynbox.config import Config
from pynbox.entrypoints.cli import cli
from pynbox.model import Element, ElementState
from pynbox.version import __version__

log = logging.getLogger(__name__)

CONFIG_PATH = "tests/assets/config.yaml"


@pytest.fixture(name="runner")
def fixture_runner(config: Config) -> CliRunner:
    """Configure the Click cli test runner."""
    return CliRunner(mix_stderr=False, env={"PYNBOX_CONFIG_PATH": CONFIG_PATH})


@pytest.fixture(name="repo")
def repo_(config: Config) -> Generator[Repository, None, None]:
    """Configure a FakeRepository instance."""
    repo = load_repository(database_url=config.database_url)

    yield repo

    repo.close()


def test_version(runner: CliRunner) -> None:
    """Prints program version when called with --version."""
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert re.search(
        rf" *pynbox: {__version__}\n *Python: .*\n *Platform: .*",
        result.stdout,
    )


def test_verbose_is_supported(config: Config, runner: CliRunner) -> None:
    """
    Given: A configured program
    When: Any command is used with the -v flag
    Then: The program runs without problem
    """
    result = runner.invoke(cli, ["-v", "null"])

    assert result.exit_code == 0


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
    runner: CliRunner, config: Config, tmpdir: LocalPath, repo: Repository
) -> None:
    """
    Given: A configured program and a file to parse
    When: parse command line is used
    Then: the element is stored in the repository, and the file is pruned
    """
    parse_file = f"{tmpdir}/parse.pynbox"
    with open(parse_file, "w+", encoding="utf-8") as file_descriptor:
        file_descriptor.write("t. Task title")

    result = runner.invoke(cli, ["parse", parse_file])

    assert result.exit_code == 0
    elements = repo.all(Element)
    assert len(elements) == 1
    assert elements[0].type_ == "task"
    assert elements[0].description == "Task title"
    with open(parse_file, "r", encoding="utf-8") as file_descriptor:
        assert file_descriptor.read() == ""


def test_add_elements(
    runner: CliRunner, config: Config, tmpdir: LocalPath, repo: Repository
) -> None:
    """
    Given: A configured program
    When: add command is used
    Then: the element is stored in the repository
    """
    result = runner.invoke(cli, ["add", "t.", "Task", "title"])

    assert result.exit_code == 0
    elements = repo.all(Element)
    assert len(elements) == 1
    assert elements[0].type_ == "task"
    assert elements[0].description == "Task title"


def test_do_element(config: Config, repo: Repository) -> None:
    """
    Given: An element in the repository
    When: the inbox processing command is used and the done key is pressed
    Then: the element is marked as done and the date is stored
    """
    # Add the element
    repo.add(Element(type_="task", description="Task title", body="task body"))
    repo.commit()
    # Load the TUI
    tui = pexpect.spawn(f"pynbox -c {CONFIG_PATH} process", timeout=5)
    tui.logfile = sys.stdout.buffer
    tui.expect(".*Quit.*")

    tui.sendline("d")  # act

    tui.expect_exact(pexpect.EOF)
    element = repo.all(Element)[0]
    assert element.state == ElementState.CLOSED
    assert element.closed is not None


def test_delete_element(config: Config, repo: Repository) -> None:
    """
    Given: An element in the repository
    When: the inbox processing command is used and the delete key is pressed
    Then: the element is marked as deleted and the date is stored
    """
    # Add the element
    repo.add(Element(type_="task", description="Task title"))
    repo.commit()
    # Load the TUI
    tui = pexpect.spawn(f"pynbox -c {CONFIG_PATH} process", timeout=5)
    tui.logfile = sys.stdout.buffer
    tui.expect(".*Quit.*")

    tui.sendline("e")  # act

    tui.expect_exact(pexpect.EOF)
    element = repo.all(Element)[0]
    assert element.state == ElementState.DELETED
    assert element.closed is not None


def test_skip_element(config: Config, repo: Repository) -> None:
    """
    Given: An element in the repository
    When: the inbox processing command is used and the skip key is pressed
    Then: the element is skipped and the skipped count is increased
    """
    # Add the element
    repo.add(Element(type_="task", description="Task title"))
    repo.commit()
    # Load the TUI
    tui = pexpect.spawn(f"pynbox -c {CONFIG_PATH} process", timeout=5)
    tui.logfile = sys.stdout.buffer
    tui.expect(".*Quit.*")

    tui.sendline("s")  # act

    tui.expect_exact(pexpect.EOF)
    element = repo.all(Element)[0]
    assert element.state == ElementState.OPEN
    assert element.skips == 1
    assert element.closed is None


def test_quit(config: Config, repo: Repository) -> None:
    """
    Given: An element in the repository
    When: the inbox processing command is used and the quit key is pressed
    Then: the element is not changed and the program ends
    """
    # Add the element
    repo.add(Element(type_="task", description="Task title"))
    repo.commit()
    # Load the TUI
    tui = pexpect.spawn(f"pynbox -c {CONFIG_PATH} process", timeout=5)
    tui.logfile = sys.stdout.buffer
    tui.expect(".*Quit.*")

    tui.sendline("q")  # act

    tui.expect_exact(pexpect.EOF)
    element = repo.all(Element)[0]
    assert element.state == ElementState.OPEN
    assert element.closed is None


def test_process_can_select_subset_of_types(config: Config, repo: Repository) -> None:
    """
    Given: Two elements with different types in the repository
    When: the inbox processing command is used specifying the type
    Then: only the element of that type is shown

    As we only give it one command (done), if both elements were shown, the test
    will return an error as it will reach the timeout of pexpect.
    """
    # Add the elements
    repo.add(Element(type_="task", description="Task title"))
    repo.add(Element(type_="idea", description="Idea title"))
    repo.commit()
    # Load the TUI
    tui = pexpect.spawn(f"pynbox -c {CONFIG_PATH} process idea", timeout=5)
    tui.logfile = sys.stdout.buffer
    tui.expect(".*Quit.*")

    tui.sendline("d")  # act

    tui.expect_exact(pexpect.EOF)
    task = repo.all(Element)[0]
    idea = repo.all(Element)[1]
    assert task.state == ElementState.OPEN
    assert idea.state == ElementState.CLOSED


def test_process_shows_warning_if_max_time_surpassed(
    config: Config, capsys: CaptureFixture[Any], repo: Repository
) -> None:
    """
    Given: An element in the repository
    When: the inbox processing command is used, and the user takes longer than max_time
        to process an element
    Then: A warning is shown in the terminal.
    """
    # Configure the max_time to 0 so the warning is always raised
    os.environ["max_time"] = "0"
    # Add the elements
    repo.add(Element(type_="task", description="Task title"))
    repo.commit()
    # Load the TUI
    tui = pexpect.spawn(f"pynbox -c {CONFIG_PATH} process", timeout=5)
    tui.logfile = sys.stdout.buffer
    tui.expect(".*Quit.*")

    tui.sendline("d")  # act

    tui.expect_exact(pexpect.EOF)
    out, err = capsys.readouterr()
    assert err == ""
    assert re.search(
        (
            "WARNING!.* it took you more than .*0.* minutes "
            "to process the last element: .*0.*"
        ),
        out,
    )


def test_process_shows_a_report_of_the_status_of_the_inbox(
    config: Config, capsys: CaptureFixture[Any], repo: Repository
) -> None:
    """
    Given: Two elements in the repository
    When: the inbox processing command is used on just one.
    Then: A report of the state of the inbox is shown.
    """
    # Add the elements
    repo.add(Element(type_="task", description="Task title"))
    repo.add(Element(type_="task", description="Task title 2"))
    repo.commit()
    # Load the TUI
    tui = pexpect.spawn(f"pynbox -c {CONFIG_PATH} process", timeout=5)
    tui.logfile = sys.stdout.buffer
    tui.expect(".*Quit.*")
    tui.sendline("d")

    tui.sendline("q")  # act

    tui.expect_exact(pexpect.EOF)
    out, err = capsys.readouterr()
    assert "" in out
    assert err == ""
    assert re.search(
        (
            "It took you .*0.* minutes to process .*1.* elements. "
            "There are still .*1.* left"
        ),
        out,
    )


def test_status_returns_the_pending_element_numbers_by_type(
    runner: CliRunner, config: Config, repo: Repository
) -> None:
    """
    Given: Three elements in the repository
    When: The status command is called
    Then: A list of types with the number of pending elements are returned
    """
    # Add the elements
    repo.add(Element(type_="idea", description="Idea title"))
    repo.add(Element(type_="task", description="Task title"))
    repo.add(Element(type_="task", description="Task title 2"))
    repo.commit()

    result = runner.invoke(cli, ["status"])

    assert result.exit_code == 0
    assert re.search(
        r"Task.*2.*\n.*Idea.*1",
        result.stdout,
    )


def test_process_can_select_newest_order(config: Config, repo: Repository) -> None:
    """
    Given: Two elements in the repository
    When: the inbox processing command is used specifying the newest flag, the first
        element is marked as done and the second as skipped
    Then: The newest item is marked as done and the oldest as skipped

    As we only give it one command (done), if both elements were shown, the test
    will return an error as it will reach the timeout of pexpect.
    """
    # Add the elements
    repo.add(Element(type_="task", description="Old task"))
    repo.add(Element(type_="task", description="New task"))
    repo.commit()
    # Load the TUI
    tui = pexpect.spawn(f"pynbox -c {CONFIG_PATH} process -n", timeout=5)
    tui.logfile = sys.stdout.buffer
    tui.expect(".*Quit.*")

    tui.sendline("d")  # act

    tui.sendline("s")
    tui.expect_exact(pexpect.EOF)
    old = repo.all(Element)[0]
    new = repo.all(Element)[1]
    assert old.state == ElementState.OPEN
    assert new.state == ElementState.CLOSED


def test_change_element_type(config: Config, repo: Repository) -> None:
    """
    Given: An element in the repository
    When: the inbox processing command is used and the change key is pressed
    Then: the element type is changed
    """
    # Add the element
    repo.add(Element(type_="task", description="Idea title"))
    repo.commit()
    # Load the TUI
    tui = pexpect.spawn(f"pynbox -c {CONFIG_PATH} process", timeout=5)
    tui.logfile = sys.stdout.buffer
    tui.expect(".*Quit.*")

    tui.sendline("t")  # act

    tui.expect(".*Select the new type.*")
    tui.sendline("j")
    tui.expect_exact(pexpect.EOF)
    element = repo.all(Element)[0]
    assert element.type_ == "idea"
    assert element.state == ElementState.OPEN
    assert element.skips == 0
    assert element.closed is None


# It doesn't have an X server so the test fails
@pytest.mark.skip_ci()
def test_copy_text_to_clipboard(config: Config, repo: Repository) -> None:
    """
    Given: An element in the repository
    When: the inbox processing command is used and the copy key is pressed
        Then we use q to quit the program
    Then: The element text is copied to the clipboard
    """
    # Add the element
    repo.add(Element(type_="task", description="Task title"))
    repo.commit()
    # Load the TUI
    tui = pexpect.spawn(f"pynbox -c {CONFIG_PATH} process", timeout=5)
    tui.logfile = sys.stdout.buffer
    tui.expect(".*Quit.*")

    tui.sendline("c")  # act

    # We need to wait so it has time to copy it
    time.sleep(2)
    assert (
        subprocess.check_output(["xclip", "-o", "-selection", "clipboard"]).decode(
            "utf-8"
        )
        == "Task title"
    )
    tui.sendline("q")
    tui.expect_exact(pexpect.EOF)

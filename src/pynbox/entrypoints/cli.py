"""Define the command line interface."""

import subprocess  # nosec
import time
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

import click
from click.core import Context
from questionary import Choice, select
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .. import services, version, views
from . import get_repo, load_config, load_logger

if TYPE_CHECKING:
    from ..model import Element


@click.group()
@click.version_option(version="", message=version.version_info())
@click.option("-v", "--verbose", is_flag=True)
@click.option(
    "-c",
    "--config_path",
    default="~/.local/share/pynbox/config.yaml",
    help="configuration file path",
    envvar="PYNBOX_CONFIG_PATH",
)
@click.pass_context
def cli(ctx: Context, config_path: str, verbose: bool) -> None:
    """Command line interface main click entrypoint."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = load_config(config_path)
    ctx.obj["repo"] = get_repo(ctx.obj["config"])
    ctx.obj["verbose"] = verbose

    load_logger(verbose)


@cli.command()
@click.argument("file_path")
@click.pass_context
def parse(ctx: Context, file_path: str) -> None:
    """Parse a markup file and add the elements to the repository."""
    repo = ctx.obj["repo"]

    services.parse_file(ctx.obj["config"], repo, file_path)

    repo.close()


@cli.command()
@click.argument("element_strings", nargs=-1)
@click.pass_context
def add(ctx: Context, element_strings: List[str]) -> None:
    """Parse a markup file and add the elements to the repository."""
    repo = ctx.obj["repo"]

    element = services.parse(ctx.obj["config"], " ".join(element_strings))[0]

    repo.add(element)
    repo.commit()
    repo.close()


@cli.command()
@click.pass_context
def status(ctx: Context) -> None:
    """Print the status of the inbox."""
    repo = ctx.obj["repo"]
    status_data = views.status(repo, ctx.obj["config"])
    repo.close()

    total_elements = sum([v for k, v in status_data.items()])
    table = Table(box=box.MINIMAL_HEAVY_HEAD, show_footer=True)

    table.add_column("Type", justify="left", style="green", footer="Total")
    table.add_column("Elements", style="magenta", footer=str(total_elements))

    for type_, elements in status_data.items():
        table.add_row(type_.title(), str(elements))

    console = Console()
    console.print(table)


class Choices(str, Enum):
    """Set the possible cli choices."""

    DONE = "Done"
    COPY = "Copy to clipboard"
    SKIP = "Skip"
    DELETE = "Delete"
    CHANGE = "Change type"
    QUIT = "Quit"


@cli.command()
@click.argument("type_", required=False, default=None)
@click.option("-n", "--newest", is_flag=True)
@click.pass_context
def process(ctx: Context, type_: Optional[str] = None, newest: bool = False) -> None:
    """Create a TUI interface to process the elements."""
    console = Console()
    session_start = time.time()
    repo = ctx.obj["repo"]
    config = ctx.obj["config"]

    choices = [
        Choice(title=Choices.DONE, shortcut_key="d"),
        Choice(title=Choices.COPY, shortcut_key="c"),
        Choice(title=Choices.SKIP, shortcut_key="s"),
        Choice(title=Choices.DELETE, shortcut_key="e"),
        Choice(title=Choices.CHANGE, shortcut_key="t"),
        Choice(title=Choices.QUIT, shortcut_key="q"),
    ]

    elements = views.get_elements(repo, config, type_, newest)
    processed_elements = 0
    for element in elements:
        try:
            processed_elements = _process_element(
                ctx, element, console, choices, processed_elements
            )
        except StopIteration:
            break
    repo.close()
    session_end = time.time()

    text = Text.assemble(
        "It took you ",
        (str(round((session_end - session_start) / 60)), "magenta"),
        " minutes to process ",
        (str(processed_elements), "green"),
        " elements. There are still ",
        (str(len(elements) - processed_elements), "red"),
        " left.",
    )
    console.print(text)


def _process_element(
    ctx: Context,
    element: "Element",
    console: Console,
    choices: List[Choice],
    processed_elements: int,
) -> int:
    """Create a TUI interface to process an Element."""
    repo = ctx.obj["repo"]
    config = ctx.obj["config"]

    if element.body is None or element.body == "":
        prompt = f"[{element.type_.title()}] {element.description}"
    else:
        prompt = f"[{element.type_.title()}] {element.description}\n\n{element.body}"
    start = time.time()
    while True:
        choice = select(
            prompt,
            qmark="\n",
            choices=choices,
            use_shortcuts=True,
        ).ask()
        if choice == Choices.COPY:
            subprocess.run(  # nosec
                ["xclip", "-selection", "clipboard", "-i"],
                input=element.description,
                text=True,
                check=True,
            )
        else:
            break

    end = time.time()

    if end - start > config.max_time:
        text = Text.assemble(
            ("\nWARNING!", "bold red"),
            " it took you more than ",
            (str(round(config.max_time / 60)), "green"),
            " minutes to process the last element: ",
            (str(round((end - start) / 60)), "red"),
        )
        console.print(text)
        print()

    if choice == Choices.DONE:
        element.close()
        processed_elements += 1
    elif choice == Choices.DELETE:
        element.delete()
        processed_elements += 1
    elif choice == Choices.SKIP:
        element.skip()
    elif choice == Choices.CHANGE:
        types = [type_.name for type_ in config.types]
        choice = select(
            "Select the new type", choices=types, default=element.type_
        ).ask()
        element.type_ = choice
    elif choice == Choices.QUIT:
        raise StopIteration
    repo.add(element)
    repo.commit()
    return processed_elements


@cli.command(hidden=True)
@click.pass_context
def null(ctx: Context) -> None:
    """Do nothing.

    Used for the tests until we have a better solution.
    """
    ctx.obj["repo"].close()


if __name__ == "__main__":  # pragma: no cover
    # E1120: As the arguments are passed through the function decorators instead of
    # during the function call, pylint get's confused.
    cli(ctx={})  # noqa: E1120

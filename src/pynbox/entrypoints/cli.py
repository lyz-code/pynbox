"""Define the command line interface."""

import time
from typing import List, Optional

import click
from click.core import Context
from questionary import Choice, select
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .. import services, version
from . import get_repo, load_config, load_logger


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
    services.parse_file(ctx.obj["config"], ctx.obj["repo"], file_path)


@cli.command()
@click.argument("element_strings", nargs=-1)
@click.pass_context
def add(ctx: Context, element_strings: List[str]) -> None:
    """Parse a markup file and add the elements to the repository."""
    repo = ctx.obj["repo"]

    element = services.parse(ctx.obj["config"], " ".join(element_strings))[0]

    repo.add(element)
    repo.commit()


@cli.command()
@click.pass_context
def status(ctx: Context) -> None:
    """Print the status of the inbox."""
    status_data = services.status(ctx.obj["repo"], ctx.obj["config"])

    total_elements = sum([v for k, v in status_data.items()])
    table = Table(box=box.MINIMAL_HEAVY_HEAD, show_footer=True)

    table.add_column("Type", justify="left", style="green", footer="Total")
    table.add_column("Elements", style="magenta", footer=str(total_elements))

    for type_, elements in status_data.items():
        table.add_row(type_.title(), str(elements))

    console = Console()
    console.print(table)


@cli.command()
@click.argument("type_", required=False, default=None)
@click.pass_context
def process(ctx: Context, type_: Optional[str] = None) -> None:
    """Create a TUI interface to process the elements."""
    console = Console()
    session_start = time.time()
    repo = ctx.obj["repo"]
    config = ctx.obj["config"]
    choices = [
        Choice(title="Done", shortcut_key="d"),
        Choice(title="Skip", shortcut_key="s"),
        Choice(title="Delete", shortcut_key="e"),
        Choice(title="Quit", shortcut_key="q"),
    ]
    elements = services.elements(repo, config, type_)
    processed_elements = 0
    for element in elements:
        if element.body is None or element.body == "":
            prompt = f"[{element.type_.title()}] {element.description}"
        else:
            prompt = (
                f"[{element.type_.title()}] {element.description}\n\n{element.body}"
            )
        start = time.time()
        choice = select(
            prompt,
            qmark="\n",
            choices=choices,
            use_shortcuts=True,
        ).ask()
        end = time.time()

        if end - start > config["max_time"]:
            text = Text.assemble(
                ("\nWARNING!", "bold red"),
                " it took you more than ",
                (str(round(config["max_time"] / 60)), "green"),
                " minutes to process the last element: ",
                (str(round((end - start) / 60)), "red"),
            )
            console.print(text)
            print()

        if choice == "Done":
            element.close()
            processed_elements += 1
        elif choice == "Delete":
            element.delete()
            processed_elements += 1
        elif choice == "Skip":
            element.skip()
        elif choice == "Quit":
            break
        repo.add(element)
        repo.commit()
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


@cli.command(hidden=True)
def null() -> None:
    """Do nothing.

    Used for the tests until we have a better solution.
    """


if __name__ == "__main__":  # pragma: no cover
    # E1120: As the arguments are passed through the function decorators instead of
    # during the function call, pylint get's confused.
    cli(ctx={})  # noqa: E1120

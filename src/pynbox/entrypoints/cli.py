"""Command line interface definition."""

import click
from click.core import Context

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
    load_logger(verbose)


@cli.command()
@click.argument("file_path")
@click.pass_context
def parse(ctx: Context, file_path: str) -> None:
    """Parse a markup file and add the elements to the repository."""
    services.parse_file(ctx.obj["config"], ctx.obj["repo"], file_path)


@cli.command(hidden=True)
def null() -> None:
    """Do nothing.

    Used for the tests until we have a better solution.
    """


if __name__ == "__main__":  # pragma: no cover
    # E1120: As the arguments are passed through the function decorators instead of
    # during the function call, pylint get's confused.
    cli(ctx={})  # noqa: E1120

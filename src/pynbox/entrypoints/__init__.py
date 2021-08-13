"""Define the different ways to expose the program functionality.

Functions:
    load_logger: Configure the Logging logger.
"""

import logging
import os
import sys
from contextlib import suppress
from shutil import copyfile

import pkg_resources
from repository_orm import Repository, load_repository

from pynbox.config import Config, ConfigError

from ..model import Element

log = logging.getLogger(__name__)


def load_config(config_path: str) -> Config:
    """Load the configuration from the file."""
    log.debug(f"Loading the configuration from file {config_path}")
    config_path = os.path.expanduser(config_path)

    with suppress(FileExistsError):
        data_directory = os.path.expanduser("~/.local/share/pynbox")
        os.makedirs(data_directory)
        log.debug("Data directory created")  # pragma: no cover

    while True:
        try:
            return Config(config_path)
        except ConfigError as error:
            log.error(f"Configuration Error: {str(error)}")
            sys.exit(1)
        except FileNotFoundError:
            log.info(f"Error opening configuration file {config_path}")
            copyfile(
                pkg_resources.resource_filename("pynbox", "assets/config.yaml"),
                config_path,
            )
            log.info("Copied default configuration template")


def get_repo(config: Config) -> Repository:
    """Configure the repository."""
    log.debug("Initializing repository")
    repo = load_repository([Element], config["database_url"])

    return repo


# I have no idea how to test this function :(. If you do, please send a PR.
def load_logger(verbose: bool = False) -> None:  # pragma no cover
    """Configure the Logging logger.

    Args:
        verbose: Set the logging level to Debug.
    """
    logging.addLevelName(logging.INFO, "[\033[36m+\033[0m]")
    logging.addLevelName(logging.ERROR, "[\033[31m+\033[0m]")
    logging.addLevelName(logging.DEBUG, "[\033[32m+\033[0m]")
    logging.addLevelName(logging.WARNING, "[\033[33m+\033[0m]")
    if verbose:
        logging.basicConfig(
            stream=sys.stderr, level=logging.DEBUG, format="%(levelname)s %(message)s"
        )
    else:
        logging.basicConfig(
            stream=sys.stderr, level=logging.INFO, format="%(levelname)s %(message)s"
        )

"""Define the configuration of the main program."""

import os
from enum import Enum
from typing import List

from goodconf import GoodConf

from .model import ElementType


class LogLevel(str, Enum):
    """Define the possible log levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Config(GoodConf):  # type: ignore
    """Configure the frontend."""

    # URL specifying the connection to the database. For example:
    #   * tinydb: tinydb:////home/user/database.tinydb
    #   * sqlite: sqlite:////home/user/mydb.sqlite
    #   * mysql: mysql://scott:tiger@localhost/mydatabase
    database_url: str = "tinydb://~/.local/share/pynbox/database.json"

    # Maximum time to process an element. A warning will be shown if it takes you
    # longer.
    max_time: int = 120

    # List of element types. Each element can define:
    #   * regexp: regular expression that identifies it
    #   * priority: type priority, by default 3.
    types: List[ElementType] = []

    log_level: LogLevel = LogLevel.INFO

    class Config:
        """Define the default files to check."""

        default_files = [
            os.path.expanduser("~/.local/share/pynbox/config.yaml"),
            "config.yaml",
        ]

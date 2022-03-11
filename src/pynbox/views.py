"""Define the views of the program."""

import operator
from contextlib import suppress
from typing import Dict, List, Optional

from repository_orm import EntityNotFoundError, Repository

from .config import Config
from .model import Element


def get_elements(
    repo: Repository, config: Config, type_: Optional[str] = None, newest: bool = False
) -> List[Element]:
    """Fetch and order the elements to process.

    Args:
        repo: Repository where the elements live.
        type_: type of element to process.
        newest: Whether to show newest items first

    Returns:
        Ordered list of elements to process.
    """
    if type_ is None:
        types = [type_.name for type_ in config.types]
    else:
        types = [type_]

    elements = []
    for element_type in types:
        with suppress(EntityNotFoundError):
            new_elements = repo.search(
                {"state": "open", "type_": element_type}, Element
            )
            if newest:
                elements.extend(
                    sorted(
                        new_elements, key=operator.attrgetter("created"), reverse=True
                    ),
                )
            else:
                elements.extend(new_elements)

    return elements


def status(repo: Repository, config: Config) -> Dict[str, int]:
    """Get the number of open elements per type.

    Args:
        repo: Repository where the elements live.
        type_: type of element to process.

    Returns:
        Number of open tasks per type
    """
    element_status = {}
    for type_ in config.types:
        with suppress(EntityNotFoundError):
            elements = len(repo.search({"state": "open", "type_": type_.name}, Element))
            if elements > 0:
                element_status[type_.name] = elements
    return element_status

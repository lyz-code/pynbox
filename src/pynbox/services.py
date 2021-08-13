"""Gather all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

import logging
import re
from contextlib import suppress
from typing import Dict, List, Optional

from repository_orm import EntityNotFoundError, Repository

from .config import Config
from .exceptions import ParseError
from .model import Element

log = logging.getLogger(__name__)


def parse(config: Config, text: str) -> List[Element]:
    """Extract Elements from a text.

    Args:
        config: pynbox configuration instance.
        text: To process.

    Returns:
        List of extracted Elements.
    """
    elements: List[Element] = []
    element = None

    type_regexps = {
        key: re.compile(rf"^{value['regexp']} ?(.*)", re.IGNORECASE)
        for key, value in config["types"].items()
    }
    priority_regexp = re.compile(r"\s([h])(?:\s|$)", re.IGNORECASE)

    log.debug("Parsing elements")
    for line in text.splitlines():
        for type_, regexp in type_regexps.items():
            match = regexp.match(line)
            if match:
                elements = _register_element(element, elements)
                element = Element(type_=type_, description=match.groups()[0])
                if priority_regexp.search(line):
                    element.description = priority_regexp.sub("", element.description)
                    element.priority = 5
                break
        else:
            if element is None:
                raise ParseError(f"No element to append the body of line {line}")
            if element.body is None:
                element.body = f"{line}"
            else:
                element.body += f"\n{line}"

    elements = _register_element(element, elements)
    return elements


def _register_element(
    element: Optional[Element], elements: List[Element]
) -> List[Element]:
    """Register an element in a list of elements.

    Args:
        element: Element to register
        elements: existing elements.

    Returns:
        list of elements with the new element introduced.
    """
    if element is not None:
        if element.body is not None:
            element.body = element.body.strip()
            log.debug(f"{element.type_}: {element.description}\n\n{element.body}")
        else:
            log.debug(f"{element.type_}: {element.description}")
        elements.append(element)
    return elements


def parse_file(config: Config, repo: Repository, file_path: str) -> None:
    """Parse the elements from a file.

    Args:
        config: pynbox configuration instance.
        repo: repository to store the elements
        file_path: Path to file to parse.
    """
    with open(file_path, "r") as file_descriptor:
        elements = parse(config, file_descriptor.read())

    for element in elements:
        repo.add(element)
    repo.commit()

    with open(file_path, "w") as file_descriptor:
        file_descriptor.write("")


def elements(
    repo: Repository, config: Config, type_: Optional[str] = None
) -> List[Element]:
    """Fetch and order the elements to process.

    Args:
        repo: Repository where the elements live.
        type_: type of element to process.

    Returns:
        Ordered list of elements to process.
    """
    if type_ is None:
        types = config.types()
    else:
        types = [type_]

    elements = []
    for type_ in types:
        with suppress(EntityNotFoundError):
            elements.extend(repo.search({"state": "open", "type_": type_}, Element))

    return elements


def status(repo: Repository, config: Config) -> Dict[str, int]:
    """Get the number of open elements per type.

    Args:
        repo: Repository where the elements live.
        type_: type of element to process.

    Returns:
        Number of open tasks per type
    """
    status = {}
    for type_ in config.types():
        with suppress(EntityNotFoundError):
            elements = len(repo.search({"state": "open", "type_": type_}, Element))
            if elements > 0:
                status[type_] = elements
    return status

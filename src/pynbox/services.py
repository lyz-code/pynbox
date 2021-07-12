"""Gather all the orchestration functionality required by the program to work.

Classes and functions that connect the different domain model objects with the adapters
and handlers to achieve the program's purpose.
"""

import re
from typing import List

from repository_orm import Repository

from .config import Config
from .exceptions import ParseError
from .model import Element


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

    for line in text.splitlines():
        for type_, regexp in type_regexps.items():
            match = regexp.match(line)
            if match:
                if element is not None:
                    elements.append(element)
                element = Element(type_=type_, description=match.groups()[0])
                if priority_regexp.search(line):
                    element.description = priority_regexp.sub("", element.description)
                    element.priority = 5
                break
        else:
            if element is None:
                raise ParseError("No element to append the body of line {line}")
            if element.body is None:
                element.body = line
            else:
                element.body = (element.body + line).strip()

    if element is not None:
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

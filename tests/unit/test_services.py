"""Tests the service layer."""

from textwrap import dedent

import pytest

from pynbox import services
from pynbox.config import Config
from pynbox.exceptions import ParseError


def test_parse_processes_one_element(config: Config) -> None:
    """
    Given: A markup compatible string with one element.
    When: it's parsed
    Then: A list with the element is returned
    """
    text = "t. Task title"

    result = services.parse(config, text)

    assert len(result) == 1
    assert result[0].type_ == "task"
    assert result[0].description == "Task title"


def test_parse_processes_two_elements(config: Config) -> None:
    """
    Given: A markup compatible string with two elements.
    When: it's parsed
    Then: A list with the elements is returned
    """
    text = dedent(
        """\
        t. Task title
        I. Idea title
        """
    )

    result = services.parse(config, text)

    assert len(result) == 2
    assert result[0].type_ == "task"
    assert result[0].description == "Task title"
    assert result[1].type_ == "idea"
    assert result[1].description == "Idea title"


def test_parse_processes_one_element_with_body(config: Config) -> None:
    """
    Given: A markup compatible string with one element with a body.
    When: it's parsed
    Then: A list with the element is returned
    """
    text = dedent(
        """\
        t. Task title

        Task body

        Second paragraph
        """
    )

    result = services.parse(config, text)

    assert len(result) == 1
    assert result[0].type_ == "task"
    assert result[0].description == "Task title"
    assert result[0].body == "Task body\n\nSecond paragraph"


def test_parse_processes_two_elements_with_body(config: Config) -> None:
    """
    Given: A markup compatible string with two elements with a body.
    When: it's parsed
    Then: A list with the elements is returned
    """
    text = dedent(
        """\
        t. Task title

        Task body
        I. Idea title
        """
    )

    result = services.parse(config, text)

    assert len(result) == 2
    assert result[0].type_ == "task"
    assert result[0].description == "Task title"
    assert result[0].body == "Task body"
    assert result[1].type_ == "idea"
    assert result[1].description == "Idea title"


def test_parse_returns_error_if_text_doesnt_comply_with_markup(config: Config) -> None:
    """
    Given: A markup incompatible string
    When: it's parsed
    Then: an error is returned
    """
    text = "Incompatible text"

    with pytest.raises(ParseError, match="No element to append"):
        services.parse(config, text)


def test_parse_extracts_priority_from_description(config: Config) -> None:
    """
    Given: A markup compatible string with the priority keyword
    When: it's parsed
    Then: the element returned has high priority.
    """
    text = "t. Task title h"

    result = services.parse(config, text)

    assert len(result) == 1
    assert result[0].type_ == "task"
    assert result[0].description == "Task title"
    assert result[0].priority == 5

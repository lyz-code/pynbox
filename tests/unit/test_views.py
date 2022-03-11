"""Tests the views layer."""

from datetime import datetime

from repository_orm import Repository

from pynbox import views
from pynbox.config import Config
from pynbox.model import Element


def test_elements_returns_ordered_items(config: Config, repo: Repository) -> None:
    """
    Given: Three tasks, of different types_ and creation dates
    When: elements is called
    Then: The elements are returned ordered first by priority of type and then by
        creation date with the oldest first.
    """
    elements = [
        Element(
            description="Low priority and old",
            type_="idea",
            created=datetime(2020, 1, 2),
        ),
        Element(
            description="Low priority and new",
            type_="idea",
            created=datetime(2020, 2, 2),
        ),
        Element(
            description="High priority and old",
            type_="task",
            created=datetime(2020, 1, 1),
        ),
        Element(
            description="High priority and new",
            type_="task",
            created=datetime(2020, 2, 1),
        ),
    ]
    for element in elements:
        repo.add(element)
    repo.commit()

    result = views.get_elements(repo, config)

    assert result[0] == elements[2]
    assert result[1] == elements[3]
    assert result[2] == elements[0]
    assert result[3] == elements[1]


def test_elements_returns_ordered_items_when_newest(
    config: Config, repo: Repository
) -> None:
    """
    Given: Three tasks, of different types_ and creation dates
    When: elements is called with the newest flag
    Then: The elements are returned ordered first by priority of type and then by
        creation date with the newest first.
    """
    elements = [
        Element(
            description="Low priority and old",
            type_="idea",
            created=datetime(2020, 1, 2),
        ),
        Element(
            description="Low priority and new",
            type_="idea",
            created=datetime(2020, 2, 2),
        ),
        Element(
            description="High priority and old",
            type_="task",
            created=datetime(2020, 1, 1),
        ),
        Element(
            description="High priority and new",
            type_="task",
            created=datetime(2020, 2, 1),
        ),
    ]
    for element in elements:
        repo.add(element)
    repo.commit()

    result = views.get_elements(repo, config, newest=True)

    assert result[0] == elements[3]
    assert result[1] == elements[2]
    assert result[2] == elements[1]
    assert result[3] == elements[0]

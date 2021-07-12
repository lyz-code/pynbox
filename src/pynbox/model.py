"""Define the program models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import Field
from repository_orm import Entity


class ElementState(str, Enum):
    """Define the possible element states."""

    OPEN = "open"
    CLOSED = "closed"


class Element(Entity):
    """Define the element model."""

    type_: str
    description: str
    body: Optional[str] = None
    priority: int = 3
    state: ElementState = ElementState.OPEN
    created: datetime = Field(default_factory=datetime.now)
    closed: Optional[datetime] = None

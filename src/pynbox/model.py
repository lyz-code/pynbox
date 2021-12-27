"""Define the program models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel  # noqa: E0611
from pydantic import Field
from repository_orm import Entity


class ElementType(BaseModel):
    """Define the configuration attributes of the element types."""

    name: str
    regexp: str
    priority: int = 3


class ElementState(str, Enum):
    """Define the possible element states."""

    OPEN = "open"
    CLOSED = "closed"
    DELETED = "deleted"


class Element(Entity):
    """Define the element model."""

    type_: str
    description: str
    body: Optional[str] = None
    priority: int = 3
    skips: int = 0
    state: ElementState = ElementState.OPEN
    created: datetime = Field(default_factory=datetime.now)
    closed: Optional[datetime] = None

    def close(self) -> None:
        """Close an element."""
        self.state = ElementState.CLOSED
        self.closed = datetime.now()

    def delete(self) -> None:
        """Delete an element."""
        self.state = ElementState.DELETED
        self.closed = datetime.now()

    def skip(self) -> None:
        """Skip an element."""
        self.skips += 1

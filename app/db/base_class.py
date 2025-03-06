"""
Base class for SQLAlchemy models.
"""

from typing import Any

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    Base class for all SQLAlchemy models.

    Provides common functionality and naming conventions for all models.
    """

    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Generate __tablename__ automatically from the class name.

        Returns:
            str: The table name in snake_case
        """
        return cls.__name__.lower()

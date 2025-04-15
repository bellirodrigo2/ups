import json
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from sqlalchemy import Dialect
from sqlalchemy.dialects.postgresql import JSON as PGJSON
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column
from sqlalchemy.types import TEXT, TypeDecorator

T = TypeVar("T")


class Base(DeclarativeBase):
    pass


class CreatedAt:
    @declared_attr
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(default=datetime.now)


class JSONEncoded(TypeDecorator[T], Generic[T]):

    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value: Optional[T], dialect: Dialect) -> Optional[str]:
        return json.dumps(value) if value is not None else None

    def process_result_value(
        self, value: Optional[str], dialect: Dialect
    ) -> Optional[T]:
        return json.loads(value) if value is not None else None


def json_column(**kwargs: Any) -> Mapped[Any]:
    dialect = kwargs.get("dialect", None)

    if dialect and dialect.name == "postgresql":
        return mapped_column(PGJSON(), **kwargs)
    else:
        return mapped_column(JSONEncoded[Any](), **kwargs)

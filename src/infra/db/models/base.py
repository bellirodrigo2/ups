import json
from typing import Generic, TypeVar

from sqlalchemy import Dialect
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.types import TEXT, TypeDecorator

T = TypeVar("T")


class JSONEncoded(TypeDecorator[str], Generic[T]):
    """TypeDecorator genérico para armazenar qualquer objeto serializável em JSON."""

    impl = TEXT
    cache_ok = True

    def process_bind_param(self, value: T | None, dialect: Dialect) -> str | None:
        return json.dumps(value) if value is not None else None

    def process_result_value(self, value: str | None, dialect: Dialect) -> T | None:
        return json.loads(value) if value is not None else None


class JSONDict(JSONEncoded[dict[str, str]]):
    pass


class JSONList(JSONEncoded[list[str]]):
    pass


class JSONTupleList(JSONEncoded[list[tuple[str, dict[str, str]]]]):
    pass


class Base(DeclarativeBase):
    pass

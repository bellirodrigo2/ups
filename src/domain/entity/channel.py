from typing import Any

from pydantic import BaseModel


class Channel(BaseModel):
    name: str
    type: str
    data: dict[str, Any]

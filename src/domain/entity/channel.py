from typing import Any

from pydantic import BaseModel


class Channel(BaseModel):
    id: str
    type: str
    configdata: dict[str, Any]

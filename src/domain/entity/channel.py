
from typing import Any

from pydantic import BaseModel


class Channel(BaseModel):
    type:str
    data: dict[str, Any]
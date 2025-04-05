from datetime import datetime

from pydantic import BaseModel


class FollowUp(BaseModel):
    fupid: str
    fupgenid: str
    date: datetime
    data: dict[str, str] = {}
    responses: list[tuple[str, dict[str, str]]]  # (channel, response)

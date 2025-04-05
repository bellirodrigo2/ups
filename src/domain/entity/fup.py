from datetime import datetime
from typing import Any

from pydantic import BaseModel


class FollowUp(BaseModel):
    fupid: str
    fupgenid: str
    date: datetime
    msg:str
    data: dict[str, str]
    responses: list[tuple[str, Any]]  # (channel, response)

    def update_response(self, channel: str, response: Any) -> None:
        for resp in self.responses:
            if resp[0] == channel:
                resp[1].update(response)
                
        
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from domain.entity.channel import Channel


class FollowUp(BaseModel):
    fupid: str
    fupgenid: str
    date: datetime
    msg: str
    # data: dict[str, str]
    responses: dict[Channel, Any]

    def update_response(self, id:str, response:Any):

        channel = next((ch for ch in self.responses if ch.id == id), None)
        
        if channel:
            self.responses[channel] = response
        else:
            raise ValueError(f"Channel '{id}'' not found in responses")
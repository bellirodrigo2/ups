from datetime import timedelta
from typing import Any

from pydantic import BaseModel

from domain.entity.channel import Channel
from domain.entity.recurrence import RecurrenceConfig, SchedulerManager


class FupGenBase(BaseModel):
    hookid: str
    ownerid: str
    name: str
    channel: list[Channel]
    description: str | None = None
    default_cycle: timedelta


class FupGenInput(FupGenBase):
    recurcoinfig: RecurrenceConfig
    msg: str  # | Callable[[dict[str, Any]], str]
    data: dict[str, Any] = {}


class FollowupGenerator(FupGenBase):
    id: str
    scheduler: SchedulerManager
    msg: tuple[str, str]
    data: tuple[str, dict[str, Any]]


if __name__ == "__main__":
    ...

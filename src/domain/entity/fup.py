from datetime import datetime
from typing import Callable

from pydantic import BaseModel

from domain.entity.fupgen import FollowupGenerator


class FollowUp(BaseModel):
    # fupid: str
    fupgenid: str
    date: datetime
    msgid: str
    dataid: str


def make_fup(
    fupgen: FollowupGenerator, ts: datetime
) -> list[FollowUp]:  # , makeid: Callable[[], str]):
    dates = fupgen.scheduler.schedule(ts)
    return [
        FollowUp(
            # fupid=makeid(),
            fupgenid=fupgen.id,
            date=date,
            msgid=fupgen.msg[0],
            dataid=fupgen.data[0],
        )
        for date in dates
    ]

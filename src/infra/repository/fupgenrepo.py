from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, cast

from app.repository.fupgenrepo import FupGenRepository as IFupGenRepository
from domain.entity.channel import Channel as DomainChannel
from domain.entity.fupgen import FollowupGenerator, FupGenInput
from domain.entity.recurrence import (
    RecurrenceConfig,
    freqtype,
    make_scheduler,
    pasteventtype,
    recurrenceFactory,
    weekdaytype,
)
from infra.db.db import Session
from infra.db.models.fupgen import FupGen
from infra.db.models.recurrenceconfig import Recurrence


def to_domain(make_recurrence: recurrenceFactory, fup: FupGen) -> FollowupGenerator:
    rec = fup.recurrence

    freq = cast(freqtype, rec.freq)
    byweekday = cast(list[weekdaytype], rec.byweekday) if rec.byweekday else None
    past_events = cast(pasteventtype, rec.past_events)
    config = RecurrenceConfig(
        freq=freq,
        dtstart=rec.dtstart,
        interval=rec.interval,
        count=rec.count,
        until=rec.until,
        byweekday=byweekday,
        bymonthday=rec.bymonthday,
        allow_infinite=rec.allow_infinite,
        last_run=rec.last_run,
        next_run=rec.next_run,
        past_events=past_events,
    )
    scheduler = make_scheduler(make_recurrence, config)

    channels = [
        DomainChannel(id=c.id, type=c.type, configdata=c.configdata)
        for c in fup.channels
    ]
    return FollowupGenerator(
        id=fup.id,
        hookid=fup.hookid,
        ownerid=fup.ownerid,
        name=fup.name,
        channel=channels,
        description=fup.description,
        default_cycle=timedelta(hours=fup.default_cycle),
        scheduler=scheduler,
        msg=(fup.message.id, fup.message.msg),
        data=(fup.data.id, fup.data.data),
    )


@dataclass
class FupGenRepository(IFupGenRepository):

    db: Session
    make_recurrence: recurrenceFactory

    def create(self, id: str, fupgen: FupGenInput) -> None: ...

    def get_fupgen(self, ownerid: str, active: bool) -> list[FollowupGenerator]:

        query = self.db.query(FupGen).join(Recurrence).filter(FupGen.ownerid == ownerid)

        if active:
            query = query.filter(Recurrence.is_exhausted == False)
        else:
            query = query.filter(Recurrence.is_exhausted == True)

        fupgens: List[FupGen] = query.all()

        return [to_domain(self.make_recurrence, fupgen) for fupgen in fupgens]

    def update_config(
        self,
        updates: list[tuple[str, bool, int | None, datetime | None, datetime | None]],
    ) -> None: ...

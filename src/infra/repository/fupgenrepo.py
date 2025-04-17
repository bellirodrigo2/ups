from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, List, cast

from sqlalchemy.exc import NoResultFound

from app.repository.fupgenrepo import FupGenRepository as IFupGenRepository
from domain.entity.channel import Channel as DomainChannel
from domain.entity.fupgen import FollowupGenerator, FupGenInput
from domain.entity.recurrence import (
    RecurrenceConfig,
    SchedulerManager,
    freqtype,
    make_scheduler,
    pasteventtype,
    recurrenceFactory,
    weekdaytype,
)
from infra.db.db import Session
from infra.db.models.channel import ChannelDB
from infra.db.models.data import Data
from infra.db.models.fupgen import FupGen
from infra.db.models.msg import Message
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
        scheduler=scheduler,
        msg=(fup.message.id, fup.message.msg),
        data=(fup.data.id, fup.data.data),
    )


def to_db(
    make_id: Callable[[], str],
    sch: SchedulerManager,
    input: FupGenInput,
):

    now = datetime.now()
    id = make_id()
    conf = sch.config
    rec = Recurrence(
        id=id,
        freq=conf.freq,
        dtstart=conf.dtstart,
        interval=conf.interval,
        count=conf.count,
        until=conf.until,
        byweekday=conf.byweekday,
        bymonthday=conf.bymonthday,
        allow_infinite=conf.allow_infinite,
        last_run=conf.last_run,
        next_run=conf.next_run,
        is_exhausted=sch.is_exhausted(now),
        past_events=conf.past_events,
    )
    msgid = make_id()
    msg = Message(id=msgid, msg=input.msg)

    dataid = make_id()
    data = Data(id=dataid, data=input.data)

    chs: list[ChannelDB] = []
    for ch in input.channel:
        cid = make_id()
        ch_db = ChannelDB(id=cid, fupgen_id=id, type=ch.type, configdata=ch.configdata)
        chs.append(ch_db)

    fupgen = FupGen(
        id=id,
        hookid=input.hookid,
        ownerid=input.ownerid,
        name=input.name,
        description=input.description,
        recurrence=rec,
        message_id=msg.id,
        data_id=data.id,
    )
    return msg, data, chs, rec, fupgen


@dataclass
class FupGenRepository(IFupGenRepository):

    db: Session
    make_recurrence: recurrenceFactory
    make_id: Callable[[], str]

    def create(self, input: FupGenInput) -> datetime | None:

        sch = make_scheduler(self.make_recurrence, input.recurconfig)

        msg, data, chs, rec, fupgen = to_db(self.make_id, sch, input)
        self.db.add_all([msg, data, *chs, rec, fupgen])

        self.db.commit()

        return sch.config.next_run

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
    ) -> None:
        for fupgen_id, is_exhausted, count, last_run, next_run in updates:
            try:
                fupgen = self.db.query(FupGen).filter_by(id=fupgen_id).one()
            except NoResultFound:
                # Pode logar: f"FupGen {fupgen_id} não encontrado."
                continue

            if fupgen.recurrence:
                fupgen.recurrence.is_exhausted = is_exhausted
                fupgen.recurrence.count = count
                fupgen.recurrence.last_run = last_run
                fupgen.recurrence.next_run = next_run

        self.db.commit()

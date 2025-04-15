from datetime import datetime

import pytest

from infra.db.db import Session
from infra.db.models.channel import Channel
from infra.db.models.data import Data
from infra.db.models.fupgen import FupGen
from infra.db.models.msg import Message
from infra.db.models.recurrenceconfig import Recurrence
from infra.recurrence.rruleadaptor import rrule_factory
from infra.repository.fupgenrepo import FupGenRepository


def insert_sample_data(session: Session):
    rec = Recurrence(
        id="rec1",
        freq="DAILY",
        dtstart=datetime(2025, 4, 15),
        interval=1,
        is_exhausted=False,
        past_events="lastonly",
    )
    session.add(rec)

    msg = Message(id="123", msg="helloworld")
    session.add(msg)

    data = Data(id="123", data={})
    session.add(data)

    # Cria FupGen
    fup = FupGen(
        id="fup1",
        hookid="hook123",
        ownerid="owner123",
        name="Test FupGen",
        description="Some test description",
        default_cycle=24,
        recurrence_id=rec.id,
        recurrence=rec,
        message_id="123",
        data_id="123",
    )
    session.add(fup)

    # Cria Channel vinculado
    ch = Channel(
        id="ch1",
        fupgen_id=fup.id,
        type="email",
        configdata={"template": "test"},
    )
    session.add(ch)

    session.commit()


def test_get_fupgen_active(session: Session):
    insert_sample_data(session)

    repo = FupGenRepository(db=session, make_recurrence=rrule_factory)

    result = repo.get_fupgen(ownerid="owner123", active=True)

    assert len(result) == 1
    fup = result[0]
    assert fup.id == "fup1"
    assert fup.name == "Test FupGen"
    assert fup.msg[0] == "123"
    assert isinstance(fup.channel, list)

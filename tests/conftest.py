from datetime import datetime
from typing import Any, Generator

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from infra.db.db import get_db, make_session
from infra.db.models.base import Base
from infra.db.models.channel import Channel
from infra.db.models.data import Data
from infra.db.models.fupgen import FupGen
from infra.db.models.msg import Message
from infra.db.models.recurrenceconfig import Recurrence

SQLITE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def session_local() -> sessionmaker[Session]:
    return make_session(SQLITE_URL, Base)


@pytest.fixture
def session(session_local: sessionmaker[Session]) -> Generator[Session, Any, None]:
    yield from get_db(session_local)


@pytest.fixture(scope="function")
def populated_session(session: Session) -> Generator[Session, None, None]:

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

    data = Data(id="123", data={"datakey": "datavalue"})
    session.add(data)

    fup = FupGen(
        id="fup1",
        hookid="hook123",
        ownerid="owner1",
        name="Test FupGen",
        description="Some test description",
        default_cycle=24,
        recurrence_id=rec.id,
        recurrence=rec,
        message_id=msg.id,
        data_id=data.id,
    )
    session.add(fup)

    ch = Channel(
        id="ch1",
        fupgen_id=fup.id,
        type="email",
        configdata={"template": "test"},
    )
    session.add(ch)

    session.commit()

    yield session

    session.execute(text("DROP TABLE IF EXISTS recurrence"))
    session.execute(text("DROP TABLE IF EXISTS fupgen"))
    session.execute(text("DROP TABLE IF EXISTS channel"))
    session.execute(text("DROP TABLE IF EXISTS fupgen_msg"))
    session.execute(text("DROP TABLE IF EXISTS fupgen_data"))

    session.commit()

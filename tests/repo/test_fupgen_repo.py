from datetime import datetime, timedelta
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from domain.entity.channel import Channel
from domain.entity.fupgen import FupGenInput
from domain.entity.recurrence import RecurrenceConfig
from infra.db.db import Session
from infra.db.models.fupgen import FupGen
from infra.db.models.recurrenceconfig import Recurrence
from infra.recurrence.rruleadaptor import rrule_factory
from infra.repository.fupgenrepo import FupGenRepository


@pytest.fixture
def repo(populated_session: Session) -> FupGenRepository:
    return FupGenRepository(
        db=populated_session,
        make_recurrence=rrule_factory,
        make_id=lambda: str(uuid4()),
    )


def test_create_ok(repo: FupGenRepository):

    ch = Channel(id="ch1", type="email", configdata={"k": "v"})
    dts = datetime(2020, 1, 1)
    recconf = RecurrenceConfig(freq="DAILY", dtstart=dts, allow_infinite=True)
    owner = "ownerTESTE"
    input = FupGenInput(
        hookid="hook1",
        ownerid=owner,
        name="fupgentest",
        channel=[ch],
        recurconfig=recconf,
        msg="teste message",
        data={"datakey1": "datavalue1"},
    )

    next_run = repo.create(input)

    assert next_run is not None
    assert next_run == dts + timedelta(days=1)
    val = repo.db.query(FupGen).filter_by(ownerid=owner).one()
    assert val.recurrence.is_exhausted == False
    assert val.recurrence.next_run == dts + timedelta(days=1)


def test_create_exhausted(repo: FupGenRepository):

    ch = Channel(id="ch1", type="email", configdata={"k": "v"})

    dts = datetime(2020, 1, 1)
    until = dts + timedelta(days=15)

    recconf = RecurrenceConfig(freq="MONTHLY", dtstart=dts, until=until)
    owner = "OWNERTESTE"
    input = FupGenInput(
        hookid="hook1",
        ownerid=owner,
        name="fupgentest",
        channel=[ch],
        recurconfig=recconf,
        msg="teste message",
        data={"datakey1": "datavalue1"},
    )

    next_run = repo.create(input)

    assert next_run is None
    val = repo.db.query(FupGen).filter_by(ownerid=owner).one()
    assert val.recurrence.is_exhausted == True
    assert val.recurrence.next_run is None


def test_create_db_failure(repo: FupGenRepository):
    repo.db.add_all = MagicMock(side_effect=Exception("DB Error"))

    ch = Channel(id="ch1", type="email", configdata={"k": "v"})
    input = FupGenInput(
        hookid="hook1",
        ownerid="ownerTESTE",
        name="fupgentest",
        channel=[ch],
        recurconfig=RecurrenceConfig(
            freq="DAILY", dtstart=datetime(2020, 1, 1), count=100
        ),
        msg="teste message",
        data={"datakey1": "datavalue1"},
    )

    with pytest.raises(Exception):
        repo.create(input)


def test_create_multiple_channels(repo: FupGenRepository):
    ch1 = Channel(id="ch1", type="email", configdata={"template": "email1"})
    ch2 = Channel(id="ch2", type="sms", configdata={"template": "sms1"})
    dts = datetime(2020, 1, 1)
    recconf = RecurrenceConfig(freq="DAILY", dtstart=dts, allow_infinite=True)
    owner = "ownerTESTE"
    input = FupGenInput(
        hookid="hook1",
        ownerid=owner,
        name="fupgentest",
        channel=[ch1, ch2],  # Múltiplos canais
        recurconfig=recconf,
        msg="teste message",
        data={"datakey1": "datavalue1"},
    )

    next_run = repo.create(input)

    val = repo.db.query(FupGen).filter_by(ownerid=owner).one()
    assert len(val.channels) == 2
    assert next_run is not None


def test_get_fupgen_active(repo: FupGenRepository):

    result = repo.get_fupgen(ownerid="owner1", active_only=True)

    assert len(result) == 1
    fup = result[0]
    assert fup.id == "id1"
    assert fup.name == "Test FupGen"
    assert fup.msg[0] == "123"
    assert isinstance(fup.channel, list)


def test_get_fupgen_active_no_owner(repo: FupGenRepository):

    result = repo.get_fupgen(ownerid="noowner", active_only=True)
    assert result == []


def test_update_config_success(repo: FupGenRepository):

    fupgen_id = "id1"
    new_last_run = datetime.now()
    new_next_run = new_last_run + timedelta(days=1)

    repo.update_config([(fupgen_id, True, 5, new_last_run, new_next_run)])

    updated = repo.db.query(FupGen).filter_by(id=fupgen_id).one()
    recurrence = updated.recurrence

    assert recurrence.is_exhausted is True
    assert recurrence.count == 5
    assert recurrence.last_run == new_last_run
    assert recurrence.next_run == new_next_run


def test_update_config_fupgen_not_found(repo: FupGenRepository):
    # Deve ignorar sem erro se FupGen não existir
    try:
        repo.update_config(
            [("nonexistent-id", True, 1, datetime.now(), datetime.now())]
        )
    except Exception:
        pytest.fail("update_config should not raise if FupGen is missing")


def test_update_config_missing_recurrence(repo: FupGenRepository):
    # Remove a recurrence
    fupgen = repo.db.query(FupGen).filter_by(id="id1").one()
    repo.db.delete(fupgen.recurrence)
    repo.db.commit()

    try:
        repo.update_config([("id1", True, 1, datetime.now(), datetime.now())])
    except Exception:
        pytest.fail("update_config should not fail if recurrence is missing")


def test_update_config_commits(session: Session):

    service = FupGenRepository(
        db=session, make_recurrence=rrule_factory, make_id=lambda: str(uuid4())
    )

    fupgen_id = "id1"

    called = {"committed": False}
    original_commit = session.commit

    def mock_commit():
        called["committed"] = True
        return original_commit()

    session.commit = mock_commit

    rec = Recurrence(
        id=fupgen_id,
        freq="DAILY",
        dtstart=datetime.now(),
        interval=1,
        is_exhausted=False,
        past_events="lastonly",
    )
    session.add(rec)
    session.add(
        FupGen(
            id=fupgen_id,
            hookid="h",
            ownerid="o",
            name="n",
            description=None,
            recurrence=rec,
            message_id="123",
            data_id="123",
        )
    )
    session.commit()

    service.update_config([(fupgen_id, True, 10, datetime.now(), datetime.now())])

    assert called["committed"] is True

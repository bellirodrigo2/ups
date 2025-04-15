import pytest

from infra.db.db import Session
from infra.recurrence.rruleadaptor import rrule_factory
from infra.repository.fupgenrepo import FupGenRepository


def test_get_fupgen_active(populated_session: Session):

    repo = FupGenRepository(db=populated_session, make_recurrence=rrule_factory)

    result = repo.get_fupgen(ownerid="owner1", active=True)

    assert len(result) == 1
    fup = result[0]
    assert fup.id == "fup1"
    assert fup.name == "Test FupGen"
    assert fup.msg[0] == "123"
    assert isinstance(fup.channel, list)

    # testar se next_run mudou
    # testar no test_run_task tbm

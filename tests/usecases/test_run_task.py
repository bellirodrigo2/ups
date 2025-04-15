from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.usecase.task.runtask import RunTask
from domain.entity.channel import Channel
from infra.db.db import Session
from infra.recurrence.rruleadaptor import rrule_factory
from infra.repository.fupgenrepo import FupGenRepository

# from domain.entity.fup import FollowUp


@pytest.mark.asyncio
async def test_run_task_executes_correctly(populated_session: Session):
    # Mocks
    fuprepo = MagicMock()
    sendgateway = AsyncMock()

    fupgenrepo = FupGenRepository(db=populated_session, make_recurrence=rrule_factory)

    # UseCase
    task = RunTask(
        fupgenrepo=fupgenrepo,
        fuprepo=fuprepo,
        sendgateway=sendgateway,
    )
    ts = datetime(2025, 4, 18)
    next_run = await task.execute("owner1", ts)

    # Asserts
    fuprepo.add.assert_called_once()
    sendgateway.send.assert_awaited_once()

    assert next_run == ts + timedelta(days=1)

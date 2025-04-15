from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.usecase.task.runtask import RunTask
from domain.entity.channel import Channel

# from domain.entity.fup import FollowUp


@pytest.mark.asyncio
async def test_run_task_executes_correctly():
    # Mocks
    fup_gen_repo = MagicMock()
    fuprepo = MagicMock()
    sendgateway = AsyncMock()
    makeid = lambda: "fup1"
    scheduler_mock = MagicMock()
    scheduler_instance = MagicMock()
    scheduler_instance.schedule.return_value = [datetime(2025, 4, 14, 12, 0)]
    scheduler_instance.get_config = MagicMock(
        next_run=datetime(2025, 4, 15),
        last_run=datetime(2025, 4, 14),
        count=1,
    )
    scheduler_instance.is_exhausted.return_value = False
    scheduler_mock.return_value = scheduler_instance

    channel1 = Channel(
        id="test_ch", type="email", configdata={"email_addr": "ex@mail.com"}
    )
    fup_gen_repo.get_recur_config.return_value = [
        MagicMock(
            id="gen1",
            hookid="hook1",
            recurrence=MagicMock(next_run=datetime(2025, 4, 14)),
            msg="Olá",
            data={},
            channel=[channel1],
            default_cycle=timedelta(days=1),
        )
    ]

    # UseCase
    task = RunTask(
        fup_gen_repo=fup_gen_repo,
        fuprepo=fuprepo,
        sendgateway=sendgateway,
        makeid=makeid,
        scheduler=scheduler_mock,
    )
    now = datetime.now()
    next_run = await task.execute("owner1", now)

    # Asserts
    fuprepo.add.assert_called_once()
    sendgateway.send.assert_awaited_once()
    fup_gen_repo.update_config.assert_called_once()
    assert isinstance(next_run, datetime)

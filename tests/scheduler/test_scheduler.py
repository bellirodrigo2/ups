import asyncio
from datetime import datetime, timedelta
from typing import Optional

import pytest

from infra.scheduler.taskscheduler import AsyncioTaskScheduler


async def my_task(task_id: str) -> Optional[datetime]:
    print(f"Task {task_id} run on {datetime.now()}.")
    return datetime.now() + timedelta(seconds=3)


@pytest.mark.asyncio
async def test_add_task():
    scheduler = AsyncioTaskScheduler()

    now = datetime.now()
    run_at = now + timedelta(seconds=0.5)

    scheduler.add_task("task1", my_task, next_run=run_at)

    await asyncio.sleep(0.1)  # passa da primeira execução

    assert "task1" in scheduler.tasks
    assert scheduler.is_running("task1")
    assert scheduler.tasks["task1"].next_run > datetime.now()

    assert scheduler.is_running("task1")

    scheduler.remove_task("task1")
    assert scheduler.is_running("task1") is False
    await asyncio.sleep(0.1)  # dá tempo pra task ser cancelada


@pytest.mark.asyncio
async def test_remove_nonexistent_task():
    scheduler = AsyncioTaskScheduler()

    # Não deve lançar exceção
    scheduler.remove_task("nope")


@pytest.mark.asyncio
async def test_is_running_on_nonexistent_task():
    scheduler = AsyncioTaskScheduler()

    assert not scheduler.is_running("ghost")


@pytest.mark.asyncio
async def test_readd_task_with_different_schedule():
    scheduler = AsyncioTaskScheduler()
    run1 = datetime.now() + timedelta(milliseconds=200)

    scheduler.add_task("task1", my_task, next_run=run1)
    await asyncio.sleep(0.3)

    scheduler.remove_task("task1")
    await asyncio.sleep(0.1)

    run2 = datetime.now() + timedelta(milliseconds=500)
    scheduler.add_task("task1", my_task, next_run=run2)

    await asyncio.sleep(0.6)

    assert "task1" in scheduler.tasks
    assert scheduler.is_running("task1")

    scheduler.remove_task("task1")
    await asyncio.sleep(0.1)


@pytest.mark.asyncio
async def test_task_returns_none_and_stops():
    scheduler = AsyncioTaskScheduler()

    async def task_that_stops(task_id: str) -> Optional[datetime]:
        return None  # Finaliza após uma execução

    run_at = datetime.now() + timedelta(milliseconds=200)
    scheduler.add_task("task_stop", task_that_stops, next_run=run_at)

    await asyncio.sleep(0.3)

    # A task foi executada e removida sozinha
    assert not scheduler.is_running("task_stop")
    assert "task_stop" in scheduler.tasks  # Ainda existe no dicionário, mas não ativa

    scheduler.remove_task("task_stop")  # Garantia de limpeza

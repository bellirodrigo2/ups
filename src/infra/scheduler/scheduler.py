import asyncio
import heapq
import logging
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol

from apscheduler.job import Job
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

# -----------------------------
# 🔌 Protocol
# -----------------------------


class TaskSchedulerProtocol(Protocol):
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
    async def schedule(
        self,
        task_id: str,
        coro: Callable[[str], Awaitable[Optional[datetime]]],
        run_at: datetime,
    ) -> None: ...
    async def cancel(self, task_id: str) -> None: ...
    async def is_active(self, task_id: str) -> bool: ...
    async def next_run(self, task_id: str) -> Optional[datetime]: ...


# -----------------------------
# 🧩 Scheduler (Alto Nível)
# -----------------------------


class TaskScheduler:
    def __init__(self, backend: TaskSchedulerProtocol):
        self._backend = backend

    async def start(self) -> None:
        await self._backend.start()

    async def stop(self) -> None:
        await self._backend.stop()

    async def schedule(
        self,
        task_id: str,
        coro: Callable[[str], Awaitable[Optional[datetime]]],
        run_at: datetime,
    ) -> None:
        await self._backend.schedule(task_id, coro, run_at)

    async def cancel(self, task_id: str) -> None:
        await self._backend.cancel(task_id)

    async def is_active(self, task_id: str) -> bool:
        return await self._backend.is_active(task_id)

    async def next_run(self, task_id: str) -> Optional[datetime]:
        return await self._backend.next_run(task_id)


# -----------------------------
# ⚙️ heapq Implementation
# -----------------------------


class ScheduledTask:
    def __init__(
        self,
        run_at: datetime,
        task_id: str,
        coro: Callable[[str], Awaitable[Optional[datetime]]],
    ):
        self.run_at = run_at
        self.task_id = task_id
        self.coro = coro

    def __lt__(self, other: Any) -> bool:
        return self.run_at < other.run_at


class HeapqTaskScheduler(TaskSchedulerProtocol):
    def __init__(self):
        self._queue: List[ScheduledTask] = []
        self._tasks: Dict[str, ScheduledTask] = {}
        self._loop_task: Optional[asyncio.Task] = None
        self._wakeup = asyncio.Event()
        self._running = False

    async def start(self) -> None:
        if not self._running:
            self._running = True
            self._loop_task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        self._running = False
        self._wakeup.set()
        if self._loop_task:
            await self._loop_task

    async def schedule(
        self,
        task_id: str,
        coro: Callable[[str], Awaitable[Optional[datetime]]],
        run_at: datetime,
    ) -> None:
        if task_id in self._tasks:
            raise ValueError(f"Task '{task_id}' already scheduled")

        task = ScheduledTask(run_at, task_id, coro)
        self._tasks[task_id] = task
        heapq.heappush(self._queue, task)
        self._wakeup.set()

    async def cancel(self, task_id: str) -> None:
        if task_id in self._tasks:
            del self._tasks[task_id]
            self._wakeup.set()

    async def is_active(self, task_id: str) -> bool:
        return task_id in self._tasks

    async def next_run(self, task_id: str) -> Optional[datetime]:
        task = self._tasks.get(task_id)
        return task.run_at if task else None

    async def _run_loop(self) -> None:
        while self._running:
            now = datetime.now()
            while self._queue and self._queue[0].task_id not in self._tasks:
                heapq.heappop(self._queue)

            if not self._queue:
                self._wakeup.clear()
                await self._wakeup.wait()
                continue

            next_task = self._queue[0]
            delay = (next_task.run_at - now).total_seconds()
            if delay > 0:
                try:
                    self._wakeup.clear()
                    await asyncio.wait_for(self._wakeup.wait(), timeout=delay)
                    continue
                except asyncio.TimeoutError:
                    pass

            heapq.heappop(self._queue)
            if next_task.task_id not in self._tasks:
                continue

            try:
                result = await next_task.coro(next_task.task_id)
                if result:
                    await self.schedule(next_task.task_id, next_task.coro, result)
                else:
                    del self._tasks[next_task.task_id]
            except Exception as e:
                print(f"[heapq] Error in task '{next_task.task_id}': {e}")
                del self._tasks[next_task.task_id]


# -----------------------------
# 🧠 APScheduler Implementation
# -----------------------------


class APSchedulerTaskScheduler(TaskSchedulerProtocol):
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs: Dict[str, Job] = {}
        self.logger = logging.getLogger("APScheduler")

    async def start(self) -> None:
        self.scheduler.start()

    async def stop(self) -> None:
        self.scheduler.shutdown(wait=True)
        self.jobs.clear()

    async def schedule(
        self,
        task_id: str,
        coro: Callable[[str], Awaitable[Optional[datetime]]],
        run_at: datetime,
    ) -> None:
        if task_id in self.jobs:
            raise ValueError(f"Task '{task_id}' already exists")

        async def wrapper():
            try:
                self.logger.info(f"Running task '{task_id}'")
                result = await coro(task_id)
                if result:
                    await self.schedule(task_id, coro, result)
            except Exception as e:
                self.logger.error(f"Task '{task_id}' failed: {e}", exc_info=True)
            finally:
                self.jobs.pop(task_id, None)

        job = self.scheduler.add_job(
            wrapper, trigger=DateTrigger(run_date=run_at), id=task_id
        )
        self.jobs[task_id] = job
        self.logger.info(f"Scheduled '{task_id}' at {run_at}")

    async def cancel(self, task_id: str) -> None:
        job = self.jobs.pop(task_id, None)
        if job:
            job.remove()
            self.logger.info(f"Removed task '{task_id}'")

    async def is_active(self, task_id: str) -> bool:
        return task_id in self.jobs

    async def next_run(self, task_id: str) -> Optional[datetime]:
        job = self.jobs.get(task_id)
        return job.next_run_time if job else None

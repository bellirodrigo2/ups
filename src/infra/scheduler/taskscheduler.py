import asyncio
import logging
from contextlib import suppress
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Awaitable, Callable, Optional


@dataclass
class Task:
    id: str
    task: asyncio.Task
    event: asyncio.Event
    next_run: datetime


@dataclass
class AsyncioTaskScheduler:
    tasks: dict[str, Task] = field(default_factory=dict)
    logger: logging.Logger = field(default_factory=logging.getLogger)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def _log(self, msg: str) -> None:
        self.logger.info(msg)

    async def add_task(
        self,
        task_id: str,
        coro: Callable[[str], Awaitable[Optional[datetime]]],
        next_run: datetime,
    ) -> None:
        # Validate next_run to be in the future
        if next_run <= datetime.now():
            raise ValueError("next_run must be in the future")

        async with self._lock:
            if task_id in self.tasks:
                self.logger.warning(f"Task '{task_id}' already exists.")
                raise ValueError(f"Task '{task_id}' already exists")

            stop_event = asyncio.Event()

            async def _run():
                scheduled_time = next_run
                try:
                    while not stop_event.is_set():
                        delay = (scheduled_time - datetime.now()).total_seconds()

                        if delay > 0:
                            try:
                                self.logger.info(
                                    f"Task '{task_id}' waiting for next run in {delay:.2f}s"
                                )
                                await asyncio.wait_for(stop_event.wait(), timeout=delay)
                            except asyncio.TimeoutError:
                                pass  # Timeout occurred, continue task

                        try:
                            result = await coro(task_id)
                            if result is None:
                                self.logger.info(
                                    f"Task '{task_id}' finished (returned None)"
                                )
                                break

                            # Update the next scheduled time for repeated execution
                            scheduled_time = result
                            async with self._lock:
                                if task_id in self.tasks:
                                    self.tasks[task_id].next_run = scheduled_time

                            self.logger.info(
                                f"Task '{task_id}' re-scheduled for '{scheduled_time}'"
                            )
                        except Exception as e:
                            self.logger.error(
                                f"Error during task '{task_id}': {e}", exc_info=True
                            )
                            break  # Stop execution if an error occurs
                finally:
                    async with self._lock:
                        self.tasks.pop(task_id, None)
                    self.logger.info(f"Task '{task_id}' removed from scheduler")

            task = asyncio.create_task(_run())
            self.tasks[task_id] = Task(
                id=task_id, task=task, event=stop_event, next_run=next_run
            )
            self.logger.info(
                f"Task '{task_id}' added to scheduler (next run: {next_run})"
            )

    async def remove_task(self, task_id: str) -> None:
        async with self._lock:
            task_obj = self.tasks.get(task_id)
            if not task_obj:
                self.logger.warning(f"Tried to remove inexistent task '{task_id}'")
                return

            task_obj.event.set()  # Signal the task to stop
            task_obj.task.cancel()  # Cancel the asyncio task

        # Wait for the task to complete without blocking the lock
        with suppress(asyncio.CancelledError, asyncio.TimeoutError):
            await asyncio.wait_for(task_obj.task, timeout=5.0)

        self.logger.info(f"Task '{task_id}' successfully removed")

    async def is_running(self, task_id: str) -> bool:
        async with self._lock:
            task = self.tasks.get(task_id)
            return task is not None and not task.task.done()


if __name__ == "__main__":

    async def main():
        sch = AsyncioTaskScheduler()

        async def task(msg: str):
            print(msg)
            return datetime.now() + timedelta(microseconds=500)

        # Agendar a primeira execução de cada tarefa
        await sch.add_task("task1", task, datetime.now() + timedelta(microseconds=500))
        await sch.add_task("task2", task, datetime.now() + timedelta(microseconds=500))

        # Esperar algum tempo para observar as execuções
        await asyncio.sleep(5)

    # Executando o loop de eventos
    asyncio.run(main())

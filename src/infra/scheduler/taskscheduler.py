import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from logging import Logger
from typing import Any, Awaitable, Callable, Optional


@dataclass
class Task:
    id: str
    task: asyncio.Task[Any]
    event: asyncio.Event
    next_run: datetime


@dataclass
class AsyncioTaskScheduler:
    tasks: dict[str, Task] = field(default_factory=dict)
    running: bool = False
    logger: Logger = field(default_factory=logging.getLogger)

    def add_task(
        self,
        task_id: str,
        coro: Callable[[str], Awaitable[Optional[datetime]]],
        next_run: datetime,
    ) -> None:
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
                            self.logger.info(f"Starting task '{task_id}' execution")
                            await asyncio.wait_for(stop_event.wait(), timeout=delay)
                            return  # Stop requested
                        except asyncio.TimeoutError:
                            pass
                    try:
                        result = await coro(task_id)
                        if result is None:
                            self.logger.info(
                                f"Task '{task_id}' finished. (return None)"
                            )
                            break  # Task finalizada
                        scheduled_time = result
                        self.tasks[task_id].next_run = scheduled_time
                        self.logger.info(
                            f"Task '{task_id}' re-scheduled '{scheduled_time}'"
                        )
                    except Exception as e:
                        self.logger.error(
                            f"Error during the task '{task_id}' execution: {e}"
                        )
                        break  # Caso ocorra um erro
            finally:
                self.logger.info(f"Task '{task_id}' removed from the scheduler.")
                self.tasks.pop(task_id, None)

        task = asyncio.create_task(_run())
        self.tasks[task_id] = Task(
            id=task_id, task=task, event=stop_event, next_run=next_run
        )
        self.logger.info(f"Task '{task_id}' added to the scheduler")

    def remove_task(self, task_id: str) -> None:
        if task_id in self.tasks:
            task_obj = self.tasks[task_id]
            task_obj.event.set()  # Sinaliza para a tarefa parar
            task_obj.task.cancel()  # Cancele a task asyncio
            self.tasks.pop(task_id, None)
            self.logger.info(f"Task '{task_id}' removed by the client.")
        else:
            self.logger.warning(f"Trying to remove inexistent task: {task_id}")

    def is_running(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        return task is not None and not task.task.done()

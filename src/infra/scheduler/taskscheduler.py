import asyncio
from dataclasses import dataclass, field
from datetime import datetime
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

    def add_task(
        self,
        task_id: str,
        coro: Callable[[str], Awaitable[Optional[datetime]]],
        next_run: datetime,
    ) -> None:
        if task_id in self.tasks:
            raise ValueError(f"Task '{task_id}' already exists")

        stop_event = asyncio.Event()

        async def _run():
            scheduled_time = next_run
            while not stop_event.is_set():
                delay = (scheduled_time - datetime.now()).total_seconds()
                if delay > 0:
                    try:
                        await asyncio.wait_for(stop_event.wait(), timeout=delay)
                        return
                    except asyncio.TimeoutError:
                        pass

                try:
                    result = await coro(task_id)
                    if result is None:
                        break

                    # remover a tarefa ?

                    scheduled_time = result
                    self.tasks[task_id].next_run = scheduled_time
                except Exception as e:
                    # print(f"[{task_id}] Error during task execution: {e}")
                    break

        task = asyncio.create_task(_run())
        self.tasks[task_id] = Task(
            id=task_id, task=task, event=stop_event, next_run=next_run
        )

    def remove_task(self, task_id: str) -> None:
        if task_id not in self.tasks:
            # print(f"Tried to remove nonexistent task: {task_id}")
            return
        task_obj = self.tasks[task_id]
        task_obj.event.set()
        task_obj.task.cancel()
        self.tasks.pop(task_id, None)

    def is_running(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        return task is not None and not task.task.done()

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Awaitable, Callable, Protocol

from domain.entity.recurrence import Recurrence


class TaskScheduler(Protocol):

    def add_task(
        self, task_id: str, recurrence: Recurrence, coro: Callable[..., Any]
    ) -> None: ...

    def remove_task(self, task_id: str) -> None: ...

    def is_running(self, task_id: str) -> bool: ...

    async def start(self) -> None: ...

    async def stop(self) -> None: ...


@dataclass
class AsyncioTaskScheduler:
    tasks: dict[str, asyncio.Task] = field(default_factory=dict)
    stop_signals: dict[str, asyncio.Event] = field(default_factory=dict)
    recurrene_dict: dict[str, Recurrence] = field(default_factory=dict)
    running: bool = False

    def add_task(
        self, task_id: str, recurrence: Recurrence, coro: Callable[..., Any]
    ) -> None:
        stop_event = asyncio.Event()
        self.stop_signals[task_id] = stop_event

        async def _run_scheduled_task():
            while not stop_event.is_set():
                next_run = recurrence.after(datetime.now())
                if not next_run:
                    break  # Acabaram as datas
                delay = (next_run - datetime.now()).total_seconds()
                if delay > 0:
                    try:
                        await asyncio.wait_for(stop_event.wait(), timeout=delay)
                        break  # Parou durante a espera
                    except asyncio.TimeoutError:
                        pass  # Timeout, hora de rodar
                try:
                    await coro(
                        task_id
                    )  # Executa sua task (ex: runTask.execute(ownerid))
                except Exception as e:
                    print(f"[{task_id}] Erro durante execução: {e}")

        self.tasks[task_id] = asyncio.create_task(_run_scheduled_task())
        self.recurrene_dict[task_id] = recurrence

    def remove_task(self, task_id: str) -> None:
        if task_id not in self.tasks:
            print(f"Tentando remover task inexistente: {task_id}")
            return
        self.stop_signals[task_id].set()
        self.tasks[task_id].cancel()

        # Limpa os registros após parar a task
        self.tasks.pop(task_id, None)
        self.stop_signals.pop(task_id, None)
        self.recurrence.pop(task_id, None)

    def is_running(self, task_id: str) -> bool:
        return task_id in self.tasks and not self.tasks[task_id].done()

    def get_config(self, task_id: str) -> Recurrence | None:
        return self.recurrene_dict.get(task_id, None)

    def set_config(self, task_id: str, recurrence: Recurrence):
        if task_id not in self.recurrene_dict:
            raise Exception(f"Task: {task_id} do not exist.")

    async def start(self) -> None:
        self.running = True
        while self.running:
            await asyncio.sleep(1)

    async def stop(self) -> None:
        self.running = False
        for task_id in list(self.tasks):
            self.remove_task(task_id)

from dataclasses import dataclass
from logging import Logger

from app.usecase.task.runtask import RunTask
from domain.entity.recurrence import RecurrenceConfig, recurrenceFactory
from infra.scheduler.taskscheduler import TaskScheduler


@dataclass
class AddTaskToScheduler:
    scheduler: TaskScheduler
    factory: recurrenceFactory
    runtask: RunTask
    logger: Logger

    def execute(self, ownerid: str, config: RecurrenceConfig) -> None:
        if self.scheduler.is_running(ownerid):
            self.logger.info(f"[{ownerid}] Task já está em execução no scheduler.")
            return

        recurrence = self.factory(config)

        self.scheduler.add_task(ownerid, recurrence, self.runtask.execute)
        self.logger.info(f"[{ownerid}] Task adicionada ao scheduler.")

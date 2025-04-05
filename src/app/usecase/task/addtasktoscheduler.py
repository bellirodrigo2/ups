from dataclasses import dataclass
from logging import Logger

from domain.entity.recurrence import RecurrenceConfig, recurrenceFactory
from infra.scheduler.taskscheduler import TaskScheduler


@dataclass
class AddTaskToScheduler:
    scheduler: TaskScheduler
    factory: recurrenceFactory
    logger: Logger

    def execute(self, ownerid: str, config: RecurrenceConfig) -> None:
        if self.scheduler.is_running(ownerid):
            self.logger.info(f"[{ownerid}] Task já está em execução no scheduler.")
            return

        self.scheduler.add_task(ownerid, config)
        self.logger.info(f"[{ownerid}] Task adicionada ao scheduler.")

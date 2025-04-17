import logging
from dataclasses import dataclass, field
from logging import Logger
from typing import Any

from app.repository.fupgenrepo import FupGenRepository
from app.usecase.task.runtask import RunTask
from app.usecase.usecase import UseCase
from domain.entity.fupgen import FupGenInput
from infra.scheduler.interface import ITaskScheduler


@dataclass
class CreateFupGenerator(UseCase):
    fupgenrepo: FupGenRepository
    scheduler: ITaskScheduler
    runtask: RunTask

    logger: Logger = field(default_factory=logging.getLogger)

    async def execute(self, fupgen: FupGenInput) -> None:

        next_run = self.fupgenrepo.create(fupgen)

        ownerid = fupgen.ownerid

        is_active = await self.scheduler.is_active(ownerid)

        if is_active:
            self.logger.info(f'Task "{ownerid}" alredy scheduled')
            return
        if next_run is None:
            self.logger.info(f"Next Run for '{ownerid}' has None as next_run")
            return

        await self.scheduler.schedule(self.runtask.execute, ownerid, next_run)

        self.logger.info(f"[{ownerid}] Task added to the scheduler.")

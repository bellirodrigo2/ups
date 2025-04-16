import logging
from dataclasses import dataclass, field
from datetime import datetime
from logging import Logger

from app.gateway.sendgateway import SendGateway
from app.repository.fupgenrepo import FupGenRepository
from app.repository.fuprepo import FupRepository
from app.usecase.usecase import UseCase
from domain.entity.fup import FollowUp, make_fup
from domain.entity.fupgen import FollowupGenerator


@dataclass
class RunTask(UseCase):
    fupgenrepo: FupGenRepository
    fuprepo: FupRepository
    sendgateway: SendGateway

    logger: Logger = field(default_factory=logging.getLogger)

    async def execute(self, ownerid: str, ts: datetime | None) -> datetime | None:

        fupgens: list[FollowupGenerator] = self.fupgenrepo.get_fupgen(
            ownerid=ownerid, active=True
        )
        self.logger.info(f'FupGen query for "{ownerid}" returned {len(fupgens)} items')
        self.logger.debug(str(fupgens))

        nexts: dict[str, datetime] = {
            fupg.id: fupg.scheduler.next_run
            for fupg in fupgens
            if fupg.scheduler.next_run is not None
        }

        ts = ts or datetime.now()

        fups: list[FollowUp] = []
        update_recurconf: list[
            tuple[str, bool, int | None, datetime | None, datetime | None]
        ] = []

        for fupgen in fupgens:

            items = make_fup(fupgen, ts)
            self.logger.info(f'FupGen "{fupgen.id}" generated {len(items)} Fups.')
            self.logger.debug(str(items))
            fups.extend(items)
            sch = fupgen.scheduler
            is_exausted = fupgen.scheduler.is_exhausted(ts)

            if sch.next_run is not None:
                nexts[fupgen.id] = sch.next_run

            update = (fupgen.id, is_exausted, sch.count, sch.last_run, sch.next_run)
            self.logger.debug(
                f"""
                FupGen "{fupgen.id}" update set: 
                is_exhausted:"{is_exausted}", count:"{sch.count}", 
                last_run: "{sch.last_run}", next_run: "{sch.next_run}"
                """
            )
            update_recurconf.append(update)

        # TODO logica aqui para salvar ou nao
        self.fuprepo.add(fups)
        self.fupgenrepo.update_config(update_recurconf)
        # TODO logica aqui para filtrar apenas alguns gateways. ex: apenas console
        await self.sendgateway.send(fups)
        # TODO faz asyncio
        # asyncio.create_task(self.sendgateway.send(fups))

        next = min(nexts.values(), default=None)

        self.logger.info(f'Next Task for "{ownerid}" scheduled for {next}')
        return next

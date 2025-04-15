from dataclasses import dataclass
from datetime import datetime

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

    async def execute(self, ownerid: str, ts: datetime | None) -> datetime:

        fupgens: list[FollowupGenerator] = self.fupgenrepo.get_fupgen(
            ownerid=ownerid, active=True
        )
        nexts: dict[str, datetime] = {
            fupg.hookid: fupg.scheduler.next_run
            for fupg in fupgens
            if fupg.scheduler.next_run is not None
        }

        ts = ts or datetime.now()

        fups: list[FollowUp] = []
        update_recurconf: list[
            tuple[str, bool, int | None, datetime | None, datetime | None]
        ] = []

        for fupgen in fupgens:

            fups.extend(make_fup(fupgen, ts))
            sch = fupgen.scheduler
            is_exausted = fupgen.scheduler.is_exhausted(ts)

            if sch.next_run is not None:
                nexts[fupgen.hookid] = sch.next_run

            update_recurconf.append(
                (fupgen.id, is_exausted, sch.count, sch.last_run, sch.next_run)
            )

        # TODO logica aqui para salvar ou nao
        self.fuprepo.add(fups)
        self.fupgenrepo.update_config(update_recurconf)
        # TODO logica aqui para filtrar apenas alguns gateways. ex: apenas console
        await self.sendgateway.send(fups)
        # TODO faz asyncio
        # asyncio.create_task(self.sendgateway.send(fups))

        if nexts:
            next = min(nexts.values())
        else:
            next_delta = min([fupg.default_cycle for fupg in fupgens])
            next = ts + next_delta

        return next

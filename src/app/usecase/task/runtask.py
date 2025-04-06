from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from app.gateway.sendgateway import SendGateway
from app.repository.fupgenrepo import FupGenRepository
from app.repository.fuprepo import FupRepository
from app.usecase.fup.readfupgen import ReadFupGenerator
from domain.entity.fupgen import FupGenReadConfig
from app.usecase.usecase import UseCase
from domain.entity.fup import FollowUp
from domain.entity.fupgen import FollowupGenerator
from domain.entity.recurrence import recurrenceFactory


@dataclass
class RunTask(UseCase):
    readfupgen: ReadFupGenerator
    fup_gen_repo: FupGenRepository
    fuprepo: FupRepository
    sendgateway: SendGateway
    makeid: Callable[[], str]
    factory: recurrenceFactory

    def execute(self, ownerid: str) -> Any:

        fupgens: list[FollowupGenerator] = self.readfupgen.execute(
            ownerid, FupGenReadConfig(active=True)
        )
        now = datetime.now()

        fups: list[FollowUp] = []
        for fupg in fupgens:
            recurrence = self.factory(fupg.recurrence)
            dates = recurrence.between(fupg.last_run, now)
            for date in dates:
                id = self.makeid()
                fup = FollowUp(
                    fupid=id,
                    fupgenid=fupg.id,
                    date=date,
                    msg=fupg.msg,
                    data=fupg.data,
                    responses=[(channel, {}) for channel in fupg.channel],
                )
                fups.append(fup)

        self.sendgateway.send(fups)

        self.fuprepo.add(fups)
        self.fup_gen_repo.update_lastrun([fupg.id for fupg in fupgens], last_run=now)

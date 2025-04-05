from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable

from app.repository.fupgenrepo import FupGenRepository
from app.usecase.fup.readfupgen import FupReadConfig, ReadFupGenerator
from app.usecase.usecase import UseCase
from domain.entity.fup import FollowUp
from domain.entity.recurrence import recurrenceFactory


@dataclass
class runTask(UseCase):
    readfupgen: ReadFupGenerator
    fup_gen_repo: FupGenRepository
    sendgateway: SendGateway
    makeid: Callable[[], str]
    factory: recurrenceFactory

    def execute(self, ownerid: str) -> Any:

        fupgens = self.readfupgen.execute(ownerid, FupReadConfig(active=True))
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
                    metadata=fupg.metadata,
                    responses=[(channel, {}) for channel in fupg.channel],
                )
                fups.append(fup)

        self.sendgateway.send(fups)

        self.fuprepo.add(fups)
        self.fup_gen_repo.update_lastrun([fupg.id for fupg in fupgens], last_run=now)
